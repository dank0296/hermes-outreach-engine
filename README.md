# Hermes Outreach Engine

**24/7 AI outreach that only interrupts you when a lead is worthwhile.**

Built for operators (first vertical: **crypto trading Discord** communities).  
Runs multi-channel sequences (email · SMS · AI voice), scores every lead, and **hands off only when criteria pass**. Everything else stays automated.

> **Dry-run by default.** No live email, SMS, or calls until you explicitly go LIVE.  
> Not a trading bot. Not financial advice. No guaranteed returns language.

**Stack:** [Hermes Agent](https://hermes-agent.nousresearch.com/) · **Grok (xAI)** primary · **OpenRouter** fallback · MIT

---

## The promise

| Cold / junk | You |
|-------------|-----|
| Engine sequences, scores, logs | Get a handoff pack only when bar is met |

Default handoff when **any** of:
- score ≥ 40  
- stage hot / qualified  
- interest reply · pricing ask · demo request · booked call  

Exhausted sequences without signal = **no ping** (logged only).

---

## Quick start

```bash
git clone https://github.com/dank0296/hermes-outreach-engine.git
cd hermes-outreach-engine

# Full canned demo (virtual days, dry-run channels)
PYTHONPATH=src python -m outreach_engine.cli demo

# Or step by step
PYTHONPATH=src python -m outreach_engine.cli init
PYTHONPATH=src python -m outreach_engine.cli list-leads
PYTHONPATH=src python -m outreach_engine.cli tick
PYTHONPATH=src python -m outreach_engine.cli simulate-reply lead_demo_02 "I'd like pricing and a demo call"
PYTHONPATH=src python -m outreach_engine.cli handoffs
```

Expected demo outcome: **1 handoff** (e.g. Aisha Rahman, high score) while tire-kickers stay in sequence or exhaust silently.

---

## CLI

| Command | Description |
|---------|-------------|
| `init` | Seed `data/` + ensure config |
| `import-leads PATH` | CSV or JSON |
| `list-leads` | Show pipeline |
| `score LEAD_ID` | Rescore |
| `tick [--dry-run]` | Process due sequence steps |
| `simulate-reply LEAD_ID "text"` | Inject inbound signal |
| `handoffs` | Pending / recent handoffs |
| `demo` | Full canned dry-run with virtual time |

---

## Architecture (short)

```
Leads → Sequence ticks (email/SMS/call dry-run or live)
     → Score + stage
     → Criteria engine
         ├─ fail → keep nurturing / exhaust
         └─ pass → HANDOFF notify (Telegram-ready) → human takes over
```

| Layer | Choice |
|-------|--------|
| Brain | Hermes Agent |
| Primary model | xAI Grok (SuperGrok / higher tier preferred) |
| Fallback | OpenRouter |
| Email | SMTP / Gmail / Composio (live later) |
| SMS | Twilio |
| Voice | Bland / Vapi (telephony skill) |
| Notify | Telegram / webhook |

Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Hermes skill

Install into a Hermes skills tree:

```bash
mkdir -p ~/.hermes/skills/sales
cp -R skills/outreach-engine ~/.hermes/skills/sales/
```

Triggers: autonomous outreach, handoff criteria, 24/7 sales engine, crypto Discord demo.

---

## Meeting package (10-day demo)

| Doc | Purpose |
|-----|---------|
| [`docs/MEETING-BRIEF.md`](docs/MEETING-BRIEF.md) | One-pager for the room |
| [`docs/10-DAY-PLAN.md`](docs/10-DAY-PLAN.md) | 2026-07-16 → 2026-07-26 |
| [`docs/ICP-CRYPTO-DISCORD.md`](docs/ICP-CRYPTO-DISCORD.md) | Ideal customer profile |
| [`skills/.../references/meeting-demo-script.md`](skills/outreach-engine/references/meeting-demo-script.md) | 8-min live script |
| [`SHARE-BRIEF.md`](SHARE-BRIEF.md) | Social copy-paste |

---

## Safety / compliance

- `dry_run: true` in `config/default.yaml` by default  
- Confirm before any LIVE send  
- Opt-out is terminal  
- Crypto copy includes risk disclaimer; **no ROI guarantees**  
- CAN-SPAM / TCPA: see [`skills/outreach-engine/references/compliance.md`](skills/outreach-engine/references/compliance.md)

---

## Layout

```
src/outreach_engine/     # core package
config/default.yaml      # scoring, handoff, channels, models
demo/leads.json          # 5 fake ICP leads
skills/outreach-engine/  # Hermes skill
docs/                    # architecture, plan, meeting brief
data/                    # runtime (gitignored)
```

---

## License

MIT © 2026 dank0296 / Viking Productions

---

## Status

Working **dry-run demo** ready for client presentation. Live channels = deliberate second phase after criteria + brand voice are locked with the operator.
