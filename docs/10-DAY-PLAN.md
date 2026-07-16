# 10-Day Plan — Hermes Outreach Engine

**Window:** 2026-07-16 → 2026-07-26  
**Goal:** Working **dry-run demo** of 24/7 outreach AI that only escalates worthwhile leads.  
**Audience for day 10:** friend who runs a crypto trading Discord.  
**Author:** dank0296 / Viking Productions  

Principle: ship a credible filter + handoff story, not vapor. No fake performance stats.

---

## Milestones

| Gate | Date | Definition of done |
|------|------|--------------------|
| M0 Scaffold | 2026-07-16 | Repo, docs, config, license |
| M1 Core loop | 2026-07-19 | Tick + sequence + dry messenger |
| M2 Score + handoff | 2026-07-22 | Scoring + criteria gates + operator payload |
| M3 Demo ready | 2026-07-25 | Scripted demo path, sample leads, brief |
| M4 Meeting | 2026-07-26 | Live dry-run demo + pricing conversation |

---

## Day by day

### Day 0 — Thu 2026-07-16 — Scaffold & narrative

**Focus:** product docs and config truth.

- [x] README, LICENSE (MIT), architecture, ICP, meeting brief, share brief  
- [x] `config/default.yaml` with dry_run, scoring, handoff, sequence, models  
- [x] demo README + .gitignore  
- [ ] Confirm Grok primary + OpenRouter fallback access for build days  

**Exit:** anyone can read the repo and understand the promise: *you only talk to leads that meet criteria.*

---

### Day 1 — Fri 2026-07-17 — Data model & store

**Focus:** durable lead state for the demo.

- [ ] Implement Lead / MessageEvent / ScoreEvent / HandoffEvent (SQLite or JSON store)  
- [ ] Seed loader for sample leads (crypto Discord personas)  
- [ ] Unit tests for create/update/due-query  

**Exit:** can load N sample leads and list who is due.

---

### Day 2 — Sat 2026-07-18 — Sequence engine

**Focus:** multi-step outreach without model dependency first.

- [ ] Sequence step scheduler (delays, stop rules)  
- [ ] Template stubs for intro → value_nudge → intent_check → soft_close  
- [ ] Opt-out / suppress path  

**Exit:** dry advance of a lead through all steps with frozen clock.

---

### Day 3 — Sun 2026-07-19 — Tick loop + dry messenger — **M1**

**Focus:** always-on skeleton.

- [ ] Tick runner (interval, batch caps, jitter)  
- [ ] Dry messenger logs simulated DMs  
- [ ] Audit log for skip/send/schedule  
- [ ] CLI: `run-tick` / `run-demo`  

**Exit:** one command runs a full dry cycle end-to-end on sample data.

---

### Day 4 — Mon 2026-07-20 — Model wiring

**Focus:** Grok primary, OpenRouter fallback.

- [ ] Model router with failover  
- [ ] Prompt pack: draft message, extract signals from reply, handoff talking points  
- [ ] Content rules: no guaranteed returns, no financial advice  

**Exit:** generated copy for one step looks operator-safe and on-brand.

---

### Day 5 — Tue 2026-07-21 — Scorer

**Focus:** explainable scores.

- [ ] Weighted scorer (intent / engagement / fit / recency)  
- [ ] Signal extractors from message history  
- [ ] Score breakdown object for handoff  

**Exit:** two leads with different histories produce clearly different scores + reasons.

---

### Day 6 — Wed 2026-07-22 — Handoff pipeline — **M2**

**Focus:** the product promise.

- [ ] Gate evaluation from config thresholds  
- [ ] Handoff queue + operator payload formatter  
- [ ] Stop sequence on handoff; cooldown  
- [ ] Demo path: force one high-intent lead → handoff, one low → no handoff  

**Exit:** demo script shows *silence* on junk and *alert* on qualified lead.

---

### Day 7 — Thu 2026-07-23 — Discord-shaped demo layer

**Focus:** look real without going live.

- [ ] Sample “Discord member” personas + channel activity tags  
- [ ] Simulated inbound replies for 2–3 scripted arcs  
- [ ] Operator handoff message formatted like a Discord embed/text block  

**Exit:** walkthrough feels like a Discord operator workflow in dry-run.

---

### Day 8 — Fri 2026-07-24 — Hardening

**Focus:** safety and polish.

- [ ] Rate limits, blocklist, opt-out keywords verified  
- [ ] Failover test (primary fail → OpenRouter)  
- [ ] Config validation errors are human-readable  
- [ ] README install path matches reality  

**Exit:** no foot-guns for live flip later; dry-run still default.

---

### Day 9 — Sat 2026-07-25 — Demo pack — **M3**

**Focus:** meeting readiness.

- [ ] `demo/README.md` steps timed (~10–15 min)  
- [ ] Rehearse MEETING-BRIEF live path  
- [ ] Capture 1–2 screenshots or terminal recordings (no fake metrics)  
- [ ] Pricing options finalized for full build conversation  

**Exit:** can run demo cold from a clean shell.

---

### Day 10 — Sun 2026-07-26 — Meeting — **M4**

**Focus:** present, don’t oversell.

- [ ] Live dry-run demo  
- [ ] Walk handoff criteria and ICP  
- [ ] Discuss full-version scope + pricing options  
- [ ] Capture feedback → backlog  

**Exit:** clear yes / iterate / no — and a written next step.

---

## Risk register (build window)

| Risk | Mitigation |
|------|------------|
| Model access flaky | OpenRouter fallback; template-only path for demo if needed |
| Scope creep (live Discord) | Live send is **out of scope** for day 10; dry-run is the product |
| Fake metrics temptation | Demo shows process + gates, not invented conversion rates |
| Copy sounds like financial advice | System prompts + content_rules + manual review day 8–9 |

---

## Definition of done (meeting demo)

1. `dry_run: true` path runs without real DMs  
2. At least one lead **does not** hand off (below criteria)  
3. At least one lead **does** hand off with score breakdown + context  
4. Operator can explain criteria in one sentence: *you only talk to leads that meet criteria*  
5. Stack story clear: Hermes + Grok primary + OpenRouter backup  

---

## Post-meeting (if green light)

- Live Discord adapter behind explicit flag  
- Operator channel wiring  
- Production secrets + hosting  
- Sequence tuning on real (consented) traffic  
