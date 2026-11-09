#!/usr/bin/env python3
"""Harmônicas e ganho em GRADE nível x frequência (e IMD de dois tons) de um efeito (pedalboard, regime estável).

Complementa `ficha_comportamento.py`, que mede THD vs nível em UMA frequência (1 kHz): aqui o eixo da FREQUÊNCIA
entra (110 Hz / 1 kHz / 5 kHz / ...), que separa não linear sem memória (THD igual em todas as frequências) de não linear
com memória/pré-ênfase/saturação por fluxo (THD ~ 1/f^2 no grave, ou mais alta no agudo).
Por ponto (nível, f): ganho do fundamental (dB), H2..H6 (dBc), THD (%), par/ímpar, DC. Cada ponto: aquecimento + janela de 1 s
no mesmo fluxo contínuo (reset=False; tom em bin exato: f inteiro). Resumo por ajuste:
  - ganho de pequeno sinal (menor nível) e nível de compressão de 1 dB (ganho cai 1 dB)
  - joelho de THD: primeiro nível com THD >= 1 % e >= 5 %
  - THD vs frequência no nível mais alto abaixo de 0 dBFS: espalhamento (dB) e relação grave/agudo
  - par vs ímpar dominante
--imd mede também IMD: SMPTE (60 Hz + 7 kHz, 4:1, bandas laterais em 7k +- n*60 Hz) e CCIF (19 kHz + 20 kHz, produtos em
1 kHz, 18 kHz, 21 kHz), em --imd-niveis (pico combinado em dBFS).
Ajustes: --settings JSON {"nome": {"param": raw 0..1, ...}, ...} (como a ficha); sem ele só o padrão de fábrica.
Uso (PYTHONPATH=<skill>/scripts):
  harmonicos_vs_nivel_freq.py "/Library/Audio/Plug-Ins/VST3/X.vst3" --out DIR [--settings s.json] [--rapido] [--imd]
Saída: <out>/grade.csv (uma linha por ponto), grade.json, grade.md. Efeito apenas (instrumento -> n/a).
"""
import argparse, csv, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medidas_comuns as mc

db = mc.db


def ponto(pl, f, L, warm, meas=1.0):
    sr = pl.sr
    y = pl.proc(mc.tom(sr, f, L, warm + meas))[0][int(warm * sr):]
    h1, hs = mc.tom_analise(y, sr, f)
    hh = [v or 0.0 for v in hs]
    thd = float(np.sqrt(sum(v * v for v in hh)))
    par = float(np.sqrt(hh[0] ** 2 + hh[2] ** 2))
    imp = float(np.sqrt(hh[1] ** 2 + hh[3] ** 2))
    return {"f_hz": f, "nivel_dbfs": L, "ganho_db": round(float(db(h1 / 10 ** (L / 20))), 3),
            **{f"H{k}_dbc": (round(float(db(v)), 1) if v else None) for k, v in zip(range(2, 7), hs)},
            "THD_pct": round(100 * thd, 5), "par_sobre_impar": round(par / (imp + 1e-18), 3), "dc": float(y.mean())}


