"""JSON file store under data/ at repo root."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from .models import Activity, Lead, iso_now


def find_repo_root(start: Optional[Path] = None) -> Path:
    """Walk up from start (or this file) looking for config/ or pyproject.toml."""
    here = start or Path(__file__).resolve().parent
    for p in [here, *here.parents]:
        if (p / "config").is_dir() or (p / "pyproject.toml").is_file():
            return p
        if p.name == "hermes-outreach-engine":
            return p
    # fallback: cwd
    cwd = Path.cwd()
    if (cwd / "config").is_dir() or (cwd / "src" / "outreach_engine").is_dir():
        return cwd
    return cwd


class JsonStore:
    """Simple JSON file persistence for leads, activities, handoffs, config overrides."""

    def __init__(self, data_dir: Optional[str | Path] = None, repo_root: Optional[str | Path] = None):
        self.repo_root = Path(repo_root) if repo_root else find_repo_root()
        self.data_dir = Path(data_dir) if data_dir else self.repo_root / "data"
        self.leads_path = self.data_dir / "leads.json"
        self.activities_path = self.data_dir / "activities.jsonl"
        self.handoffs_path = self.data_dir / "handoffs.jsonl"
        self.state_path = self.data_dir / "state.json"
        self.config_path = self.repo_root / "config" / "default.yaml"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.repo_root / "config").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "demo").mkdir(parents=True, exist_ok=True)

    # ----- low-level IO -----
    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        tmp.replace(path)

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    # ----- config -----
    def load_config(self) -> dict[str, Any]:
        path = self.config_path
        if not path.exists():
            return {}
        try:
            import yaml  # type: ignore
        except ImportError:
            # minimal YAML subset via json if pure-yaml not available — try stdlib fallback
            text = path.read_text(encoding="utf-8")
            # attempt simple load with yaml if present, else use a tiny parser path
            try:
                import yaml as _y  # noqa
                return _y.safe_load(text) or {}
            except ImportError:
                return self._parse_simple_yaml(text)
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def _parse_simple_yaml(text: str) -> dict[str, Any]:
        """Very small YAML subset for dry-run without PyYAML (indent-based maps/lists)."""
        try:
            import yaml  # type: ignore
            return yaml.safe_load(text) or {}
        except ImportError:
            pass
        # Prefer json if someone swapped extension; else return empty and rely on code defaults
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Use a minimal recursive descent for the config we ship
            return _minimal_yaml_load(text)

    # ----- leads -----
    def load_leads(self) -> dict[str, Lead]:
        raw = self._read_json(self.leads_path, {"leads": []})
        items = raw.get("leads", raw) if isinstance(raw, dict) else raw
        leads: dict[str, Lead] = {}
        for item in items or []:
            lead = Lead.from_dict(item)
            leads[lead.id] = lead
        return leads

    def save_leads(self, leads: dict[str, Lead] | list[Lead]) -> None:
        if isinstance(leads, dict):
            items = list(leads.values())
        else:
            items = leads
        payload = {
            "updated_at": iso_now(),
            "leads": [l.to_dict() for l in items],
        }
        self._write_json(self.leads_path, payload)

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        return self.load_leads().get(lead_id)

    def upsert_lead(self, lead: Lead) -> Lead:
        leads = self.load_leads()
        lead.touch()
        leads[lead.id] = lead
        self.save_leads(leads)
        return lead

    def upsert_leads(self, new_leads: list[Lead]) -> int:
        leads = self.load_leads()
        for lead in new_leads:
            lead.touch()
            leads[lead.id] = lead
        self.save_leads(leads)
        return len(new_leads)

    # ----- activities -----
    def append_activity(self, activity: Activity) -> None:
        self._append_jsonl(self.activities_path, activity.to_dict())

    def list_activities(self, lead_id: Optional[str] = None) -> list[Activity]:
        rows = self._read_jsonl(self.activities_path)
        acts = [Activity.from_dict(r) for r in rows]
        if lead_id:
            acts = [a for a in acts if a.lead_id == lead_id]
        return acts

    # ----- handoffs -----
    def append_handoff(self, record: dict[str, Any]) -> None:
        self._append_jsonl(self.handoffs_path, record)

    def list_handoffs(self) -> list[dict[str, Any]]:
        return self._read_jsonl(self.handoffs_path)

    # ----- virtual clock / state -----
    def load_state(self) -> dict[str, Any]:
        return self._read_json(self.state_path, {"virtual_now": None, "tick_count": 0})

    def save_state(self, state: dict[str, Any]) -> None:
        self._write_json(self.state_path, state)

    def reset_runtime(self) -> None:
        """Clear runtime data (leads/activities/handoffs/state) but keep config."""
        self.ensure_dirs()
        for p in (self.leads_path, self.activities_path, self.handoffs_path, self.state_path):
            if p.exists():
                p.unlink()
        self.save_leads([])
        self.save_state({"virtual_now": None, "tick_count": 0})


def _minimal_yaml_load(text: str) -> dict[str, Any]:
    """Indent-based YAML loader for maps, lists, scalars used by default.yaml."""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        # strip inline comments carefully
        if " #" in raw:
            raw = raw.split(" #", 1)[0].rstrip()
        lines.append(raw)

    def parse_scalar(s: str) -> Any:
        s = s.strip()
        if s in ("true", "True"):
            return True
        if s in ("false", "False"):
            return False
        if s in ("null", "None", "~", ""):
            return None
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            return s

    def indent_of(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_block(idx: int, min_indent: int) -> tuple[Any, int]:
        if idx >= len(lines):
            return None, idx
        ind = indent_of(lines[idx])
        if ind < min_indent:
            return None, idx
        # list?
        if lines[idx].lstrip().startswith("- "):
            items: list[Any] = []
            while idx < len(lines) and indent_of(lines[idx]) == ind and lines[idx].lstrip().startswith("- "):
                content = lines[idx].lstrip()[2:].strip()
                if content and ":" in content and not content.endswith(":"):
                    # inline map item like - key: val — treat as string map of one? rare
                    key, _, val = content.partition(":")
                    # could be nested object starting with key
                    obj = {key.strip(): parse_scalar(val)}
                    # check following indented keys under this list item
                    nxt = idx + 1
                    while nxt < len(lines) and indent_of(lines[nxt]) > ind and not lines[nxt].lstrip().startswith("- "):
                        kline = lines[nxt]
                        k = kline.strip()
                        if ":" in k:
                            kk, _, vv = k.partition(":")
                            kk = kk.strip()
                            vv = vv.strip()
                            if vv == "":
                                child, nxt = parse_block(nxt + 1, indent_of(kline) + 1)
                                obj[kk] = child
                            else:
                                obj[kk] = parse_scalar(vv)
                                nxt += 1
                        else:
                            nxt += 1
                    items.append(obj)
                    idx = nxt
                elif content.endswith(":") or content == "":
                    key = content[:-1].strip() if content.endswith(":") else None
                    child, idx = parse_block(idx + 1, ind + 1)
                    if key:
                        items.append({key: child})
                    else:
                        items.append(child)
                else:
                    items.append(parse_scalar(content))
                    idx += 1
            return items, idx

        # map
        result: dict[str, Any] = {}
        while idx < len(lines) and indent_of(lines[idx]) == ind:
            line = lines[idx]
            if line.lstrip().startswith("- "):
                break
            if ":" not in line:
                idx += 1
                continue
            key, _, rest = line.strip().partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest == "":
                # nested
                child, idx = parse_block(idx + 1, ind + 1)
                result[key] = child
            else:
                result[key] = parse_scalar(rest)
                idx += 1
        return result, idx

    root, _ = parse_block(0, 0)
    return root if isinstance(root, dict) else {}
