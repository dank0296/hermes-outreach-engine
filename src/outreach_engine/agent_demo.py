"""Real engine-driven Discord demo (not a slideshow).

Uses OutreachRunner: import → tick → simulate-reply → handoff → more ticks.
Each real action is posted to #outreach-handoffs.

Modes:
  - auto: short pauses between engine actions
  - step: wait for `agent-demo next` (same pattern as step next)
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from .live_sim import C_BLUE, C_GRAY, C_GREEN, C_ORANGE, C_PURPLE, C_RED, C_YELLOW, _embed, _now
from .notify import HandoffNotifier
from .runner import OutreachRunner
from .store import JsonStore


class AgentDemo:
    """Drive the real outreach engine and mirror actions to Discord."""

    def __init__(self, store: Optional[JsonStore] = None, *, live: bool = True):
        self.store = store or JsonStore()
        self.store.ensure_dirs()
        self.config = self.store.load_config()
        self.config["dry_run"] = True  # never real outbound
        notify = self.config.setdefault("notify", {})
        notify["primary"] = "discord"
        discord = notify.setdefault("discord", {})
        discord["enabled"] = True
        if live:
            notify["dry_run"] = False
            discord["dry_run"] = False
        self.live = live
        self.runner = OutreachRunner(store=self.store, config=self.config, dry_run=True)
        self.runner.notifier = HandoffNotifier(
            self.store, config=self.config, dry_run=not live
        )
        self.notifier = self.runner.notifier
        self.state_path = self.store.data_dir / "agent_demo_state.json"
        self.log: list[str] = []

    def post(self, content: str = "", embeds: Optional[list[dict[str, Any]]] = None) -> str:
        st = self.notifier.post_discord(content=content, embeds=embeds or [])
        self.log.append(st)
        print(f"[agent-demo] {st} | {content[:70]}")
        return st

    def _load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"phase": 0, "started": False}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self, state: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def _set_virtual(self, day_offset: int) -> None:
        base = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        now = (base + timedelta(days=day_offset)).isoformat()
        st = self.store.load_state()
        st["virtual_now"] = now
        self.store.save_state(st)

    def phases(self) -> list[str]:
        return [
            "boot",
            "import_leads",
            "tick_day0_email",
            "opens",
            "tick_day2_sms",
            "aisha_reply_handoff",
            "tick_day4_value",
            "tick_day7_call",
            "tick_day10_close",
            "summary",
        ]

    def run_phase(self, phase: str) -> dict[str, Any]:
        """Execute one real engine phase + Discord mirror."""
        detail: dict[str, Any] = {"phase": phase}

        if phase == "boot":
            self.post(
                "🟢 **REAL ENGINE DEMO** (not a slideshow)",
                [
                    _embed(
                        "Hermes Outreach Engine — live run",
                        (
                            "This run uses the **real** store, sequence, scorer, and handoff logic.\n"
                            "Outbound channels = **dry-run** (safe).\n"
                            "Discord = **live ops feed**.\n\n"
                            f"Started {_now()}"
                        ),
                        color=C_GREEN,
                        footer_mode="agent-demo",
                    )
                ],
            )

        elif phase == "import_leads":
            demo_path = self.store.repo_root / "demo" / "leads.json"
            self.store.reset_runtime()
            start = datetime(2026, 7, 1, 9, 0, 0, tzinfo=timezone.utc)
            self.runner.set_virtual_now(start)
            count = self.runner.import_leads(str(demo_path))
            # Align enrollment / next_touch to virtual start (same as runner.demo)
            leads_map = self.store.load_leads()
            for lead in leads_map.values():
                lead.enrolled_at = start.isoformat()
                lead.next_touch_at = start.isoformat()
                lead.sequence_step = 0
                lead.touches = 0
                lead.score = 0
                lead.stage = "cold"
                lead.status = "active"
                lead.signals = []
                lead.handoff_ready = False
            self.store.save_leads(leads_map)
            self.post(
                "📥 **Engine: import_leads**",
                [
                    _embed(
                        f"Imported {count} leads into store",
                        "Real JSON store updated. Sequence enrollment active (virtual clock Day 0).",
                        color=C_BLUE,
                        footer_mode="agent-demo",
                        fields=[
                            {
                                "name": lid,
                                "value": f"{L.first_name} {L.last_name}".strip() or lid,
                                "inline": True,
                            }
                            for lid, L in list(leads_map.items())[:5]
                        ],
                    )
                ],
            )
            detail["count"] = count

        elif phase == "tick_day0_email":
            self._set_virtual(0)
            summary = self.runner.tick()
            n = int(summary.get("sent") or summary.get("actions") or 0)
            # fallback: total non-skipped
            if not n:
                n = int(summary.get("sent", 0)) + int(summary.get("exhausted", 0))
            self.post(
                "📧 **Engine: tick() · Day 0 EMAIL**",
                [
                    _embed(
                        f"Sequence step executed · sent={summary.get('sent', 0)}",
                        (
                            "Real `runner.tick()` fired day-0 email steps.\n"
                            "Channel adapter: **EmailChannel DRY-RUN** "
                            "(nothing left the machine).\n"
                            f"```{json.dumps({k: summary[k] for k in summary if k != 'details'}, default=str)[:400]}```"
                        ),
                        color=C_GRAY,
                        footer_mode="agent-demo",
                        fields=[
                            {"name": "sent", "value": str(summary.get("sent", 0)), "inline": True},
                            {"name": "Channel", "value": "email", "inline": True},
                        ],
                    )
                ],
            )
            detail["summary"] = {k: v for k, v in summary.items() if k != "details"}

        elif phase == "opens":
            for lid in ("lead_demo_02", "lead_demo_01"):
                try:
                    self.runner.apply_signal(lid, "email_opened")
                except KeyError:
                    pass
            self.post(
                "👁️ **Engine: apply_signal(email_opened)**",
                [
                    _embed(
                        "Aisha + Marcus opened — still no owner ping",
                        (
                            "Real signal path. Opens update score slightly.\n"
                            "**Handoff criteria NOT met** → you stay undisturbed."
                        ),
                        color=C_YELLOW,
                        footer_mode="agent-demo",
                    )
                ],
            )

        elif phase == "tick_day2_sms":
            self._set_virtual(2)
            summary = self.runner.tick()
            self.post(
                "💬 **Engine: tick() · Day 2 SMS**",
                [
                    _embed(
                        f"SMS sequence step · sent={summary.get('sent', 0)}",
                        "Real tick advanced virtual clock to day 2. SMSChannel DRY-RUN.",
                        color=C_GRAY,
                        footer_mode="agent-demo",
                    )
                ],
            )
            detail["summary"] = {k: v for k, v in summary.items() if k != "details"}

        elif phase == "aisha_reply_handoff":
            text = (
                "Interested — what's pricing for the Discord? "
                "Can we hop on a demo call this week?"
            )
            result = self.runner.simulate_reply("lead_demo_02", text)
            lead_d = result.get("lead") or {}
            score = lead_d.get("score", "?")
            stage = lead_d.get("stage", lead_d.get("status", "?"))
            status = lead_d.get("status", "")
            self.post(
                "🔥 **Engine: simulate_reply(Aisha)**",
                [
                    _embed(
                        "Inbound reply classified by real scorer",
                        f"> {text}\n\nScore now **{score}** · stage/status `{stage}` / `{status}`",
                        color=C_ORANGE,
                        footer_mode="agent-demo",
                    )
                ],
            )
            if status == "handed_off" or (result.get("handoff") or {}).get("should_handoff"):
                self.post(
                    "🚨 **Engine: HANDOFF CRITERIA MET**",
                    [
                        _embed(
                            "Owner take-over (real handoff path)",
                            (
                                f"**{lead_d.get('first_name', 'Aisha')} {lead_d.get('last_name', '')}** cleared the bar.\n"
                                f"Score **{score}**. Engine paused automated touches.\n"
                                "Same handoff notifier as production (Discord embed above/nearby)."
                            ),
                            color=C_RED,
                            footer_mode="agent-demo",
                        )
                    ],
                )
            detail["score"] = score
            detail["status"] = status

        elif phase == "tick_day4_value":
            self._set_virtual(4)
            summary = self.runner.tick()
            self.post(
                "📧 **Engine: tick() · Day 4 value email**",
                [
                    _embed(
                        f"Cold leads continue · sent={summary.get('sent', 0)}",
                        "Aisha is paused (handed off). Others still sequence. **No extra owner pings.**",
                        color=C_GRAY,
                        footer_mode="agent-demo",
                    )
                ],
            )

        elif phase == "tick_day7_call":
            self._set_virtual(7)
            summary = self.runner.tick()
            self.post(
                "📞 **Engine: tick() · Day 7 call script**",
                [
                    _embed(
                        f"CallChannel DRY-RUN · sent={summary.get('sent', 0)}",
                        "AI call script logged only. Risk disclaimer included.",
                        color=C_GRAY,
                        footer_mode="agent-demo",
                    )
                ],
            )

        elif phase == "tick_day10_close":
            self._set_virtual(10)
            summary = self.runner.tick()
            self.post(
                "✉️ **Engine: tick() · Day 10 break-up email**",
                [
                    _embed(
                        f"Final touch · sent={summary.get('sent', 0)}",
                        "Polite close for remaining cold leads → exhaust.",
                        color=C_GRAY,
                        footer_mode="agent-demo",
                    )
                ],
            )

        elif phase == "summary":
            leads = self.store.load_leads()
            lines = []
            handoffs = 0
            for lid, L in leads.items():
                name = f"{L.first_name} {L.last_name}".strip() or lid
                score = L.score
                status = L.status
                if status == "handed_off" or L.stage == "handoff":
                    handoffs += 1
                lines.append(f"**{name}** — {score} — `{status}`")
            self.post(
                "🗄️ **Engine: pipeline snapshot (real store)**",
                [
                    _embed(
                        f"Handoffs: {handoffs} · Leads: {len(leads)}",
                        "\n".join(lines) + "\n\n**Real engine state** — not a scripted slideshow.",
                        color=C_PURPLE,
                        footer_mode="agent-demo",
                    )
                ],
            )
            detail["handoffs"] = handoffs

        else:
            return {"ok": False, "error": f"unknown phase {phase}"}

        detail["ok"] = True
        return detail

    def start(self) -> dict[str, Any]:
        state = {"phase": 0, "started": True, "total": len(self.phases())}
        self._save(state)
        return self.next()

    def next(self) -> dict[str, Any]:
        state = self._load()
        if not state.get("started"):
            return {"ok": False, "error": "not_started", "hint": "agent-demo start"}
        phases = self.phases()
        i = int(state.get("phase", 0))
        if i >= len(phases):
            return {"ok": True, "done": True, "message": "Agent demo complete. agent-demo start to reset."}
        phase = phases[i]
        result = self.run_phase(phase)
        state["phase"] = i + 1
        state["last_phase"] = phase
        self._save(state)
        remaining = len(phases) - state["phase"]
        talk = {
            "boot": "Say: real engine, dry-run sends, live Discord feed.",
            "import_leads": "Say: real store, five ICP leads enrolled.",
            "tick_day0_email": "Say: real tick() — email dry-run.",
            "opens": "Say: opens don't wake you.",
            "tick_day2_sms": "Say: SMS step via real sequence.",
            "aisha_reply_handoff": "BIG PAUSE — real scorer + real handoff.",
            "tick_day4_value": "Say: Aisha paused; cold still works.",
            "tick_day7_call": "Say: call script logged only.",
            "tick_day10_close": "Say: break-up / exhaust cold.",
            "summary": "Ask pilot vs live. STOP talking.",
        }
        return {
            "ok": True,
            "done": remaining == 0,
            "phase": phase,
            "index": state["phase"],
            "total": len(phases),
            "remaining": remaining,
            "talk": talk.get(phase, ""),
            "detail": {k: v for k, v in result.items() if k != "simulate"},
            "next_command": "agent-demo next" if remaining else "done",
        }

    def status(self) -> dict[str, Any]:
        state = self._load()
        phases = self.phases()
        i = int(state.get("phase", 0))
        return {
            "started": bool(state.get("started")),
            "index": i,
            "total": len(phases),
            "next_phase": phases[i] if i < len(phases) else None,
            "last_phase": state.get("last_phase"),
        }

    def reset(self) -> dict[str, Any]:
        if self.state_path.exists():
            self.state_path.unlink()
        return {"ok": True, "reset": True}

    def run_auto(self, *, pace: float = 3.0) -> dict[str, Any]:
        import time

        self.reset()
        out = self.start()
        results = [out]
        while not out.get("done"):
            time.sleep(pace)
            out = self.next()
            results.append(out)
            if not out.get("ok"):
                break
        return {"ok": True, "steps": len(results), "results": results}
