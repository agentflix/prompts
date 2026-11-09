#!/usr/bin/env python3
"""Matriz de cobertura: dimensão de comportamento -> medido? -> fase(s) que mediram -> erro/limite -> lacuna.

Garantia = processo verificável: a matriz lista TODAS as dimensões que a classe/tipo do plugin exige e mostra, com base nos
arquivos de medição que existem, o que está coberto, por quantas fases independentes (estatico, blackbox, musica, fechamento),
dentro ou fora do limite, e o que é lacuna. Dimensão com 2+ fases independentes = convergente (confiança sobe, ver
references/ledger-confianca.md); 1 fase = única fonte; 0 = LACUNA.

MANIFESTO (JSON):
{ "plugin": "Nome", "base_dir": ".", "classificacao": "classificacao/classificacao.json" (opcional: dimensões de classes com veredito
  'nao' viram n/a),
  "dimensoes": [ {"id": "rt60_por_banda", "nome": "RT60 por oitava", "classe": "e" (a..f, ou "todas"), "limite": "±5 %", "limite_num": 5.0,
      "evidencias": [ {"fase": "blackbox", "arquivo": "ir/ir.json", "chave": "capturas.0.analise.rt60"},
                      {"fase": "estatico", "arquivo": "static/strings.txt", "grep": "decay|rt60"},
                      {"fase": "fechamento", "arquivo": "fechamento/fechamento.json", "chave": "componentes.estatistico.pct",
                       "erro": "componentes.estatistico.erro_max"} ] } ] }
 - arquivo: relativo a base_dir (aceita glob); chave: caminho pontilhado em JSON (índices numéricos para listas); medido = existe e
   não é None/"n/a"/vazio; grep: regex (sem caixa) em arquivo texto; erro: caminho numérico comparado a limite_num (|erro| <= limite_num).
 - fases válidas: estatico | blackbox | musica | fechamento.
Uso:
  matriz_cobertura.py --gera-modelo reverb > manifesto.json      (tipos: reverb delay saturador eq compressor modulacao fita)
  matriz_cobertura.py manifesto.json --out DIR                    -> cobertura.json + cobertura.md
Sai com código 1 se houver LACUNA em dimensão aplicável (use --tolera-lacunas para 0).
"""
import argparse, glob, json, os, re, sys

FASES = ("estatico", "blackbox", "musica", "fechamento")
CLS = "classificacao/classificacao.json"
FICHA = "ficha/ficha.json"
GRADE = "grade/grade.json"
IR = "ir/ir.json"
DLY = "delay/delay.json"
MOD = "modulacao/modulacao.json"
FECH = "fechamento/fechamento.json"
MUS = "musica/musica.json"
STR = "static/strings.txt"


def D(id_, nome, classe, limite, ev, lim_num=None):
    d = {"id": id_, "nome": nome, "classe": classe, "limite": limite, "evidencias": ev}
    if lim_num is not None:
        d["limite_num"] = lim_num
    return d


def bb(arq, chave=None):
    e = {"fase": "blackbox", "arquivo": arq}
    if chave:
        e["chave"] = chave
    return e


def fe(chave, erro=None):
    e = {"fase": "fechamento", "arquivo": FECH, "chave": chave}
    if erro:
        e["erro"] = erro
    return e


def gr(rx):
    return {"fase": "estatico", "arquivo": STR, "grep": rx}


