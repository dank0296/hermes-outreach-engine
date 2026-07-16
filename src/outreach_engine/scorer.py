"""Lead scoring and stage machine."""

from __future__ import annotations

from typing import Any, Optional

from .models import Lead, SignalType, Stage


DEFAULT_WEIGHTS: dict[str, int] = {
    SignalType.EMAIL_OPENED.value: 1,
    SignalType.EMAIL_REPLIED.value: 15,
    SignalType.SMS_REPLIED.value: 12,
    SignalType.CALL_INTEREST.value: 20,
    SignalType.BOOKED_CALL.value: 25,
    SignalType.ASKED_PRICING.value: 18,
    SignalType.VISITED_DISCORD_INVITE.value: 10,
    SignalType.EXPLICIT_DEMO_REQUEST.value: 22,
    SignalType.INTEREST_KEYWORDS.value: 12,
    SignalType.HOSTILE.value: -50,
    SignalType.OPT_OUT.value: 0,  # terminal; handled separately
}

DEFAULT_STAGE_THRESHOLDS: dict[str, tuple[int, Optional[int]]] = {
    # stage: (min_inclusive, max_inclusive) — max None = unbounded
    Stage.COLD.value: (0, 9),
    Stage.WARM.value: (10, 24),
    Stage.HOT.value: (25, 49),
    Stage.QUALIFIED.value: (50, None),
}


class LeadScorer:
    def __init__(
        self,
        weights: Optional[dict[str, int]] = None,
        stage_thresholds: Optional[dict[str, tuple[int, Optional[int]]]] = None,
    ):
        self.weights = {**DEFAULT_WEIGHTS, **(weights or {})}
        self.stage_thresholds = stage_thresholds or DEFAULT_STAGE_THRESHOLDS

    def weight_for(self, signal: str) -> int:
        return int(self.weights.get(signal, 0))

    def compute_score(self, signals: list[str]) -> int:
        """Sum unique-ish signals; allow multiples for opens, single-count terminal."""
        if SignalType.OPT_OUT.value in signals:
            return min(0, sum(self.weight_for(s) for s in signals if s != SignalType.OPT_OUT.value))
        total = 0
        seen_once: set[str] = set()
        multi_ok = {SignalType.EMAIL_OPENED.value}
        for s in signals:
            if s in multi_ok:
                total += self.weight_for(s)
            elif s not in seen_once:
                total += self.weight_for(s)
                seen_once.add(s)
        return total

    def stage_for(self, score: int, *, status: str = "active", signals: Optional[list[str]] = None) -> str:
        signals = signals or []
        if status == "opted_out" or SignalType.OPT_OUT.value in signals:
            return Stage.OPTED_OUT.value
        if status == "handed_off":
            return Stage.HANDOFF.value
        if status == "exhausted":
            return Stage.EXHAUSTED.value
        # ordered from high to low
        if score >= 50:
            return Stage.QUALIFIED.value
        if score >= 25:
            return Stage.HOT.value
        if score >= 10:
            return Stage.WARM.value
        return Stage.COLD.value

    def apply_signal(self, lead: Lead, signal: str) -> Lead:
        if signal not in lead.signals or signal == SignalType.EMAIL_OPENED.value:
            lead.signals = list(lead.signals) + [signal]
        if signal == SignalType.OPT_OUT.value:
            lead.status = "opted_out"
            lead.stage = Stage.OPTED_OUT.value
            lead.score = self.compute_score(lead.signals)
            lead.touch()
            return lead
        if signal == SignalType.HOSTILE.value:
            # still score, may not handoff
            pass
        lead.score = self.compute_score(lead.signals)
        if lead.status not in ("opted_out", "handed_off", "exhausted"):
            lead.stage = self.stage_for(lead.score, status=lead.status, signals=lead.signals)
        lead.touch()
        return lead

    def rescore(self, lead: Lead) -> Lead:
        lead.score = self.compute_score(lead.signals)
        if lead.status not in ("opted_out", "handed_off", "exhausted"):
            lead.stage = self.stage_for(lead.score, status=lead.status, signals=lead.signals)
        lead.touch()
        return lead

    def mark_exhausted(self, lead: Lead) -> Lead:
        lead.status = "exhausted"
        lead.stage = Stage.EXHAUSTED.value
        lead.touch()
        return lead

    def mark_handoff(self, lead: Lead, reasons: list[str]) -> Lead:
        lead.status = "handed_off"
        lead.stage = Stage.HANDOFF.value
        lead.handoff_ready = True
        lead.handoff_reasons = reasons
        lead.touch()
        return lead


def scorer_from_config(config: dict[str, Any]) -> LeadScorer:
    scoring = config.get("scoring") or {}
    weights = scoring.get("weights") or {}
    return LeadScorer(weights=weights)
