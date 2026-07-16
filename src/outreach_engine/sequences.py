"""Multi-touch outreach sequences for crypto Discord ICP."""

from __future__ import annotations

from typing import Any, Optional

from .models import Sequence, SequenceStep


RISK_DISCLAIMER = (
    "Risk disclaimer: Trading cryptocurrencies and using prop-style or educational "
    "trading communities involves substantial risk of loss. Nothing in this message "
    "is financial advice. Past performance is not indicative of future results. "
    "No return guarantees. DYOR."
)


def risk_disclaimer() -> str:
    return RISK_DISCLAIMER


def default_sequence() -> Sequence:
    """Educational multi-touch sequence — NO return guarantees."""
    steps = [
        SequenceStep(
            id="d0_email_intro",
            day_offset=0,
            channel="email",
            name="Intro — value + community",
            subject="A calmer way to learn crypto markets (community invite)",
            template=(
                "Hi {first_name},\n\n"
                "I'm reaching out because you look like someone who takes markets seriously — "
                "not hype, process.\n\n"
                "We run a private Discord for traders who want structured market education, "
                "peer review, and risk-first habits. Think playbooks, session recaps, and "
                "accountability — not signals-with-promises.\n\n"
                "If that resonates, reply and I'll share the invite + how onboarding works.\n\n"
                "{risk_disclaimer}\n\n"
                "— {sender_name}"
            ),
        ),
        SequenceStep(
            id="d2_sms_bump",
            day_offset=2,
            channel="sms",
            name="SMS soft bump",
            subject="",
            template=(
                "Hey {first_name} — quick note from {sender_name}. Sent a note about our "
                "education-focused crypto Discord (no ROI promises). Want the invite, or "
                "should I close your file? Reply STOP to opt out."
            ),
        ),
        SequenceStep(
            id="d4_email_social_proof",
            day_offset=4,
            channel="email",
            name="Case-style social proof",
            subject="How members use the room (no ROI claims)",
            template=(
                "Hi {first_name},\n\n"
                "A few members described the Discord as a place to:\n"
                "• journal trades with peers before size-up\n"
                "• stress-test narratives without FOMO pressure\n"
                "• practice risk framing before entries\n\n"
                "That's the product: process and community, not guaranteed outcomes.\n\n"
                "If you'd like a 15-min walkthrough of the rooms + rules, reply 'demo' "
                "or grab time and I'll send a link.\n\n"
                "{risk_disclaimer}\n\n"
                "— {sender_name}"
            ),
        ),
        SequenceStep(
            id="d7_call_attempt",
            day_offset=7,
            channel="call",
            name="Call attempt",
            subject="Call script — discovery",
            script=(
                "CALL SCRIPT — {first_name} @ {company}\n"
                "1) Permission: 'Got 2 minutes? Happy to hang up if bad time.'\n"
                "2) Context: education-first crypto Discord for serious traders / prop-adjacent.\n"
                "3) Value: structured rooms, risk culture, peer review — not signal spam.\n"
                "4) Ask: interest in invite or short demo of the workspace?\n"
                "5) Handle pricing questions factually; no performance claims.\n"
                "6) Close: book follow-up or send Discord invite + onboarding checklist.\n"
                "DISCLAIMER on call: not financial advice; trading involves loss risk.\n"
                "{risk_disclaimer}"
            ),
            template=(
                "Call attempt to {first_name} ({phone}). Script logged. "
                "{risk_disclaimer}"
            ),
        ),
        SequenceStep(
            id="d10_email_breakup",
            day_offset=10,
            channel="email",
            name="Break-up / last touch",
            subject="Closing the loop — last note from me",
            template=(
                "Hi {first_name},\n\n"
                "I'll keep this short. I've shared how our Discord works (education + risk "
                "culture, no return guarantees). If now isn't the right time, no worries — "
                "I'll close your sequence so we don't keep pinging you.\n\n"
                "If you want back in later, just reply 'reopen' or ask for the invite.\n\n"
                "{risk_disclaimer}\n\n"
                "— {sender_name}"
            ),
        ),
    ]
    return Sequence(
        id="crypto_discord_default",
        name="Crypto Discord ICP — educational 10-day",
        description="Multi-touch email/sms/call sequence for crypto traders / prop-adjacent ICP.",
        steps=steps,
        max_touches=len(steps),
    )


SEQUENCES: dict[str, Sequence] = {
    default_sequence().id: default_sequence(),
}


def get_sequence(sequence_id: str = "crypto_discord_default") -> Sequence:
    if sequence_id in SEQUENCES:
        return SEQUENCES[sequence_id]
    return default_sequence()


def sequence_from_config(config: dict[str, Any]) -> Sequence:
    seq_id = (config.get("sequence") or {}).get("id") or config.get("sequence_id") or "crypto_discord_default"
    return get_sequence(seq_id)


def render_step(
    step: SequenceStep,
    *,
    first_name: str = "there",
    last_name: str = "",
    email: str = "",
    phone: str = "",
    company: str = "",
    sender_name: str = "Alex",
    extra: Optional[dict[str, str]] = None,
) -> tuple[str, str]:
    """Return (subject, body) with template vars filled."""
    ctx = {
        "first_name": first_name or "there",
        "last_name": last_name or "",
        "email": email or "",
        "phone": phone or "n/a",
        "company": company or "your desk",
        "sender_name": sender_name,
        "risk_disclaimer": risk_disclaimer(),
    }
    if extra:
        ctx.update(extra)
    subject = (step.subject or "").format(**ctx)
    body_src = step.template or step.script or ""
    body = body_src.format(**ctx)
    return subject, body
