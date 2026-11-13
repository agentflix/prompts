#!/usr/bin/env python3
# Corpo da statusline. Chamado por statusline.sh com python3 -I.
# Nunca pode quebrar: qualquer erro imprime linha vazia.
import glob
import json
import os
import re
import subprocess
import sys
import time

G, R, Y, D, N, BASE = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m", "\033[36m"


def obj(x):
    return x if isinstance(x, dict) else {}


def num(x):
    import math
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None


def safe(fn, *args):
    try:
        return fn(*args)
    except Exception:
        return None


def clean(s, limit):
    s = re.sub(r"[\x00-\x1f\x7f]", " ", str(s))
    return s if len(s) <= limit else s[: limit - 1] + "…"


def git(root, *args):
    try:
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
        r = subprocess.run(["git", "--no-optional-locks", "-C", root, *args],
                           capture_output=True, text=True, timeout=2, env=env)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def find_root(d):
    ws = obj(d.get("workspace"))
    root = ws.get("project_dir") or os.environ.get("CLAUDE_PROJECT_DIR")
    if isinstance(root, str) and root:
        return root
    here = ws.get("current_dir") or d.get("cwd") or os.getcwd()
    here = here if isinstance(here, str) else os.getcwd()
    return git(here, "rev-parse", "--show-toplevel").strip() or here


def state_path(root):
    gd = git(root, "rev-parse", "--git-path", "prevec").strip()
    if not gd:
        return None
    return gd if os.path.isabs(gd) else os.path.join(root, gd)


def task_max():
    try:
        return max(10, int(os.environ.get("STATUS_TASK_MAX", "40")))
    except ValueError:
        return 40


def plan_task(root, prefer=None):
    """Sem tarefa nativa: a task atual do plano em execução (a que o hook inferiu, a 🔄, ou a próxima ⬜)."""
    files = []
    for sub in ("work", "planos"):
        d = os.path.join(root, ".context", sub)
        try:
            files += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md") and not f.startswith("_")]
        except OSError:
            pass
    files.sort(key=os.path.getmtime, reverse=True)
    for f in files[:10]:
        try:
            with open(f, encoding="utf-8") as fh:
                text = fh.read(200_000)
        except OSError:
            continue
        if os.sep + "work" + os.sep not in f and not re.search(r"^status:\s*(em-execucao|em-execução)", text[:600], re.M):
            continue
        heads = re.findall(r"^###\s+(T[\d.]+)\s*[—–-]\s*([^·\n]*)(.*)$", text, re.M)
        if not heads:
            continue
        done = sum(1 for h in heads if "✅" in h[2])
        cur = (next((h for h in heads if h[0] == prefer), None) if prefer else None) \
            or next((h for h in heads if "🔄" in h[2]), None) or next((h for h in heads if "✅" not in h[2]), None)
        if cur:
            return {"n": done + 1, "total": len(heads), "text": f"{cur[0]} {cur[1].strip()}"}
    return None


def task_part(d, root):
    sp = state_path(root)
    st = {}
    if sp:
        sid = re.sub(r"[^A-Za-z0-9_.-]", "_", str(d.get("session_id") or "sem-sessao"))[:80]
        try:
            with open(os.path.join(sp, "status", sid + ".json"), encoding="utf-8") as fh:
                st = json.load(fh)
        except Exception:
            st = {}
    st = obj(st)
    cur = obj(st.get("current"))
    task = None
    if cur.get("text"):  # lista de tarefas nativa, quando a ferramenta tem
        total = int(num(st.get("total")) or 0)
        n = int(num(st.get("done")) or 0) + 1
        task = {"n": n, "total": total, "text": cur["text"]}
    elif st.get("plan_cur"):  # task do plano que o hook inferiu nesta sessão
        task = plan_task(root, st.get("plan_cur"))
    if not task and isinstance(st.get("pedido"), str) and st["pedido"]:
        task = {"n": 0, "total": 0, "text": st["pedido"]}  # sem plano: o pedido atual
    if not task:
        task = plan_task(root)  # sessão nova com plano em execução
    acao = st.get("acao") if isinstance(st.get("acao"), str) and time.time() - (num(st.get("acao_t")) or 0) < 300 else None
    if task is not None:
        task["acao"] = acao
    agents = [obj(a).get("type") for a in obj(st.get("agents")).values()
              if time.time() - (num(obj(a).get("t")) or 0) < 1800]
    agents = [a for a in agents if isinstance(a, str) and a]
    return task, agents


def queue_part(root):
    gd = git(root, "rev-parse", "--git-common-dir").strip()
    if not gd:
        return None
    gd = gd if os.path.isabs(gd) else os.path.join(root, gd)
    import fcntl
    qd = os.path.join(gd, "prevec", "tq")
    try:
        names = [f for f in os.listdir(qd) if f.endswith(".t")]
    except OSError:
        return None
    n = 0
    for f in names[:50]:  # só conta ticket com dono vivo (flock ocupado); não apaga nada
        try:
            fd = os.open(os.path.join(qd, f), os.O_RDONLY)
        except OSError:
            continue
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            n += 1
        finally:
            os.close(fd)
    if n <= 0:
        return None
    return f"{Y}fila {n}{N}" if n > 1 else f"{D}suíte rodando{N}"


def gate_part(root):
    gd = git(root, "rev-parse", "--git-path", "prevec").strip()
    if not gd:
        return None
    if not os.path.isabs(gd):
        gd = os.path.join(root, gd)
    try:
        with open(os.path.join(gd, "gate-log.tsv"), "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 512))
            last = fh.read().decode("utf-8", "replace").strip().splitlines()[-1].split("\t")
        secs, res = last[1], last[3]
    except Exception:
        return None
    mark = {"verde": G + "✓", "vermelho": R + "✗", "timeout": R + "⏱", "liberado": Y + "!"}.get(res, "?")
    return f"gate {mark}{N} {clean(secs, 6)}s"


def parse_time(exp):
    if isinstance(exp, (int, float)):
        return exp / 1000 if exp > 1e12 else exp
    if isinstance(exp, str):
        from datetime import datetime, timezone
        s = re.sub(r"\.\d+", "", exp.strip()).replace("Z", "+00:00")
        try:
            t = datetime.fromisoformat(s)
        except ValueError:
            return None
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return t.timestamp()
    return None


def cache_part(d):
    pc, cw = obj(d.get("prompt_cache")), obj(d.get("context_window"))
    ratio = num(pc.get("hit_ratio"))
    if ratio is None:
        u = obj(cw.get("current_usage"))
        rd = num(u.get("cache_read_input_tokens")) or 0
        tot = rd + (num(u.get("cache_creation_input_tokens")) or 0) + (num(u.get("input_tokens")) or 0)
        ratio = rd / tot if tot else None
    if ratio is None or ratio < 0:
        return None
    pct = round(100 * ratio) if ratio <= 1 else round(ratio)
    color = G if pct >= 80 else (Y if pct >= 50 else R)
    txt = f"cache {color}{pct}%{N}"
    if pc.get("warm") is False:
        txt += f" {D}frio{N}"
    else:
        exp = parse_time(pc.get("expires_at"))
        if exp:
            left = int(exp - time.time())
            if 0 < left < 60:
                txt += f" {Y}esfria em <1m{N}"
            elif 60 <= left < 600:
                txt += f" {Y}esfria em {left // 60}m{N}"
    cause = None
    lm = pc.get("last_miss_cause")
    if isinstance(lm, dict):
        cs = lm.get("causes") or lm.get("cause")
        cause = cs[0] if isinstance(cs, list) and cs else cs
    if not cause:
        mc = pc.get("miss_causes")
        if isinstance(mc, dict) and mc:
            cause = max(mc, key=lambda k: mc[k] if isinstance(mc[k], (int, float)) else 0)
    if pct < 80 and cause:
        txt += f" {D}({clean(cause, 24)}){N}"
    return txt


def fmt(n):
    n = int(n or 0)
    if n >= 1_000_000:
        return f"{n / 1e6:.1f}".rstrip("0").rstrip(".") + "M"
    return f"{round(n / 1000)}k" if n >= 1000 else str(n)


def base_line(d, root):
    seg = []
    # Pasta: nome do projeto e, se o cwd está numa subpasta ou worktree, o caminho relativo.
    ws = obj(d.get("workspace"))
    here = ws.get("current_dir") or d.get("cwd") or ""
    folder = os.path.basename(os.path.normpath(root)) if root else ""
    if isinstance(here, str) and here and root:
        r = os.path.relpath(os.path.normpath(here), os.path.normpath(root))
        if r != "." and not r.startswith(".."):
            folder = f"{folder}/{r}"
        elif r.startswith(".."):
            folder = os.path.basename(os.path.normpath(here))
    wt = obj(d.get("worktree")).get("name")
    if isinstance(wt, str) and wt:
        folder = f"{folder} ⎇{wt}"
    if folder:
        seg.append(clean(folder, 40))
    branch = git(root, "symbolic-ref", "--short", "-q", "HEAD").strip() or git(root, "rev-parse", "--short", "HEAD").strip()
    if branch:
        dirty = len([l for l in git(root, "status", "--porcelain").splitlines() if l.strip()])
        seg.append(f"{branch}*{dirty}" if dirty else branch)
    m = obj(d.get("model"))
    ident = f"{m.get('id') or ''} {m.get('display_name') or ''}".lower()
    fam = next((n for n in ("Opus", "Sonnet", "Haiku", "Fable") if n.lower() in ident), m.get("display_name"))
    if fam:
        seg.append(clean(fam, 20))
    cw = obj(d.get("context_window"))
    win = num(cw.get("context_window_size"))
    if not win or win <= 0:
        win = 1_000_000 if "1m" in str(m.get("id") or "").lower() else 200_000
    u = obj(cw.get("current_usage"))
    used = None
    if u:
        used = sum(num(v) or 0 for v in (u.get("input_tokens"), u.get("cache_read_input_tokens"),
                                         u.get("cache_creation_input_tokens")))
    elif num(cw.get("used_percentage")) is not None:
        used = num(cw.get("used_percentage")) * win / 100
    pct = max(0, min(100, round(100 * used / win))) if used is not None else 0
    filled = max(0, min(10, round(pct / 10)))
    ctx = f"{'█' * filled}{'░' * (10 - filled)} {pct}% ({fmt(used)}/{fmt(win)})"
    if pct >= 80:
        ctx += " compactar"
    seg.append(ctx)
    cost = obj(d.get("cost"))
    add, rem = int(num(cost.get("total_lines_added")) or 0), int(num(cost.get("total_lines_removed")) or 0)
    if add or rem:
        seg.append(f"+{add} -{rem}")
    return BASE + "  |  ".join(seg) + N


ANSI = re.compile(r"\033\[[0-9;]*m")


def vis(s):
    return len(ANSI.sub("", s))


def clip(s, width):
    """Corta pela largura visível, sem quebrar código de cor."""
    if vis(s) <= width:
        return s
    out, n, i = [], 0, 0
    while i < len(s) and n < width - 1:
        m = ANSI.match(s, i)
        if m:
            out.append(m.group(0)); i = m.end(); continue
        out.append(s[i]); n += 1; i += 1
    return "".join(out) + "…" + N


def width():
    try:
        w = int(os.environ.get("COLUMNS", "0"))
    except ValueError:
        w = 0
    return w if w >= 30 else 120


def second_line(d, root, w):
    task, agents = safe(task_part, d, root) or (None, [])
    tail = [p for p in (safe(gate_part, root), safe(queue_part, root), safe(cache_part, d)) if p]
    if agents:
        names = sorted(set(agents))
        tail.insert(0, f"{BASE}⇢ {', '.join(names[:2])}{' +' + str(len(agents) - 2) if len(agents) > 2 else ''}{N}")
    sep = " · "
    if not task:
        return sep.join(tail) if tail else None
    if task.get("acao"):
        tail.insert(0, f"{D}{task['acao']}{N}")
    prefix = f"▶ {task['n']}/{task['total']} " if task.get("total") else "▶ "
    # A tarefa usa o que sobra da linha, até STATUS_TASK_MAX. Sobrou pouco: sai o fim da linha.
    while True:
        rest = sep.join(tail)
        room = w - vis(prefix) - (vis(rest) + len(sep) if rest else 0)
        lim = min(task_max(), room)
        if lim >= 12 or not tail:
            break
        tail.pop()
    text = clean(task["text"], max(lim, 8))
    return sep.join([prefix + text] + tail)


def main():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        d = {}
    d = obj(d)
    root = find_root(d)
    w = width()
    lines = []
    first = safe(base_line, d, root)
    if first:
        lines.append(clip(first, w))
    second = safe(second_line, d, root, w)
    if second:
        lines.append(clip(second, w))
    print("\n".join(lines))


try:
    main()
except Exception:
    print("")
