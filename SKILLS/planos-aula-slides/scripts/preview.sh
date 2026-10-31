#!/bin/bash
# Gera uma folha de previa (PNG) de um deck HTML para conferir alinhamento e textos.
# Uso: preview.sh <arquivo.html> <prefixo>   -> cria <prefixo>_sheet0.png, _sheet1.png ...
set -e
HTML="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; P="$2"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP=$(mktemp -d)
"$CH" --headless=new --disable-gpu --no-pdf-header-footer --user-data-dir="$TMP" --print-to-pdf="$P.pdf" "file://$HTML" >/dev/null 2>&1
rm -f "$P"-*.png; pdftoppm -r 50 -png "$P.pdf" "$P" >/dev/null
python3 - "$P" <<'PY'
import sys,glob
from PIL import Image
p=sys.argv[1]; fs=sorted(glob.glob(p+'-*.png')); im=[Image.open(f) for f in fs]; w,h=im[0].size
per=9
for part in range(0,len(im),per):
    sub=im[part:part+per]; rows=(len(sub)+2)//3; sh=Image.new('RGB',(3*w,rows*h),'white')
    for k,x in enumerate(sub): sh.paste(x,((k%3)*w,(k//3)*h))
    sh.save(f'{p}_sheet{part//per}.png')
print(len(im),'slides; folhas:',f'{p}_sheet*.png')
PY
rm -rf "$TMP"
