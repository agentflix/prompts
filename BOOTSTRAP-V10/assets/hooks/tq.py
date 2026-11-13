#!/usr/bin/env python3
"""Fila de testes pesados (tq). Uma suíte por repositório por vez, em ordem de chegada.

Uso:
  tq.sh '<comando>'      entra na fila, espera a vez e roda o comando com bash -c
  tq.sh --status         mostra quem roda e quem espera
  tq.sh --full '<cmd>'   como acima; verde, grava o estado do código (para não rodar de novo)
  tq.sh --full-ok '<cmd>'  sai 0 se esse comando já passou neste mesmo estado do código
  tq.sh --fase           fim de fase: roda só as partes de GATE_PARTS que o diff tocou
                         (sem GATE_PARTS, o GATE_FULL)

Como funciona:
  - Cada processo que quer rodar cria um ticket <tempo_ns>-<pid>.t e segura flock nele.
    A ordem dos nomes é a ordem de chegada (FIFO).
  - Quem tem o menor ticket vivo roda. Os outros esperam, sem gastar token: o processo
    só dorme e imprime a posição quando ela muda (e a cada 60s).
  - Ticket de processo morto (crash, kill -9) não segura nada: o kernel solta o flock,
    e quem lista a fila apaga o ticket. Não há PID para reciclar nem lock velho para limpar.
  - A pasta fica em git-common-dir, então vale para todas as worktrees do mesmo repositório.
  - TQ_HELD=1 no ambiente do comando: um teste que chama outro comando da fila não trava.
Saída: o código do comando. 75 quando a espera passa de TQ_WAIT segundos.
"""
import contextlib
import fcntl
import json
import os
import signal
import subprocess
import sys
import time


def queue_dir():
    try:
        g = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True,
                           text=True, timeout=5).stdout.strip()
    except Exception:
        g = ""
    base = os.path.realpath(g) if g else os.path.join(os.path.expanduser("~"), ".cache")
    d = os.path.join(base, "prevec", "tq")
    os.makedirs(d, exist_ok=True)
    return d


@contextlib.contextmanager
def guard(d):
    fd = os.open(os.path.join(d, "guard"), os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        yield
    finally:
        os.close(fd)


def live(d):
    """Tickets vivos em ordem. Chame com o guard; apaga ticket de dono morto."""
    out = []
    for f in sorted(x for x in os.listdir(d) if x.endswith(".t")):
        p = os.path.join(d, f)
        try:
            fd = os.open(p, os.O_RDONLY)
        except FileNotFoundError:
            continue
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            out.append(f)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(p)
        finally:
            os.close(fd)
    return out


def info(d, ticket):
    try:
        with open(os.path.join(d, ticket), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def short(cmd, n=60):
    cmd = " ".join(str(cmd).split())
    return cmd if len(cmd) <= n else cmd[: n - 1] + "…"


def status(d):
    with guard(d):
        q = live(d)
    if not q:
        print("[tq] fila vazia")
        return 0
    now = time.time()
    for i, t in enumerate(q):
        h = info(d, t)
        state = "rodando" if i == 0 else f"espera {i}"
        print(f"[tq] {state}: pid {h.get('pid')} há {int(now - h.get('t', now))}s · {short(h.get('cmd', ''))}")
    return 0


def run(d, cmd):
    if os.environ.get("TQ_HELD") == "1":
        return subprocess.call(["bash", "-c", cmd])
    wait_max = int(os.environ.get("TQ_WAIT", "0") or 0)
    mine = f"{time.time_ns():020d}-{os.getpid()}.t"
    path = os.path.join(d, mine)
    with guard(d):
        live(d)
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o644)
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, json.dumps({"pid": os.getpid(), "t": time.time(), "cmd": cmd,
                                 "cwd": os.getcwd()}).encode())
    child = None

    def forward(sig, _frame):
        if child and child.poll() is None:
            with contextlib.suppress(Exception):
                os.killpg(child.pid, sig)
        raise SystemExit(128 + sig)

    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, forward)
    t0 = last = time.time()
    lastpos = None
    try:
        while True:
            with guard(d):
                q = live(d)
            if mine not in q:  # ticket sumiu (pasta limpa à mão): recria a vez no fim
                return run(d, cmd)
            pos = q.index(mine)
            if pos == 0:
                break
            if wait_max and time.time() - t0 > wait_max:
                print(f"[tq] desisti após {wait_max}s na fila. Tente de novo mais tarde.", file=sys.stderr)
                return 75
            if pos != lastpos or time.time() - last >= 60:
                h = info(d, q[0])
                print(f"[tq] fila: posição {pos + 1} de {len(q)} · rodando há "
                      f"{int(time.time() - h.get('t', time.time()))}s: {short(h.get('cmd', ''))}",
                      file=sys.stderr, flush=True)
                lastpos, last = pos, time.time()
            time.sleep(1)
        if lastpos is not None:
            print(f"[tq] sua vez após {int(time.time() - t0)}s", file=sys.stderr, flush=True)
        # Filho herda o fd: se este processo morrer, a suíte ainda em execução segura a vez.
        os.set_inheritable(fd, True)
        env = dict(os.environ, TQ_HELD="1")
        child = subprocess.Popen(["bash", "-c", cmd], env=env, pass_fds=(fd,), start_new_session=True)
        return child.wait()
    finally:
        os.close(fd)
        with contextlib.suppress(FileNotFoundError):
            os.unlink(path)


