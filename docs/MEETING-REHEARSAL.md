# Meeting Rehearsal — Flawless Demo (train yourself)

**Status:** DEMO-READY for dry-run + live Discord handoff  
**Audience:** Friend — crypto trading Discord  
**WHERE to run commands:** **Hermes container** (`root@05c6bc…`, `/opt/data` exists)  
**Not:** bare VPS host paths unless you map `/docker/hermes-agent-0gbq/data/`

---

## Are we meeting-ready?

| Gate | Status |
|------|--------|
| Repo + docs + meeting brief | ✅ |
| Core engine + dry-run sequences | ✅ |
| Handoff scoring / criteria | ✅ |
| Discord `#outreach-handoffs` private channel | ✅ |
| Live Discord webhook test (204) | ✅ |
| Hermes skill + compliance notes | ✅ |
| Live email/SMS/calls | ❌ **by design** (dry-run) — say this proudly |
| Friend’s real lead list / brand voice | ⏳ lock in meeting |
| Your 1× full rehearsal out loud | ⏳ **you do this now** |

**Verdict: Yes — meeting-ready for a dry-run product demo.**  
Not “production live spam.” That’s correct for trust.

---

## The one sentence (tattoo this)

> “It works 24/7 on cold outreach. **You only get pinged when a lead meets your bar** — then you take over.”

---

## Room setup (T−10 min)

1. **Hermes container** terminal open, font large  
2. Discord open on **Dank AI → `#outreach-handoffs`** (friend can see if you invited him)  
3. Optional: browser tab to repo README  
4. Pre-flight:

```bash
# WHERE: Hermes container
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli notify-diagnose
# expect: ready true, webhook_configured true
```

---

## Exact command path (correct CLI — memorize)

```bash
# WHERE: Hermes container
cd /opt/data/repos/hermes-outreach-engine

# 1) Full story in one shot (virtual days, dry channels)
PYTHONPATH=src python -m outreach_engine.cli demo

# 2) Show pipeline after demo
PYTHONPATH=src python -m outreach_engine.cli list-leads
PYTHONPATH=src python -m outreach_engine.cli handoffs

# 3) Optional live handoff ping (second wow)
PYTHONPATH=src python -m outreach_engine.cli notify-test --live

# 4) Interactive “make this lead hot” (if you skip full demo)
PYTHONPATH=src python -m outreach_engine.cli init
PYTHONPATH=src python -m outreach_engine.cli import-leads demo/leads.json
PYTHONPATH=src python -m outreach_engine.cli list-leads
PYTHONPATH=src python -m outreach_engine.cli simulate-reply lead_demo_02 "Interested — what's pricing? Can we book a call?"
PYTHONPATH=src python -m outreach_engine.cli handoffs
```

**Note:** `simulate-reply` is positional: `LEAD_ID` then `"text"` — not `--lead-id`.

---

## 8-minute script (say this)

### 0:00–0:45 — Hook
> “Most operators drown in cold DMs. This is a Hermes agent that sequences email, SMS, and AI voice 24/7. **You don’t babysit cold leads.** You only get a Discord ping when someone clears your criteria.”

Point at Discord `#outreach-handoffs`.

### 0:45–2:30 — Run the engine
Run: `demo`  
While it scrolls:
> “Watch — five fake trader leads. Day 0 email, day 2 SMS, later email and call script. Everything outbound is **dry-run** — logged, not sent. Crypto copy has risk language — no guaranteed returns.”

### 2:30–4:00 — The filter
When summary prints (1 handoff, others exhausted):
> “Aisha replied with pricing + demo interest — score 93, handed off.  
> Marcus and the tire-kickers burned the sequence and **never rang you**.  
> That’s the product: attention filter, not a spam cannon.”

### 4:00–5:30 — Live handoff wow
Run: `notify-test --live`  
Discord lights up:
> “That’s your take-over card — name, score, why, contact. Engine pauses that lead so you don’t double-message.”

### 5:30–6:30 — Compliance / LIVE gate
> “Live email/SMS/calls stay off until you say so. We honor opt-out. We don’t promise trading profits. You own list consent and brand voice — we own the automation loop.”

### 6:30–8:00 — Ask (stop talking after)
> “Does criteria-first match how you want to spend time?  
> Want pilot on dry-run with your ICP, or wire live Twilio/Gmail next?  
> Options: Pilot / Operator / Full — we can price after we lock scope.”

**Then shut up.** Write notes.

---

## Objection drill (practice out loud)

| They say | You say |
|----------|---------|
| “Can it guarantee members / money?” | “No. It’s a qualification engine, not a trading signal bot. More good conversations, less junk time.” |
| “Just spam my list.” | “We won’t. Dry-run first, consent and rate limits before LIVE. Burned Discord = dead brand.” |
| “Why not ChatGPT paste?” | “This is state + sequence + score + handoff + channels on a schedule — not a one-off chat.” |
| “I want it in *my* Discord.” | “Customer Discord stays clean. Handoffs land in a private ops channel — can be yours later.” |
| “What about legal?” | “Guardrails + no ROI claims + STOP. Not legal advice; list compliance is on the operator.” |
| “Show live SMS.” | “We can next phase with Twilio — today I won’t fire real texts in a first meeting.” |

---

## Flawless meeting rules

1. **One thesis** every 2 minutes — handoff filter  
2. **Never** send live cold email/SMS “to prove it”  
3. **Never** invent ROI stats  
4. If CLI glitches → open Discord last handoff + README architecture — still win  
5. End with **their** answer, not more features  

---

## Post-meeting capture

- [ ] Handoff bar he wants (score / signals)  
- [ ] Brand voice notes  
- [ ] LIVE channels wanted (email / SMS / call)  
- [ ] Option A/B/C interest  
- [ ] Consent status of his list  

---

## Your homework (before the real meeting)

Do **twice** out loud, timer 8 minutes:

1. Pre-flight diagnose  
2. `demo`  
3. Point at Discord  
4. `notify-test --live`  
5. Close + ask  

Second run should feel boring. Boring = ready.
