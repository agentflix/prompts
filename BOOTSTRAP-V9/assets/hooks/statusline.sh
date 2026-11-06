#!/usr/bin/env bash
# Statusline do Claude Code. Desenhada pelo harness: não gasta token do modelo.
# Linha 1 (uma cor): branch*arquivos pendentes | modelo | janela de contexto | linhas +/- da sessão.
#   main*5  |  Opus  |  ████░░░░░░ 35% (348k/1M)  |  +1201 -71
# Linha 2: tarefa atual da feature longa · último gate · cache (só o que existir).
#   ▶ 7/30 valida CPF no cadastro · gate ✓ 12s · cache 94% esfria em 3m
# Os dados vêm do JSON que o Claude Code passa no stdin. O corpo está em statusline.py.
exec python3 -I "$(dirname "$0")/statusline.py"
