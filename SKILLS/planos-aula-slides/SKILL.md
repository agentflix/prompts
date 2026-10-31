---
name: planos-aula-slides
description: Gera, de forma guiada e automática, o plano de aula mensal em Word preenchido (turmas A e B), os slides em HTML e o PowerPoint a partir dos PDFs de aula do Centro de Mídias SP / SEDUC (História, Geografia e outras disciplinas, 6º ao 9º ano). Use SEMPRE que a professora (ou quem usa o computador dela) falar em plano de aula, preencher o modelo/arquivo Word da semana ou do mês, baixar os PDFs do gov/repositório/Centro de Mídias, montar slides ou PowerPoint de aula para a TV, aulas de 50 minutos, Saresp, correlação de aulas, "fazer os planos do próximo mês", "fazer igual ao de novembro" ou "gerar as outras turmas", mesmo que ela não cite a skill.
---

# Planos de aula + slides (Word, HTML e PowerPoint)

Esta skill refaz o fluxo que já foi aprovado com a professora: ler o **modelo Word** do plano, pegar nos
**PDFs da SEDUC** as aulas certas (mesma quantidade do "Nº de aulas"), preencher as colunas, e montar os **slides**
(HTML + PowerPoint) divididos por aulas de 50 min. Tudo organizado numa pasta só, com um Word UNIFICADO de todas as turmas.

Leia antes de começar: `references/preferencias.md` (regras e gostos dela — é o que evita refazer coisas) e, ao escrever
os slides, `references/deck-schema.md`. Para baixar os PDFs: `references/gov-download.md`.

Os scripts ficam em `scripts/` (guarde este caminho: `SK=~/.claude-trabalho/skills/planos-aula-slides`).

## Passo 0 — Preparar (uma vez)
```bash
bash $SK/scripts/setup.sh        # instala pptxgenjs e sharp (Node), confere poppler/tesseract
```

## Passo 1 — Perguntar (poucas perguntas, em português simples)
Use AskUserQuestion, agrupando. Pergunte **só o que falta** (o que ela já disse na conversa vale):
1. **Anos/séries das turmas** (6º, 7º, 8º, 9º…) e **quais turmas** de cada ano (A, B, C…).
2. **Componentes** (História, Geografia, outro) e **mês/ano** do plano (ex.: novembro/2026) e o bimestre.
3. **Arquivos-modelo Word**: peça os caminhos (ela costuma ter um por ano+matéria, ex.: "Planos de aula novembro história sextos anos.docx").
   Se não tiver o modelo, avise que sem ele só gero os slides.
