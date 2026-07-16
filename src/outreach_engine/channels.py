"""Outbound channels — dry_run default True; log only, never live send."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

from .models import Activity, ActivityType, ChannelType

logger = logging.getLogger("outreach_engine.channels")


@dataclass
class SendResult:
    ok: bool
    channel: str
    dry_run: bool
    message: str
    meta: dict[str, Any] = field(default_factory=dict)


class Channel(Protocol):
    name: str
    dry_run: bool
    enabled: bool

    def send(
        self,
        *,
        to: str,
        subject: str = "",
        body: str = "",
        lead_id: str = "",
        step_id: str = "",
        meta: Optional[dict[str, Any]] = None,
    ) -> SendResult: ...


class BaseChannel:
    name: str = "base"
    channel_type: str = "base"

    def __init__(self, dry_run: bool = True, enabled: bool = True):
        self.dry_run = dry_run
        self.enabled = enabled

    def send(
        self,
        *,
        to: str,
        subject: str = "",
        body: str = "",
        lead_id: str = "",
        step_id: str = "",
        meta: Optional[dict[str, Any]] = None,
    ) -> SendResult:
        if not self.enabled:
            msg = f"[{self.name}] SKIP disabled → {to}"
            logger.info(msg)
            return SendResult(ok=False, channel=self.channel_type, dry_run=self.dry_run, message=msg, meta=meta or {})

        # ALWAYS dry-run safe: never place real network calls in this package.
        # Even if dry_run=False, we only log — live providers must be wired externally.
        mode = "DRY-RUN" if self.dry_run else "LOG-ONLY (no live provider configured)"
        preview = (body or "")[:160].replace("\n", " ")
        msg = f"[{self.name}] {mode} → {to} | subject={subject!r} | body={preview!r}..."
        logger.info(msg)
        print(msg)
        return SendResult(
            ok=True,
            channel=self.channel_type,
            dry_run=self.dry_run,
            message=msg,
            meta={
                **(meta or {}),
                "to": to,
                "subject": subject,
                "lead_id": lead_id,
                "step_id": step_id,
            },
        )

    def to_activity(
        self,
        result: SendResult,
        *,
        lead_id: str,
        step_id: str = "",
        subject: str = "",
        body: str = "",
    ) -> Activity:
        return Activity.create(
            lead_id=lead_id,
            type=ActivityType.OUTBOUND.value,
            channel=self.channel_type,
            step_id=step_id or None,
            subject=subject,
            body=body,
            dry_run=result.dry_run,
            meta={"send_ok": result.ok, "send_message": result.message, **result.meta},
        )


class EmailChannel(BaseChannel):
    name = "EmailChannel"
    channel_type = ChannelType.EMAIL.value


class SmsChannel(BaseChannel):
    name = "SmsChannel"
    channel_type = ChannelType.SMS.value


class CallChannel(BaseChannel):
    name = "CallChannel"
    channel_type = ChannelType.CALL.value


def build_channels(config: Optional[dict[str, Any]] = None, dry_run: Optional[bool] = None) -> dict[str, BaseChannel]:
    config = config or {}
    global_dry = config.get("dry_run", True) if dry_run is None else dry_run
    ch = config.get("channels") or {}
    email_cfg = ch.get("email") or {}
    sms_cfg = ch.get("sms") or {}
    call_cfg = ch.get("call") or {}
    return {
        "email": EmailChannel(
            dry_run=bool(email_cfg.get("dry_run", global_dry)),
            enabled=bool(email_cfg.get("enabled", True)),
        ),
        "sms": SmsChannel(
            dry_run=bool(sms_cfg.get("dry_run", global_dry)),
            enabled=bool(sms_cfg.get("enabled", True)),
        ),
        "call": CallChannel(
            dry_run=bool(call_cfg.get("dry_run", global_dry)),
            enabled=bool(call_cfg.get("enabled", True)),
        ),
    }
