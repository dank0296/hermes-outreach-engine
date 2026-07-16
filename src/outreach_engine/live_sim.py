"""Live working-model simulation for Discord screen-share demos.

Posts a real-time ops feed into #outreach-handoffs so a screen-share
looks like the engine is running — enroll → touches → reply → score → handoff.
Not marketing slides; an activity stream.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Optional

from .notify import HandoffNotifier
from .store import JsonStore


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


def _embed(
    title: str,
    description: str,
    *,
    color: int,
    fields: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    e: dict[str, Any] = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": f"Hermes Outreach · live sim · {_now()}"},
    }
    if fields:
        e["fields"] = fields
    return e


# Discord colors
C_BLUE = 0x3498DB
C_GRAY = 0x95A5A6
C_YELLOW = 0xF1C40F
C_ORANGE = 0xE67E22
C_GREEN = 0x2ECC71
C_RED = 0xE74C3C
C_PURPLE = 0x9B59B6


class LiveSim:
    """Screen-share friendly live activity stream in Discord."""

    def __init__(self, store: Optional[JsonStore] = None, *, live: bool = True):
        self.store = store or JsonStore()
        self.store.ensure_dirs()
        self.config = self.store.load_config()
        notify = self.config.setdefault("notify", {})
        notify["primary"] = "discord"
        discord = notify.setdefault("discord", {})
        discord["enabled"] = True
        if live:
            notify["dry_run"] = False
            discord["dry_run"] = False
        else:
            notify["dry_run"] = True
            discord["dry_run"] = True
        self.live = live
        self.notifier = HandoffNotifier(self.store, config=self.config, dry_run=not live)
        self.log: list[str] = []

    def post(self, content: str = "", embeds: Optional[list[dict[str, Any]]] = None) -> str:
        st = self.notifier.post_discord(content=content, embeds=embeds or [])
        self.log.append(st)
        print(f"[{_now()}] {st} | {(content or (embeds or [{}])[0].get('title', ''))[:70]}")
        return st

    def run(self, *, pace: float = 2.5) -> dict[str, Any]:
        """Run the live working model simulation.

        pace = seconds between events (use 2.5–4 for talking room).
        """
        if not self.notifier.diagnose()["discord"]["ready"]:
            raise RuntimeError("Discord not configured (webhook / bot+channel)")

        # --- BOOT ---
        self.post(
            "🟢 **OUTREACH ENGINE ONLINE**",
            [
                _embed(
                    "System status",
                    (
                        f"**Mode:** working model (screen-share sim)\n"
                        f"**Outbound:** dry-run (no real email/SMS/calls)\n"
                        f"**Handoff feed:** this channel · live\n"
                        f"**Started:** {_now()}\n\n"
                        "_Watch this channel — activity streams here as the engine works._"
                    ),
                    color=C_GREEN,
                    fields=[
                        {"name": "Queue", "value": "5 leads", "inline": True},
                        {"name": "Sequence", "value": "crypto_discord", "inline": True},
                        {"name": "Handoff bar", "value": "score ≥ 40 / intent", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- ENROLL ---
        leads = [
            ("lead_demo_01", "Marcus Chen", "cold"),
            ("lead_demo_02", "Aisha Rahman", "watch"),
            ("lead_demo_03", "Diego Alvarez", "cold"),
            ("lead_demo_04", "Priya Nair", "cold"),
            ("lead_demo_05", "Jordan Blake", "cold"),
        ]
        self.post(
            "📥 **Batch enrolled**",
            [
                _embed(
                    "5 leads → sequence",
                    "Imported trader ICP list. Enrolled in multi-touch sequence.",
                    color=C_BLUE,
                    fields=[
                        {"name": lid, "value": f"**{name}** · {tag}", "inline": True}
                        for lid, name, tag in leads
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- TOUCH WAVE 1: EMAIL ---
        self.post(
            "📧 **Tick · Day 0 · EMAIL** (dry-run)",
            [
                _embed(
                    "Outbound: intro email × 5",
                    (
                        "Subject: *A calmer way to learn crypto markets (community invite)*\n"
                        "Logged only — not actually sent.\n"
                        "Risk disclaimer attached (no ROI promises)."
                    ),
                    color=C_GRAY,
                    fields=[
                        {"name": "Channel", "value": "email", "inline": True},
                        {"name": "Status", "value": "dry_run ✅", "inline": True},
                        {"name": "Next", "value": "SMS in 2 days", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- OPENS ---
        self.post(
            "👁️ **Signal · email_opened**",
            [
                _embed(
                    "Aisha Rahman opened email",
                    "Open tracked. Score +1 → still cold. **No owner ping** (opens alone don't handoff).",
                    color=C_YELLOW,
                    fields=[
                        {"name": "Lead", "value": "Aisha Rahman", "inline": True},
                        {"name": "Score", "value": "1 → cold", "inline": True},
                        {"name": "Notify owner?", "value": "No", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace * 0.8)

        self.post(
            "👁️ **Signal · email_opened**",
            [
                _embed(
                    "Marcus Chen opened email",
                    "Open only. No reply. Engine continues — you stay quiet.",
                    color=C_YELLOW,
                    fields=[
                        {"name": "Score", "value": "1 → cold", "inline": True},
                        {"name": "Notify owner?", "value": "No", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- TOUCH WAVE 2: SMS ---
        self.post(
            "💬 **Tick · Day 2 · SMS** (dry-run)",
            [
                _embed(
                    "Outbound: SMS bump × 5",
                    (
                        "Body preview: *…education-focused crypto Discord (no ROI promises). "
                        "Want the invite, or close your file?*\n"
                        "Logged only — Twilio not fired."
                    ),
                    color=C_GRAY,
                    fields=[
                        {"name": "Channel", "value": "sms", "inline": True},
                        {"name": "Status", "value": "dry_run ✅", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- THE REPLY (money moment) ---
        self.post(
            "🔥 **INBOUND REPLY**",
            [
                _embed(
                    "Aisha Rahman replied",
                    (
                        "> \"Interested — what's pricing for the Discord? "
                        "Can we hop on a demo call this week?\"\n\n"
                        "Classified signals:\n"
                        "• `email_replied`\n"
                        "• `asked_pricing`\n"
                        "• `explicit_demo_request`\n"
                        "• `booked_call` / call intent\n"
                        "• `interest_keywords`"
                    ),
                    color=C_ORANGE,
                    fields=[
                        {"name": "Company", "value": "Solstice Prop Desk", "inline": True},
                        {"name": "Title", "value": "Prop Trader (Crypto)", "inline": True},
                        {"name": "Touches so far", "value": "2", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- SCORE ---
        self.post(
            "📈 **Rescore**",
            [
                _embed(
                    "Aisha Rahman · score 93 · stage QUALIFIED",
                    (
                        "Criteria check:\n"
                        "✅ score ≥ 40 (93)\n"
                        "✅ stage qualified\n"
                        "✅ pricing / demo / call signals\n\n"
                        "**HANDOFF THRESHOLD MET** → notifying owner…"
                    ),
                    color=C_PURPLE,
                    fields=[
                        {"name": "Before", "value": "cold · 1", "inline": True},
                        {"name": "After", "value": "qualified · 93", "inline": True},
                        {"name": "Action", "value": "HANDOFF", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pace * 0.8)

        # --- HANDOFF (the product) ---
        self.post(
            "🚨 **OWNER HANDOFF — YOUR TURN**",
            [
                _embed(
                    "Take over: Aisha Rahman",
                    (
                        "**Why you're seeing this:** she cleared the bar.\n"
                        "Engine **paused** further automated touches.\n\n"
                        "Suggested next move: personal reply / book call / "
                        "invite to *your* trading Discord."
                    ),
                    color=C_RED,
                    fields=[
                        {"name": "Email", "value": "`demo+2@example.com`", "inline": True},
                        {"name": "Phone", "value": "`+1555…0102`", "inline": True},
                        {"name": "Score", "value": "**93**", "inline": True},
                        {
                            "name": "Reasons",
                            "value": "score≥40 · qualified · pricing · demo · call intent",
                            "inline": False,
                        },
                        {"name": "Lead ID", "value": "`lead_demo_02`", "inline": False},
                    ],
                )
            ],
        )
        time.sleep(pace)

        # --- OTHERS STILL WORKING (contrast) ---
        self.post(
            "🤖 **Background · still working cold leads**",
            [
                _embed(
                    "You are NOT notified for these",
                    (
                        "While you handle Aisha, engine continues dry-run sequence:\n"
                        "• Marcus — no real intent → will exhaust\n"
                        "• Diego — mild only → will exhaust\n"
                        "• Priya / Jordan — silent → will exhaust\n\n"
                        "**No Discord pings.** That's the filter."
                    ),
                    color=C_GRAY,
                )
            ],
        )
        time.sleep(pace)

        # --- EXHAUST ---
        self.post(
            "🗄️ **Sequence complete · cold leads exhausted**",
            [
                _embed(
                    "Pipeline snapshot",
                    (
                        "| Lead | Score | Status |\n"
                        "|------|------:|--------|\n"
                        "| Aisha Rahman | 93 | **handed_off** |\n"
                        "| Marcus Chen | 1 | exhausted |\n"
                        "| Diego Alvarez | 23 | exhausted |\n"
                        "| Priya Nair | 0 | exhausted |\n"
                        "| Jordan Blake | 0 | exhausted |\n\n"
                        f"**Handoffs: 1 · Owner interruptions: 1 · Finished: {_now()}**"
                    ),
                    color=C_BLUE,
                    fields=[
                        {
                            "name": "Product thesis",
                            "value": "24/7 cold work. Human only when worthwhile.",
                            "inline": False,
                        }
                    ],
                )
            ],
        )
        time.sleep(pace * 0.6)

        # --- CTA ---
        self.post(
            "⏭️ **Working model complete**",
            [
                _embed(
                    "What you just watched",
                    (
                        "A live ops feed of the agent:\n"
                        "enroll → touch → signal → score → **handoff** → quiet on junk.\n\n"
                        "Next: plug your ICP + brand voice. "
                        "LIVE email/SMS only when you approve."
                    ),
                    color=C_GREEN,
                )
            ],
        )

        return {
            "ok": all("ok" in x or x == "dry_run" for x in self.log),
            "events": len(self.log),
            "deliveries": self.log,
            "live": self.live,
            "pace": pace,
        }
