# Preferências, regras e dicas combinadas com a professora

Quem usa: uma professora da rede pública de São Paulo (use o gênero e o tratamento que ela informar; outra pessoa pode operar o computador e testar no PC dela).
Rede pública de São Paulo; leciona História e Geografia no Ensino Fundamental (Anos Finais).
Comunicação: português do Brasil, simples, curto, sem jargão. Resolva sozinho o que for óbvio; pergunte só o que muda o resultado.

## Entregáveis (padrão: os três)
1. **Word** do plano de aula preenchido (um arquivo por série + componente; tabelas A e B espelhadas) **e um Word UNIFICADO**
   com todas as turmas (capa + índice), ordenado por **disciplina** e, dentro dela, **6ºA, 6ºB, 7ºA, 7ºB…** (`consolidate_docs.py`).
2. **HTML** dos slides (1 arquivo, funciona offline: fonte e foto embutidas).
3. **PowerPoint** editável (.pptx) dos mesmos slides + pasta `fonte-Lexend/` com a fonte e um LEIA-ME.
Tudo dentro de uma pasta única, organizada (veja "Organização"). Ao terminar, abra a pasta no Finder (`open`) e
mostre o HTML no Chrome. A professora costuma testar no PC dela: lembre de instalar a fonte Lexend.

## Plano de aula (Word)
- Cada tabela é uma turma (1ª = A, 2ª = B). A linha "DISCIPLINA … ANO/SÉRIE: 6ºA" deve trazer a turma certa em cada tabela
  (os modelos vinham com "6ºA" nas duas). Turmas A e B podem ter nº de aulas diferente por semana — respeite cada uma.
- O **"Nº DE AULAS" da semana manda**: escolher nos PDFs a mesma quantidade de aulas. Essas são as aulas **principais**.
  Os PDFs que sobram viram **correlação** (a professora quer "passar pelos outros temas", sem perder o foco).
- Se o modelo já vem com temas escritos (AULA / CONTEÚDO), **respeite a escolha dela**; senão use as **últimas aulas do bimestre**.
- Semana do **Saresp**: linha de revisão, sem PDF (padrão: 3ª semana; mantenha o texto dela se já existir). Vale para 6º ao 9º.
- **Avaliação Bimestral**: ocupa a última aula da última semana.
- Colunas: AULA, CONTEÚDO/AE (objetivos do PDF), METODOLOGIA (a partir de Para começar / Na prática do PDF),
  RECURSOS, AVALIAÇÃO. "ADAPTAÇÃO CURRICULAR" não se mexe.
- **RECURSOS — sempre**: TV, Livro didático (Livro do Estudante), Material digital SEDUC (PDF), Caderno de Exercícios, lousa e caderno.
  - **Geografia**: mapas e atlas, Google Maps/Google Earth, **Waze (versão web, no computador)**, globo terrestre, imagens de satélite, IBGE.
  - **História**: vídeos no YouTube (documentários/animações), TV Escola e Canal Futura, linha do tempo, mapas históricos e imagens de época,
    fontes impressas, museus virtuais.
  - Tudo precisa caber na **escola pública**. **Celular NÃO pode** (proibido na escola): nada de "Waze no celular"; use computador.
- Corrigir erros do modelo e avisar: ano do período (ex.: "2024" → 2026), totais de aulas que não batem com a soma das linhas,
  disciplina errada no cabeçalho.
- Entregue em pasta separada; **nunca sobrescreva** os originais da professora.

## Slides
- **Layout aprovado** (use sempre): fundo creme, vinho e dourado; cores de apoio por aula (vinho / azul-petróleo / verde-oliva);
  ícones SVG (nunca emoji); cartões brancos; faixa "Ideia-chave"; barra de progresso colorida no rodapé; botões ‹ › ao passar o mouse.
- **Fonte Lexend** (moderna, fácil leitura), tamanhos grandes: o deck será **projetado em TV de 50"**. Mínimos práticos:
  texto de cartão ≥ 24 px (palco 1280×720), títulos 48-54 px. Conteúdo centralizado na altura (nada colado no topo).
- **Infográficos e movimento**: fluxo, barras, linha do tempo, duelo, hub, pirâmide, comparação. Entradas escalonadas, linha do
  tempo que se desenha, tiers que sobem; **respeitar `prefers-reduced-motion`**. No PowerPoint **não há animações** (avisar).
- **Dividido por aulas de 50 min** (a semana do plano tem 2 a 4 aulas): cada slide tem etiqueta "Aula X de N · Y min · min a–b",
  e o fim de cada aula tem slide **"Ponto de parada"** (o que ficou, próxima aula, pergunta para retomar). Mostre "Planejado: X de 50 min".
- Slide "Sobre a professora": foto + dados do Lattes (veja `assets/profile.default.json`). O Lattes exige captcha: peça o **PDF do
  currículo** (ele é imagem; use `tesseract -l por`) ou os dados por escrito. Não afirme formação que o Lattes não traz.
- Conteúdo: **só fatos dos PDFs**; exemplo inventado → marcar "ilustrativo"; confira datas.
- Primeiro gere **um** deck, mostre, ajuste; depois gere os demais no mesmo estilo (aprovação do layout veio assim).
- Turma B só ganha deck próprio quando as aulas da semana forem diferentes das da A; senão o mesmo deck serve.

## Organização das pastas (padrão)
```
~/Downloads/planos-aula/<mês-ano>/
  <serie>-<componente>/            ex.: 6ano-historia
     Plano-<serie>-<componente>.docx
     slides/semana-1-<tema>.html / .pptx
  fonte-Lexend/  (Lexend.ttf + LEIA-ME.txt)
~/Downloads/cmsp/<ano>/EF-anos-finais/<serie>ano/<bim>bim/<componente>/   (PDFs baixados)
```

## Armadilhas já vividas
- `goto_url` na aba logada do site derruba a sessão (fica na memória da aba).
- `while read` ignora a última linha sem `\n` ao baixar listas: use `[ -n "$u" ]` ou garanta o `\n` final.
- Trocar o filtro de **série** limpa o **componente**; defina o componente depois.
- Aula duplicada no site (versão adaptada) e aulas só em PPTX existem; aulas podem pular números (ex.: Aula 17 ausente).
- Em arquivos Word, as colunas MET./REC./AVAL. vêm vazias e a coluna ADAPTAÇÃO tem texto fixo; o preenchimento edita o XML.
- Não há Word/PowerPoint na máquina: confira o .pptx com `qlmanage -t -s 1400 -o <pasta> arquivo.pptx` (só a 1ª página) gerando um .pptx por slide
  com `ONLY=<n>`; o .docx confira com `textutil`/`inspect_plan.py`.
- PDF → texto: o layout em duas colunas mistura conteúdo e objetivos; `pdf_meta.py` já separa.
