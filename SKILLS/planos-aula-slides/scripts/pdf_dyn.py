"""Lê o PDF da aula e devolve as dinâmicas (Para começar / Na prática) para a coluna METODOLOGIA."""
import re,subprocess,os,json
CAP=r'[A-ZÇÃÕÁÉÍÓÚÂÊ][A-ZÇÃÕÁÉÍÓÚÂÊ ]{4,}'
def dyn(path):
    full=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout
    m=re.search(r'Para começar\s+(\d+)\s*minutos?\s+('+CAP+')',full)
    op=(m.group(2).strip(),int(m.group(1))) if m else None
    acts=[]
    for a in re.finditer(r'Na prática\s+('+CAP+r')\s+Atividade\s+(\d+)(.{0,80})',full):
        mm=re.search(r'(\d+)\s*minutos?',a.group(3))
        acts.append((a.group(1).strip(),int(a.group(2)),int(mm.group(1)) if mm else None))
    return dict(open=op,acts=acts,livro='Veja no livro' in full)
