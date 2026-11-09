#!/usr/bin/env python3
"""Despeja todos os parâmetros de um plugin via pedalboard (somente leitura/edição de parâmetros).

Para cada parâmetro: nome, tipo (float/bool/enum), faixa, passo, unidades, valor padrão (raw e string),
varredura fina raw 0..1 -> string_value -> número (taper raw->valor) e detecção de quantização.
ATENÇÃO: `quantizado_string` só diz que a STRING do parâmetro tem degraus (knob em passos ou texto
arredondado). Para saber se o DSP quantiza de verdade, medir áudio (references/blackbox-pedalboard.md §5).
Grava <out>/parametros.json, parametros.csv e tapers.csv (raw, valor por parâmetro).
Nota: raw_value é NORMALIZADO 0..1; o taper raw->valor sai da varredura.
"""
import argparse, csv, json, math, os, re, sys
import numpy as np

RX_NUM = re.compile(r"[-+]?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?")


def num(s):
    # primeiro número da string ("-12.5 dB" -> -12.5); aceita vírgula decimal
    m = RX_NUM.search(s or "")
    return float(m.group(0).replace(",", ".")) if m else None


def classifica_taper(x, y):
    # degraus / linear / log / exp, pelo ajuste de y(x) (x=raw)
    x, y = np.asarray(x), np.asarray(y)
    if len(set(np.round(y, 9))) <= 1:
        return "constante", 1.0
    # poucos valores distintos na varredura = knob em posições fixas (ex.: attack 0,1/0,3/1/3/10/30 ms)
    u = np.unique(np.round(y, 9))
    if 3 <= len(u) <= 24 and len(u) <= len(x) // 4:
        d = np.diff(u)
        if d.max() / (d.min() + 1e-30) < 1.05:
            return f"degraus regulares ({len(u)} valores, passo {d.mean():g})", 1.0
        return f"degraus/enum-like ({len(u)} valores: {', '.join(f'{v:g}' for v in u[:12])}{'...' if len(u) > 12 else ''})", 1.0
    r2 = lambda a, b: 1 - ((b - np.polyval(np.polyfit(a, b, 1), a)) ** 2).sum() / (((b - b.mean()) ** 2).sum() + 1e-30)
    lin = r2(x, y)
    if lin > 0.9995:
        return "linear", lin
    if (y > 0).all():
        lg = r2(x, np.log(y))
        if lg > 0.9995:
            return "exponencial (log(valor) linear em raw)", lg
        # potência: y = a + b x^k aproximada via log-log com deslocamento mínimo
        return "curvo (não linear/exp; ver tapers.csv)", max(lin, lg)
    return "curvo (não linear; ver tapers.csv)", lin


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin", help="caminho do .vst3/.component")
    ap.add_argument("--out", default="parametros_out", help="pasta de saída (padrão: parametros_out)")
    ap.add_argument("--pontos", type=int, default=201, help="pontos da varredura fina raw 0..1 (padrão 201)")
    ap.add_argument("--filtro", default="", help="só parâmetros cujo nome contém este texto")
    ap.add_argument("--max", type=int, default=0, help="limita nº de parâmetros (teste rápido); 0 = todos")
    a = ap.parse_args()
    from pedalboard import load_plugin
    fx = load_plugin(a.plugin)
    os.makedirs(a.out, exist_ok=True)
    P = fx.parameters
    nomes = [n for n in P.keys() if a.filtro in n]
    if a.max:
        nomes = nomes[: a.max]
    info = {"plugin": a.plugin, "nome": fx.name, "is_instrument": getattr(fx, "is_instrument", None),
            "is_effect": getattr(fx, "is_effect", None), "n_parametros": len(P), "parametros": []}
    xs = np.linspace(0, 1, a.pontos)
    taper_rows = {}
    for n in nomes:
        p = P[n]
        d = {"nome": n, "rotulo": getattr(p, "label", ""), "unidades": getattr(p, "units", ""),
             "tipo_py": getattr(p.type, "__name__", str(p.type))}
        raw0 = float(p.raw_value)
        d["default_raw"] = raw0
        d["default_string"] = str(p.string_value)
        d["faixa"] = list(p.range) if getattr(p, "range", None) else None
        vv = getattr(p, "valid_values", None) or []
        d["n_valores_validos"] = len(vv)
        # varredura fina
        strs, vals = [], []
        for x in xs:
            try:
                p.raw_value = float(x)
                s = str(p.string_value)
            except Exception as e:
                s = f"<erro {e}>"
            strs.append(s); vals.append(num(s))
        try:
            p.raw_value = raw0  # restaura o padrão
        except Exception:
            pass
        uniq = list(dict.fromkeys(strs))
        d["strings_distintas"] = len(uniq)
        numericos = all(v is not None for v in vals)
        if d["tipo_py"] == "bool" or len(uniq) == 2:
            d["classe"] = "bool"; d["valores"] = uniq
        elif not numericos or (len(uniq) <= 24 and not any(ch.isdigit() for u in uniq[:2] for ch in u)):
            d["classe"] = "enum"; d["valores"] = uniq[:64]
        else:
            d["classe"] = "float"
            v = np.array(vals, float)
            d["valor_min"], d["valor_max"] = float(v.min()), float(v.max())
            d["valor_no_raw_0_5"] = float(v[len(v) // 2])
            tp, r2 = classifica_taper(xs, v)
            d["taper"] = tp; d["taper_r2"] = round(float(r2), 6)
            # quantização: varredura FINA em torno de raw=0,5 (a grossa só vê o passo da amostragem)
            fino, vf = np.linspace(0.497, 0.503, 61), []
            for x in fino:
                p.raw_value = float(x); vf.append(num(str(p.string_value)))
            try:
                p.raw_value = raw0
            except Exception:
                pass
            vf = np.array([q for q in vf if q is not None], float)
            dv = np.unique(np.round(vf, 6))
            d["valores_distintos_fino"] = int(len(dv))
            # plateaus (poucos valores distintos em 61 pontos) = knob em degraus OU string arredondada
            d["quantizado_string"] = bool(len(dv) < 40)
            d["passo_fino"] = float(np.min(np.diff(dv))) if len(dv) >= 2 else None
            d["valores_distintos"] = int(len(np.unique(np.round(v, 6))))
            if d["faixa"] and len(d["faixa"]) == 3 and d["faixa"][2]:
                d["passo_declarado"] = d["faixa"][2]
        info["parametros"].append(d)
        taper_rows[n] = vals
        print(f"{n:34s} {d['classe']:6s} {d.get('taper','')[:22]:22s} def={d['default_string']!r}", file=sys.stderr)
    json.dump(info, open(os.path.join(a.out, "parametros.json"), "w"), indent=1, ensure_ascii=False)
    cols = ["nome", "classe", "unidades", "rotulo", "default_raw", "default_string", "valor_min", "valor_max",
            "taper", "taper_r2", "valores_distintos", "passo_fino", "quantizado_string", "passo_declarado", "valores"]
    with open(os.path.join(a.out, "parametros.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for d in info["parametros"]:
            w.writerow([json.dumps(d.get(c), ensure_ascii=False) if isinstance(d.get(c), (list, dict)) else d.get(c, "") for c in cols])
    with open(os.path.join(a.out, "tapers.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["raw"] + list(taper_rows))
        for i, x in enumerate(xs):
            w.writerow([f"{x:.5f}"] + [taper_rows[n][i] if taper_rows[n][i] is not None else "" for n in taper_rows])
    print(f"{len(info['parametros'])} parâmetros -> {a.out}/parametros.json|csv, tapers.csv")


if __name__ == "__main__":
    main()
