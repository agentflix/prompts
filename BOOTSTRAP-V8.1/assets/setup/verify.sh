#!/usr/bin/env bash
# Passo 7 — verificação de conformidade do PREVEC V8.
# Rode da raiz do projeto:  bash BOOTSTRAP-V8/assets/setup/verify.sh
# Também serve depois do setup, para auditar se a estrutura degradou.

FAIL=0
ok()   { printf "  \033[32mOK\033[0m    %s\n" "$1"; }
bad()  { printf "  \033[31mFALHA\033[0m %s\n" "$1"; FAIL=1; }
warn() { printf "  \033[33mAVISO\033[0m %s\n" "$1"; }
head_() { printf "\n\033[1m%s\033[0m\n" "$1"; }
toml_valid() {
  python3 -c 'import sys,tomllib; tomllib.load(open(sys.argv[1], "rb"))' "$1" >/dev/null 2>&1
}

echo "=== PREVEC V8 — verificação ==="

head_ "Contrato"
if [ -f AGENTS.md ]; then
  n=$(wc -l < AGENTS.md | tr -d ' ')
  [ "$n" -le 80 ] && ok "AGENTS.md ($n linhas, limite 80)" || bad "AGENTS.md com $n linhas — limite é 80"
  b=$(wc -c < AGENTS.md | tr -d ' ')
  [ "$b" -le 32768 ] && ok "AGENTS.md ${b}B (teto do Codex: 32768B)" || bad "AGENTS.md ${b}B excede o teto de 32 KiB do Codex"
else bad "AGENTS.md ausente"; fi

if [ -f CLAUDE.md ]; then
  grep -q "@AGENTS.md" CLAUDE.md && ok "CLAUDE.md importa @AGENTS.md" || bad "CLAUDE.md não importa @AGENTS.md"
  n=$(wc -l < CLAUDE.md | tr -d ' ')
  [ "$n" -le 5 ] || warn "CLAUDE.md tem $n linhas — deveria ser só o import"
else bad "CLAUDE.md ausente"; fi

head_ "Agents e modelos"
declare -a WANT_AGENT=("PLANNER:opus" "BUILDER:sonnet" "REVIEWER:sonnet")
for pair in "${WANT_AGENT[@]}"; do
  a="${pair%%:*}"; m="${pair##*:}"
  f=".claude/agents/$a.md"
  if [ -f "$f" ]; then
    got=$(grep -m1 '^model:' "$f" | sed 's/model:[[:space:]]*//')
    [ "$got" = "$m" ] && ok "$a.md (model: $got)" || bad "$a.md com model: '$got' — esperado '$m'"
  else bad "$a.md ausente"; fi
done
[ -f .claude/agents/ORCHESTRATOR.md ] && bad "ORCHESTRATOR.md existe — no V8 ele funde no PLANNER"

head_ "Settings"
if [ -f .claude/settings.json ]; then
  if command -v jq >/dev/null 2>&1; then
    if jq -e . .claude/settings.json >/dev/null 2>&1; then
      got=$(jq -r '.agent // empty' .claude/settings.json)
      [ "$got" = "PLANNER" ] && ok "settings.json → agent: PLANNER" || bad "settings.json com agent: '$got' — esperado PLANNER"
    else bad "settings.json é JSON inválido — isso desabilita TODAS as settings do arquivo"; fi
  else warn "jq ausente: não foi possível validar o JSON"; fi
else bad ".claude/settings.json ausente"; fi

