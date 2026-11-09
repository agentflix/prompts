#!/usr/bin/env python3
"""Classifica o SISTEMA de um plugin de efeito por testes empíricos curtos (pedalboard, regime estável).

Decide em quais classes o plugin cai (pode cair em várias) e recomenda os protocolos de medição:
  (a) linear e invariante no tempo (LTI)     ganho independente do nível, sem harmônicas, sem modulação
  (b) não linear SEM memória                 curva estática: THD/ganho dependem do nível; assenta em poucos ms
  (c) não linear COM memória                 compressão/histerese: ganho leva dezenas de ms+ para assentar
  (d) variante no tempo / modulado           bandas laterais (AM/FM) num tom puro; IR muda com o deslocamento
  (e) com malha de realimentação             cauda longa na IR e/ou ecos discretos periódicos
  (f) estocástico                            ruído com entrada muda; saídas diferentes para a mesma entrada e estado
Cada classe sai com veredito sim / não / inconclusivo, evidência numérica e limiar usado. Dúvida = "inconclusivo".

Testes (~25-40 s de áudio por plugin; 1 reset no início, depois reset=False; aquecimento antes de cada medida):
  T1 tom 1 kHz em 3 níveis: ganho e harmônicas por nível (bin exato)      -> (a)(b)
  T2 ruído em 2 níveis: |H(f)| e coerência (homogeneidade)                -> (a)(b), apoio
  T3 degrau de nível +24 dB e volta: tempo de assentamento do ganho       -> (b) vs (c)
  T4 tom estável: demodulação AM/FM (bandas laterais, pico de LFO)        -> (d)
  T5 cliques separados e deslocados: cauda, ecos, invariância ao deslocamento -> (e) (a)(d)
  T6 mesma entrada após reset, 2x; depois com estado livre; entrada muda  -> (f) (d)
Efeito 100 % molhado: se existir um parâmetro "mix", é posto em 1,0 (use --sem-mix para não mexer).
Uso: PYTHONPATH=<skill>/scripts python classificar_sistema.py "/Library/Audio/Plug-Ins/VST3/X.vst3" --out DIR [--rapido]
     [--set nome=raw ...] [--settings s.json] [--niveis -30,-18,-6] [--sr 48000]
Saída: <out>/classificacao.json e classificacao.md. Instrumentos (MIDI) não são tratados (n/a).
"""
import argparse, json, os, sys, time
import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medidas_comuns as mc

db = mc.db


# ------------------------------------------------------------------ testes
def t1_tons(pl, niveis, f0, warm, meas):
    sr = pl.sr
    res = []
    for L in list(niveis) + [niveis[0]]:                       # o último repete o 1º nível: linha de base de repetibilidade
        x = mc.tom(sr, f0, L, warm + meas)                       # fluxo contínuo: aquece e mede no mesmo sinal
        y = pl.proc(x)[0]
        seg = y[int(warm * sr):]
        h1, hs = mc.tom_analise(seg, sr, f0)
        thd = float(np.sqrt(sum((v or 0) ** 2 for v in hs)))
        res.append({"nivel_dbfs": L, "ganho_db": round(float(db(h1 / 10 ** (L / 20))), 3),
                    "harm_dbc": [round(float(db(v)), 1) if v else None for v in hs],
                    "thd_dbc": round(float(db(thd)), 1),
                    "dc": float(seg.mean())})
    return res


