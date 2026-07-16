# Compliance Notes — Outreach Engine

**Not legal advice.** Owner is responsible for jurisdiction-specific compliance before any LIVE campaign. This skill encodes operational guardrails for demo and production.

## Demo vs production

| Mode | What is allowed | What is not |
|------|-----------------|-------------|
| **Demo / dry-run** (default) | Log payloads, simulate replies, preview handoff alerts labeled `[DEMO]` | Real email/SMS/calls; claiming “we already complied” |
| **Production / LIVE** | Sends only after owner confirm, consent checks, clean copy | Silent live switch; guaranteed-profit claims; ignoring STOP |

Dry-run success ≠ legal readiness. Treat demo as product UX proof only.

## CAN-SPAM (email — US baseline)

Operational checklist before LIVE email:

- [ ] Accurate **From** / **Reply-To** (no spoofed identity)
- [ ] Subject lines that match body content (no deceptive subjects)
- [ ] Clear identification that message is commercial / promotional where required
- [ ] Physical postal address in production footers (business address)
- [ ] Working **unsubscribe** mechanism honored promptly
- [ ] Suppression list checked before every send

Engine behavior:

- Opt-out / unsubscribe events → immediate `opted_out` in store → all channels suppressed
- Exhausted sequences do not re-mail without new enrollment + consent review

## TCPA / consent (SMS & calls — US baseline)

Operational checklist before LIVE SMS or AI voice:

- [ ] **Prior express consent** documented for the number (and express written consent where autodialed marketing requires it)
- [ ] Calling/texting hours respect local quiet hours expectations
- [ ] First SMS identifies who is texting and why
- [ ] Clear **STOP** / opt-out path; honor immediately
- [ ] No autodialed/AI calls to numbers without appropriate consent class
- [ ] Reassigned number / DNC hygiene considered for production lists

Engine behavior:

- `STOP`, `UNSUBSCRIBE`, `CANCEL`, `END`, `QUIT` (and similar) → opt-out all channels
- AI call scripts must include identity + purpose + easy hang-up / callback path
- Never re-enroll an opted-out phone without fresh consent evidence

## Crypto / trading marketing (content rules)

**Forbidden in all templates and agent-generated copy:**

- Guaranteed profits, “risk-free,” “can’t lose,” “guaranteed returns”
- Promising specific ROI percentages as certainty
- Implying past performance guarantees future results
- Fake urgency that misrepresents capacity/scarcity if untrue
- Impersonating exchanges, regulators, or celebrities

**Required tone:**

- Educational / community value framing (Discord community, tools, education)
- Risk awareness where claims about markets appear
- Honest product description: what members get (signals, chat, education) without fantasy outcomes

If the model drafts hype language, rewrite before any send (including dry-run demos — demos train bad habits).

## Opt-out handling (all channels)

1. Detect opt-out signal (email unsubscribe link, SMS STOP, verbal “remove me,” form flag)
2. Set `opted_out=true` + reason + timestamp
3. Cancel remaining sequence steps
4. Confirm suppression on next `tick` / `send` (hard fail closed)
5. Do **not** notify owner as a “hot lead” for pure opt-outs

## Handoff vs harassment

| Action | Allowed |
|--------|---------|
| Multi-touch sequence with spacing and opt-out | Yes (with consent) |
| Continue after STOP | **No** |
| Notify owner on every open | **No** — handoff criteria only |
| Notify owner on interested reply / score ≥ 40 / demo ask | Yes |
| Endless daily pings with no value | **No** — mark exhausted |

## Data & secrets

- Do not commit `.env`, lead dumps with PII to public repos, or full phone/email lists into skill docs
- Prefer minimal PII in handoff alerts (name + channel + why + next action)
- Access to Twilio/Gmail/Telegram tokens is owner-scoped; agent must not exfiltrate keys into chat logs casually

## Pre-LIVE gate (agent must enforce)

Before any `--live` send:

1. Owner explicitly confirmed LIVE for this action or campaign window
2. `DRY_RUN` is not forcing dry (or owner overrode with full awareness)
3. Lead not `opted_out`
4. Copy pass: no guaranteed-return claims
5. Channel-appropriate consent assumed/documented by owner
6. Rate/volume is a targeted sequence, not a raw blast list dump

If any item is unclear → stay in dry-run and ask the owner.

## Jurisdiction note

US CAN-SPAM / TCPA are baselines used in this skill because the demo stack (Twilio, Gmail) is US-centric. EU (GDPR/ePrivacy), UK PECR, Canada CASL, and others may impose stricter consent. Owner must validate before production outside the demo.
