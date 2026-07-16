"""CLI entry for hermes-outreach-engine.

Usage:
  PYTHONPATH=src python -m outreach_engine.cli <command>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .runner import OutreachRunner
from .store import JsonStore, find_repo_root


DEFAULT_YAML = """# Hermes Outreach Engine — default config
# dry_run is TRUE by default: no live email/SMS/calls.

dry_run: true

sender:
  name: Alex
  from_email: outreach@example.com

channels:
  email:
    enabled: true
    dry_run: true
  sms:
    enabled: true
    dry_run: true
  call:
    enabled: true
    dry_run: true

scoring:
  weights:
    email_opened: 1
    email_replied: 15
    sms_replied: 12
    call_interest: 20
    booked_call: 25
    asked_pricing: 18
    visited_discord_invite: 10
    explicit_demo_request: 22
    interest_keywords: 12
    hostile: -50
    opt_out: 0
  stages:
    cold: [0, 9]
    warm: [10, 24]
    hot: [25, 49]
    qualified: [50, null]

handoff:
  min_score: 40
  stages:
    - hot
    - qualified
  signals_any:
    - booked_call
    - asked_pricing
    - explicit_demo_request
    - call_interest
    - interest_keywords
  block_on_opt_out: true
  block_on_hostile: false

sequence:
  id: crypto_discord_default

notify:
  primary: discord
  dry_run: true
  discord:
    enabled: true
    dry_run: true
  telegram:
    enabled: false
    dry_run: true
  webhook:
    dry_run: true

model:
  primary: xai/grok
  fallback: openrouter