COMUM = [
    D("classificacao", "Classe do sistema (a-f)", "todas", "veredito por classe", [bb(CLS, "classes")]),
    D("parametros", "Parâmetros: faixa, taper, passo", "todas", "tabela completa", [bb("params/parametros.json"), gr("param")]),
    D("neutro", "Ganho unitário/coloração no neutro", "todas", "|ganho| <= 0,1 dB", [bb(FICHA, "neutro"), fe("componentes.regua.pct", "componentes.regua.erro_ganho_max_db")], 0.1),
    D("latencia", "Latência", "todas", "0 amostras de erro", [bb(FICHA, "latencia")]),
    D("estereo", "Estéreo/mono, link", "todas", "L=R no mono", [bb(FICHA, "estereo")]),
    D("ruido_dc", "Ruído de fundo e DC", "todas", "±6 dB", [bb(FICHA, "ruido_dc")]),
    D("dependencia_sr", "Dependência de SR (44,1/48/96)", "todas", "qualitativa", [bb("sr/sr.json")]),
    D("musica", "Música: resíduo nulo por janela de 100 ms", "todas", ">= 95 % das janelas <= -40 dB", [{"fase": "musica", "arquivo": MUS, "chave": "pct_janelas_<=_-40dB"}, fe("componentes.musica.pct")]),
    D("fechamento", "Teste de fechamento (recriação vs plugin)", "todas", ">= 95 % por componente", [fe("resumo.pct_geral")]),
]
TIPOS = {
    "saturador": [
        D("curva_estatica", "Curva estática e núcleo (clip/tanh/poli, assimetria)", "b", "resíduo 1e-3 no tempo", [bb("estatica/curva.json"), gr("tanh|clip|saturat")]),
        D("thd_nivel", "THD/H2..H6 vs nível", "b", "|H| <= 0,005", [bb(FICHA, "thd"), bb(GRADE, "por_ajuste"), fe("componentes.regua.pct", "componentes.regua.erro_h_max")], 0.005),
        D("thd_freq", "THD vs frequência (memória)", "b", "espalhamento H3 < 3 dB", [bb(GRADE, "por_ajuste.neutro.resumo")]),
        D("imd", "IMD SMPTE/CCIF", "b", "±3 dB", [bb(GRADE, "por_ajuste.neutro.imd")]),
        D("aliasing", "Aliasing/oversampling", "b", "±3 dB inarmônico", [bb(FICHA, "aliasing")]),
        D("ordem_blocos", "Ordem input/drive/mix", "b", "qualitativa", [bb("ordem/ordem.json")]),
        D("suavizacao", "Rampas e quantização dos knobs", "b", "ms ±10 %", [bb("rampas/rampas.json")]),
    ],
    "eq": [
        D("resposta", "Resposta em magnitude por banda", "a", "|erro| <= 0,1 dB", [bb(FICHA, "freq"), fe("componentes.resposta.pct", "componentes.resposta.erro_max_db")], 0.1),
        D("fase", "Fase (mínima/linear)", "a", "±5 graus", [bb("fase/fase.json"), gr("linear.?phase|minimum")]),
        D("q_vs_ganho", "Q/largura vs ganho; reciprocidade", "a", "±5 %", [bb("q/q.json")]),
        D("cramping", "Cramping perto de Nyquist (SR)", "a", "±0,2 dB", [bb("sr/sr.json")]),
        D("coloracao", "THD com boost forte", "a", "-60 dBc", [bb(FICHA, "thd")]),
        D("interacao_bandas", "Interação entre bandas", "a", "aditivo ±0,1 dB", [bb("interacao/interacao.json")]),
    ],
    "compressor": [
        D("curva_estatica", "Curva estática: threshold, ratio, joelho", "c", "|GR| <= 0,1 dB", [bb("estatica/curva_comp.json")], 0.1),
        D("tempos", "Ataque/release (63 %), auto-release", "c", "±5 %", [bb("tempos/tempos.json")], 5.0),
        D("detector", "Detector pico/RMS, sidechain HPF, link", "c", "qualitativa", [bb("detector/detector.json"), gr("sidechain|detector")]),
        D("coloracao_gr", "THD com GR = 0 e GR != 0", "c", "±1,5 dB", [bb(GRADE, "por_ajuste")]),
        D("lookahead", "Lookahead/latência/teto (limiter)", "c", "0 amostras", [bb(FICHA, "latencia")]),
        D("makeup_mix", "Makeup automático e paralelo", "c", "±0,1 dB", [bb("makeup/makeup.json")]),
        D("sidechain_externo", "Sidechain externo (fora do pedalboard)", "c", "lacuna declarada", [bb("sidechain/sidechain.json")]),
    ],
    "reverb": [
        D("rt60_bandas", "RT60 por oitava (T30/T20/EDT, Schroeder)", "e", "±5 %", [bb(IR, "capturas.0.analise.rt60"), fe("componentes.estatistico.rt60_pct", "componentes.estatistico.rt60_erro_max_pct")], 5.0),
        D("rt60_vs_decay", "RT60 vs knob de decay/size", "e", "±5 %", [bb(IR, "capturas.1")]),
        D("edc", "Curva de decaimento de energia (EDC)", "e", "RMS <= 1,5 dB", [fe("componentes.estatistico.edc_rms_db", "componentes.estatistico.edc_rms_db")], 1.5),
        D("predelay", "Pré-atraso", "e", "±2 ms", [bb(IR, "capturas.0.analise.pre")]),
        D("densidade", "Densidade de ecos (NED, tempo até 1)", "e", "±20 %", [bb(IR, "capturas.0.analise.ned")]),
        D("early", "Early reflections (atrasos e níveis, 0-80 ms)", "e", "±2 ms; ±3 dB", [bb("early/early.json")]),
        D("damping", "Damping/filtros por banda e espectro da cauda", "e", "±1,5 dB", [bb(IR, "capturas.0.analise.espectro_cauda_oitavas_db")]),
        D("largura", "IACC/largura estéreo", "e", "±0,1", [bb(IR, "capturas.0.analise.iacc_tardio_80ms_1s")]),
        D("modulacao", "Modulação (taxa, profundidade) e variância da IR", "d", "±5 %", [bb(IR, "capturas.0.variancia"), bb(MOD, "medidas")]),
        D("estrutura", "Estrutura FDN/Schroeder/Dattorro (ecos, modos)", "e", "inferência + estático", [bb("estrutura/estrutura.json"), gr("fdn|dattorro|allpass|comb|diffus")]),
        D("estocastico", "Estatística do que não casa amostra a amostra", "f", ">= 95 % das métricas", [fe("componentes.estatistico.pct")]),
    ],
    "delay": [
        D("tempo", "Tempo vs knob; sync (BPM)", "e", "±1 ms", [bb(DLY, "medidas.0.analise.tempo_ms")], 1.0),
        D("feedback", "Feedback por repetição", "e", "±0,5 dB", [bb(DLY, "medidas.0.analise.feedback_db_por_repeticao")], 0.5),
        D("filtro_malha", "Filtro na malha (fc, inclinação)", "e", "±1 dB/oit", [bb(DLY, "medidas.0.analise.filtro_malha_db_por_repeticao")]),
        D("saturacao_malha", "Saturação/compressão na malha", "b", "±1 dB", [bb(DLY, "medidas.0.nivel_baixo")]),
        D("pingpong", "Ping-pong/estéreo/spread", "e", "alternância", [bb(DLY, "medidas.0.analise.alterna_canais")]),
        D("modulacao", "Modulação do tempo (jitter, wow/flutter)", "d", "±20 %", [bb(DLY, "medidas.0.analise.jitter_ms"), bb(MOD, "medidas")]),
        D("ducking", "Ducking/swell", "c", "qualitativa", [bb("ducking/ducking.json")]),
        D("glide", "Glide ao mudar o tempo (crossfade/pitch)", "d", "qualitativa", [bb("glide/glide.json")]),
        D("estocastico", "Estatística do que não casa amostra a amostra", "f", ">= 95 % das métricas", [fe("componentes.estatistico.pct")]),
    ],
    "modulacao": [
        D("lfo_taxa", "Taxa do LFO vs knob (razão)", "d", "±5 %", [bb(MOD, "medidas.0.canais.0.taxa_hz")], 5.0),
        D("lfo_prof", "Profundidade AM (dB) e FM (cents)", "d", "±20 %", [bb(MOD, "medidas.0.canais.0.am_pico_a_pico_db")]),
        D("lfo_forma", "Forma do LFO", "d", "categoria", [bb(MOD, "medidas.0.canais.0.forma")]),
        D("fase_estereo", "Fase L-R do LFO", "d", "±10 graus", [bb(MOD, "medidas.0.fase_L_R_graus")]),
        D("feedback", "Feedback/ressonância", "e", "±1 dB", [bb("feedback/feedback.json")]),
        D("mix_manual", "Mix, manual/delay base", "d", "±0,1 dB", [bb("mix/mix.json")]),
    ],
    "fita": [
        D("thd_nivel_freq", "THD vs nível e frequência (histerese)", "c", "±1,5 dB", [bb(GRADE, "por_ajuste")]),
        D("imd", "IMD de dois tons", "c", "±3 dB", [bb(GRADE, "por_ajuste.neutro.imd")]),
        D("compressao", "Compressão por degrau (assentamento)", "c", "±10 %", [bb("compressao/compressao.json"), bb(CLS, "classes.c_nao_linear_com_memoria")]),
        D("head_bump", "Head bump e curvas por velocidade", "a", "±0,5 dB", [bb(FICHA, "freq")]),
        D("wow_flutter", "Wow/flutter por demodulação de FM de tom alto", "d", "±20 %", [bb(MOD, "medidas")]),
        D("ruido", "Espectro do ruído (hiss, hum) e bias/tipo de fita", "f", "±3 dB por banda", [bb(FICHA, "ruido_dc"), bb("ruido/espectro.json")]),
    ],
}


