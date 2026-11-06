#!/usr/bin/env bash
# PREVEC V9 — doctor. Rode da raiz do projeto: bash <pasta-do-bootstrap>/assets/doctor.sh
# Serve no setup e depois, para ver se o contexto engordou ou degradou.
# Mede o custo do que carrega sempre, acha placeholder, ênfase em CAPS, regra sem paths,
# hook quebrado e config de ferramenta inválida.

FAIL=0
ok()   { printf "  \033[32mOK\033[0m    %s\n" "$1"; }
bad()  { printf "  \033[31mFALHA\033[0m %s\n" "$1"; FAIL=1; }
warn() { printf "  \033[33mAVISO\033[0m %s\n" "$1"; }
sec()  { printf "\n\033[1m%s\033[0m\n" "$1"; }
tok()  { [ -f "$1" ] && echo $(( $(wc -c < "$1") / 4 )) || echo 0; }
frontmatter() { awk 'NR==1 && /^---/ {f=1; next} f && /^---/ {exit} f' "$1"; }
toml_ok() {
  [ "${PY:-0}" = 1 ] || return 3
  python3 -I - "$1" <<'PY' 2>/dev/null
import sys
try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        sys.exit(3)
tomllib.load(open(sys.argv[1], "rb"))
PY
}

echo "=== PREVEC V9 — doctor ==="

sec "Sempre carregado"
if [ -f AGENTS.md ]; then
  n=$(wc -l < AGENTS.md | tr -d ' ')
  if   [ "$n" -le 60 ];  then ok "AGENTS.md: $n linhas"
  elif [ "$n" -le 100 ]; then warn "AGENTS.md: $n linhas (alvo até 60). O que o agente descobre lendo o código pode sair"
  else bad "AGENTS.md: $n linhas. Acima de 100 a adesão cai e o custo sobe em todo turno"; fi
  [ "$(wc -c < AGENTS.md)" -le 32768 ] || bad "AGENTS.md passa de 32 KiB: o Codex corta o excedente"
else bad "AGENTS.md ausente"; fi

if [ -f CLAUDE.md ]; then
  grep -q '^@AGENTS.md' CLAUDE.md && ok "CLAUDE.md importa @AGENTS.md" || bad "CLAUDE.md não importa @AGENTS.md"
elif [ -d .claude/hooks ] && [ -f .claude/settings.json ]; then warn "CLAUDE.md ausente: sem ele, o Claude Code pode ignorar o AGENTS.md. Crie com @AGENTS.md"; fi

