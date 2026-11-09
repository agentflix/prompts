#!/usr/bin/env python3
"""Teste de fechamento: plugin REAL vs RECRIAÇÃO, com a métrica certa para cada tipo de parte. % por componente.

Recriação = função Python  --py arq.py:func  (f(x[2,N] float64, sr) -> y[2,N])  OU  executável em lote  --exe "CMD {in} {out}"
(float32 cru estéreo entrelaçado em --sr; env PLUGINRE_SR). Cada chamada é uma renderização completa a partir do estado zero.
O plugin roda em regime estável (um reset; reset=False; aquecimento; mix=100 % se houver parâmetro mix).

Componentes (--componentes, separados por vírgula; padrão regua,estatistico):
  regua        DETERMINÍSTICO: tons em níveis x frequências; |erro de ganho| <= --tol-ganho (0,1 dB) e |erro de cada H2..H6| <=
               --tol-h (0,005, razão linear); % de pontos dentro. Casa AMOSTRA A AMOSTRA (partes sem estado aleatório).
  resposta     DETERMINÍSTICO linear: |H(f)| por ruído (1/3 de oitava, 100 Hz-8 kHz): % de bandas com |erro| <= --tol-ganho.
  musica       DETERMINÍSTICO: resíduo nulo em janelas de 100 ms (--musica arquivo): % de janelas <= --limite (-40 dB), só janelas com
               plugin > -60 dBFS; alinhamento por correlação (+-200 amostras). NÃO usar em parte estocástica/modulada livre.
  estatistico  ESTOCÁSTICO/modulado: não se compara amostra, compara-se ESTATÍSTICA: IR por varredura (Farina) -> EDC de Schroeder (RMS
               do desvio em dB, 0 a -30 dB), RT60 por oitava (+-5 %), pré-atraso (+-max(2 ms,10 %)), tempo até NED=1 (+-20 %), espectro da
               cauda por oitava (+-1,5 dB), IACC precoce/tardio (+-0,1), modulação de um tom (banda lateral +-6 dB; com --mod-periodica também taxa +-5 %, AM/FM +-20 %), ruído de fundo
               com entrada muda (+-6 dB). % de métricas dentro da tolerância.
Cache: o lado do plugin é salvo em <out>/ref_plugin.json; --usar-cache reaproveita sem tocar no host (o host pode estar em uso).
Saída: <out>/fechamento.json (resumo.pct_geral, componentes.<nome>.pct, erros máximos) e fechamento.md. Alvo: --alvo 95 (%).
Uso (PYTHONPATH=<skill>/scripts):
  teste_fechamento.py "/Library/Audio/Plug-Ins/VST3/X.vst3" --py meu_motor.py:render --out DIR --componentes regua,resposta,musica --musica faixa.wav
  teste_fechamento.py PLUGIN --exe "./motor {in} {out}" --out DIR --componentes estatistico --rapido --settings s.json
Sem recriação (--py/--exe omitidos) só mede o plugin (preenche o cache). Reprodutível: sementes fixas.
"""
import argparse, json, os, sys, time
import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medidas_comuns as mc

db = mc.db


# ------------------------------------------------------------------ medidas por lado (alvo = plugin ou recriação)
def _stream(alvo, x):
    """processa x (2,N); para a recriação já é a renderização inteira, para o plugin o fluxo contínuo"""
    return alvo.proc(x)


def m_tons(alvo, niveis, freqs, warm):
    sr = alvo.sr
    out = {}
    for f in freqs:
        for L in niveis:
            y = _stream(alvo, mc.tom(sr, f, L, warm + 1.0))[0][int(warm * sr):int(warm * sr) + sr]
            h1, hs = mc.tom_analise(y, sr, f)
            out[f"{int(f)}@{L:g}"] = {"ganho_db": float(db(h1 / 10 ** (L / 20))), "h": [v if v is not None else 0.0 for v in hs]}
    return out


