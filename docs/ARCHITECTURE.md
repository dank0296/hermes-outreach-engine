# Architecture — Hermes Outreach Engine

System design for a 24/7 outreach agent that **only escalates leads that meet criteria**.

Audience: operators (crypto trading Discord first). Tone of the product: filter + handoff, not autopilot sales.

---

## Goals

1. Run continuous outreach without operator babysitting  
2. Score every lead on intent, engagement, fit, recency  
3. Automate low-signal nurture  
4. **Handoff only when gates pass** — human time is the scarce resource  
5. Stay safe: dry-run default, rate limits, opt-out, no guaranteed-returns copy  

Non-goals: trade execution, portfolio advice, guaranteed conversion rates, replacing the operator on close.

---

## High-level design

```
                    ┌──────────────────────────────────────────┐
                    │            Hermes Agent runtime          │
                    │  skills / tools / config / model router  │
                    └──────────────────────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
  ┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
  │  Discovery  │                 │  Tick Loop  │                 │  Handoff    │
  │  adapters   │────────────────▶│  + Sequence │────────────────▶│  pipeline   │
  └─────────────┘                 └──────┬──────┘                 └──────▲──────┘
                                         │                               │
                                         ▼                               │
                                  ┌─────────────┐                 ┌──────┴──────┐
                                  │  Messenger  │                 │   Scorer    │
                                  │  (dry/live) │                 │  criteria   │
                                  └─────────────┘                 └─────────────┘
```

**Primary model:** Grok (xAI) — preferred for conversational outreach.  
**Fallback:** OpenRouter — continuity under outage/rate limits.  
**Runtime:** Hermes Agent skills + local package under `src/outreach_engine/`.

---

## Components

### 1. Discovery

Pulls candidate leads from a channel adapter.

- **Demo:** static / sample lead file (`demo/sample_leads.json` when present)  
- **Discord (live later):** new members, recent posters in allowed channels, tagged cohorts  
- **Filters early:** blocklist tags, prior opt-out, recent handoff cooldown  

Output: `Lead` records written/updated in the lead store.

### 2. Tick loop

Heartbeat of the system. On each tick:

1. Load due leads (next_action_at ≤ now, not suppressed)  
2. Cap batch size (`tick.max_leads_per_tick`)  
3. For each lead: load conversation state + sequence step  
4. Generate or select next message (model call, template + context)  
5. Apply safety checks (rate limit, opt-out, content rules)  
6. Send or simulate (`dry_run`)  
7. Re-score  
8. If handoff gates pass → enqueue handoff; else schedule next step  
9. Persist audit events  

Interval: `tick.interval_seconds` (+ jitter).

### 3. Sequence engine

Ordered steps with delays (`sequence.steps[]` in config).

| Step | Role |
|------|------|
| intro | Identity + value + light CTA |
| value_nudge | Concrete benefit + qualifying question |
| intent_check | Direct intent; open human door |
| soft_close | Final touch; then archive |

Stops on: handoff, opt-out, max steps, suppress flags.

### 4. Scorer

Produces score 0–100 and signal set.

```
score = w_intent * intent
      + w_engagement * engagement
      + w_fit * fit
      + w_recency * recency
```

Weights live in `config/default.yaml` → `scoring.weights`.

Signals are boolean/count features (explicit interest, reply count, ICP tags, etc.). Scoring is explainable: every handoff includes breakdown.

### 5. Handoff pipeline

**Only runs when criteria pass.** Defaults:

- `score >= handoff.min_score`  
- at least one intent signal from allowlist  
- not suppressed  
- min replies / min sequence step as configured  

Payload to operator:

- lead identity + channel  
- score + breakdown  
- matched signals  
- last N messages  
- recommended talking points (model-generated, short)  

Delivery: operator DM or dedicated Discord channel (adapter-specific).

### 6. Messenger

Abstract send API:

- `dry_run`: log simulated message; no network send  
- `live`: channel adapter sends DM  

Respects rate limits and opt-out before any send path.

### 7. Model router

```
try primary (Grok / xAI)
  on failure or rate limit → fallback (OpenRouter)
```

Used for: message drafting, signal extraction from replies, talking points on handoff.

---

## Data model

Logical entities (implementation may use SQLite/JSON for demo).

### Lead

