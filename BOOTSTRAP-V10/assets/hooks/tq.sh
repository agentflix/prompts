#!/usr/bin/env bash
# Fila de testes pesados: uma suíte por repositório por vez, em ordem de chegada.
#   .claude/hooks/tq.sh '<comando>'     espera a vez e roda
#   .claude/hooks/tq.sh --status        quem roda e quem espera
# Detalhes em tq.py.
exec python3 -I "$(dirname "$0")/tq.py" "$@"
