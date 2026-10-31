#!/usr/bin/env python3
"""Lê os materiais da SEDUC (PDF ou PPTX de aula) e gera um meta.json.

Uso:  python3 pdf_meta.py <pasta-raiz-dos-pdfs> <saida meta.json>

A pasta raiz é organizada assim:  <ano>/<etapa>/<série>/<bimestre>/<componente>/*.pdf
(ex.: 6ano/4bim/historia/152838_1708708.pdf). Cada pasta que contém arquivos vira uma
chave do meta.json (o caminho relativo). Para cada aula guardamos:
  aula, title, cont (conteúdos), ae (objetivos), file, pptx (True se só existia PPTX)

Por que ler layout e dividir colunas: a 1ª página do material tem os conteúdos na coluna
da esquerda e os objetivos (AE) na da direita; o pdftotext -layout mistura as duas, então
cortamos pela posição do 2º marcador "●".
"""
import glob, json, os, re, subprocess, sys, zipfile


def from_pdf(path):
    t = subprocess.run(['pdftotext', '-f', '1', '-l', '3', '-layout', path, '-'],
                       capture_output=True, text=True).stdout
    m = re.search(r'Aula\s+(\d+)', t)
    lines = t.split('\n')
    i0 = next((i for i, l in enumerate(lines) if re.match(r'\s*(História|Geografia|Ciências|Arte|Matemática|Língua [A-Za-zÀ-ú]+)\s*$', l)), None)
    # exige o cabeçalho "Nº bimestre" para ignorar livros do estudante e cadernos de resolução
    if not m or i0 is None or not re.search(r'\d\s*[ºo°]\s*bimestre', t):
        return None
    aula = int(m.group(1))
    title = []
    for l in lines[i0 + 1:]:
        if re.search(r'\d\s*[ºo°]\s*bimestre', l):
            break
        if l.strip():
            title.append(l.strip())
    title = ' '.join(title)
    j0 = next((i for i, l in enumerate(lines) if 'Anos Finais' in l or 'Anos Iniciais' in l or 'Ensino Médio' in l), 0)
    j1 = next((i for i, l in enumerate(lines) if 'Para começar' in l), len(lines))
    blk = [l for l in lines[j0 + 1:j1] if l.strip()]
    col = None
    for l in blk:
        p = [k for k, c in enumerate(l) if c == '●']
        if len(p) >= 2:
            col = p[1]
            break
    if col is None:
        col = min(40, max((len(l) for l in blk), default=80) // 2)
    L = [l[:col].rstrip() for l in blk]
    R = [l[col:].strip() for l in blk]

    def join(ls):
        items, cur = [], ''
        for l in ls:
            s = l.strip()
            if not s:
                continue
            if s.startswith('●'):
                if cur:
                    items.append(cur)
                cur = s[1:].strip()
            else:
                cur = (cur + ' ' + s).strip()
        if cur:
            items.append(cur)
        return items

    return dict(aula=aula, title=title, cont=join(L), ae=join(R), file=os.path.basename(path), pptx=False)


VERBS = ('Analisar', 'Compreender', 'Identificar', 'Reconhecer', 'Explicar', 'Interpretar', 'Relacionar',
         'Criar', 'Refletir', 'Localizar', 'Diferenciar', 'Descrever', 'Comparar', 'Elaborar', 'Explorar', 'Investigar')


def from_pptx(path):
    z = zipfile.ZipFile(path)
    sl = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml', n)],
                key=lambda n: int(re.findall(r'\d+', n)[0]))
    txt = lambda n: [x.strip() for x in re.findall(r'<a:t>([^<]*)</a:t>', z.read(n).decode()) if x.strip()]
    s1 = txt(sl[0])
    joined = ' '.join(s1)
    m = re.search(r'Aula\s*(\d+)', joined)
    if not m:
        return None
    title = s1[-1]
    items = [x for x in txt(sl[1]) if len(x) > 3]
    ae = [x for x in items if x.startswith(VERBS)]
    cont = [x for x in items if x not in ae]
    return dict(aula=int(m.group(1)), title=title, cont=cont, ae=ae, file=os.path.basename(path), pptx=True)


def main(root, out):
    root = os.path.expanduser(root)
    res = {}
    for d in sorted({os.path.dirname(f) for f in glob.glob(os.path.join(root, '**', '*.*'), recursive=True)}):
        rel = os.path.relpath(d, root)
        items, seen = [], {}
        for f in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            m = from_pdf(f)
            if m:
                items.append(m); seen[m['aula']] = True
        for f in sorted(glob.glob(os.path.join(d, '*.pptx'))):
            m = from_pptx(f)
            if m and m['aula'] not in seen:       # PPTX só entra quando a aula não tem PDF
                items.append(m); seen[m['aula']] = True
        if items:
            # aula duplicada (ex.: versão adaptada): mantém o primeiro arquivo
            uniq = {}
            for m in items:
                uniq.setdefault(m['aula'], m)
            res[rel] = [uniq[k] for k in sorted(uniq)]
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
    for k, v in res.items():
        print(f'{k}: aulas {[m["aula"] for m in v]}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
