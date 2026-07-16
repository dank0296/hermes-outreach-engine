# Discord handoff setup

## Recommendation (Kero / Dank)

| Decision | Answer |
|----------|--------|
| **Meeting demo (now)** | **Private channel on existing Dank AI Discord** — best |
| **Brand-new Kerogroup server?** | **Not required for Jul 26.** Optional later as a multi-product *ops* hub |
| **Friend’s trading Discord** | **Never** for handoffs — that’s customer-facing, not your control plane |

### Why private channel on Dank AI is enough

- Bot / invite already exist (`guild` you already use for billing/claim)
- Friend can be invited as a **guest** for the meeting without building a whole new community
- Handoffs stay **owner-only** (role-lock `#sales-handoffs` or `#outreach-handoffs`)
- Zero brand confusion with his trading community

### When a Kerogroup Discord *does* make sense (later)

Create **Kero Group Ops** (or similar) **only if** you want a long-term internal HQ for:

- Multiple products (Hermes, Kasm, outreach, billing alerts)
- Staff / contractors / agents — not end customers
- Channels like `#outreach-handoffs` · `#billing` · `#incidents` · `#demos`

That’s an **ops control plane**, not a second public community.  
Don’t block the meeting on it. Ship the private channel first; migrate webhooks later if you grow.

```
WRONG:  spam handoffs into public trading Discord
RIGHT:  private #outreach-handoffs on Dank/Kero ops
LATER:  dedicated Kerogroup Ops server if product count grows
```

---

## Setup on Dank AI Discord (~2 minutes)

1. Create private channel: `#outreach-handoffs` (or `#sales-handoffs`)  
2. Permissions: only you + friend (+ bot) can see it  
3. Channel settings → **Integrations** → **Webhooks** → **New Webhook**  
   - Name: `Hermes Outreach`  
   - Copy URL  
4. On VPS (never commit the URL):

```bash
# /opt/data/.env
DISCORD_HANDOFF_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

5. Optional live ping during dry-run outreach:

```yaml
# config/default.yaml or config/local.yaml
notify:
  primary: discord
  dry_run: false
  discord:
    enabled: true
    dry_run: false
channels:
  email: { dry_run: true }
  sms: { dry_run: true }
  call: { dry_run: true }
```

6. Test:

```bash
cd /opt/data/repos/hermes-outreach-engine
PYTHONPATH=src python -m outreach_engine.cli notify-diagnose
PYTHONPATH=src python -m outreach_engine.cli notify-test          # dry-run
PYTHONPATH=src python -m outreach_engine.cli notify-test --live   # real post
```

### Alternate: bot + channel ID

If you prefer the existing Discord bot over a webhook:

```bash
export DISCORD_BOT_TOKEN=...          # already on VPS
export DISCORD_HANDOFF_CHANNEL_ID=... # right-click channel → Copy ID
```

Bot needs **View Channel**, **Send Messages**, **Embed Links** on that channel.

---

## What posts on handoff

Rich embed: name · score · stage · email/phone · reasons · signals · lead id.  
Engine **pauses** the lead so you don’t double-touch.

Telegram stays **optional / off by default** for this client.
