#!/usr/bin/env bash
# Entrada dos hooks de estado do V10 (status, ritmo, escopo, plano). O corpo está em prevec.py.
# Exporta o gates.conf para o Python ler ESCOPO, RITMO_* e afins. Nunca bloqueia por erro próprio.
d="$(dirname "$0")"
if [ -f "$d/gates.conf" ]; then set -a; . "$d/gates.conf" 2>/dev/null; set +a; fi
command -v python3 >/dev/null 2>&1 || { cat >/dev/null; exit 0; }
exec python3 -I "$d/prevec.py" "$@"
