#!/usr/bin/env python3
"""Hooks do PREVEC V10 que precisam ler estado. Chamado por prevec.sh <comando>.

  status   PostToolUse (TaskCreate|TaskUpdate|TodoWrite|Agent|Task), SubagentStart, SubagentStop,
           UserPromptSubmit. Grava o pedido atual, a tarefa nativa (quando a ferramenta tem) e
           os subagentes ativos; subagente que volta "VEREDITO: ok" fecha a task (✅) no plano.
  pre      PreToolUse em edição, Bash, leitura e Agent. Grava a ação em curso para a
           statusline ("editando cli.py", "testando"), infere a task do plano pelo arquivo
           editado ou pelo código T<n> na descrição do subagente e a marca 🔄, roda o escopo
           (edição) e o rótulo (Agent). O modelo não precisa lembrar de atualizar nada.
  ritmo    PostToolUse no thread principal. Avisa uma vez por turno quando o turno cresce
           (muitas edições ou muitas leituras) para o agente pesar se delega.
  escopo   PreToolUse em edição. Compara o arquivo com a seção A da task ativa do plano.
  cmdlog   PostToolUse em Bash. Registra a assinatura do comando (sem caminhos nem números)
           para a skill retro achar trabalho manual repetido que vale virar script ou skill.
  rotulo   PreToolUse no tool Agent. Põe o modelo na frente da descrição do subagente
           ("Sonnet · Escrevendo testes"), para a lista de agentes mostrar quem roda onde.
  marca    Linha de comando: prevec.sh marca T3 [ok|andamento]. Única forma de mudar o estado
           à mão; editar o estado no plano disputa com o hook.
  plano    PostToolUse em Write/Edit de .context/planos/*.md ou .context/work/*.md, ou na linha de comando
           (prevec.sh plano <arquivo>). Checa o plano de forma determinística.

Regra geral: hook de estado nunca bloqueia nem quebra o turno. Erro inesperado sai 0 calado.
"""
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import time

TASK_CODE = re.compile(r"^\s*(T\d+(?:\.\d+)*)\b")
HEAD = re.compile(r"^###\s+(T\d+(?:\.\d+)*)\s*[—–-]\s*(.*)$")
STATES = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}


# ---------- utilidades ----------

def read_input():
    try:
        d = json.loads(sys.stdin.read() or "{}")
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def git(root, *args):
    try:
        r = subprocess.run(["git", "--no-optional-locks", "-C", root, *args],
                           capture_output=True, text=True, timeout=3)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def project_root(d):
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if root:
        return root
    cwd = d.get("cwd") if isinstance(d.get("cwd"), str) else os.getcwd()
    return git(cwd, "rev-parse", "--show-toplevel") or cwd


def state_dir(root):
    p = git(root, "rev-parse", "--git-path", "prevec") or os.path.join(".git", "prevec")
    if not os.path.isabs(p):
        p = os.path.join(root, p)
    os.makedirs(os.path.join(p, "status"), exist_ok=True)
    return p


def safe_id(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(s or "sem-sessao"))[:80]


