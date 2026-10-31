#!/usr/bin/env python3
"""Preenche o modelo de plano de aula (.docx) a partir do spec.json (veja assign_plan.py).

Uso:
  python3 fill_plan.py <spec.json> <meta.json> <pasta-dos-pdfs> <saida.docx> [--ano 2026]

Edita o XML do próprio modelo (não recria o arquivo), então fontes, bordas e larguras da
professora são mantidas. Preenche as colunas AULA, CONTEÚDO/AE, METODOLOGIA, RECURSOS e
AVALIAÇÃO de cada linha, mantém ADAPTAÇÃO CURRICULAR como está e corrige o cabeçalho
(disciplina, série + turma A/B, total de aulas, período do mês).
"""
import calendar, json, os, re, sys, zipfile
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_dyn import dyn


def clean(t): return re.sub(r'\s+', ' ', t).strip()


CUT = re.compile(r'\s*(?:●|Relembre|VIREM E CONVERSEM|COM SUAS PALAVRAS|TODO MUNDO|HORA DA|Para começar|Clique|Disponível|Na última aula|[A-ZÇÃÕÉÍÓÚ]{4,}(?: [A-ZÇÃÕÉÍÓÚ]{2,})* \d+ minutos|\d+\.\s)')
BAD = re.compile(r'(,[;.]$|\b(os|as|a|o|de|da|do|dos|das|e|na|no|em|para|com|que)[;.]$|\($|\([^)]*[;.]$)')


def tidy(t):
    t = clean(t)
    m = CUT.search(t)
    if m and m.start() > 10:
        t = t[:m.start()]
    t = t.strip()
    return t if t.endswith(('.', ';')) else t + '.'


def good_bullets(items):
    out = []
    for it in items:
        t = tidy(it)
        if 12 < len(t) < 400 and '?' not in t and not re.search(r'Imagem|Foto|Fonte|Acesso', t) and not BAD.search(t):
            out.append(t)
    return out


def run(t, b=False, i=False, sz=18):
    rp = ('<w:b/>' if b else '') + ('<w:i/>' if i else '') + f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    return f'<w:r><w:rPr>{rp}</w:rPr><w:t xml:space="preserve">{escape(t)}</w:t></w:r>'


def para(segs, after=60):
    return ('<w:p><w:pPr><w:spacing w:after="%d" w:line="240" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>' % after
            + ''.join(run(*s) if isinstance(s, tuple) else run(s) for s in segs) + '</w:p>')


SARESP = dict(aula='Revisão para o Saresp (retomada de conteúdos)',
              cont='Retomada dos conteúdos que serão abordados no Saresp e priorização de habilidades e competências a serem trabalhadas novamente, com base em simulados.',
              met='Aula de revisão: resolução de simulado no formato Saresp, correção coletiva e retomada das habilidades com maior índice de erro.',
              rec='Simulado impresso; lousa; caderno do aluno.', av='Desempenho no simulado e participação na correção coletiva.')
AVAL = dict(aula='Avaliação Bimestral', cont='Avaliação bimestral dos conteúdos trabalhados no 4º bimestre.',
            met='Prova individual, sem consulta, aplicada em sala.', rec='Prova impressa; material de escrita.', av='Nota da avaliação bimestral.')

# Recursos: sempre TV + livro didático. A escola pública NÃO permite celular: Waze/GPS só no computador.
GEO = ['Mapas impressos e Atlas geográfico', 'Google Maps e Google Earth',
       'Waze (versão web, no computador) para localização e rotas', 'Globo terrestre e imagens de satélite', 'Mapas e dados do IBGE']
HIS = ['Vídeos no YouTube (documentários e animações educativas)', 'Vídeos da TV Escola e do Canal Futura',
       'Linha do tempo no quadro ou em cartolina', 'Mapas históricos e imagens de época',
       'Textos e fontes históricas impressos', 'Museus virtuais (Google Arts & Culture)']


def extras(disc, titles):
    out = []
    t = ' '.join(titles).lower()
    if disc.startswith('Geo'):
        if re.search(r'modelagem|maquete', t): out.append('Massa de modelar ou argila (modelagem de relevo)')
        if re.search(r'\bsolo\b', t): out.append('Amostras de solo trazidas pelos alunos')
        if re.search(r'pegada|alternativas para o futuro', t): out.append('Calculadora de pegada ecológica (no computador)')
    return out


