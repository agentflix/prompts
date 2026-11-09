# Manual do plugin em PDF

Como produzir o manual que acompanha o plugin (o mesmo padrão do BRICKR, `docs/BRICKR-manual.pdf`). Serve para qualquer plugin da suíte: o conteúdo muda, o desenho não.

Leia isto na fase 11 (entrega). O manual não é enfeite: é o que faz o usuário leigo conseguir usar o plugin sem te chamar.

## 1. Formato e ferramenta

- **A4 retrato, 8 páginas** (capa + 7 seções). Menos que isso falta informação; mais que isso ninguém lê.
- **HTML + CSS de impressão → PDF pelo Chrome**. Nada de editor de texto: o arquivo fonte é `docs/manual.html`, versionado junto do projeto, e o PDF é gerado por comando. Assim o manual atualiza quando o produto muda.
- Não use reportlab/Word para este manual: o layout é editorial (tabelas, capa sangrada, cartões) e o HTML resolve em minutos.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer --allow-file-access-from-files \
  --virtual-time-budget=6000 \
  --print-to-pdf=docs/NOME-manual.pdf "file://$PWD/docs/manual.html"
```

- `--no-pdf-header-footer` tira a URL e a data que o Chrome imprime por padrão.
- `--allow-file-access-from-files` permite a imagem local da capa.
- Confira sempre com `pdftoppm -png -r 100 docs/NOME-manual.pdf /tmp/mp` e **olhe as páginas**: página quase vazia ou tabela cortada é defeito de CSS, não de conteúdo.

## 2. Estrutura de páginas (a ordem funciona)

| # | Página | Conteúdo |
|---|---|---|
| 1 | **Capa** | fundo escuro sangrado, marca, subtítulo, “MANUAL DO USUÁRIO”, **screenshot real do painel** e rodapé com empresa/versão/formatos |
| 2 | **O que é** | uma frase de posicionamento, diagrama da cadeia de sinal em chips e 4 cartões com os conceitos que mudam o som |
| 3 | **O painel** | tabela seção-por-seção (o que cada controle faz) + presets e navegador |
| 4 | **Parâmetros** | tabela faixa/padrão/observação + a conta principal do motor com um exemplo numérico |
| 5 | **Na prática** | receitas numeradas por uso (master, bus, instrumento) + o aviso que evita reclamação (ex.: true peak) |
| 6 | **Presets de fábrica** | tabela gerada do `presets.json`, agrupada por categoria |
| 7 | **Tecnologia** | a seção que dá orgulho (IDR, oversampling, detector…) com números medidos |
| 8 | **Especificações e instalação** | formatos, latência, CPU, caminhos de instalação, problemas comuns e boas práticas |

Regras editoriais:
- Título de seção numerado (`01`, `02`…) em teal, com filete preto embaixo.
- Fale em **segunda pessoa** e em português simples; número técnico só quando ajuda a decidir (“ATTEN 3–5 dB”).
- Toda página responde “o que eu faço com isso?”. Se não responder, corte.
- Inclua a linha de **problemas comuns** com os sintomas que o usuário realmente relata (“está cortando”, “não faz volume”, “o release não muda nada”).

## 3. Tokens de design

```css
:root{
  --ink:#15171a;      /* texto */
  --ink2:#3d434b;     /* texto secundário */
  --ink3:#6b7280;     /* rótulos, legendas */
  --line:#dfe3e8;     /* filetes e bordas */
  --acc:#12a89f;      /* teal da marca (texto sobre branco) */
  --acc-d:#0b7d77;    /* teal escuro (números de seção) */
  --bg:#ffffff; --soft:#f5f7f8;   /* fundo de cartão */
  --font:"SF Pro Display",Inter,"Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,monospace;
}
```

- **Capa:** fundo `#101114`, texto `#eef1f3`, acento `#4fd8d2` (o teal claro do painel), meta em `#8b939c`.
- **Tipografia:** títulos 800; corpo 15px/1.55; tabelas 13,5px; rótulos 11px caixa-alta com `.08em` de tracking. Números sempre `font-variant-numeric: tabular-nums`.
- **Espaço:** A4 com margem 0 no `@page` e **padding por seção** (`17mm 16mm`) — é o que permite a capa sangrar até a borda sem gambiarra de margem negativa.
- **Componentes:** cartão (`--soft` + borda), nota (barra teal à esquerda), aviso (barra âmbar), tabela zebrada com cabeçalho em caixa-alta.
- **Print:** `-webkit-print-color-adjust: exact` no `body`, senão o Chrome tira os fundos.

## 4. CSS que faz o PDF ficar certo