def imd(pl, L_pico, warm, tipo):
    sr = pl.sr
    N = sr
    t = np.arange(int((warm + 1.0) * sr)) / sr
    A = 10 ** (L_pico / 20)
    if tipo == "smpte":
        f1, f2, a1, a2 = 60.0, 7000.0, 0.8 * A, 0.2 * A
    else:
        f1, f2, a1, a2 = 19000.0, 20000.0, 0.5 * A, 0.5 * A
        if f2 > 0.46 * sr:
            return None
    x = (a1 * np.sin(2 * np.pi * f1 * t) + a2 * np.sin(2 * np.pi * f2 * t)).astype(np.float32)
    y = pl.proc(np.vstack([x, x]))[0][int(warm * sr):]
    w = np.hanning(N)
    Y = np.abs(np.fft.rfft(y * w)) * 2 / w.sum()
    pk = lambda f: float(Y[max(0, int(round(f)) - 2):int(round(f)) + 3].max())
    if tipo == "smpte":
        sb = [pk(f2 + k * f1) for k in (-3, -2, -1, 1, 2, 3)]
        return {"tipo": "SMPTE 60Hz+7kHz 4:1", "nivel_pico_dbfs": L_pico, "imd_pct": round(100 * float(np.sqrt(sum(v * v for v in sb)) / (pk(f2) + 1e-30)), 5),
                "bandas_laterais_dbc": [round(float(db(v / (pk(f2) + 1e-30))), 1) for v in sb]}
    prod = {"1k(f2-f1)": pk(f2 - f1), "18k(2f1-f2)": pk(2 * f1 - f2), "21k(2f2-f1)": pk(2 * f2 - f1) if 2 * f2 - f1 < 0.46 * sr else None}
    ref = pk(f2)
    return {"tipo": "CCIF 19k+20k", "nivel_pico_dbfs": L_pico,
            "produtos_dbc": {k: (round(float(db(v / (ref + 1e-30))), 1) if v is not None else None) for k, v in prod.items()}}


