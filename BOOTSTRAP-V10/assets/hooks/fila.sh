#!/usr/bin/env bash
# PreToolUse em Bash. Suíte pesada (GATE_FULL ou padrão de TQ_MATCH) só roda pela fila tq,
# para dois agentes não rodarem a suíte ao mesmo tempo e travarem a máquina.
# Reescreve o comando para .claude/hooks/tq.sh '<comando>' (updatedInput), sem perder turno.
# Não espera aqui: esperar no hook prenderia o turno e o timeout do hook; a espera acontece
# dentro do tq, sem gastar token.
set -u
. "$(dirname "$0")/_lib.sh"
py_ok || exit 0
[ "${TQ_ON:-1}" = "1" ] || exit 0

cmd="$(json_get tool_input.command)"
[ -n "$cmd" ] || exit 0

hit="$(py -c '
import fnmatch, os, re, shlex, sys
SEP = {"&&", "||", ";", "|", "&", ";;", "(", ")"}

def segments(text):
    """Trechos de comando como listas de tokens. Aspas ficam dentro do token: o ; de uma
    mensagem de commit não abre trecho novo. Comando que não tokeniza: nenhum trecho."""
    try:
        lx = shlex.shlex(text, posix=True, punctuation_chars=True)
        lx.whitespace_split = True
        toks = list(lx)
    except ValueError:
        return []
    out, cur = [], []
    for t in toks:
        if t in SEP:
            if cur: out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur: out.append(cur)
    res = []
    for seg in out:
        clean, skip = [], False
        for i, t in enumerate(seg):
            if skip:
                skip = False; continue
            if t and set(t) <= set("<>&"):          # redirecionamento: some com o alvo
                if clean and clean[-1].isdigit(): clean.pop()
                skip = True; continue
            clean.append(t)
        seg = clean
        changed = True
        while seg and changed:                      # VAR=x, time, nice, env, command, timeout N
            changed = False
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[0]) or seg[0] in ("time", "nice", "env", "command", "exec"):
                seg = seg[1:]; changed = True
            elif seg[0] in ("timeout", "gtimeout") and len(seg) > 1:
                seg = seg[2:]; changed = True
        if seg: res.append(seg)
    return res

def is_path(a):
    if a.startswith("-"):
        return False
    if os.path.exists(a) or "/" in a or "::" in a:
        return True
    return bool(re.search(r"\.(py|ts|tsx|js|jsx|mjs|cjs|php|go|rb|rs|java|kt|cs|swift)$", a))

pats = []
full = sys.argv[2].strip()
if full and not full.startswith("<"):
    pats += [(" ".join(s), "GATE_FULL") for s in segments(full)]
pats += [(" ".join(p.split()), p.strip()) for p in sys.argv[3].split("|") if p.strip() and not p.strip().startswith("<")]
# Cada trecho casa quando começa pelo padrão e nenhum argumento é caminho (pytest -x -k foo).
# Com arquivo ou pasta no argumento (pytest tests/a.py) é teste afetado e não passa pela fila.
# Redirecionamento (2>&1, > log) e prefixos (time, timeout 100, VAR=x) não escondem a suíte.
for seg in segments(sys.argv[1]):
    if os.path.basename(seg[0]) in ("tq.sh", "tq.py") or (len(seg) > 1 and os.path.basename(seg[1]) == "tq.py"):
        continue
    joined = " ".join(seg)
    for pat, name in pats:
        ptoks = pat.split()
        if fnmatch.fnmatchcase(joined, pat):
            print(name); sys.exit()
        if seg[:len(ptoks)] == ptoks and not any(is_path(a) for a in seg[len(ptoks):]):
            print(name); sys.exit()
' "$cmd" "${GATE_FULL:-}" "${TQ_MATCH:-}")"
[ -n "$hit" ] || exit 0

# Reescreve o comando para passar pela fila (updatedInput): o agente não perde turno.
# A reescrita exige permissionDecision "allow"; o comando é o mesmo que o agente pediu.
# Foreground ganha timeout de 10 minutos (o padrão de 2 mataria a suíte na espera).
py -c '
import json, shlex, sys
d = json.loads(sys.argv[1] or "{}")
ti = dict(d.get("tool_input") or {})
tq = sys.argv[2] + "/.claude/hooks/tq.sh"
ti["command"] = shlex.quote(tq) + " " + shlex.quote(ti.get("command") or "")
if not ti.get("run_in_background"):
    try:
        cur = int(ti.get("timeout") or 0)
    except (TypeError, ValueError):
        cur = 0
    ti["timeout"] = max(cur, 600000)
msg = ("Suíte pesada (" + sys.argv[3] + ") rodando pela fila de testes: uma por vez neste repositório. "
       "Se a fila estiver ocupada, o comando espera a vez sozinho; não rode a suíte de novo. "
       "Durante uma task, rode só o teste afetado.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                  "permissionDecisionReason": msg, "updatedInput": ti, "additionalContext": msg}},
                 ensure_ascii=False))
' "$INPUT" "$ROOT" "$hit"
exit 0
