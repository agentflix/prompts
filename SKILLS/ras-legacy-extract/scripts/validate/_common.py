"""Shared helpers for ras-legacy-extract validators (stdlib only).

The validators read only the extraction contract (JSON files under the output root).
They never read or assume anything about the legacy stack.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterator

CONTRACT_VERSION = "1.1.0"
SKILL_DIR = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = SKILL_DIR / "schemas"

ID_PATTERNS = {
    "API": re.compile(r"^API-[A-Z0-9]{2,6}-\d{3}$"),
    "SCR": re.compile(r"^SCR-[A-Z0-9]{2,6}-\d{3}$"),
    "PAR": re.compile(r"^PAR-[A-Z0-9]{2,6}-\d{3}$"),
    "REQ": re.compile(r"^REQ-[A-Z0-9]{2,6}-[UEWSO]\d{3}$"),
    "FLW": re.compile(r"^FLW-[A-Z0-9]{2,6}-\d{2}$"),
    "PRC": re.compile(r"^PRC-[A-Z0-9]{2,6}-\d{3}$"),
    "NFR": re.compile(r"^NFR-[A-Z0-9]{2,6}-\d{3}$"),
    "JRN": re.compile(r"^JRN-\d{2}$"),
    "FND": re.compile(r"^FND-\d{3}$"),
    "UNK": re.compile(r"^UNK-\d{3}$"),
}
ANY_ID_RE = re.compile(
    r"\b(?:(?:API|SCR|PAR|PRC|NFR)-[A-Z0-9]{2,6}-\d{3}|REQ-[A-Z0-9]{2,6}-[UEWSO]\d{3}"
    r"|FLW-[A-Z0-9]{2,6}-\d{2}|JRN-\d{2}|FND-\d{3}|UNK-\d{3})\b"
)
EARS_LETTER = {"ubiquitous": "U", "event": "E", "unwanted": "W", "state": "S", "optional": "O"}


class Report:
    """Collects failures and warnings for one validator run."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def print(self) -> None:
        for w in self.warnings:
            print(f"  WARN  [{self.name}] {w}")
        for f in self.failures:
            print(f"  FAIL  [{self.name}] {f}")
        status = "OK" if not self.failures else f"{len(self.failures)} falha(s)"
        print(f"[{self.name}] {status}, {len(self.warnings)} aviso(s)")

    @property
    def ok(self) -> bool:
        return not self.failures


def base_args(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--root", required=True, help="output root of the extraction (reverse/)")
    p.add_argument("--module", help="validate only this module (directory name under 02-modules/)")
    return p


def load_json(path: Path, report: Report) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.fail(f"{path}: JSON inválido ({exc})")
        return None


class Contract:
    """Loaded view of an extraction output root."""

    def __init__(self, root: Path, report: Report) -> None:
        self.root = root
        self.manifest = load_json(root / "manifest.json", report)
        self.inventory = load_json(root / "00-inventory" / "inventory.json", report)
        self.db = load_json(root / "01-database" / "db-metadata.json", report)
        self.journeys = load_json(root / "03-journeys" / "journeys.json", report)
        self.modules: dict[str, dict] = {}
        mod_root = root / "02-modules"
        if mod_root.is_dir():
            for d in sorted(p for p in mod_root.iterdir() if p.is_dir()):
                data = load_json(d / "module.json", report)
                if data is not None:
                    self.modules[d.name] = data

    def module_dirs(self, only: str | None) -> list[str]:
        return [m for m in self.modules if only is None or m == only]

    def inventory_items(self) -> list[dict]:
        return list((self.inventory or {}).get("items", []))

    def manifest_modules(self) -> dict[str, dict]:
        return {m["name"]: m for m in (self.manifest or {}).get("modules", []) if "name" in m}


def module_entities(mod: dict) -> Iterator[tuple[str, dict]]:
    """Yield (collection, entity) for every ID-bearing entity of a module.json."""
    for coll in ("apis", "requirements", "flows", "screens"):
        for ent in mod.get(coll, []) or []:
            yield coll, ent


def covered_keys(mod: dict) -> dict[str, list[str]]:
    """Map inventory_key -> list of what covers it inside a module.json."""
    out: dict[str, list[str]] = {}

    def add(key: str | None, by: str) -> None:
        if key:
            out.setdefault(key, []).append(by)

    for ent in mod.get("apis", []) or []:
        add(ent.get("inventory_key"), ent.get("id", "?"))
    for ent in mod.get("screens", []) or []:
        add(ent.get("inventory_key"), ent.get("id", "?"))
    for ent in mod.get("data", []) or []:
        add(ent.get("inventory_key"), f"data:{ent.get('table', '?')}")
    for coll in ("requirements", "flows"):
        for ent in mod.get(coll, []) or []:
            for k in ent.get("inventory_keys", []) or []:
                add(k, ent.get("id", "?"))
    for c in mod.get("covers", []) or []:
        add(c.get("inventory_key"), ",".join(c.get("by", [])) or "covers")
    for e in mod.get("exclusions", []) or []:
        add(e.get("inventory_key"), f"excluded:{e.get('status', '?')}")
    return out


def iter_sources(obj: Any) -> Iterator[dict]:
    """Yield every source dict found under keys 'source' / 'sources' anywhere in obj."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source" and isinstance(v, dict):
                yield v
            elif k == "sources" and isinstance(v, list):
                for s in v:
                    if isinstance(s, dict):
                        yield s
            else:
                yield from iter_sources(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_sources(v)


def finish(reports: list[Report]) -> int:
    for r in reports:
        r.print()
    return 0 if all(r.ok for r in reports) else 1


def main_wrapper(fn) -> None:
    sys.exit(fn(sys.argv[1:]))
