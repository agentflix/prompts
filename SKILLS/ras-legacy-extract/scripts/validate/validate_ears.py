#!/usr/bin/env python3
"""Lint EARS requirement statements in module.json files.

Checks, per requirement:
- has a modal keyword in uppercase (DEVE / DEVERÁ / SHALL / MUST);
- has the trigger keyword required by its ears_type
  (event: QUANDO/WHEN, unwanted: SE..ENTÃO / IF..THEN, state: ENQUANTO/WHILE,
  optional: ONDE/WHERE);
- has no vague term (pt-BR and English list below).

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
            for problem in lint(str(req.get("statement", "")), str(req.get("ears_type", "")), waived):
                report.fail(f"{req.get('id')}: {problem}")
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
