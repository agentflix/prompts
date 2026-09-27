#!/usr/bin/env python3
"""Validate contract JSON files against schemas/ (minimal JSON Schema subset, stdlib only).

Supported keywords: type, required, properties, items, enum, pattern, minLength,
minItems, minimum, anyOf, $ref ("#name" -> schema $defs_local, then _defs.schema.json).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from _common import SCHEMAS_DIR, Contract, Report, base_args, finish, main_wrapper

TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float), "null": type(None),
}
SHARED = json.loads((SCHEMAS_DIR / "_defs.schema.json").read_text(encoding="utf-8"))


def _type_ok(value: Any, t: str) -> bool:
    if t in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, TYPES[t])


def check(value: Any, schema: dict, path: str, local: dict, errors: list[str]) -> None:
    if "$ref" in schema:
        name = schema["$ref"].lstrip("#")
        target = local.get(name) or SHARED.get(name)
        if target is None:
            errors.append(f"{path}: $ref desconhecido {schema['$ref']}")
            return
        check(value, target, path, local, errors)
        return
    t = schema.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_type_ok(value, x) for x in ts):
            errors.append(f"{path}: esperado {t}, veio {type(value).__name__}")
            return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: valor {value!r} fora de {schema['enum']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: texto curto demais (min {schema['minLength']})")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} não segue {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < mínimo {schema['minimum']}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: campo obrigatório ausente '{req}'")
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                check(value[k], sub, f"{path}.{k}", local, errors)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: mínimo de {schema['minItems']} item(ns)")
        if "items" in schema:
            for i, v in enumerate(value):
                check(v, schema["items"], f"{path}[{i}]", local, errors)
    if "anyOf" in schema:
        if not any(_try(value, s, local) for s in schema["anyOf"]):
            errors.append(f"{path}: não satisfaz nenhuma alternativa de anyOf")


def _try(value: Any, schema: dict, local: dict) -> bool:
    errs: list[str] = []
    check(value, schema, "", local, errs)
    return not errs


def validate_file(data: Any, schema_name: str, label: str, report: Report) -> None:
    schema = json.loads((SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"))
    errors: list[str] = []
    check(data, schema, label, schema.get("$defs_local", {}), errors)
    for e in errors:
        report.fail(e)


def run(argv: list[str]) -> Report:
    args = base_args("Valida os JSON do contrato contra schemas/").parse_args(argv)
    report = Report("schema")
    c = Contract(Path(args.root), report)
    if c.manifest is None:
        report.fail("manifest.json ausente")
        return report
    validate_file(c.manifest, "manifest.schema.json", "manifest", report)
    if c.inventory is not None:
        validate_file(c.inventory, "inventory.schema.json", "inventory", report)
    else:
        report.warn("00-inventory/inventory.json ainda não existe")
    if c.db is not None:
        validate_file(c.db, "db-metadata.schema.json", "db-metadata", report)
    if c.journeys is not None:
        validate_file(c.journeys, "journeys.schema.json", "journeys", report)
    for name in c.module_dirs(args.module):
        validate_file(c.modules[name], "module.schema.json", f"module[{name}]", report)
    if args.module and args.module not in c.modules:
        report.fail(f"02-modules/{args.module}/module.json não encontrado")
    return report


def main(argv: list[str]) -> int:
    return finish([run(argv)])


if __name__ == "__main__":
    main_wrapper(main)
