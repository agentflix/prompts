#!/usr/bin/env bash
# PostToolUse em edições. Formata o arquivo editado. Nunca bloqueia e não imprime nada:
# formatação é trabalho de máquina, não precisa gastar token do modelo.
set -u
. "$(dirname "$0")/_lib.sh"
py_ok || exit 0
is_placeholder "${FORMAT:-}" && exit 0

# O caminho entra por variável de ambiente ($FILE), nunca interpolado no comando.
# "{file}" e '{file}' viram "$FILE"; {file} solto também.
cmd="$(printf '%s' "$FORMAT" | sed -e "s/\"{file}\"/\"\$FILE\"/g" -e "s/'{file}'/\"\$FILE\"/g" -e 's/{file}/"$FILE"/g')"

while IFS= read -r p; do
  case "$p" in ../*|..) continue ;; esac
  [ -f "$ROOT/$p" ] || continue
  (cd "$ROOT" && FILE="$ROOT/$p" bash -c "$cmd" </dev/null) >/dev/null 2>&1 || true
done < <(edited_paths)
exit 0
