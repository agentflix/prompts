#!/usr/bin/env python3
"""Junta TODOS os planos de aula (Word) em UM arquivo unificado, com capa e índice.

Uso:
  python3 consolidate_docs.py <saida.docx> <plano1.docx> [plano2.docx ...] \
      [--titulo "Planos de aula – Novembro/2026"] [--prof "Prof.ª Nome Sobrenome"] [--disciplinas "História,Geografia"]

O que faz:
  * capa (título, professora) + índice (disciplina, série+turma e total de aulas de cada turma);
  * cada TURMA vira um bloco em página nova (paisagem, igual ao modelo). Ordem combinada com a professora:
    por DISCIPLINA e, dentro dela, em ordem crescente 6ºA, 6ºB, 7ºA, 7ºB (padrão: História e depois Geografia;
    mude com --disciplinas "Geografia,História");
  * as imagens do cabeçalho de cada plano (logos/faixas) são copiadas e renumeradas, para não colidirem;
  * ids repetidos (paraId, docPr) são removidos/renumerados, para o Word não pedir "reparar o arquivo".
Todos os planos devem vir do mesmo modelo (mesmos estilos), o que é o caso dos modelos da professora.
"""
import os, re, sys, zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inspect_plan import inspect

REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'


def body_of(xml):
    m = re.search(r'<w:body>(.*)</w:body>', xml, flags=re.S)
    inner = m.group(1)
    sect = re.search(r'<w:sectPr[ >].*?</w:sectPr>\s*$', inner, flags=re.S)
    return (inner[:sect.start()] if sect else inner), (sect.group(0) if sect else '')


def rels_of(z):
    x = z.read('word/_rels/document.xml.rels').decode()
    return {m.group(1): (m.group(2), m.group(3), m.group(4)) for m in
            re.finditer(r'<Relationship Id="([^"]+)" Type="([^"]+)" Target="([^"]+)"(?: TargetMode="([^"]+)")?\s*/>', x)}


def split_blocks(body):
    """Divide o corpo em blocos, um por tabela (= uma turma): cabeçalho da turma + tabela."""
    blocks, pos = [], 0
    tabs = list(re.finditer(r'<w:tbl>.*?</w:tbl>', body, flags=re.S))
    for i, m in enumerate(tabs):
        end = len(body) if i == len(tabs) - 1 else m.end()
        blocks.append(body[pos:end])
        pos = end
    return blocks


def block_label(block):
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', re.sub(r'</w:p>', ' ', block.split('<w:tbl>')[0])))
    disc = re.search(r'DISCIPLINA:\s*(\S+)', text)
    serie = re.search(r'ANO/SÉRIE:\s*(\d+)\s*º\s*([A-Z])', text)
    total = re.search(r'TOTAL DE AULAS DO PERÍODO:\s*(\d+)', text)
    return dict(disc=disc.group(1) if disc else '?', serie=int(serie.group(1)) if serie else 0,
                turma=serie.group(2) if serie else '?', total=total.group(1) if total else '?')


def p(text, size=24, bold=False, color='241C2B', after=120, align='left', page_break=False):
    r = ('<w:br w:type="page"/>' if page_break else '') + (f'<w:t xml:space="preserve">{escape(text)}</w:t>' if text else '')
    rp = f'<w:rPr>{"<w:b/>" if bold else ""}<w:color w:val="{color}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'
    return f'<w:p><w:pPr><w:spacing w:after="{after}"/><w:jc w:val="{align}"/></w:pPr><w:r>{rp}{r}</w:r></w:p>'