def git_out(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, timeout=30).stdout
    except Exception:
        return b""


EXCL = [":(exclude).context", ":(exclude)*.md"]  # plano e doc mudam sem mudar o código


def changed_files():
    names = git_out("diff", "--name-only", "-z", "HEAD", "--", ".", *EXCL)
    names += git_out("ls-files", "-z", "--others", "--exclude-standard", "--", ".", *EXCL)
    return [n.decode() for n in names.split(b"\0") if n]


def code_state():
    """Hash do código: diff dos rastreados mais conteúdo dos não rastreados."""
    import hashlib
    h = hashlib.sha1(git_out("rev-parse", "HEAD"))
    h.update(git_out("diff", "--no-ext-diff", "HEAD", "--", ".", *EXCL))
    for n in sorted(git_out("ls-files", "-z", "--others", "--exclude-standard", "--", ".", *EXCL).split(b"\0")):
        if n and os.path.isfile(n):
            h.update(n)
            with open(n, "rb") as fh:
                h.update(hashlib.sha1(fh.read()).digest())
    return h.hexdigest()


def full_ok_path():
    p = git_out("rev-parse", "--git-path", "prevec").decode().strip() or ".git/prevec"
    os.makedirs(p, exist_ok=True)
    return os.path.join(p, "full-ok.json")


def norm(cmd):
    return " ".join(str(cmd).split())


def full_ok(cmd):
    try:
        with open(full_ok_path(), encoding="utf-8") as fh:
            h = json.load(fh)
    except Exception:
        return None
    # Vale se o comando gravado cobriu cada parte do GATE_FULL (rodar só "npm test" não cobre o build).
    import re
    parts = [norm(x) for x in re.split(r"&&|;|\|\|", cmd) if norm(x)]
    if parts and all(x in h.get("cmd", "") for x in parts) and h.get("state") == code_state():
        return h
    return None


def run_full(d, cmd):
    rc = run(d, cmd)
    if rc == 0:
        with open(full_ok_path(), "w", encoding="utf-8") as fh:
            json.dump({"cmd": norm(cmd), "state": code_state(), "t": time.time()}, fh)
    return rc


def fase(d):
    full = os.environ.get("GATE_FULL", "").strip()
    parts = []
    for item in os.environ.get("GATE_PARTS", "").split("|"):
        if "=" in item and not item.strip().startswith("<"):
            pasta, cmd = item.split("=", 1)
            parts.append((pasta.strip().rstrip("/") + "/", cmd.strip()))
    if not parts:
        if not full or full.startswith("<"):
            print("[tq] sem GATE_FULL nem GATE_PARTS no gates.conf", file=sys.stderr)
            return 2
        return run_full(d, full)
    files = changed_files()
    hit = [(p, c) for p, c in parts if any(f.startswith(p) for f in files)]
    if not hit:
        print("[tq] fase: nenhuma parte de GATE_PARTS foi tocada; nada a rodar")
        return 0
    print("[tq] fase: rodando " + ", ".join(p for p, _ in hit), file=sys.stderr, flush=True)
    return run(d, " && ".join(f"({c})" for _, c in hit))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--full-ok":
        h = full_ok(" ".join(argv[1:]))
        if h:
            print(time.strftime("%H:%M", time.localtime(h.get("t", 0))))
            return 0
        return 1
    d = queue_dir()
    if argv[0] == "--status":
        return status(d)
    if argv[0] == "--fase":
        return fase(d)
    if argv[0] == "--full":
        import shlex
        rest = argv[1:]
        return run_full(d, shlex.join(rest) if len(rest) > 1 else (rest[0] if rest else ""))
    import shlex
    return run(d, shlex.join(argv) if len(argv) > 1 else argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