def m_ruido(alvo, nivel=-20.0, dur=4.0):
    sr = alvo.sr
    rng = np.random.default_rng(3)
    x = (rng.standard_normal(int(dur * sr)) * 10 ** (nivel / 20)).astype(np.float32)
    y = _stream(alvo, np.vstack([x, x]))[0]
    a = int(0.5 * sr)
    f, pxx = signal.welch(x[a:], sr, nperseg=8192)
    _, pxy = signal.csd(x[a:], y[a:], sr, nperseg=8192)
    H = np.abs(pxy / (pxx + 1e-30))
    cs = [100 * 2 ** (k / 3) for k in range(0, 21) if 100 * 2 ** (k / 3) < min(8000, sr / 2.2)]
    return {str(round(c, 1)): float(db(np.mean(H[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))]))) for c in cs}


def edc_bb(h):
    e = (h ** 2).sum(0)
    return mc.edc_db(e)


def m_estat(alvo, rapido, f_mod=1000.0):
    sr = alvo.sr
    T, cauda = (1.5, 3.0) if rapido else (3.0, 6.0)
    h, _ = mc.captura_ess(alvo, T=T, cauda=cauda)
    A = mc.analisa_ir(h, sr)
    edc = edc_bb(h)
    t = np.arange(len(edc)) / sr
    # EDC amostrada de 0 a -30 dB (ou até onde existe), em passos de 10 ms
    idx = np.arange(0, len(edc), int(0.01 * sr))
    A["edc_db_10ms"] = [float(v) for v in edc[idx]]
    # modulação de um tom
    if alvo.tipo == "plugin":
        alvo.mudo(1.0)
    dur, aq = (4.0, 1.5) if rapido else (8.0, 2.0)
    y = _stream(alvo, mc.tom(sr, f_mod, -20, aq + dur))[:, int(aq * sr):]
    A["modulacao"] = mc.demod_tom(y, sr, f_mod)["canais"][0]
    # ruído de fundo (entrada muda)
    if alvo.tipo == "plugin":
        alvo.fx.reset()                                    # a cauda do teste anterior não é ruído de fundo
        alvo.mudo(1.0)
    z = _stream(alvo, np.zeros((2, sr), np.float32))
    A["ruido_dbfs"] = float(db(np.sqrt(np.mean(z ** 2))))
    return A


def m_musica(alvo, x):
    sr = alvo.sr
    if alvo.tipo == "plugin":
        alvo.mudo(1.0)
    return _stream(alvo, x.astype(np.float32))


# ------------------------------------------------------------------ comparações
def ok_rel(a, b, tol_rel, tol_abs=0.0):
    if a is None and b is None:
        return True, 0.0
    if a is None or b is None:
        return False, None
    e = abs(a - b)
    return e <= max(tol_abs, tol_rel * abs(a)), e


def cmp_regua(P, R, tg, th):
    n = ok = 0
    eg, eh = [], []
    linhas = []
    for k in P:
        dg = abs(P[k]["ganho_db"] - R[k]["ganho_db"])
        dh = max(abs(np.array(P[k]["h"]) - np.array(R[k]["h"])))
        d = dg <= tg and dh <= th
        n += 1
        ok += d
        eg.append(dg)
        eh.append(dh)
        linhas.append({"ponto": k, "erro_ganho_db": round(dg, 4), "erro_h_max": round(float(dh), 5), "dentro": bool(d)})
    return {"pct": round(100 * ok / max(1, n), 1), "n": n, "erro_ganho_max_db": round(float(max(eg)), 4), "erro_ganho_p50_db": round(float(np.median(eg)), 4),
            "erro_h_max": round(float(max(eh)), 5), "erro_h_p50": round(float(np.median(eh)), 5), "regua": {"ganho_db": tg, "h_abs": th}, "pontos": linhas}


def cmp_resposta(P, R, tg):
    e = {k: abs(P[k] - R[k]) for k in P}
    return {"pct": round(100 * sum(v <= tg for v in e.values()) / len(e), 1), "n": len(e), "erro_max_db": round(max(e.values()), 3),
            "erro_p50_db": round(float(np.median(list(e.values()))), 3), "regua_db": tg, "erro_por_banda_db": {k: round(v, 3) for k, v in e.items()}}


