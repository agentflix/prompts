#!/usr/bin/env python3
"""Validate coverage: every inventory item is covered or excluded; control counts match.

--phase inventory : only inventory checks (control counts, module assignment).
--write           : (re)write coverage.md with the current numbers.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from _common import Contract, Report, base_args, covered_keys, finish, main_wrapper, module_entities

DB_KEY_PREFIX = {"tables": "table", "views": "view", "procedures": "procedure",
                 "triggers": "trigger", "sequences": "sequence"}


def _inventory_checks(c: Contract, report: Report, final: bool) -> None:
    items = c.inventory_items()
    if not items:
        report.fail("inventário vazio ou ausente")
        return
    by_kind = Counter(it.get("kind") for it in items)
    counts = {cc.get("kind"): cc for cc in (c.inventory or {}).get("control_counts", [])}
    for kind, n in sorted(by_kind.items()):
        cc = counts.get(kind)
        if cc is None:
            report.fail(f"kind '{kind}' ({n} itens) sem contagem de controle")
        elif cc.get("count") != n and not cc.get("explanation"):
            report.fail(f"kind '{kind}': extrator={n}, controle={cc.get('count')} "
                        f"({cc.get('command')}) sem explicação")
    for kind, cc in counts.items():
        if kind not in by_kind and cc.get("count", 0) > 0 and not cc.get("explanation"):
            report.fail(f"controle encontrou {cc['count']} '{kind}', extrator encontrou 0")
    if c.db:
        keys = {str(it.get("key", "")).upper() for it in items}
        for coll, prefix in DB_KEY_PREFIX.items():
            for obj in c.db.get(coll, []) or []:
                key = f"{prefix}:{obj.get('name', '')}"
                if key.upper() not in keys:
                    report.fail(f"db-metadata tem {coll[:-1]} {obj.get('name')!r} sem item "
                                f"'{key}' no inventário")
    known = set(c.manifest_modules()) | {"_unassigned"}
    for it in items:
        if it.get("module") not in known:
            report.fail(f"item {it.get('key')!r}: módulo '{it.get('module')}' não existe no manifest")
    unassigned = [it for it in items if it.get("module") == "_unassigned"]
    if unassigned:
        msg = f"{len(unassigned)} item(ns) em _unassigned"
        report.fail(msg) if final else report.warn(msg)


def _module_status_checks(c: Contract, name: str, report: Report) -> None:
    status = c.manifest_modules().get(name, {}).get("status")
    if status != "verified":
        return
    for coll, ent in module_entities(c.modules[name]):
        critic = ent.get("critic")
        if critic in ("pending", "rejected"):
            report.fail(f"{name} está 'verified' mas {ent.get('id')} tem critic={critic}")


def _coverage(c: Contract, only: str | None, report: Report) -> dict[str, tuple[int, int]]:
    items = c.inventory_items()
    inventory_keys = {it.get("key") for it in items}
    per_module_items: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        per_module_items[it.get("module")].append(it)

    stats: dict[str, tuple[int, int]] = {}
    modules = [only] if only else sorted(set(per_module_items) - {"_unassigned"})
    for name in modules:
        mod = c.modules.get(name)
        expected = per_module_items.get(name, [])
        if mod is None:
            if expected:
                report.fail(f"{name}: {len(expected)} item(ns) no inventário e nenhum module.json")
            stats[name] = (0, len(expected))
            continue
        cov = covered_keys(mod)
        for k in cov:
            if k not in inventory_keys:
                report.fail(f"{name}: cobre chave que não existe no inventário: {k!r}")
        missing = [it for it in expected if it.get("key") not in cov]
        for it in missing:
            report.fail(f"{name}: não coberto [{it.get('kind')}] {it.get('key')}")
        stats[name] = (len(expected) - len(missing), len(expected))
        _module_status_checks(c, name, report)
    return stats


def _write_md(root: Path, c: Contract, stats: dict[str, tuple[int, int]]) -> None:
    items = c.inventory_items()
    kinds = Counter(it.get("kind") for it in items)
    covered_all: set[str] = set()
    for mod in c.modules.values():
        covered_all |= set(covered_keys(mod))
    kind_cov = Counter(it.get("kind") for it in items if it.get("key") in covered_all)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Cobertura da extração", "",
             f"Gerado por `validate_coverage.py --write` em {now}. Não editar à mão.", "",
             "## Por superfície", "", "| kind | cobertos | total | % |", "|---|---:|---:|---:|"]
    for k, n in sorted(kinds.items()):
        lines.append(f"| {k} | {kind_cov[k]} | {n} | {100 * kind_cov[k] // max(n, 1)}% |")
    lines += ["", "## Por módulo", "", "| módulo | status | cobertos | total | % |",
              "|---|---|---:|---:|---:|"]
    mm = c.manifest_modules()
    for name, (done, total) in sorted(stats.items()):
        lines.append(f"| {name} | {mm.get(name, {}).get('status', '?')} | {done} | {total} | "
                     f"{100 * done // max(total, 1)}% |")
    (root / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(argv: list[str]) -> Report:
    p = base_args("Valida cobertura do inventário")
    p.add_argument("--phase", choices=["inventory", "full"], default="full")
    p.add_argument("--write", action="store_true", help="rewrite coverage.md")
    args = p.parse_args(argv)
    report = Report("coverage")
    root = Path(args.root)
    c = Contract(root, report)
    if c.manifest is None:
        report.fail("manifest.json ausente")
        return report
    _inventory_checks(c, report, final=args.phase == "full" and not args.module)
    if args.phase == "inventory":
        return report
    stats = _coverage(c, args.module, report)
    total_done = sum(d for d, _ in stats.values())
    total = sum(t for _, t in stats.values())
    report.warn(f"cobertura: {total_done}/{total} item(ns)")
    if args.write and not args.module:
        _write_md(root, c, stats)
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
