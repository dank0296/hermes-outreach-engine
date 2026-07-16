"""Interactive + auto live sim for Discord screen-share.

- live: auto-paced (old behavior)
- step: YOU advance with `step next` when done talking
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

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
    footer_mode: str = "live sim",
) -> dict[str, Any]:
    e: dict[str, Any] = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": f"Hermes Outreach · {footer_mode} · {_now()}"},
    }
    if fields:
        e["fields"] = fields
    return e


C_BLUE = 0x3498DB
C_GRAY = 0x95A5A6
C_YELLOW = 0xF1C40F
C_ORANGE = 0xE67E22
C_GREEN = 0x2ECC71
C_RED = 0xE74C3C
C_PURPLE = 0x9B59B6


class LiveSim:
    """Screen-share friendly activity stream in Discord (auto or stepped)."""

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
        self.state_path = self.store.data_dir / "step_state.json"

    def post(self, content: str = "", embeds: Optional[list[dict[str, Any]]] = None) -> str:
        st = self.notifier.post_discord(content=content, embeds=embeds or [])
        self.log.append(st)
        title = ""
        if embeds:
            title = embeds[0].get("title", "")
        print(f"[{_now()}] {st} | {(content or title)[:70]}")
        return st

    def steps(self) -> list[tuple[str, Callable[[], None]]]:
        """Ordered (id, fn) events for auto or interactive mode."""

        def boot() -> None:
            self.post(
                "🟢 **OUTREACH ENGINE ONLINE**",
                [
                    _embed(
                        "System status",
                        (
                            f"**Mode:** working model (screen-share)\n"
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

        def enroll() -> None:
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

        def email_tick() -> None:
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

        def open_aisha() -> None:
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

        def open_marcus() -> None:
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

        def sms_tick() -> None:
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

        def reply() -> None:
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

        def rescore() -> None:
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

        def handoff() -> None:
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

        def background() -> None:
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

        def exhaust() -> None:
            self.post(
                "🗄️ **Sequence complete · cold leads exhausted**",
                [
                    _embed(
                        "Pipeline snapshot",
                        (
                            "**Aisha Rahman** — 93 — **handed_off**\n"
                            "**Marcus Chen** — 1 — exhausted\n"
                            "**Diego Alvarez** — 23 — exhausted\n"
                            "**Priya Nair** — 0 — exhausted\n"
                            "**Jordan Blake** — 0 — exhausted\n\n"
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

        def done() -> None:
            self.post(
                "⏭️ **Working model complete**",
                [
                    _embed(
                        "What you just watched",
                        (
                            "Ops feed of the agent:\n"
                            "enroll → touch → signal → score → **handoff** → quiet on junk.\n\n"
                            "Next: plug your ICP + brand voice. "
                            "LIVE email/SMS only when you approve."
                        ),
                        color=C_GREEN,
                    )
                ],
            )

        return [
            ("boot", boot),
            ("enroll", enroll),
            ("email_tick", email_tick),
            ("open_aisha", open_aisha),
            ("open_marcus", open_marcus),
            ("sms_tick", sms_tick),
            ("reply", reply),
            ("rescore", rescore),
            ("handoff", handoff),
            ("background", background),
            ("exhaust", exhaust),
            ("done", done),
        ]

    # ----- interactive step state -----

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"index": 0, "started": False, "mode": "step"}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def step_start(self) -> dict[str, Any]:
        steps = self.steps()
        state = {"index": 0, "started": True, "mode": "step", "total": len(steps)}
        self._save_state(state)
        # banner in Discord
        self.post(
            "🎛️ **INTERACTIVE MODE** — presenter advances each step",
            [
                _embed(
                    "Talk at your own pace",
                    (
                        "Host runs `step next` when ready for the next event.\n"
                        f"**{len(steps)} steps** total. You control the clock."
                    ),
                    color=C_PURPLE,
                    footer_mode="step mode",
                )
            ],
        )
        # first real event
        return self.step_next()

    def step_next(self) -> dict[str, Any]:
        steps = self.steps()
        state = self._load_state()
        if not state.get("started"):
            return {"ok": False, "error": "not_started", "hint": "Run: step start"}
        idx = int(state.get("index", 0))
        if idx >= len(steps):
            return {
                "ok": True,
                "done": True,
                "index": idx,
                "total": len(steps),
                "message": "All steps complete. Run step start to reset.",
            }
        step_id, fn = steps[idx]
        fn()
        state["index"] = idx + 1
        state["last_step"] = step_id
        self._save_state(state)
        remaining = len(steps) - state["index"]
        talk_hints = {
            "boot": "Say: dry-run outbound, live handoffs in this channel.",
            "enroll": "Say: five trader leads — your kind of ICP.",
            "email_tick": "Say: Day 0 email — logged, not really sent.",
            "open_aisha": "Say: opens alone do NOT ping you.",
            "open_marcus": "Say: still quiet for the owner.",
            "sms_tick": "Say: Day 2 SMS — still automated.",
            "reply": "PAUSE — pricing + demo. Real intent.",
            "rescore": "Say: score 93, criteria cleared.",
            "handoff": "BIG PAUSE — this is YOUR moment. You take over.",
            "background": "Say: junk keeps running, no pings.",
            "exhaust": "Say: 1 handoff, 4 never woke you.",
            "done": "Ask: pilot dry-run or live next? Then STOP talking.",
        }
        return {
            "ok": True,
            "done": remaining == 0,
            "step": step_id,
            "index": state["index"],
            "total": len(steps),
            "remaining": remaining,
            "talk": talk_hints.get(step_id, ""),
            "next_command": "step next" if remaining else "step start  # to run again",
        }

    def step_status(self) -> dict[str, Any]:
        steps = self.steps()
        state = self._load_state()
        idx = int(state.get("index", 0))
        return {
            "started": bool(state.get("started")),
            "index": idx,
            "total": len(steps),
            "remaining": max(0, len(steps) - idx),
            "last_step": state.get("last_step"),
            "next_step": steps[idx][0] if idx < len(steps) else None,
        }

    def step_reset(self) -> dict[str, Any]:
        if self.state_path.exists():
            self.state_path.unlink()
        return {"ok": True, "reset": True}

    def run(self, *, pace: float = 2.5) -> dict[str, Any]:
        """Auto-run all steps with delay (legacy)."""
        import time

        if not self.notifier.diagnose()["discord"]["ready"]:
            raise RuntimeError("Discord not configured")
        for _sid, fn in self.steps():
            fn()
            time.sleep(pace)
        return {
            "ok": all("ok" in x or x == "dry_run" for x in self.log),
            "events": len(self.log),
            "deliveries": self.log,
            "live": self.live,
            "pace": pace,
        }