def resume(pontos):
    out = {}
    fs = sorted({p["f_hz"] for p in pontos})
    Ls = sorted({p["nivel_dbfs"] for p in pontos})
    f_ref = 1000.0 if 1000.0 in fs else fs[len(fs) // 2]
    ref = sorted([p for p in pontos if p["f_hz"] == f_ref], key=lambda p: p["nivel_dbfs"])
    g0 = ref[0]["ganho_db"]
    out["ganho_pequeno_sinal_db"] = g0
    comp = [p["nivel_dbfs"] for p in ref if p["ganho_db"] < g0 - 1.0]
    out["nivel_compressao_1dB_dbfs"] = comp[0] if comp else None
    for lim in (1.0, 5.0):
        k = [p["nivel_dbfs"] for p in ref if p["THD_pct"] >= lim]
        out[f"joelho_THD_{lim:g}pct_dbfs"] = k[0] if k else None
    Lt = max([L for L in Ls if L < 0] or Ls)
    th = {p["f_hz"]: p["THD_pct"] for p in pontos if p["nivel_dbfs"] == Lt}
    out["nivel_comparacao_THD_dbfs"] = Lt
    out["THD_pct_por_freq"] = {str(int(f)): v for f, v in sorted(th.items())}
    # THD total mistura conjuntos de harmônicas diferentes (as acima de Nyquist somem): o teste de memória usa H3 (e H2)
    # só nas frequências onde existem; THD total fica como informação
    h3 = {p["f_hz"]: p["H3_dbc"] for p in pontos if p["nivel_dbfs"] == Lt and p["H3_dbc"] is not None}
    out["H3_dbc_por_freq"] = {str(int(f)): v for f, v in sorted(h3.items())}
    if len(h3) >= 2:
        out["espalhamento_H3_entre_freq_db"] = round(float(max(h3.values()) - min(h3.values())), 2)
        out["H3_grave_menos_agudo_db"] = round(float(h3[min(h3)] - h3[max(h3)]), 2)
        out["memoryless_provavel"] = bool(out["espalhamento_H3_entre_freq_db"] < 3.0)
    else:
        out["memoryless_provavel"] = None
        out["aviso"] = "menos de 2 frequências com H3 abaixo de Nyquist: não dá para decidir memória por frequência"
    pi = [p["par_sobre_impar"] for p in pontos if p["nivel_dbfs"] == Lt]
    out["par_sobre_impar_mediano"] = round(float(np.median(pi)), 3)
    out["dominante"] = "pares" if np.median(pi) > 1.2 else ("ímpares" if np.median(pi) < 0.8 else "misto")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="grade_out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--niveis", default="-60,-40,-30,-20,-12,-6,-3,0")
    ap.add_argument("--freqs", default="110,1000,5000,10000", help="Hz inteiros")
    ap.add_argument("--warm", type=float, default=1.0)
    ap.add_argument("--rapido", action="store_true", help="níveis -30,-12,-3; freqs 110,1000,8000; aquecimento 0,5 s")
    ap.add_argument("--settings", help="JSON {nome: {param: raw}}")
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw", help="ajustes comuns a todos")
    ap.add_argument("--imd", action="store_true")
    ap.add_argument("--imd-niveis", default="-18,-6")
    ap.add_argument("--sem-mix", action="store_true")
    a = ap.parse_args()
    if a.rapido:
        a.niveis, a.freqs, a.warm = "-30,-12,-3", "110,1000,8000", 0.5
    niv = [float(v) for v in a.niveis.split(",")]
    frs = [float(v) for v in a.freqs.split(",")]
    t0 = time.time()
    pl = mc.Plugin(a.plugin, a.sr, mc.parse_sets(a.set), None, mix_auto=not a.sem_mix)
    R = {"plugin": a.plugin, "nome": pl.nome, "sr": a.sr, "ajustes_base": pl.alterados, "por_ajuste": {}}
    if getattr(pl.fx, "is_instrument", False):
        R["aviso"] = "instrumento (MIDI): n/a"
        niv, frs = [], []
    ajs = {"neutro": {}}
    if a.settings:
        ajs.update(json.load(open(a.settings)))
    base = dict(pl.alterados)
    linhas = []
    pl.proc(np.random.default_rng(1).standard_normal((2, a.sr)).astype(np.float32) * 0.01)       # aquecimento geral
    for nome, aj in ajs.items():
        for k, v in pl.padrao.items():
            pl.P[k].raw_value = v                         # volta ao padrão de fábrica e reaplica a base + o ajuste
        pl.setp(**{**base, **aj})
        pl.proc(np.zeros((2, a.sr // 2), np.float32))
        pts = []
        for f in frs:
            for L in niv:
                p = ponto(pl, f, L, a.warm)
                p["ajuste"] = nome
                pts.append(p)
        R["por_ajuste"][nome] = {"pontos": pts}
        if pts:
            R["por_ajuste"][nome]["resumo"] = resume(pts)
        if a.imd and pts:
            R["por_ajuste"][nome]["imd"] = [r for L in a.imd_niveis.split(",") for t in ("smpte", "ccif")
                                            for r in [imd(pl, float(L), a.warm, t)] if r]
        linhas += pts
    R["tempo_s"] = round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(R, open(os.path.join(a.out, "grade.json"), "w"), indent=1, ensure_ascii=False, default=float)
    if linhas:
        with open(os.path.join(a.out, "grade.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
            w.writeheader()
            w.writerows(linhas)
    L = [f"# Harmônicas vs nível e frequência: {R['nome']}", "", f"SR {a.sr}; aquecimento {a.warm} s + janela 1 s, reset=False. Base: {R['ajustes_base']}", ""]
    if R.get("aviso"):
        L.append(R["aviso"])
    for nome, d in R["por_ajuste"].items():
        L += [f"## Ajuste: {nome}", "", "| f Hz | nível dBFS | ganho dB | H2 | H3 | H4 | H5 | H6 | THD % | par/ímpar |", "|---|---|---|---|---|---|---|---|---|---|"]
        for p in d["pontos"]:
            L.append(f"| {p['f_hz']:g} | {p['nivel_dbfs']:g} | {p['ganho_db']} | {p['H2_dbc']} | {p['H3_dbc']} | {p['H4_dbc']} | {p['H5_dbc']} | {p['H6_dbc']} | {p['THD_pct']} | {p['par_sobre_impar']} |")
        if d.get("resumo"):
            L += ["", "Resumo: " + json.dumps(d["resumo"], ensure_ascii=False)]
        for r in d.get("imd", []):
            L.append("- IMD: " + json.dumps(r, ensure_ascii=False))
        L.append("")
    open(os.path.join(a.out, "grade.md"), "w").write("\n".join(L))
    for nome, d in R["por_ajuste"].items():
        print(nome, json.dumps(d.get("resumo"), ensure_ascii=False))


if __name__ == "__main__":
    main()
