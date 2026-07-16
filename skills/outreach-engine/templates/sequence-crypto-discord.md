# Sequence: Crypto Discord Community

**id:** `crypto-discord`  
**Product:** Crypto trading Discord community (education, chat, tools — not financial advice)  
**Default mode:** dry-run  
**Goal:** Warm cold contacts until handoff criteria or exhaustion  
**Compliance:** No guaranteed profits; SMS/voice require consent in LIVE; honor STOP

Variables: `{{first_name}}`, `{{sender_name}}`, `{{community_name}}`, `{{value_hook}}`, `{{calendar_or_reply}}`, `{{opt_out_sms}}`

---

## Cadence overview

| Step | Day | Channel | Purpose |
|------|-----|---------|---------|
| 1 | 0 | email | Value intro |
| 2 | 1 | sms | Short bump + opt-out |
| 3 | 3 | email | Social proof / what members get |
| 4 | 5 | voice | Brief AI call / voicemail path |
| 5 | 7 | email | Soft close + clear CTA |
| 6 | 10 | sms | Final check-in → exhaust if silence |

If handoff fires at any step → **pause sequence** and notify owner only.

---

## Step 1 — Day 0 — Email

**Subject:** `{{first_name}}, a calmer way to follow markets with {{community_name}}`

```
Hi {{first_name}},

I'm {{sender_name}}. We run {{community_name}} — a Discord for traders who want structured discussion, education, and tools without the hype feed.

{{value_hook}}

No guaranteed returns — markets are risky and nothing here is financial advice. If a focused community sounds useful, reply and I'll share how membership works.

— {{sender_name}}
```

---

## Step 2 — Day 1 — SMS

```
Hey {{first_name}} — {{sender_name}} from {{community_name}}. Sent you a quick note on a trader Discord focused on process over hype. Want the details? Reply YES or {{opt_out_sms}}
```

`{{opt_out_sms}}` example: `Reply STOP to opt out.`

---

## Step 3 — Day 3 — Email

**Subject:** `What people actually use {{community_name}} for`

```
Hi {{first_name}},

Quick follow-up with less pitch, more substance.

Members usually join for:
• Live discussion when markets move
• Educational breakdowns (risk, setups, process)
• A room that filters noise

Again: not financial advice, no promised profits. If you want tiers/pricing or a walkthrough, just reply — or tell me to close the loop.

— {{sender_name}}
```

---

## Step 4 — Day 5 — AI voice (script)

**Goal:** 20–40s, respectful, leave a path back. Not a hard sell.

```
Hi {{first_name}}, this is an automated call from {{sender_name}} with {{community_name}}.
We sent a couple notes about our trader Discord — education and community, not guaranteed results.
If you're curious, you can reply to our text or email and a human will follow up.
If you'd rather not hear from us, say "remove me" or reply STOP to our SMS.
Thanks for your time.
```

**Adapter notes:** Bland/Vapi via `telephony` skill; dry-run logs script only; LIVE needs consent class appropriate for AI/autodial.

---

## Step 5 — Day 7 — Email

**Subject:** `Should I close the loop, {{first_name}}?`

```
Hi {{first_name}},

I'll keep this short. Happy to share {{community_name}} membership options or hop on a quick call if useful: {{calendar_or_reply}}.

If now's not the right time, no worries — I won't keep chasing you.

— {{sender_name}}
```

---

## Step 6 — Day 10 — SMS (final)

```
{{first_name}} — last check-in from {{sender_name}} / {{community_name}}. Want the Discord details? Reply YES. Otherwise I'll close your file. {{opt_out_sms}}
```

On silence after this step → stage `exhausted`, **no handoff notify**.

---

## Intent → handoff shortcuts

Any inbound matching these should raise score / stage and may handoff early:

| Inbound signal | Effect |
|----------------|--------|
| “pricing”, “how much”, “tiers” | +score, likely handoff |
| “call”, “zoom”, “book” | handoff |
| “interested”, “tell me more”, “YES” | +score; handoff if strong |
| “STOP”, “remove me”, “unsubscribe” | opt-out, suppress all |
| Hostile / report spam | opt-out + log |

---

## Copy constraints (every step)

- No “guaranteed profit”, “risk-free”, “100% win rate”, etc.
- Identify sender and community
- Easy exit (email ignore/unsub, SMS STOP, voice remove-me)
- Discord invite links only after interest or handoff (don’t dump invite in first cold blast unless owner policy says otherwise)

---

## Enrollment example

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli enroll \
  --lead-id <ID> \
  --sequence crypto-discord
```
