#!/usr/bin/env python3
"""Captura e análise da resposta ao impulso (IR) de reverb/efeito com cauda, em regime estável (pedalboard).

Método padrão: varredura senoidal exponencial (Farina) estéreo + deconvolução -> IR linear (a distorção
vai para lag negativo e é descartada). Alternativa: --metodo impulso (clique; robusto a variância no tempo).
Análise por IR (L e R): pré-atraso, RT60 por oitava (125 Hz-8 kHz) por T30/T20/EDT sobre a curva de decaimento
de energia de Schroeder (com correção do piso de ruído), faixa dinâmica da EDC, densidade de ecos normalizada
(NED, Abel-Huang; tempo até NED=1), IACC precoce (0-80 ms) e tardio por banda, espectro da cauda por oitava,
simetria L/R de energia, piso de ruído. --repete N captura N vezes e mede a variância entre capturas
(correlação da IR precoce e diferença de RT60): IR que muda = modulação/aleatoriedade.
Varredura de parâmetro: --varre PARAM --valores 0.1,0.5,0.9 (raw 0..1) -> tabela RT60 por banda vs valor
(taper de decay/size/damping). Uma captura leva ~(T + 2*cauda) s de áudio por valor (flush + captura).
Uso (PYTHONPATH=<skill>/scripts):
  captura_ir.py "/Library/Audio/Plug-Ins/VST3/ValhallaRoom.vst3" --out DIR --varre decay --valores 0.1,0.5,0.9 --rapido
  captura_ir.py PLUGIN --out DIR --set decay=0.5 --repete 2 --salva-ir
Opções úteis: --rapido (T=1,5 s, cauda 3 s), --cauda S, --T S, --mono-in/--so-L (entrada só no L: mede cross-feed),
--sem-mix (não forçar mix=100 %). Saída: <out>/ir.json, ir.md (+ ir_<tag>.wav com --salva-ir).
Limitações: RT60 só até a faixa dinâmica obtida (campo faixa_db; T30 exige >= 35 dB, senão cai para T20/EDT, rotulado);
plugin com sidechain/MIDI fora de escopo; entrada mono (L=R) por padrão.
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medidas_comuns as mc


def captura(pl, a):
    if a.metodo == "ess":
        h, info = mc.captura_ess(pl, T=a.T, cauda=a.cauda, mono=not a.so_L)
    else:
        h, info = mc.captura_impulso(pl, cauda=a.cauda, mono=not a.so_L)
    return h, info


def variancia(h1, h2, sr):
    pk = int(np.argmax(np.abs(h1[0])))
    seg = slice(max(0, pk - 48), pk + int(0.2 * sr))
    cc = []
    for c in range(2):
        x, y = h1[c, seg], h2[c, seg]
        cc.append(float(np.sum(x * y) / (np.sqrt(np.sum(x * x) * np.sum(y * y)) + 1e-30)))
    return {"corr_IR_precoce_200ms_L_R": [round(v, 4) for v in cc]}


def md(R):
    M = [f"# Captura de IR: {R['nome']}", "",
         f"SR {R['sr']} Hz, método {R['metodo']}, cauda {R['cauda_s']} s. Ajustes base: {R['ajustes'] or 'padrão'}"
         + (f"; mix auto = {R['mix_param']}" if R.get('mix_param') else ""), ""]
    bandas = list(mc.BANDAS_OITAVA)
    M += ["| ajuste | valor | " + " | ".join(f"RT60 {b}" for b in bandas) + " | pré-atraso ms | NED=1 ms | IACC 0-80 ms | IACC tardio |",
          "|---|---|" + "---|" * (len(bandas) + 4)]
    for c in R["capturas"]:
        rt = c["analise"]["rt60"]
        cel = lambda b: (f"{rt[str(b)]['rt60_s']}{'' if rt[str(b)]['base'] == 't30' else '*'}" if rt.get(str(b)) and rt[str(b)]['rt60_s'] else "-")
        M.append(f"| {c['tag']} | {c.get('valor_texto', '')} | " + " | ".join(cel(b) for b in bandas) +
                 f" | {c['analise']['pre'].get('pre_atraso_ms')} | {c['analise']['ned']['t_ned_1_ms']} | "
                 f"{None if c['analise']['iacc_precoce_0_80ms'] is None else round(c['analise']['iacc_precoce_0_80ms'], 3)} | "
                 f"{None if c['analise']['iacc_tardio_80ms_1s'] is None else round(c['analise']['iacc_tardio_80ms_1s'], 3)} |")
    M += ["", "`*` = RT60 estimado por T20/EDT (faixa dinâmica menor que 35 dB); `-` = não decaiu o bastante.", ""]
    for c in R["capturas"]:
        A = c["analise"]
        M += [f"## {c['tag']} {c.get('valor_texto', '')}",
              f"- direto detectado: {A['pre'].get('direto_detectado')}; onset {A['pre']['onset_ms']} ms; pré-atraso {A['pre'].get('pre_atraso_ms')} ms",
              f"- faixa dinâmica da EDC por banda (dB): " + ", ".join(f"{k}: {v['faixa_db']}" for k, v in A['rt60'].items()),
              f"- NED: {A['ned']}", f"- IACC tardio por oitava: {A['iacc_oitavas_tardio']}",
              f"- espectro da cauda (dB rel.): {A['espectro_cauda_oitavas_db']}",
              f"- energia L-R: {round(A['energia_L_menos_R_db'], 2)} dB; piso de ruído {A['piso_ruido_db_rel_pico']} dB re pico"]
        if c.get("variancia"):
            M.append(f"- variância entre capturas: {c['variancia']}")
        M.append("")
    return "\n".join(M)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="ir_out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--metodo", choices=["ess", "impulso"], default="ess")
    ap.add_argument("--T", type=float, default=3.0, help="duração da varredura em s")
    ap.add_argument("--cauda", type=float, default=6.0, help="cauda gravada após a varredura, s (>= RT60 desejado + margem)")
    ap.add_argument("--rapido", action="store_true", help="T=1,5 s e cauda=3 s")
    ap.add_argument("--repete", type=int, default=1, help="capturas por ajuste (>=2 mede a variância da IR)")
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw")
    ap.add_argument("--settings")
    ap.add_argument("--varre", help="nome do parâmetro a varrer (raw 0..1)")
    ap.add_argument("--valores", default="0.1,0.5,0.9")
    ap.add_argument("--so-L", dest="so_L", action="store_true", help="entrada só no canal L")
    ap.add_argument("--sem-mix", action="store_true")
    ap.add_argument("--salva-ir", action="store_true", help="grava as IR em wav float32")
    a = ap.parse_args()
    if a.rapido:
        a.T, a.cauda = 1.5, min(a.cauda, 3.0)
    t0 = time.time()
    pl = mc.Plugin(a.plugin, a.sr, mc.parse_sets(a.set), a.settings, mix_auto=not a.sem_mix)
    R = {"plugin": a.plugin, "nome": pl.nome, "sr": a.sr, "metodo": a.metodo, "cauda_s": a.cauda, "T": a.T,
         "ajustes": pl.alterados, "mix_param": pl.mix_param, "capturas": []}
    jobs = [("base", None, None)]
    if a.varre:
        nome = pl.achar(a.varre.lower()) if a.varre not in pl.P.keys() else a.varre
        if not nome:
            sys.exit(f"parâmetro '{a.varre}' não encontrado. Disponíveis: {list(pl.P.keys())[:40]}")
        jobs = [(f"{nome}={v}", nome, float(v)) for v in a.valores.split(",")]
    os.makedirs(a.out, exist_ok=True)
    for tag, nome, v in jobs:
        if nome:
            pl.setp(**{nome: v})
        # 2º process() em diante vale: o flush de silêncio dentro de captura_* cobre isso
        hs = []
        for _ in range(max(1, a.repete)):
            h, info = captura(pl, a)
            hs.append(h)
        c = {"tag": tag, "analise": mc.analisa_ir(hs[0], a.sr)}
        if nome:
            c["valor_texto"] = pl.P[nome].string_value
        if len(hs) > 1:
            c["variancia"] = variancia(hs[0], hs[1], a.sr)
            c["rt60_2a_captura"] = mc.rt_resumo(mc.rt_bandas(hs[1], a.sr))
        R["capturas"].append(c)
        if a.salva_ir:
            from scipy.io import wavfile
            wavfile.write(os.path.join(a.out, f"ir_{tag.replace('=', '_')}.wav"), a.sr, (hs[0].T / (np.abs(hs[0]).max() + 1e-30)).astype(np.float32))
    R["tempo_s"] = round(time.time() - t0, 1)
    json.dump(R, open(os.path.join(a.out, "ir.json"), "w"), indent=1, ensure_ascii=False, default=float)
    txt = md(R)
    open(os.path.join(a.out, "ir.md"), "w").write(txt)
    print("\n".join(txt.split("\n")[:3 + 4 + len(R["capturas"])]))


if __name__ == "__main__":
    main()