def t2_ruido(pl, niveis, warm, meas, seed=11):
    sr = pl.sr
    rng = np.random.default_rng(seed)
    base = rng.standard_normal(int((warm + meas) * sr))
    out = {}
    H = {}
    for L in list(niveis) + [niveis[0]]:
        x = (base * 10 ** (L / 20) / np.std(base)).astype(np.float32)
        x = np.clip(x, -1, 1)
        y = pl.proc(np.vstack([x, x]))[0]
        xs, ys = x[int(warm * sr):], y[int(warm * sr):]
        nps = 8192
        f, pxx = signal.welch(xs, sr, nperseg=nps)
        _, pyy = signal.welch(ys, sr, nperseg=nps)
        _, pxy = signal.csd(xs, ys, sr, nperseg=nps)
        H[len(H)] = (f, np.abs(pxy / (pxx + 1e-30)), np.abs(pxy) ** 2 / (pxx * pyy + 1e-30), L)
    ks = list(H)
    f = H[0][0]
    cs = [100 * 2 ** (k / 3) for k in range(0, 21) if 100 * 2 ** (k / 3) < min(8000, sr / 2.2)]
    banda = lambda c: (f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))
    gb = lambda k, c: db(np.mean(H[k][1][banda(c)]))
    niv_k = ks[:-1]                                              # níveis distintos; ks[-1] repete o 1º
    dev = [float(max(gb(k, c) for k in niv_k) - min(gb(k, c) for k in niv_k)) for c in cs]
    rep = [float(abs(gb(ks[-1], c) - gb(ks[0], c))) for c in cs]
    m = (f >= 100) & (f <= 8000)
    out["desvio_max_H_entre_niveis_db"] = round(max(dev), 3)
    out["desvio_mediano_H_db"] = round(float(np.median(dev)), 3)
    out["repetibilidade_mediana_H_db"] = round(float(np.median(rep)), 3)
    out["coerencia_media_100_8k"] = {str(H[k][3]): round(float(np.mean(H[k][2][m])), 4) for k in niv_k}
    return out


def t3_degrau(pl, f0, lo, hi, seg_s):
    """tom em lo, sobe para hi, volta para lo; ganho por janelas de 5 ciclos (5 ms a 1 kHz)."""
    sr = pl.sr
    x = np.concatenate([mc.tom(sr, f0, lo, seg_s)[0], mc.tom(sr, f0, hi, seg_s)[0], mc.tom(sr, f0, lo, seg_s)[0]])
    amp = np.concatenate([np.full(int(seg_s * sr), 10 ** (lo / 20)), np.full(int(seg_s * sr), 10 ** (hi / 20)),
                          np.full(int(seg_s * sr), 10 ** (lo / 20))])
    # aquecimento no nível baixo (mesmo sinal) para o estado assentar antes do degrau
    pl.proc(np.tile(mc.tom(sr, f0, lo, 1.5)[0], (2, 1)))
    y = pl.proc(np.vstack([x, x]))[0]
    W = int(round(5 * sr / f0))
    n = len(y) // W
    g = np.array([abs(mc.fasor(y[i * W:(i + 1) * W], f0, sr)) / amp[i * W:(i + 1) * W].mean() for i in range(n)])
    gdb = db(g)
    ns = int(seg_s * sr / W)

    def assenta(i0, i1, tol=0.1):
        seg = gdb[i0:i1]
        fin = float(np.mean(seg[-max(2, int(0.1 * sr / W)):]))
        ruim = np.where(np.abs(seg - fin) > tol)[0]
        t = (int(ruim[-1]) + 1) * W / sr * 1000 if len(ruim) else 0.0
        return fin, t, float(seg[0] - fin)
    fin_s, t_s, salto_s = assenta(ns, 2 * ns)
    fin_d, t_d, salto_d = assenta(2 * ns, 3 * ns)
    fin_0 = float(np.mean(gdb[max(0, ns - 20):ns - 2]))
    return {"ganho_final_nivel_baixo_db": round(fin_0, 3), "ganho_final_nivel_alto_db": round(fin_s, 3),
            "ganho_final_volta_db": round(fin_d, 3),
            "assenta_subida_ms": round(t_s, 1), "assenta_descida_ms": round(t_d, 1),
            "salto_1a_janela_subida_db": round(salto_s, 3), "salto_1a_janela_descida_db": round(salto_d, 3),
            "histerese_volta_vs_inicio_db": round(fin_d - fin_0, 3),
            "janela_ms": round(1000 * W / sr, 2), "degrau_db": hi - lo}


