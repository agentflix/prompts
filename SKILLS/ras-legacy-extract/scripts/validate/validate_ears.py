#!/usr/bin/env python3
"""Lint EARS requirement statements in module.json files.

Checks, per requirement:
- has a modal keyword in uppercase (DEVE / DEVERÁ / SHALL / MUST);
- has the trigger keyword required by its ears_type
  (event: QUANDO/WHEN, unwanted: SE..ENTÃO / IF..THEN, state: ENQUANTO/WHILE,
  optional: ONDE/WHERE);
- has no vague term (pt-BR and English list below).

Warnings (do not fail the gate): more than one modal keyword, statement longer than
MAX_LEN characters, an enumeration of numbers inside the statement, or short free-text
fields (API summary, screen purpose/menu, action result/precondition) above TEXT_LIMITS.

Quoted text ("..." and “...”) is ignored, so literal error messages are not linted.
A term may be waived per requirement with `lint_waivers: [{"term": ..., "reason": ...}]`.
"""
from __future__ import annotations

import re
from pathlib import Path

from _common import Contract, Report, base_args, finish, main_wrapper

MODAL = re.compile(r"\b(DEVE|DEVERÁ|SHALL|MUST)\b")
TRIGGERS = {
    "event": [("QUANDO/WHEN", re.compile(r"\b(QUANDO|WHEN)\b"))],
    "unwanted": [("SE/IF", re.compile(r"\b(SE|IF)\b")),
                 ("ENTÃO/THEN", re.compile(r"\b(ENTÃO|ENTAO|THEN)\b"))],
    "state": [("ENQUANTO/WHILE", re.compile(r"\b(ENQUANTO|WHILE)\b"))],
    "optional": [("ONDE/WHERE", re.compile(r"\b(ONDE|WHERE)\b"))],
    "ubiquitous": [],
}
VAGUE_TERMS = [
    # pt-BR
    r"adequad[oa]s?", r"adequadamente", r"corretamente", r"apropriad[oa]s?", r"apropriadamente",
    r"devidamente", r"trata(r|do|da|dos|das)?", r"gerencia(r)?", r"v[aá]ri[oa]s",
    r"quando necess[aá]rio", r"se necess[aá]rio", r"conforme necess[aá]rio", r"razo[aá]vel",
    r"rapidamente", r"eficientemente", r"amig[aá]vel", r"etc\.?", r"e/ou",
    # English
    r"properly", r"appropriate(ly)?", r"correctly", r"handles?", r"handled", r"manages?",
    r"managed", r"several", r"various", r"as needed", r"if needed", r"reasonable",
    r"quickly", r"efficiently", r"user-friendly", r"and/or",
]
VAGUE = [(t, re.compile(rf"(?<!\w){t}(?!\w)", re.IGNORECASE)) for t in VAGUE_TERMS]
QUOTED = re.compile(r"\"[^\"]*\"|“[^”]*”")


MODAL_ALL = re.compile(r"\b(DEVE|DEVERÁ|SHALL|MUST)\b")
NUMBER = re.compile(r"\b\d+\b")
MAX_LEN = 300


def size_warnings(statement: str) -> list[str]:
    """Signals of a compound requirement or an enumeration inside the statement."""
    text = QUOTED.sub(" ", statement)
    out: list[str] = []
    if len(MODAL_ALL.findall(text)) > 1:
        out.append("mais de um DEVE/SHALL: provavelmente são requisitos separados")
    if len(statement) > MAX_LEN:
        out.append(f"{len(statement)} caracteres (> {MAX_LEN}): avalie dividir")
    if len(NUMBER.findall(text)) >= 6:
        out.append("muitos números no enunciado: mova a enumeração para `values` e cite-a")
    return out


def lint(statement: str, ears_type: str, waived: set[str]) -> list[str]:
    text = QUOTED.sub(" ", statement)
    problems: list[str] = []
    if not MODAL.search(text):
        problems.append("sem palavra modal em maiúsculas (DEVE / SHALL)")
    for label, pattern in TRIGGERS.get(ears_type, []):
        if not pattern.search(text):
            problems.append(f"tipo '{ears_type}' exige a palavra {label} em maiúsculas")
    for _term, pattern in VAGUE:
        m = pattern.search(text)
        if m and m.group(0).lower() not in waived:
            problems.append(f"termo vago '{m.group(0)}'")
    return problems


# Short free-text fields: longer text usually means two facts in one field.
TEXT_LIMITS = {("apis", "summary"): 100, ("screens", "purpose"): 200, ("screens", "menu"): 120,
               ("actions", "result"): 200, ("actions", "precondition"): 120}


def brevity_warnings(mod: dict) -> list[str]:
    out: list[str] = []

    def check(owner: str, kind: str, field: str, value: object) -> None:
        limit = TEXT_LIMITS[(kind, field)]
        if isinstance(value, str) and len(value) > limit:
            out.append(f"{owner}.{field}: {len(value)} caracteres (> {limit}); seja direto e mova "
                       "detalhes para notes/regras")

    for api in mod.get("apis", []) or []:
        check(api.get("id", "?"), "apis", "summary", api.get("summary"))
    for scr in mod.get("screens", []) or []:
        check(scr.get("id", "?"), "screens", "purpose", scr.get("purpose"))
        check(scr.get("id", "?"), "screens", "menu", scr.get("menu"))
        for a in scr.get("actions", []) or []:
            owner = f"{scr.get('id')}[{a.get('label')}]"
            check(owner, "actions", "result", a.get("result"))
            check(owner, "actions", "precondition", a.get("precondition"))
    return out


def run(argv: list[str]) -> Report:
    args = base_args("Lint dos enunciados EARS").parse_args(argv)
    report = Report("ears")
    c = Contract(Path(args.root), report)
    for name in c.module_dirs(args.module):
        for req in c.modules[name].get("requirements", []) or []:
            waivers = req.get("lint_waivers", []) or []
            for w in waivers:
                if len(str(w.get("reason", ""))) < 10:
                    report.fail(f"{req.get('id')}: waiver de '{w.get('term')}' sem motivo")
            waived = {str(w.get("term", "")).lower() for w in waivers}
            statement = str(req.get("statement", ""))
            for problem in lint(statement, str(req.get("ears_type", "")), waived):
                report.fail(f"{req.get('id')}: {problem}")
            for hint in size_warnings(statement):
                report.warn(f"{req.get('id')}: {hint}")
        for hint in brevity_warnings(c.modules[name]):
            report.warn(hint)
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