def load(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def save(path, data):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    os.replace(tmp, path)


@contextlib.contextmanager
def locked(path):
    """Serializa load→save do mesmo arquivo de estado entre hooks paralelos (subagentes)."""
    fd = os.open(path + ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def emit(event, context=None, decision=None, reason=None):
    out = {"hookEventName": event}
    if context:
        out["additionalContext"] = context
    if decision:
        out["permissionDecision"] = decision
        out["permissionDecisionReason"] = reason or context or ""
    print(json.dumps({"hookSpecificOutput": out}, ensure_ascii=False))


def find_key(obj, keys, depth=0):
    if depth > 4:
        return None
    if isinstance(obj, dict):
        for k in keys:
            v = obj.get(k)
            if isinstance(v, (str, int)) and not isinstance(v, bool) and str(v):
                return str(v)
        for v in obj.values():
            r = find_key(v, keys, depth + 1)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, keys, depth + 1)
            if r:
                return r
    elif isinstance(obj, str) and depth == 0:
        try:
            return find_key(json.loads(obj), keys, depth + 1)
        except Exception:
            m = re.search(r"#?(\d+)", obj)
            return m.group(1) if m else None
    return None


def rel(root, p, base=None):
    if not isinstance(p, str) or not p:
        return ""
    if not os.path.isabs(p):
        p = os.path.join(base or root, p)
    return os.path.relpath(os.path.normpath(p), os.path.normpath(root))


# ---------- plano ----------

def active_plan(root, code=None):
    """Plano em execução mais recente; com code, o mais recente que tem essa task."""
    for f in active_plans(root):
        if not code:
            return f
        try:
            with open(f, encoding="utf-8") as fh:
                if re.search(rf"^###\s+{re.escape(code)}\s*[—–-]", fh.read(), re.M):
                    return f
        except OSError:
            continue
    return None


def plan_files(root, sub):
    d = os.path.join(root, ".context", sub)
    try:
        return [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md") and not f.startswith("_")]
    except OSError:
        return []


def active_plans(root):
    """Planos em execução: todo plano em .context/work/ e, por compatibilidade, os de
    .context/planos/ com status em-execucao. Mais recente primeiro."""
    files = plan_files(root, "work")
    for f in plan_files(root, "planos"):
        try:
            with open(f, encoding="utf-8") as fh:
                head = fh.read(600)
        except OSError:
            continue
        if re.search(r"^status:\s*(em-execucao|em-execução)", head, re.M):
            files.append(f)
    return sorted(files, key=os.path.getmtime, reverse=True)


def parse_plan(text):
    """Devolve (frontmatter, tasks). Cada task: code, title, line, fase, flags, deps, body."""
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    tasks, cur, fase, bad = [], None, None, []
    for i, line in enumerate(text.splitlines()):
        if line.startswith("## "):
            fm_f = re.match(r"^##\s+Fase\s+(\S+)", line)
            fase = fm_f.group(1) if fm_f else fase
            if cur:
                tasks.append(cur)
                cur = None
            continue
        h = HEAD.match(line)
        if not h and re.match(r"^###\s+T", line):
            bad.append(line.strip()[:60])
        if h:
            if cur:
                tasks.append(cur)
            meta = h.group(2)
            dep = re.search(r"depende:\s*([^·]+)", meta)
            deps = re.findall(r"T\d+(?:\.\d+)*", dep.group(1)) if dep else []
            cur = {"code": h.group(1), "title": meta.split("·")[0].strip(), "line": i,
                   "fase": fase, "par": "[P]" in meta, "deps": deps, "body": []}
            continue
        if cur is not None:
            cur["body"].append(line)
    if cur:
        tasks.append(cur)
    fm["_bad"] = bad
    return fm, tasks


def field(body, letter):
    """Linhas do campo **X** até o próximo campo em negrito."""
    out, on = [], False
    for line in body:
        s = line.strip()
        if re.match(r"^\*\*[^*]+\*\*", s):
            on = s.startswith(f"**{letter}**")
            if on:
                out.append(s[len(letter) + 4:])
            continue
        if on:
            out.append(line)
    return out


def a_paths(body):
    """(caminho, marca) da seção A. Marca: novo, editar, apagar ou ''."""
    res = []
    for line in field(body, "A"):
        if re.match(r"^\s*(Ref|Referência)\s*:", line.strip(), re.I):
            continue
        found = list(re.finditer(r"`(?P<p>[^`]+)`\s*(?:\((?P<n>[^)]*)\))?", line))
        if not found:  # caminho sem crase: "- app/Http/X.php (editar, criado na T9)"
            found = list(re.finditer(
                r"(?<![\w/.-])(?P<p>(?:[\w.-]+/)+[\w.-]+|[\w-]+(?:\.[\w-]+)*\.[a-z]{2,5})(?![\w(])\s*(?:\((?P<n>[^)]*)\))?", line))
        for m in found:
            path = m.group("p").strip().rstrip(".,;:")
            if " " in path or ("/" not in path and "." not in path) or re.match(r"^[\d.]+$", path):
                continue  # comando, símbolo ou número, não caminho
            mark = re.split(r"[:,—;\s]", (m.group("n") or "").strip().lower(), maxsplit=1)[0]
            res.append((path, mark))
    return res


def ref_paths(body):
    res = []
    for line in body:
        mm = re.match(r"^\**(Ref|Referência)\**\s*:?\s*(.*)$", line.strip(), re.I)
        if mm:
            res += [re.sub(r":[\d,-]+$", "", p) for p in re.findall(r"`([^`]+)`", mm.group(2))]
    return res


def suggest_plan(path):
    """Dependência que talvez não exista: as tasks não dividem arquivo e a dependente não cita
    nenhum arquivo da outra. Só sugestão: a dependência pode ser de comportamento."""
    try:
        with open(path, encoding="utf-8") as fh:
            _, tasks = parse_plan(fh.read())
    except OSError:
        return []
    by = {t["code"]: t for t in tasks}
    out = []
    for t in tasks:
        mine = {p for p, _ in a_paths(t["body"])}
        text = "\n".join(t["body"])
        for dep in t["deps"]:
            dt = by.get(dep)
            if not dt:
                continue
            theirs = {p for p, _ in a_paths(dt["body"])}
            stems = {os.path.splitext(os.path.basename(p))[0] for p in theirs}
            if theirs and not (mine & theirs) and not any(s and s in text for s in stems):
                out.append(f"{t['code']} depende de {dep}, mas não divide arquivo nem cita arquivo dela: "
                           f"se não usa nada que {dep} cria, tire a dependência (e marque [P] se couber)")
    return out


def check_plan(root, path):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        return [f"não abriu {path}: {e}"]
    fm, tasks = parse_plan(text)
    probs = []
    for k in ("feature", "status"):
        if k not in fm:
            probs.append(f"frontmatter sem `{k}`")
    for b in fm.get("_bad", []):
        probs.append(f"cabeçalho fora do formato `### T1 — título · depende: — · estado: ⬜`: {b}")
    if not tasks:
        probs.append("nenhuma task no formato `### T1 — título · depende: — · estado: ⬜`")
    if not re.search(r"^##\s+Pronto quando", text, re.M):
        probs.append("falta a seção `## Pronto quando` (critério da feature, não a soma das tasks)")
    codes = {t["code"] for t in tasks}
    # arquivo (novo) já criado não é erro durante a execução
    executing = fm.get("status", "").startswith("em-execu") or os.sep + "work" + os.sep in os.path.abspath(path)
    seen = set()
    for t in tasks:
        c = t["code"]
        if c in seen:
            probs.append(f"{c}: código repetido")
        seen.add(c)
        paths = a_paths(t["body"])
        if not paths:
            probs.append(f"{c}: **A** sem arquivo exato entre crases")
        for p, mark in paths:
            full = os.path.join(root, p)
            if any(ch in p for ch in "*?"):
                probs.append(f"{c}: `{p}` é padrão; a seção A lista arquivos exatos")
            elif mark.startswith("novo"):
                if os.path.exists(full) and not executing:
                    probs.append(f"{c}: `{p}` marcado (novo) mas já existe")
            elif not os.path.exists(full):
                probs.append(f"{c}: `{p}` não existe; marque (novo) ou corrija o caminho")
        for r in ref_paths(t["body"]):
            if not os.path.exists(os.path.join(root, r)):
                probs.append(f"{c}: referência `{r}` não existe")
        cl = [l for l in field(t["body"], "C") if l.strip()]
        if not any(re.search(r"\b(WHEN|IF|WHILE|WHERE|QUANDO|SE|ENQUANTO|ONDE)\b", l) for l in cl):
            probs.append(f"{c}: **C** sem cláusula EARS (QUANDO/SE … O SISTEMA DEVE …)")
        el = " ".join(field(t["body"], "E"))
        if "`" not in el:
            probs.append(f"{c}: **E** sem comando entre crases")
        for dep in t["deps"]:
            if dep not in codes:
                probs.append(f"{c}: depende de {dep}, que não existe")
    # ciclo
    graph = {t["code"]: t["deps"] for t in tasks}
    state = {}

    def visit(n, stack):
        state[n] = 1
        for m in graph.get(n, []):
            if state.get(m) == 1:
                probs.append(f"dependência circular: {' → '.join(stack + [m])}")
            elif m in graph and not state.get(m):
                visit(m, stack + [m])
        state[n] = 2

    for n in graph:
        if not state.get(n):
            visit(n, [n])
    # [P] na mesma fase não divide arquivo
    by_fase = {}
    for t in tasks:
        if t["par"]:
            by_fase.setdefault(t["fase"], []).append(t)
    for group in by_fase.values():
        owner = {}
        for t in group:
            for p, _ in a_paths(t["body"]):
                if p in owner and owner[p] != t["code"]:
                    probs.append(f"{t['code']} e {owner[p]} são [P] e tocam `{p}`: tire o [P] de uma ou separe o arquivo")
                owner.setdefault(p, t["code"])
    return probs


def mark_plan(root, code, symbol):
    plan = active_plan(root, code)
    if not plan or not code:
        return
    with locked(plan):
        _mark_plan(plan, code, symbol)


RANK = {"⬜": 0, "🔄": 1, "✅": 2}


def _mark_plan(plan, code, symbol):
    try:
        with open(plan, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return
    changed = False
    for i, line in enumerate(lines):
        h = HEAD.match(line)
        if h and h.group(1) == code:
            old = re.search(r"estado:\s*(\S+)", line)
            if old and RANK.get(old.group(1), 0) >= RANK.get(symbol, 0):
                break  # estado nunca regride (TaskCreate pending de task já feita, retomada)
            if old:
                new = re.sub(r"estado:\s*\S+", f"estado: {symbol}", line)
            else:
                new = f"{line} · estado: {symbol}"
            if new != line:
                lines[i], changed = new, True
            break
    if changed:
        tmp = f"{plan}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        os.replace(tmp, plan)


# ---------- modelo do subagente ----------

FAMILIES = ("opus", "sonnet", "haiku", "fable")


def agent_model(root, agent_type, override=None, effort_override=None):
    """Rótulo curto do modelo: 'Sonnet', 'Opus 1M', 'Haiku'. None quando herda e não dá para saber."""
    model, effort = override, None
    if agent_type and re.match(r"^[A-Za-z0-9_.-]+$", agent_type):
        for base in (os.path.join(root, ".claude", "agents"), os.path.join(os.path.expanduser("~"), ".claude", "agents")):
            try:
                with open(os.path.join(base, agent_type + ".md"), encoding="utf-8") as fh:
                    head = fh.read(3000)
            except OSError:
                continue
            fm = re.match(r"^---\n(.*?)\n---", head, re.S)
            if fm:
                m = re.search(r"^model:\s*(\S+)", fm.group(1), re.M)
                e = re.search(r"^effort:\s*(\S+)", fm.group(1), re.M)
                model = model or (m.group(1) if m else None)
                effort = e.group(1) if e else None
            break
    if not model and agent_type in ("Explore", "explore"):
        model = os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL") or "haiku"
    if not model or model == "inherit":
        return None
    low = model.lower()
    fam = next((f for f in FAMILIES if f in low), None)
    label = fam.capitalize() if fam else model[:20]
    if "[1m]" in low or "1m" in low.split("-")[-1:]:
        label += " 1M"
    effort = effort_override or effort
    return label + (f" {effort}" if effort else "")


def signature(cmd):
    """Comando sem o que varia (caminho, número, texto entre aspas): mesma ação, mesma assinatura."""
    c = " ".join(cmd.split())[:300]
    c = re.sub(r"(['\"]).*?\1", "S", c)
    c = re.sub(r"\S*/\S*", "P", c)
    c = re.sub(r"\b\d+\b", "N", c)
    return c[:160]


def cmd_cmdlog(d, root):
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    cmd = ti.get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        return
    sd = state_dir(root)
    path = os.path.join(sd, "cmds.tsv")
    try:
        if os.path.getsize(path) > 2_000_000:  # mantém só a metade recente
            with open(path, encoding="utf-8") as fh:
                keep = fh.readlines()[-5000:]
            with open(path, "w", encoding="utf-8") as fh:
                fh.writelines(keep)
    except OSError:
        pass
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\t".join([time.strftime("%Y-%m-%dT%H:%M:%S"), safe_id(d.get("session_id")),
                            d.get("agent_type") or "main", signature(cmd)]) + "\n")


