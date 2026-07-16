# YouTube × Kasm Flywheel — Hermes Outreach

**Thesis:** One hand washes the other.

| Hand | Role |
|------|------|
| **YouTube** | Show the *outcome* (agent works cold; human only on handoff) → inbound demand |
| **Kasm Hermes** | Sell the *seat* (browser workspace where that agent lives and runs) → revenue + retention |
| **Outreach product** | Hero use-case in the video (Discord owners, agencies, trading communities) |

Do **not** lead with “buy Kasm.” Lead with “watch an agent qualify leads 24/7.”  
Close with “run this yourself in a Hermes workspace.”

---

## Why this works

1. **Visual proof** > pitch decks (Discord ops feed + think/tool/result is screen-share gold)
2. **ICP is huge** — Discord server owners, marketing firms, community operators (not only Banda)
3. **Kasm is the fulfillment** — after “I want this,” the answer is operator seat / workspace, not a zip of source
4. **Public demo repo** = SEO + trust; **production** = hosted product

---

## Video ladder (ship in order)

| # | Format | Length | Goal | CTA |
|---|--------|--------|------|-----|
| **V1** | YouTube **Short / vertical** | 45–60s | Hook + handoff moment | “Full demo in description” |
| **V2** | YouTube **long** | 8–12 min | Full working model + product framing | “Book pilot / start Hermes seat” |
| **V3** | YouTube **Short** | 30–45s | “Discord owners only” cut | Same |
| **V4** | YouTube **Short** | 30–45s | “Agencies running client Discords” | Same |

V1 can ship this week from existing `#outreach-handoffs` recording + voiceover.

---

## V1 — Short (script)

**Title options**
1. AI that only pings you when a lead is worth it
2. Stop living in cold DMs — watch this agent
3. 24/7 outreach. Human only on handoff.

**On-screen (screen record Discord `#outreach-handoffs`)**
0–3s: Text hook — “Your agent works cold. You don’t.”
3–15s: Fast cuts — enroll → email dry-run → open (no ping)
15–35s: Inbound reply → score → **🚨 HANDOFF** (hold 3s)
35–50s: “4 others never woke you”
50–60s: CTA — “Full demo + Hermes workspace link in description”

**Voiceover (one take)**
> Most outreach tools spam for you. This one works the list 24/7 and only interrupts you when someone is actually worth your time. Watch — opens don’t ping you. Pricing and demo intent does. That’s the handoff. Everything else stays automated. Link below to see the full run and how to run it in a Hermes agent workspace.

**Description template**
```
Hermes Outreach — criteria-first multi-channel outreach (dry-run demo).

What you saw:
• Real sequence + scoring + handoff
• Discord ops feed (owner only when worth it)
• Built for Discord communities, agencies, operators

Full walkthrough: [V2 URL]
Run it in a Hermes workspace (Kasm): [booking / dank.kerogroup / waitlist]
Repo (demo): https://github.com/dank0296/hermes-outreach-engine

Not financial advice. Outbound in this video is simulated.
```

---

## V2 — Long form (8–12 min outline)

| Min | Section | Record |
|-----|---------|--------|
| 0:00 | Hook + thesis | Face or VO + freeze frame handoff |
| 0:45 | Who it’s for | Discord owners, marketing firms, community ops |
| 1:30 | Problem | Owner time tax / AE calendar / brand-safe growth |
| 2:30 | **Part A** explain | `agent-demo` + `./next` (or edit tighter) |
| 6:00 | **Part B** visual agent | `./visual-demo` full think/tool/result |
| 9:00 | What we sell | Pilot / Operator seat — not free white-label |
| 10:00 | **How you run it** | Kasm Hermes workspace = browser desktop + agent |
| 11:00 | CTA | Pilot form / Discord / site |
| 11:30 | End screen | Sub + V1 short + waitlist |

**Bridge line (Kasm, natural)**
> The agent is the product. The Hermes workspace is how operators actually live with it day to day — browser login, agent ready, handoffs in Discord. One hand washes the other.

---

## Funnel after video

```
YouTube view
  → description link / comment CTA
    → waitlist or booking
      → Discord demo call (you already have the kit)
        → Pilot fee / monthly Operator seat
          → Kasm Hermes workspace provisioned
```

**Do not** send raw VPS access as the default offer.

---

## Production checklist (V1 this week)

- [ ] Clear `#outreach-handoffs` (or use clean segment)
- [ ] Run `./visual-demo 5` while **OBS / Discord Go Live record**
- [ ] Optional: second take of Part A `./next` for B-roll
- [ ] Voiceover in one clean take
- [ ] Captions (auto + fix hook lines)
- [ ] Thumbnail: red **HANDOFF** card + text “Only pings you when it’s real”
- [ ] Description + pinned comment CTA
- [ ] End screen → full video (once V2 exists) or site

**Commands (Hermes container)**
```bash
cd /opt/data/repos/hermes-outreach-engine
# record Discord channel while this runs:
./visual-demo 5
```

---

## Positioning rules (on camera)

| Say | Don’t say |
|-----|-----------|
| Criteria-first / handoff-only | Guaranteed members / ROI |
| Dry-run demo, live when you approve | “We’ll blast your list today” |
| Pilot / operator seat | “Here’s the full source, resell it” |
| Workspace to run your agent | “SSH into our VPS” |

---

## Metrics that matter

| Metric | Why |
|--------|-----|
| Short 3s hold + CTR | Hook quality |
| V2 average view duration | Story works |
| CTA clicks | Funnel |
| Demo calls booked | Sales |
| Seats started | Kasm flywheel closes |

---

## One-liner for investors / partners

> We demo AI outreach that only escalates hot leads on YouTube; we fulfill with Hermes agent workspaces on Kasm. Content creates demand; seats capture it.

---

*Related: docs/BANDA-PRE-MEETING-BRIEF.md · docs/BANDA-MEETING-CHEATSHEET.md · visual-demo CLI*
