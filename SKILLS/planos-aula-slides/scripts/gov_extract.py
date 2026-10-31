# Roda DENTRO do browser-harness (ele fornece js(), time etc.). Não execute com python direto.
#
#   LISTAR as opções dos filtros:   MODE=list browser-harness < gov_extract.py
#   FILTRAR e extrair os links:     MODE=extract F_ANO=2026 F_ETAPA=2 F_SERIE=6 F_BIM=4 F_COMP=9 browser-harness < gov_extract.py
#   Só ler a tela atual (sem mexer): MODE=current browser-harness < gov_extract.py
#
# A aba do site (repositorio.educacao.sp.gov.br/midia) precisa estar ABERTA E LOGADA (gov.br).
# Lição importante: a sessão fica na memória da aba. NUNCA use goto_url/recarregar nessa aba —
# isso derruba o login. Aqui só lemos o DOM e mexemos nos filtros.
#
# Valores dos filtros (conferir com MODE=list): ano = 2026; etapa 2 = Fund. Anos Finais;
# série 6/7/8/9; bimestre 1-4; componente 8 = Geografia, 9 = História (outros: veja a lista).
import json, os, time

MODE = os.environ.get('MODE', 'current')

def setsel(name, value):
    js("""(()=>{const s=document.querySelector('[name=%s]');
        Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,'%s');
        s.dispatchEvent(new Event('change',{bubbles:true}))})()""" % (name, value))
    time.sleep(0.8)

if MODE == 'list':
    print(js("""JSON.stringify([...document.querySelectorAll('select')].map(s=>({name:s.name,
        options:[...s.options].map(o=>[o.value,o.text])})))"""))
else:
    if MODE == 'extract':
        # ordem importa: trocar a série ZERA o componente, por isso o componente vem por último
        for name, env in (('anoLetivo', 'F_ANO'), ('etapa', 'F_ETAPA'), ('serieAno', 'F_SERIE'),
                          ('bimestre', 'F_BIM'), ('componenteCurricular', 'F_COMP')):
            if os.environ.get(env):
                setsel(name, os.environ[env])
        js("document.getElementById('botaoPesquisar').click()")
        time.sleep(4)
    state = js("JSON.stringify({a:document.querySelector('[name=anoLetivo]').value,e:document.querySelector('[name=etapa]').value,s:document.querySelector('[name=serieAno]').value,b:document.querySelector('[name=bimestre]').value,c:document.querySelector('[name=componenteCurricular]').value})")
    # os links reais estão nas props do React de cada botão PDF/PPTX (arquivos[].linkDownload)
    links = js("""(()=>{const seen=new Set(),out=[];document.querySelectorAll('button.btn-download').forEach(b=>{
        const k=Object.keys(b).find(x=>x.startsWith('__reactFiber'));let f=b[k];
        while(f&&!(f.memoizedProps&&f.memoizedProps.arquivos))f=f.return;
        if(f&&!seen.has(f)&&!seen.has(f.alternate)){seen.add(f);f.memoizedProps.arquivos.forEach(x=>out.push(x.linkDownload))}});
        return JSON.stringify(out)})()""")
    print('STATE' + state)
    print('LINKS' + links)
