"""Handoff notifier — handoffs.jsonl + Telegram-ready message; optional webhook."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

from .models import Lead, iso_now
from .store import JsonStore


class HandoffNotifier:
    def __init__(
        self,
        store: JsonStore,
        *,
        webhook_url: Optional[str] = None,
        dry_run: bool = True,
    ):
        self.store = store
        self.webhook_url = webhook_url or os.environ.get("OUTREACH_HANDOFF_WEBHOOK") or os.environ.get(
            "HANDOFF_WEBHOOK_URL"
        )
        self.dry_run = dry_run

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

    def notify(self, lead: Lead, reasons: list[str]) -> dict[str, Any]:
        record = {
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
            "telegram_message": self.format_telegram(lead, reasons),
        }
        self.store.append_handoff(record)

        plain = self.format_plain(lead, reasons)
        telegram = record["telegram_message"]
        print("\n" + "=" * 60)
        print("HANDOFF NOTIFICATION")
        print("=" * 60)
        print(plain)
        print("-" * 60)
        print(telegram)
        print("=" * 60 + "\n")

        webhook_status = "skipped"
        if self.webhook_url and not self.dry_run:
            webhook_status = self._post_webhook(record)
        elif self.webhook_url and self.dry_run:
            webhook_status = f"dry_run_skip webhook={self.webhook_url[:48]}..."
            print(f"[HandoffNotifier] DRY-RUN webhook not called: {self.webhook_url[:64]}")

        record["webhook_status"] = webhook_status
        return record

    def _post_webhook(self, record: dict[str, Any]) -> str:
        assert self.webhook_url
        data = json.dumps({"text": record.get("telegram_message"), "handoff": record}).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310 — user-configured URL only
                return f"ok status={resp.status}"
        except urllib.error.URLError as e:
            return f"error: {e}"
