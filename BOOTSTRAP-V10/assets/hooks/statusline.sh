#!/usr/bin/env bash
# Statusline do Claude Code. Desenhada pelo harness: não gasta token do modelo.
# Linha 1: pasta | branch*arquivos pendentes | modelo | janela de contexto | linhas +/- da sessão.
#   reelr/api  |  main*5  |  Opus  |  ████░░░░░░ 35% (348k/1M)  |  +1201 -71
# Linha 2: tarefa atual · subagente ativo · último gate · fila de testes · cache.
#   ▶ 3/7 Validando CPF no cadastro · ⇢ executor · gate ✓ 12s · fila 2 · cache 94%
# A tarefa vem do hook de status (lista de tarefas nativa), não da memória do modelo.
# Cada linha cabe em $COLUMNS; o texto da tarefa tem teto em STATUS_TASK_MAX (gates.conf).
d="$(dirname "$0")"
[ -f "$d/gates.conf" ] && { set -a; . "$d/gates.conf" 2>/dev/null; set +a; }
exec python3 -I "$d/statusline.py"
