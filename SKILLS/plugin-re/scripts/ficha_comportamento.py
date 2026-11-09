#!/usr/bin/env python3
"""Ficha de comportamento padrão de um plugin de efeito (pedalboard, regime estável).

Blocos (cada um roda isolado; se faltar parâmetro/capacidade vira "n/a" com o motivo):
  neutro      ganho unitário (tom -12 dBFS) e null vs entrada e vs bypass (ruído)
  thd         THD/harmônicas H2..H6 vs nível, por ajuste (--settings)
  freq        resposta em frequência por ruído branco (H = Pxy/Pxx) em bandas de 1/3 de oitava
  latencia    fx.reported_latency_samples (após processar um bloco) + posição do impulso na saída bruta (só confere)
  estereo     mono duplicado em L=R: diferença máxima L-R
  aliasing    tom agudo forte: % de energia fora dos harmônicos (use --sr 48000)
  ruido_dc    saída com entrada muda: RMS (dBFS) e DC
Saída: <out>/ficha.json e <out>/ficha.md. Ajustes: JSON {"nome": {"param_raw": 0..1}, ...};
sem --settings usa só "neutro" (padrão de fábrica). Efeito apenas (instrumento -> n/a; ver por-tipo.md).
O "neutro" é o padrão de FÁBRICA, que pode já colorir (ex.: depth 50 %); passe um ajuste "neutro_real"
(tudo zerado/transparente) em --settings para a medida de coloração mínima.
"""
import argparse, json, os, sys, traceback
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ss_template import Harness


def db(v):
    return float(20 * np.log10(max(abs(v), 1e-12)))


def aplica(h, aj):
    h.defaults(**aj)


def bloco(R, nome, fn):
    # roda um bloco; falha vira n/a sem derrubar a ficha
    try:
        R[nome] = fn()
    except Exception as e:
        R[nome] = {"n/a": f"{type(e).__name__}: {e}"}
        print(f"[{nome}] n/a: {e}", file=sys.stderr)
        if os.environ.get("FICHA_DEBUG"):
            traceback.print_exc()