TEST_HINT = re.compile(r"\b(test|tests|pytest|unittest|vitest|jest|phpunit|pest|go test|rspec|mocha|tq\.sh)\b")


def describe(tool, ti, root, cwd):
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        p = rel(root, ti.get("file_path") or ti.get("notebook_path") or "", cwd)
        verb = "criando" if tool == "Write" and not os.path.exists(os.path.join(root, p)) else "editando"
        return f"{verb} {os.path.basename(p)}"
    if tool == "Bash":
        cmd = " ".join(str(ti.get("command") or "").split())
        if "tq.sh" in cmd:
            return "suíte na fila"
        if TEST_HINT.search(cmd):
            return "testando"
        if cmd.startswith("git commit"):
            return "commitando"
        parts = cmd.split(" ")
        word = parts[0] if parts else ""
        if word in ("bash", "sh", "zsh", "python3", "python", "node", "npx", "pnpm", "npm", "yarn", "php", "uv", "make") and len(parts) > 1:
            nxt = next((p for p in parts[1:] if not p.startswith("-")), "")
            word = f"{os.path.basename(word)} {os.path.basename(nxt)}".strip()
        else:
            word = os.path.basename(word)
        return f"rodando {word[:30]}" if word else None
    if tool in ("Read", "Grep", "Glob"):
        return "lendo"
    if tool in ("Agent", "Task"):
        return f"delegando: {str(ti.get('description') or '')[:40]}"
    return None


