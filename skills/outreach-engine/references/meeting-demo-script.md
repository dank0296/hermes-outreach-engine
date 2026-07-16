# Meeting Demo Script — 8 Minutes

**Audience:** Friend / client — crypto trading Discord business  
**Goal:** Prove Hermes runs cold multi-channel outreach 24/7 and only pings the human when a lead is worth taking over.  
**Mode:** Dry-run only (`DRY_RUN=true`). Label every “send” as simulated.

---

## Setup (before they sit down) — T-5 min

```bash
cd /opt/data/repos/hermes-outreach-engine
# Confirm dry-run
grep DRY_RUN .env .env.example 2>/dev/null || true
PYTHONPATH=src python -m outreach_engine.cli status
```

- Terminal font large; split pane optional (CLI + handoff preview)
- Have one sample lead ready (name, email, phone placeholders)
- Telegram handoff chat open if notify preview is wired; otherwise show logged alert text

---

## Minute 0:00–0:45 — Hook

**Say:**

> “Most people burn hours chasing cold leads. This engine works 24/7 on email, SMS, and AI voice. You only get a ping when someone is actually worth your time.”

**Show:** one-line architecture (brain → store/scorer → channels → handoff notify).

---

## Minute 0:45–2:00 — Import + enroll (dry)

**Do:**

```bash
PYTHONPATH=src python -m outreach_engine.cli demo
# or: import + enroll if demo is a single umbrella command
PYTHONPATH=src python -m outreach_engine.cli status
```

**Say:**

> “Leads land in the store, get enrolled in the crypto-Discord sequence. Default is dry-run — nothing leaves this machine.”

**Point at:** sequence steps (email → SMS → email → AI call → …) without reading every template.

---

## Minute 2:00–3:30 — Tick a cold touch

**Do:**

```bash
PYTHONPATH=src python -m outreach_engine.cli tick
# or send dry-run for one channel
PYTHONPATH=src python -m outreach_engine.cli send --lead-id <ID> --channel email --dry-run
```

**Say:**

> “Here’s the email that would go out — value first, no ‘guaranteed profits’ garbage. Logged only.”

**Show:** touch log payload preview. Mention SMS/Twilio and AI call adapters exist the same way.

---

## Minute 3:30–5:00 — Simulate interest → score

**Do:**

```bash
PYTHONPATH=src python -m outreach_engine.cli simulate-reply \
  --lead-id <ID> \
  --text "Interested — what's pricing for the Discord? Can we hop on a call?"
PYTHONPATH=src python -m outreach_engine.cli score --lead-id <ID>
```

**Say:**

> “Cold replies get scored. Opens alone don’t wake you. Pricing + call intent pushes score and stage into handoff range.”

**Show:** score ≥ 40 and/or stage `hot` / `qualified`.

---

## Minute 5:00–6:30 — Handoff only

**Do:**

```bash
PYTHONPATH=src python -m outreach_engine.cli handoff --lead-id <ID>
```

**Say:**

> “This is the only time the system bothers you — a single handoff alert with context. Exhausted cold leads never ring your phone.”

**Show:** handoff alert shape (name, score, why, last messages, suggested next action). If Telegram preview: `[DEMO]` tag.

**Contrast:** “If they go silent through the sequence, we mark exhausted and log it. No babysitting.”

---

## Minute 6:30–7:30 — Live gate + compliance one-liner

**Say:**

> “Live mode is gated. I need your explicit go-ahead before any real email, SMS, or call. We honor STOP immediately, and we never promise guaranteed trading returns.”

**Optional show:** `.env.example` with `DRY_RUN=true` and channel keys blank/redacted.

---

## Minute 7:30–8:00 — Close + ask

**Say:**

> “In ten days this is the loop: import → autonomous sequence → you only talk to hot leads. Want us to wire your real Twilio/Gmail next, or keep it demo until list consent is clean?”

**Stop talking.** Take their answer. Note follow-ups (consent, brand voice, Discord invite link, calendar link for handoff).

---

## Fallback if CLI not fully wired yet

If a subcommand is missing mid-meeting:

1. Show skill + templates (`skills/outreach-engine/`) as the operating contract
2. Walk architecture diagram from `references/architecture.md`
3. Read one email + one SMS from `templates/sequence-crypto-discord.md`
4. Read handoff template aloud as the owner notification

Still hit the thesis: **engine works cold; human only on handoff.**

---

## Anti-patterns during the demo

- Do not send a real message “just to show it works”
- Do not invent ROI guarantees when they ask “does this make money”
- Do not drown them in code — stay on outcomes and the handoff moment
- Do not promise TCPA/CAN-SPAM “all handled” — say guardrails + owner responsibility

## Post-meeting checklist

- [ ] Capture feedback (must-have channels, tone, CRM)
- [ ] Confirm whether LIVE credentials are in scope
- [ ] File any missing CLI gaps as build tasks for remaining days
- [ ] Leave them with: dry-run by default, handoff criteria defaults, no spam thesis