def build_row(meta, disc, vol, items, serie=''):
    get = lambda n: next(a for a in meta if a['aula'] == n)
    mains = [n for k, n in items if k == 'A']
    corrs = [n for k, n in items if k == 'C']
    kinds = [k for k, _ in items]
    A, C, M = [], [], []
    first = get(mains[0])['title'] if mains else ''
    for n in mains:
        m = get(n)
        A.append(para([(f'Aula {n} – ', True), m['title']]))
        C.append(para([(f'Aula {n}: ', True), tidy(' '.join(m['ae']))]))
        d = m.get('_dyn') or {'open': None, 'acts': [], 'livro': True}
        tg = []
        if d['open']: tg.append(d['open'][0])
        for a in d['acts']:
            if a[0] not in tg: tg.append(a[0])
        txt = 'Abertura com o “Para começar” do material; exposição dialogada nos slides “Foco no conteúdo”; “Na prática”'
        txt += (' (' + ', '.join(t.capitalize() for t in tg) + ')') if tg else ''
        txt += ' com correção coletiva' + (' e indicação do “Veja no livro”.' if d['livro'] else '.')
        M.append(para([(f'Aula {n}: ', True), txt]))
    for n in corrs:
        m = get(n)
        A.append(para([('Correlação – ', True, True), (f'Aula {n}: {m["title"]}', False, True)]))
        g = good_bullets(m['cont'])[:2]
        C.append(para([('Correlação – ', True, True), (f'Aula {n}: ' + ('; '.join(x.rstrip(';. ') for x in g) + '.' if g else 'relacionar o tema ao assunto da aula principal.'), False, True)]))
    if corrs:
        M.append(para([('Correlação: ', True, True), (f'retomada breve {"da aula" if len(corrs) == 1 else "das aulas"} {", ".join(map(str, corrs))} (roda de conversa ou mapa mental no caderno), ligando esses temas a “{first}”.', False, True)]))
    if 'S' in kinds:
        A.append(para([SARESP['aula']])); C.append(para([SARESP['cont']])); M.append(para([SARESP['met']]))
    if 'V' in kinds:
        A.append(para([(AVAL['aula'], True)])); C.append(para([AVAL['cont']])); M.append(para([AVAL['met']]))
    recs = []
    if mains:
        titles = [get(n)['title'] for n in mains + corrs]
        recs += ['TV', f'Livro didático – Livro do Estudante {vol} ({disc}{" " + serie if serie else ""})',
                 f'Material digital SEDUC-SP (PDF) – {"Aula" if len(mains) == 1 else "Aulas"} {", ".join(map(str, mains))}']
        recs += GEO if disc.startswith('Geo') else HIS if disc.startswith('Hist') else []
        recs += extras(disc, titles) + ['Caderno de Exercícios', 'Lousa e caderno']
    if 'S' in kinds: recs.append(SARESP['rec'].rstrip('.'))
    if 'V' in kinds: recs.append(AVAL['rec'].rstrip('.'))
    R = ''.join(para([r + (';' if i < len(recs) - 1 else '.')]) for i, r in enumerate(recs))
    avs = []
    if mains: avs += ['Participação nas dinâmicas de abertura', 'Registro e correção das atividades do “Na prática”', 'Atividades do Caderno de Exercícios', 'Observação contínua']
    if 'S' in kinds: avs.append(SARESP['av'].rstrip('.'))
    if 'V' in kinds: avs.append(AVAL['av'].rstrip('.'))
    V = ''.join(para([a + (';' if i < len(avs) - 1 else '.')]) for i, a in enumerate(avs))
    return [''.join(A), ''.join(C), ''.join(M), R, V]


def set_cell(cell, inner):
    tcpr = re.match(r'<w:tc>(<w:tcPr>.*?</w:tcPr>)', cell, flags=re.S).group(1)
    return '<w:tc>' + tcpr + inner + '</w:tc>'


def ptext(p): return ''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', p))


def set_para_text(p, new):
    first = [True]
    def f(m):
        if first[0]:
            first[0] = False
            return '<w:t xml:space="preserve">' + escape(new) + '</w:t>'
        return '<w:t></w:t>'
    return re.sub(r'<w:t(?: [^>]*)?>[^<]*</w:t>', f, p)


