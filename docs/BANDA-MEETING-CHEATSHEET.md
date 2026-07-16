# BANDA MEETING — PIN THIS

**WHERE:** Hermes container terminal  
**SHOW:** Discord `#outreach-handoffs` (screen share)  
**VOICE:** Talk to Banda — does **not** run the agent  

**Pre-brief for Banda:** `docs/BANDA-PRE-MEETING-BRIEF.md`  
(Share before meeting — he picks option 1 / 2 / 3)

---

## MEETING FLOW

### Part A — Explain (YOU pace) · ~8–12 min · skippable
```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli agent-demo reset
PYTHONPATH=src python -m outreach_engine.cli agent-demo start
./next
# talk → ./next → talk → ./next … until done
```

### Part B — Visual Hermes agent (HE watches) · ~6–10 min ⭐
```bash
cd /opt/data/repos/hermes-outreach-engine
./visual-demo
# slower: ./visual-demo 6
```

No `./next` — agent streams think → tool → result by itself.

---

## ORDER

| If Banda chose… | You run |
|-----------------|---------|
| **1 Full** | Part A → then Part B |
| **2 Visual first** | Part B first → explain only if asked |
| **3 Visual only** | Part B → thesis → ask |

**Always:** big pause on HANDOFF → ask pilot vs live → **stop talking**

---

## Thesis

> Hermes works cold 24/7. You only get pinged when a lead is worth it.

Outbound = dry-run. Discord = live. No Kasm required for this meeting.
