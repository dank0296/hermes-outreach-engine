"""OutreachRunner — tick leads, send next step, score, maybe handoff."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from .channels import BaseChannel, build_channels
from .criteria import HandoffCriteria, classify_reply, evaluate
from .models import Activity, ActivityType, Lead, SignalType, iso_now
from .notify import HandoffNotifier
from .scorer import LeadScorer, scorer_from_config
from .sequences import get_sequence, render_step, sequence_from_config
from .store import JsonStore


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    v = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _fmt_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


class OutreachRunner:
    def __init__(
        self,
        store: Optional[JsonStore] = None,
        config: Optional[dict[str, Any]] = None,
        *,
        dry_run: Optional[bool] = None,
    ):
        self.store = store or JsonStore()
        self.store.ensure_dirs()
        self.config = config if config is not None else self.store.load_config()
        if dry_run is not None:
            self.config["dry_run"] = dry_run
        self.dry_run = bool(self.config.get("dry_run", True))
        self.scorer = scorer_from_config(self.config)
        self.criteria = HandoffCriteria.from_config(self.config)
        self.sequence = sequence_from_config(self.config)
        self.channels: dict[str, BaseChannel] = build_channels(self.config, dry_run=self.dry_run)
        sender = (self.config.get("sender") or {})
        self.sender_name = sender.get("name") or self.config.get("sender_name") or "Alex"
        self.notifier = HandoffNotifier(self.store, config=self.config, dry_run=self.dry_run)

    # ----- clock -----
    def now(self) -> datetime:
        state = self.store.load_state()
        if state.get("virtual_now"):
            dt = _parse_dt(state["virtual_now"])
            if dt:
                return dt
        return datetime.now(timezone.utc)

    def set_virtual_now(self, dt: datetime) -> None:
        state = self.store.load_state()
        state["virtual_now"] = _fmt_dt(dt)
        self.store.save_state(state)

    def advance_days(self, days: float) -> datetime:
        n = self.now() + timedelta(days=days)
        self.set_virtual_now(n)
        return n

    # ----- init / import -----
    def init(self) -> dict[str, Any]:
        self.store.ensure_dirs()
        cfg_path = self.store.config_path
        if not cfg_path.exists():
            # write will be done by CLI from template; here just ensure data
            pass
        self.store.save_state({"virtual_now": _fmt_dt(datetime.now(timezone.utc)), "tick_count": 0})
        if not self.store.leads_path.exists():
            self.store.save_leads([])
        return {
            "data_dir": str(self.store.data_dir),
            "config": str(self.store.config_path),
            "dry_run": self.dry_run,
        }

    def import_leads(self, path: str | Path) -> int:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_text(encoding="utf-8")
        leads: list[Lead] = []
        if path.suffix.lower() == ".json":
            data = json.loads(text)
            items = data.get("leads", data) if isinstance(data, dict) else data
            for item in items:
                leads.append(self._lead_from_mapping(item))
        else:
            # CSV
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    leads.append(self._lead_from_mapping(row))
        now = _fmt_dt(self.now())
        for lead in leads:
            if not lead.enrolled_at:
                lead.enrolled_at = now
            if not lead.next_touch_at:
                lead.next_touch_at = now
            lead.sequence_id = lead.sequence_id or self.sequence.id
        self.store.upsert_leads(leads)
        return len(leads)

    def _lead_from_mapping(self, item: dict[str, Any]) -> Lead:
        # normalize keys
        norm = {str(k).strip().lower().replace(" ", "_"): v for k, v in item.items()}
        email = norm.get("email") or norm.get("email_address")
        if not email:
            raise ValueError(f"Lead missing email: {item}")
        tags = norm.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        lead = Lead.create(
            email=str(email),
            first_name=str(norm.get("first_name") or norm.get("firstname") or ""),
            last_name=str(norm.get("last_name") or norm.get("lastname") or ""),
            phone=str(norm.get("phone") or norm.get("mobile") or ""),
            company=str(norm.get("company") or norm.get("firm") or ""),
            title=str(norm.get("title") or norm.get("role") or ""),
            source=str(norm.get("source") or "import"),
            tags=list(tags),
            notes=str(norm.get("notes") or ""),
            lead_id=str(norm["id"]) if norm.get("id") else None,
            sequence_id=str(norm.get("sequence_id") or self.sequence.id),
        )
        return lead

    # ----- listing / scoring -----
    def list_leads(self) -> list[Lead]:
        return list(self.store.load_leads().values())

    def score_lead(self, lead_id: str) -> Lead:
        lead = self.store.get_lead(lead_id)
        if not lead:
            raise KeyError(f"Unknown lead: {lead_id}")
        lead = self.scorer.rescore(lead)
        self.store.upsert_lead(lead)
        return lead

    # ----- tick -----
    def tick(self, *, dry_run: Optional[bool] = None) -> dict[str, Any]:
        if dry_run is not None:
            self.dry_run = dry_run
            self.channels = build_channels(self.config, dry_run=dry_run)
            self.notifier.dry_run = dry_run

        now = self.now()
        leads = self.store.load_leads()
        sent = 0
        handoffs = 0
        exhausted = 0
        skipped = 0
        details: list[dict[str, Any]] = []

        for lead in sorted(leads.values(), key=lambda l: l.id):
            if lead.status in ("opted_out", "handed_off", "exhausted"):
                skipped += 1
                continue
            if lead.handoff_ready:
                skipped += 1
                continue

            seq = get_sequence(lead.sequence_id or self.sequence.id)
            if lead.sequence_step >= len(seq.steps):
                # max touches without response → exhausted (no handoff)
                if not lead.signals or set(lead.signals) <= {SignalType.EMAIL_OPENED.value}:
                    self.scorer.mark_exhausted(lead)
                    self.store.upsert_lead(lead)
                    self.store.append_activity(
                        Activity.create(
                            lead.id,
                            ActivityType.SYSTEM.value,
                            body="Marked exhausted: max touches without meaningful response",
                            dry_run=self.dry_run,
                        )
                    )
                    exhausted += 1
                    details.append({"lead_id": lead.id, "action": "exhausted"})
                continue

            next_at = _parse_dt(lead.next_touch_at) or now
            if next_at > now:
                skipped += 1
                continue

            step = seq.steps[lead.sequence_step]
            subject, body = render_step(
                step,
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
                phone=lead.phone,
                company=lead.company,
                sender_name=self.sender_name,
            )
            channel_key = step.channel
            channel = self.channels.get(channel_key)
            if not channel:
                details.append({"lead_id": lead.id, "action": "no_channel", "channel": channel_key})
                continue

            to = lead.email if channel_key == "email" else (lead.phone or lead.email)
            result = channel.send(
                to=to,
                subject=subject,
                body=body,
                lead_id=lead.id,
                step_id=step.id,
            )
            act = channel.to_activity(result, lead_id=lead.id, step_id=step.id, subject=subject, body=body)
            self.store.append_activity(act)

            lead.touches += 1
            lead.sequence_step += 1
            lead.last_touch_at = _fmt_dt(now)
            # schedule next
            if lead.sequence_step < len(seq.steps):
                next_step = seq.steps[lead.sequence_step]
                # day_offset is absolute from enrollment
                enrolled = _parse_dt(lead.enrolled_at) or now
                lead.next_touch_at = _fmt_dt(enrolled + timedelta(days=next_step.day_offset))
            else:
                lead.next_touch_at = None

            # passive open signal for email in dry-run demos? leave to simulate
            lead = self.scorer.rescore(lead)
            hr = evaluate(lead, self.criteria)
            if hr.should_handoff:
                lead = self.scorer.mark_handoff(lead, hr.reasons)
                lead.handoff_at = _fmt_dt(now)
                self.store.upsert_lead(lead)
                self.notifier.notify(lead, hr.reasons)
                handoffs += 1
                details.append({"lead_id": lead.id, "action": "handoff", "step": step.id, "reasons": hr.reasons})
            else:
                # if finished sequence with weak signals → exhausted
                if lead.sequence_step >= len(seq.steps) and lead.score < self.criteria.min_score:
                    if lead.stage not in ("hot", "qualified"):
                        self.scorer.mark_exhausted(lead)
                        exhausted += 1
                        details.append({"lead_id": lead.id, "action": "exhausted_after_sequence", "step": step.id})
                    else:
                        details.append({"lead_id": lead.id, "action": "sent", "step": step.id})
                else:
                    details.append({"lead_id": lead.id, "action": "sent", "step": step.id, "channel": channel_key})
                self.store.upsert_lead(lead)
            sent += 1

        state = self.store.load_state()
        state["tick_count"] = int(state.get("tick_count") or 0) + 1
        state["last_tick_at"] = _fmt_dt(now)
        self.store.save_state(state)

        summary = {
            "now": _fmt_dt(now),
            "sent": sent,
            "handoffs": handoffs,
            "exhausted": exhausted,
            "skipped": skipped,
            "details": details,
            "dry_run": self.dry_run,
        }
        return summary

    # ----- inbound -----
    def simulate_reply(self, lead_id: str, text: str, *, channel: str = "email") -> dict[str, Any]:
        lead = self.store.get_lead(lead_id)
        if not lead:
            raise KeyError(f"Unknown lead: {lead_id}")

        signals = classify_reply(text, self.criteria)
        # map channel reply
        if channel == "sms" and SignalType.EMAIL_REPLIED.value in signals:
            signals = [SignalType.SMS_REPLIED.value if s == SignalType.EMAIL_REPLIED.value else s for s in signals]
            if SignalType.SMS_REPLIED.value not in signals:
                signals.append(SignalType.SMS_REPLIED.value)
        elif channel == "email" and SignalType.EMAIL_REPLIED.value not in signals and SignalType.OPT_OUT.value not in signals:
            signals.append(SignalType.EMAIL_REPLIED.value)

        self.store.append_activity(
            Activity.create(
                lead.id,
                ActivityType.INBOUND.value,
                channel=channel,
                body=text,
                dry_run=self.dry_run,
                meta={"inferred_signals": signals},
            )
        )

        for sig in signals:
            lead = self.scorer.apply_signal(lead, sig)
            self.store.append_activity(
                Activity.create(
                    lead.id,
                    ActivityType.SIGNAL.value,
                    signal=sig,
                    channel=channel,
                    dry_run=self.dry_run,
                    body=f"Applied signal {sig} from reply",
                )
            )

        hr = evaluate(lead, self.criteria)
        handoff_record = None
        if hr.should_handoff and lead.status not in ("handed_off", "opted_out"):
            lead = self.scorer.mark_handoff(lead, hr.reasons)
            lead.handoff_at = _fmt_dt(self.now())
            handoff_record = self.notifier.notify(lead, hr.reasons)
            self.store.append_activity(
                Activity.create(
                    lead.id,
                    ActivityType.HANDOFF.value,
                    body="; ".join(hr.reasons),
                    dry_run=self.dry_run,
                    meta={"reasons": hr.reasons},
                )
            )

        self.store.upsert_lead(lead)
        return {
            "lead": lead.to_dict(),
            "signals": signals,
            "handoff": hr.to_dict(),
            "handoff_record": handoff_record,
        }

    def apply_signal(self, lead_id: str, signal: str) -> Lead:
        lead = self.store.get_lead(lead_id)
        if not lead:
            raise KeyError(f"Unknown lead: {lead_id}")
        lead = self.scorer.apply_signal(lead, signal)
        self.store.append_activity(
            Activity.create(lead.id, ActivityType.SIGNAL.value, signal=signal, dry_run=self.dry_run)
        )
        hr = evaluate(lead, self.criteria)
        if hr.should_handoff and lead.status not in ("handed_off", "opted_out"):
            lead = self.scorer.mark_handoff(lead, hr.reasons)
            lead.handoff_at = _fmt_dt(self.now())
            self.notifier.notify(lead, hr.reasons)
        self.store.upsert_lead(lead)
        return lead

    def list_handoffs(self) -> list[dict[str, Any]]:
        return self.store.list_handoffs()

    # ----- full demo -----
    def demo(self) -> dict[str, Any]:
        """
        End-to-end canned dry-run:
        - reset runtime data
        - import demo leads
        - virtually advance through sequence days
        - inject warm replies for at least one lead → handoff
        """
        print("=== Hermes Outreach Engine DEMO (dry-run) ===")
        self.dry_run = True
        self.config["dry_run"] = True
        self.channels = build_channels(self.config, dry_run=True)
        self.notifier.dry_run = True

        self.store.reset_runtime()
        self.store.ensure_dirs()
        start = datetime(2026, 7, 1, 9, 0, 0, tzinfo=timezone.utc)
        self.set_virtual_now(start)

        demo_path = self.store.repo_root / "demo" / "leads.json"
        if not demo_path.exists():
            raise FileNotFoundError(f"Missing demo leads at {demo_path}")
        n = self.import_leads(demo_path)
        print(f"Imported {n} demo leads from {demo_path}")

        # Align enrollment / next_touch to virtual start
        leads = self.store.load_leads()
        for lead in leads.values():
            lead.enrolled_at = _fmt_dt(start)
            lead.next_touch_at = _fmt_dt(start)
            lead.sequence_step = 0
            lead.touches = 0
            lead.score = 0
            lead.stage = "cold"
            lead.status = "active"
            lead.signals = []
            lead.handoff_ready = False
        self.store.save_leads(leads)

        timeline_days = [0, 2, 4, 7, 10]
        tick_summaries = []

        # Day 0 touches
        print(f"\n--- Virtual day 0 @ {self.now().date()} ---")
        tick_summaries.append(self.tick(dry_run=True))

        # Simulate passive opens on a few leads after intro
        leads = self.store.load_leads()
        warm_id = None
        cold_reply_id = None
        for lid, lead in leads.items():
            if "warm" in (lead.tags or []) or lead.meta.get("demo_role") == "warm":
                warm_id = lid
            if lead.meta.get("demo_role") == "curious":
                cold_reply_id = lid
        if not warm_id:
            # pick second lead as warm target
            ids = sorted(leads.keys())
            warm_id = ids[1] if len(ids) > 1 else ids[0]
        if not cold_reply_id:
            ids = sorted(leads.keys())
            cold_reply_id = ids[2] if len(ids) > 2 else ids[0]

        print(f"\n--- Simulate email opens ---")
        for lid in list(leads.keys())[:3]:
            self.apply_signal(lid, SignalType.EMAIL_OPENED.value)

        # Day 2
        self.set_virtual_now(start + timedelta(days=2, hours=1))
        print(f"\n--- Virtual day 2 @ {self.now().date()} ---")
        tick_summaries.append(self.tick(dry_run=True))

        # Warm lead replies with interest on day 3
        self.set_virtual_now(start + timedelta(days=3, hours=2))
        print(f"\n--- Simulate warm reply from {warm_id} ---")
        reply_result = self.simulate_reply(
            warm_id,
            "Hey this sounds interesting — can we book a demo? Also what's the pricing for the Discord?",
            channel="email",
        )
        print(f"Warm lead score={reply_result['lead']['score']} stage={reply_result['lead']['stage']}")

        # Day 4 — remaining active leads
        self.set_virtual_now(start + timedelta(days=4, hours=1))
        print(f"\n--- Virtual day 4 @ {self.now().date()} ---")
        tick_summaries.append(self.tick(dry_run=True))

        # Curious lead mild reply (not enough alone maybe — add invite visit)
        if cold_reply_id != warm_id:
            print(f"\n--- Simulate mild engagement from {cold_reply_id} ---")
            self.apply_signal(cold_reply_id, SignalType.VISITED_DISCORD_INVITE.value)
            self.simulate_reply(cold_reply_id, "Thanks, I'll check it out later.", channel="sms")

        # Day 7
        self.set_virtual_now(start + timedelta(days=7, hours=1))
        print(f"\n--- Virtual day 7 @ {self.now().date()} ---")
        tick_summaries.append(self.tick(dry_run=True))

        # Day 10
        self.set_virtual_now(start + timedelta(days=10, hours=1))
        print(f"\n--- Virtual day 10 @ {self.now().date()} ---")
        tick_summaries.append(self.tick(dry_run=True))

        handoffs = self.list_handoffs()
        final_leads = [l.to_dict() for l in self.list_leads()]

        print("\n=== DEMO SUMMARY ===")
        print(f"Leads: {len(final_leads)}")
        print(f"Handoffs: {len(handoffs)}")
        for h in handoffs:
            print(f"  - {h.get('name')} <{h.get('email')}> score={h.get('score')} reasons={h.get('reasons')}")
        for ld in final_leads:
            print(
                f"  lead {ld['id']}: {ld.get('first_name')} score={ld['score']} "
                f"stage={ld['stage']} status={ld['status']} touches={ld['touches']}"
            )

        if not handoffs:
            raise RuntimeError("Demo failed: expected at least one handoff notification")

        return {
            "leads": final_leads,
            "handoffs": handoffs,
            "ticks": tick_summaries,
            "warm_lead_id": warm_id,
            "ok": True,
        }
