# ICP — Crypto Trading Discord

Ideal customer / lead profile for Hermes Outreach Engine demos and scoring defaults.

**Product stance:** qualify hard. Lurkers and noise stay automated. **You only talk to leads that meet criteria.**

This is not financial advice and not a promise that ICP members convert or profit.

---

## Who the operator is

| Attribute | Profile |
|-----------|---------|
| Role | Runs or co-runs a crypto trading Discord (signals, education, community, or hybrid) |
| Pain | Inbox/DM overload; inconsistent follow-up; hard to spot serious members |
| Goal | More conversations with people who actually engage — not more spray-and-pray |
| Constraint | Reputation risk; Discord ToS; community trust; no fake hype |

---

## Who a *worthwhile lead* is (member-side ICP)

### Positive signals (fit ↑)

- **Active trader self-description** — talks about process, risk, journals, setups (not “guaranteed moon”)  
- **Participates in education / discussion channels** — questions show thinking, not only “entry?”  
- **Consistent presence** — not a same-day join → spam DM → vanish pattern  
- **Skin-in-the-game language** — size, timeframe, markets they actually trade (without needing PII dumps)  
- **Clear intent when asked** — wants human chat, paid tier info, onboarding, or specific offer details  
- **Respectful of rules** — no pump spam, no harassment  

### Negative signals (fit ↓ / suppress)

- Pure lurker with zero replies over long window  
- Giveaway / free signal hunters only  
- Pump-shill or competitor scout behavior  
- Opt-out / hostility / scam patterns  
- Brand-new account + high-pressure “admin?” spam  

### Intent signals (handoff fuel)

These move a lead from “nurture” to “maybe human”:

- Explicit interest in the offer / community tier  
- Asks about pricing, onboarding, or how to join seriously  
- Requests a call, voice, or operator DM  
- Shares enough trading context to make a conversation useful  
- Responds thoughtfully to qualifying questions in the sequence  

Engagement alone (emoji, one-word “ok”) is **not** enough for handoff under default gates.

---

## Scoring map (defaults)

See `config/default.yaml` → `scoring` + `icp`.

| Dimension | What we look for in this vertical |
|-----------|-----------------------------------|
| Intent | Offer/pricing/call language; serious follow-ups |
| Engagement | Reply count, depth, latency (not emoji-only) |
| Fit | positive_tags vs negative_tags; channel activity |
| Recency | Fresh replies beat stale threads |

Handoff still requires **min score + intent gate + not suppressed** — fit without intent stays automated.

---

## Messaging principles (for sequences)

Do:

- Sound like a sharp community operator, not a broker  
- Offer one clear next step  
- Ask qualifying questions  
- Respect “stop” immediately  

Don’t:

- Promise returns, “risk-free,” or guaranteed alpha  
- Pressure language or fake scarcity theater  
- Impersonate mods/admins in deceptive ways  
- Collect sensitive financial data in cold DMs  

---

## Example personas (demo only)

| Persona | Expected path |
|---------|----------------|
| **Alex — active futures trader** | Replies with process questions → scores high → handoff |
| **Sam — lurker** | No reply / one emoji → low score → no handoff |
| **Riley — giveaway hunter** | Free-only language → negative fit → suppressed or low score |
| **Jordan — serious but slow** | Delayed thoughtful reply → nurtures → may hand off after intent step |

No conversion rates attached — personas exist to show **gates**, not vanity metrics.

---

## Operator checklist before live

1. Written offer the sequence is allowed to mention  
2. Handoff destination (DM or private channel)  
3. Thresholds reviewed (min_score, intent list)  
4. Mod team aware of bot identity and rate limits  
5. dry_run signed off before any live send  

---

## Related

- [ARCHITECTURE.md](ARCHITECTURE.md)  
- [MEETING-BRIEF.md](MEETING-BRIEF.md)  
- [../config/default.yaml](../config/default.yaml)  
