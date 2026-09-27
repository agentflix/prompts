#!/usr/bin/env python3
"""Self-test for the validators: builds a tiny fixture, expects green, then breaks it.

Run: python3 scripts/validate/selftest.py
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_all  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def build(tmp: Path) -> tuple[Path, dict]:
    # The legacy repo is a subdirectory of a git repository (monorepo case).
    mono = tmp / "mono"
    repo = mono / "legacy"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "Orders.php").write_text("\n".join(f"line {i}" for i in range(1, 51)) + "\n")
    git(mono, "init", "-q")
    git(mono, "-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
    git(mono, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init")
    sha = git(mono, "rev-parse", "HEAD")

    root = tmp / "reverse"
    src = {"repo": "backend", "file": "src/Orders.php", "line": 10}
    files = {
        "manifest.json": {
            "contract_version": "1.0.0", "system": "demo", "language": "pt-BR", "has_frontend": True,
            "repos": [{"name": "backend", "path": str(repo), "commit": sha}],
            "modules": [{"code": "ORD", "name": "orders", "status": "verified"}],
            "phases": {"0": {"status": "done"}},
        },
        "00-inventory/inventory.json": {
            "contract_version": "1.0.0", "generated_at": "2026-09-27", "generator": "test",
            "items": [
                {"key": "POST /orders", "kind": "http_endpoint", "module": "orders", "source": src},
                {"key": "screen:/orders/new", "kind": "screen", "module": "orders", "source": src},
                {"key": "table:ORDERS", "kind": "db_table", "module": "orders", "source": src},
            ],
            "control_counts": [
                {"kind": "http_endpoint", "command": "grep -c route", "count": 1},
                {"kind": "screen", "command": "grep -c page", "count": 1},
                {"kind": "db_table", "command": "select count", "count": 1},
            ],
        },
        "02-modules/orders/module.json": {
            "contract_version": "1.0.0", "module": {"code": "ORD", "name": "orders"},
            "apis": [{"id": "API-ORD-001", "inventory_key": "POST /orders", "method": "POST",
                      "path": "/orders", "auth": "logged user", "summary": "create order",
                      "sources": [src], "requirements": ["REQ-ORD-W001"],
                      "confidence": "verified", "critic": "approved"}],
            "requirements": [{"id": "REQ-ORD-W001", "ears_type": "unwanted",
                              "statement": "SE total <= 0, ENTÃO rejeitar com 422.",
                              "sources": [src], "confidence": "verified", "critic": "approved"}],
            "flows": [],
            "screens": [{"id": "SCR-ORD-001", "inventory_key": "screen:/orders/new",
                         "route": "/orders/new", "title": "Nova ordem", "sources": [src],
                         "fields": [{"label": "Total", "type": "number", "required": True}],
                         "actions": [{"label": "Salvar", "api": "API-ORD-001"}]}],
            "data": [{"inventory_key": "table:ORDERS", "table": "ORDERS", "access": "RW",
                      "tenant_filtered": True, "sources": [src]}],
            "exclusions": [],
        },
    }
    for rel, data in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    (root / "02-modules/orders/apis.md").write_text("## API-ORD-001\n")
    (root / "02-modules/orders/rules.md").write_text("## REQ-ORD-W001\n")
    (root / "02-modules/orders/screens").mkdir()
    (root / "02-modules/orders/screens/SCR-ORD-001.md").write_text("# SCR-ORD-001\n")
    (root / "05-parity/cases").mkdir(parents=True)
    files["05-parity/cases/PAR-ORD-001.json"] = {
        "id": "PAR-ORD-001", "api": "API-ORD-001", "requirements": ["REQ-ORD-W001"]}
    (root / "05-parity/cases/PAR-ORD-001.json").write_text(
        json.dumps(files["05-parity/cases/PAR-ORD-001.json"]))
    return root, files


def expect(root: Path, want_ok: bool, label: str) -> bool:
    code = run_all.main(["--root", str(root)])
    ok = (code == 0) == want_ok
    print(f"\n>>> {'PASS' if ok else 'FAIL'}: {label}\n")
    return ok


def mutate(root: Path, rel: str, fn) -> None:
    p = root / rel
    data = json.loads(p.read_text())
    fn(data)
    p.write_text(json.dumps(data))


def main() -> int:
    results = []
    with tempfile.TemporaryDirectory() as t:
        root, files = build(Path(t))
        results.append(expect(root, True, "fixture válida → gate verde"))

        cases = [
            ("item do inventário sem cobertura",
             "00-inventory/inventory.json",
             lambda d: d["items"].append({"key": "GET /x", "kind": "http_endpoint", "module": "orders",
                                          "source": d["items"][0]["source"]})),
            ("linha além do fim do arquivo",
             "02-modules/orders/module.json",
             lambda d: d["requirements"][0]["sources"][0].update(line=999)),
            ("requisito sem fonte",
             "02-modules/orders/module.json",
             lambda d: d["requirements"][0].update(sources=[])),
            ("referência para ID inexistente",
             "02-modules/orders/module.json",
             lambda d: d["apis"][0].update(requirements=["REQ-ORD-W009"])),
            ("letra EARS não bate com o tipo",
             "02-modules/orders/module.json",
             lambda d: d["requirements"][0].update(ears_type="event")),
            ("API sem tela e sem no_screen_reason",
             "02-modules/orders/module.json",
             lambda d: d["screens"][0].update(actions=[{"label": "Voltar", "navigates_to": "/"}])),
            ("nome do módulo diverge do diretório",
             "02-modules/orders/module.json",
             lambda d: d["module"].update(name="pedidos")),
            ("código do módulo diverge do manifest",
             "manifest.json",
             lambda d: d["modules"][0].update(code="PED")),
            ("caso de paridade aponta para API inexistente",
             "05-parity/cases/PAR-ORD-001.json",
             lambda d: d.update(api="API-ORD-099")),
            ("módulo verified com critic pending",
             "02-modules/orders/module.json",
             lambda d: d["apis"][0].update(critic="pending")),
        ]
        for label, rel, fn in cases:
            original = json.dumps(files[rel])
            mutate(root, rel, fn)
            results.append(expect(root, False, label))
            (root / rel).write_text(original)

        (root / "02-modules/orders/rules.md").write_text("nada\n")
        results.append(expect(root, False, "ID no JSON ausente do Markdown"))
    print(f"selftest: {sum(results)}/{len(results)} cenários corretos")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