```css
@page{ size:A4; margin:0; }
body{ margin:0; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.cover{ height:297mm; width:210mm; page-break-after:always; padding:26mm 20mm 18mm; background:#101114; }
section{ padding:17mm 16mm 16mm; }
section.brk{ page-break-before:always; }
h2,h3{ page-break-after:avoid; }              /* título não fica órfão no pé */
table,.card,.note,.warn{ break-inside:avoid; } /* nada de tabela partida */
```

- Quebre página **só** onde precisa (capa, tabela de presets, especificações). Se todas as seções quebram, sobram páginas meio vazias.
- Depois de gerar, conte as páginas: `python3 -c "import re;d=open('docs/x.pdf','rb').read();print(len(re.findall(rb'/Type\s*/Page[^s]',d)))"`.

## 5. A imagem da capa

Nunca desenhe mockup: **renderize a UI de verdade**.

```bash
# 1) a UI servida com o backend JUCE falso (o mesmo stub do teste headless)
python3 - <<'EOF'
import os,re,shutil,subprocess,sys,time
ROOT="."; stub=re.search(r'STUB = r"""(.*?)"""',open("plugin/Tests/ui_headless_test.py").read(),re.S).group(1)
tmp="/tmp/uir"; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
shutil.copytree(ROOT+"/ui/js",tmp+"/js")
html=open(ROOT+"/ui/index.html").read().replace("<head>","<head>\n<script>"+stub+"</script>",1)
open(tmp+"/index.html","w").write(html)
srv=subprocess.Popen([sys.executable,"-m","http.server","8772","--bind","127.0.0.1"],cwd=tmp,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","--headless=new","--disable-gpu",
  "--user-data-dir="+tmp+"/prof","--virtual-time-budget=8000","--window-size=760,430","--force-device-scale-factor=2",
  "--screenshot=docs/painel.png","http://127.0.0.1:8772/index.html"])
srv.terminate()
EOF
```

- `--force-device-scale-factor=2` gera 1520×860: nítido no papel.
- Se a UI for bitmap (skin), a captura é a própria skin em 2×.
- Ajuste o estado antes de capturar (valores típicos, não “-inf” em tudo) para o print parecer em uso.

## 6. Tabela de presets gerada

Nunca digite preset à mão: gere do `presets.json`, senão o manual desatualiza na primeira recalibração.

```python
import json
d=json.load(open('src/presets.json')); rows=[]; cat=None
for p in d['presets']:
    pa=p['params']
    if p['category']!=cat:
        cat=p['category']
        rows.append(f'<tr><td colspan="6" class="cat">{cat}</td></tr>')
    rows.append(f"<tr><td><b>{p['name']}</b></td><td class='num'>{pa['thr']:.1f} dB</td>…</tr>")
```

Formate número com **vírgula** decimal (`-6,0 dB`), como no resto do texto.

## 7. Checklist antes de entregar

- [ ] Screenshot é da UI real, em 2×, com estado plausível.
- [ ] Toda página tem conteúdo suficiente (nada de meia página vazia).
- [ ] Tabela de presets gerada do JSON e com os valores atuais.
- [ ] Faixas/padrões conferem com `Parameters.h` (não com a memória).
- [ ] Latência, formatos e CPU conferem com o build atual.
- [ ] Existe a seção “problemas comuns” com as queixas reais.
- [ ] PDF abre e tem contagem de páginas esperada.
- [ ] O plugin tem um jeito de abrir o manual (botão `?` na UI; ver §8).

## 8. Botão “?” no plugin

O manual precisa estar a um clique dentro do plugin:

1. **Embuta o PDF** no `juce_add_binary_data` junto da UI:
   ```cmake
   juce_add_binary_data(NomeUI SOURCES ${UI_DIR}/index.html ../docs/NOME-manual.pdf)
   ```
   O símbolo gerado vira `BinaryData::NOME_manual_pdf` (+ `...Size`). Confira no header gerado em `plugin/build/.../JuceLibraryCode/BinaryData.h`.
2. **Função nativa** no editor (antes do `web = make_unique<WebBrowserComponent>`):
   ```cpp
   .withNativeFunction ("nomeManual", [this] (const juce::Array<juce::var>&, Done done)
   {
       auto dir = juce::File::getSpecialLocation (juce::File::userApplicationDataDirectory)
                    .getChildFile ("Empresa/NOME");
       dir.createDirectory();
       auto pdf = dir.getChildFile ("NOME-manual.pdf");
       pdf.replaceWithData (BinaryData::NOME_manual_pdf, (size_t) BinaryData::NOME_manual_pdfSize);
       pdf.startAsProcess();          // abre no Preview
       done (true);
   })
   ```
3. **Botão na UI**: ação na barra de presets (`?`) chamando a função nativa; fora do plugin (dev) o botão não faz nada.
4. **Mencione no próprio manual** que o `?` abre o PDF.
