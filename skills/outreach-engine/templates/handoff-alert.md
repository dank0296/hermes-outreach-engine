# Handoff Alert Template

Use for Telegram, webhook, or CLI preview. In dry-run, prefix subject/title with `[DEMO]`.

---

## Short (Telegram / SMS-to-owner)

```
{{demo_tag}}HANDOFF · {{lead_name}}
Score {{score}} · stage {{stage}}
Why: {{handoff_reason}}
Channel: {{last_channel}} · {{lead_email_or_phone}}
Last msg: "{{last_inbound_snippet}}"
Next: {{suggested_action}}
Lead id: {{lead_id}}
```

### Example

```
[DEMO] HANDOFF · Alex R.
Score 47 · stage hot
Why: interested reply + pricing ask
Channel: email · alex@example.com
Last msg: "Interested — what's pricing for the Discord? Can we hop on a call?"
Next: Reply within 1h; send Discord tiers + calendar link
Lead id: lead_0xA1
```

---

## Full (webhook JSON-ish / email to owner)

```markdown
## {{demo_tag}}Lead handoff — take over

| Field | Value |
|-------|-------|
| Lead | {{lead_name}} ({{lead_id}}) |
| Score / stage | {{score}} / {{stage}} |
| Source | {{source}} |
| Email | {{lead_email}} |
| Phone | {{lead_phone}} |
| Sequence | {{sequence_id}} @ step {{step_index}} |
| Handoff reason | {{handoff_reason}} |
| Criteria matched | {{criteria_matched}} |

### Why now
{{handoff_reason_detail}}

### Recent touches
{{touch_log_summary}}

### Last inbound
> {{last_inbound_full}}

### Suggested owner actions
1. {{suggested_action}}
2. Confirm budget / fit for Discord community
3. Send invite or book call — **you** close; engine pauses sequence on handoff

### Engine state
- Sequence: **paused on handoff**
- Opted out: {{opted_out}}
- Mode: {{dry_run_or_live}}
```

---

## Reason codes (map scorer → `handoff_reason`)

| Code | Human line |
|------|------------|
| `score_threshold` | Score crossed {{threshold}} (default 40) |
| `stage_hot` | Stage moved to hot |
| `stage_qualified` | Stage moved to qualified |
| `intent_interested` | Positive / interested reply detected |
| `intent_pricing` | Asked about pricing |
| `intent_demo` | Requested demo |
| `intent_book_call` | Asked to book a call |

Multiple codes can appear in `criteria_matched` (comma-separated).

---

## Rules

1. **One alert per handoff transition** — do not spam the owner on every subsequent open
2. Never send handoff for pure opt-out or exhausted-cold
3. Keep PII minimal in group chats; prefer DM/home channel
4. Always include `lead_id` so the owner can ask Hermes: “open lead X”
5. `suggested_action` should be concrete (reply, call, send tiers) — not “follow up sometime”