def achar(h, *chaves):
    for n in h.P.keys():
        if any(k in n.lower() for k in chaves):
            return n
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="ficha_out")
    ap.add_argument("--sr", type=int, default=96000, help="taxa de amostragem (padrão 96000; use 48000 p/ aliasing realista)")
    ap.add_argument("--settings", help="JSON {nome: {param: raw}} com os ajustes a medir (além do neutro)")
    ap.add_argument("--niveis", default="-40,-30,-20,-12,-6,-3,0", help="níveis do tom em dBFS (THD)")
    ap.add_argument("--freq", type=float, default=1000.0, help="frequência do tom (inteira em Hz)")
    ap.add_argument("--blocos", default="neutro,thd,freq,latencia,estereo,aliasing,ruido_dc")
    ap.add_argument("--canais", type=int, default=2, help="canais do plugin (padrão 2: L=R duplicado, testa link estéreo)")
    ap.add_argument("--mono", action="store_true", help="atalho para --canais 1")
    ap.add_argument("--warm", type=int, default=3)
    a = ap.parse_args()
    blocos = set(a.blocos.split(","))
    h = Harness(a.plugin, a.sr, 1 if a.mono else a.canais, a.warm)
    R = {"plugin": a.plugin, "nome": h.fx.name, "sr": a.sr, "warm_s": a.warm}
    if getattr(h.fx, "is_instrument", False):
        R["aviso"] = "instrumento: a ficha de efeito não se aplica; use MIDI (por-tipo.md, sintetizador)"
        blocos = set()
    ajustes = {"neutro": {}}
    if a.settings:
        ajustes.update(json.load(open(a.settings)))
    nivs = [float(v) for v in a.niveis.split(",")]
    f0 = a.freq
    rng = np.random.default_rng(7)
    ruido = (10 ** (-20 / 20) * rng.standard_normal(h.N) / 1.0).astype(np.float32)
    ruido = np.clip(ruido, -1, 1)
    bypass = achar(h, "bypass")
    R["param_bypass"] = bypass

    def neutro():
        h.defaults()
        m = h.meas(-12, f0)
        out = {"ganho_db_tom_-12dBFS": round(m["gain"], 4), "dc": m["mean"], "pico": m["peak"]}
        y = h.run(ruido)
        nul = lambda a_, b_: db(np.sqrt(np.mean((a_ - b_) ** 2)) / (np.sqrt(np.mean(b_ ** 2)) + 1e-12))
        x = ruido if y.ndim == 1 else np.tile(ruido, (y.shape[0], 1))
        out["null_vs_entrada_db"] = round(nul(y, x), 2)
        if bypass:
            h.defaults(); h.setp(**{bypass: 1.0})
            yb = h.run(ruido)
            out["null_vs_bypass_db"] = round(nul(y, yb), 2)
            out["bypass_vs_entrada_db"] = round(nul(yb, x), 2)
            h.defaults()
        else:
            out["null_vs_bypass_db"] = "n/a: sem parâmetro bypass"
        return out

    def thd():
        res = {}
        for nome, aj in ajustes.items():
            linhas = []
            for L in nivs:
                aplica(h, aj)
                m = h.meas(L, f0)
                hh = [v or 0 for v in m["h"]]
                linhas.append({"nivel_dbfs": L, "ganho_db": round(m["gain"], 3), "H2": hh[0], "H3": hh[1], "H4": hh[2],
                               "H5": hh[3], "H6": hh[4], "THD_pct": round(100 * float(np.sqrt(sum(v * v for v in hh))), 4),
                               "pares_vs_impares": round(float(np.sqrt(hh[0] ** 2 + hh[2] ** 2) / (np.sqrt(hh[1] ** 2 + hh[3] ** 2 + 1e-18))), 3),
                               "dc": m["mean"]})
            res[nome] = linhas
        return res

    def freq():
        res = {}
        for nome, aj in ajustes.items():
            from scipy import signal
            aplica(h, aj)
            y = h.run(ruido)
            y = y if y.ndim == 1 else y[0]
            f, pxx = signal.welch(ruido, h.sr, nperseg=8192)
            _, pxy = signal.csd(ruido, y, h.sr, nperseg=8192)
            H = np.abs(pxy / (pxx + 1e-30))
            cs = [31.5 * 2 ** (k / 3) for k in range(0, 31) if 31.5 * 2 ** (k / 3) < h.sr / 2.05]
            res[nome] = []
            for c in cs:
                m_ = (f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))
                if m_.any():   # banda sem bin (resolução 8192 pts) é pulada
                    res[nome].append({"f_hz": round(c, 1), "ganho_db": round(db(np.mean(H[m_])), 3)})
        aplica(h, {})
        return res

    def latencia():
        # O pedalboard compensa a latência: a posição do impulso na saída dá 0. Valor confiável =
        # fx.reported_latency_samples, lido DEPOIS de processar áudio (força reconfiguração).
        out = {}
        for nome, aj in ajustes.items():   # por ajuste: modos (ex.: oversampling) mudam a latência
            aplica(h, aj)
            L = h.latencia()
            out[f"latencia_amostras[{nome}]"] = L
            out[f"latencia_ms[{nome}]"] = round(1000 * L / h.sr, 3)
        h.defaults()
        # conferência: impulso na 1ª chamada após reset (compensada) deve voltar em `pos`
        x = np.zeros(h.N, np.float32); pos = 2000; x[pos] = 0.5
        h.fx.reset()
        y = np.asarray(h.fx(h._blk(x), h.sr, reset=False))[0, :h.N]
        out["pico_impulso_vs_pos_amostras"] = int(np.argmax(np.abs(y))) - pos
        out["nota"] = "pico_impulso_vs_pos ~0 é esperado (host compensa); a latência vale a reportada"
        return out

    def estereo():
        if h.canais != 2:
            hh = Harness(a.plugin, a.sr, 2, a.warm)
        else:
            hh = h
        hh.defaults()
        y = hh.run(ruido)
        return {"max_abs_L_menos_R": float(np.abs(y[0] - y[1]).max()), "L_igual_R": bool(np.abs(y[0] - y[1]).max() < 1e-6)}

    def aliasing():
        fa = max(1000.0, round(0.1458 * 48000))   # ~7 kHz
        h.defaults()
        t = np.arange(h.N) / h.sr
        x = (10 ** (-3 / 20) * np.sin(2 * np.pi * fa * t)).astype(np.float32)
        out = {}
        for nome, aj in ajustes.items():
            aplica(h, aj)
            y = h.run(x)
            y = y if y.ndim == 1 else y[0]
            Y = np.abs(np.fft.rfft(y * h.w)) ** 2
            msk = np.ones(len(Y), bool)
            for k in range(1, int(h.sr / 2 / fa) + 2):
                b = int(round(k * fa * h.N / h.sr)); msk[max(0, b - 3):b + 4] = False
            msk[:3] = False
            out[nome] = {"freq_tom_hz": fa, "pct_energia_inarmonica": round(100 * float(Y[msk].sum() / Y.sum()), 4)}
        aplica(h, {})
        return out

    def ruido_dc():
        h.defaults()
        y = h.run(np.zeros(h.N, np.float32))
        y = y if y.ndim == 1 else y[0]
        return {"rms_dbfs": round(db(np.sqrt(np.mean(y ** 2))), 1), "dc": float(y.mean())}

    for nome, fn in (("neutro", neutro), ("thd", thd), ("freq", freq), ("latencia", latencia),
                     ("estereo", estereo), ("aliasing", aliasing), ("ruido_dc", ruido_dc)):
        if nome in blocos:
            bloco(R, nome, fn)
    os.makedirs(a.out, exist_ok=True)
    json.dump(R, open(os.path.join(a.out, "ficha.json"), "w"), indent=1, ensure_ascii=False)
    # markdown
    M = [f"# Ficha de comportamento: {R['nome']}", "", f"SR {a.sr} Hz, aquecimento {a.warm} s sem reset (regime estável).", ""]
    if "aviso" in R: M += [R["aviso"], ""]
    for k in ("neutro", "latencia", "estereo", "ruido_dc"):
        if k in R:
            M += [f"## {k}"] + [f"- {kk}: {vv}" for kk, vv in R[k].items()] + [""]
    if "thd" in R and "n/a" not in R["thd"]:
        for nome, L in R["thd"].items():
            M += [f"## THD vs nível: {nome}", "| nível | ganho dB | H2 | H3 | H4 | H5 | H6 | THD % | par/ímpar |", "|---|---|---|---|---|---|---|---|---|"]
            M += [f"| {r['nivel_dbfs']} | {r['ganho_db']} | {r['H2']:.5f} | {r['H3']:.5f} | {r['H4']:.5f} | {r['H5']:.5f} | {r['H6']:.5f} | {r['THD_pct']} | {r['pares_vs_impares']} |" for r in L] + [""]
    if "freq" in R and "n/a" not in R["freq"]:
        for nome, L in R["freq"].items():
            M += [f"## Resposta em frequência (ruído): {nome}", "| Hz | dB |", "|---|---|"] + [f"| {r['f_hz']} | {r['ganho_db']} |" for r in L] + [""]
    if "aliasing" in R and "n/a" not in R["aliasing"]:
        M += ["## Aliasing (tom agudo -3 dBFS)"] + [f"- {n}: {v}" for n, v in R["aliasing"].items()] + [""]
    for k in R:
        if isinstance(R[k], dict) and "n/a" in R[k]:
            M += [f"- {k}: n/a ({R[k]['n/a']})"]
    open(os.path.join(a.out, "ficha.md"), "w").write("\n".join(M))
    print("\n".join(M[:40]))


if __name__ == "__main__":
    main()