def index_table(rows):
    cell = lambda t, w, b=False, fill=None: (
        f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>' + (f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else '') +
        f'<w:tcMar><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/></w:tcMar></w:tcPr>' +
        p(t, 24, b, 'FFFFFF' if fill else '241C2B', 0) + '</w:tc>')
    widths = [900, 4600, 3200, 3200]
    b = '<w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:sz="6" w:space="0" w:color="C79A3B"/>' for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')) + '</w:tblBorders>'
    out = f'<w:tbl><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/>{b}</w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>'
    out += '<w:tr>' + ''.join(cell(t, w, True, '6B1E2E') for t, w in zip(['Nº', 'Disciplina', 'Série e turma', 'Total de aulas no mês'], widths)) + '</w:tr>'
    for i, r in enumerate(rows, 1):
        out += '<w:tr>' + ''.join(cell(t, w) for t, w in zip([str(i), r[0], r[1], r[2]], widths)) + '</w:tr>'
    return out + '</w:tbl>'


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    skip = {opt('--titulo'), opt('--prof'), opt('--disciplinas')}
    args = [x for x in a if not x.startswith('--') and x not in skip]
    out_path, plans = args[0], args[1:]
    title = opt('--titulo', 'Planos de aula')
    prof = opt('--prof', '')
    order = [x.strip().lower() for x in opt('--disciplinas', 'História,Geografia').split(',')]

    base = zipfile.ZipFile(plans[0])
    base_xml = base.read('word/document.xml').decode('utf8')
    head = base_xml[:re.search(r'<w:body>', base_xml).end()]
    _, sect = body_of(base_xml)
    base_rels = base.read('word/_rels/document.xml.rels').decode()
    extra_rels, extra_files, blocks = [], {}, []
    docpr = [1000]

    for idx, pl in enumerate(plans):
        z = zipfile.ZipFile(pl)
        xml = z.read('word/document.xml').decode('utf8')
        body, _ = body_of(xml)
        rels = rels_of(z)
        used = sorted(set(re.findall(r'r:(?:embed|id|link)="([^"]+)"', body)))
        remap = {}
        for rid in used:
            typ, target, mode = rels[rid]
            if mode == 'External':
                new = f'rIdU{idx}x{len(remap)}'
                extra_rels.append(f'<Relationship Id="{new}" Type="{typ}" Target="{escape(target)}" TargetMode="External"/>')
            elif typ.endswith('/image'):
                new = f'rIdU{idx}x{len(remap)}'
                name = f'media/u{idx}_{os.path.basename(target)}'
                extra_files['word/' + name] = z.read('word/' + target)
                extra_rels.append(f'<Relationship Id="{new}" Type="{typ}" Target="{name}"/>')
            else:
                raise SystemExit(f'{pl}: o corpo usa uma relação do tipo {typ} que não sei copiar')
            remap[rid] = new
        body = re.sub(r'(r:(?:embed|id|link)=")([^"]+)(")', lambda m: m.group(1) + remap.get(m.group(2), m.group(2)) + m.group(3), body)
        body = re.sub(r' w14:(?:paraId|textId)="[^"]*"', '', body)       # ids duplicados confundem o Word
        for b in split_blocks(body):
            blocks.append((block_label(b), b))

    def key(item):
        lb = item[0]
        d = lb['disc'].lower()
        return (order.index(d) if d in order else len(order), d, lb['serie'], lb['turma'])
    blocks.sort(key=key)
    out_blocks = []
    for lb, b in blocks:
        def renum(m):
            docpr[0] += 1
            return f'<wp:docPr id="{docpr[0]}"'
        out_blocks.append(re.sub(r'<wp:docPr id="\d+"', renum, b))

    rows = [(lb['disc'], f'{lb["serie"]}º{lb["turma"]}', lb['total']) for lb, _ in blocks]
    cover = (p('', 24, after=1200) + p(title, 72, True, '6B1E2E', 200, 'center') +
             (p(prof, 36, False, '8A5F0A', 600, 'center') if prof else '') + p('Índice dos planos', 32, True, '6B1E2E', 160) + index_table(rows))
    page_break = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    new_xml = head + cover + ''.join(page_break + b for b in out_blocks) + sect + '</w:body></w:document>'
    new_rels = base_rels.replace('</Relationships>', ''.join(extra_rels) + '</Relationships>')

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    zo = zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED)
    for it in base.infolist():
        data = base.read(it.filename)
        if it.filename == 'word/document.xml': data = new_xml.encode('utf8')
        elif it.filename == 'word/_rels/document.xml.rels': data = new_rels.encode('utf8')
        zo.writestr(it, data)
    for name, data in extra_files.items():
        zo.writestr(name, data)
    zo.close()
    print(f'Unificado: {out_path}  ({len(rows)} turmas em {len(plans)} arquivos)')
    for r in rows:
        print('  -', r[0], r[1], '| aulas', r[2])


if __name__ == '__main__':
    main()
