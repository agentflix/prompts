#!/usr/bin/env python3
"""Analisa um delay/eco (pedalboard, regime estável) a partir da resposta a um clique e das repetições.

Mede, por clique estéreo (mono L=R ou só L):
  tempo de atraso T (mediana dos espaços entre ecos, ms; picos de envelope RMS de 1 ms com interpolação parabólica),
  jitter do tempo (desvio-padrão dos espaços, ms: wow/flutter, modulação do tempo) e deriva (1º vs último espaço),
  latência fixa do plugin (instante do 1º eco menos T, quando não há som direto) e presença de direto,
  feedback por repetição (razão de energia entre ecos consecutivos -> ganho linear e dB por repetição),
  filtro NA MALHA: resposta por 1/3 de oitava (razão espectral eco k+1 / eco k, mediana), inclinação em dB/oitava
    (250 Hz a 8 kHz) e fc estimada (-3 dB re 500 Hz-2 kHz): cada repetição fica mais escura?
  saturação/compressão na malha: o ganho por repetição muda entre dois níveis de clique (--nivel-baixo)?
  ping-pong: com entrada só em L (--entrada L), a energia dos ecos alterna entre L e R?
Varredura de parâmetro: --varre PARAM --valores v1,v2,... (raw 0..1): tabela valor mostrado x T medido (taper do
  tempo; sync: ver se o valor segue grade de BPM) e x feedback.
NÃO mede: sync ao BPM do host, ducking, glide de pitch ao mudar o tempo (protocolos em references/por-tipo.md).
Delays < 20 ms (comb/flanger) saem do regime de ecos discretos: use analisa_modulacao.py / captura_ir.py.
Uso (PYTHONPATH=<skill>/scripts):
  analisa_delay.py "/Library/Audio/Plug-Ins/VST3/ValhallaDelay.vst3" --out DIR [--entrada L] [--rapido]
  analisa_delay.py PLUGIN --out DIR --varre delay --valores 0.1,0.3,0.5
Saída: <out>/delay.json e delay.md.
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medidas_comuns as mc

TERCOS = [125 * 2 ** (k / 3) for k in range(0, 21)]          # 125 Hz .. ~16 kHz


def clique(pl, dur, amp_db, so_L, flush=2.5):
    sr = pl.sr
    pl.fx.reset()                                            # zera a malha (cauda do clique anterior); o plugin ignora ajustes ~0,3 s após o reset
    pl.mudo(flush)                           # 1 s de silêncio: ajustes assentam e o pré-clique vira medida de ruído de fundo
    n = int(dur * sr)
    x = np.zeros((2, n), np.float32)
    p = int(0.25 * sr)
    a = 10 ** (amp_db / 20)
    x[0, p] = a
    if not so_L:
        x[1, p] = a
    return pl.proc(x) / a, p


def bandas_potencia(seg, sr):
    w = np.hanning(len(seg))
    P = np.abs(np.fft.rfft(seg * w, 1 << int(np.ceil(np.log2(max(len(seg), 4096)))))) ** 2
    f = np.fft.rfftfreq(2 * (len(P) - 1), 1 / sr)
    out = []
    for c in TERCOS:
        if c * 2 ** (1 / 6) > 0.46 * sr:
            break
        m = (f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))
        out.append(P[m].sum() + 1e-30)
    return np.array(out)


def analisa(y, p, sr, min_eco_ms=20.0, lim_db=-60.0, nmax=8):
    env_in = np.sqrt(y[0] ** 2 + y[1] ** 2)
    pk = mc.acha_ecos(env_in, sr, t0=p / sr - 0.002, limiar_db=lim_db, sep_ms=min_eco_ms, sup_ms=1.0)
    R = {"n_picos": len(pk)}
    if len(pk) < 2:
        R["aviso"] = "menos de 2 picos: aumente --dur, o nível, ou o feedback; ou o plugin não é um delay discreto"
        return R
    tp = np.array([t - p / sr for t, _ in pk])               # tempos relativos ao clique, s
    nv = np.array([v for _, v in pk])
    direto = tp[0] < 0.003
    R["direto_detectado"] = bool(direto)
    sp = np.diff(tp)[:nmax]
    T = float(np.median(sp))
    R["tempo_ms"] = round(T * 1000, 3)
    R["espacos_ms"] = [round(float(v) * 1000, 2) for v in sp]
    R["jitter_ms"] = round(float(sp.std() * 1000), 3)
    R["deriva_ms_primeiro_ultimo"] = round(float((sp[-1] - sp[0]) * 1000), 3)
    R["latencia_fixa_ms"] = round(float((tp[0] - (0.0 if direto else T)) * 1000), 3)
    t1 = tp[1] if direto else tp[0]                          # 1º eco da malha (relativo ao clique)
    R["primeiro_eco_ms"] = round(float(t1 * 1000), 2)
    # energia por eco em grade ancorada no 1º eco (robusto a picos perdidos)
    K = min(nmax, int((len(y[0]) / sr - p / sr - t1) / T))
    seg = lambda k: slice(int(p + (t1 + (k) * T - 0.25 * T) * sr), int(p + (t1 + k * T + 0.75 * T) * sr))
    # piso de ruído do plugin medido no silêncio ANTES do clique (0,2 s): subtraído da energia/espectro de cada janela
    npre = int(0.2 * sr)
    rpow = [float(np.mean(y[c, :npre] ** 2)) for c in range(2)]
    R["ruido_pre_clique_db_re_clique"] = round(float(10 * np.log10(sum(rpow) / 2 + 1e-30)), 1)
    E = np.array([[max(float(np.sum(y[c, seg(k)] ** 2)) - rpow[c] * (seg(k).stop - seg(k).start), 1e-30) for c in range(2)] for k in range(K)]) if K >= 1 else np.zeros((0, 2))
    tot = E.sum(1)
    R["energia_por_eco_db_re_1o"] = [round(float(10 * np.log10(v / tot[0] + 1e-30)), 2) for v in tot]
    ok = [k for k in range(K) if tot[k] > tot[0] * 10 ** (-40 / 10)]
    if len(ok) >= 3:
        r = np.array([10 * np.log10(tot[k + 1] / tot[k]) for k in range(len(ok) - 1) if k + 1 in ok])
        r5 = r[:5]                                                          # só as primeiras repetições (acima do piso de ruído)
        R["feedback_db_por_repeticao"] = round(float(np.median(r5)), 2)      # = 20 log10 (ganho linear)
        R["feedback_ganho_linear"] = round(float(10 ** (np.median(r5) / 20)), 4)
        R["feedback_db_por_repeticao_lista"] = [round(float(v), 2) for v in r]
        # filtro na malha: razão espectral de ecos consecutivos
        pre = y[0, :npre] + y[1, :npre]
        def Pcorr(k):
            sg = seg(k)
            n_ = sg.stop - sg.start
            ruido = bandas_potencia(np.resize(pre, n_), sr)          # mesmo comprimento/janela: ruído de fundo por banda
            return np.maximum(bandas_potencia(y[0, sg] + y[1, sg], sr) - ruido, 1e-30)
        Pk = [Pcorr(k) for k in ok]
        rat = np.array([10 * np.log10(Pk[i + 1] / Pk[i]) for i in range(min(len(Pk) - 1, 4))])
        curva = np.median(rat, axis=0)
        fc = TERCOS[:len(curva)]
        R["filtro_malha_db_por_repeticao"] = {str(round(f)): round(float(v), 2) for f, v in zip(fc, curva)}
        ref = float(np.median([v for f, v in zip(fc, curva) if 500 <= f <= 2000]))
        m = [(np.log2(f), v) for f, v in zip(fc, curva) if 250 <= f <= 8000]
        R["filtro_malha_inclinacao_db_oitava"] = round(float(np.polyfit([a for a, _ in m], [b for _, b in m], 1)[0]), 2)
        queda = [f for f, v in zip(fc, curva) if f > 2000 and v < ref - 3]
        R["filtro_malha_fc_menos3db_hz"] = round(float(queda[0])) if queda else None
        R["filtro_malha_ref_500_2k_db"] = round(ref, 2)
        # alta frequência vs baixa (escurece?)
        R["escurece_a_cada_repeticao"] = bool(R["filtro_malha_inclinacao_db_oitava"] < -0.5)
    else:
        R["aviso_feedback"] = "menos de 3 ecos acima de -40 dB (re 1º eco, após descontar o ruído): feedback/filtro não estimados (suba o feedback ou o nível)"
    # ping-pong: fração L por eco
    fl = [float(E[k, 0] / (E[k].sum() + 1e-30)) for k in range(K)]
    R["fracao_energia_L_por_eco"] = [round(v, 3) for v in fl]
    R["alterna_canais"] = bool(K >= 3 and all((fl[k] - 0.5) * (fl[k + 1] - 0.5) < 0 for k in range(min(K - 1, 5))) and
                               min(abs(v - 0.5) for v in fl[:6]) > 0.1)
    return R


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="delay_out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--dur", type=float, default=6.0, help="janela de gravação em s (>= 5 ecos)")
    ap.add_argument("--rapido", action="store_true", help="dur=4 s, sem teste de segundo nível")
    ap.add_argument("--amp-db", type=float, default=-12.0, help="nível do clique (dBFS)")
    ap.add_argument("--nivel-baixo", type=float, default=-30.0, help="2º nível p/ detectar saturação na malha")
    ap.add_argument("--entrada", choices=["mono", "L"], default="mono")
    ap.add_argument("--assenta", type=float, default=2.5, help="s de silêncio após reset/mudança de parâmetro antes do clique (glide do tempo)")
    ap.add_argument("--min-eco-ms", type=float, default=20.0)
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw")
    ap.add_argument("--settings")
    ap.add_argument("--varre")
    ap.add_argument("--valores", default="0.1,0.3,0.5")
    ap.add_argument("--sem-mix", action="store_true")
    a = ap.parse_args()
    if a.rapido:
        a.dur = min(a.dur, 4.0)
    t0 = time.time()
    pl = mc.Plugin(a.plugin, a.sr, mc.parse_sets(a.set), a.settings, mix_auto=not a.sem_mix)
    R = {"plugin": a.plugin, "nome": pl.nome, "sr": a.sr, "ajustes": pl.alterados, "mix_param": pl.mix_param, "medidas": []}
    jobs = [("base", None, None)]
    if a.varre:
        nome = a.varre if a.varre in pl.P.keys() else pl.achar(a.varre.lower())
        if not nome:
            sys.exit(f"parâmetro '{a.varre}' não encontrado. Disponíveis: {list(pl.P.keys())[:40]}")
        jobs = [(f"{nome}={v}", nome, float(v)) for v in a.valores.split(",")]
    for tag, nome, v in jobs:
        if nome:
            pl.setp(**{nome: v})
        y, p = clique(pl, a.dur, a.amp_db, a.entrada == "L", a.assenta)
        M = {"tag": tag, "analise": analisa(y, p, a.sr, a.min_eco_ms)}
        if nome:
            M["valor_texto"] = pl.P[nome].string_value
        if not a.rapido and "feedback_db_por_repeticao" in M["analise"]:
            y2, p2 = clique(pl, a.dur, a.nivel_baixo, a.entrada == "L", a.assenta)
            A2 = analisa(y2, p2, a.sr, a.min_eco_ms)
            if "feedback_db_por_repeticao" in A2:
                d = A2["feedback_db_por_repeticao"] - M["analise"]["feedback_db_por_repeticao"]
                M["nivel_baixo"] = {"nivel_dbfs": a.nivel_baixo, "feedback_db_por_repeticao": A2["feedback_db_por_repeticao"],
                                    "tempo_ms": A2.get("tempo_ms"), "dif_feedback_db": round(d, 2),
                                    "indicio_saturacao_ou_compressao_na_malha": bool(abs(d) > 1.0)}
        R["medidas"].append(M)
    R["tempo_s"] = round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(R, open(os.path.join(a.out, "delay.json"), "w"), indent=1, ensure_ascii=False, default=float)
    L = [f"# Análise de delay: {R['nome']}", "", f"SR {a.sr} Hz; entrada {a.entrada}; clique {a.amp_db} dBFS; janela {a.dur} s. Ajustes: {R['ajustes']}", "",
         "| ajuste | valor | T medido ms | jitter ms | latência ms | feedback dB/rep | ganho lin | fc malha Hz | inclin. dB/oit | alterna L/R | indício sat. malha |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for M in R["medidas"]:
        A = M["analise"]
        g = lambda k: A.get(k, "-")
        L.append(f"| {M['tag']} | {M.get('valor_texto', '')} | {g('tempo_ms')} | {g('jitter_ms')} | {g('latencia_fixa_ms')} | {g('feedback_db_por_repeticao')} | "
                 f"{g('feedback_ganho_linear')} | {g('filtro_malha_fc_menos3db_hz')} | {g('filtro_malha_inclinacao_db_oitava')} | {g('alterna_canais')} | "
                 f"{M.get('nivel_baixo', {}).get('indicio_saturacao_ou_compressao_na_malha', '-')} |")
    L.append("")
    for M in R["medidas"]:
        A = M["analise"]
        L += [f"## {M['tag']} {M.get('valor_texto', '')}"] + [f"- {k}: {v}" for k, v in A.items()]
        if M.get("nivel_baixo"):
            L.append(f"- nível baixo: {M['nivel_baixo']}")
        L.append("")
    open(os.path.join(a.out, "delay.md"), "w").write("\n".join(L))
    print("\n".join(L[:6 + len(R["medidas"])]))


if __name__ == "__main__":
    main()
