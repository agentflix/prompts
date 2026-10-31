#!/usr/bin/env python3
"""Baixa os materiais de aula (links extraídos por gov_extract.py) para uma pasta organizada.

Uso:
  browser-harness < gov_extract.py | grep '^LINKS' | sed 's/^LINKS//' > links.json
  python3 download_pdfs.py links.json <pasta-destino>

Exemplo de destino: ~/Downloads/cmsp/2026/EF-anos-finais/6ano/4bim/historia
Regras aprendidas:
 * Os links diretos (acervocmsp.educacao.sp.gov.br/<pasta>/<arquivo>.pdf) abrem SEM login: basta curl -L.
 * Cada aula costuma ter .pptx + .pdf na mesma pasta numérica. Baixamos o PDF. Se a aula só tem
   PPTX (aconteceu com a Aula 5 de História 7º), baixamos o PPTX para ainda poder ler o conteúdo.
 * O Livro do Estudante e o caderno de resolução também vêm como PDF; ficam na pasta (pdf_meta.py os ignora).
 * Nome do arquivo: <pasta>_<arquivo>.<ext>. Linhas repetidas são baixadas uma vez.
"""
import json, os, re, subprocess, sys
from collections import defaultdict


def main(links_json, dest):
    links = json.load(open(links_json))
    dest = os.path.expanduser(dest)
    os.makedirs(dest, exist_ok=True)
    groups = defaultdict(list)
    for u in links:
        m = re.search(r'/(\d+)/(\d+)\.(\w+)$', u)
        if m:
            groups[m.group(1)].append((u, m.group(2), m.group(3).lower()))
    ok = fail = 0
    pptx_only = []
    for gid, items in groups.items():
        pdfs = [i for i in items if i[2] == 'pdf']
        pick = pdfs if pdfs else [i for i in items if i[2] == 'pptx'][:1]
        if not pdfs and pick:
            pptx_only.append(gid)
        for u, fid, ext in pick:
            out = os.path.join(dest, f'{gid}_{fid}.{ext}')
            if os.path.exists(out) and os.path.getsize(out) > 1000:
                continue
            r = subprocess.run(['curl', '-sfL', '-o', out, u])
            good = r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1000
            if good and ext == 'pdf':
                good = open(out, 'rb').read(5) == b'%PDF-'
            ok += good
            fail += (not good)
            if not good:
                print('FALHOU:', u)
    print(f'{ok} arquivos novos em {dest} ({fail} falhas). Aulas só em PPTX: {pptx_only or "nenhuma"}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