def plan_tasks(root):
    plan = active_plan(root)
    if not plan:
        return None, None, []
    try:
        with open(plan, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return None, None, []
    _, tasks = parse_plan("\n".join(lines))
    return plan, lines, tasks


def cmd_pre(d, root):
    tool = d.get("tool_name") or ""
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    cwd = d.get("cwd")
    sd = state_dir(root)
    path = os.path.join(sd, "status", safe_id(d.get("session_id")) + ".json")
    mark = None
    with locked(path):
        st = load(path, {})
        st.setdefault("e_ran", {})
        act = describe(tool, ti, root, cwd)
        if act and not d.get("agent_id"):
            st["acao"] = act
            st["acao_t"] = time.time()
        plan, lines, tasks = plan_tasks(root)
        code = None
        if plan and tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
            p = rel(root, ti.get("file_path") or ti.get("notebook_path") or "", cwd)
            for t in tasks:
                if "✅" in lines[t["line"]]:
                    continue
                if p in [a for a, _ in a_paths(t["body"])]:
                    code = t["code"]
                    break
        elif plan and tool in ("Agent", "Task"):
            m = re.search(r"\b(T\d+(?:\.\d+)*)\b", str(ti.get("description") or ""))
            if m and any(t["code"] == m.group(1) for t in tasks):
                code = m.group(1)
        elif plan and tool == "Bash" and st.get("plan_cur"):
            cmd = " ".join(str(ti.get("command") or "").split())
            cur = next((t for t in tasks if t["code"] == st["plan_cur"]), None)
            if cur:
                ecmd = re.findall(r"`([^`]+)`", " ".join(field(cur["body"], "E")))
                if ecmd and " ".join(ecmd[0].split()) in cmd:
                    st["e_ran"][cur["code"]] = True
        if code and not d.get("agent_id"):
            st["ativos"] = sorted(set(st.get("ativos") or []) | {code})
        if code and code != st.get("plan_cur") and not d.get("agent_id") and tool not in ("Agent", "Task"):
            prev = st.get("plan_cur")
            st["plan_cur"] = code
            if prev and st["e_ran"].get(prev):
                st["ativos"] = [c for c in st["ativos"] if c != prev]
                mark = (prev, code)
            else:
                mark = (None, code)
        st["plan"] = os.path.relpath(plan, root) if plan else None
        save(path, st)
    if mark:
        if mark[0]:
            mark_plan(root, mark[0], "✅")
        mark_plan(root, mark[1], "🔄")
    elif code and tool in ("Agent", "Task"):
        mark_plan(root, code, "🔄")
        with locked(path):  # SubagentStart liga este código ao agent_id; SubagentStop fecha a task
            st2 = load(path, {})
            st2["pend"] = (st2.get("pend") or [])[-9:] + [code]
            save(path, st2)
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit") or (tool == "apply_patch"):
        cmd_escopo(d, root)
    elif tool in ("Agent", "Task"):
        cmd_rotulo(d, root)


def cmd_rotulo(d, root):
    if (d.get("tool_name") or "") not in ("Agent", "Task"):
        return
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    desc = ti.get("description")
    if not isinstance(desc, str):
        return
    label = agent_model(root, ti.get("subagent_type") or "", ti.get("model"), ti.get("effort"))
    if not label or desc.lower().startswith(label.split()[0].lower()):
        return
    new = dict(ti)
    new["description"] = f"{label} · {desc}"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                             "updatedInput": new}}, ensure_ascii=False))


