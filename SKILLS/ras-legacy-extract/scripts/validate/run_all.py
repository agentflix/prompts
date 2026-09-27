#!/usr/bin/env python3
"""Run every validator. Exit code 0 only when all pass (the extraction gate).

Usage:
  python3 run_all.py --root <project>/docs/reverse [--module <name>] [--write]
"""
from __future__ import annotations

import sys

import validate_coverage
import validate_crosslinks
import validate_ids
import validate_refs
import validate_schema
from _common import finish, main_wrapper


def main(argv: list[str]) -> int:
    write = "--write" in argv
    base = [a for a in argv if a != "--write"]
    reports = [
        validate_schema.run(base),
        validate_ids.run(base),
        validate_refs.run(base),
        validate_coverage.run(base + (["--write"] if write else [])),
        validate_crosslinks.run(base),
    ]
    code = finish(reports)
    print("\nGATE:", "VERDE" if code == 0 else "VERMELHO")
    return code


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    main_wrapper(main)
