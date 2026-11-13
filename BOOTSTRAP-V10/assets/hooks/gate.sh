#!/usr/bin/env bash
# Stop. Roda o GATE_FAST quando o turno deixou mudança no working tree.
#   - verde: grava o hash do estado e libera; o mesmo estado não roda de novo.
#   - vermelho: exit 2 com o fim da saída no stderr. O agente continua e corrige.
#   - após GATE_MAX_RETRIES bloqueios seguidos no mesmo turno: libera com aviso e grava o
#     estado como "liberado". Esse estado não bloqueia de novo, então um gate que já estava
#     vermelho antes não prende turnos seguintes nem turno só de conversa.
# No Codex, exit 2 vira um novo prompt de continuação com o mesmo texto.
# Nada vai para o stdout: o Stop do Codex só aceita JSON ou saída vazia.
set -u
. "$(dirname "$0")/_lib.sh"

[ "${GATE_ON_STOP:-1}" = "1" ] || exit 0
# Sem python3 não há como ler o turno nem limitar as tentativas; o doctor acusa a falta.
py_ok || exit 0
# Pausa explícita, usada na fase vermelha de testes primeiro (testes escritos antes do código).
[ -f "$HOOKS_DIR/gate.pause" ] && exit 0
is_placeholder "${GATE_FAST:-}" && exit 0
git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 || exit 0

