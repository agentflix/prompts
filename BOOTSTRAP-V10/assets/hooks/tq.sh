#!/usr/bin/env bash
# Fila de testes pesados: uma suíte por repositório por vez, em ordem de chegada.
#   .claude/hooks/tq.sh '<comando>'     espera a vez e roda
#   .claude/hooks/tq.sh --status        quem roda e quem espera
#   .claude/hooks/tq.sh --fase          fim de fase: só as partes do GATE_PARTS tocadas pelo diff
# Detalhes em tq.py.
# --fase lê GATE_FULL e GATE_PARTS do gates.conf.
if [ "${1:-}" = "--fase" ] && [ -f "$(dirname "$0")/gates.conf" ]; then
  set -a; . "$(dirname "$0")/gates.conf"; set +a
fi
exec python3 -I "$(dirname "$0")/tq.py" "$@"