FILLER = re.compile(r"^(por favor|pf|agora|então|entao|ok|beleza|blz|show|certo|bom|olá|ola|oi)[,.!: ]+", re.I)


def resumo(text, n=60):
    """Primeira frase do pedido, sem cortesia, cortada em palavra inteira."""
    t = re.sub(r"\s+", " ", text).strip()
    while True:
        u = FILLER.sub("", t)
        if u == t:
            break
        t = u
    t = re.split(r"(?<=[.!?;])\s", t, maxsplit=1)[0].rstrip(".!;")
    if len(t) > n:
        t = t[:n].rsplit(" ", 1)[0]
    return t[:1].upper() + t[1:]


# ---------- comandos ----------

def cmd_status(d, root):
    sd = state_dir(root)
    path = os.path.join(sd, "status", safe_id(d.get("session_id")) + ".json")
    with locked(path):
        touched, tasks, detalhe = _status(d, root, sd, path)
    if detalhe:
        emit("UserPromptSubmit", context=(
            "Modo técnico nesta resposta: o usuário pediu detalhe. Comece pela conclusão e depois dê "
            "funções, trechos de código, alternativas consideradas e o porquê da escolha. "
            "Na próxima resposta, volte ao formato em camadas."))
    if touched and touched in tasks:
        m = TASK_CODE.match(tasks[touched].get("subject") or "")
        sym = STATES.get(tasks[touched].get("status"))
        if m and sym:
            mark_plan(root, m.group(1), sym)


