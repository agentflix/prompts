#!/usr/bin/env python3
"""Validate IDs: format, uniqueness, module code, cross-references, JSON <-> Markdown parity."""
from __future__ import annotations

import re
from pathlib import Path

from _common import (
    ANY_ID_RE, EARS_LETTER, ID_PATTERNS, Contract, Report, base_args, finish, main_wrapper,
    module_entities,
)


def _ids_in_markdown(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(ANY_ID_RE.findall(path.read_text(encoding="utf-8")))


def _module_markdown_ids(mod_dir: Path) -> set[str]:
    ids: set[str] = set()
    for md in mod_dir.rglob("*.md"):
        if md.name == "verification-log.md":
            continue
        ids |= _ids_in_markdown(md)
    return ids


def run(argv: list[str]) -> Report:
    args = base_args("Valida IDs e referências cruzadas").parse_args(argv)
    report = Report("ids")
    root = Path(args.root)
    c = Contract(root, report)

    # Global registry of IDs (all modules, so cross-module references resolve).
    registry: dict[str, str] = {}
    for name, mod in c.modules.items():
        code = (mod.get("module") or {}).get("code", "")
        for coll, ent in module_entities(mod):
            eid = ent.get("id", "")
            prefix = eid.split("-")[0]
            pat = ID_PATTERNS.get(prefix)
            if pat is None or not pat.match(eid):
                report.fail(f"{name}/{coll}: ID inválido {eid!r}")
                continue
            if eid.split("-")[1] != code:
                report.fail(f"{name}: {eid} não usa o código do módulo '{code}'")
            if coll == "requirements":
                letter = EARS_LETTER.get(ent.get("ears_type", ""))
                if letter and eid.split("-")[2][0] != letter:
                    report.fail(f"{eid}: letra do ID não bate com ears_type '{ent.get('ears_type')}'")
            if eid in registry:
                report.fail(f"ID duplicado {eid} em {registry[eid]} e {name}")
            registry[eid] = name
    for j in (c.journeys or {}).get("journeys", []):
        jid = j.get("id", "")
        if jid in registry:
            report.fail(f"ID duplicado {jid}")
        registry[jid] = "journeys"

    findings = _ids_in_markdown(root / "findings.md")
    unknowns = _ids_in_markdown(root / "unknowns.md")
    known = set(registry) | {i for i in findings if i.startswith("FND")} | {
        i for i in unknowns if i.startswith("UNK")}

    def ref(owner: str, target: str | None) -> None:
        if target and target not in known:
            report.fail(f"{owner}: referência para ID inexistente {target}")

    for name in c.module_dirs(args.module):
        mod = c.modules[name]
        for ent in mod.get("apis", []) or []:
            for r in ent.get("requirements", []) or []:
                ref(ent.get("id", "?"), r)
        for ent in mod.get("requirements", []) or []:
            for f in ent.get("findings", []) or []:
                ref(ent.get("id", "?"), f)
        for ent in mod.get("flows", []) or []:
            for r in (ent.get("apis", []) or []) + (ent.get("requirements", []) or []):
                ref(ent.get("id", "?"), r)
        for ent in mod.get("screens", []) or []:
            for a in ent.get("actions", []) or []:
                ref(ent.get("id", "?"), a.get("api"))
                if a.get("navigates_to", "").startswith("SCR-"):
                    ref(ent.get("id", "?"), a["navigates_to"])

        # JSON <-> Markdown parity for the module's own IDs.
        mod_dir = root / "02-modules" / name
        code = (mod.get("module") or {}).get("code", "")
        json_ids = {e.get("id") for _, e in module_entities(mod)}
        md_ids = {i for i in _module_markdown_ids(mod_dir)
                  if re.match(rf"^(API|REQ|FLW|SCR)-{re.escape(code)}-", i)}
        for missing in sorted(json_ids - md_ids):
            report.fail(f"{name}: {missing} está no module.json mas não nos .md")
        for extra in sorted(md_ids - json_ids):
            report.fail(f"{name}: {extra} aparece nos .md mas não no module.json")

    if not args.module:
        for j in (c.journeys or {}).get("journeys", []):
            for s in j.get("steps", []):
                owner = f"{j.get('id')}#{s.get('n')}"
                ref(owner, s.get("screen"))
                ref(owner, s.get("api"))
                for r in s.get("requirements", []) or []:
                    ref(owner, r)

    # Inventory keys must be unique.
    seen: set[str] = set()
    for it in c.inventory_items():
        k = it.get("key")
        if k in seen:
            report.fail(f"inventory: chave duplicada {k!r}")
        seen.add(k)
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
