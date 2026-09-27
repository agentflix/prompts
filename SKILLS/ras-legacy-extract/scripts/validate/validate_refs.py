#!/usr/bin/env python3
"""Validate every source reference (file:line) against the pinned commit of its repo."""
from __future__ import annotations

import subprocess
from pathlib import Path

from _common import Contract, Report, base_args, finish, iter_sources, main_wrapper

SPECIAL_REPOS = {"db", "runtime"}


class RepoReader:
    """Reads file line counts at the pinned commit (git) or from disk (fallback)."""

    def __init__(self, name: str, path: Path, commit: str, report: Report) -> None:
        self.name, self.path, self.commit = name, path, commit
        self.cache: dict[str, int | None] = {}
        self.git = (path / ".git").exists() or self._is_git()
        if not path.exists():
            report.fail(f"repo '{name}': caminho não existe ({path})")
        elif not self.git:
            report.warn(f"repo '{name}': não é git, conferindo no disco (sem commit fixado)")
        else:
            head = self._run(["rev-parse", "HEAD"])
            if head and not head.startswith(commit[:7]):
                report.warn(f"repo '{name}': HEAD {head[:10]} difere do commit fixado {commit[:10]}; "
                            "conferindo no commit fixado")

    def _is_git(self) -> bool:
        return self._run(["rev-parse", "--is-inside-work-tree"]) == "true"

    def _run(self, cmd: list[str]) -> str | None:
        try:
            out = subprocess.run(["git", "-C", str(self.path), *cmd], capture_output=True,
                                 text=True, check=True)
            return out.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def line_count(self, file: str) -> int | None:
        if file not in self.cache:
            if self.git:
                try:
                    out = subprocess.run(["git", "-C", str(self.path), "show", f"{self.commit}:{file}"],
                                         capture_output=True, check=True)
                    self.cache[file] = out.stdout.count(b"\n") + (0 if out.stdout.endswith(b"\n") else 1)
                except subprocess.CalledProcessError:
                    self.cache[file] = None
            else:
                p = self.path / file
                self.cache[file] = (len(p.read_bytes().splitlines()) if p.is_file() else None)
        return self.cache[file]


def run(argv: list[str]) -> Report:
    args = base_args("Valida file:line contra o commit fixado").parse_args(argv)
    report = Report("refs")
    root = Path(args.root)
    c = Contract(root, report)
    if c.manifest is None:
        report.fail("manifest.json ausente")
        return report
    readers = {r["name"]: RepoReader(r["name"], (root / r["path"]).resolve()
                                     if not Path(r["path"]).is_absolute() else Path(r["path"]),
                                     r["commit"], report)
               for r in c.manifest.get("repos", [])}
    db_objects: set[str] = set()
    if c.db:
        for coll in ("tables", "views", "procedures", "triggers", "sequences"):
            db_objects |= {str(o.get("name", "")).upper() for o in c.db.get(coll, [])}

    targets: list[tuple[str, object]] = []
    if not args.module:
        targets.append(("inventory", c.inventory or {}))
    targets += [(f"module[{n}]", c.modules[n]) for n in c.module_dirs(args.module)]

    checked = 0
    for label, obj in targets:
        for s in iter_sources(obj):
            repo = s.get("repo")
            checked += 1
            if repo == "runtime":
                cap = s.get("capture")
                if cap and not (root / cap).exists():
                    report.fail(f"{label}: captura inexistente {cap}")
                continue
            if repo == "db":
                name = str(s.get("object", "")).split()[-1].upper() if s.get("object") else ""
                if db_objects and name and name not in db_objects:
                    report.fail(f"{label}: objeto de banco não está no db-metadata: {s.get('object')}")
                continue
            reader = readers.get(repo)
            if reader is None:
                report.fail(f"{label}: repo '{repo}' não registrado no manifest")
                continue
            file, line = s.get("file"), s.get("line")
            if not file:
                continue
            n = reader.line_count(file)
            if n is None:
                report.fail(f"{label}: arquivo não existe no commit fixado: {repo}:{file}")
            elif line and line > n:
                report.fail(f"{label}: {repo}:{file}:{line} além do fim do arquivo ({n} linhas)")
            elif s.get("end_line") and s["end_line"] > n:
                report.fail(f"{label}: {repo}:{file}:{s['end_line']} (end_line) além do fim ({n} linhas)")
    if checked == 0:
        report.warn("nenhuma referência encontrada para conferir")
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