def _status(d, root, sd, path):
    st = load(path, {})
    st.setdefault("tasks", {})
    st.setdefault("agents", {})
    ev = d.get("hook_event_name") or ""
    tool = d.get("tool_name") or ""
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    if os.environ.get("PREVEC_DEBUG") == "1":
        with open(os.path.join(sd, "status", "debug.log"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({k: d.get(k) for k in ("hook_event_name", "tool_name", "tool_input",
                                                       "tool_response", "agent_id", "agent_type")},
                                ensure_ascii=False)[:4000] + "\n")
    touched = None
    # SubagentStop perdido não deixa agente fantasma: some depois de 30 minutos.
    st["agents"] = {k: v for k, v in st["agents"].items() if time.time() - v.get("t", 0) < 1800}
    if ev in ("SubagentStart", "SubagentStop"):
        # Registro curto para diagnosticar subagente que não aparece (só nomes de campo e ids).
        with open(os.path.join(sd, "status", "agentes.log"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ev": ev, "sid": d.get("session_id"), "agent_id": d.get("agent_id"),
                                 "agent_type": d.get("agent_type"), "campos": sorted(d.keys())},
                                ensure_ascii=False) + "\n")
    if ev == "UserPromptSubmit":
        st["turno"] = int(st.get("turno") or 0) + 1
        prompt = d.get("prompt") if isinstance(d.get("prompt"), str) else ""
        first = next((l.strip() for l in prompt.splitlines() if l.strip()), "")
        # Aviso do sistema (<task-notification>, <system-reminder>) não é pedido do usuário.
        if first and not first.startswith("<"):
            st["pedido"] = resumo(first)
            st["acao"] = None
        # "detalhe" no começo do pedido (ou pedido curto com a palavra): modo técnico só nesta resposta.
        low = prompt.strip().lower()
        if os.environ.get("DETALHE_HOOK", "1") == "1" and (
                re.match(r"^(detalh|t[eé]cnico\b|como funciona por dentro)", low)
                or (len(low) <= 60 and re.search(r"\b(detalh\w*|t[eé]cnico)\b", low))):
            st["_detalhe"] = True
    elif tool in ("Agent", "Task") and ev == "PostToolUse":
        resp = d.get("tool_response")
        text = resp if isinstance(resp, str) else json.dumps(resp, ensure_ascii=False)
        m = TASK_CODE.match(str(ti.get("description") or "")) or re.search(r"\b(T\d+(?:\.\d+)*)\b", str(ti.get("description") or ""))
        if m and re.search(r"VEREDITO:\s*ok", text or "", re.I):
            st["fechar"] = m.group(1)
    elif ev == "SubagentStart":
        aid = d.get("agent_id") or str(time.time())
        typ = d.get("agent_type") or "subagente"
        lab = agent_model(root, typ)
        pend = st.get("pend") or []
        st["agents"][aid] = {"type": f"{typ}·{lab.split()[0]}" if lab else typ, "t": time.time(),
                             "code": pend.pop(0) if pend else None}
        st["pend"] = pend
    elif ev == "SubagentStop":
        # Background também fecha: o SubagentStop traz a última mensagem do subagente.
        ag = st["agents"].get(d.get("agent_id") or "") or {}
        msg = d.get("last_assistant_message") if isinstance(d.get("last_assistant_message"), str) else ""
        m = re.search(r"^\W*TASK:\s*(T\d+(?:\.\d+)*)", msg, re.M | re.I)
        code = (m.group(1) if m else None) or ag.get("code")
        if code and re.search(r"VEREDITO:\W*ok\b", msg, re.I):
            st["fechar"] = code
        st["agents"].pop(d.get("agent_id") or "", None)
        if not d.get("agent_id") and st["agents"]:
            st["agents"].pop(sorted(st["agents"], key=lambda k: st["agents"][k].get("t", 0))[0], None)
    elif tool == "TodoWrite":
        todos = ti.get("todos") if isinstance(ti.get("todos"), list) else []
        st["tasks"] = {}
        for i, t in enumerate(todos):
            if isinstance(t, dict):
                st["tasks"][str(i)] = {"subject": t.get("content") or "", "active": t.get("activeForm") or "",
                                       "status": t.get("status") or "pending", "t": time.time() + i / 1000}
    elif tool == "TaskCreate":
        st["seq"] = int(st.get("seq") or 0) + 1
        tid = find_key(d.get("tool_response"), ("id", "taskId", "task_id")) or f"c{st['seq']}"
        st["tasks"][tid] = {"subject": ti.get("subject") or ti.get("content") or "",
                            "active": ti.get("activeForm") or "", "status": ti.get("status") or "pending",
                            "t": time.time()}
        touched = tid
    elif tool == "TaskUpdate":
        tid = str(ti.get("taskId") or ti.get("task_id") or ti.get("id") or "")
        if tid and tid not in st["tasks"] and isinstance(ti.get("subject"), str):
            # id desconhecido (resposta do TaskCreate sem id): casa pelo assunto
            tid = next((k for k, v in st["tasks"].items() if v.get("subject") == ti["subject"]), tid)
        if tid:
            t = st["tasks"].setdefault(tid, {"subject": "", "active": "", "status": "pending"})
            if ti.get("status") == "deleted":
                st["tasks"].pop(tid, None)
            else:
                for src, dst in (("subject", "subject"), ("activeForm", "active"), ("status", "status")):
                    if isinstance(ti.get(src), str) and ti[src]:
                        t[dst] = ti[src]
                t["t"] = time.time()
                touched = tid
    # tarefa atual: a em andamento mais recente
    tasks = st["tasks"]
    doing = sorted((k for k, v in tasks.items() if v.get("status") == "in_progress"),
                   key=lambda k: tasks[k].get("t", 0), reverse=True)
    if doing:
        cur = tasks[doing[0]]
        m = TASK_CODE.match(cur.get("subject") or "")
        st["current"] = {"text": cur.get("active") or cur.get("subject") or "",
                         "code": m.group(1) if m else "", "subject": cur.get("subject") or ""}
    else:
        st["current"] = None
    st["done"] = sum(1 for v in tasks.values() if v.get("status") == "completed")
    st["total"] = len(tasks)
    st["updated"] = time.time()
    fechar = st.pop("fechar", None)
    detalhe = st.pop("_detalhe", False)
    save(path, st)
    if fechar:
        mark_plan(root, fechar, "✅")
    return touched, tasks, detalhe


