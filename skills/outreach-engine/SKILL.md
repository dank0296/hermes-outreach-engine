---
name: outreach-engine
description: Use when running autonomous multi-channel lead outreach, cold sequences, handoff criteria, or 24/7 sales engine for Discord/crypto community demos. Runs dry-run-safe by default; notifies owner only when lead is worthwhile.
version: 1.0.0
author: Viking Productions / Dank
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [outreach, sales, crm, sms, email, telephony, hermes, crypto, discord]
    related_skills: [lead-nurture, crm-manager, telephony]
---

# Outreach Engine

24/7 multi-channel cold outreach that **only interrupts the human when a lead is worth it**.

## Overview

**Paper / agent roles (non-negotiable):**

| Role | Responsibility |
|------|----------------|
| **Engine (Hermes)** | Runs sequences 24/7 — email, SMS, AI voice. Scores replies. Logs everything. Exhausts cold leads without pinging the owner. |
| **Human (owner)** | Only gets notified on **handoff**. Takes the call / closes / onboards. Never babysits cold leads. |

Default mode is **demo / dry-run**: every channel logs what *would* send; nothing leaves the machine until the owner explicitly switches to LIVE and confirms.

Repo: `/opt/data/repos/hermes-outreach-engine`  
Skill path (in-repo): `skills/outreach-engine/`

## When to Use

- Running or demoing the crypto trading Discord outreach engine
- Multi-channel cold sequences (email + SMS + AI call)
- Defining / checking handoff criteria before owner alert
- Dry-run verification before any live send
- 10-day client demo prep for the Discord community product

**Do not use for:**

- Spam, harassment, or non-consensual blasting
- Guaranteed-returns / “risk-free profits” crypto claims
- Closing deals yourself as the agent (handoff only)
- Live sends without explicit owner confirmation
- Legal advice (point at compliance notes; owner decides)

## Architecture

```
Hermes brain (Grok SuperGrok/xAI primary → OpenRouter backup)
        │
        ▼
   ┌─────────┐     ┌────────┐     ┌──────────────────┐
   │  Store  │────▶│ Scorer │────▶│ Handoff gate     │
   │ leads + │     │ score  │     │ notify only if   │
   │ events  │     │ stage  │     │ criteria met     │
   └─────────┘     └────────┘     └────────┬─────────┘
        ▲                                  │
        │                                  ▼
   Channels                         Telegram / webhook
   email · SMS · AI call            (owner only)
```

| Component | Role |
|-----------|------|
| **Brain** | Hermes Agent; primary model xAI Grok (SuperGrok); fallback OpenRouter |
| **Store** | Lead records, sequence state, touch log, opt-outs |
| **Scorer** | Maps opens/replies/intent → score + stage (cold→warm→hot→qualified) |
| **Channels** | Email (Gmail/SMTP/Composio), SMS (Twilio), AI call (Bland/Vapi via `telephony`) |
| **Notify** | Telegram home channel + optional webhook — **handoff only** |

Full diagram and data flow: [references/architecture.md](references/architecture.md)

## Commands

Always run from the repo root with `PYTHONPATH=src`:

```bash
cd /opt/data/repos/hermes-outreach-engine

# Demo (default dry-run path — preferred for meetings)
PYTHONPATH=src python -m outreach_engine.cli demo

# Status / pipeline snapshot
PYTHONPATH=src python -m outreach_engine.cli status

# Import leads (CSV or JSON)
PYTHONPATH=src python -m outreach_engine.cli import --file path/to/leads.csv

# Enroll a lead into a sequence (demo mode unless --live)
PYTHONPATH=src python -m outreach_engine.cli enroll --lead-id <ID> --sequence crypto-discord

# Tick the engine once (process due touches)
PYTHONPATH=src python -m outreach_engine.cli tick

# Score / re-score a lead
PYTHONPATH=src python -m outreach_engine.cli score --lead-id <ID>

# Dry-run a single touch (never sends)
PYTHONPATH=src python -m outreach_engine.cli send --lead-id <ID> --channel email --dry-run

# LIVE send — ONLY after owner confirmation
PYTHONPATH=src python -m outreach_engine.cli send --lead-id <ID> --channel email --live

# Simulate inbound reply (demo)
PYTHONPATH=src python -m outreach_engine.cli simulate-reply --lead-id <ID> --text "Interested, what's pricing?"

# Force handoff check / notify (still respects criteria unless --force)
PYTHONPATH=src python -m outreach_engine.cli handoff --lead-id <ID>

# Opt-out / suppress
PYTHONPATH=src python -m outreach_engine.cli opt-out --lead-id <ID> --reason "STOP"
```

**Completion criteria for any CLI action:** command exits 0, stdout shows intended mode (`dry_run` vs `live`), and store reflects the new state (`status` / `score` re-check).

## Handoff Criteria (defaults)

Notify the owner when **any** of these is true:

| Signal | Default |
|--------|---------|
| Score | ≥ **40** |
| Stage | `hot` or `qualified` |
| Reply intent | Interested / positive intent detected |
| Explicit ask | Booked call, pricing question, or demo request |

**No handoff when:**

- Sequence exhausted with no positive signal (log only)
- Opt-out / STOP / unsubscribe
- Bounce / invalid contact
- Score still cold/warm below threshold

Template for the alert: [templates/handoff-alert.md](templates/handoff-alert.md)

## Channel Mapping

| Channel | Provider | Notes |
|---------|----------|-------|
| **Email** | Gmail / SMTP / Composio | Prefer Composio Gmail when connected; else SMTP from `.env` |
| **SMS** | Twilio | Creds often already on VPS; always honor STOP |
| **AI call** | Bland or Vapi | Route via `telephony` skill; scripted, short, opt-out aware |

