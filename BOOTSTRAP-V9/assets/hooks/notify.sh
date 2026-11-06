#!/usr/bin/env bash
# Notification. Avisa no desktop quando o Claude Code espera você ou terminou.
# Não bloqueia nada; falha em silêncio se não houver como notificar.
set -u
. "$(dirname "$0")/_lib.sh"
py_ok || exit 0
msg="$(json_get message)"; title="$(json_get title)"
title="${title:-Claude Code}"; msg="${msg:-Precisa de você}"
proj="$(basename "$ROOT")"
if command -v osascript >/dev/null 2>&1; then
  osascript - "$title · $proj" "$msg" <<'OSA' >/dev/null 2>&1
on run argv
  display notification (item 2 of argv) with title (item 1 of argv) sound name "Glass"
end run
OSA
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "$title · $proj" "$msg" >/dev/null 2>&1
else
  { printf '\a' > /dev/tty; } 2>/dev/null
fi
exit 0
