#!/usr/bin/env python3
"""Mostra a estrutura de um modelo de plano de aula (.docx) para você conferir antes de preencher.

Uso:  python3 inspect_plan.py "Plano de aula novembro historia sextos anos.docx"

Para cada tabela (cada uma é uma turma: 1ª = A, 2ª = B, ...) imprime o cabeçalho
(disciplina, série, total de aulas) e cada linha: data, nº de aulas e o que já está
preenchido nas colunas AULA e CONTEÚDO/AE. Também devolve tudo como JSON com --json.
"""
import json, re, sys, zipfile


def clean(t):
    return re.sub(r'\s+', ' ', t).strip()


def txt(xml):
    return clean(re.sub(r'<[^>]+>', ' ', re.sub(r'</w:p>', '\n', xml)))


def paras(xml):
    return [clean(re.sub(r'<[^>]+>', '', p)) for p in re.findall(r'<w:p[ >].*?</w:p>', xml, flags=re.S)]


def inspect(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    heads = [p for p in paras(x) if 'TOTAL DE AULAS' in p or 'DISCIPLINA' in p]
    tables = []
    for ti, tb in enumerate(re.findall(r'<w:tbl>.*?</w:tbl>', x, flags=re.S)):
        rows = re.findall(r'<w:tr[ >].*?</w:tr>', tb, flags=re.S)
        out = []
        for r in rows[1:]:
            cells = re.findall(r'<w:tc>.*?</w:tc>', r, flags=re.S)
            if len(cells) != 7:
                continue
            date = txt(cells[0])
            m = re.search(r'(\d+)\s*(aulas?)?\s*$', date)
            out.append(dict(date=date, n=int(m.group(1)) if m else None,
                            aula=[p for p in paras(cells[1]) if p], cont=[p for p in paras(cells[2]) if p]))
        tables.append(dict(index=ti, header=heads[ti * 2:ti * 2 + 2], rows=out))
    return tables


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    t = inspect(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps(t, ensure_ascii=False, indent=1))
    else:
        for tb in t:
            print(f'=== Tabela {tb["index"]} (turma {"ABCDEFG"[tb["index"]]})')
            for h in tb['header']:
                print('  ', h)
            for r in tb['rows']:
                print(f'   {r["date"]!r:28} aulas={r["n"]}  AULA preenchida: {"; ".join(r["aula"])[:70] or "(vazia)"}')
