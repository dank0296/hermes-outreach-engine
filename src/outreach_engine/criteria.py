"""Handoff criteria configuration and evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .models import HandoffResult, Lead, SignalType, Stage


INTEREST_KEYWORDS = [
    r"\binterested\b",
    r"\bdemo\b",
    r"\bpricing\b",
    r"\bprice\b",
    r"\bcost\b",
    r"\bjoin\b",
    r"\bdiscord\b",
    r"\bsign me up\b",
    r"\blet'?s talk\b",
    r"\bschedule\b",
    r"\bbook\b",
    r"\bcall me\b",
    r"\btell me more\b",
    r"\bhow (do|does|much|to)\b",
    r"\bprop firm\b",
    r"\bedge\b",
    r"\bcommunity\b",
    r"\byes\b",
    r"\bsounds good\b",
    r"\bcount me in\b",
]

NEGATIVE_KEYWORDS = [
    r"\bstop\b",
    r"\bunsubscribe\b",
    r"\bopt[\s-]?out\b",
    r"\bremove me\b",
    r"\bdo not contact\b",
    r"\bdon'?t contact\b",
    r"\bleave me alone\b",
    r"\bscam\b",
    r"\bfraud\b",
    r"\bgo away\b",
    r"\bhate\b",
]


@dataclass
class HandoffCriteria:
    min_score: int = 40
    stages: list[str] = field(default_factory=lambda: [Stage.HOT.value, Stage.QUALIFIED.value])
    signals_any: list[str] = field(
        default_factory=lambda: [
            SignalType.BOOKED_CALL.value,
            SignalType.ASKED_PRICING.value,
            SignalType.EXPLICIT_DEMO_REQUEST.value,
            SignalType.CALL_INTEREST.value,
            SignalType.INTEREST_KEYWORDS.value,
        ]
    )
    interest_keywords: list[str] = field(default_factory=lambda: list(INTEREST_KEYWORDS))
    block_on_opt_out: bool = True
    block_on_hostile: bool = False  # hostile still can handoff? default no block but no auto
    block_statuses: list[str] = field(default_factory=lambda: ["opted_out", "exhausted", "handed_off"])

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "HandoffCriteria":
        h = (config.get("handoff") or config.get("handoff_criteria") or {})
        return cls(
            min_score=int(h.get("min_score", 40)),
            stages=list(h.get("stages", [Stage.HOT.value, Stage.QUALIFIED.value])),
            signals_any=list(
                h.get(
                    "signals_any",
                    [
                        SignalType.BOOKED_CALL.value,
                        SignalType.ASKED_PRICING.value,
                        SignalType.EXPLICIT_DEMO_REQUEST.value,
                        SignalType.CALL_INTEREST.value,
                        SignalType.INTEREST_KEYWORDS.value,
                    ],
                )
            ),
            interest_keywords=list(h.get("interest_keywords", INTEREST_KEYWORDS)),
            block_on_opt_out=bool(h.get("block_on_opt_out", True)),
            block_on_hostile=bool(h.get("block_on_hostile", False)),
        )


def text_has_interest(text: str, patterns: Optional[list[str]] = None) -> bool:
    patterns = patterns or INTEREST_KEYWORDS
    lower = text.lower()
    return any(re.search(p, lower, re.I) for p in patterns)


def text_is_negative(text: str, patterns: Optional[list[str]] = None) -> bool:
    patterns = patterns or NEGATIVE_KEYWORDS
    lower = text.lower()
    return any(re.search(p, lower, re.I) for p in patterns)


def classify_reply(text: str, criteria: Optional[HandoffCriteria] = None) -> list[str]:
    """Return signal types inferred from free-text reply."""
    criteria = criteria or HandoffCriteria()
    signals: list[str] = []
    lower = text.lower()
    if text_is_negative(text):
        if re.search(r"\b(scam|fraud|hate|go away)\b", lower):
            signals.append(SignalType.HOSTILE.value)
        signals.append(SignalType.OPT_OUT.value)
        return signals
    if re.search(r"\b(price|pricing|cost|how much|fee|subscription)\b", lower):
        signals.append(SignalType.ASKED_PRICING.value)
    if re.search(r"\b(demo|show me|walkthrough|trial)\b", lower):
        signals.append(SignalType.EXPLICIT_DEMO_REQUEST.value)
    if re.search(r"\b(book|schedule|calendar|call me|let'?s talk|meeting)\b", lower):
        signals.append(SignalType.BOOKED_CALL.value)
    if text_has_interest(text, criteria.interest_keywords):
        signals.append(SignalType.INTEREST_KEYWORDS.value)
        signals.append(SignalType.EMAIL_REPLIED.value)
    else:
        # generic reply still counts as engagement
        signals.append(SignalType.EMAIL_REPLIED.value)
    return signals


def evaluate(lead: Lead, criteria: Optional[HandoffCriteria] = None) -> HandoffResult:
    """Evaluate whether a lead meets handoff criteria."""
    criteria = criteria or HandoffCriteria()
    reasons: list[str] = []

    if lead.status in criteria.block_statuses:
        return HandoffResult(should_handoff=False, reasons=[f"blocked_status:{lead.status}"], score=lead.score, stage=lead.stage)

    if criteria.block_on_opt_out and (
        lead.status == "opted_out" or SignalType.OPT_OUT.value in lead.signals
    ):
        return HandoffResult(should_handoff=False, reasons=["opt_out"], score=lead.score, stage=lead.stage)

    if criteria.block_on_hostile and SignalType.HOSTILE.value in lead.signals:
        return HandoffResult(should_handoff=False, reasons=["hostile"], score=lead.score, stage=lead.stage)

    if lead.score >= criteria.min_score:
        reasons.append(f"score>={criteria.min_score} (score={lead.score})")

    if lead.stage in criteria.stages:
        reasons.append(f"stage={lead.stage}")

    for sig in criteria.signals_any:
        if sig in lead.signals:
            reasons.append(f"signal:{sig}")

    # de-dupe while preserving order
    seen: set[str] = set()
    uniq: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            uniq.append(r)

    return HandoffResult(
        should_handoff=bool(uniq),
        reasons=uniq,
        score=lead.score,
        stage=lead.stage,
    )
