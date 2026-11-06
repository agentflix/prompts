#!/usr/bin/env bash
# PreToolUse em edições. Bloqueia (exit 2) três coisas que regra escrita não garante:
#   1. arquivo protegido (.env, chave, lockfile);
#   2. migration já versionada no git;
#   3. teste existente enquanto .claude/hooks/tests.lock existir (modo spec).
# Teste novo continua permitido: o agente pode acrescentar prova, não apagar a que existe.
# Alcance: edições pelas tools de arquivo. Comando de shell que escreve arquivo não passa por aqui.
set -u
. "$(dirname "$0")/_lib.sh"

block() { echo "Bloqueado pelo guard: $1" >&2; exit 2; }

if ! py_ok; then
  block "python3 indisponível, então o guard não consegue ler a edição. Instale o python3 (no macOS, xcode-select --install) ou remova o guard do settings.json."
fi

tracked() { GIT_LITERAL_PATHSPECS=1 git -C "$ROOT" ls-files --error-unmatch -- "$1" >/dev/null 2>&1; }

while IFS= read -r p; do
  [ -z "$p" ] && continue
  case "$(basename "$p")" in *.example|*.sample|*.template) is_model=1 ;; *) is_model=0 ;; esac
  if [ $is_model -eq 0 ] && ! is_placeholder "${PROTECTED:-}" && matches_any "$p" "$PROTECTED"; then
    block "$p é protegido (gates.conf PROTECTED). Peça ao usuário para editar à mão."
  fi
  case "$p" in ../*|..) continue ;; esac
  if ! is_placeholder "${MIGRATIONS:-}" && matches_any "$p" "$MIGRATIONS" && tracked "$p"; then
    block "$p é migration já versionada. Crie uma migration nova com a correção."
  fi
  if [ -f "$HOOKS_DIR/tests.lock" ] && ! is_placeholder "${TESTS:-}" && matches_any "$p" "$TESTS" && tracked "$p"; then
    block "$p é teste existente e os testes estão travados (modo spec). Escreva teste novo em arquivo novo. Se o teste está errado, pare e explique ao usuário."
  fi
done < <(edited_paths)
exit 0