def cmp_estat(P, R, mod_periodica=False):
    M = []

    def add(nome, ok, a, b, tol):
        M.append({"metrica": nome, "plugin": a, "recriacao": b, "tolerancia": tol, "dentro": bool(ok)})
    # RT60 por banda
    rt_err = []
    for b in P["rt60"]:
        a_, b_ = P["rt60"][b]["rt60_s"], R["rt60"][b]["rt60_s"]
        ok, e = ok_rel(a_, b_, 0.05)
        add(f"rt60_{b}Hz_s", ok, a_, b_, "5 %")
        if e is not None and a_:
            rt_err.append(100 * e / a_)
    # EDC (0..-30 dB)
    ea, eb = np.array(P["edc_db_10ms"]), np.array(R["edc_db_10ms"])
    n = min(len(ea), len(eb))
    msk = ea[:n] >= -30
    rms = float(np.sqrt(np.mean((ea[:n][msk] - eb[:n][msk]) ** 2))) if msk.any() else None
    add("edc_rms_db_0_a_-30", rms is not None and rms <= 1.5, rms and round(rms, 2), None, "1,5 dB")
    pa, pb = P["pre"].get("pre_atraso_ms"), R["pre"].get("pre_atraso_ms")
    add("pre_atraso_ms", pa is not None and pb is not None and abs(pa - pb) <= max(2.0, 0.1 * pa), pa, pb, "max(2 ms, 10 %)")
    na, nb = P["ned"]["t_ned_1_ms"], R["ned"]["t_ned_1_ms"]
    add("t_ned_1_ms", (na is None and nb is None) or (na and nb and abs(na - nb) <= 0.2 * na), na, nb, "20 %")
    sa, sb = P.get("espectro_cauda_oitavas_db"), R.get("espectro_cauda_oitavas_db")
    if sa and sb and P.get("energia_cauda_200ms_em_diante_db", -99) > -50:      # sem cauda real o "espectro" é só ruído de deconvolução
        for k in sa:
            add(f"espectro_cauda_{k}Hz_db", k in sb and abs(sa[k] - sb[k]) <= 1.5, sa[k], sb.get(k), "1,5 dB")
    for nome in ("iacc_precoce_0_80ms", "iacc_tardio_80ms_1s"):
        a_, b_ = P[nome], R[nome]
        add(nome, a_ is not None and b_ is not None and abs(a_ - b_) <= 0.1 if (a_ is not None or b_ is not None) else True, a_, b_, "0,1")
    ma, mb = P["modulacao"], R["modulacao"]
    sem = lambda m: m["banda_lateral_dbc"] < -70
    if sem(ma) and sem(mb):
        add("modulacao_ausente_nos_dois", True, ma["banda_lateral_dbc"], mb["banda_lateral_dbc"], "ambos < -70 dBc")
    else:
        # modulação aleatória (reverb/delay com semente livre): compara-se a ESTATÍSTICA (nível das bandas laterais), não a taxa
        add("modulacao_banda_lateral_dbc", abs(ma["banda_lateral_dbc"] - mb["banda_lateral_dbc"]) <= 6.0, ma["banda_lateral_dbc"], mb["banda_lateral_dbc"], "6 dB")
        if mod_periodica:
            add("modulacao_taxa_hz", abs(ma["taxa_hz"] - mb["taxa_hz"]) <= 0.05 * ma["taxa_hz"] + 1e-9, ma["taxa_hz"], mb["taxa_hz"], "5 %")
            add("modulacao_AM_dB_pp", abs(ma["am_pico_a_pico_db"] - mb["am_pico_a_pico_db"]) <= max(0.3, 0.2 * ma["am_pico_a_pico_db"]), ma["am_pico_a_pico_db"], mb["am_pico_a_pico_db"], "max(0,3 dB; 20 %)")
            add("modulacao_FM_cents", abs(ma["fm_pico_cents"] - mb["fm_pico_cents"]) <= max(1.0, 0.2 * ma["fm_pico_cents"]), ma["fm_pico_cents"], mb["fm_pico_cents"], "max(1 cent; 20 %)")
    add("ruido_fundo_dbfs", abs(P["ruido_dbfs"] - R["ruido_dbfs"]) <= 6 or (P["ruido_dbfs"] < -110 and R["ruido_dbfs"] < -110), round(P["ruido_dbfs"], 1), round(R["ruido_dbfs"], 1), "6 dB (ou ambos < -110)")
    pct = round(100 * sum(m["dentro"] for m in M) / len(M), 1)
    return {"pct": pct, "n": len(M), "rt60_pct": round(100 * sum(m["dentro"] for m in M if m["metrica"].startswith("rt60")) / max(1, sum(m["metrica"].startswith("rt60") for m in M)), 1),
            "rt60_erro_max_pct": round(max(rt_err), 2) if rt_err else None, "edc_rms_db": None if rms is None else round(rms, 2), "metricas": M}


