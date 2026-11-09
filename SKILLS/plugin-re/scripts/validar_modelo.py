#!/usr/bin/env python3
"""Valida um modelo/motor contra a verdade medida no plugin real: % de pontos dentro de uma régua.

CONTRATO DO CSV DE VERDADE (um ponto por linha, cabeçalho obrigatório):
  - colunas de parâmetros: QUALQUER nome que não seja reservado, valor em RAW 0..1 (como o pedalboard)
    (o motor/modelo é quem converte raw -> unidade; parâmetros ausentes = padrão de fábrica)
  - amp_db : nível do tom de 1 kHz (ou --freq) em dBFS
  - gain_db: ganho medido do fundamental (dB), saída/entrada
  - h2..h6 : harmônicas medidas RELATIVAS a H1 (razão linear, não dB); h2.. opcionais (qualquer subconjunto)
Reservadas: amp_db, gain_db, h2..h9, grupo (rótulo opcional p/ resultados por grupo).

MODELO (escolha um):
  --exe CAMINHO   executável em lote: lê CSV em stdin (mesmas colunas de parâmetro + amp_db) e escreve em
                  stdout um CSV com cabeçalho gain_db,h2,h3,... na MESMA ordem das linhas. Para motor C++.
  --py ARQ.py:FUNC  função Python f(params: dict[str,float], amp_db: float) -> dict(gain=dB, h=[h2,h3,...])

SUBCOMANDOS (flags):
  --gerar N --limites lim.json --seed S --saida amostra.csv
        amostra aleatória NOVA a partir dos limites {"param": [lo, hi], "amp_db": [-30, 0]}; use semente que o ajuste
        nunca viu. Com --medir-plugin PLUGIN [--sr] mede cada ponto no plugin real (regime estável) e grava a verdade.
  --verdade verdade.csv  (+ --exe/--py) calcula erro e % dentro da régua (--tol-gain dB, --tol-h abs).
Saída: relatório texto + --json arquivo (por grupo, max, p50/p90, piores pontos).
"""
import argparse, csv, json, os, subprocess, sys, importlib.util
import numpy as np

RESERV = {"amp_db", "gain_db", "grupo"} | {f"h{k}" for k in range(2, 10)}


def le_csv(path):
    with open(path) as f:
        r = list(csv.DictReader(f))
    return r


