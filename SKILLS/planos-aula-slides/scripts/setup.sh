#!/bin/bash
# Prepara tudo (so precisa rodar uma vez). Uso: bash setup.sh
set -e
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Instale o Node.js (brew install node)"; exit 1; }
[ -d node_modules/pptxgenjs ] && [ -d node_modules/sharp ] || npm install --silent pptxgenjs@3.12.0 sharp
python3 - <<'PY'
import importlib
for m in ('PIL',):
    try: importlib.import_module(m)
    except Exception: print('Falta Pillow: pip3 install pillow  (so e usado para a folha de previa)')
PY
command -v pdftotext >/dev/null || echo "Falta poppler: brew install poppler (leitura dos PDFs)"
command -v tesseract >/dev/null || echo "Opcional: brew install tesseract tesseract-lang (OCR do Lattes em PDF imagem)"
echo "Setup ok"