"""


def _runner(dry_run: Optional[bool] = None) -> OutreachRunner:
    store = JsonStore(repo_root=find_repo_root())
    return OutreachRunner(store=store, dry_run=dry_run)


def cmd_init(_args: argparse.Namespace) -> int:
    store = JsonStore(repo_root=find_repo_root())
    store.ensure_dirs()
    cfg = store.config_path
    if not cfg.exists():
        cfg.write_text(DEFAULT_YAML, encoding="utf-8")
        print(f"Wrote {cfg}")
    else:
        print(f"Config already exists: {cfg}")
    r = OutreachRunner(store=store)
    info = r.init()
    print(json.dumps(info, indent=2))
    print("Init complete (dry_run default true).")
    return 0


def cmd_import_leads(args: argparse.Namespace) -> int:
    r = _runner()
    n = r.import_leads(args.path)
    print(f"Imported {n} leads from {args.path}")
    return 0


def cmd_list_leads(_args: argparse.Namespace) -> int:
    r = _runner()
    leads = r.list_leads()
    if not leads:
        print("No leads.")
        return 0
    for lead in leads:
        print(
            f"{lead.id:16} {lead.full_name:24} {lead.email:32} "
            f"score={lead.score:3} stage={lead.stage:10} status={lead.status:12} "
            f"touches={lead.touches} next={lead.next_touch_at}"
        )
    print(f"Total: {len(leads)}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    r = _runner()
    lead = r.score_lead(args.lead_id)
    print(json.dumps(lead.to_dict(), indent=2))
    return 0


def cmd_tick(args: argparse.Namespace) -> int:
    dry = True if args.dry_run or not getattr(args, "live", False) else False
    # --dry-run flag forces true; default from config is true
    r = _runner(dry_run=True if args.dry_run else None)
    if args.dry_run:
        r.dry_run = True
    summary = r.tick(dry_run=r.dry_run)
    print(json.dumps({k: v for k, v in summary.items() if k != "details"}, indent=2))
    for d in summary.get("details") or []:
        print(f"  {d}")
    return 0


def cmd_simulate_reply(args: argparse.Namespace) -> int:
    r = _runner()
    result = r.simulate_reply(args.lead_id, args.text)
    print(json.dumps({
        "lead_id": result["lead"]["id"],
        "score": result["lead"]["score"],
        "stage": result["lead"]["stage"],
        "status": result["lead"]["status"],
        "signals": result["signals"],
        "handoff": result["handoff"],
    }, indent=2))
    return 0


def cmd_handoffs(_args: argparse.Namespace) -> int:
    r = _runner()
    rows = r.list_handoffs()
    if not rows:
        print("No handoffs.")
        return 0
    for h in rows:
        print(
            f"{h.get('created_at')} | {h.get('name')} <{h.get('email')}> "
            f"score={h.get('score')} stage={h.get('stage')} reasons={h.get('reasons')}"
        )
    print(f"Total pending/recorded: {len(rows)}")
    return 0


def cmd_notify_diagnose(_args: argparse.Namespace) -> int:
    r = _runner()
    print(json.dumps(r.notifier.diagnose(), indent=2))
    return 0


def cmd_notify_test(args: argparse.Namespace) -> int:
    """Send (or dry-run) a sample Discord handoff embed."""
    from .models import Lead
    from .notify import HandoffNotifier

    store = JsonStore(repo_root=find_repo_root())
    store.ensure_dirs()
    config = store.load_config()
    notify = config.setdefault("notify", {})
    notify["primary"] = "discord"
    discord = notify.setdefault("discord", {})
    discord["enabled"] = True
    if args.live:
        notify["dry_run"] = False
        discord["dry_run"] = False
        print("LIVE Discord notify requested.")
    else:
        notify["dry_run"] = True
        discord["dry_run"] = True
        print("Dry-run notify test (use --live to actually post to Discord).")

    notifier = HandoffNotifier(store, config=config, dry_run=not args.live)
    lead = Lead(
        id="lead_notify_test",
        email="demo+handoff@example.com",
        first_name="Demo",
        last_name="Handoff",
        phone="+15550001111",
        company="Demo Prop Desk",
        title="Trader",
        score=93,
        stage="qualified",
        signals=["email_replied", "asked_pricing", "booked_call", "interest_keywords"],
        touches=2,
    )
    record = notifier.notify(
        lead,
        reasons=[
            "score>=40 (score=93)",
            "stage=qualified",
            "signal:asked_pricing",
            "signal:booked_call",
            "notify-test",
        ],
    )
    print(
        json.dumps(
            {"deliveries": record.get("deliveries"), "diagnose": notifier.diagnose()},
            indent=2,
        )
    )
    return 0


def cmd_demo(_args: argparse.Namespace) -> int:
    # ensure config exists
    store = JsonStore(repo_root=find_repo_root())
    store.ensure_dirs()
    if not store.config_path.exists():
        store.config_path.write_text(DEFAULT_YAML, encoding="utf-8")
    r = OutreachRunner(store=store, dry_run=True)
    result = r.demo()
    print(json.dumps({"ok": result["ok"], "handoff_count": len(result["handoffs"])}, indent=2))
    return 0 if result.get("ok") else 1


def cmd_present(args: argparse.Namespace) -> int:
    """Discord-first meeting presentation — friend watches the channel, not the terminal."""
    from .present import DiscordPresenter

    live = not args.dry_run
    print(
        "PRESENT MODE — look at Discord #outreach-handoffs (not this terminal).\n"
        f"live_posts={live}\n"
    )
    presenter = DiscordPresenter(live=live)
    if not presenter.notifier.diagnose()["discord"]["ready"]:
        print(
            "Discord not configured. Set DISCORD_HANDOFF_WEBHOOK_URL in /opt/data/.env",
            file=sys.stderr,
        )
        return 2
    result = presenter.run(pause=float(args.pause))
    print(json.dumps(result, indent=2))
    print("\n✅ Done. Switch to Discord #outreach-handoffs and walk top → bottom.")
    return 0 if result.get("ok") else 1


def cmd_live(args: argparse.Namespace) -> int:
    """Working-model live sim for screen-share — activity stream in Discord."""
    from .live_sim import LiveSim

    live = not args.dry_run
    print(
        "\n"
        "══════════════════════════════════════════════\n"
        "  LIVE WORKING MODEL — screen-share Discord\n"
        "  Open: Dank AI → #outreach-handoffs\n"
        "  Ignore this terminal. Watch the channel.\n"
        f"  pace={args.pace}s between events · live={live}\n"
        "══════════════════════════════════════════════\n"
    )
    sim = LiveSim(live=live)
    if not sim.notifier.diagnose()["discord"]["ready"]:
        print(
            "Discord not configured. Set DISCORD_HANDOFF_WEBHOOK_URL in /opt/data/.env",
            file=sys.stderr,
        )
        return 2
    result = sim.run(pace=float(args.pace))
    print(json.dumps(result, indent=2))
    print("\n✅ Live sim finished. Scroll #outreach-handoffs for the full run.")
    return 0 if result.get("ok") else 1


def cmd_step(args: argparse.Namespace) -> int:
    """Interactive slideshow-style live sim — YOU advance each card."""
    from .live_sim import LiveSim

    sim = LiveSim(live=not args.dry_run)
    if not sim.notifier.diagnose()["discord"]["ready"] and not args.dry_run:
        print("Discord not configured.", file=sys.stderr)
        return 2
    action = args.action
    if action == "start":
        result = sim.step_start()
    elif action == "next":
        result = sim.step_next()
    elif action == "status":
        result = sim.step_status()
    elif action == "reset":
        result = sim.step_reset()
    else:
        print(f"Unknown action {action}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    if result.get("talk"):
        print(f"\n💬 SAY: {result['talk']}")
    if result.get("next_command") and not result.get("done"):
        print(f"➡️  Next: PYTHONPATH=src python -m outreach_engine.cli {result['next_command']}")
    return 0 if result.get("ok", True) and not result.get("error") else 1


def cmd_agent_demo(args: argparse.Namespace) -> int:
    """REAL engine run mirrored to Discord — what Banda should see as 'working model'."""
    from .agent_demo import AgentDemo

    demo = AgentDemo(live=not args.dry_run)
    if not demo.notifier.diagnose()["discord"]["ready"] and not args.dry_run:
        print("Discord not configured.", file=sys.stderr)
        return 2
    action = args.action
    if action == "start":
        print(
            "\n══════════════════════════════════════════════\n"
            "  REAL ENGINE DEMO (not slideshow)\n"
            "  Screen-share: #outreach-handoffs\n"
            "  Advance: agent-demo next  (when done talking)\n"
            "══════════════════════════════════════════════\n"
        )
        result = demo.start()
    elif action == "next":
        result = demo.next()
    elif action == "status":
        result = demo.status()
    elif action == "reset":
        result = demo.reset()
    elif action == "auto":
        result = demo.run_auto(pace=float(args.pace))
    else:
        print(f"Unknown action {action}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, default=str))
    if isinstance(result, dict) and result.get("talk"):
        print(f"\n💬 SAY: {result['talk']}")
    if isinstance(result, dict) and result.get("next_command") and not result.get("done"):
        print(
            f"➡️  Next: PYTHONPATH=src python -m outreach_engine.cli {result['next_command']}"
        )
    return 0 if (not isinstance(result, dict)) or result.get("ok", True) else 1


def cmd_visual(args: argparse.Namespace) -> int:
    """Watch Hermes Agent visually execute tools (screen-share for Banda)."""
    from .visual_agent import VisualAgentDemo

    print(
        "\n══════════════════════════════════════════════\n"
        "  VISUAL HERMES AGENT DEMO\n"
        "  Screen-share: Discord #outreach-handoffs\n"
        "  You watch — agent thinks + calls tools\n"
        f"  pace={args.pace}s · live={not args.dry_run}\n"
        "══════════════════════════════════════════════\n"
    )
    demo = VisualAgentDemo(live=not args.dry_run)
    if not demo.notifier.diagnose()["discord"]["ready"] and not args.dry_run:
        print("Discord not configured.", file=sys.stderr)
        return 2
    result = demo.run(pace=float(args.pace))
    print(json.dumps(result, indent=2))
    print("\n✅ Visual agent run finished. Scroll #outreach-handoffs.")
    return 0 if result.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="outreach_engine",
        description="Hermes Outreach Engine — dry-run-first multi-touch outreach for crypto Discord ICP",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init", help="Seed data dir + default config")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("import-leads", help="Import leads from CSV or JSON")
    sp.add_argument("path", help="Path to leads.csv or leads.json")
    sp.set_defaults(func=cmd_import_leads)

    sp = sub.add_parser("list-leads", help="List leads in the store")
    sp.set_defaults(func=cmd_list_leads)

    sp = sub.add_parser("score", help="Rescore a lead")
    sp.add_argument("lead_id")
    sp.set_defaults(func=cmd_score)

    sp = sub.add_parser("tick", help="Process due sequence steps")
    sp.add_argument("--dry-run", action="store_true", default=False, help="Force dry-run mode")
    sp.set_defaults(func=cmd_tick)

    sp = sub.add_parser("simulate-reply", help="Inject inbound reply text")
    sp.add_argument("lead_id")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_simulate_reply)

    sp = sub.add_parser("handoffs", help="List recorded handoffs")
    sp.set_defaults(func=cmd_handoffs)

    sp = sub.add_parser(
        "notify-diagnose",
        help="Show Discord/Telegram handoff config readiness",
    )
    sp.set_defaults(func=cmd_notify_diagnose)

    sp = sub.add_parser(
        "notify-test",
        help="Post a sample handoff to Discord (dry-run unless --live)",
    )
    sp.add_argument(
        "--live",
        action="store_true",
        help="Actually post to Discord (requires webhook or bot+channel)",
    )
    sp.set_defaults(func=cmd_notify_test)

    sp = sub.add_parser("demo", help="Full canned end-to-end dry-run demo")
    sp.set_defaults(func=cmd_demo)

    sp = sub.add_parser(
        "present",
        help="Discord-first meeting demo — posts the story into #outreach-handoffs",
    )
    sp.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't post to Discord (print only)",
    )
    sp.add_argument(
        "--pause",
        type=float,
        default=1.2,
        help="Seconds between Discord posts (default 1.2)",
    )
    sp.set_defaults(func=cmd_present)

    sp = sub.add_parser(
        "live",
        help="WORKING MODEL screen-share: auto-paced activity stream (fast)",
    )
    sp.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't post to Discord",
    )
    sp.add_argument(
        "--pace",
        type=float,
        default=2.5,
        help="Seconds between live events (default 2.5; use 3.5 if talking)",
    )
    sp.set_defaults(func=cmd_live)

    sp = sub.add_parser(
        "step",
        help="Interactive cards: step start, then step next when YOU are ready",
    )
    sp.add_argument(
        "action",
        choices=["start", "next", "status", "reset"],
        help="start | next | status | reset",
    )
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_step)

    sp = sub.add_parser(
        "agent-demo",
        help="REAL engine demo in Discord: agent-demo start / next (Banda working model)",
    )
    sp.add_argument(
        "action",
        choices=["start", "next", "status", "reset", "auto"],
        help="start | next | status | reset | auto",
    )
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--pace", type=float, default=3.0, help="Only for auto mode")
    sp.set_defaults(func=cmd_agent_demo)

    sp = sub.add_parser(
        "visual",
        help="VISUAL Hermes agent: watch think/tool/result stream in Discord (screen-share)",
    )
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument(
        "--pace",
        type=float,
        default=4.0,
        help="Seconds between agent actions (default 4; use 5–6 if narrating)",
    )
    sp.set_defaults(func=cmd_visual)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    # Auto-load Discord/Twilio/etc secrets from host/container .env files
    from .env_load import load_env_files
    from .store import find_repo_root

    loaded = load_env_files(find_repo_root())
    if loaded and os.environ.get("OUTREACH_DEBUG_ENV"):
        print(f"[env] loaded from: {', '.join(loaded)}", file=sys.stderr)

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — CLI boundary
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
