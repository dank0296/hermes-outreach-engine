# BANDA DEMO — PIN THIS

**WHERE:** Hermes container terminal (`root@05c6bc…`)  
**SHOW:** Discord `#outreach-handoffs` (screen share)  
**VOICE:** Talk to Banda on Discord VC only — voice does NOT advance the demo

---

## START (once)

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli agent-demo reset
PYTHONPATH=src python -m outreach_engine.cli agent-demo start
```

---

## EVERY SECTION AFTER THAT

```bash
./next
```

Talk → `./next` → Talk → `./next` → … until **done**

---

## DO / DON’T

| Do | Don’t |
|----|--------|
| Type `./next` in **terminal** | Type only `agent-demo next` (bash won’t know it) |
| **Say** the `💬 SAY:` line out loud to Banda | Type the SAY line into the terminal |
| Screen-share Discord channel | Screen-share secrets / whole messy desktop |
| Pause hard on **HANDOFF** | Rush past the handoff card |

---

## MEETING ORDER

1. Join **Voice** with Banda  
2. **Screen share** Discord → `#outreach-handoffs`  
3. Say: *“Let’s run a live working model.”*  
4. Run **START** block above  
5. Talk using `💬 SAY` hints  
6. `./next` when ready for next beat  
7. On **🚨 HANDOFF** — big pause  
8. Ask: pilot dry-run vs live next? → **stop talking**

---

## IF STUCK

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli agent-demo status
# restart clean:
PYTHONPATH=src python -m outreach_engine.cli agent-demo reset
PYTHONPATH=src python -m outreach_engine.cli agent-demo start
```

---

## ONE-LINER THESIS

> 24/7 cold outreach. You only get pinged when a lead is worth it.

Outbound = dry-run (safe). Discord feed = live.