if [ -d .codex ]; then
  if [ -f .codex/config.toml ]; then
    if command -v python3 >/dev/null 2>&1 && python3 -c 'import tomllib' >/dev/null 2>&1; then
      toml_valid .codex/config.toml && ok ".codex/config.toml válido" \
        || bad ".codex/config.toml é TOML inválido"
    else
      warn "Python 3.11+ ausente: não foi possível validar a sintaxe TOML"
    fi

    got=$(grep -m1 '^model[[:space:]]*=' .codex/config.toml | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
    [ "$got" = "gpt-5.6-sol" ] && ok "Codex thread principal: gpt-5.6-sol" \
      || bad "Codex thread principal com model '$got' — esperado gpt-5.6-sol"
    got=$(grep -m1 '^model_reasoning_effort[[:space:]]*=' .codex/config.toml | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
    [ "$got" = "high" ] && ok "Codex thread principal: reasoning high" \
      || bad "Codex thread principal com reasoning '$got' — esperado high"
    grep -q 'developer_instructions' .codex/config.toml \
      && grep -q 'PLANNER' .codex/config.toml \
      && grep -q '\.claude/agents/PLANNER.md' .codex/config.toml \
      && ok "Codex inicia com comportamento PLANNER" \
      || bad "Codex config não injeta o PLANNER canônico na thread principal"
    got=$(grep -m1 '^max_concurrent_threads_per_session[[:space:]]*=' .codex/config.toml | sed -E 's/.*=[[:space:]]*([0-9]+).*/\1/')
    [ -n "$got" ] && [ "$got" -ge 8 ] \
      && ok "Codex suporta REVIEWER + 7 revisores ($got threads)" \
      || bad "Codex precisa de max_concurrent_threads_per_session >= 8"
    got=$(grep -m1 '^default_subagent_model[[:space:]]*=' .codex/config.toml | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
    got_effort=$(grep -m1 '^default_subagent_reasoning_effort[[:space:]]*=' .codex/config.toml | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
    [ "$got" = "gpt-5.6-terra" ] && [ "$got_effort" = "medium" ] \
      && ok "Codex subagent default: gpt-5.6-terra/medium" \
      || bad "Codex subagent default divergente — esperado gpt-5.6-terra/medium"
    grep -q '^enabled[[:space:]]*=[[:space:]]*true' .codex/config.toml \
      && ok "Codex multi-agent habilitado" \
      || bad "Codex [agents].enabled precisa ser true"
  else
    bad ".codex/config.toml ausente"
  fi

  declare -a WANT_CODEX_AGENT=(
    "planner:PLANNER:gpt-5.6-sol:high"
    "builder:BUILDER:gpt-5.6-terra:medium"
    "reviewer:REVIEWER:gpt-5.6-sol:high"
  )
  for spec in "${WANT_CODEX_AGENT[@]}"; do
    IFS=: read -r file agent model effort <<< "$spec"
    f=".codex/agents/$file.toml"
    if [ -f "$f" ]; then
      if command -v python3 >/dev/null 2>&1 && python3 -c 'import tomllib' >/dev/null 2>&1; then
        toml_valid "$f" || bad "$f é TOML inválido"
      fi
      got_name=$(grep -m1 '^name[[:space:]]*=' "$f" | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
      got_model=$(grep -m1 '^model[[:space:]]*=' "$f" | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
      got_effort=$(grep -m1 '^model_reasoning_effort[[:space:]]*=' "$f" | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')
      [ "$got_name" = "$agent" ] && [ "$got_model" = "$model" ] && [ "$got_effort" = "$effort" ] \
        && ok "Codex $agent ($got_model/$got_effort)" \
        || bad "Codex $file: name/model/effort divergente — esperado $agent/$model/$effort"
      grep -q '^developer_instructions[[:space:]]*=' "$f" \
        && grep -q "\.claude/agents/$agent.md" "$f" \
        || bad "Codex $agent não aponta para a especificação canônica"
    else
      bad "$f ausente"
    fi
  done
fi

head_ "Arquitetura — 5 arquivos"
for f in overview.md modules.yaml rules.md gates.md flows.md; do
  [ -f ".context/arch/$f" ] && ok "arch/$f" || bad "arch/$f ausente"
done

head_ "Derivados (não devem existir)"
DERIV=0
for f in modules.md context-snapshot.md project-state.yaml context-version.yaml dependencies.yaml project-brain.yaml; do
  [ -f ".context/arch/$f" ] && { bad "arch/$f é derivado — remova"; DERIV=1; }
  [ -f ".context/ARCHITECTURE/$f" ] && { bad "ARCHITECTURE/$f é do V7 — migre"; DERIV=1; }
done
[ "$DERIV" -eq 0 ] && ok "nenhum derivado materializado"

head_ "Pastas do V7 que não sobrevivem ao V8"
LEG=0
for d in .context/DOCS/PRDS .context/DOCS/FEATURES .context/DOCS/TASKS .context/DOCS/CHANGELOG .context/.session .context/skills; do
  [ -d "$d" ] && { bad "$d ainda existe — foi absorvida no V8"; LEG=1; }
done
[ -f .context/orchestrator-context-model.md ] && { bad "orchestrator-context-model.md — vira seção do PLANNER"; LEG=1; }
[ "$LEG" -eq 0 ] && ok "nenhum resíduo do V7"

head_ "Skills"
for s in plan build ship; do
  [ -f ".claude/skills/$s/SKILL.md" ] && ok "skills/$s" || bad "skills/$s ausente"
done
ctx=$(ls -d .claude/skills/arch-* .claude/skills/gates 2>/dev/null | wc -l | tr -d ' ')
[ "$ctx" -ge 2 ] && ok "$ctx skills de contexto" || warn "só $ctx skill(s) de contexto — o AGENTS.md tende a inflar"
for s in .claude/skills/*/SKILL.md; do
  [ -f "$s" ] || continue
  grep -q "^description:" "$s" || bad "$(dirname "$s"|xargs basename): SKILL.md sem 'description' — não dispara"
done

head_ "Metodologia"
if [ -f .context/PREVEC.md ]; then
  ok "PREVEC.md presente (metodologia auto-contida)"
  grep -q "ia-coders" .context/PREVEC.md && ok "crédito ao ia-coders" || bad "PREVEC.md sem o crédito ao ia-coders"
  grep -qE "T\.A\.C\.E|TACE" .context/PREVEC.md && ok "T.A.C.E definido em PREVEC.md" \
    || bad "PREVEC.md não define o T.A.C.E — é o mecanismo central do workflow"
  grep -q "PREVEC.md" AGENTS.md 2>/dev/null && ok "AGENTS.md aponta para PREVEC.md" \
    || bad "AGENTS.md não referencia PREVEC.md — a metodologia fica órfã"
else bad ".context/PREVEC.md ausente — a metodologia precisa viajar com o repositório"; fi
if grep -rq "github.com/ia-coders" AGENTS.md .context .claude 2>/dev/null; then
  bad "há URL de repositório externo no contexto — crédito é nome, não link (pode sair do ar)"
else ok "nenhuma dependência de URL externa"; fi

head_ "Formatos e templates"
for f in .context/formats/plan.md .context/formats/response.md; do
  [ -f "$f" ] && ok "$(basename "$f")" || bad "$f ausente — os agents referenciam este path"
done
[ -f .context/work/_TEMPLATE.md ] && ok "work/_TEMPLATE.md" || bad "work/_TEMPLATE.md ausente"
[ -d .context/arch/decisions ] && { [ -f .context/arch/decisions/_TEMPLATE.md ] && ok "decisions/_TEMPLATE.md" || warn "decisions/ sem _TEMPLATE.md"; }

head_ "Colas nativas"
if [ -d .codex ]; then
  [ -L .codex/skills ] && ok ".codex/skills → $(readlink .codex/skills)" || bad ".codex/skills não é symlink"
fi
if [ -f opencode.json ]; then
  if command -v jq >/dev/null 2>&1; then
    jq -e . opencode.json >/dev/null 2>&1 && ok "opencode.json válido" || bad "opencode.json é JSON inválido"
  fi
fi

head_ "Variáveis de template não substituídas"
# TODAS as skills e também .context/design/ — as arch-* e a design nascem como
# template e é fácil copiá-las com placeholder dentro.
# ALL_DOMAINS é sentinela LEGÍTIMA de modules.yaml, não placeholder — por isso o -v.
hits=$(grep -rlE '\[[A-Z_]{3,}\]|\[ADAPTAR\]' \
         AGENTS.md .claude/agents/ .claude/skills/ .codex/agents/ .context/arch/ .context/formats/ .context/design/ 2>/dev/null \
       | while read -r f; do
           # um arquivo só é acusado se tiver placeholder que NÃO seja um sentinela conhecido
           grep -oE '\[[A-Z_]{3,}\]|\[ADAPTAR\]' "$f" | grep -qvE '^\[(ALL_DOMAINS|ADDED|MODIFIED|REMOVED|N)\]$' && echo "$f"
         done)
[ -z "$hits" ] && ok "nenhuma" || { bad "placeholders remanescentes:"; echo "$hits" | sed 's/^/        /'; }

head_ "Duplicação de CONTEÚDO"
# Referência a um path NÃO é duplicação — é o design funcionando. O que este bloco
# mede é conteúdo COPIADO: comando de gate reproduzido, e texto de regra reescrito
# onde deveria haver só o número dela.
probe () {
  local label="$1" pat="$2" limit="$3"
  local n
  n=$(grep -rl -- "$pat" AGENTS.md .claude/agents/ .claude/skills/ .codex/agents/ .context/ 2>/dev/null | wc -l | tr -d ' ')
  if [ "$n" -le "$limit" ]; then ok "$label: $n arquivo(s)"
  else bad "$label: $n arquivos (limite $limit) — copiado em vez de referenciado"; fi
}

if [ -f .context/arch/gates.md ]; then
  # Extrai o comando de gate DE VERDADE, de dentro dos blocos ```bash: pega a última
  # palavra-de-comando da linha, descartando o prefixo `cd <path> &&` que o template
  # prescreve. Sem isso a probe media "cd <path>" e nunca detectava duplicação.
  cmd=$(sed -n '/^```bash/,/^```/p' .context/arch/gates.md \
        | grep -vE '^```|^\s*#|^\s*$' \
        | sed 's/.*&&[[:space:]]*//' \
        | grep -oE '^[a-z][a-z0-9_.-]* [a-z][a-z0-9:_.-]*' | head -1 | xargs)
  if [ -n "$cmd" ]; then
    probe "comando de gate '$cmd'" "$cmd" 3
  else
    warn "não consegui extrair um comando de gate de arch/gates.md — a probe de duplicação não rodou"
  fi
fi

# Texto de regra copiado: pega a frase mais longa de cada uma das 3 primeiras regras
# e confere se ela vive em mais de um arquivo. Regra deve ser CITADA POR NÚMERO.
if [ -f .context/arch/rules.md ]; then
  dup=0
  while IFS= read -r frag; do
    [ ${#frag} -lt 25 ] && continue
    n=$(grep -rl -- "$frag" AGENTS.md .claude/ .codex/agents/ .context/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$n" -gt 1 ]; then
      bad "texto de regra em $n arquivos: \"$(echo "$frag" | cut -c1-48)…\""
      grep -rl -- "$frag" AGENTS.md .claude/ .codex/agents/ .context/ 2>/dev/null | sed 's/^/        /'
      dup=1
    fi
  done < <(grep -E '^\*\*[0-9]+\.\*\*' .context/arch/rules.md | head -3 \
            | sed 's/^\*\*[0-9]*\.\*\* *//' | cut -d'.' -f1 | cut -c1-60)
  [ "$dup" -eq 0 ] && ok "nenhum texto de regra copiado — as regras são citadas por número"
fi

head_ "Referências (aqui mais é melhor)"
for p in "arch/rules.md" "arch/gates.md" "formats/response.md"; do
  n=$(grep -rl -- "$p" AGENTS.md .claude/ .codex/agents/ .context/ 2>/dev/null | wc -l | tr -d ' ')
  [ "$n" -ge 2 ] && ok "$p referenciado em $n arquivos" \
    || warn "$p referenciado em só $n arquivo — os agents deveriam apontar para ele"
done

echo
if [ "$FAIL" -eq 0 ]; then
  printf "\033[32m=== conforme ===\033[0m\n"
else
  printf "\033[31m=== há falhas acima ===\033[0m\n"
fi
exit $FAIL