def cmd_ritmo(d, root):
    if d.get("agent_id"):
        return
    sd = state_dir(root)
    path = os.path.join(sd, "status", safe_id(d.get("session_id")) + ".ritmo.json")
    with locked(path):
        msg = _ritmo(d, root, path)
    if msg:
        emit("PostToolUse", context=msg)


def _ritmo(d, root, path):
    turn = str(d.get("prompt_id") or "")
    if not turn:  # sem prompt_id: o contador de turno que o status grava no UserPromptSubmit
        sp = path.replace(".ritmo.json", ".json")
        turn = "t" + str(load(sp, {}).get("turno") or 0)
    st = load(path, {})
    if not turn or st.get("turn") != turn:
        st = {"turn": turn, "edits": [], "reads": 0, "warned": []}
    tool = d.get("tool_name") or ""
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        p = rel(root, ti.get("file_path") or ti.get("notebook_path") or "", d.get("cwd"))
        if p and p not in st["edits"]:
            st["edits"].append(p)
    elif tool in ("Read", "Grep", "Glob"):
        st["reads"] += 1
    max_e = int(os.environ.get("RITMO_EDITS", "5") or 0)
    max_r = int(os.environ.get("RITMO_READS", "15") or 0)
    msg = None
    if max_e and len(st["edits"]) >= max_e and "e" not in st["warned"]:
        st["warned"].append("e")
        msg = (f"Ritmo: este turno já editou {len(st['edits'])} arquivos no thread principal. "
               "Pese: se o que falta são partes independentes ou trabalho mecânico, delegue com o pedido completo "
               "(skill delegar: arquivos, referência, o que já sabemos, prova). Se falta pouco e está acoplado, siga.")
    elif max_r and st["reads"] >= max_r and not st["edits"] and "r" not in st["warned"]:
        st["warned"].append("r")
        msg = (f"Ritmo: {st['reads']} leituras neste turno sem editar. Se já sabe o bastante, decida e execute. "
               "Se ainda falta mapear muita coisa, mande o explorador e receba só a conclusão.")
    save(path, st)
    return msg


