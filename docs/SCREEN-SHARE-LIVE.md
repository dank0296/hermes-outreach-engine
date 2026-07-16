# Screen-share working model (what he actually wants)

`present` = slide cards (fine for intro).  
**`live`** = working model in action — activity stream he can watch on screen share.

## What he sees (Discord `#outreach-handoffs`)

A real-time ops feed:

1. 🟢 Engine online  
2. 📥 5 leads enrolled  
3. 📧 Email tick (dry-run)  
4. 👁️ Opens (no owner ping)  
5. 💬 SMS tick (dry-run)  
6. 🔥 **Aisha replies** (pricing + demo)  
7. 📈 Score → 93 qualified  
8. 🚨 **OWNER HANDOFF** (your turn)  
9. 🤖 Cold leads keep running — no pings  
10. 🗄️ Pipeline snapshot (1 handoff / 4 exhausted)

Feels like the system is **running**, not a pitch deck.

---

## Meeting flow (screen share)

### Setup (30s)
1. Discord full screen → **`#outreach-handoffs`**  
2. Hermes container ready in background (he doesn’t need to see it)  
3. Optional: hide terminal after you hit Enter  

### Start the model

```bash
# WHERE: Hermes container
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli live --pace 3
```

`--pace 3` = ~3 seconds between events (good for talking).  
Faster demo: `--pace 2`  
Slower teaching: `--pace 4`

### What you say (while feed runs)

| Event on screen | You say |
|-----------------|---------|
| Engine online | “This is the live ops feed. Outbound is simulated; handoffs are real in this channel.” |
| Enrolled / email / SMS | “It’s working the list 24/7. Opens alone don’t bother you.” |
| Aisha reply | “Here’s a real intent reply — pricing + demo.” |
| Score 93 | “Criteria engine scores it. Bar cleared.” |
| **HANDOFF** | “Only now do you get interrupted. You take the relationship.” |
| Others exhaust | “Junk stays automated. That’s the product.” |

### Close
> “That’s a working model. Next we plug your ICP and only go live when you say so.”

---

## vs `present` vs `demo`

| Command | Feels like | Use when |
|---------|------------|----------|
| `live` | **Working system** on screen share | Main meeting demo ← **this** |
| `present` | Pitch cards | Optional 30s intro |
| `demo` | Terminal logs | Dev / backup only |

---

## One-liner for him

> “You’re watching the agent work. Cold stays quiet. Worth-it leads land here.”
