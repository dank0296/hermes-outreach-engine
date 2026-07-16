"""Core data models for the outreach engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utcnow().isoformat()


class Stage(str, Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    QUALIFIED = "qualified"
    EXHAUSTED = "exhausted"
    OPTED_OUT = "opted_out"
    HANDOFF = "handoff"


class ChannelType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"


class ActivityType(str, Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    SIGNAL = "signal"
    SYSTEM = "system"
    HANDOFF = "handoff"


class SignalType(str, Enum):
    EMAIL_OPENED = "email_opened"
    EMAIL_REPLIED = "email_replied"
    SMS_REPLIED = "sms_replied"
    CALL_INTEREST = "call_interest"
    BOOKED_CALL = "booked_call"
    ASKED_PRICING = "asked_pricing"
    VISITED_DISCORD_INVITE = "visited_discord_invite"
    OPT_OUT = "opt_out"
    HOSTILE = "hostile"
    EXPLICIT_DEMO_REQUEST = "explicit_demo_request"
    INTEREST_KEYWORDS = "interest_keywords"


@dataclass
class Activity:
    id: str
    lead_id: str
    type: str
    channel: Optional[str] = None
    signal: Optional[str] = None
    step_id: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    dry_run: bool = True
    meta: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=iso_now)

    @staticmethod
    def create(
        lead_id: str,
        type: str,
        *,
        channel: Optional[str] = None,
        signal: Optional[str] = None,
        step_id: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        dry_run: bool = True,
        meta: Optional[dict[str, Any]] = None,
    ) -> "Activity":
        return Activity(
            id=f"act_{uuid.uuid4().hex[:12]}",
            lead_id=lead_id,
            type=type,
            channel=channel,
            signal=signal,
            step_id=step_id,
            subject=subject,
            body=body,
            dry_run=dry_run,
            meta=meta or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Activity":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Lead:
    id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    company: str = ""
    title: str = ""
    source: str = "import"
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    # scoring / lifecycle
    score: int = 0
    stage: str = Stage.COLD.value
    status: str = "active"  # active | exhausted | opted_out | handed_off
    signals: list[str] = field(default_factory=list)
    # sequence state
    sequence_id: str = "crypto_discord_default"
    sequence_step: int = 0  # next step index to send
    touches: int = 0
    last_touch_at: Optional[str] = None
    next_touch_at: Optional[str] = None
    enrolled_at: Optional[str] = None
    # handoff
    handoff_ready: bool = False
    handoff_at: Optional[str] = None
    handoff_reasons: list[str] = field(default_factory=list)
    # timestamps
    created_at: str = field(default_factory=iso_now)
    updated_at: str = field(default_factory=iso_now)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @staticmethod
    def create(
        email: str,
        *,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        company: str = "",
        title: str = "",
        source: str = "import",
        tags: Optional[list[str]] = None,
        notes: str = "",
        lead_id: Optional[str] = None,
        sequence_id: str = "crypto_discord_default",
        meta: Optional[dict[str, Any]] = None,
    ) -> "Lead":
        now = iso_now()
        return Lead(
            id=lead_id or f"lead_{uuid.uuid4().hex[:10]}",
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company,
            title=title,
            source=source,
            tags=tags or [],
            notes=notes,
            sequence_id=sequence_id,
            enrolled_at=now,
            next_touch_at=now,
            created_at=now,
            updated_at=now,
            meta=meta or {},
        )

    def touch(self) -> None:
        self.updated_at = iso_now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Lead":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        cleaned = {k: v for k, v in data.items() if k in known}
        # defaults for partial imports
        if "id" not in cleaned:
            cleaned["id"] = f"lead_{uuid.uuid4().hex[:10]}"
        if "email" not in cleaned:
            raise ValueError("Lead requires email")
        return cls(**cleaned)


@dataclass
class HandoffResult:
    should_handoff: bool
    reasons: list[str] = field(default_factory=list)
    score: int = 0
    stage: str = Stage.COLD.value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SequenceStep:
    id: str
    day_offset: int
    channel: str  # email | sms | call
    name: str
    subject: str = ""
    template: str = ""
    script: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Sequence:
    id: str
    name: str
    steps: list[SequenceStep] = field(default_factory=list)
    max_touches: int = 5
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "max_touches": self.max_touches,
            "steps": [s.to_dict() for s in self.steps],
        }