def t4_modulacao(pl, f0, nivel, warm, meas):
    sr = pl.sr
    y = pl.proc(mc.tom(sr, f0, nivel, warm + meas))
    y = y[:, int(warm * sr):]
    d = mc.demod_tom(y, sr, f0)
    c = d["canais"][0]
    return {"canal0": c, "fase_L_R_graus": d.get("fase_L_R_graus")}


def t5_impulsos(pl, cauda, amp=0.5):
    """cliques em t=0,25 s e 0,25+cauda s (+37 amostras): cauda, ecos discretos, invariância ao deslocamento"""
    sr = pl.sr
    pl.mudo(min(cauda, 3.0))                                    # limpa a cauda anterior
    p1 = int(0.25 * sr)
    p2 = p1 + int(cauda * sr) + 37
    n = p2 + int(min(cauda, 1.0) * sr) + int(0.25 * sr)
    x = np.zeros((2, n), np.float32)
    x[:, p1] = amp
    x[:, p2] = amp
    y = pl.proc(x)[0] / amp
    r1 = y[p1:p1 + int(cauda * sr)]
    # cauda: envelope em 10 ms
    ev = mc.envelope_db(r1, sr, 10.0)
    pk = int(np.argmax(ev))
    piso = float(np.median(ev[-max(3, len(ev) // 10):]))
    ok = np.where(ev > max(piso + 6, -70))[0]
    cauda_ms = float(10 * (ok[-1] - pk)) if len(ok) else 0.0
    # tempo para -30 dB
    t30 = np.where(ev[pk:] < -30)[0]
    t_m30 = float(10 * t30[0]) if len(t30) else None
    ecos = mc.acha_ecos(r1, sr, t0=0.02, limiar_db=-45, sep_ms=5.0)
    per, razao = None, None
    if len(ecos) >= 2:
        tt = np.array([e[0] for e in ecos])
        per = float(np.median(np.diff(tt)) * 1000)
        nv = np.array([e[1] for e in ecos])
        razao = float(np.median(np.diff(nv)))
    # densidade: nº de picos por 100 ms nos primeiros 300 ms (reverb: muitos; delay: poucos)
    ecos_100ms = len([e for e in ecos if e[0] < 0.3]) / 3.0
    if ecos_100ms > 3:                                          # cauda difusa (reverb): "período" não tem sentido
        per, razao = None, None
    # invariância ao deslocamento: 100 ms após cada clique, alinhados pelo pico
    L = int(0.1 * sr)
    a = y[p1:p1 + L]
    b = y[p2:p2 + L]
    ia, ib = int(np.argmax(np.abs(a))), int(np.argmax(np.abs(b)))
    a = y[p1 + ia - 16:p1 + ia - 16 + L]
    b = y[p2 + ib - 16:p2 + ib - 16 + L]
    inv = float(db(np.sqrt(np.mean((a - b) ** 2)) / (np.sqrt(np.mean(a ** 2)) + 1e-30)))
    resid = float(db(np.sqrt(np.mean(y[p2 - int(0.05 * sr):p2] ** 2)) / (np.sqrt(np.mean(a ** 2)) + 1e-30)))
    return {"cauda_ms": round(cauda_ms, 1), "tempo_ate_-30dB_ms": t_m30, "piso_db_rel_pico": round(piso, 1),
            "n_ecos_discretos": len(ecos), "tipo_cauda": "difusa" if ecos_100ms > 3 else "discreta", "periodo_ecos_ms": None if per is None else round(per, 2),
            "queda_db_por_eco": None if razao is None else round(razao, 2), "ecos_por_100ms": round(ecos_100ms, 2),
            "invariancia_deslocamento_db": round(inv, 1), "residuo_cauda_antes_clique2_db": round(resid, 1),
            "cauda_disponivel_s": cauda}


def t6_estocastico(pl, dur=0.4, cauda=1.5, amp_db=-20, pre=0.5):
    sr = pl.sr
    rng = np.random.default_rng(5)
    n0 = int(pre * sr)                                          # silêncio pós-reset (o plugin ignora ajustes ~0,3 s)
    x = np.zeros((2, n0 + int((dur + cauda) * sr)), np.float32)
    ruido = (rng.standard_normal(int(dur * sr)) * 10 ** (amp_db / 20)).astype(np.float32)
    x[:, n0:n0 + len(ruido)] = ruido
    n = int(dur * sr)

    def ciclo(reset):
        if reset:
            pl.fx.reset()
        return pl.proc(x)[:, n0:]
    nulo = lambda a, b, N: float(db(np.sqrt(np.mean((a[:, :N] - b[:, :N]) ** 2)) / (np.sqrt(np.mean(a[:, :N] ** 2)) + 1e-30)))
    ya = ciclo(True)
    yb = ciclo(True)
    yc = ciclo(False)                                          # sem reset: estado livre (LFO/ruído seguiram)
    N = n + int(0.3 * sr)
    leftover = float(db(np.sqrt(np.mean(ya[:, -int(0.2 * sr):] ** 2)) / (np.sqrt(np.mean(ya[:, :n] ** 2)) + 1e-30)))
    out = {"nulo_reset_vs_reset_db": round(nulo(ya, yb, N), 1), "nulo_reset_vs_livre_db": round(nulo(ya, yc, N), 1),
           "sobra_cauda_antes_db": round(leftover, 1)}
    # entrada muda: ruído de fundo (descarta a cauda do bloco anterior)
    pl.mudo(2.0)
    z = pl.proc(np.zeros((2, int(1.0 * sr)), np.float32))
    out["ruido_entrada_muda_dbfs"] = round(float(db(np.sqrt(np.mean(z ** 2)))), 1)
    return out


# ------------------------------------------------------------------ vereditos
def decide(r, lim):
    t1, t2, t3, t4, t5, t6 = (r.get(k) for k in ("T1_tons", "T2_ruido", "T3_degrau", "T4_modulacao", "T5_impulsos", "T6_estocastico"))
    V = {}

    # ---- não linearidade (base de a, b, c)
    nl_ev, nl_pro, nl_con = [], 0, 0
    var_alta = False                                             # medida não repetível: NL não é separável de modulação/ruído
    if t1:
        base = t1[:-1]
        g = [x["ganho_db"] for x in base]
        spread = max(g) - min(g)
        rep_g = abs(t1[-1]["ganho_db"] - t1[0]["ganho_db"])
        thd_hi, thd_lo, thd_rep = base[-1]["thd_dbc"], base[0]["thd_dbc"], t1[-1]["thd_dbc"]
        nl_ev.append(f"ganho do tom varia {spread:.3f} dB entre {base[0]['nivel_dbfs']} e {base[-1]['nivel_dbfs']} dBFS "
                     f"(repetindo o 1º nível: {rep_g:.3f} dB)")
        nl_ev.append(f"THD {thd_lo:.1f} dBc no nível baixo (repetição {thd_rep:.1f}), {thd_hi:.1f} dBc no alto")
        if rep_g > lim["ganho_nl_db"]:
            var_alta = True
            nl_ev.append("o próprio 1º nível não se repete: sistema modulado/estocástico mascara a não linearidade; evidência de NL descartada")
        else:
            piso_thd = max(thd_lo, thd_rep)
            if thd_hi > lim["thd_nl_dbc"] and thd_hi - piso_thd > 6:
                nl_pro += 2
            elif thd_hi < lim["thd_lin_dbc"] and spread < lim["ganho_lin_db"]:
                nl_con += 2
            if spread > max(lim["ganho_nl_db"], 3 * rep_g):
                nl_pro += 1
            elif spread < lim["ganho_lin_db"]:
                nl_con += 1
    if t2 and not var_alta:
        d, r_ = t2["desvio_mediano_H_db"], t2["repetibilidade_mediana_H_db"]
        nl_ev.append(f"|H(f)| de ruído difere {d:.3f} dB (mediana por banda) entre os níveis; repetindo o mesmo nível: {r_:.3f} dB")
        if d > max(lim["ganho_nl_db"], 3 * r_):
            nl_pro += 1
        elif d < lim["ganho_lin_db"]:
            nl_con += 1
    if nl_pro >= 2:
        nl = "sim"
    elif nl_pro == 0 and nl_con >= 2:
        nl = "nao"
    elif nl_pro >= 1 and nl_con == 0:
        nl = "sim"
    else:
        nl = "inconclusivo"
    if var_alta:
        nl = "inconclusivo"
    V["_nao_linear"] = {"veredito": nl, "evidencia": nl_ev}

    # ---- memória de dinâmica (c vs b)
    mem, mem_ev = "inconclusivo", []
    if t3:
        t = max(t3["assenta_subida_ms"], t3["assenta_descida_ms"])
        mem_ev.append(f"ganho assenta em {t3['assenta_subida_ms']} ms (subida) e {t3['assenta_descida_ms']} ms (descida) "
                      f"após degrau de {t3['degrau_db']} dB (janela {t3['janela_ms']} ms)")
        mem_ev.append(f"ganho final: {t3['ganho_final_nivel_baixo_db']} dB (baixo) vs {t3['ganho_final_nivel_alto_db']} dB (alto); "
                      f"volta ao baixo: {t3['ganho_final_volta_db']} dB")
        mem = "sim" if t > lim["memoria_ms"] else "nao"
    ml = t3 and (abs(t3["ganho_final_nivel_alto_db"] - t3["ganho_final_nivel_baixo_db"]) > lim["ganho_nl_db"]
                 or abs(t3["histerese_volta_vs_inicio_db"]) > lim["ganho_nl_db"])
    cauda_longa = bool(t5 and t5["cauda_ms"] > lim["cauda_ms"])

    def v(valor, ev, nota=None):
        d = {"veredito": valor, "evidencia": ev}
        if nota:
            d["nota"] = nota
        return d

    # ---- (a) LTI
    # ---- (d) variante no tempo
    d_ev, d_pro, d_con = [], 0, 0
    if t4:
        c = t4["canal0"]
        d_ev.append(f"tom puro: bandas laterais {c['banda_lateral_dbc']} dBc, LFO {c['taxa_hz']} Hz "
                    f"(proeminência {c['proeminencia_db']} dB, fonte {c['fonte_dominante']}, AM {c['am_pico_a_pico_db']} dB pp, FM {c['fm_pico_cents']} cents)")
        if c["banda_lateral_dbc"] > lim["mod_dbc"] and c["proeminencia_db"] > 12:
            d_pro += 2
        elif c["banda_lateral_dbc"] > lim["mod_dbc"]:
            d_pro += 1                                          # modulação aperiódica/ruidosa
        elif c["banda_lateral_dbc"] < lim["mod_nao_dbc"]:
            d_con += 2
    if t5:
        d_ev.append(f"IR deslocada difere {t5['invariancia_deslocamento_db']} dB (100 ms após o clique); "
                    f"resíduo da cauda anterior {t5['residuo_cauda_antes_clique2_db']} dB")
        if t5["residuo_cauda_antes_clique2_db"] > -40:
            d_ev.append("cauda anterior ainda alta: teste de deslocamento descartado")
        elif t5["invariancia_deslocamento_db"] > lim["inv_dB"]:
            d_pro += 1
        elif t5["invariancia_deslocamento_db"] < lim["inv_ok_dB"]:
            d_con += 1
    dv = "sim" if d_pro >= 2 or (d_pro >= 1 and d_con == 0) else ("nao" if d_con >= 2 and d_pro == 0 else "inconclusivo")
    V["d_variante_no_tempo"] = v(dv, d_ev, "AM/FM em tom puro: um efeito que só muda de ganho por nível (compressor) NÃO deve aparecer aqui"
                                 if dv == "sim" else None)

    # ---- (e) realimentação
    e_ev, ev_ = [], "inconclusivo"
    if t5:
        e_ev.append(f"cauda {t5['cauda_ms']} ms acima do piso; ecos discretos {t5['n_ecos_discretos']}"
                    + (f", período {t5['periodo_ecos_ms']} ms, queda {t5['queda_db_por_eco']} dB/eco" if t5['periodo_ecos_ms'] else "")
                    + f"; {t5['ecos_por_100ms']} picos/100 ms nos 300 ms iniciais")
        if t5["cauda_ms"] >= lim["cauda_ms"] or t5["n_ecos_discretos"] >= 3:
            ev_ = "sim"
        elif t5["cauda_ms"] < lim["cauda_ms"] and t5["n_ecos_discretos"] <= 1:
            ev_ = "nao"
            if t5["cauda_ms"] > lim["cauda_nao_ms"]:
                e_ev.append("cauda de 100-250 ms sem ecos: típica de passa-altas de DC, filtro ressonante ou fase linear (resposta linear longa, não malha de realimentação)")
        if ev_ == "sim" and t5["cauda_ms"] >= 0.95 * 1000 * t5["cauda_disponivel_s"]:
            e_ev.append("a cauda não terminou na janela medida: aumente --cauda")
    V["e_realimentacao"] = v(ev_, e_ev)

    # ---- (f) estocástico / determinismo
    f_ev, f_pro, f_con = [], 0, 0
    if t6:
        f_ev.append(f"mesma entrada após reset 2x: nulo {t6['nulo_reset_vs_reset_db']} dB; sem reset (estado livre): {t6['nulo_reset_vs_livre_db']} dB "
                    f"(cauda restante {t6['sobra_cauda_antes_db']} dB)")
        f_ev.append(f"ruído com entrada muda: {t6['ruido_entrada_muda_dbfs']} dBFS")
        if t6["nulo_reset_vs_reset_db"] > lim["det_dB"]:
            f_pro += 2
        elif t6["nulo_reset_vs_reset_db"] < lim["det_ok_dB"]:
            f_con += 1
        if t6["ruido_entrada_muda_dbfs"] > lim["ruido_dbfs"]:
            f_pro += 1
        elif t6["ruido_entrada_muda_dbfs"] < lim["ruido_ok_dbfs"]:
            f_con += 1
    fv = "sim" if f_pro >= 2 else ("nao" if f_con >= 2 and f_pro == 0 else "inconclusivo")
    nota_f = None
    if t6 and fv != "sim" and t6["nulo_reset_vs_livre_db"] > max(-60, t6["sobra_cauda_antes_db"] + 10):
        nota_f = ("determinístico após reset, mas o estado livre difere: LFO/fase corrente ou semente que reinicia no reset "
                  "(variante no tempo, não estocástico estrito)")
    if fv == "sim" and t4 and t4["canal0"]["proeminencia_db"] > 20 and t4["canal0"]["banda_lateral_dbc"] > lim["mod_dbc"]:
        nota_f = ("o pedalboard reset() não reinicia a fase de LFO/semente de todos os plugins: 'sim' aqui pode ser LFO periódico livre "
                  f"(pico a {t4['canal0']['taxa_hz']} Hz, proeminência {t4['canal0']['proeminencia_db']} dB) e não ruído; "
                  "decidir pela estatística da modulação (analisa_modulacao.py): periódica = determinística livre, aperiódica = estocástica")
    V["f_estocastico"] = v(fv, f_ev, nota_f)

    # ---- (b)(c)
    if nl == "sim":
        bv = "nao" if mem == "sim" else ("sim" if mem == "nao" else "inconclusivo")
        cv = "sim" if mem == "sim" else ("nao" if mem == "nao" else "inconclusivo")
        nota = None
        if mem == "sim" and cauda_longa:
            cv, nota = "inconclusivo", "assentamento longo pode ser a cauda linear (e), não dinâmica: confirmar com 2 degraus (+12/+24 dB) e normalizar"
    elif nl == "nao":
        bv = cv = "nao"
        nota = None
    else:
        bv = cv = "inconclusivo"
        nota = None
    V["b_nao_linear_sem_memoria"] = v(bv, nl_ev + (mem_ev if bv != "nao" else []))
    V["c_nao_linear_com_memoria"] = v(cv, nl_ev + mem_ev, nota)
    V["a_linear_invariante"] = None
    # (a): linear E invariante. Estocástico/variante no tempo reprovam.
    if nl == "sim" or dv == "sim" or fv == "sim":
        av, a_ev = "nao", [f"reprovado por: {', '.join(n for n, x in (('não linearidade', nl), ('variância no tempo', dv), ('estocástico', fv)) if x == 'sim')}"]
    elif nl == "nao" and dv == "nao" and fv != "inconclusivo":
        av, a_ev = "sim", nl_ev + d_ev[:1]
    else:
        av, a_ev = "inconclusivo", nl_ev
    V["a_linear_invariante"] = v(av, a_ev)
    return V


PROTOCOLOS = {
    "a_linear_invariante": ["resposta ao impulso/ESS e magnitude+fase (por-tipo EQ/filtro); null vs recriação; coloração = THD em +12 dB de ganho"],
    "b_nao_linear_sem_memoria": ["curva estática por tom e domínio do tempo; harmonicos_vs_nivel_freq.py (THD por nível e frequência; IMD); "
                                  "ficha_comportamento.py; validar_modelo.py com hold-out; aliasing/oversampling"],
    "c_nao_linear_com_memoria": ["degrau de nível (attack/release, 63 %); curva estática em regime; detector (pico/RMS), sidechain HPF; "
                                 "harmonicos_vs_nivel_freq.py com GR ≠ 0; dois tons (IMD) para histerese; música no fechamento"],
    "d_variante_no_tempo": ["analisa_modulacao.py (taxa, profundidade, forma, fase estéreo; varrer o knob de taxa); IR em dois instantes (captura_ir.py --repete 2)"],
    "e_realimentacao": ["captura_ir.py (reverb: RT60 por oitava, EDC, NED, IACC; varrer decay) ou analisa_delay.py (tempo, feedback, filtro e saturação na malha)"],
    "f_estocastico": ["comparar ESTATÍSTICAS, não amostras: EDC/RT60, NED, espectro da cauda, IACC, estatística de modulação; "
                      "teste_fechamento.py --componentes estatistico; medir o ruído de fundo (espectro) separadamente"],
}


def limiares(rapido):
    return {"thd_nl_dbc": -60.0, "thd_lin_dbc": -75.0, "ganho_nl_db": 0.25, "ganho_lin_db": 0.08,
            "memoria_ms": 40.0, "cauda_ms": 250.0, "cauda_nao_ms": 100.0,
            "mod_dbc": -60.0, "mod_nao_dbc": -70.0, "inv_dB": -35.0, "inv_ok_dB": -55.0,
            "det_dB": -60.0, "det_ok_dB": -100.0, "ruido_dbfs": -80.0, "ruido_ok_dbfs": -95.0}


def md(R):
    M = [f"# Classificação do sistema: {R['nome']}", "",
         f"SR {R['sr']} Hz, regime estável (1 reset, reset=False), tempo de medição {R['tempo_s']} s. "
         f"Ajustes: {R['ajustes'] or 'padrão de fábrica'}" + (f"; mix auto = {R['mix_param']} em 1.0" if R.get('mix_param') else ""), ""]
    if R.get("aviso"):
        return "\n".join(M + [R["aviso"]])
    M += ["| classe | veredito |", "|---|---|"]
    for k, v in R["classes"].items():
        M.append(f"| {k} | **{v['veredito']}** |")
    M.append("")
    for k, v in R["classes"].items():
        M.append(f"## {k}: {v['veredito']}")
        M += [f"- {e}" for e in v["evidencia"]]
        if v.get("nota"):
            M.append(f"- nota: {v['nota']}")
        M.append("")
    M += ["## Protocolos recomendados", ""] + [f"- {p}" for p in R["protocolos"]] + [""]
    M += ["## Limiares usados", "", "```", json.dumps(R["limiares"]), "```", ""]
    M.append("Veredito 'inconclusivo' = a evidência não separa as hipóteses; medir mais (ver protocolos), não assumir.")
    return "\n".join(M)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="classificacao_out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw", help="parâmetros em raw 0..1")
    ap.add_argument("--settings", help="JSON {param: raw}")
    ap.add_argument("--sem-mix", action="store_true", help="não forçar mix=100 %%")
    ap.add_argument("--niveis", default="-30,-18,-6", help="níveis do tom em dBFS (crescentes)")
    ap.add_argument("--freq", type=float, default=1000.0, help="tom (Hz inteiro; 1000 = bin exato com janela de 1 s)")
    ap.add_argument("--cauda", type=float, default=3.0, help="duração da janela de cauda/ecos em s")
    ap.add_argument("--rapido", action="store_true", help="metade do tempo: aquecimentos/janelas menores, cauda 1,5 s")
    ap.add_argument("--so", default="", help="roda só estes testes (T1,T2,...), separados por vírgula")
    a = ap.parse_args()
    t0 = time.time()
    pl = mc.Plugin(a.plugin, a.sr, mc.parse_sets(a.set), a.settings, mix_auto=not a.sem_mix)
    R = {"plugin": a.plugin, "nome": pl.nome, "sr": a.sr, "ajustes": pl.alterados, "mix_param": pl.mix_param, "limiares": limiares(a.rapido)}
    if getattr(pl.fx, "is_instrument", False):
        R["aviso"] = "instrumento (MIDI): classificação de efeito não se aplica (por-tipo.md, sintetizador)"
        R["classes"], R["protocolos"] = {}, []
    else:
        quer = set(a.so.split(",")) if a.so else {"T1", "T2", "T3", "T4", "T5", "T6"}
        warm, meas = (0.5, 1.0) if a.rapido else (1.0, 1.0)
        niv = [float(v) for v in a.niveis.split(",")]
        cauda = 1.5 if a.rapido else a.cauda
        # aquecimento geral: o 2º process() em diante vale; ~1 s de ruído baixo após o reset
        pl.proc(np.random.default_rng(1).standard_normal((2, a.sr)).astype(np.float32) * 0.01)
        passos = [("T1_tons", "T1", lambda: t1_tons(pl, niv, a.freq, warm, meas)),
                  ("T2_ruido", "T2", lambda: t2_ruido(pl, [niv[0], niv[-1]], 0.5 if a.rapido else 1.0, 2.0 if a.rapido else 3.0)),
                  ("T3_degrau", "T3", lambda: t3_degrau(pl, a.freq, niv[0], niv[-1] if niv[-1] - niv[0] <= 30 else niv[0] + 24, 0.4 if a.rapido else 0.6)),
                  ("T4_modulacao", "T4", lambda: t4_modulacao(pl, a.freq, niv[1] if len(niv) > 1 else niv[0], 1.0, 3.0 if a.rapido else 5.0)),
                  ("T5_impulsos", "T5", lambda: t5_impulsos(pl, cauda)),
                  ("T6_estocastico", "T6", lambda: t6_estocastico(pl))]
        for nome, k, fn in passos:
            if k in quer:
                try:
                    R[nome] = fn()
                except Exception as e:
                    R[nome] = None
                    R.setdefault("erros", {})[nome] = f"{type(e).__name__}: {e}"
                    print(f"[{nome}] falhou: {e}", file=sys.stderr)
        V = decide(R, R["limiares"])
        R["nao_linear_base"] = V.pop("_nao_linear")
        R["classes"] = V
        R["protocolos"] = []
        for k, v in V.items():
            if v["veredito"] in ("sim", "inconclusivo"):
                R["protocolos"] += [f"[{k}{' (inconclusivo)' if v['veredito'] == 'inconclusivo' else ''}] {p}" for p in PROTOCOLOS[k]]
        if not R["protocolos"]:
            R["protocolos"] = ["nenhuma classe afirmada: repetir com ajustes mais fortes (mais drive/ganho/mix) antes de concluir"]
    R["tempo_s"] = round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(R, open(os.path.join(a.out, "classificacao.json"), "w"), indent=1, ensure_ascii=False, default=float)
    txt = md(R)
    open(os.path.join(a.out, "classificacao.md"), "w").write(txt)
    print("\n".join(txt.split("\n")[:14]))


if __name__ == "__main__":
    main()
