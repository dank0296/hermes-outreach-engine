# Present in Discord (user-friendly)

You do **not** need to understand the terminal for the meeting.

## The idea

| Old way (confusing) | New way (this) |
|---------------------|----------------|
| Friend watches CLI scroll | Friend watches **`#outreach-handoffs`** |
| You explain code | You point at Discord cards |
| Many commands | **One command** |

---

## Meeting day — 3 steps

### 1. Open Discord
Dank AI server → private channel **`#outreach-handoffs`**  
(Invite friend with View permission if needed.)

### 2. Run ONE command

```bash
# WHERE: Hermes container (root@05c6bc…, /opt/data works)
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli present
```

Terminal will print boring status. **Ignore it.**  
Look at Discord — cards appear top → bottom.

### 3. Talk while cards appear

You only need these lines:

| Discord card | You say |
|--------------|---------|
| **MEETING DEMO** | “24/7 outreach agent. You only get pinged when a lead is worth it.” |
| **How it works** | “Sequence → score → handoff. Cold stays automated.” |
| **Simulated outreach** | “Five fake traders. Outbound is dry-run — nothing really sent.” |
| **🚨 Handoff Aisha** | “She hit pricing + call. **This** is when you take over.” |
| **Results 1 of 5** | “One handoff. Four never woke you. That’s the product.” |
| **Close** | “Criteria-first. Pilot dry-run with your list, or live next?” |

Then **stop talking**.

---

## If something breaks

Still win:
1. Scroll `#outreach-handoffs` for last Aisha handoff embed  
2. Say the one-liner: *you only talk to leads that meet criteria*  
3. Offer pilot  

---

## Optional: slower pacing

```bash
# WHERE: Hermes container
PYTHONPATH=src python -m outreach_engine.cli present --pause 3
```

Gives you ~3 seconds between cards to talk.
