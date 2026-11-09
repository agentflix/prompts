"""Valida (decodifica) e classifica os PNG/JPG carveados por funcao provavel. Gera README.md."""
import sys as _s
if any(a in ("-h", "--help") for a in _s.argv[1:]):
    print(__doc__); raise SystemExit(0)
import sys, os, glob
from PIL import Image

d=sys.argv[1]; title=sys.argv[2]
rows=[]; bad=[]
for f in sorted(glob.glob(os.path.join(d,"*.png"))+glob.glob(os.path.join(d,"*.jpg"))):
    try:
        im=Image.open(f); im.load(); w,h=im.size; mode=im.mode
    except Exception as e:
        bad.append((os.path.basename(f),str(e)[:50])); continue
    ar=h/w if w else 0
    # heuristica de papel
    if w>=1000 and h>=900 and ar<2: role="fundo/painel"
    elif ar>=6: role=f"filmstrip ({h//w} quadros se {w}x{w})"
    elif 2<=ar<6 and h>=400: role="strip/fader/escala"
    elif w<=40 and h<=140: role="botao/toggle (estados)"
    elif 1.2<ar<3: role="medidor/escala"
    else: role="elemento"
    rows.append((os.path.basename(f),w,h,mode,role))

rows.sort(key=lambda r:-(r[1]*r[2]))
lines=[f"# UI assets extraidos — {title}","",
  f"Carveados do Mach-O (JUCE BinaryData) por assinatura PNG/JPEG. {len(rows)} validos"+(f", {len(bad)} corrompidos" if bad else "")+".",
  "**Uso restrito:** arte da SSL, estudo local, nao redistribuir.","",
  "| arquivo | WxH | modo | papel provavel |","|---|---|---|---|"]
for n,w,h,m,role in rows:
    lines.append(f"| `{n}` | {w}x{h} | {m} | {role} |")
if bad:
    lines+=["","## corrompidos (re-carve necessario)"]+[f"- {n}: {e}" for n,e in bad]
open(os.path.join(d,"README.md"),"w").write("\n".join(lines)+"\n")
print(f"{title}: {len(rows)} validos, {len(bad)} corrompidos -> {d}/README.md")
for n,w,h,m,role in rows[:12]: print(f"  {w}x{h:<5} {role:<28} {n}")