always=$(( $(tok AGENTS.md) + $(tok CLAUDE.md) ))
global_rules=0
for r in .claude/rules/*.md; do
  [ -f "$r" ] || continue
  if frontmatter "$r" | grep -q '^paths:'; then :; else
    global_rules=$((global_rules + 1)); always=$((always + $(tok "$r")))
    warn "$r sem paths: carrega em toda sessão"
  fi
done
desc=0
for s in .claude/skills/*/SKILL.md; do
  [ -f "$s" ] || continue
  frontmatter "$s" | grep -q '^disable-model-invocation:[[:space:]]*true' && continue
  d=$(frontmatter "$s" | awk '/^description:/ {sub(/^description:[[:space:]]*/, ""); v=$0; m=1; next} m && /^[[:space:]]/ {v=v " " $0; next} m {exit} END {print v}')
  desc=$((desc + ${#d} / 4 + 10))
  [ ${#d} -le 1024 ] || bad "$s: description com ${#d} caracteres (máximo 1024)"
  l=$(wc -l < "$s" | tr -d ' ')
  [ "$l" -le 500 ] || warn "$s: $l linhas (alvo até 500; mova detalhe para references/)"
done
always=$((always + desc))
if [ "$always" -le 1700 ]; then ok "Custo fixo estimado: ~$always tokens por sessão (AGENTS + CLAUDE + regras globais + descrições de skill)"
elif [ "$always" -le 3000 ]; then warn "Custo fixo estimado: ~$always tokens. Alvo: até 1700. As descrições de skill pesam; desinstale as que não usa"
else bad "Custo fixo estimado: ~$always tokens. Corte o AGENTS.md ou ponha paths: nas regras"; fi

sec "Higiene"
files=$(ls AGENTS.md CLAUDE.md .claude/rules/*.md .claude/skills/*/SKILL.md .claude/agents/*.md .claude/hooks/gates.conf 2>/dev/null)
[ -n "$files" ] || files=/dev/null
# Placeholder só nos arquivos que o setup preenche; skills e agents do kit têm moldes de resposta legítimos.
pfiles=$(ls AGENTS.md CLAUDE.md .claude/rules/*.md .claude/hooks/gates.conf 2>/dev/null)
[ -n "$pfiles" ] || pfiles=/dev/null
PH_RE='<ex\.:|<Projeto>|<Uma linha|<pt-BR>|<idioma>|<chave>|<lib>|<Seção|(^|[^[:alnum:]_])<[^<>]*[[:space:]]\|[[:space:]][^<>]*>|<[^<>]*[[:space:]](de|do|da|dos|das|ou|com|se|sem|no|na)[[:space:]][^<>]*>|\[ADAPTAR|\[PROJECT'
ph=$(for f in $pfiles; do
  awk -v F="$f" '/^[[:space:]]*```/ {fence = !fence; next} !fence {print F ":" NR ":" $0}' "$f" 2>/dev/null
done | sed 's/`[^`]*`//g' | grep -E "$PH_RE")
[ -z "$ph" ] && ok "Nenhum placeholder" || { bad "Placeholder não resolvido:"; echo "$ph" | head -10 | sed 's/^/        /'; }
cm=$(grep -n '<!--' AGENTS.md .claude/rules/*.md 2>/dev/null)
[ -z "$cm" ] && ok "Sem comentário de molde nos arquivos gerados" || { bad "Comentário de molde copiado junto:"; echo "$cm" | head -5 | sed 's/^/        /'; }
caps=$(grep -nE '\b(IMPORTANT|CRITICAL|MUST|NEVER|ALWAYS|NUNCA|SEMPRE|OBRIGATÓRIO|PROIBIDO)\b|([A-ZÁÉÍÓÚÃÕÇ]{4,} ){3,}' $files 2>/dev/null)
[ -z "$caps" ] && ok "Sem ênfase em CAPS" || { warn "Ênfase em CAPS (modelos atuais aplicam a regra além da conta; escreva o motivo):"; echo "$caps" | head -5 | sed 's/^/        /'; }

sec "Hooks"
# Checa só o que foi instalado: o wizard do setup deixa o usuário desligar partes.
if python3 -I -c 'import json' >/dev/null 2>&1; then PY=1; ok "python3 disponível"
else PY=0; bad "python3 ausente ou quebrado: o guard bloqueia toda edição e o format não roda. No macOS: xcode-select --install"; fi
if [ -d .claude/hooks ]; then
  for h in _lib.sh gates.conf; do
    [ -f ".claude/hooks/$h" ] && ok ".claude/hooks/$h" || bad ".claude/hooks/$h ausente: os hooks dependem dele"
  done
  for h in gate.sh guard.sh format.sh statusline.sh notify.sh; do
    [ -f ".claude/hooks/$h" ] && { [ -x ".claude/hooks/$h" ] || bad ".claude/hooks/$h sem permissão de execução (chmod +x)"; }
  done
  [ -f .claude/hooks/statusline.sh ] && { [ -f .claude/hooks/statusline.py ] || bad ".claude/hooks/statusline.py ausente: a statusline fica em branco"; }
fi
if [ -f .claude/hooks/gates.conf ]; then
  gf=$( . .claude/hooks/gates.conf; printf '%s' "${GATE_FAST:-}" )
  case "$gf" in
    "<"*) bad "GATE_FAST com placeholder: preencha ou deixe \"\"" ;;
    "")   warn "GATE_FAST vazio: o gate do fim de turno está desligado. Normal só em projeto sem typecheck nem teste" ;;
    *)    ok "GATE_FAST definido" ;;
  esac
fi
if [ -f .claude/settings.json ]; then
  if [ "$PY" = 1 ]; then
    python3 -I -c 'import json;json.load(open(".claude/settings.json"))' 2>/dev/null && ok "settings.json válido" || bad "settings.json inválido"
  fi
  for h in gate.sh guard.sh format.sh notify.sh statusline.sh; do
    if grep -q "$h" .claude/settings.json; then
      [ -f ".claude/hooks/$h" ] && ok "settings.json liga $h" || bad "settings.json liga $h, mas o arquivo não existe"
    elif [ -f ".claude/hooks/$h" ]; then
      warn "$h existe mas o settings.json não o liga"
    fi
  done
  grep -q '"agent"' .claude/settings.json && warn "settings.json fixa um agente padrão: o thread principal deve ser o agente nativo"
elif [ -f CLAUDE.md ]; then
  bad ".claude/settings.json ausente: com Claude Code, os hooks não rodam sem ele"
else
  ok "Sem Claude Code: settings.json, statusline e notify não se aplicam"
fi
if [ -x .claude/hooks/statusline.sh ] && [ "$PY" = 1 ]; then
  out=$(echo '{}' | .claude/hooks/statusline.sh 2>/dev/null)
  [ -n "$out" ] && ok "statusline responde (teste com JSON vazio)" || bad "statusline não imprimiu nada com JSON vazio"
fi
if [ -x .claude/hooks/guard.sh ] && [ "$PY" = 1 ]; then
  echo '{"tool_input":{"file_path":".env"}}' | CLAUDE_PROJECT_DIR="$PWD" .claude/hooks/guard.sh >/dev/null 2>&1
  [ $? -eq 2 ] && ok "guard.sh bloqueia .env (teste simulado)" || warn "guard.sh não bloqueou .env: confira PROTECTED no gates.conf"
fi

[ -f .claude/hooks/gate.pause ] && warn "gate.pause ativo: o gate do fim de turno está desligado. Apague se a fase de testes vermelhos acabou"
[ -f .claude/hooks/tests.lock ] && warn "tests.lock ativo: testes existentes travados. Apague se nenhuma spec está em andamento"

sec "Subagentes"
if ls .claude/agents/*.md >/dev/null 2>&1; then
  for a in .claude/agents/*.md; do
    m=$(frontmatter "$a" | sed -n 's/^model:[[:space:]]*//p' | head -1)
    e=$(frontmatter "$a" | sed -n 's/^effort:[[:space:]]*//p' | head -1)
    case "$m" in
      haiku|sonnet|opus|fable|best|inherit|claude-*|*"[1m]") ok "$(basename "$a" .md): ${m} · ${e:-effort herdado}" ;;
      "") warn "$(basename "$a" .md) sem model: herda o modelo da conversa principal (Opus por padrão)" ;;
      *) bad "$(basename "$a" .md): model '$m' não é alias nem ID conhecido" ;;
    esac
    case "$e" in ""|low|medium|high|xhigh|max) ;; *) bad "$(basename "$a" .md): effort '$e' inválido (low, medium, high, xhigh, max)" ;; esac
    case "$(basename "$a" .md):$m" in revisor:haiku) warn "revisor em Haiku: revisão é onde o modelo barato mais erra" ;; esac
  done
  [ -d .claude/skills/delegar ] || warn "Há subagentes mas a skill delegar não está instalada: o orquestrador fica sem a regra de roteamento"
