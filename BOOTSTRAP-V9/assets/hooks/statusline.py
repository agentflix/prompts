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


def task_line(root):
    pattern = os.path.join(glob.escape(root), ".context", "specs", "*", "features.json")
    def mtime(f):
        try:
            return os.path.getmtime(f)
        except OSError:
            return 0
    files = sorted(glob.glob(pattern), key=mtime, reverse=True)
    for f in files[:20]:
        try:
            if os.path.getsize(f) > 2_000_000:
                continue
            with open(f, encoding="utf-8") as fh:
                items = json.load(fh)
        except Exception:
            continue
        if not isinstance(items, list) or not items:
            continue
        pend = [i for i in items if isinstance(i, dict) and not i.get("passa")]
        if pend:
            crit = pend[0].get("criterio") or pend[0].get("id") or ""
            return f"▶ {len(items) - len(pend) + 1}/{len(items)} {clean(crit, 42)}"
    return None


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


def main():
    try:
        d = json.loads(sys.stdin.read() or "{}")
    except Exception:
        d = {}
    d = obj(d)
    root = find_root(d)
    first = safe(base_line, d, root)
    lines = [first] if first else []
    parts = [p for p in (safe(task_line, root), safe(gate_part, root), safe(cache_part, d)) if p]
    if parts:
        lines.append(" · ".join(parts))
    print("\n".join(lines))


try:
    main()
except Exception:
    print("")