def cmp_musica(yp, ye, sr, lim, janela_ms=100.0):
    n = min(yp.shape[1], ye.shape[1])
    yp, ye = yp[:, :n].astype(np.float64), ye[:, :n].astype(np.float64)
    k = min(n, 10 * sr)
    cc = signal.correlate(yp[0, :k], ye[0, :k], "full", method="fft")
    lags = signal.correlation_lags(k, k)
    msk = np.abs(lags) <= 200
    lag = int(lags[msk][np.argmax(cc[msk])])
    if lag:
        ye = np.roll(ye, lag, axis=1)
    W = int(sr * janela_ms / 1000)
    nw = n // W
    res = ye - yp
    wr = np.array([db(np.sqrt((res[:, i * W:(i + 1) * W] ** 2).mean()) / (np.sqrt((yp[:, i * W:(i + 1) * W] ** 2).mean()) + 1e-12)) for i in range(nw)])
    wp = np.array([db(np.sqrt((yp[:, i * W:(i + 1) * W] ** 2).mean())) for i in range(nw)])
    ok = wp > -60
    if not ok.any():
        return {"pct": None, "aviso": "sem janelas com sinal"}
    return {"pct": round(float(100 * (wr[ok] <= lim).mean()), 2), "janelas_validas": int(ok.sum()), "lag_amostras": lag, "limite_db": lim,
            "mediana_janela_db": round(float(np.median(wr[ok])), 2), "p90_janela_db": round(float(np.percentile(wr[ok], 90)), 2),
            "residuo_global_db": round(float(db(np.sqrt((res ** 2).mean()) / (np.sqrt((yp ** 2).mean()) + 1e-12))), 2)}


