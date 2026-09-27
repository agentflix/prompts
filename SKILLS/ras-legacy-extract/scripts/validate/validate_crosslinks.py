#!/usr/bin/env python3
"""Validate screen <-> API <-> requirement links in both directions.

Rules:
- every API is called by some screen action or journey step, or has `no_screen_reason`
  (skipped when manifest.has_frontend is false);
- every screen action points to an API (`api`) or declares an `external_call`;
- every API cites at least one requirement;
- requirements not referenced by any API/flow/screen are reported as warnings.
"""
from __future__ import annotations

from pathlib import Path

from _common import Contract, Report, base_args, finish, main_wrapper


def run(argv: list[str]) -> Report:
    args = base_args("Valida ligações tela ↔ API ↔ requisito").parse_args(argv)
    report = Report("crosslinks")
    c = Contract(Path(args.root), report)
    if c.manifest is None:
        report.fail("manifest.json ausente")
        return report
    has_frontend = c.manifest.get("has_frontend", True)

    called: set[str] = set()
    referenced_reqs: set[str] = set()
    for mod in c.modules.values():
        for scr in mod.get("screens", []) or []:
            for a in scr.get("actions", []) or []:
                if a.get("api"):
                    called.add(a["api"])
        for api in mod.get("apis", []) or []:
            referenced_reqs |= set(api.get("requirements", []) or [])
        for flw in mod.get("flows", []) or []:
            referenced_reqs |= set(flw.get("requirements", []) or [])
    for j in (c.journeys or {}).get("journeys", []):
        for s in j.get("steps", []):
            if s.get("api"):
                called.add(s["api"])
            referenced_reqs |= set(s.get("requirements", []) or [])

    for name in c.module_dirs(args.module):
        mod = c.modules[name]
        for api in mod.get("apis", []) or []:
            aid = api.get("id")
            if not api.get("requirements"):
                report.fail(f"{aid}: API sem nenhum requisito associado")
            if has_frontend and aid not in called and not api.get("no_screen_reason"):
                report.fail(f"{aid}: nenhuma tela/jornada chama esta API e não há no_screen_reason")
        for scr in mod.get("screens", []) or []:
            for a in scr.get("actions", []) or []:
                if not a.get("api") and not a.get("external_call") and not a.get("navigates_to"):
                    report.fail(f"{scr.get('id')}: ação '{a.get('label')}' sem api/external_call/navigates_to")
        for req in mod.get("requirements", []) or []:
            if req.get("id") not in referenced_reqs:
                report.warn(f"{req.get('id')}: requisito não ligado a API, fluxo ou jornada")
    if not has_frontend:
        report.warn("manifest.has_frontend=false: checagem API→tela desativada")
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
