#!/usr/bin/env python3
"""Render the human-readable Markdown of the extraction from its JSON (single source of truth).

The author writes only module.json and journeys.json. This script produces:
  02-modules/<mod>/README.md, apis.md, rules.md, flows.md, data.md, screens/SCR-*.md
  03-journeys/JRN-NN-<slug>.md

Not rendered (written by hand): acceptance.feature, verification-log.md, 04-nfr/, 01-database/,
findings.md, unknowns.md, glossary.md, decisions-v2.md.

Usage:
  python3 render_md.py --root <reverse> [--module <name>]           # write files
  python3 render_md.py --root <reverse> [--module <name>] --check   # exit 1 if any file is stale
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "validate"))

from _common import Contract, Report  # noqa: E402

HEADER = "<!-- Gerado por render_md.py a partir de {src}. Não editar: altere o JSON e rode o script. -->\n\n"
CONF = {"verified": "✅ verified", "inferred": "🟡 inferred", "unknown": "❓ unknown"}
EARS_PT = {"ubiquitous": "Ubíquo", "event": "Evento", "unwanted": "Indesejado",
           "state": "Estado", "optional": "Opcional"}


def cell(value: object) -> str:
    """Make a value safe for a Markdown table cell."""
    if value is None or value == "" or value == []:
        return "—"
    if isinstance(value, bool):
        return "sim" if value else "não"
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    text = str(value).replace("\n", " ").replace("|", "\\|")
    return text


def src(s: dict) -> str:
    if s.get("file"):
        line = f":{s['line']}" if s.get("line") else ""
        end = f"-{s['end_line']}" if s.get("end_line") else ""
        return f"`{s['repo']}:{s['file']}{line}{end}`"
    if s.get("object"):
        line = f":{s['line']}" if s.get("line") else ""
        return f"`db:{s['object']}{line}`"
    return f"`runtime:{s.get('capture', '?')}`"


def srcs(sources: list[dict] | None) -> str:
    return ", ".join(src(s) for s in sources or []) or "—"


def table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(cell(v) for v in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]


# ---------------------------------------------------------------- module files

def callers(c: Contract) -> dict[str, list[str]]:
    """API id -> screens/journey steps that call it (computed, never written by hand)."""
    out: dict[str, list[str]] = {}
    for mod in c.modules.values():
        for scr in mod.get("screens", []) or []:
            for a in scr.get("actions", []) or []:
                if a.get("api"):
                    out.setdefault(a["api"], []).append(f'{scr["id"]} ("{a.get("label", "?")}")')
    for j in (c.journeys or {}).get("journeys", []):
        for s in j.get("steps", []):
            if s.get("api"):
                out.setdefault(s["api"], []).append(f'{j["id"]} passo {s.get("n")}')
    return out


def render_apis(mod: dict, call: dict[str, list[str]]) -> str:
    name = mod["module"]["name"]
    apis = mod.get("apis", []) or []
    parts = [f"# APIs — {name}\n\n",
             table(["ID", "Método", "Path", "Autenticação", "Resumo", "Confiança"],
                   [[a["id"], a.get("method"), f"`{a.get('path')}`", a.get("auth"), a.get("summary"),
                     CONF.get(a.get("confidence"), a.get("confidence"))] for a in apis])]
    for a in apis:
        parts.append(f"\n## {a['id']} — {a.get('summary')}\n")
        parts.append(f"`{a.get('method')} {a.get('path')}` · {CONF.get(a.get('confidence'), '?')} · "
                     f"Critic: {a.get('critic')}\n\n")
        parts.append(f"- **Fonte**: {srcs(a.get('sources'))}\n")
        parts.append(f"- **Autenticação**: {a.get('auth')}\n")
        if call.get(a["id"]):
            parts.append(f"- **Chamada por**: {', '.join(call[a['id']])}\n")
        if a.get("no_screen_reason"):
            parts.append(f"- **Sem tela**: {a['no_screen_reason']}\n")
        parts.append(f"- **Regras**: {', '.join(a.get('requirements', [])) or '—'}\n")
        if a.get("side_effects"):
            parts.append(f"- **Side-effects**: {'; '.join(a['side_effects'])}\n")
        params = a.get("params", []) or []
        parts.append("\n**Parâmetros**\n\n")
        parts.append(table(["Campo", "Onde", "Tipo", "Obrig.", "Validação", "Descrição"],
                           [[p.get("name"), p.get("in"), p.get("type"), p.get("required"),
                             p.get("validation"), p.get("description")] for p in params])
                     if params else "Sem parâmetros.\n")
        parts.append("\n**Respostas**\n\n")
        parts.append(table(["Status", "Quando", "Corpo / destino", "Mensagem", "Regras"],
                           [[r.get("status"), r.get("when"), r.get("body"), r.get("message"),
                             r.get("requirements")] for r in a.get("responses", []) or []]))
    return "".join(parts)


def render_rules(mod: dict) -> str:
    reqs = mod.get("requirements", []) or []
    parts = [f"# Regras — {mod['module']['name']}\n\n",
             table(["ID", "Tipo", "Requisito", "Fonte", "Confiança", "Critic", "Findings"],
                   [[r["id"], EARS_PT.get(r.get("ears_type"), r.get("ears_type")), r.get("statement"),
                     srcs(r.get("sources")), CONF.get(r.get("confidence"), "?"), r.get("critic"),
                     r.get("findings")] for r in reqs])]
    with_values = [r for r in reqs if r.get("values")]
    if with_values:
        parts.append("\n## Valores concretos\n\n")
        rows = []
        for r in with_values:
            for k, v in r["values"].items():
                rows.append([r["id"], k, json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v])
        parts.append(table(["Requisito", "Chave", "Valor"], rows))
    return "".join(parts)


def render_flows(mod: dict) -> str:
    parts = [f"# Fluxos — {mod['module']['name']}\n"]
    for f in mod.get("flows", []) or []:
        parts.append(f"\n## {f['id']} — {f.get('title')}\n\n")
        if f.get("trigger"):
            parts.append(f"**Gatilho**: {f['trigger']}\n")
        parts.append(f"**APIs**: {', '.join(f.get('apis', [])) or '—'} · "
                     f"**Regras**: {', '.join(f.get('requirements', [])) or '—'}\n")
        if f.get("diagram"):
            parts.append(f"\n~~~mermaid\n{f['diagram'].strip()}\n~~~\n")
        if f.get("edge_cases"):
            parts.append("\n**Falhas e bordas**\n\n" + "".join(f"- {e}\n" for e in f["edge_cases"]))
    return "".join(parts)


def render_data(mod: dict) -> str:
    return (f"# Dados — {mod['module']['name']}\n\n"
            + table(["Tabela", "Acesso", "Filtro de tenant", "Fonte", "Observação"],
                    [[d.get("table"), d.get("access"), d.get("tenant_filtered"), srcs(d.get("sources")),
                      d.get("note")] for d in mod.get("data", []) or []]))


def render_screen(scr: dict) -> str:
    parts = [f"# {scr['id']} — {scr.get('title')}\n\n",
             f"- **Rota**: `{scr.get('route')}`" + (f" · **Menu**: {scr['menu']}" if scr.get("menu") else "") + "\n",
             f"- **Objetivo**: {scr.get('purpose')}\n",
             f"- **Perfis**: {cell(scr.get('profiles'))}\n",
             f"- **Fonte**: {srcs(scr.get('sources'))}\n",
             f"- **Confiança**: {CONF.get(scr.get('confidence'), '?')} · Critic: {scr.get('critic', '—')}\n"]
    if scr.get("screenshot"):
        parts.append(f"\n![]({scr['screenshot']})\n")
    fields = scr.get("fields", []) or []
    parts.append("\n## Campos\n\n")
    parts.append(table(["Label", "Nome", "Tipo", "Obrig.", "Máscara", "Padrão", "Opções", "Validação no front",
                        "Campo na API"],
                       [[f.get("label"), f.get("name"), f.get("type"), f.get("required"), f.get("mask"),
                         f.get("default"), f.get("options"), f.get("validation"), f.get("api_field")]
                        for f in fields]) if fields else "Sem campos de entrada.\n")
    parts.append("\n## Ações\n\n")
    parts.append(table(["Ação", "Pré-condição", "Chama", "Resultado", "Mensagens", "Vai para"],
                       [[a.get("label"), a.get("precondition"), a.get("api") or a.get("external_call"),
                         a.get("result"), a.get("messages"), a.get("navigates_to")]
                        for a in scr.get("actions", []) or []]))
    if scr.get("notes"):
        parts.append("\n## Observações\n\n" + "".join(f"- {n}\n" for n in scr["notes"]))
    return "".join(parts)


def render_readme(mod: dict) -> str:
    meta = mod["module"]
    counts = [["APIs", len(mod.get("apis", []) or []), "apis.md"],
              ["Regras", len(mod.get("requirements", []) or []), "rules.md"],
              ["Fluxos", len(mod.get("flows", []) or []), "flows.md"],
              ["Telas", len(mod.get("screens", []) or []), "screens/"],
              ["Tabelas", len(mod.get("data", []) or []), "data.md"],
              ["Exclusões", len(mod.get("exclusions", []) or []), "abaixo"]]
    parts = [f"# Módulo {meta['name']} ({meta['code']})\n\n"]
    if meta.get("summary"):
        parts.append(f"{meta['summary']}\n\n")
    parts.append(table(["Tipo", "Quantidade", "Arquivo"], counts))
    if meta.get("depends_on") or meta.get("used_by"):
        parts.append("\n## Dependências\n\n")
        parts.append(f"- **Usa**: {cell(meta.get('depends_on'))}\n- **É usado por**: {cell(meta.get('used_by'))}\n")
    exc = mod.get("exclusions", []) or []
    if exc:
        parts.append("\n## Exclusões\n\n")
        parts.append(table(["Item do inventário", "Status", "Motivo", "Evidência"],
                           [[f"`{e.get('inventory_key')}`", e.get("status"), e.get("reason"),
                             "; ".join(f"`{x}`" for x in e.get("evidence", []))] for e in exc]))
    if meta.get("attention"):
        parts.append("\n## Pontos de atenção\n\n" + "".join(f"- {a}\n" for a in meta["attention"]))
    return "".join(parts)


def render_journey(j: dict) -> str:
    parts = [f"# {j['id']} — {j.get('title')}\n\n",
             f"**Ator**: {j.get('actor')} · **Módulos**: {cell(j.get('modules'))}\n\n",
             f"**Pré-condições**: {j.get('preconditions', '—')}\n\n",
             table(["#", "Tela", "O que o usuário faz", "API", "Regras", "Resultado"],
                   [[s.get("n"), s.get("screen"), s.get("action"), s.get("api"), s.get("requirements"),
                     s.get("result")] for s in j.get("steps", [])])]
    if j.get("alternatives"):
        parts.append("\n**Caminhos alternativos**\n\n" + "".join(f"- {a}\n" for a in j["alternatives"]))
    if j.get("parity_cases"):
        parts.append(f"\n**Casos de paridade**: {', '.join(j['parity_cases'])}\n")
    return "".join(parts)


# ---------------------------------------------------------------- driver

def planned_files(c: Contract, only: str | None) -> dict[Path, str]:
    root = c.root
    call = callers(c)
    out: dict[Path, str] = {}
    for name in c.module_dirs(only):
        mod = c.modules[name]
        d = root / "02-modules" / name
        h = HEADER.format(src="module.json")
        out[d / "README.md"] = h + render_readme(mod)
        out[d / "apis.md"] = h + render_apis(mod, call)
        out[d / "rules.md"] = h + render_rules(mod)
        out[d / "flows.md"] = h + render_flows(mod)
        out[d / "data.md"] = h + render_data(mod)
        for scr in mod.get("screens", []) or []:
            out[d / "screens" / f"{scr['id']}.md"] = h + render_screen(scr)
    if not only:
        jdir = root / "03-journeys"
        for j in (c.journeys or {}).get("journeys", []):
            slug = j.get("slug")
            if not slug:
                existing = sorted(jdir.glob(f"{j['id']}-*.md"))
                slug = existing[0].stem[len(j["id"]) + 1:] if existing else slugify(j.get("title", ""))
            out[jdir / f"{j['id']}-{slug}.md"] = HEADER.format(src="journeys.json") + render_journey(j)
    return out


def stale(c: Contract, only: str | None) -> list[Path]:
    return [p for p, text in planned_files(c, only).items()
            if not p.exists() or p.read_text(encoding="utf-8") != text]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--module")
    ap.add_argument("--check", action="store_true", help="only report stale files")
    args = ap.parse_args(argv)
    report = Report("render")
    c = Contract(Path(args.root), report)
    if report.failures:
        report.print()
        return 1
    if args.check:
        files = stale(c, args.module)
        for p in files:
            print(f"desatualizado: {p.relative_to(c.root)}")
        return 1 if files else 0
    for path, text in planned_files(c, args.module).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"gerado: {path.relative_to(c.root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
