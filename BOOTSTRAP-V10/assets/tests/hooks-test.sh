#!/usr/bin/env bash
# Suíte de regressão dos hooks do V10. Roda só num diretório temporário próprio.
# Uso: bash <kit>/assets/tests/hooks-test.sh
TMP="$(mktemp -d 2>/dev/null)" || { echo "mktemp falhou"; exit 1; }
case "$TMP" in /tmp/*|/private/*|/var/*) ;; *) echo "TMP inesperado: $TMP"; exit 1 ;; esac
trap 'rm -rf "$TMP"' EXIT
S="$TMP/v10 test/proj"
B="$(cd "$(dirname "$0")/../.." && pwd)"
[ -f "$B/assets/hooks/gate.sh" ] || { echo "kit não encontrado em $B"; exit 1; }
mkdir -p "$S" && cd "$S" || exit 1; git init -q && git config user.email t@t && git config user.name t
mkdir -p .claude/hooks migrations tests sub/tests sub/secrets
cp "$B"/assets/hooks/* .claude/hooks/ && chmod +x .claude/hooks/*.sh
conf() { cat > .claude/hooks/gates.conf; }
conf <<'EOF'
GATE_FAST="grep -q good new.txt 2>/dev/null || ! test -f new.txt"
FORMAT='for a in "{file}"; do echo "[$a]" >> fmt.log; done; cat >/dev/null'
GATE_MAX_RETRIES=2
PROTECTED=".env .env.local *.pem secrets/*"
MIGRATIONS="migrations/*"
TESTS="tests/*"
EOF
echo x > migrations/1.sql; echo t > tests/a.ts; echo t > sub/tests/a.ts; touch real.pem; mkdir -p ../out; echo S > ../out/envfile
printf '.claude/hooks/gate-*\nfmt.log\n' > .gitignore
git add -A; git commit -qm i
n=0; fails=0
chk() { n=$((n+1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (esperado $2, veio $1)"; fails=$((fails+1)); fi; }
g() { echo "$1" | /bin/bash .claude/hooks/$2 >/dev/null 2>&1; echo $?; }
chk "$(g '{"tool_input":{"file_path":"other.pem"}}' guard.sh)" 2 "glob com arquivo existente"
chk "$(g '{"tool_input":{"file_path":".ENV"}}' guard.sh)" 2 "maiúscula .ENV"
chk "$(g '{"tool_input":{"file_path":"sub/secrets/a"}}' guard.sh)" 2 "padrão em subpasta"
chk "$(g '{"tool_input":{"file_path":".env.example"}}' guard.sh)" 0 ".env.example livre"
ln -s ../out/envfile .env 2>/dev/null; chk "$(g '{"tool_input":{"file_path":".env"}}' guard.sh)" 2 "symlink .env"; rm .env
chk "$(g '{"tool_input":{"file_path":"./migrations/1.sql"}}' guard.sh)" 2 "migration ./"
chk "$(g '{"tool_input":{"file_path":"a/../migrations/1.sql"}}' guard.sh)" 2 "migration a/../"
chk "$(g '{"tool_input":{"file_path":"migrations/2.sql"}}' guard.sh)" 0 "migration nova"
chk "$(g '{"cwd":"'"$S"'/sub","tool_input":{"file_path":"tests/a.ts"}}' guard.sh)" 0 "cwd subpasta sem lock"
touch .claude/hooks/tests.lock
chk "$(g '{"tool_input":{"file_path":"tests/a.ts"}}' guard.sh)" 2 "teste travado"
chk "$(g '{"cwd":"'"$S"'/sub","tool_input":{"file_path":"tests/a.ts"}}' guard.sh)" 2 "teste travado via cwd"
chk "$(g '{"tool_input":{"file_path":"tests/novo.ts"}}' guard.sh)" 0 "teste novo liberado"
rm .claude/hooks/tests.lock
echo 'raise SystemExit(5)' > json.py; chk "$(g '{"tool_input":{"file_path":".env"}}' guard.sh)" 2 "json.py na raiz não derruba"; rm json.py
chk "$(python3 -c 'import json;print(json.dumps({"tool_input":{"command":"*** Begin Patch\n*** Add File: .env.local\n+A\n*** End Patch"}}))' | /bin/bash .claude/hooks/guard.sh >/dev/null 2>&1; echo $?)" 2 "codex apply_patch"
mkdir -p "d s"; touch "d s/f.txt" b.txt '$(touch PWNED).ts'
python3 -c 'import json;print(json.dumps({"tool_input":{"command":"*** Begin Patch\n*** Update File: d s/f.txt\n*** Update File: b.txt\n*** Update File: $(touch PWNED).ts\n*** End Patch"}}))' | /bin/bash .claude/hooks/format.sh
chk "$(grep -c . fmt.log)" 3 "format: 3 arquivos, sem engolir stdin"
chk "$(grep -c 'd s/f.txt\]' fmt.log)" 1 "format: caminho com espaço é 1 argumento"
chk "$(ls PWNED 2>/dev/null | wc -l | tr -d ' ')" 0 "format sem injeção"
rm -rf "d s" b.txt '$(touch PWNED).ts' fmt.log
G() { echo "{\"session_id\":\"s\",\"stop_hook_active\":$1}" | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1; echo $?; }
echo good > new.txt; chk "$(G false)" 0 "gate verde"
echo bad > new.txt; chk "$(G false)" 2 "conteúdo de untracked muda"
echo good > new.txt; chk "$(G true)" 0 "fix no lugar"
echo b1 > new.txt; chk "$(G false)" 2 "turno novo: tentativa 1"
echo b2 > new.txt; chk "$(G true)" 2 "continuação: tentativa 2"
echo b3 > new.txt; chk "$(G true)" 0 "continuação: libera após max"
chk "$(G false)" 0 "estado liberado não prende turno de conversa"
echo b4 > new.txt; chk "$(G false)" 2 "mudança nova volta a checar"
echo good > new.txt; G false >/dev/null
conf <<'EOF'
GATE_FAST='date +%s%N > .tsbuildinfo; echo run >> runs.log'
EOF
echo '.claude/hooks/gate-*' > .gitignore; echo runs.log >> .gitignore
G false >/dev/null; G false >/dev/null; G false >/dev/null
chk "$(wc -l < runs.log | tr -d ' ')" 1 "artefato do gate não faz rodar todo turno"
rm -f runs.log .tsbuildinfo
conf <<'EOF'
GATE_FAST='sleep 30'
GATE_TIMEOUT=2
EOF
echo z >> new.txt; s=$(date +%s); r=$(G false); e=$(( $(date +%s) - s ))
chk "$r" 2 "timeout vira falha"; chk "$([ $e -lt 8 ] && echo rapido)" rapido "timeout respeitado (${e}s)"
conf <<'EOF'
GATE_FAST='head -c 3000000 /dev/zero | tr "\0" x; false'
EOF
echo y >> new.txt; sz=$(echo '{"session_id":"q","stop_hook_active":false}' | /bin/bash .claude/hooks/gate.sh 2>&1 >/dev/null | wc -c | tr -d ' ')
chk "$([ $sz -lt 5000 ] && echo pequeno)" pequeno "saída limitada ($sz bytes)"
chk "$(echo '{}' | /bin/bash .claude/hooks/gate.sh 2>/dev/null | wc -c | tr -d ' ')" 0 "stdout vazio"
for i in $(seq 1 2000); do echo $i > "u$i.txt"; done
conf <<'EOF'
GATE_FAST='true'
EOF
s=$(date +%s); G false >/dev/null; e=$(( $(date +%s) - s )); chk "$([ $e -lt 10 ] && echo rapido)" rapido "2000 untracked em ${e}s"
rm -f u*.txt
cd "$TMP" && mkdir nohead && cd nohead || exit 1 && git init -q && mkdir -p .claude/hooks && cp "$B"/assets/hooks/* .claude/hooks/ && printf "GATE_FAST='echo r >> ../runs2.log'\n" > .claude/hooks/gates.conf && echo .claude/ > .gitignore && git add .gitignore
echo a > f; git add f; G false >/dev/null; echo b > f; git add f; G false >/dev/null
chk "$(wc -l < ../runs2.log | tr -d ' ')" 2 "repo sem HEAD vê staged"
echo "== $((n-fails))/$n passaram"
cd "$S"
printf "GATE_FAST='false'\nGATE_MAX_RETRIES=2\n" > .claude/hooks/gates.conf; rm -rf .git/prevec
r=""; for i in 1 2 3 4; do echo "m$i" > new.txt; r="$r$(echo '{"session_id":"z"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1; echo $?)"; done
chk "$r" 2202 "sem stop_hook_active nem turn_id: limite vale (2,2,0,2)"
printf "GATE_FAST='trap \"\" TERM; sleep 4813'\nGATE_TIMEOUT=1\n" > .claude/hooks/gates.conf; echo k >> new.txt
s=$(date +%s); r=$(echo '{"session_id":"k"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1; echo $?); e=$(( $(date +%s) - s ))
chk "$([ $e -le 6 ] && echo ok)" ok "comando que ignora TERM leva KILL (${e}s)"; sleep 1
chk "$(pgrep -f '^sleep 4813$' | wc -l | tr -d ' ')" 0 "sem órfão após KILL"
printf "GATE_FAST='kill -TERM \$\$'\nGATE_TIMEOUT=60\n" > .claude/hooks/gates.conf; echo t >> new.txt
msg=$(echo '{"session_id":"t"}' | /bin/bash .claude/hooks/gate.sh 2>&1 >/dev/null | head -1)
chk "$(echo "$msg" | grep -c 'interrompido')" 0 "SIGTERM externo não vira timeout"
printf "GATE_FAST='true'\n" > .claude/hooks/gates.conf
mkdir -p nested && (cd nested && git init -q && echo a > x) && echo z1 > zz.txt
echo '{"session_id":"n"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1
printf "GATE_FAST='false'\n" > .claude/hooks/gates.conf; echo z2 > zz.txt
chk "$(echo '{"session_id":"n2"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1; echo $?)" 2 "repo aninhado não esconde mudança em zz.txt"
printf "GATE_FAST='true'\n" > .claude/hooks/gates.conf; echo q >> zz.txt
s=$(python3 -c 'import time;print(time.time())'); echo '{"session_id":"q"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1
e=$(python3 -c "import time;print(round(time.time()-$s,2))"); chk "$(python3 -c "print('ok' if $e < 2.5 else 'lento')")" ok "gate verde rápido (${e}s)"
echo "== $((n-fails))/$n passaram (com extras)"
printf 'GATE_FAST=%s\n' "'printf \"[%s]\" {changed} > ../changed.txt; true'" > .claude/hooks/gates.conf
echo a > "c 1.txt"; echo b > "d&e.txt"
echo '{"session_id":"c"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1
chk "$(grep -c '\[c 1.txt\]' ../changed.txt)" 1 "{changed}: espaço vira um argumento"
chk "$(grep -c '\[d&e.txt\]' ../changed.txt)" 1 "{changed}: & preservado"
printf "GATE_FAST='date +%%s%%N > art.out; echo r >> ../runs3.log; exit 1'\nGATE_MAX_RETRIES=0\n" > .claude/hooks/gates.conf; rm -f ../runs3.log; echo w >> zz.txt
for i in 1 2 3; do echo '{"session_id":"r"}' | /bin/bash .claude/hooks/gate.sh >/dev/null 2>&1; done
chk "$(wc -l < ../runs3.log | tr -d ' ')" 1 "liberado com artefato não roda de novo"
echo "== $((n-fails))/$n passaram (final)"
# ---------- V10: fila, status, escopo, ritmo, plano, statusline ----------
cd "$S" || exit 1
cat > .claude/hooks/gates.conf <<'EOF2'
GATE_FULL="npm test && npm run build"
TQ_MATCH="pytest|npx vitest run"
ESCOPO=avisar
RITMO_EDITS=2
RITMO_READS=3
STATUS_TASK_MAX=20
EOF2
F() { python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "$1" | /bin/bash .claude/hooks/fila.sh 2>/dev/null | grep -q updatedInput && echo 2 || echo 0; }
chk "$(F 'cd x && npm test && npm run build')" 2 "fila: GATE_FULL vai pela fila"
chk "$(F 'pytest -x -q')" 2 "fila: suíte com flags vai pela fila"
chk "$(F 'FOO=1 pytest')" 2 "fila: variável na frente não escapa"
chk "$(F 'npx vitest run src/a.test.ts')" 0 "fila: teste de um arquivo não espera"
chk "$(F "./.claude/hooks/tq.sh 'pytest'")" 0 "fila: comando já pela fila passa"
chk "$(F 'npx tsc --noEmit')" 0 "fila: comando comum passa"
fo=$(python3 -c 'import json;print(json.dumps({"tool_input":{"command":"npm test && npm run build","description":"d"}}))' | /bin/bash .claude/hooks/fila.sh)
chk "$(echo "$fo" | python3 -c 'import json,sys;t=json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"];print("tq.sh" in t["command"] and t["command"].endswith(" '"'"'npm test && npm run build'"'"'"), t["timeout"], t["description"])')" "True 600000 d" "fila: reescreve pelo tq com timeout e mantém os campos"
chk "$(bash -c "$(echo "$fo" | python3 -c 'import json,sys;print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["command"].replace("npm test && npm run build","echo pela-fila"))')" 2>/dev/null)" pela-fila "fila: comando reescrito roda"
rm -f order.log
for i in 1 2 3; do (.claude/hooks/tq.sh "echo s$i >> order.log; sleep 1; echo e$i >> order.log" 2>/dev/null &); sleep 0.8; done
sleep 4; chk "$(tr '\n' ' ' < order.log)" "s1 e1 s2 e2 s3 e3 " "tq: FIFO sem sobreposição"
.claude/hooks/tq.sh "exit 7" 2>/dev/null; chk "$?" 7 "tq: devolve o código do comando"
chk "$(.claude/hooks/tq.sh ".claude/hooks/tq.sh 'echo aninhado'" 2>/dev/null)" aninhado "tq: chamada aninhada não trava"
(.claude/hooks/tq.sh "sleep 20" 2>/dev/null &); sleep 0.5; pkill -9 -f 'tq.py sleep 20'; pkill -f '^sleep 20$'; sleep 0.3
chk "$(.claude/hooks/tq.sh 'echo livre' 2>/dev/null)" livre "tq: dono morto não prende a fila"
rm -f order.log
mkdir -p src .context/planos; echo a > src/a.ts; echo m > src/m.ts; git add src; git commit -qm src
cat > .context/planos/cpf.md <<'EOF2'
---
feature: cpf
tamanho: médio
status: em-execucao
---
## Fase 1 — x
### T1 — Validar CPF no cadastro de usuário novo · depende: — · estado: ⬜
**A** `src/a.ts` (editar: chama) · `src/cpf.ts` (novo)
**Ref** `src/m.ts:1` (padrão)
**C**
- QUANDO cpf inválido, O SISTEMA DEVE responder 422
**E** `npx vitest run src/cpf.test.ts` → 3 passed
### T2 — Outra · [P] · depende: T9 · estado: ⬜
**A** `src/nao.ts`
**C** nada
**E** sem comando
### T3 — Terceira · [P] · depende: T2 · estado: ⬜
**A** `src/nao.ts` (novo)
**C** - SE x, ENTÃO O SISTEMA DEVE y
**E** `true`
## Pronto quando
- [ ] x
EOF2
PV() { /bin/bash .claude/hooks/prevec.sh "$@"; }
chk "$(PV plano .context/planos/cpf.md | grep -c '^- ')" 5 "plano: acha os 5 problemas"
chk "$(echo '{"tool_name":"Write","tool_input":{"file_path":".context/planos/cpf.md"}}' | PV plano | grep -c additionalContext)" 1 "plano: hook devolve contexto"
J() { python3 -c 'import json,sys;print(json.dumps(json.loads(sys.argv[1])))' "$1" | PV status; }
J '{"session_id":"S1","hook_event_name":"PostToolUse","tool_name":"TaskCreate","tool_input":{"subject":"T1 — Validar","activeForm":"Validando CPF no cadastro de usuário novo"},"tool_response":{"task":{"id":"7"}}}'
J '{"session_id":"S1","hook_event_name":"PostToolUse","tool_name":"TaskUpdate","tool_input":{"taskId":"7","status":"in_progress"}}'
chk "$(grep -c '### T1 .*estado: 🔄' .context/planos/cpf.md)" 1 "status: em andamento marca 🔄 no plano"
J '{"session_id":"S1","hook_event_name":"SubagentStart","agent_id":"a1","agent_type":"executor"}'
sl=$(echo '{"session_id":"S1","model":{"display_name":"Opus"}}' | COLUMNS=60 /bin/bash .claude/hooks/statusline.sh | sed 's/\x1b\[[0-9;]*m//g')
chk "$(echo "$sl" | sed -n 2p | grep -c 'Validando CPF no')" 1 "statusline: tarefa vem do hook"
chk "$(echo "$sl" | sed -n 2p | grep -c 'executor')" 1 "statusline: subagente ativo"
chk "$(echo "$sl" | sed -n 1p | grep -c '^proj')" 1 "statusline: pasta na linha 1"
chk "$(echo "$sl" | python3 -c 'import sys;print(max(len(l) for l in sys.stdin.read().splitlines()) <= 60)')" True "statusline: cabe em COLUMNS"
chk "$(echo '{"session_id":"S1","tool_name":"Edit","tool_input":{"file_path":"src/fora.ts"}}' | PV escopo | grep -c 'fora da seção A')" 1 "escopo: avisa fora do A"
chk "$(echo '{"session_id":"S1","tool_name":"Edit","tool_input":{"file_path":"src/a.ts"}}' | PV escopo | wc -c | tr -d ' ')" 0 "escopo: dentro do A passa calado"
sed -i.bak 's/^ESCOPO=.*/ESCOPO=bloquear/' .claude/hooks/gates.conf && rm -f .claude/hooks/gates.conf.bak
chk "$(echo '{"session_id":"S1","tool_name":"Edit","tool_input":{"file_path":"src/fora.ts"}}' | PV escopo | grep -c '"deny"')" 1 "escopo: bloquear nega"
J '{"session_id":"S1","hook_event_name":"PostToolUse","tool_name":"TaskUpdate","tool_input":{"taskId":"7","status":"completed"}}'
chk "$(grep -c '### T1 .*estado: ✅' .context/planos/cpf.md)" 1 "status: concluída marca ✅ no plano"
R() { echo "{\"session_id\":\"S1\",\"prompt_id\":\"$1\",\"tool_name\":\"Edit\",$3\"tool_input\":{\"file_path\":\"src/$2.ts\"}}" | PV ritmo | grep -c Ritmo; }
chk "$(R p1 a '')$(R p1 b '')$(R p1 c '')" 010 "ritmo: avisa uma vez no limite"
chk "$(R p2 a '"agent_id":"x",')" 0 "ritmo: subagente não conta"
mkdir -p .claude/agents; cp "$B"/assets/agents/executor.md .claude/agents/
chk "$(echo '{"tool_name":"Agent","tool_input":{"subagent_type":"executor","description":"Escrevendo x","prompt":"p"}}' | PV rotulo | grep -c 'Sonnet high · Escrevendo x')" 1 "rotulo: modelo na descrição do subagente"
chk "$(echo '{"tool_name":"Agent","tool_input":{"subagent_type":"executor","model":"opus","effort":"xhigh","description":"x","prompt":"p"}}' | PV rotulo | grep -c 'Opus xhigh · x')" 1 "rotulo: escalada por chamada aparece"
chk "$(echo '{"tool_name":"Agent","tool_input":{"subagent_type":"general-purpose","description":"x","prompt":"p"}}' | PV rotulo | wc -c | tr -d ' ')" 0 "rotulo: agente que herda fica como está"
echo '{"session_id":"S1","tool_input":{"command":"grep -rn \"x\" src/a.ts | head -20"}}' | PV cmdlog
chk "$(cut -f4 "$(git rev-parse --git-path prevec)/cmds.tsv" | tail -1)" "grep -rn S P | head -N" "cmdlog: assinatura sem caminho nem número"
sed -i.bak 's/^status: em-execucao/status: rascunho/' .context/planos/cpf.md; rm -f .context/planos/cpf.md.bak
touch src/cpf.ts; chk "$(PV plano .context/planos/cpf.md | grep -c 'já existe')" 1 "plano: (novo) que já existe acusa no rascunho"
sed -i.bak 's/^status: rascunho/status: em-execucao/' .context/planos/cpf.md; rm -f .context/planos/cpf.md.bak
chk "$(PV plano .context/planos/cpf.md | grep -c 'já existe')" 0 "plano: em execução não acusa (novo) já criado"
sed -i.bak 's/^ESCOPO=.*/ESCOPO=avisar/' .claude/hooks/gates.conf; rm -f .claude/hooks/gates.conf.bak
sed -i.bak 's/^### T3 \(.*\)estado: ⬜/### T3 \1estado: 🔄/' .context/planos/cpf.md; rm -f .context/planos/cpf.md.bak
chk "$(echo '{"session_id":"S2","agent_id":"z","tool_name":"Write","tool_input":{"file_path":"src/nao.ts"}}' | PV escopo | wc -c | tr -d ' ')" 0 "escopo: [P] paralela em 🔄 vale para subagente"
chk "$(F 'npm test 2>&1 | tail -20')" 2 "fila: redirecionamento não esconde a suíte"
chk "$(F 'timeout 100 pytest -k foo')" 2 "fila: prefixo e valor de flag não escondem"
chk "$(F 'pytest tests/test_a.py -x')" 0 "fila: caminho no argumento é teste afetado"
J '{"session_id":"S1","hook_event_name":"PostToolUse","tool_name":"TaskCreate","tool_input":{"subject":"T1 — Validar","status":"pending"}}'
chk "$(grep -c '### T1 .*estado: ✅' .context/planos/cpf.md)" 1 "status: estado nunca regride"
printf '### T9: errado\n' >> .context/planos/cpf.md
chk "$(PV plano .context/planos/cpf.md | grep -c 'fora do formato')" 1 "plano: cabeçalho malformado acusa"
sed -i.bak '/^### T9: errado$/d' .context/planos/cpf.md; rm -f .context/planos/cpf.md.bak
sed -i.bak 's/estado: 🔄/estado: ⬜/' .context/planos/cpf.md; rm -f .context/planos/cpf.md.bak
echo '{"session_id":"S3","tool_name":"Edit","tool_input":{"file_path":"src/nao.ts"}}' | PV pre >/dev/null
chk "$(grep -c '### T2 .*estado: 🔄' .context/planos/cpf.md)" 1 "pre: editar arquivo do A marca a task 🔄"
sl=$(echo '{"session_id":"S3","model":{"display_name":"Opus"}}' | COLUMNS=120 /bin/bash .claude/hooks/statusline.sh | sed 's/\x1b\[[0-9;]*m//g' | sed -n 2p)
chk "$(echo "$sl" | grep -c 'T2 Outra.*editando nao.ts')" 1 "statusline: task inferida e ação em curso"
chk "$(echo '{"session_id":"S3","tool_name":"Edit","tool_input":{"file_path":"src/fora.ts"}}' | PV pre | grep -c 'fora da seção A de T2')" 1 "pre: escopo só com as tasks da sessão"
chk "$(echo '{"session_id":"S4","tool_name":"Edit","tool_input":{"file_path":"src/fora.ts"}}' | PV pre | wc -c | tr -d ' ')" 0 "pre: outra sessão sem task não recebe aviso"
echo '{"session_id":"S5","hook_event_name":"UserPromptSubmit","prompt":"corrige o bug do login\nmais texto"}' | PV status
chk "$(echo '{"session_id":"S5","model":{}}' | /bin/bash .claude/hooks/statusline.sh | sed 's/\x1b\[[0-9;]*m//g' | sed -n 2p | grep -c 'corrige o bug')" 1 "statusline: sem plano mostra o pedido"
for f in a b c d e f; do echo "{\"session_id\":\"S5\",\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"src/$f.ts\"}}" | PV ritmo; done > ritmo.out
chk "$(grep -c Ritmo ritmo.out)" 1 "ritmo: funciona sem prompt_id"; rm -f ritmo.out
U() { python3 -c 'import json,sys;print(json.dumps({"session_id":"S6","hook_event_name":"UserPromptSubmit","prompt":sys.argv[1]}))' "$1" | PV status; python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["pedido"])' "$(git rev-parse --git-path prevec)/status/S6.json"; }
chk "$(U 'blz, agora corrige o login quebrado. Depois roda os testes')" "Corrige o login quebrado" "pedido: primeira frase sem cortesia"
chk "$(U '<task-notification> agente terminou')" "Corrige o login quebrado" "pedido: aviso do sistema não substitui"
mv .context/planos /tmp/planos.$$
echo '{"session_id":"S6","tool_name":"Bash","tool_input":{"command":"bash scripts/deploy.sh --x"}}' | PV pre
chk "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["acao"])' "$(git rev-parse --git-path prevec)/status/S6.json")" "rodando bash deploy.sh" "pre: sem pasta de planos grava a ação com o nome do script"
mv /tmp/planos.$$ .context/planos
echo "== $((n-fails))/$n passaram (V10)"
[ "$fails" -eq 0 ]
