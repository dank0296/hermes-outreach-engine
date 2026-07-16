"""Handoff notifier — Discord primary, Telegram optional, generic webhook.

Delivery targets (any combination from config/env):
  - Discord incoming webhook (best for meeting demo)
  - Discord bot → channel (DISCORD_BOT_TOKEN + channel_id)
  - Telegram-formatted text (print + optional webhook)
  - Generic HANDOFF_WEBHOOK_URL

Outreach channel dry_run is separate from notify dry_run so you can
post a real Discord handoff while email/SMS stay simulated.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

from .models import Lead, iso_now
from .store import JsonStore


def _env(*names: str) -> Optional[str]:
    for n in names:
        v = os.environ.get(n)
        if v and v.strip():
            return v.strip()
    return None


class HandoffNotifier:
    def __init__(
        self,
        store: JsonStore,
        *,
        config: Optional[dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        dry_run: bool = True,
    ):
        self.store = store
        self.config = config or {}
        notify = (self.config.get("notify") or {}) if isinstance(self.config, dict) else {}

        # Global notify dry_run can be independent of outreach dry_run
        if "dry_run" in notify:
            self.dry_run = bool(notify.get("dry_run"))
        else:
            self.dry_run = dry_run

        self.primary = (notify.get("primary") or "discord").lower()

        discord = notify.get("discord") or {}
        self.discord_enabled = bool(discord.get("enabled", True))
        self.discord_webhook = (
            discord.get("webhook_url")
            or webhook_url
            or _env(
                "DISCORD_HANDOFF_WEBHOOK_URL",
                "OUTREACH_DISCORD_WEBHOOK",
                "OUTREACH_HANDOFF_WEBHOOK",
                "HANDOFF_WEBHOOK_URL",
            )
        )
        self.discord_bot_token = discord.get("bot_token") or _env(
            "DISCORD_HANDOFF_BOT_TOKEN", "DISCORD_BOT_TOKEN"
        )
        self.discord_channel_id = str(
            discord.get("channel_id")
            or _env("DISCORD_HANDOFF_CHANNEL_ID", "OUTREACH_DISCORD_CHANNEL_ID")
            or ""
        ).strip()
        # Per-target dry_run overrides
        self.discord_dry_run = bool(discord.get("dry_run", self.dry_run))

        telegram = notify.get("telegram") or {}
        self.telegram_enabled = bool(telegram.get("enabled", False))
        self.telegram_bot_token = telegram.get("bot_token") or _env("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = str(
            telegram.get("chat_id") or _env("TELEGRAM_HANDOFF_CHAT_ID", "TELEGRAM_HOME_CHANNEL") or ""
        ).strip()
        self.telegram_dry_run = bool(telegram.get("dry_run", self.dry_run))

        generic = notify.get("webhook") or {}
        self.generic_webhook = (
            generic.get("url")
            or webhook_url
            or _env("OUTREACH_HANDOFF_WEBHOOK", "HANDOFF_WEBHOOK_URL")
        )
        # If generic webhook looks like Discord, treat as discord
        if self.generic_webhook and "discord.com/api/webhooks" in self.generic_webhook:
            if not self.discord_webhook:
                self.discord_webhook = self.generic_webhook
            self.generic_webhook = None if self.discord_webhook == self.generic_webhook else self.generic_webhook
        self.generic_dry_run = bool(generic.get("dry_run", self.dry_run))

    # ----- formatters -----

    def format_discord_content(self, lead: Lead, reasons: list[str]) -> str:
        reason_txt = ", ".join(reasons) if reasons else "criteria met"
        return (
            f"🚨 **OUTREACH HANDOFF** — take over this lead\n"
            f"**{lead.full_name}** · score **{lead.score}** · stage `{lead.stage}`\n"
            f"Email: `{lead.email}` · Phone: `{lead.phone or 'n/a'}`\n"
            f"Company: {lead.company or 'n/a'} · Title: {lead.title or 'n/a'}\n"
            f"**Why:** {reason_txt}\n"
            f"Signals: {', '.join(lead.signals) or 'none'} · Touches: {lead.touches}\n"
            f"ID: `{lead.id}`\n"
            f"_Engine paused this lead. Your move._"
        )

    def format_discord_embed(self, lead: Lead, reasons: list[str]) -> dict[str, Any]:
        reason_txt = ", ".join(reasons) if reasons else "criteria met"
        color = 0xE74C3C if lead.score >= 50 else 0xF39C12  # red / orange
        return {
            "title": f"Handoff · {lead.full_name}",
            "description": "Lead met criteria — owner take-over.",
            "color": color,
            "fields": [
                {"name": "Score / Stage", "value": f"**{lead.score}** · `{lead.stage}`", "inline": True},
                {"name": "Email", "value": lead.email or "n/a", "inline": True},
                {"name": "Phone", "value": lead.phone or "n/a", "inline": True},
                {"name": "Company", "value": lead.company or "n/a", "inline": True},
                {"name": "Title", "value": lead.title or "n/a", "inline": True},
                {"name": "Touches", "value": str(lead.touches), "inline": True},
                {"name": "Reasons", "value": reason_txt[:1024] or "criteria met", "inline": False},
                {
                    "name": "Signals",
                    "value": (", ".join(lead.signals) or "none")[:1024],
                    "inline": False,
                },
                {"name": "Lead ID", "value": f"`{lead.id}`", "inline": False},
            ],
            "footer": {"text": "Hermes Outreach Engine · not financial advice"},
        }

    def format_telegram(self, lead: Lead, reasons: list[str]) -> str:
        reason_txt = ", ".join(reasons) if reasons else "criteria met"
        lines = [
            "🚨 *OUTREACH HANDOFF*",
            f"*Lead:* {lead.full_name}",
            f"*Email:* `{lead.email}`",
            f"*Phone:* {lead.phone or 'n/a'}",
            f"*Company:* {lead.company or 'n/a'}",
            f"*Title:* {lead.title or 'n/a'}",
            f"*Score:* {lead.score} | *Stage:* {lead.stage}",
            f"*Reasons:* {reason_txt}",
            f"*Signals:* {', '.join(lead.signals) or 'none'}",
            f"*Touches:* {lead.touches}",
            f"*ID:* `{lead.id}`",
            "",
            "_Owner action: personal follow-up. Engine will pause this lead._",
        ]
        return "\n".join(lines)

    def format_plain(self, lead: Lead, reasons: list[str]) -> str:
        reason_txt = ", ".join(reasons) if reasons else "criteria met"
        return (
            f"[HANDOFF] {lead.full_name} <{lead.email}> "
            f"score={lead.score} stage={lead.stage} reasons={reason_txt} id={lead.id}"
        )

    # ----- main -----

    def notify(self, lead: Lead, reasons: list[str]) -> dict[str, Any]:
        record: dict[str, Any] = {
            "id": f"handoff_{lead.id}_{iso_now().replace(':', '').replace('-', '')[:15]}",
            "lead_id": lead.id,
            "email": lead.email,
            "name": lead.full_name,
            "phone": lead.phone,
            "company": lead.company,
            "score": lead.score,
            "stage": lead.stage,
            "reasons": reasons,
            "signals": list(lead.signals),
            "touches": lead.touches,
            "created_at": iso_now(),
            "status": "pending",
            "primary": self.primary,
            "telegram_message": self.format_telegram(lead, reasons),
            "discord_content": self.format_discord_content(lead, reasons),
            "discord_embed": self.format_discord_embed(lead, reasons),
            "deliveries": {},
        }
        self.store.append_handoff(record)

        plain = self.format_plain(lead, reasons)
        print("\n" + "=" * 60)
        print("HANDOFF NOTIFICATION")
        print("=" * 60)
        print(plain)
        print("-" * 60)
        print(record["discord_content"])
        print("=" * 60 + "\n")

        deliveries: dict[str, str] = {}

        if self.discord_enabled and (self.discord_webhook or (self.discord_bot_token and self.discord_channel_id)):
            deliveries["discord"] = self._deliver_discord(lead, reasons, record)
        elif self.discord_enabled:
            deliveries["discord"] = "skipped: set DISCORD_HANDOFF_WEBHOOK_URL or bot+channel_id"
            print(
                "[HandoffNotifier] Discord enabled but not configured. "
                "Set DISCORD_HANDOFF_WEBHOOK_URL (recommended) or "
                "DISCORD_BOT_TOKEN + DISCORD_HANDOFF_CHANNEL_ID."
            )

        if self.telegram_enabled and self.telegram_bot_token and self.telegram_chat_id:
            deliveries["telegram"] = self._deliver_telegram(record["telegram_message"])
        elif self.telegram_enabled:
            deliveries["telegram"] = "skipped: missing TELEGRAM_BOT_TOKEN or chat_id"

        if self.generic_webhook and not (
            self.discord_webhook and self.generic_webhook == self.discord_webhook
        ):
            deliveries["webhook"] = self._post_generic_webhook(record)

        record["deliveries"] = deliveries
        record["webhook_status"] = deliveries.get("discord") or deliveries.get("webhook") or "local_only"
        return record

    # ----- Discord -----

    def _deliver_discord(self, lead: Lead, reasons: list[str], record: dict[str, Any]) -> str:
        payload = {
            "content": f"🚨 **Handoff ready** — {lead.full_name} (score {lead.score})",
            "embeds": [record["discord_embed"]],
            "allowed_mentions": {"parse": []},
        }

        if self.discord_dry_run:
            print(
                f"[HandoffNotifier] DRY-RUN Discord payload ready "
                f"(webhook={'yes' if self.discord_webhook else 'no'}, "
                f"channel={self.discord_channel_id or 'n/a'})"
            )
            print(json.dumps(payload, indent=2)[:800])
            return "dry_run"

        # Prefer webhook (no bot perms needed on target server beyond webhook)
        if self.discord_webhook:
            return self._post_json(self.discord_webhook, payload, label="discord_webhook")

        if self.discord_bot_token and self.discord_channel_id:
            url = f"https://discord.com/api/v10/channels/{self.discord_channel_id}/messages"
            return self._post_json(
                url,
                payload,
                label="discord_bot",
                headers={
                    "Authorization": f"Bot {self.discord_bot_token}",
                    "Content-Type": "application/json",
                },
            )

        return "skipped: no discord transport"

    # ----- Telegram (optional) -----

    def _deliver_telegram(self, text: str) -> str:
        if self.telegram_dry_run:
            print("[HandoffNotifier] DRY-RUN Telegram not sent")
            return "dry_run"
        assert self.telegram_bot_token and self.telegram_chat_id
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
        return self._post_json(url, payload, label="telegram")

    # ----- generic -----

    def _post_generic_webhook(self, record: dict[str, Any]) -> str:
        assert self.generic_webhook
        if self.generic_dry_run:
            print(f"[HandoffNotifier] DRY-RUN generic webhook: {self.generic_webhook[:64]}")
            return "dry_run"
        data = {
            "text": record.get("discord_content") or record.get("telegram_message"),
            "handoff": {k: v for k, v in record.items() if k != "discord_embed"},
        }
        return self._post_json(self.generic_webhook, data, label="webhook")

    def _post_json(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        label: str,
        headers: Optional[dict[str, str]] = None,
    ) -> str:
        body = json.dumps(payload).encode("utf-8")
        hdrs = {"Content-Type": "application/json", "User-Agent": "hermes-outreach-engine/1.0"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:  # nosec B310
                raw = resp.read().decode("utf-8", errors="replace")[:200]
                print(f"[HandoffNotifier] {label} ok status={resp.status}")
                return f"ok status={resp.status} body={raw}"
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:300]
            print(f"[HandoffNotifier] {label} HTTP {e.code}: {err}")
            return f"error http={e.code}: {err}"
        except urllib.error.URLError as e:
            print(f"[HandoffNotifier] {label} error: {e}")
            return f"error: {e}"

    def diagnose(self) -> dict[str, Any]:
        return {
            "primary": self.primary,
            "dry_run_global": self.dry_run,
            "discord": {
                "enabled": self.discord_enabled,
                "dry_run": self.discord_dry_run,
                "webhook_configured": bool(self.discord_webhook),
                "bot_token_configured": bool(self.discord_bot_token),
                "channel_id": self.discord_channel_id or None,
                "ready": bool(
                    self.discord_webhook
                    or (self.discord_bot_token and self.discord_channel_id)
                ),
            },
            "telegram": {
                "enabled": self.telegram_enabled,
                "dry_run": self.telegram_dry_run,
                "ready": bool(self.telegram_bot_token and self.telegram_chat_id),
            },
            "generic_webhook": bool(self.generic_webhook),
        }