fi

sec "Ferramentas"
if [ -L .agents/skills ] || [ -e .agents/skills ] || [ -d .codex ]; then
  [ -d .agents/skills ] && ok ".agents/skills resolve (Codex lê skills daqui)" || bad ".agents/skills ausente ou symlink quebrado"
  [ -L .codex/skills ] && warn ".codex/skills é do V8: o Codex lê .agents/skills. Remova"
  if [ -f .codex/config.toml ]; then
    toml_ok .codex/config.toml; rc=$?
    if [ $rc -eq 0 ]; then ok ".codex/config.toml válido"
    elif [ $rc -eq 3 ]; then warn ".codex/config.toml não validado: precisa de Python 3.11+ (tomllib) ou do pacote tomli"
    else bad ".codex/config.toml inválido"; fi
  fi
  if [ -f .codex/hooks.json ]; then
    if [ "$PY" = 1 ]; then python3 -I -c 'import json;json.load(open(".codex/hooks.json"))' 2>/dev/null && ok ".codex/hooks.json válido" || bad ".codex/hooks.json inválido"; fi
  fi
fi
if [ -f opencode.json ]; then
  grep -q '"agent"[[:space:]]*:' opencode.json && bad "opencode.json usa a chave agent do schema V1. No V2 é agents" || ok "opencode.json no schema V2"
fi

sec "Formato do .context"
if [ -d .context ]; then
  extra=$(find .context -mindepth 1 -maxdepth 1 ! -name decisions ! -name specs ! -name _arquivo ! -name '.*' 2>/dev/null)
  [ -z "$extra" ] && ok ".context/ no formato V9 (decisions, specs, _arquivo)" || { warn "Fora do formato V9 em .context/ (migre ou arquive, seção 2 do bootstrap):"; echo "$extra" | head -8 | sed 's/^/        /'; }
fi

sec "Restos do V8"
for f in .context/PREVEC.md .context/formats .context/arch .context/work .claude/agents/PLANNER.md .claude/agents/BUILDER.md .claude/agents/REVIEWER.md .claude/skills/plan .claude/skills/build .claude/skills/gates .claude/skills/design .codex/agents/planner.toml .codex/agents/builder.toml .codex/agents/reviewer.toml; do
  [ -e "$f" ] && warn "$f ainda existe (V8). Veja a migração no bootstrap-v9.md"
done
for f in .claude/skills/arch-*; do [ -e "$f" ] && warn "$f ainda existe (V8): virou .claude/rules/"; done

echo
[ $FAIL -eq 0 ] && echo "Resultado: OK" || { echo "Resultado: FALHA"; exit 1; }
