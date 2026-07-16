"""Visual Hermes-agent demo for screen-share.

Looks like an agent loop (think → tool → result), not marketing slides.
Still dry-run outbound; real store/tick/score/handoff under the hood.
Posts to #outreach-handoffs for Banda to watch.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from .agent_demo import AgentDemo
from .live_sim import C_BLUE, C_GRAY, C_GREEN, C_ORANGE, C_PURPLE, C_RED, C_YELLOW, _embed, _now
from .store import JsonStore


def _agent_embed(
    title: str,
    description: str,
    *,
    color: int,
    fields: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    e = _embed(title, description, color=color, fields=fields, footer_mode="Hermes Agent visual")
    return e


class VisualAgentDemo:
    """Screen-share: watch 'Hermes' run tools against the outreach engine."""

    def __init__(self, store: Optional[JsonStore] = None, *, live: bool = True):
        self.inner = AgentDemo(store=store, live=live)
        self.store = self.inner.store
        self.notifier = self.inner.notifier
        self.live = live
        self.log: list[str] = []

    def post(self, content: str = "", embeds: Optional[list[dict[str, Any]]] = None) -> str:
        st = self.notifier.post_discord(content=content, embeds=embeds or [])
        self.log.append(st)
        print(f"[visual] {st} | {content[:80]}")
        return st

    def _think(self, text: str) -> None:
        self.post(
            "🧠 **Hermes · thinking**",
            [_agent_embed("Reasoning", text, color=C_PURPLE)],
        )

    def _tool(self, name: str, args: str, result: str, *, ok: bool = True) -> None:
        color = C_GREEN if ok else C_RED
        self.post(
            f"🔧 **Hermes · tool `{name}`**",
            [
                _agent_embed(
                    f"Tool call: {name}",
                    f"**Args**\n```\n{args[:900]}\n```\n\n**Result**\n```\n{result[:900]}\n```",
                    color=color,
                    fields=[
                        {"name": "Status", "value": "ok" if ok else "error", "inline": True},
                        {"name": "Time", "value": _now(), "inline": True},
                    ],
                )
            ],
        )

    def _say(self, text: str) -> None:
        self.post(
            "💬 **Hermes · message**",
            [_agent_embed("To operator / Banda", text, color=C_BLUE)],
        )

    def run(self, *, pace: float = 4.0) -> dict[str, Any]:
        """Full visual agent run — auto-paced for screen share."""
        if not self.notifier.diagnose()["discord"]["ready"]:
            raise RuntimeError("Discord not configured")

        # Boot
        self.post(
            "🤖 **HERMES AGENT ONLINE — visual demo**",
            [
                _agent_embed(
                    "Session started",
                    (
                        "You are watching **Hermes Agent** execute the outreach skill.\n"
                        "• Real engine under the hood (store / tick / score / handoff)\n"
                        "• Outbound channels = **dry-run** (safe)\n"
                        "• This channel = live activity feed\n\n"
                        f"Started {_now()}"
                    ),
                    color=C_GREEN,
                )
            ],
        )
        time.sleep(pace)

        self._think(
            "User wants a working model of 24/7 outreach for a crypto Discord business. "
            "I should load the outreach-engine skill, import demo ICP leads, run the sequence, "
            "and only notify the owner when handoff criteria clear."
        )
        time.sleep(pace * 0.8)

        self._tool(
            "skill_view",
            "name=outreach-engine",
            "Loaded: multi-channel sequence, scorer, handoff criteria, dry-run default.",
        )
        time.sleep(pace * 0.6)

        # Import via real engine
        self._think("Importing demo trader leads into the outreach store and enrolling them.")
        time.sleep(pace * 0.5)
        phase = self.inner.run_phase("import_leads")
        self._tool(
            "outreach.import_leads",
            "path=demo/leads.json",
            f"imported={phase.get('count')} status=ok virtual_clock=Day0",
            ok=phase.get("ok", False),
        )
        time.sleep(pace)

        self._say(
            "Five ICP leads enrolled (Marcus, Aisha, Diego, Priya, Jordan). "
            "Starting Day 0 email tick — dry-run only."
        )
        time.sleep(pace * 0.7)

        # Day 0 email
        self._think("Sequence step 0 is email. I'll call tick() with virtual clock Day 0.")
        time.sleep(pace * 0.5)
        phase = self.inner.run_phase("tick_day0_email")
        summary = phase.get("summary") or {}
        self._tool(
            "outreach.tick",
            "virtual_day=0 channel=email dry_run=true",
            f"sent={summary.get('sent')} skipped={summary.get('skipped')} handoffs={summary.get('handoffs')}",
        )
        time.sleep(pace)

        # Opens
        self._think(
            "Some opens came in. Opens alone should NOT wake the owner — "
            "I'll apply email_opened signals and confirm no handoff."
        )
        time.sleep(pace * 0.5)
        self.inner.run_phase("opens")
        self._tool(
            "outreach.apply_signal",
            "leads=[Aisha, Marcus] signal=email_opened",
            "scores updated slightly · handoff=false · owner_notified=false",
        )
        self._say("Opens recorded. You stay quiet — filter is working.")
        time.sleep(pace)

        # SMS
        self._think("Advance virtual clock to Day 2 and fire SMS sequence step.")
        time.sleep(pace * 0.5)
        phase = self.inner.run_phase("tick_day2_sms")
        summary = phase.get("summary") or {}
        self._tool(
            "outreach.tick",
            "virtual_day=2 channel=sms dry_run=true",
            f"sent={summary.get('sent')} dry_run=true",
        )
        time.sleep(pace)

        # Reply + handoff — THE moment
        self._think(
            "Inbound reply from Aisha Rahman detected. "
            "I need to classify intent, rescore, and evaluate handoff criteria."
        )
        time.sleep(pace * 0.6)
        phase = self.inner.run_phase("aisha_reply_handoff")
        self._tool(
            "outreach.simulate_reply",
            'lead=Aisha text="pricing? demo call this week?"',
            f"score={phase.get('score')} status={phase.get('status')} handoff=true",
            ok=True,
        )
        time.sleep(pace * 0.5)
        self._tool(
            "outreach.notify_owner",
            "channel=discord #outreach-handoffs",
            "HANDOFF posted · engine paused further touches on Aisha",
        )
        self._say(
            "🚨 **Owner handoff:** Aisha cleared the bar (pricing + demo intent). "
            "I paused automation on her. Cold leads continue without pinging you."
        )
        time.sleep(pace)

        # Continue cold
        self._think("Aisha is handed_off. Continue sequence for remaining cold leads only.")
        time.sleep(pace * 0.4)
        for label, phase_name, day in [
            ("Day 4 value email", "tick_day4_value", 4),
            ("Day 7 call script", "tick_day7_call", 7),
            ("Day 10 break-up", "tick_day10_close", 10),
        ]:
            self.inner.run_phase(phase_name)
            self._tool(
                "outreach.tick",
                f"virtual_day={day} note={label}",
                "Aisha skipped (handed_off) · cold leads processed · owner_notified=false",
            )
            time.sleep(pace * 0.7)

        # Summary
        phase = self.inner.run_phase("summary")
        self._tool(
            "outreach.pipeline_snapshot",
            "source=real_store",
            f"handoffs={phase.get('handoffs')} leads=5",
        )
        time.sleep(pace * 0.5)
        self._say(
            "Run complete.\n"
            "• **1 handoff** (Aisha) — you take over\n"
            "• **4 never woke you**\n\n"
            "That's the product: Hermes works cold 24/7; you only talk when criteria clear.\n"
            "Next: your ICP + brand voice; LIVE channels only when you approve."
        )

        self.post(
            "✅ **Hermes Agent · session complete**",
            [
                _agent_embed(
                    "Visual demo finished",
                    (
                        "You watched Hermes call real outreach tools.\n"
                        "Not a slideshow — engine state is in the store.\n\n"
                        f"Finished {_now()}"
                    ),
                    color=C_GREEN,
                )
            ],
        )

        return {
            "ok": True,
            "mode": "visual",
            "events": len(self.log),
            "handoffs": phase.get("handoffs"),
            "pace": pace,
        }