def cmd_escopo(d, root):
    mode = (os.environ.get("ESCOPO") or "avisar").lower()
    if mode in ("off", "desligado", "0", ""):
        return
    plan = active_plan(root)
    if not plan:
        return
    try:
        with open(plan, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return
    _, tasks = parse_plan("\n".join(lines))
    # Tasks ativas: as 🔄 do plano (o hook de status marca, inclusive [P] em paralelo) e a
    # atual da sessão. Subagente paralelo pode editar o A de qualquer task ativa.
    sd = state_dir(root)
    st = load(os.path.join(sd, "status", safe_id(d.get("session_id")) + ".json"), {})
    cur = st.get("current") if isinstance(st.get("current"), dict) else {}
    # Só as tasks desta sessão: plano esquecido de outra sessão não gera aviso em fix pontual.
    mine = set(st.get("ativos") or []) | {cur.get("code"), st.get("plan_cur")}
    active = [t for t in tasks if t["code"] in mine and "✅" not in lines[t["line"]]]
    if not active:
        return
    allowed = [p for t in active for p, _ in a_paths(t["body"])]
    if not allowed:
        return
    code = "/".join(t["code"] for t in active)
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    paths = [ti.get(k) for k in ("file_path", "notebook_path", "path") if isinstance(ti.get(k), str)]
    cmd = ti.get("command") if isinstance(ti.get("command"), str) else ""
    paths += re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", cmd, re.M)
    import fnmatch
    out = []
    for p in paths:
        r = rel(root, p.strip(), d.get("cwd"))
        if r.startswith(".context/") or r.startswith(".."):
            continue
        if not any(r == a or fnmatch.fnmatchcase(r, a) or (a.endswith("/") and r.startswith(a)) for a in allowed):
            out.append(r)
    if not out:
        return
    plan_rel = os.path.relpath(plan, root)
    msg = (f"Escopo: {', '.join(out)} está fora da seção A de {code} ({plan_rel}). "
           f"Se a edição é necessária, acrescente o arquivo ao A de {code} com o motivo em uma linha; "
           "se não é, não edite.")
    if mode in ("bloquear", "block"):
        emit("PreToolUse", decision="deny", reason=msg)
    else:
        emit("PreToolUse", context=msg)


def cmd_plano(d, root, argv):
    if argv:
        probs = check_plan(root, argv[0])
        for p in probs:
            print(f"- {p}")
        for s in suggest_plan(argv[0]):
            print(f"  sugestão: {s}")
        print("plano ok" if not probs else f"{len(probs)} problema(s)")
        return 1 if probs else 0
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    cands = [ti.get("file_path")] if isinstance(ti.get("file_path"), str) else []
    cmd = ti.get("command") if isinstance(ti.get("command"), str) else ""
    cands += re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", cmd, re.M)  # apply_patch do Codex
    p = next((q for q in (rel(root, c.strip(), d.get("cwd")) for c in cands)
              if re.match(r"^\.context/(planos|work)/[^/_][^/]*\.md$", q)), None)
    if not p:
        return 0
    probs = check_plan(root, os.path.join(root, p))
    sug = suggest_plan(os.path.join(root, p))
    ctx = ""
    if probs:
        ctx = (f"Checagem do plano {p} ({len(probs)}):\n- " + "\n- ".join(probs[:15])
               + "\nCorrija antes de executar: task com decisão pendente vira retrabalho na execução.")
    if sug:
        ctx += ("\n" if ctx else f"Plano {p}: ") + "Sugestões (confira, não são erro):\n- " + "\n- ".join(sug[:8])
    if ctx:
        emit("PostToolUse", context=ctx)
    return 0


def cmd_marca(root, rest):
    """prevec.sh marca T3 [ok|andamento]: marca a task pelo mesmo caminho do hook (com trava),
    para o agente não editar o estado à mão e brigar com o hook. Estado nunca regride."""
    if not rest or not re.match(r"^T\d+(\.\d+)*$", rest[0]):
        print("uso: prevec.sh marca T3 [ok|andamento]", file=sys.stderr)
        return 2
    sym = "🔄" if (rest[1:] and rest[1].lower().startswith("and")) else "✅"
    plan = active_plan(root, rest[0])
    if not plan:
        print(f"{rest[0]} não está em nenhum plano ativo (.context/work/)", file=sys.stderr)
        return 1
    mark_plan(root, rest[0], sym)
    print(f"{rest[0]} {sym} em {os.path.relpath(plan, root)}")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    sub, rest = argv[0], argv[1:]
    if sub == "marca":
        return cmd_marca(project_root({}), rest)
    d = {} if (sub == "plano" and rest) else read_input()
    root = project_root(d)
    try:
        if sub == "status":
            cmd_status(d, root)
        elif sub == "ritmo":
            cmd_ritmo(d, root)
        elif sub == "pre":
            cmd_pre(d, root)
        elif sub == "cmdlog":
            cmd_cmdlog(d, root)
        elif sub == "rotulo":
            cmd_rotulo(d, root)
        elif sub == "escopo":
            cmd_escopo(d, root)
        elif sub == "plano":
            return cmd_plano(d, root, rest)
    except Exception as e:  # hook de estado nunca derruba o turno
        if os.environ.get("PREVEC_DEBUG") == "1":
            print(f"prevec {sub}: {e!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
