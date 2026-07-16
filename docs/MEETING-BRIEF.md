# Meeting Brief — Hermes Outreach Engine

**One-pager · 2026-07-26 demo**  
**From:** dank0296 / Viking Productions  
**To:** Operator — crypto trading Discord  
**Mode:** founder-to-founder · dry-run demo · no hype stats  

---

## Problem

You run a trading Discord. Attention is the scarce resource.

- DMs and “interested” pings don’t scale  
- Most outreach is noise: lurkers, giveaway hunters, half-curious browsers  
- Manual follow-up is inconsistent  
- When a *real* lead shows up, context is scattered  

You don’t need more messages. You need a **filter** so human time only hits people who meet your bar.

---

## Solution

**Hermes Outreach Engine** — a 24/7 outreach agent that:

1. Runs multi-step sequences (intro → value → intent → soft close)  
2. Scores every lead (intent · engagement · fit · recency)  
3. **Hands off only when criteria pass**  
4. Stays quiet otherwise  

**Promise:** you only talk to leads that meet criteria.

Not a trading bot. Not guaranteed closes. Not financial advice automation. A qualification + escalation system on Hermes, with Grok primary and OpenRouter fallback.

---

## Live demo steps (~10–15 min)

All steps use **`dry_run: true`** — no real DMs.

| # | Step | What you’ll see |
|---|------|------------------|
| 1 | Open config | `dry_run`, handoff `min_score`, sequence steps |
| 2 | Load sample leads | Mixed ICP fit: tire-kicker vs engaged trader persona |
| 3 | Run one tick | Simulated outbound messages logged, not sent |
| 4 | Inject / show replies | Low-intent vs high-intent response arcs |
| 5 | Re-score | Score breakdown (why high / why low) |
| 6 | Handoff queue | **Only** the qualified lead appears with context pack |
| 7 | Safety | Opt-out / rate-limit behavior called out |

**Success criterion for the room:** junk stays automated; worthwhile lead surfaces with “why now.”

Commands: see [../demo/README.md](../demo/README.md).

---

## Pricing options — full version build

Indicative scopes for discussion (not a formal quote). Adjust after feedback.

| Option | Scope | Best for |
|--------|--------|----------|
| **A — Pilot** | Dry-run hardened + your ICP/sequence tuned + handoff to a channel you choose; limited live behind flag | Validate on your community rules without chaos |
| **B — Operator** | Live Discord adapter, operator handoff formatting, audit log, rate limits, weekly tuning window (e.g. 30 days) | Run for real with guardrails |
| **C — Full** | Multi-sequence, dashboard/queue, Telegram or email adapter #2, runbooks, handoff SLA design | Scale across channels / team |

Commercial structure (pick one in conversation):

- **Fixed build** for A/B/C milestones + optional monthly care  
- **Build + retain** if you want ongoing sequence/model ops  
- **No revenue-share on trades** — this is software/ops, not a signal desk  

Exact numbers agreed live; docs intentionally avoid invented market prices.

---

## Tech

| Piece | Choice |
|-------|--------|
| Runtime | Hermes Agent |
| Primary model | Grok (xAI) — SuperGrok / higher tier preferred for load |
| Fallback | OpenRouter |
| Config | YAML thresholds (score, sequence, safety) |
| Default mode | dry_run |
| License (this repo) | MIT |

Architecture detail: [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Risks

| Risk | Honest take |
|------|-------------|
| Spam / ban risk on live Discord | Real — mitigated by dry-run default, rate limits, consent-aware rollout, operator review |
| Model quality / tone | Mitigated by templates + review + failover; still needs human taste |
| Over-automation | Product is built to **under**-notify; if handoffs are noisy, raise thresholds |
| Legal / compliance | Not legal advice; no guaranteed returns language; operator owns community ToS and local rules |
| Scope creep | Day-10 demo is dry-run only; live is a deliberate second phase |

---

## Ask

1. Does the **criteria-first** model match how you want to spend time?  
2. Which handoff bar feels right (score / intent signals / min replies)?  
3. Interest in Option A/B/C — and any hard constraints (ToS, mods, brand voice)?  

---

*Next step if aligned: lock pilot scope, ICP tags, and handoff channel — then leave dry_run only when you say so.*