STATE="$(git -C "$ROOT" rev-parse --git-path prevec 2>/dev/null)"
case "$STATE" in /*) ;; *) STATE="$ROOT/$STATE" ;; esac
mkdir -p "$STATE"

G() { git -C "$ROOT" "$@"; }
has_head() { G rev-parse --verify -q HEAD >/dev/null 2>&1; }
tracked_diff() {
  if has_head; then G diff --no-ext-diff --no-textconv HEAD
  else G diff --no-ext-diff --no-textconv --cached; G diff --no-ext-diff --no-textconv; fi
}
# Só arquivos regulares: repo aninhado (sub/) e FIFO quebrariam o hash em lote.
untracked_z() {
  G ls-files -z --others --exclude-standard 2>/dev/null | while IFS= read -r -d '' f; do
    [ -f "$ROOT/$f" ] && printf '%s\0' "$f"
  done
}

# Estado = diff dos rastreados + nome e conteúdo dos não rastreados (hash em lote).
state_hash() {
  {
    tracked_diff 2>/dev/null
    untracked_z | tr '\0' '\n'
    (cd "$ROOT" && untracked_z | xargs -0 git hash-object -- 2>/dev/null)
  } | git hash-object --stdin
}

if [ -z "$(tracked_diff 2>/dev/null | head -c 1)" ] && [ -z "$(untracked_z | head -c 1)" ]; then
  exit 0
fi
hash="$(state_hash)"
[ "$(cat "$STATE/gate-ok" 2>/dev/null)" = "$hash" ] && { rm -f "$STATE/gate-tries"; exit 0; }
[ "$(cat "$STATE/gate-released" 2>/dev/null)" = "$hash" ] && exit 0

case "${GATE_TIMEOUT:-}" in ''|*[!0-9]*|0) GATE_TIMEOUT=120 ;; esac
case "${GATE_MAX_RETRIES:-}" in ''|*[!0-9]*) GATE_MAX_RETRIES=3 ;; esac

# Turno: o Codex manda turn_id. No Claude Code, stop_hook_active=false abre turno novo e
# true continua o mesmo. Sem nenhum dos dois, a sessão inteira conta como um turno.
session="$(json_get session_id)"; session="${session:-sem-sessao}"
active="$(json_get stop_hook_active)"
turn="$(json_get turn_id)"
tries_file="$STATE/gate-tries"
last_turn=""; tries=0
if [ -f "$tries_file" ]; then
  read -r last_turn tries < "$tries_file"
  case "$tries" in ''|*[!0-9]*) tries=0 ;; esac
fi
if [ -z "$turn" ]; then
  case "$active" in
    false) turn="$session-$(date +%s)-$$" ;;
    true)  case "$last_turn" in "$session"*) turn="$last_turn" ;; *) turn="$session" ;; esac ;;
    *)     turn="$session" ;;
  esac
fi
[ "$last_turn" = "$turn" ] || tries=0

# Subagente ainda trabalhando nesta sessão: o turno da conversa principal acabou, mas o
# código está pela metade. Gate agora reprovaria arquivo em escrita e gastaria tentativa.
# O próximo Stop (quando o subagente voltar) roda o gate.
busy="$(py -c '
import json, sys, time
try:
    st = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit()
print(sum(1 for v in (st.get("agents") or {}).values() if time.time() - v.get("t", 0) < 1800))
' "$STATE/status/$(printf '%s' "$session" | tr -c 'A-Za-z0-9_.-' '_' | cut -c1-80).json" 2>/dev/null)"
case "$busy" in ''|0) ;; *)
  log_busy() { printf '%s\t0\t0\tsubagente\n' "$(date +%Y-%m-%dT%H:%M:%S)" >> "$STATE/gate-log.tsv"; }
  log_busy; exit 0 ;;
esac

# {changed}: arquivos alterados que ainda existem, cada um entre aspas de shell.
cmd="$GATE_FAST"
case "$cmd" in *"{changed}"*)
  changed=""
  while IFS= read -r -d '' f; do
    [ -n "$f" ] && [ -e "$ROOT/$f" ] || continue
    # Plano, documentação e config do kit não são código: não entram no {changed}.
    case "$f" in .context/*|.claude/*|*.md|*.MD) continue ;; esac
    changed="$changed $(printf '%q' "$f")"
  done < <( { if has_head; then G diff -z --name-only --relative HEAD; else G diff -z --name-only --relative --cached; fi; untracked_z; } 2>/dev/null )
  [ -z "$changed" ] && exit 0
  # Sem aspas em volta de $changed: no bash 3.2 elas viram literais. O %q acima já escapa & e \.
  cmd="${cmd//\{changed\}/$changed}"
;; esac

# Fila de testes: com TQ_FAST=1 o gate espera a vez como qualquer suíte.
# A espera tem teto de metade do GATE_TIMEOUT; fila ocupada demais pula o gate sem gastar tentativa.
tq_on=0
if [ "${TQ_FAST:-0}" = "1" ] && [ -f "$HOOKS_DIR/tq.py" ]; then
  tq_on=1
  cmd="TQ_WAIT=$(( GATE_TIMEOUT / 2 )) python3 -I $(printf '%q' "$HOOKS_DIR/tq.py") $(printf '%q' "$cmd")"
fi

# Registro para a skill retro: data, segundos, código de saída, resultado.
log_run() { printf '%s\t%s\t%s\t%s\n' "$(date +%Y-%m-%dT%H:%M:%S)" "$1" "$2" "$3" >> "$STATE/gate-log.tsv"; }

# Roda com saída em arquivo e limite de tempo (o macOS não tem `timeout`).
out_file="$STATE/gate-out"
started=$(date +%s)
# set -m põe o comando num grupo de processos próprio: o timeout mata também os filhos (tsc, vitest).
rm -f "$STATE/gate-timedout"
set -m
(cd "$ROOT" && exec bash -c "$cmd" </dev/null >"$out_file" 2>&1) &
pid=$!
set +m
# Vigia: TERM no grupo ao estourar o tempo e, se o comando ignorar, KILL 2s depois.
(
  i=0
  while [ "$i" -lt "$GATE_TIMEOUT" ]; do
    sleep 1; kill -0 "$pid" 2>/dev/null || exit 0; i=$((i + 1))
  done
  : > "$STATE/gate-timedout"
  kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  sleep 2
  kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
) >/dev/null 2>&1 &
watchdog=$!
# Se o próprio gate for interrompido, leva o grupo do comando junto.
trap 'kill -TERM -- "-$pid" 2>/dev/null; kill "$watchdog" 2>/dev/null; exit 130' TERM INT HUP
{ wait "$pid"; rc=$?; } 2>/dev/null
trap - TERM INT HUP
kill "$watchdog" 2>/dev/null; { wait "$watchdog"; } 2>/dev/null
timed_out=0
[ -f "$STATE/gate-timedout" ] && { timed_out=1; rm -f "$STATE/gate-timedout"; }
elapsed=$(( $(date +%s) - started ))

if [ $tq_on -eq 1 ] && [ $rc -eq 75 ] && grep -q '^\[tq\] desisti' "$out_file" 2>/dev/null; then
  log_run "$elapsed" 75 fila
  echo "Gate rápido pulado: a fila de testes está ocupada. Rode o teste afetado antes de encerrar." >&2
  exit 0
fi

if [ $rc -eq 0 ]; then
  log_run "$elapsed" 0 verde
  state_hash > "$STATE/gate-ok"
  rm -f "$tries_file" "$STATE/gate-released"
  exit 0
fi

tries=$((tries + 1))
echo "$turn $tries" > "$tries_file"
max="$GATE_MAX_RETRIES"
if [ "$tries" -gt "$max" ]; then
  rm -f "$tries_file"
  state_hash > "$STATE/gate-released"
  log_run "$elapsed" "$rc" liberado
  echo "Gate rápido ainda vermelho após $max tentativas. Liberando o turno: diga ao usuário o que falta." >&2
  exit 0
fi

if [ $timed_out -eq 1 ]; then log_run "$elapsed" "$rc" timeout; else log_run "$elapsed" "$rc" vermelho; fi
{
  if [ $timed_out -eq 1 ]; then
    printf 'Gate rápido passou de %ss e foi interrompido: %s\n' "$GATE_TIMEOUT" "$GATE_FAST"
  else
    printf 'Gate rápido falhou (tentativa %s de %s): %s\n' "$tries" "$max" "$GATE_FAST"
  fi
  tail -n 40 "$out_file" | tail -c 4000
  printf '\n%s\n' "Corrija a causa. Não edite teste nem desligue regra para passar."
  printf '%s\n' "Se a falha já existia antes da sua mudança, diga isso ao usuário em vez de corrigir código fora do pedido."
  [ -f "$HOOKS_DIR/tests.lock" ] && printf '%s\n' "Testes existentes estão travados (tests.lock): escreva teste novo em arquivo novo."
} >&2
exit 2
