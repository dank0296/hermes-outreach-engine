# Banda meeting — talk-paced + real engine

## Problem
`live --pace 3` is too fast. You need time to talk, then advance.

## Two modes for the meeting

### 1) Interactive cards (you control the clock)
```bash
# WHERE: Hermes container
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli step start
# talk...
PYTHONPATH=src python -m outreach_engine.cli step next
# talk...
PYTHONPATH=src python -m outreach_engine.cli step next
# ... until done
```

### 2) REAL engine working model (what he asked for) ⭐
Uses real store, tick(), scorer, handoff — not a slideshow script.

```bash
# WHERE: Hermes container
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli agent-demo start
# talk over Discord card...
PYTHONPATH=src python -m outreach_engine.cli agent-demo next
# repeat until "done"
```

Outbound still **dry-run**. Discord feed is **live**.

---

## Meeting flow with Banda (recommended)

| Phase | What |
|-------|------|
| VC + screen share | `#outreach-handoffs` |
| Optional intro | 30s thesis |
| **“Let’s run a live working model”** | `agent-demo start` |
| Each beat | Talk → `agent-demo next` |
| Handoff card | Big pause — product moment |
| Close | Pilot vs live? |

---

## Cheatsheet on second monitor

```
agent-demo start
agent-demo next   ← mash this when done talking
agent-demo status
agent-demo reset
```

Talk hints print in the terminal after each next (`💬 SAY: ...`).

---

## vs old commands

| Command | Speed | Real engine? |
|---------|-------|----------------|
| `live --pace 3` | Auto-fast | No (scripted feed) |
| `step next` | Manual | No (scripted feed) |
| **`agent-demo next`** | Manual | **Yes** |
| `agent-demo auto --pace 4` | Auto-slow | Yes |