def resolve(obj, chave):
    for p in chave.split("."):
        if isinstance(obj, list):
            try:
                obj = obj[int(p)]
            except (ValueError, IndexError):
                return None
        elif isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return None
    return obj


def vazio(v):
    return v is None or v == "n/a" or v == [] or v == {} or (isinstance(v, dict) and set(v) == {"n/a"}) or (isinstance(v, dict) and "n/a" in v and len(v) == 1)


def avalia(ev, base, cache):
    arqs = sorted(glob.glob(os.path.join(base, ev["arquivo"]))) if any(c in ev["arquivo"] for c in "*?[") else [os.path.join(base, ev["arquivo"])]
    arqs = [a for a in arqs if os.path.exists(a)]
    r = {"fase": ev["fase"], "arquivo": ev["arquivo"], "medido": False, "erro": None}
    if not arqs:
        r["motivo"] = "arquivo ausente"
        return r
    arq = arqs[0]
    if "grep" in ev:
        txt = open(arq, errors="replace").read()
        r["medido"] = bool(re.search(ev["grep"], txt, re.I))
        r["motivo"] = "" if r["medido"] else "padrão não encontrado"
        return r
    if arq not in cache:
        try:
            cache[arq] = json.load(open(arq))
        except Exception:
            cache[arq] = None
    j = cache[arq]
    if "chave" not in ev:
        r["medido"] = True
        return r
    v = resolve(j, ev["chave"]) if j is not None else None
    r["medido"] = not vazio(v)
    if not r["medido"]:
        r["motivo"] = "chave ausente ou n/a"
    if r["medido"] and ev.get("erro"):
        e = resolve(j, ev["erro"])
        if isinstance(e, (int, float)):
            r["erro"] = float(e)
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifesto", nargs="?")
    ap.add_argument("--gera-modelo", choices=sorted(TIPOS), help="imprime um manifesto para o tipo e sai")
    ap.add_argument("--out", default="cobertura_out")
    ap.add_argument("--tolera-lacunas", action="store_true")
    a = ap.parse_args()
    if a.gera_modelo:
        dims = COMUM + TIPOS[a.gera_modelo]
        print(json.dumps({"plugin": "NOME", "tipo": a.gera_modelo, "base_dir": ".", "classificacao": CLS, "dimensoes": dims}, indent=1, ensure_ascii=False))
        return
    if not a.manifesto:
        ap.error("informe o manifesto ou --gera-modelo")
    M = json.load(open(a.manifesto))
    base = os.path.join(os.path.dirname(os.path.abspath(a.manifesto)), M.get("base_dir", "."))
    cls = {}
    if M.get("classificacao") and os.path.exists(os.path.join(base, M["classificacao"])):
        cj = json.load(open(os.path.join(base, M["classificacao"])))
        cls = {k.split("_")[0]: v["veredito"] for k, v in cj.get("classes", {}).items()}
    cache, linhas = {}, []
    for d in M["dimensoes"]:
        c = d.get("classe", "todas")
        aplic = not (c != "todas" and cls.get(c) == "nao")
        evs = [avalia(e, base, cache) for e in d["evidencias"]] if aplic else []
        fases = sorted({e["fase"] for e in evs if e["medido"]}, key=FASES.index)
        err = next((e["erro"] for e in evs if e["erro"] is not None), None)
        lim = d.get("limite_num")
        if not aplic:
            st = "n/a (classe '%s' = nao)" % c
        elif not fases:
            st = "LACUNA"
        elif err is not None and lim is not None and abs(err) > lim:
            st = "FORA DO LIMITE"
        elif len(fases) >= 2:
            st = "CONVERGENTE"
        else:
            st = "UMA FASE"
        linhas.append({"id": d["id"], "nome": d["nome"], "classe": c, "aplica": aplic, "limite": d.get("limite"), "fases": fases,
                       "erro": err, "limite_num": lim, "status": st, "evidencias": evs,
                       "lacuna": ("sem medição em: " + ", ".join(sorted({e["arquivo"] for e in evs}))) if aplic and not fases else ""})
    ap_ = [l for l in linhas if l["aplica"]]
    n = max(1, len(ap_))
    res = {"plugin": M.get("plugin"), "classes_veredito": cls,
           "aplicaveis": len(ap_), "medidas": sum(1 for l in ap_ if l["fases"]),
           "convergentes": sum(1 for l in ap_ if l["status"] == "CONVERGENTE"),
           "fora_do_limite": sum(1 for l in ap_ if l["status"] == "FORA DO LIMITE"),
           "lacunas": [l["id"] for l in ap_ if l["status"] == "LACUNA"]}
    res["pct_cobertura"] = round(100 * res["medidas"] / n, 1)
    res["pct_convergente"] = round(100 * res["convergentes"] / n, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump({"resumo": res, "dimensoes": linhas}, open(os.path.join(a.out, "cobertura.json"), "w"), indent=1, ensure_ascii=False)
    L = [f"# Matriz de cobertura: {res['plugin']}", "",
         f"Cobertura {res['pct_cobertura']} % ({res['medidas']}/{res['aplicaveis']}); convergente (2+ fases) {res['pct_convergente']} %; fora do limite {res['fora_do_limite']}; lacunas {len(res['lacunas'])}.",
         "", "| dimensão | classe | medido? | fase(s) | erro / limite | status | lacuna |", "|---|---|---|---|---|---|---|"]
    for l in linhas:
        el = "-" if l["erro"] is None else f"{l['erro']:.4g} / {l['limite_num'] if l['limite_num'] is not None else l['limite']}"
        if l["erro"] is None and l["limite"]:
            el = f"- / {l['limite']}"
        L.append(f"| {l['nome']} | {l['classe']} | {'sim' if l['fases'] else ('n/a' if not l['aplica'] else 'NAO')} | {', '.join(l['fases']) or '-'} | {el} | **{l['status']}** | {l['lacuna']} |")
    L += ["", "Convergente = duas fases independentes mediram (promove confiança); 'UMA FASE' = fonte única; LACUNA entra no §8 do dossiê."]
    open(os.path.join(a.out, "cobertura.md"), "w").write("\n".join(L))
    print("\n".join(L[:8]))
    sys.exit(1 if (res["lacunas"] and not a.tolera_lacunas) else 0)


if __name__ == "__main__":
    main()
