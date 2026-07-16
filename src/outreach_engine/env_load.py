"""Load .env files into os.environ (no-op if already set).

Search order (first file wins per key only if key not already in environ):
  1. OUTREACH_ENV_FILE (if set)
  2. <repo>/.env
  3. /opt/data/.env                    # Hermes container / agent view
  4. /docker/hermes-agent-0gbq/data/.env  # host-mounted path if present
  5. $HERMES_HOME/.env
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional


def _candidate_paths(repo_root: Optional[Path] = None) -> list[Path]:
    paths: list[Path] = []
    explicit = os.environ.get("OUTREACH_ENV_FILE")
    if explicit:
        paths.append(Path(explicit))
    if repo_root is not None:
        paths.append(Path(repo_root) / ".env")
    paths.extend(
        [
            Path("/opt/data/.env"),
            Path("/docker/hermes-agent-0gbq/data/.env"),
        ]
    )
    hermes = os.environ.get("HERMES_HOME")
    if hermes:
        paths.append(Path(hermes) / ".env")
    # de-dupe while preserving order
    seen: set[str] = set()
    out: list[Path] = []
    for p in paths:
        key = str(p.resolve()) if p.exists() else str(p)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def load_env_files(
    repo_root: Optional[Path] = None,
    *,
    override: bool = False,
    prefixes: Optional[Iterable[str]] = None,
) -> list[str]:
    """Load KEY=VAL lines into os.environ.

    Returns list of files that were read.
    By default does not override existing env vars.
    If prefixes is set, only load keys starting with those prefixes
    (plus exact matches for common tokens).
    """
    loaded: list[str] = []
    allow = tuple(prefixes) if prefixes else None
    for path in _candidate_paths(repo_root):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        count = 0
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if not key:
                continue
            if allow and not any(key.startswith(p) or key == p for p in allow):
                # still allow related tokens
                if key not in (
                    "DISCORD_BOT_TOKEN",
                    "TELEGRAM_BOT_TOKEN",
                    "TELEGRAM_HOME_CHANNEL",
                    "HANDOFF_WEBHOOK_URL",
                ) and not key.startswith(("DISCORD_", "OUTREACH_", "TELEGRAM_", "TWILIO_", "BLAND_", "VAPI_")):
                    continue
            if not override and key in os.environ and os.environ.get(key):
                continue
            os.environ[key] = val
            count += 1
        if count:
            loaded.append(str(path))
    return loaded
