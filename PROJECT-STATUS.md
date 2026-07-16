# Hermes Outreach Engine — Project Status

**Client demo:** Friend — crypto trading Discord business  
**Deadline:** ~2026-07-26 (10 days from 2026-07-16)  
**Public repo:** https://github.com/dank0296/hermes-outreach-engine  
**Local path:** `/opt/data/repos/hermes-outreach-engine`  
**Skill install:** `/opt/data/skills/sales/outreach-engine`

## Status: DEMO SHIPPED (dry-run)

- [x] Core engine (store, scorer, criteria, sequences, channels, runner, CLI)
- [x] Hermes skill + compliance + demo script
- [x] Docs + meeting brief + 10-day plan
- [x] Dry-run `demo` CLI green (1 handoff @ score 93)
- [x] Public GitHub push (MIT)

## Demo command

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli demo
```

## Next (toward meeting)

1. Lock friend’s ICP + brand voice + handoff criteria
2. Wire Telegram handoff to home channel
3. Optional: LIVE email/SMS behind confirm (Twilio already on VPS)
4. Rehearse 8-min script from skill references
5. Pricing options A/B/C from MEETING-BRIEF