4. **PDFs**: (a) ela já tem a pasta com os PDFs → peça o caminho; ou (b) você baixa do site do governo →
   peça o **link** (padrão: https://repositorio.educacao.sp.gov.br/midia) e peça que ela **entre pelo gov.br no Chrome** e avise quando estiver logada.
5. **Foto** dela (para capa e "Sobre a professora") e, se quiser atualizar, o **PDF do Lattes** ou dados novos
   (padrão em `assets/profile.default.json`; confirme só se algo mudou).
6. **O que gerar** (padrão: Word + HTML + PowerPoint) e, se houver mais de uma semana, **quais semanas** em slides
   (padrão: comece pela semana 1 de UMA disciplina, mostre, depois gere o resto no mesmo estilo).
Faltando regra do calendário (semana do Saresp, avaliação bimestral), use o padrão e avise: Saresp = 3ª semana; avaliação = última aula do mês.

## Passo 2 — Pastas (deixe tudo organizado)
Crie `~/Downloads/planos-aula/<mes-ano>/<serie>ano-<componente>/` com o Word e `slides/`. PDFs em
`~/Downloads/cmsp/<ano>/EF-anos-finais/<serie>ano/<bim>bim/<componente>/`. Nunca altere os arquivos originais dela.
Copie `assets/Lexend.ttf` + LEIA-ME para `fonte-Lexend/` na pasta do mês.

## Passo 3 — PDFs (só se ela não os tiver)
Siga `references/gov-download.md`: `gov_extract.py` (browser-harness, **sem recarregar a aba logada**) → `download_pdfs.py`.
Depois leia tudo: `python3 $SK/scripts/pdf_meta.py ~/Downloads/cmsp/<ano>/EF-anos-finais meta.json`
(mostra, por pasta, quais aulas existem; confira lacunas como "Aula 17 ausente" ou aula só em PPTX).

## Passo 4 — Plano em Word
```bash
python3 $SK/scripts/inspect_plan.py "<modelo>.docx"                       # veja tabelas/linhas/aulas por turma
python3 $SK/scripts/assign_plan.py "<modelo>.docx" meta.json 6ano/4bim/historia spec.json --disc História --serie 6º
```
`assign_plan.py` propõe, por turma e por semana, as aulas **principais (A)**, **correlação (C)**, **Saresp (S)** e
**avaliação (V)**. **Mostre o resumo à professora e ajuste o `spec.json`** (ela pode trocar aulas, mover correlações,
mudar a semana do Saresp). Só então:
```bash
python3 $SK/scripts/fill_plan.py spec.json meta.json ~/Downloads/cmsp/<ano>/EF-anos-finais "<saida>.docx" --ano 2026
```
Confira o resultado com `inspect_plan.py` na saída. Repita para cada Word (série+componente).
Os modelos podem trazer erros (ano do período, totais, disciplina errada): o script corrige e você **avisa o que mudou**.

## Passo 4b — Unificar (um arquivo só)
Depois de gerar todos os Words, junte-os em **um documento unificado** com capa e índice:
```bash
python3 $SK/scripts/consolidate_docs.py "<pasta-do-mes>/Planos-<mes>-<ano>-UNIFICADO.docx" plano1.docx plano2.docx … \
        --titulo "Planos de aula – <Mês>/<ano>" --prof "Prof.ª Nome Sobrenome"
```
**Ordem combinada:** por **disciplina** (História, depois Geografia) e, dentro dela, em ordem crescente de turma
**6ºA, 6ºB, 7ºA, 7ºB, 8ºA…** (cada turma começa em página nova). Outra ordem de disciplinas: `--disciplinas "Geografia,História"`.
Os Words individuais continuam na pasta (o unificado é um extra para imprimir/enviar de uma vez). Confira o índice que o
script imprime e abra o arquivo no Finder.

## Passo 5 — Slides (HTML + PowerPoint)
1. Leia as aulas escolhidas (`meta.json` + o texto dos PDFs, `pdftotext -raw`) e **escreva o deck** em `decks/<nome>.js`
   seguindo `references/deck-schema.md` (copie um exemplo de `examples/decks/` e adapte). Uma semana = 2 a 4 aulas de 50 min,
   com `pause` no fim de cada aula e infográfico em cada aula.
2. Gere (a foto vai em `PHOTO`; use `scripts/crop_photo.sh` para recortar):
```bash
export PHOTO=~/Downloads/planos-aula/foto.jpg
node $SK/scripts/build-deck.js  "<saida>.html"  decks/<nome>.js
node $SK/scripts/build-pptx.js  "<saida>.pptx"  decks/<nome>.js
bash $SK/scripts/preview.sh "<saida>.html" /tmp/previa        # folhas PNG para você olhar (alinhamento, textos que estouram)
```
3. **Olhe as folhas** (Read nas imagens) e corrija o que sobrar/estourar antes de mostrar. Para o PowerPoint, gere miniaturas
   com `ONLY=<n> node build-pptx.js …` + `qlmanage -t` (veja armadilhas em `references/preferencias.md`).
4. Mostre **um deck primeiro**; só depois gere o resto. O PowerPoint **não tem animações** (diga isso).

## Passo 6 — Entrega
- `open` na pasta do mês no Finder e `open -a "Google Chrome" file://…html#1` no primeiro deck.
- Resuma em poucas linhas: o que foi gerado (inclua o arquivo UNIFICADO), onde está, o que ela precisa fazer (instalar a fonte Lexend no PC onde vai abrir o .pptx),
  o que você assumiu (Saresp, avaliação, correlações, tempos estimados) e o que não pôde conferir (PowerPoint real).
- Pergunte se quer as próximas semanas/turmas.

## Princípios
- **Automático, mas confirmável:** decida o óbvio sozinho; mostre `spec.json`/primeiro deck para ela aprovar.
- **Fiel aos PDFs:** não invente conteúdo; marque exemplos como ilustrativos.
- **Projeção em TV de 50":** texto grande e curto (por isso a Lexend e o limite de palavras por cartão).
- **Escola pública:** recursos viáveis, sem celular.
- Se algo travar (login, captcha, PDF ausente), diga o que falta e peça o arquivo/ação em vez de adivinhar.
