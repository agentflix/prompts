#!/usr/bin/env python3
"""Decide QUAIS aulas dos PDFs entram em cada semana do plano (e quais viram "correlação").

Uso:
  python3 assign_plan.py <modelo.docx> <meta.json> <area> <saida spec.json> \
      [--disc Historia] [--serie 6º] [--saresp-week 3] [--no-avaliacao]

  <area> = chave do meta.json, ex.: 6ano/4bim/historia

Regras (combinadas com a professora):
 * Cada tabela do .docx é uma turma (1ª = A, 2ª = B ...). A e B podem ter nº de aulas diferente.
 * O "Nº DE AULAS" da semana manda: escolhe-se a MESMA quantidade de aulas dos PDFs.
 * Linhas que já vêm preenchidas no modelo (a professora já escolheu os temas) são respeitadas:
   os N primeiros temas da linha viram aulas principais; os temas que sobram viram "correlação".
 * Linhas vazias: usa as ÚLTIMAS aulas do bimestre, em ordem (o que veio antes vira correlação).
 * Semana do Saresp (padrão: a 3ª semana, ou qualquer linha cujo texto cite Saresp): sem PDF.
 * Avaliação Bimestral: ocupa a última aula da última semana (--no-avaliacao desliga).
 * Aulas dos PDFs que sobram são correlacionadas à semana mais próxima (a professora quer
   "passar pelos outros temas" sem perder o foco nas aulas principais).

A saída (spec.json) é só um rascunho: mostre-o à professora e ajuste antes de gerar o Word.
Formato de cada linha: [["A", 4], ["A", 5], ["C", 1], ["S", 0], ["V", 0]]
  A = aula principal, C = correlação, S = revisão Saresp, V = avaliação bimestral.
"""
import json, re, sys, unicodedata, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inspect_plan import inspect


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9 ]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn')).strip()


def match_titles(existing, aulas):
    """mapeia os temas já escritos no modelo para números de aula do meta."""
    by = [(a['aula'], norm(a['title'])) for a in aulas]
    got = []
    for t in existing:
        nt = norm(t)
        if not nt:
            continue
        hit = next((n for n, tt in by if tt == nt or tt.startswith(nt) or nt.startswith(tt)), None)
        if hit is None:
            hit = next((n for n, tt in by if nt in tt or tt in nt), None)
        got.append(hit)
    return got


def assign(table, aulas, saresp_idx, avaliacao):
    rows = table['rows']
    nums = [a['aula'] for a in aulas]
    kinds = []
    for i, r in enumerate(rows):
        text = ' '.join(r['aula']).lower()
        pref = any(norm(t) for t in r['aula'])
        if 'saresp' in text or (i == saresp_idx and not pref):
            kinds.append('S')
        elif pref:
            kinds.append('P')
        else:
            kinds.append('E')
    out = [[] for _ in rows]
    last_non_s = max((i for i, k in enumerate(kinds) if k != 'S'), default=None)
    # avaliação bimestral: já escrita no modelo ou na última semana
    av_row = None
    for i, r in enumerate(rows):
        if any('avalia' in t.lower() for t in r['aula']):
            av_row = i
    if av_row is None and avaliacao:
        av_row = last_non_s
    mentioned = []
    # linhas pré-preenchidas
    for i, r in enumerate(rows):
        if kinds[i] == 'S':
            out[i] = [['S', 0]]
        elif kinds[i] == 'P':
            titles = [t for t in r['aula'] if 'avalia' not in t.lower() and 'saresp' not in t.lower()]
            got = [g for g in match_titles(titles, aulas) if g is not None]
            slots = r['n'] - (1 if av_row == i else 0)
            out[i] = [['A', g] for g in got[:slots]] + [['C', g] for g in got[slots:]]
            mentioned += got
    # linhas vazias: últimas aulas
    empties = [i for i, k in enumerate(kinds) if k == 'E']
    pool = [n for n in nums if n not in mentioned]
    if empties:
        slots = {i: rows[i]['n'] - (1 if av_row == i else 0) for i in empties}
        total = sum(slots.values())
        take = pool[-total:] if total else []
        cur = 0
        for i in empties:
            out[i] = [['A', n] for n in take[cur:cur + slots[i]]]
            cur += slots[i]
        mentioned += take
    # sobras -> correlação
    left = [n for n in nums if n not in mentioned]
    if left:
        firsts = [(min(n for k, n in o if k == 'A'), i) for i, o in enumerate(out) if any(k == 'A' for k, _ in o)]
        if firsts:
            first_row = min(firsts)[1]
            last_row = max(firsts)[1]
            # aulas que ficaram "entre" temas pré-escritos vão para a semana vizinha mais próxima
            for n in left:
                best = min(firsts, key=lambda f: abs(f[0] - n))
                out[best[1]].append(['C', n])
            # empty-case: muitas sobras iniciais -> as mais antigas vão para a última semana (retomada)
            if empties and len(left) > 4:
                ear = sorted(left)[:len(left) - 4]
                for n in ear:
                    for o in out:
                        if ['C', n] in o:
                            o.remove(['C', n])
                    out[last_row].append(['C', n])
    for i, o in enumerate(out):                      # A (na ordem), depois C em ordem crescente, depois S
        out[i] = [x for x in o if x[0] == 'A'] + sorted([x for x in o if x[0] == 'C'], key=lambda x: x[1]) + [x for x in o if x[0] == 'S']
    if av_row is not None and ['V', 0] not in out[av_row]:
        out[av_row].append(['V', 0])
    # confere total de aulas por linha
    warns = []
    for i, r in enumerate(rows):
        got = sum(1 for k, _ in out[i] if k in 'AV') + (r['n'] if any(k == 'S' for k, _ in out[i]) else 0)
        if got != r['n']:
            warns.append(f'linha {i + 1} ({r["date"]}): modelo pede {r["n"]} aulas, spec tem {got}')
    return out, warns


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        sys.exit(__doc__)
    docx, meta, area, outp = a[:4]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    aulas = json.load(open(meta))[area]
    saresp = int(opt('--saresp-week', 3)) - 1
    avaliacao = '--no-avaliacao' not in a
    nums_all = [x['aula'] for x in aulas]
    gaps = [n for n in range(min(nums_all), max(nums_all) + 1) if n not in nums_all]
    if gaps:
        print(f'AVISO: aulas {gaps} não aparecem nos arquivos desta pasta. Se o site tiver só o PPTX dessa aula, baixe-o '
              f'(download_pdfs.py faz isso) e rode pdf_meta.py de novo; senão confirme que ela não existe.')
    tables = inspect(docx)
    spec = dict(docx=docx, area=area, disc=opt('--disc', area.split('/')[-1].capitalize()), serie=opt('--serie', ''), tables=[])
    for t in tables:
        rows, warns = assign(t, aulas, saresp, avaliacao)
        spec['tables'].append(dict(turma='ABCDEFG'[t['index']], rows=rows, dates=[r['date'] for r in t['rows']], warnings=warns))
        print(f'--- turma {"ABCDEFG"[t["index"]]}')
        for r, d in zip(rows, t['rows']):
            print(f'  {d["date"]:<24}', ' '.join(f'{k}{n if n else ""}' for k, n in r))
        for w in warns:
            print('  AVISO:', w)
    json.dump(spec, open(outp, 'w'), ensure_ascii=False, indent=1)
    print('Rascunho salvo em', outp)


if __name__ == '__main__':
    main()
