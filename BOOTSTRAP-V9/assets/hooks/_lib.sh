#!/usr/bin/env bash
# Funções comuns dos hooks. Funciona com Claude Code (Edit/Write: tool_input.file_path)
# e Codex (apply_patch: caminhos dentro de tool_input.command).

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
HOOKS_DIR="$ROOT/.claude/hooks"
# shellcheck disable=SC1091
[ -f "$HOOKS_DIR/gates.conf" ] && . "$HOOKS_DIR/gates.conf"

INPUT="$(cat)"

# -I isola o Python: sem isso, um json.py na raiz do projeto seria importado no lugar do módulo.
py() { python3 -I "$@"; }
py_ok() { command -v python3 >/dev/null 2>&1 && python3 -I -c 'import json, os, re' >/dev/null 2>&1; }

json_get() {
  # json_get <campo.aninhado>  →  valor (string) ou vazio
  py -c '
import json, sys
try:
    d = json.loads(sys.stdin.read() or "{}")
except Exception:
    sys.exit(0)
for k in sys.argv[1].split("."):
    d = d.get(k) if isinstance(d, dict) else None
if d is None:
    sys.exit(0)
print(d if isinstance(d, str) else json.dumps(d))
' "$1" <<<"$INPUT" 2>/dev/null
}

edited_paths() {
  # Um caminho por linha, relativo à raiz. Para cada arquivo editado imprime a forma
  # normalizada sem seguir symlink e, se diferente, a forma com symlink resolvido,
  # para que um symlink não esconda o alvo protegido nem o nome protegido.
  py -c '
import json, os, re, sys
root = sys.argv[1]
try:
    d = json.loads(sys.stdin.read() or "{}")
except Exception:
    sys.exit(0)
base = d.get("cwd") if isinstance(d.get("cwd"), str) else root
ti = d.get("tool_input") or {}
paths = []
for key in ("file_path", "notebook_path", "path"):
    if isinstance(ti.get(key), str):
        paths.append(ti[key])
cmd = ti.get("command") if isinstance(ti.get("command"), str) else ""
paths += re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", cmd, re.M)
paths += re.findall(r"^\*\*\* Move to: (.+)$", cmd, re.M)
seen = set()
for p in paths:
    p = p.strip()
    if not os.path.isabs(p):
        p = os.path.join(base, p)
    for q in (os.path.relpath(os.path.normpath(p), os.path.normpath(root)),
              os.path.relpath(os.path.realpath(p), os.path.realpath(root))):
        if q not in seen:
            seen.add(q)
            print(q)
' "$ROOT" <<<"$INPUT" 2>/dev/null
}

matches_any() {
  # matches_any <caminho> <padrões separados por espaço>
  # Casa o caminho inteiro, o nome do arquivo e o padrão em qualquer subpasta (*/padrão).
  # Sem diferença de maiúsculas: no macOS .ENV e .env são o mesmo arquivo.
  local path="$1" pat base rc=1 had_f=0 had_nc=0
  base="$(basename "$path")"
  case $- in *f*) had_f=1 ;; esac
  shopt -q nocasematch && had_nc=1
  set -f
  shopt -s nocasematch
  for pat in $2; do
    # shellcheck disable=SC2254
    case "$path" in $pat|*/$pat) rc=0; break ;; esac
    case "$base" in $pat) rc=0; break ;; esac
  done
  [ $had_f -eq 1 ] || set +f
  [ $had_nc -eq 1 ] || shopt -u nocasematch
  return $rc
}

is_placeholder() { case "$1" in ""|"<"*) return 0 ;; esac; return 1; }
