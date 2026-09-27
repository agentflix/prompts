#!/usr/bin/env python3
"""Fail when a rendered Markdown file is missing or differs from what render_md.py produces."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import render_md  # noqa: E402
from _common import Contract, Report, base_args, finish, main_wrapper  # noqa: E402


def run(argv: list[str]) -> Report:
    args = base_args("Confere se o Markdown gerado está em dia com o JSON").parse_args(argv)
    report = Report("rendered")
    c = Contract(Path(args.root), report)
    for path in render_md.stale(c, args.module):
        report.fail(f"{path.relative_to(c.root)} desatualizado ou ausente — rode render_md.py")
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