def gera(a):
    lim = json.load(open(a.limites))
    rng = np.random.default_rng(a.seed)
    cols = list(lim)
    linhas = []
    for _ in range(a.gerar):
        l = {}
        for c in cols:
            v = lim[c]
            lo, hi = (v[0], v[1]) if isinstance(v, list) else (v, v)
            l[c] = float(rng.uniform(lo, hi))
        linhas.append(l)
    if "amp_db" not in cols:
        for l in linhas:
            l["amp_db"] = -6.0
    if a.medir_plugin:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from ss_template import Harness
        h = Harness(a.medir_plugin, a.sr, 1, 3)
        for i, l in enumerate(linhas):
            h.defaults(**{k: v for k, v in l.items() if k != "amp_db"})
            m = h.meas(l["amp_db"], a.freq)
            l["gain_db"] = m["gain"]
            for k, v in enumerate(m["h"]):
                l[f"h{k + 2}"] = v if v is not None else 0.0
            print(f"[{i + 1}/{len(linhas)}] medido", file=sys.stderr, end="\r")
    with open(a.saida, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader(); w.writerows(linhas)
    print(f"{len(linhas)} pontos -> {a.saida} (semente {a.seed})")


def roda_modelo(a, rows):
    pcols = [c for c in rows[0] if c not in RESERV]
    if a.exe:
        ent = ",".join(pcols + ["amp_db"]) + "\n" + "\n".join(",".join(r[c] for c in pcols + ["amp_db"]) for r in rows) + "\n"
        p = subprocess.run([a.exe], input=ent, capture_output=True, text=True, check=True)
        out = list(csv.DictReader(p.stdout.splitlines()))
        if len(out) != len(rows):
            sys.exit(f"exe devolveu {len(out)} linhas, esperado {len(rows)}")
        return [(float(o["gain_db"]), [float(o[f"h{k}"]) for k in range(2, 10) if f"h{k}" in o]) for o in out]
    arq, fn = a.py.split(":")
    spec = importlib.util.spec_from_file_location("modelo_usuario", arq)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    f = getattr(mod, fn)
    res = []
    for r in rows:
        o = f({c: float(r[c]) for c in pcols}, float(r["amp_db"]))
        res.append((float(o["gain"]), list(o["h"])))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verdade", help="CSV de verdade medida (contrato acima)")
    ap.add_argument("--exe"); ap.add_argument("--py")
    ap.add_argument("--tol-gain", type=float, default=0.1, help="régua |erro de ganho| em dB (padrão 0,1)")
    ap.add_argument("--tol-h", type=float, default=0.005, help="régua |erro de harmônica| absoluto (padrão 0,005)")
    ap.add_argument("--json", help="grava o resumo em JSON")
    ap.add_argument("--gerar", type=int, help="gera N pontos aleatórios (precisa --limites, --saida)")
    ap.add_argument("--limites"); ap.add_argument("--seed", type=int, default=31337); ap.add_argument("--saida", default="amostra.csv")
    ap.add_argument("--medir-plugin", help="mede a amostra gerada neste plugin real")
    ap.add_argument("--sr", type=int, default=96000); ap.add_argument("--freq", type=float, default=1000.0)
    a = ap.parse_args()
    if a.gerar:
        if not a.limites:
            sys.exit("--gerar exige --limites")
        return gera(a)
    if not a.verdade or not (a.exe or a.py):
        ap.error("informe --verdade e (--exe ou --py), ou use --gerar")
    rows = le_csv(a.verdade)
    mod = roda_modelo(a, rows)
    hk = [k for k in range(2, 10) if f"h{k}" in rows[0]]
    res = {}
    for r, (g, hs) in zip(rows, mod):
        eg = abs(g - float(r["gain_db"]))
        eh = max((abs(hs[i] - float(r[f"h{k}"])) for i, k in enumerate(hk) if i < len(hs)), default=0.0)
        if "grupo" in r:
            res.setdefault(r["grupo"], []).append((eg, eh, r))
        res.setdefault("TODOS", []).append((eg, eh, r))
    out = {}
    for g, L in res.items():
        eg = np.array([x[0] for x in L]); eh = np.array([x[1] for x in L])
        ok = (eg <= a.tol_gain) & (eh <= a.tol_h)
        pior = sorted(L, key=lambda x: -max(x[0] / a.tol_gain, x[1] / a.tol_h))[:3]
        out[g] = {"n": len(L), "pct_dentro": round(100 * float(ok.mean()), 2),
                  "gain_p50": float(np.median(eg)), "gain_p90": float(np.percentile(eg, 90)), "gain_max": float(eg.max()),
                  "h_p50": float(np.median(eh)), "h_p90": float(np.percentile(eh, 90)), "h_max": float(eh.max()),
                  "piores": [{"eg": p[0], "eh": p[1], "ponto": {k: v for k, v in p[2].items()}} for p in pior]}
        print(f"{g:10s} n={len(L):5d}  dentro da régua (|g|<={a.tol_gain} dB, |h|<={a.tol_h}): {out[g]['pct_dentro']:6.2f} %"
              f"   ganho p50/p90/max {out[g]['gain_p50']:.4f}/{out[g]['gain_p90']:.4f}/{out[g]['gain_max']:.4f} dB"
              f"   h p50/p90/max {out[g]['h_p50']:.5f}/{out[g]['h_p90']:.5f}/{out[g]['h_max']:.5f}")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
