# Banda is here — full meeting muscle memory

**Audience:** Banda (crypto trading Discord)  
**You:** Operator / presenter  
**Stage:** Discord `#outreach-handoffs` on screen share  
**Engine:** Hermes container, one command  

Do this **twice** without stopping. Second time should feel automatic.

---

## T−10 min (before Banda “arrives”)

Do these alone, once, then freeze.

### Desk layout
1. **Monitor 1 (shared):** Discord full screen → Dank AI → `#outreach-handoffs` → scrolled to **bottom**
2. **Monitor 2 or corner (not shared):** Hermes terminal ready
3. Water / notes: blank page for his answers

### Terminal pre-positioned (don’t run yet)

```bash
# WHERE: Hermes container
cd /opt/data/repos/hermes-outreach-engine
# leave this typed, cursor ready — do NOT press Enter until Step 4
PYTHONPATH=src python -m outreach_engine.cli live --pace 3
```

### 10-second health check (optional)

```bash
PYTHONPATH=src python -m outreach_engine.cli notify-diagnose
```

Want: `"ready": true`  
Then re-type the `live` line and wait.

### Discord
- Friend (Banda) can view `#outreach-handoffs` (or he watches your share)
- Mute unrelated channels / DMs

**Freeze. You’re meeting-ready.**

---

## T−0 — Banda sits down (or you pretend)

### Step 1 — Hello (30 sec) · no laptop heroics
**Do:** Face him. Discord already open on share.

**Say:**
> “Banda — I built a working model of a 24/7 outreach agent for your Discord business.  
> You won’t babysit cold leads. You only get pinged when someone is worth your time.  
> I’m going to screen-share the live ops channel and run the engine once.”

**Don’t:** open GitHub, don’t scroll terminal.

---

### Step 2 — Screen share Discord (20 sec)
**Do:**
1. Share **Discord window** (or full screen with only Discord visible)
2. Confirm he sees `#outreach-handoffs`
3. Point at the channel name

**Say:**
> “This private channel is the handoff feed. In production it can live on your ops server.  
> Outbound email/SMS today is simulated. What you’ll see here is the engine working.”

---

### Step 3 — Thesis (15 sec) · still no Enter
**Say:**
> “Watch for three things only:  
> 1) it works the list,  
> 2) opens don’t wake you,  
> 3) a real reply hands off to you.”

---

### Step 4 — Start the working model (you hit Enter)
**Do:** On the unshared (or tiny) terminal — **Enter** on:

```bash
PYTHONPATH=src python -m outreach_engine.cli live --pace 3
```

**Immediately:** eyes back to Discord.  
**Say:**
> “Engine’s live. Ops feed is this channel.”

---

### Step 5 — Talk over the stream (muscle memory lines)

| When Discord shows | You do | You say (out loud) |
|--------------------|--------|---------------------|
| 🟢 Engine online | Point | “Online. Dry-run outbound. Live handoffs here.” |
| 📥 Batch enrolled | Point at 5 names | “Five trader leads enrolled — your kind of ICP.” |
| 📧 Email tick | Point | “Day 0 email — logged, not really sent.” |
| 👁️ Opens | Point | “Opens only. **No ping to you.**” |
| 💬 SMS tick | Point | “Day 2 SMS bump — still automated.” |
| 🔥 Aisha reply | **Pause** | “Stop — she asked pricing and a demo. Real intent.” |
| 📈 Score 93 | Point | “Scored 93. Criteria cleared.” |
| 🚨 OWNER HANDOFF | **Big pause** | “**This** is your moment. Engine paused her. You take the relationship.” |
| 🤖 Background cold | Point | “Others keep running. You never hear about them.” |
| 🗄️ Snapshot | Point at 1 vs 4 | “Five in. One handoff. Four never touched your day.” |
| ⏭️ Complete | Face Banda | “That’s the working model.” |

---

### Step 6 — Silence (3 full seconds)
Let him look at the last cards. **Do not fill silence.**

---

### Step 7 — Close + ask (then stop)
**Say:**
> “Criteria-first. You only talk to worthwhile leads.  
> Does that match how you want to spend time?  
> Want a pilot dry-run on your ICP next, or wire live email/SMS after list consent is clean?”

**Then stop talking.**  
Write his answer on the blank page.

---

### Step 8 — Capture (if he engages)
Ask only if needed:
1. Handoff bar (what’s “worth it” for him)?  
2. Brand voice (aggressive vs calm education)?  
3. Channels: email / SMS / calls priority?  
4. List consent status?

---

### Step 9 — End clean
**Say:**
> “I’ll leave the feed as the record of this run. Next step is your list + voice, still dry-run until you green-light live.”

Stop sharing. Done.

---

## Full timeline (practice with phone timer)

| Clock | Action |
|------:|--------|
| 0:00 | Hello + thesis |
| 0:30 | Screen share Discord |
| 0:50 | “Three things to watch” |
| 1:00 | **Enter** on `live --pace 3` |
| 1:00–2:30 | Talk over feed (table above) |
| 2:30 | 3-second silence |
| 2:35 | Close + ask |
| 3:00 | Listen / notes |

Target: **under 5 minutes** for the demo core. Discussion after is free.

---

## Muscle-memory drills (do in order)

### Drill 1 — Hands only (no talking) × 1
- Open Discord channel  
- Type `live` command  
- Enter  
- Confirm stream at bottom  
- Stop  

### Drill 2 — Mouth only × 1  
- Don’t run engine  
- Scroll last successful run in `#outreach-handoffs`  
- Say every line in the table out loud  

### Drill 3 — Full Banda sim × 2  
- Timer on  
- Full script Steps 1–7  
- Pretend he asks: “Can it guarantee members?”  
  **Answer:** “No. More good conversations, less junk time — not a signal bot.”  

---

## Panic card (if something breaks mid-meeting)

| Problem | Do this |
|---------|---------|
| No new Discord posts | “One sec” → check terminal for 204 → re-run `live --pace 2` |
| Terminal error | Scroll to last good **HANDOFF Aisha** embed and narrate from history |
| He wants live SMS now | “Next phase after consent — today is the working model, not a blast.” |
| You freeze | Say only: “You only get interrupted when criteria clear.” |

---

## One block to leave on screen before he joins

```bash
# WHERE: Hermes container — press Enter only when Banda can see #outreach-handoffs
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli live --pace 3
```

---

## After two full sims, you’re done when:

- [ ] You don’t look at this doc during the run  
- [ ] Enter happens without hesitation  
- [ ] Eyes stay on Discord after Enter  
- [ ] Handoff line is automatic  
- [ ] You can shut up after the ask  

**Banda isn’t buying a terminal. He’s buying that handoff moment.**  
Practice until that moment is boring for you.
