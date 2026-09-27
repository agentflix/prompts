#!/usr/bin/env python3
"""Validate IDs: format, uniqueness, module code, cross-references, JSON <-> Markdown parity."""
from __future__ import annotations

import re
from pathlib import Path

from _common import (
    ANY_ID_RE, EARS_LETTER, ID_PATTERNS, Contract, Report, base_args, finish, main_wrapper,
    load_json, module_entities,
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


NFR_FILES = {"SEC": "security.md", "PERF": "volumetry-performance.md",
             "SRCH": "search.md", "AVL": "availability.md"}
FND_DEF = re.compile(r"^\|\s*(FND-\d{3})\s*\|", re.M)
UNK_DEF = re.compile(r"^##\s+(UNK-\d{3})\b", re.M)
NFR_DEF = re.compile(r"^\|\s*(NFR-[A-Z0-9]{2,6}-\d{3})\s*\|", re.M)
PRC_OBJECT = re.compile(r"^\*\*Objeto\*\*:\s*`([^`]+)`", re.M)


def _defs(path: Path, pattern: re.Pattern, label: str, report: Report) -> list[str]:
    if not path.exists():
        return []
    found = pattern.findall(path.read_text(encoding="utf-8"))
    for dup in sorted({x for x in found if found.count(x) > 1}):
        report.fail(f"{label}: {dup} definido mais de uma vez")
    return found


def _markdown_definitions(root: Path, c: Contract, report: Report) -> set[str]:
    """IDs defined outside module.json: FND, UNK, NFR, PRC and PAR."""
    known: set[str] = set()
    known |= set(_defs(root / "findings.md", FND_DEF, "findings.md", report))
    known |= set(_defs(root / "unknowns.md", UNK_DEF, "unknowns.md", report))

    nfr_dir = root / "04-nfr"
    for md in sorted(nfr_dir.glob("*.md")) if nfr_dir.is_dir() else []:
        for nid in _defs(md, NFR_DEF, f"04-nfr/{md.name}", report):
            area = nid.split("-")[1]
            expected = NFR_FILES.get(area)
            if expected is None:
                report.fail(f"04-nfr/{md.name}: {nid} usa área desconhecida (use {', '.join(NFR_FILES)})")
            elif expected != md.name:
                report.fail(f"04-nfr/{md.name}: {nid} deveria estar em {expected}")
            if nid in known:
                report.fail(f"{nid} definido em mais de um arquivo de 04-nfr/")
            known.add(nid)

    db_objects: set[str] = set()
    if c.db:
        for coll in ("tables", "views", "procedures", "triggers", "sequences"):
            db_objects |= {str(o.get("name", "")).upper() for o in c.db.get(coll, [])}
    prc_dir = root / "01-database" / "procedures"
    for md in sorted(prc_dir.glob("*.md")) if prc_dir.is_dir() else []:
        pid = md.stem
        if not ID_PATTERNS["PRC"].match(pid):
            report.fail(f"01-database/procedures/{md.name}: nome deve ser PRC-<MOD>-NNN.md")
            continue
        m = PRC_OBJECT.search(md.read_text(encoding="utf-8"))
        if not m:
            report.fail(f"{pid}: falta a linha **Objeto**: `<TIPO> <NOME>`")
        elif db_objects and m.group(1).split()[-1].upper() not in db_objects:
            report.fail(f"{pid}: objeto {m.group(1)!r} não existe no db-metadata")
        known.add(pid)

    cases = root / "05-parity" / "cases"
    known |= {p.stem for p in cases.glob("*.json")} if cases.is_dir() else set()
    return known


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

    # Module identity: directory name, module.json and manifest must agree.
    manifest_mods = c.manifest_modules()
    for name, mod in c.modules.items():
        meta = mod.get("module") or {}
        if meta.get("name") != name:
            report.fail(f"02-modules/{name}: module.name é {meta.get('name')!r}, esperado {name!r}")
        if name not in manifest_mods:
            report.fail(f"02-modules/{name}: módulo não registrado no manifest")
        elif manifest_mods[name].get("code") != meta.get("code"):
            report.fail(f"{name}: código {meta.get('code')!r} difere do manifest "
                        f"{manifest_mods[name].get('code')!r}")
    codes = [m.get("code") for m in manifest_mods.values()]
    for dup in sorted({x for x in codes if codes.count(x) > 1}):
        report.fail(f"manifest: código de módulo duplicado {dup}")
    repo_names = [r.get("name") for r in (c.manifest or {}).get("repos", [])]
    for dup in sorted({x for x in repo_names if repo_names.count(x) > 1}):
        report.fail(f"manifest: repo duplicado {dup}")

    known = set(registry) | _markdown_definitions(root, c, report)

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
                if (a.get("navigates_to") or "").startswith("SCR-"):
                    ref(ent.get("id", "?"), a["navigates_to"])
        for cov in mod.get("covers", []) or []:
            for by in cov.get("by", []) or []:
                if by not in known:
                    report.fail(f"{name}: covers[{cov.get('inventory_key')!r}].by cita {by!r}, "
                                "que não é um ID existente")

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

        # Parity cases: file name == id, references resolve.
        for case in sorted((root / "05-parity" / "cases").glob("*.json")):
            data = load_json(case, report) or {}
            cid = data.get("id", "")
            if not ID_PATTERNS["PAR"].match(cid) or case.stem != cid:
                report.fail(f"05-parity/cases/{case.name}: id {cid!r} inválido ou diferente do nome do arquivo")
            ref(cid or case.name, data.get("api"))
            for r in data.get("requirements", []) or []:
                ref(cid or case.name, r)

    # Every ID cited in any Markdown file must resolve (verification logs may cite removed IDs).
    scan_root = root / "02-modules" / args.module if args.module else root
    for md in sorted(scan_root.rglob("*.md")):
        rel = md.relative_to(root)
        if md.name == "verification-log.md" or rel.parts[0] == "adapter":
            continue
        for i in sorted(_ids_in_markdown(md) - known):
            report.fail(f"{rel}: cita {i}, que não está definido em lugar nenhum")

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
