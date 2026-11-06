#!/usr/bin/env bash
# Suíte de regressão dos hooks do V9. Roda só num diretório temporário próprio.
# Uso: bash <kit>/assets/tests/hooks-test.sh
TMP="$(mktemp -d 2>/dev/null)" || { echo "mktemp falhou"; exit 1; }
case "$TMP" in /tmp/*|/private/*|/var/*) ;; *) echo "TMP inesperado: $TMP"; exit 1 ;; esac
trap 'rm -rf "$TMP"' EXIT
S="$TMP/v9 test/proj"
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
[ "$fails" -eq 0 ]
