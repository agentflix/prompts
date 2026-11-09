#!/usr/bin/env python3
"""Extrai o LFO de um efeito de modulação (chorus, flanger, phaser, tremolo, vibrato, reverb/delay modulado)
por demodulação AM e FM de um tom estável (pedalboard, regime estável, reset=False, aquecimento).

Entrada: tom senoidal (padrão 1 kHz, -20 dBFS) em L=R. Saída: para cada canal, a portadora é isolada (passa-faixa
0,7-1,3 f; harmônicas não entram), o sinal analítico (Hilbert) dá envelope (AM) e fase (FM); tira-se a deriva
(< 0,2 Hz) e o que passa de 60 Hz; o pico do espectro de cada demodulado dá:
  taxa do LFO (Hz, com interpolação parabólica), proeminência do pico sobre a mediana (dB; < 12 dB = sem LFO periódico),
  profundidade AM (dB pico a pico do envelope) e FM (cents de pico), banda lateral (dBc),
  forma (razão dos harmônicos 2 e 3 do LFO sobre o fundamental: senoidal / triangular / quadrada / dente de serra /
  aleatória), e fase/atraso entre canais L e R no pico (AM e FM): LFO em quadratura (90 graus) = estéreo largo.
Varredura: --varre PARAM --valores v1,v2 (raw 0..1) -> taxa e profundidade vs knob (taper da taxa; profundidade em cents/dB).
Tom único não vê todos os efeitos: flanger/phaser com notch num ponto só mostra AM mais forte perto do notch; repita
com --freq 250,1000,4000 (aceita lista) para ver a profundidade em função da frequência.
Uso (PYTHONPATH=<skill>/scripts):
  analisa_modulacao.py "/Library/Audio/Plug-Ins/VST3/ValhallaSpaceModulator.vst3" --out DIR [--rapido]
  analisa_modulacao.py PLUGIN --out DIR --varre rate --valores 0.1,0.5,0.9 --freq 1000,4000
Saída: <out>/modulacao.json e modulacao.md. Duração: --dur (padrão 8 s; resolução do LFO ~ 1/dur Hz; LFO < 0,3 Hz exige --dur maior).
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medidas_comuns as mc


def mede(pl, f, nivel, aquece, dur):
    sr = pl.sr
    y = pl.proc(mc.tom(sr, f, nivel, aquece + dur))[:, int(aquece * sr):]       # fluxo contínuo: aquece e mede no mesmo sinal
    return mc.demod_tom(y, sr, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="mod_out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--freq", default="1000", help="tom(ns) em Hz, separados por vírgula")
    ap.add_argument("--nivel", type=float, default=-20.0)
    ap.add_argument("--dur", type=float, default=8.0)
    ap.add_argument("--aquece", type=float, default=3.0)
    ap.add_argument("--rapido", action="store_true", help="dur=4 s, aquecimento 1,5 s")
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw")
    ap.add_argument("--settings")
    ap.add_argument("--varre")
    ap.add_argument("--valores", default="0.1,0.5,0.9")
    ap.add_argument("--sem-mix", action="store_true")
    a = ap.parse_args()
    if a.rapido:
        a.dur, a.aquece = min(a.dur, 4.0), 1.5
    t0 = time.time()
    pl = mc.Plugin(a.plugin, a.sr, mc.parse_sets(a.set), a.settings, mix_auto=not a.sem_mix)
    R = {"plugin": a.plugin, "nome": pl.nome, "sr": a.sr, "nivel_dbfs": a.nivel, "dur_s": a.dur, "ajustes": pl.alterados, "medidas": []}
    freqs = [float(v) for v in a.freq.split(",")]
    jobs = [("base", None, None)]
    if a.varre:
        nome = a.varre if a.varre in pl.P.keys() else pl.achar(a.varre.lower())
        if not nome:
            sys.exit(f"parâmetro '{a.varre}' não encontrado. Disponíveis: {list(pl.P.keys())[:40]}")
        jobs = [(f"{nome}={v}", nome, float(v)) for v in a.valores.split(",")]
    for tag, nome, v in jobs:
        if nome:
            pl.setp(**{nome: v})
        for f in freqs:
            d = mede(pl, f, a.nivel, a.aquece, a.dur)
            m = {"tag": tag, "freq_hz": f, **d}
            if nome:
                m["valor_texto"] = pl.P[nome].string_value
                nums = [t for t in m["valor_texto"].replace(",", ".").split() if t.replace(".", "", 1).lstrip("-").isdigit()]
                if nums and "hz" in m["valor_texto"].lower() and float(nums[0]) > 0:
                    m["razao_taxa_medida_sobre_knob"] = round(m["canais"][0]["taxa_hz"] / float(nums[0]), 3)
            R["medidas"].append(m)
    R["tempo_s"] = round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(R, open(os.path.join(a.out, "modulacao.json"), "w"), indent=1, ensure_ascii=False, default=float)
    L = [f"# Análise de modulação: {R['nome']}", "", f"SR {a.sr}; tom {a.nivel} dBFS; janela {a.dur} s (resolução ~{1 / a.dur:.3f} Hz). Ajustes: {R['ajustes']}", "",
         "| ajuste | valor | tom Hz | taxa Hz | proem. dB | fonte | AM dB pp | FM cents | banda lat. dBc | forma | fase L-R (graus) | atraso L-R ms | taxa/knob |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in R["medidas"]:
        c = m["canais"][0]
        L.append(f"| {m['tag']} | {m.get('valor_texto', '')} | {m['freq_hz']:g} | {c['taxa_hz']} | {c['proeminencia_db']} | {c['fonte_dominante']} | {c['am_pico_a_pico_db']} | "
                 f"{c['fm_pico_cents']} | {c['banda_lateral_dbc']} | {c['forma']} | {m.get('fase_L_R_graus', '-')} | {m.get('atraso_L_R_ms', '-')} | {m.get('razao_taxa_medida_sobre_knob', '-')} |")
    L += [""] + [f"AVISO {m['tag']} {m['freq_hz']:g} Hz: taxa {m['canais'][0]['taxa_hz']} Hz perto/abaixo da resolução (~{1 / a.dur:.2f} Hz): aumente --dur"
                 for m in R["medidas"] if m["canais"][0]["taxa_hz"] < 3.0 / a.dur]
    L += ["", "taxa/knob constante (ex.: 4,00) = o LFO medido é múltiplo fixo do knob (vozes em quadratura, flanger com várias fases): usar a razão no modelo.",
          "Flanger/phaser: o tom pode cruzar notches (AM profundo, fase salta): ver `picos_espectro_modulacao` no JSON; repita com --freq em outras frequências.",
          "Proeminência < 12 dB = sem LFO periódico claro (modulação aleatória ou ausente). Fase L-R vale na fonte dominante; AM e FM separados no JSON."]
    open(os.path.join(a.out, "modulacao.md"), "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