| Field | Type | Notes |
|-------|------|--------|
| id | string | stable id |
| channel | enum | discord / telegram / email |
| external_id | string | platform user id |
| display_name | string | |
| tags | string[] | ICP + operational tags |
| status | enum | new / active / handed_off / suppressed / archived |
| score | float | latest 0–100 |
| signals | object | latest signal map |
| sequence_id | string | |
| sequence_step | int | |
| next_action_at | datetime | |
| reply_count | int | |
| last_message_at | datetime | |
| handoff_at | datetime? | |
| suppress_reason | string? | |
| metadata | object | freeform |

### MessageEvent

| Field | Type | Notes |
|-------|------|--------|
| id | string | |
| lead_id | string | |
| direction | in / out | |
| body | string | |
| dry_run | bool | |
| step_id | string? | sequence step |
| created_at | datetime | |
| model | string? | if generated |

### ScoreEvent

| Field | Type |
|-------|------|
| lead_id | string |
| score | float |
| breakdown | object |
| signals | object |
| created_at | datetime |

### HandoffEvent

| Field | Type |
|-------|------|
| lead_id | string |
| score | float |
| reason_codes | string[] |
| context_snapshot | object |
| notified | bool |
| created_at | datetime |

### AuditEvent

Generic append-only log: tick starts, skips, rate-limit hits, opt-outs, errors.

---

## Tick loop (detail)

```
on_tick():
  leads = store.due(limit=max_leads_per_tick)
  for lead in leads:
    if safety.blocked(lead): continue
    ctx = store.conversation(lead)
    draft = sequence.next_message(lead, ctx)   # may call model
    if not safety.allow_send(lead, draft): 
      store.audit(skip); continue
    messenger.deliver(lead, draft)             # dry_run or live
    store.append_message(out)
    # if inbound replies arrived since last tick, merge first
    score, signals = scorer.evaluate(lead, ctx)
    store.save_score(lead, score, signals)
    if handoff.eligible(lead, score, signals):
      handoff.enqueue(lead, score, signals, ctx)
      lead.status = handed_off
    else:
      sequence.schedule_next(lead)
  store.commit()
```

Inbound replies (webhook/poll) update `MessageEvent` and may **fast-path** re-score between ticks if intent is high.

---

## Handoff pipeline (detail)

```
eligible(lead, score, signals):
  if lead.suppressed or lead.status == handed_off: return false
  if score < min_score: return false
  if not any(s in require_any_intent for s in signals): return false
  if lead.reply_count < min_replies: return false
  if lead.sequence_step < min_sequence_step: return false
  if within_cooldown(lead): return false
  return true

enqueue(...):
  snapshot = build_context(...)
  notify operator channel
  audit + HandoffEvent
  stop sequence for lead
```

**Product rule:** operator inbox should stay quiet unless criteria fire. Tuning knobs live in config, not hard-coded heroics.

---

## Safety architecture

| Control | Where |
|---------|--------|
| dry_run default | config root |
| rate limits | safety.rate_limits before messenger |
| opt-out keywords | inbound parse → suppress |
| no guaranteed returns | content_rules + prompt system |
| blocklist tags | discovery + tick |
| audit log | all state transitions |

---

## Config surface

Single source of truth: `config/default.yaml` (override with `config/local.yaml`).

Key sections: `models`, `tick`, `scoring`, `handoff`, `safety`, `sequence`, `channels`, `icp`, `demo`.

---

## Deployment sketch (post-demo)

- Hermes process or service with skill loaded  
- Secrets via env, not repo  
- SQLite for single-operator demo; Postgres later if multi-tenant  
- Discord bot token only when leaving dry_run  
- Observability: tick metrics, handoff count, skip reasons  

---

## Extension points

1. New channel = implement Discovery + Messenger adapter  
2. New ICP = retag + scoring weights  
3. New sequence = YAML steps + templates  
4. Operator UI = read handoff queue + audit (out of scope for day-10 demo)  

---

## Related docs

- [10-DAY-PLAN.md](10-DAY-PLAN.md)  
- [MEETING-BRIEF.md](MEETING-BRIEF.md)  
- [ICP-CRYPTO-DISCORD.md](ICP-CRYPTO-DISCORD.md)  
- [../config/default.yaml](../config/default.yaml)  