def row_count(cell0):
    dt = clean(re.sub(r'<[^>]+>', ' ', cell0))
    return int(re.search(r'(\d+)\s*(aulas?)?\s*$', dt).group(1))


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        sys.exit(__doc__)
    spec = json.load(open(a[0])); meta_all = json.load(open(a[1])); pdf_root = os.path.expanduser(a[2]); outp = a[3]
    year = a[a.index('--ano') + 1] if '--ano' in a else '2026'
    meta = meta_all[spec['area']]
    for m in meta:                                   # tags das dinâmicas (Virem e conversem etc.)
        f = os.path.join(pdf_root, spec['area'], m['file'])
        m['_dyn'] = dyn(f) if m['file'].endswith('.pdf') and os.path.exists(f) else None
    disc = spec['disc']
    AVAL['cont'] = f"Avaliação bimestral dos conteúdos trabalhados no {spec.get('bimestre', '4º')} bimestre."
    vol = spec.get('volume', 'Vol. 4')
    x = zipfile.ZipFile(spec['docx']).read('word/document.xml').decode('utf8')
    n_tables = len(re.findall(r'<w:tbl>.*?</w:tbl>', x, flags=re.S))
    assert n_tables == len(spec['tables']), 'o nº de tabelas do modelo difere do spec'
    out = x
    for ti in range(n_tables - 1, -1, -1):          # de trás para frente para não deslocar offsets
        tm = list(re.finditer(r'<w:tbl>.*?</w:tbl>', out, flags=re.S))[ti]
        tb = tm.group(0); rows = list(re.finditer(r'<w:tr[ >].*?</w:tr>', tb, flags=re.S)); newtb = tb
        spec_rows = spec['tables'][ti]['rows']
        assert len(rows) - 1 == len(spec_rows), f'tabela {ti}: modelo tem {len(rows) - 1} linhas, spec {len(spec_rows)}'
        for ri in range(len(rows) - 1, 0, -1):
            r = rows[ri]; cells = list(re.finditer(r'<w:tc>.*?</w:tc>', r.group(0), flags=re.S))
            assert len(cells) == 7, 'linha com colunas mescladas: precisa de ajuste manual'
            items = spec_rows[ri - 1]
            vals = build_row(meta, disc, vol, items, spec.get('serie', ''))
            keep = any(k == 'S' for k, _ in items) and clean(re.sub(r'<[^>]+>', ' ', cells[1].group(0))) != ''
            nc = [c.group(0) for c in cells]
            for k in range(5):
                if keep and k < 2: continue          # respeita o texto da professora na semana do Saresp
                nc[1 + k] = set_cell(nc[1 + k], vals[k])
            rs = r.group(0)
            newrow = rs[:cells[0].start()] + ''.join(nc) + rs[cells[-1].end():]
            newtb = newtb[:r.start()] + newrow + newtb[r.end():]
        out = out[:tm.start()] + newtb + out[tm.end():]
    # cabeçalhos (total de aulas, período, disciplina e turma)
    paras = list(re.finditer(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>', out, flags=re.S))
    totals = [m for m in paras if 'TOTAL DE AULAS' in ptext(m.group(0))]
    discs = [m for m in paras if 'DISCIPLINA' in ptext(m.group(0))]
    assert len(totals) == n_tables and len(discs) == n_tables
    sums = []
    for tm in re.finditer(r'<w:tbl>.*?</w:tbl>', out, flags=re.S):
        rws = list(re.finditer(r'<w:tr[ >].*?</w:tr>', tm.group(0), flags=re.S))
        sums.append(sum(row_count(list(re.finditer(r'<w:tc>.*?</w:tc>', r.group(0), flags=re.S))[0].group(0)) for r in rws[1:]))
    mm = re.search(r'MÊS:\s*(\d{1,2})/(\d{4})', ' '.join(ptext(m.group(0)) for m in paras))
    month = int(mm.group(1)) if mm else 11
    last = calendar.monthrange(int(year), month)[1]
    period = f'(Período de 01/{month:02d}/{year} A {last}/{month:02d}/{year})'
    disc_name = disc
    edits = []
    for ti in range(n_tables):
        t = ptext(totals[ti].group(0))
        t2 = re.sub(r'\(Período de[^)]*\)', period, t)
        t2 = re.sub(r'TOTAL DE AULAS DO PERÍODO:\s*\d+\s*aulas', f'TOTAL DE AULAS DO PERÍODO: {sums[ti]} aulas', t2)
        edits.append((totals[ti], set_para_text(totals[ti].group(0), t2)))
        d = ptext(discs[ti].group(0))
        d2 = re.sub(r'DISCIPLINA:\s*\S+', f'DISCIPLINA: {disc_name}', d)
        d2 = re.sub(r'ANO/SÉRIE:\s*\d\s*º\s*[A-Z]', f'ANO/SÉRIE: {spec["serie"]}{spec["tables"][ti]["turma"]}', d2)
        edits.append((discs[ti], set_para_text(discs[ti].group(0), d2)))
    for m, newp in sorted(edits, key=lambda e: -e[0].start()):
        out = out[:m.start()] + newp + out[m.end():]
    zin = zipfile.ZipFile(spec['docx'])
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    zo = zipfile.ZipFile(outp, 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == 'word/document.xml': data = out.encode()
        zo.writestr(it, data)
    zo.close()
    print('Word gerado:', outp, '| totais por turma:', sums)


if __name__ == '__main__':
    main()
