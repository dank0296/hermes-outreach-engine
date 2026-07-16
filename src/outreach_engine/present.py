"""Discord-first meeting presentation.

Posts a clear, non-technical story into #outreach-handoffs so you
present in Discord — not by reading terminal logs.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from .models import Lead
from .notify import HandoffNotifier
from .runner import OutreachRunner
from .store import JsonStore


def _embed(
    title: str,
    description: str,
    *,
    color: int = 0x5865F2,
    fields: Optional[list[dict[str, Any]]] = None,
    footer: str = "Hermes Outreach Engine · dry-run demo · not financial advice",
) -> dict[str, Any]:
    e: dict[str, Any] = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {"text": footer},
    }
    if fields:
        e["fields"] = fields
    return e


class DiscordPresenter:
    """Guided walkthrough posted to Discord for the friend meeting."""

    def __init__(self, store: Optional[JsonStore] = None, *, live: bool = True):
        self.store = store or JsonStore()
        self.store.ensure_dirs()
        self.config = self.store.load_config()
        # Force Discord live for presentation posts if live=True
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
        self.results: list[str] = []

    def post(self, content: str, embeds: Optional[list[dict[str, Any]]] = None) -> str:
        status = self.notifier.post_discord(content=content, embeds=embeds or [])
        self.results.append(status)
        print(f"[present] {status} | {content[:80]}")
        return status

    def run(self, *, pause: float = 1.2) -> dict[str, Any]:
        """Post the full meeting story to Discord."""

        # 1) Title card
        self.post(
            "🎬 **MEETING DEMO — Hermes Outreach Engine**",
            [
                _embed(
                    "What this is",
                    (
                        "A **24/7 AI outreach agent** for a trading Discord business.\n\n"
                        "It works cold leads on email / SMS / calls (simulated today).\n"
                        "You only get pinged when a lead is **worth your time**."
                    ),
                    color=0x5865F2,
                    fields=[
                        {
                            "name": "The promise",
                            "value": "You only talk to leads that meet criteria.",
                            "inline": False,
                        },
                        {
                            "name": "Mode today",
                            "value": "🔒 Outbound = **DRY-RUN** (nothing actually sent)\n"
                            "📢 Handoffs = **live in this channel**",
                            "inline": False,
                        },
                    ],
                )
            ],
        )
        time.sleep(pause)

        # 2) How it works
        self.post(
            "⚙️ **How it works (simple)**",
            [
                _embed(
                    "Engine loop",
                    (
                        "**1.** Load leads\n"
                        "**2.** Run multi-step sequence (email → SMS → email → call → last touch)\n"
                        "**3.** Score replies & signals\n"
                        "**4.** If criteria met → **handoff here**\n"
                        "**5.** If not → keep nurturing or mark exhausted — **you never hear about them**"
                    ),
                    color=0x57F287,
                    fields=[
                        {
                            "name": "Handoff bar (default)",
                            "value": "Score ≥ 40 **or** pricing / demo / call intent",
                            "inline": False,
                        }
                    ],
                )
            ],
        )
        time.sleep(pause)

        # 3) Cold work happening
        self.post(
            "📬 **Simulated outreach running…** (dry-run)",
            [
                _embed(
                    "5 demo trader leads enrolled",
                    (
                        "The engine is working them automatically:\n"
                        "• Day 0 — intro email\n"
                        "• Day 2 — SMS bump\n"
                        "• Day 4 — value email\n"
                        "• Day 7 — call script\n"
                        "• Day 10 — polite close\n\n"
                        "_No real messages leave the machine._"
                    ),
                    color=0xFEE75C,
                    fields=[
                        {"name": "Marcus", "value": "Cold / low signal", "inline": True},
                        {"name": "Aisha", "value": "Hot prop trader 👀", "inline": True},
                        {"name": "Diego", "value": "Mild interest", "inline": True},
                        {"name": "Priya", "value": "No reply", "inline": True},
                        {"name": "Jordan", "value": "No reply", "inline": True},
                    ],
                )
            ],
        )
        time.sleep(pause)

        # 4) Run real engine demo (generates handoff for Aisha + posts via notifier)
        runner = OutreachRunner(store=self.store, config=self.config, dry_run=True)
        # Keep outreach dry; notifier already live from presenter config
        # Re-bind runner notifier to our live one so handoff posts here
        runner.notifier = self.notifier
        runner.config["dry_run"] = True
        demo_result = runner.demo()
        time.sleep(pause)

        # 5) Explicit contrast card (in case they missed the handoff embed)
        self.post(
            "📊 **Results — this is the whole product**",
            [
                _embed(
                    "5 leads in. 1 handoff. 4 never woke you.",
                    (
                        "**✅ HANDOFF — Aisha Rahman** (score 93)\n"
                        "Prop trader · asked pricing · wants demo/call\n"
                        "→ **You take over. Engine paused her.**\n\n"
                        "**😴 No ping**\n"
                        "• Marcus — exhausted (score 1)\n"
                        "• Diego — exhausted (mild only)\n"
                        "• Priya — exhausted (silent)\n"
                        "• Jordan — exhausted (silent)\n\n"
                        "Cold noise stays automated. Attention stays expensive."
                    ),
                    color=0xED4245,
                    fields=[
                        {
                            "name": "What you do next",
                            "value": "Personal reply / call / invite to *his* trading Discord.",
                            "inline": False,
                        },
                        {
                            "name": "What you don't do",
                            "value": "Babysit cold follow-ups at 11pm.",
                            "inline": False,
                        },
                    ],
                )
            ],
        )
        time.sleep(pause)

        # 6) Close / ask
        self.post(
            "🤝 **Close**",
            [
                _embed(
                    "Questions for you",
                    (
                        "1. Does **criteria-first** match how you want to spend time?\n"
                        "2. What handoff bar feels right (score / intent)?\n"
                        "3. Pilot on dry-run with your ICP — or wire live email/SMS next?\n\n"
                        "**Options:** Pilot · Operator · Full build\n"
                        "No guaranteed trading returns. Not a signal bot. An attention filter."
                    ),
                    color=0xEB459E,
                )
            ],
        )

        return {
            "ok": True,
            "live": self.live,
            "posts": len(self.results),
            "deliveries": self.results,
            "demo_handoffs": len(demo_result.get("handoffs") or []),
            "demo_ok": bool(demo_result.get("ok")),
        }