**LIVE send gate (always):**

1. Confirm `DRY_RUN` / demo mode is intentional, or
2. Owner explicitly says go LIVE for this lead/channel
3. Contact is not opted out
4. Compliance copy is clean (no guaranteed profits)

Never silently flip from dry-run to live.

## Demo Mode (always default)

- `DRY_RUN=true` in `.env` (see repo `.env.example`)
- CLI defaults to dry-run unless `--live` is passed **and** env allows it
- Channels write to the touch log with payload preview; no external API send
- Handoff notify can still fire in demo as a **preview** message clearly labeled `[DEMO]`

Client meeting flow: [references/meeting-demo-script.md](references/meeting-demo-script.md)

## Sequence: Crypto Discord (default pack)

Canonical sequence template: [templates/sequence-crypto-discord.md](templates/sequence-crypto-discord.md)

High-level (example cadence):

1. **Day 0 — Email** value intro (community edge, not hype)
2. **Day 1 — SMS** short bump + opt-out language
3. **Day 3 — Email** social proof / what members get
4. **Day 5 — AI call** brief, respectful, leave callback path
5. **Day 7 — Email** soft close / last value touch
6. **Day 10 — SMS** final check-in → mark exhausted if silence

Every message: no guaranteed returns; clear who we are; easy opt-out.

## 10-Day Build Plan (summary)

| Day | Focus | Done when |
|-----|-------|-----------|
| 1 | Repo scaffold, skill skeleton, env | Structure + this skill present |
| 2 | Store + lead model + import | CSV import + `status` works dry |
| 3 | Scorer + stages + handoff rules | Score/handoff unit path green |
| 4 | Email channel dry-run | Touch log shows email payload |
| 5 | SMS channel dry-run (Twilio mock) | SMS payload logged, STOP path |
| 6 | AI voice dry-run via telephony | Call script logged, no live dial |
| 7 | Sequence runner + `tick` | Multi-day cadence advances in dry |
| 8 | Notify (Telegram/webhook) | Handoff alert fires on criteria only |
| 9 | Demo polish + meeting script | `cli demo` end-to-end green |
| 10 | Client meeting + live gate review | Demo delivered; LIVE still gated |

Deadline target: ~2026-07-26 (from 2026-07-16 kickoff).

## Compliance (must load before LIVE)

Read [references/compliance.md](references/compliance.md) before any live campaign.

Hard rules for this skill:

- CAN-SPAM: identity, physical address (production), unsubscribe
- TCPA: prior express consent for SMS/calls; honor STOP immediately
- Crypto marketing: **no guaranteed profits / risk-free claims**
- Demo ≠ production: dry-run does not prove legal readiness

## Common Pitfalls

1. **Babysitting cold leads** — Do not notify on every open. Only handoff criteria.
2. **Silent LIVE mode** — Never send without explicit owner confirm + env not dry-run.
3. **Guaranteed-return language** — Instant rewrite; compliance failure.
4. **Ignoring STOP** — Immediate suppress; never re-enroll without new consent.
5. **Treating exhausted as handoff** — Exhausted = log only, no owner ping.
6. **Skipping dry-run before demo** — Always run `cli demo` first; fix log noise.
7. **Wrong PYTHONPATH** — Commands fail without `PYTHONPATH=src` from repo root.
8. **Mixing nurture vs cold engine** — Use `lead-nurture` for warm pipeline; this skill is autonomous cold → handoff.
9. **Calling without telephony skill** — Load `telephony` for Bland/Vapi patterns.
10. **Committing secrets** — `.env` is gitignored; only `.env.example` is safe.

## Verification Checklist

- [ ] `cd /opt/data/repos/hermes-outreach-engine` and `DRY_RUN=true` (or unset live flags)
- [ ] `PYTHONPATH=src python -m outreach_engine.cli demo` exits 0
- [ ] `status` shows leads/stages without errors
- [ ] Simulated interested reply → score/stage rises → handoff criteria true
- [ ] Handoff alert uses [templates/handoff-alert.md](templates/handoff-alert.md) shape and is labeled `[DEMO]` in dry-run
- [ ] Exhausted cold lead produces **no** owner notify
- [ ] Opt-out path suppresses all further channels
- [ ] No message copy promises guaranteed trading profits
- [ ] LIVE path requires explicit owner confirmation (gate tested, not used casually)
- [ ] Related skills available when needed: `lead-nurture`, `crm-manager`, `telephony`

## One-Shot Recipes

### A) Pre-meeting dry-run

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli demo
PYTHONPATH=src python -m outreach_engine.cli status
```

Done when: demo completes, status readable, no live sends.

### B) Simulate hot lead → handoff

```bash
PYTHONPATH=src python -m outreach_engine.cli simulate-reply --lead-id <ID> --text "Yes, send pricing and book a call"
PYTHONPATH=src python -m outreach_engine.cli score --lead-id <ID>
PYTHONPATH=src python -m outreach_engine.cli handoff --lead-id <ID>
```

Done when: score ≥ 40 or stage hot/qualified and handoff preview fires once.

### C) Owner confirmed single LIVE email

```bash
# Only after verbal/written confirm from owner
PYTHONPATH=src python -m outreach_engine.cli send --lead-id <ID> --channel email --live
```

Done when: provider accepts message and touch log records live send; still no spam blast.

## Related Skills

- `lead-nurture` — warm pipeline sequences after handoff or inbound
- `crm-manager` — contacts/deals if pipeline lives in CRM
- `telephony` — Bland/Vapi AI call setup and scripts
