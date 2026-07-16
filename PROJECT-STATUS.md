# Hermes Outreach Engine — Project Status

**Client demo:** Friend — crypto trading Discord business  
**Deadline:** ~2026-07-26 (10 days from 2026-07-16)  
**Repo (target):** https://github.com/dank0296/hermes-outreach-engine  
**Local path:** `/opt/data/repos/hermes-outreach-engine`

## Product thesis

24/7 multi-channel outreach (email / SMS / AI voice) that **only interrupts the owner when a lead meets handoff criteria**. Cold work is fully agent-run.

## Stack

| Layer | Choice |
|-------|--------|
| Brain | Hermes Agent |
| Primary model | xAI Grok (SuperGrok / $300 tier preferred) |
| Fallback | OpenRouter |
| Email | Gmail SMTP / Composio (live later) |
| SMS | Twilio (creds present on VPS) |
| Voice | Bland / Vapi via telephony skill |
| Notify | Telegram home channel |
| Default mode | **dry_run** (demo-safe) |

## Build status

- [x] Repo scaffold
- [ ] Core engine (subagent)
- [ ] Hermes skill (subagent)
- [ ] Docs + meeting brief (subagent)
- [ ] Dry-run demo green
- [ ] Public GitHub push

## Commands (once core lands)

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli demo
```

## Owner take-over trigger (default)

Handoff when **any**:
- score ≥ 40
- stage hot/qualified
- interested reply
- booked call / pricing ask / demo request

Exhausted sequences = no handoff (logged only).
