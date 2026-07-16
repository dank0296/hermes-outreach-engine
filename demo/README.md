# Demo — Hermes Outreach Engine

How to run the **dry-run** demo. Nothing is sent to real Discord users while `dry_run: true`.

**Promise under test:** junk leads stay automated; worthwhile leads hit the handoff queue with context.  
**You only talk to leads that meet criteria.**

---

## Prerequisites

- Repo cloned; shell at repo root or `demo/`  
- Python 3.11+ recommended  
- Config: `config/default.yaml` (default already safe)  
- Optional for live model drafts: `XAI_API_KEY` (Grok) and/or `OPENROUTER_API_KEY`  
  - Without keys, demo should still run on templates / fixtures when implemented  

---

## Safety check (do this first)

```bash
# From repo root
grep -n "dry_run" config/default.yaml
# Expect: dry_run: true
```

Do **not** set live Discord tokens or `dry_run: false` for the meeting demo.

---

## Meeting path (~10–15 min)

### 1. Show the product frame

Open:

- [../README.md](../README.md) — one-screen pitch  
- [../docs/MEETING-BRIEF.md](../docs/MEETING-BRIEF.md) — problem / solution  
- [../config/default.yaml](../config/default.yaml) — thresholds  

Call out: `handoff.min_score`, `require_any_intent`, sequence steps.

### 2. Load sample leads

When sample data and CLI exist:

```bash
# Example interface (as implemented in build days)
python -m outreach_engine.demo load-leads --config config/default.yaml
python -m outreach_engine.demo list-leads
```

Expect mixed personas (see [../docs/ICP-CRYPTO-DISCORD.md](../docs/ICP-CRYPTO-DISCORD.md)): engaged trader vs lurker vs giveaway hunter.

### 3. Run one tick (dry-run)

```bash
python -m outreach_engine.demo run-tick --config config/default.yaml
# or
python -m outreach_engine.demo --config config/default.yaml
```

Expect:

- Simulated outbound messages printed (not sent)  
- Audit lines for schedule / skip / send(sim)  

### 4. Apply scripted replies

```bash
python -m outreach_engine.demo apply-replies --scenario high_vs_low
python -m outreach_engine.demo run-tick --config config/default.yaml
```

Expect different score trajectories.

### 5. Show handoff queue

```bash
python -m outreach_engine.demo handoffs
```

Expect:

- **High-intent / high-fit lead** present with score breakdown + last messages  
- **Low-signal lead** absent (still in sequence or archived)  

If both hand off, thresholds are too loose — raise `min_score` or tighten intent gates live in config and re-run.

### 6. Show a safety path

```bash
python -m outreach_engine.demo apply-replies --scenario opt_out
python -m outreach_engine.demo run-tick
```

Expect suppress + no further messages.

---

## Config knobs to tweak live in the room

| Knob | File | Effect |
|------|------|--------|
| `dry_run` | `config/default.yaml` | Must stay `true` for demo |
| `handoff.min_score` | same | Raise → fewer handoffs |
| `handoff.require_any_intent` | same | Intent gate list |
| `scoring.weights` | same | Emphasize fit vs intent |
| `sequence.steps` | same | Cadence of nurture |

Copy to `config/local.yaml` for experiments; keep secrets out of git.

---

## If implementation is mid-build

Until the CLI is complete, walk the room through:

1. Architecture diagram in [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)  
2. Config as source of truth  
3. 10-day plan status in [../docs/10-DAY-PLAN.md](../docs/10-DAY-PLAN.md)  
4. Any available partial command output  

Be explicit: “demo path shipping on the 10-day plan; dry-run contract already locked.”

---

## After the demo

- Capture feedback on thresholds and brand voice  
- Decide pilot option (see Meeting Brief pricing table)  
- Only then discuss live Discord adapter and tokens  

---

## Related

- [../docs/MEETING-BRIEF.md](../docs/MEETING-BRIEF.md)  
- [../docs/ICP-CRYPTO-DISCORD.md](../docs/ICP-CRYPTO-DISCORD.md)  
- [../SHARE-BRIEF.md](../SHARE-BRIEF.md)  