def carrega_musica(path, sr, ini, dur):
    from pedalboard.io import AudioFile
    with AudioFile(path) as f:
        x = f.read(f.frames).astype(np.float64)
        sr0 = int(f.samplerate)
    x = np.vstack([x, x]) if x.shape[0] == 1 else x[:2]
    if sr0 != sr:
        x = signal.resample_poly(x, sr, sr0, axis=1)
    a = int(ini * sr)
    return x[:, a:a + int(dur * sr)] if dur > 0 else x[:, a:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--py")
    ap.add_argument("--exe")
    ap.add_argument("--out", default="fechamento_out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--componentes", default="regua,estatistico")
    ap.add_argument("--musica")
    ap.add_argument("--inicio", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=10.0)
    ap.add_argument("--limite", type=float, default=-40.0)
    ap.add_argument("--niveis", default="-30,-18,-6")
    ap.add_argument("--freqs", default="110,1000,5000")
    ap.add_argument("--tol-ganho", type=float, default=0.1)
    ap.add_argument("--tol-h", type=float, default=0.005)
    ap.add_argument("--mod-periodica", action="store_true", help="LFO determinístico/periódico (chorus, tremolo): compara taxa e profundidade, não só a estatística")
    ap.add_argument("--alvo", type=float, default=95.0)
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--usar-cache", action="store_true", help="não toca no plugin: lê <out>/ref_plugin.json")
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw")
    ap.add_argument("--settings")
    ap.add_argument("--sem-mix", action="store_true")
    a = ap.parse_args()
    comps = [c for c in a.componentes.split(",") if c]
    niv = [float(v) for v in a.niveis.split(",")]
    frs = [float(v) for v in a.freqs.split(",")]
    warm = 0.5 if a.rapido else 1.0
    if a.rapido:
        niv, frs = niv[::2][:2] or niv, frs[:2]
    os.makedirs(a.out, exist_ok=True)
    cache_f = os.path.join(a.out, "ref_plugin.json")
    t0 = time.time()
    ref = json.load(open(cache_f)) if (a.usar_cache and os.path.exists(cache_f)) else {}
    rec = mc.Recriacao(a.py, a.exe, a.sr) if (a.py or a.exe) else None
    x_mus = carrega_musica(a.musica, a.sr, a.inicio, a.rapido and min(a.dur, 5.0) or a.dur) if "musica" in comps else None
    if not ref or any(c not in ref for c in comps):
        if a.usar_cache:
            sys.exit("--usar-cache: cache ausente/incompleto em " + cache_f)
        pl = mc.Plugin(a.plugin, a.sr, mc.parse_sets(a.set), a.settings, mix_auto=not a.sem_mix)
        ref["ajustes"] = pl.alterados
        pl.proc(np.random.default_rng(1).standard_normal((2, a.sr)).astype(np.float32) * 0.01)
        if "regua" in comps:
            ref["regua"] = m_tons(pl, niv, frs, warm)
        if "resposta" in comps:
            ref["resposta"] = m_ruido(pl)
        if "estatistico" in comps:
            ref["estatistico"] = m_estat(pl, a.rapido)
        if "musica" in comps:
            ref["musica"] = m_musica(pl, x_mus).tolist()
        json.dump(ref, open(cache_f, "w"), default=float)
    R = {"plugin": a.plugin, "recriacao": a.py or a.exe, "sr": a.sr, "componentes": {}, "ajustes_plugin": ref.get("ajustes")}
    if rec is None:
        R["aviso"] = "sem --py/--exe: só o lado do plugin foi medido (cache gravado)"
    else:
        if "regua" in comps:
            R["componentes"]["regua"] = cmp_regua(ref["regua"], m_tons(rec, niv, frs, warm), a.tol_ganho, a.tol_h)
        if "resposta" in comps:
            R["componentes"]["resposta"] = cmp_resposta(ref["resposta"], m_ruido(rec), a.tol_ganho)
        if "estatistico" in comps:
            R["componentes"]["estatistico"] = cmp_estat(ref["estatistico"], m_estat(rec, a.rapido), a.mod_periodica)
        if "musica" in comps:
            R["componentes"]["musica"] = cmp_musica(np.array(ref["musica"]), m_musica(rec, x_mus), a.sr, a.limite)
        pcs = {k: v["pct"] for k, v in R["componentes"].items() if v.get("pct") is not None}
        R["resumo"] = {"pct_por_componente": pcs, "pct_geral": round(float(np.mean(list(pcs.values()))), 1) if pcs else None,
                       "pct_minimo": round(float(min(pcs.values())), 1) if pcs else None, "alvo": a.alvo,
                       "passou": bool(pcs and min(pcs.values()) >= a.alvo)}
    R["tempo_s"] = round(time.time() - t0, 1)
    json.dump(R, open(os.path.join(a.out, "fechamento.json"), "w"), indent=1, ensure_ascii=False, default=float)
    L = [f"# Teste de fechamento: {os.path.basename(a.plugin)} vs {R['recriacao']}", "", f"SR {a.sr}. Alvo {a.alvo} % por componente."]
    if R.get("aviso"):
        L.append(R["aviso"])
    for k, v in R["componentes"].items():
        L += ["", f"## {k}: {v.get('pct')} %"]
        for kk, vv in v.items():
            if kk not in ("pontos", "metricas", "erro_por_banda_db"):
                L.append(f"- {kk}: {vv}")
        for m in v.get("metricas", []):
            L.append(f"  - {'OK ' if m['dentro'] else 'FALHA'} {m['metrica']}: plugin {m['plugin']} vs recriação {m['recriacao']} (tol {m['tolerancia']})")
    if R.get("resumo"):
        L += ["", f"**Resumo**: {R['resumo']}"]
    open(os.path.join(a.out, "fechamento.md"), "w").write("\n".join(L))
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()
