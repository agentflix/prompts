# Como escrever um deck (arquivo `decks/<nome>.js`)

Um deck é um módulo Node que exporta metadados e a lista de slides `S`. O mesmo arquivo gera o HTML
(`build-deck.js`) e o PowerPoint (`build-pptx.js`). Exemplos prontos em `examples/decks/`.

```js
const C = require('/caminho/da/skill/scripts/common.js');   // about(), pause(), close()
module.exports = {
  file: 'Aula-Historia-6ano-semana1-Idade-Media',  // nome dos arquivos de saída (sem acento/espaço)
  DISC: 'História · 6º ano',                        // aparece no rodapé
  title: 'História 6º – Igreja, trabalho e feudalismo', // <title> do HTML e título do PPTX
  aria: 'Aulas 4, 5 e 6 – História 6º ano',
  S: [ ...slides... ]
};
```

## Campos comuns a todo slide
| campo | significado |
|---|---|
| `k` | tipo do slide (tabela abaixo) |
| `a` | cor/aula: `0` geral e `4`,`5`,`6` = 1ª, 2ª e 3ª aula (vinho, azul-petróleo, verde-oliva). Use 4/5/6 por POSIÇÃO, mesmo que a aula do material seja a 10, 11, 12 |
| `au` | aula do dia: `1`, `2`, `3` (cada uma = 50 min). Define a etiqueta "Aula 2 de 3" |
| `min` | minutos planejados para o slide. A soma por `au` deve ficar entre ~35 e 50; mostre a folga ao professor |
| `tag` | linha pequena acima do título (ex.: `Aula 4 · Virem e conversem · 5 min`) |
| `title` | título (até ~45 caracteres; títulos longos viram 2 linhas) |

## Tipos (`k`)
| `k` | campos específicos | quando usar |
|---|---|---|
| `cover` | `title`, `sub`, `meta[]` (3 linhas), `who` | 1º slide, com a foto da professora |
| `agenda` | `items[[chip,titulo,descricao,icone]]` (3), `note` | "Nossa semana" |
| `question` | `qs[]` (1-2 perguntas), `sub?` | abertura "Virem e conversem", "Pause e responda", "Com suas palavras" (fundo escuro) |
| `cards` | `cards[[titulo,texto,icone,numeroGrande?]]` (3 em colunas ou 4 em 2x2), `key?` | ideias em blocos. `key` = faixa "Ideia-chave" |
| `three` | `cols[[chip,titulo,texto,icone,numeroGrande?]]`, `note` | 3 colunas com ícone grande (ordens sociais, tipos de poluição, tipos de relevo) |
| `versus` | `l`,`r` = `[titulo,icone,[2 itens]]`, `foot[[rotulo,texto]]` | comparar duas coisas (campo × cidade) |
| `flow` | `steps[[titulo,texto]]` (3-4), `note?` | processo em etapas com setas |
| `bars` | `bars[{label,pct,c,txt}]`, `note?` | proporções (64% × 36%) |
| `timeline` | `pts[[ano,texto]]`, `from`, `to`, `sub` | linha do tempo proporcional |
| `swords` | `left`,`right`=`[rotulo,titulo,subtitulo,icone]`, `mid`, `key` | duelo/oposição de dois poderes |
| `hub` | `hub`, `nodes[[titulo,texto,icone]]` (3) | um centro com 3 desdobramentos |
| `pyramid` | `tiers[4]`, `notes[4]`, `down`, `up` | hierarquia com setas de fluxo |
| `steps` | `steps[]` (4), `foot` | atividade em passos numerados ("Um passo de cada vez") |
| `reading` | `quote`, `cite`, `ask`, `foot` | leitura de fonte + pergunta |
| `pause` | `n:'1ª'`, `kept[3]`, `next`, `ask` | **ponto de parada** no fim de cada aula de 50 min (use `C.pause`) |
| `about` | — | "Sobre a professora" (use `C.about`) |
| `close` | `points[3]`, `next` | "Para levar" + próxima semana (use `C.close`) |

Ícones disponíveis (campo `icone`): landmark link sword swords book sprout pen hammer users castle home coins map
cross crown mountain wave layers drop rain factory city phone ship globe clock wind bulb pause.

## Estrutura padrão de uma semana com 3 aulas
- **Aula 1 (min 0-50):** `cover` (1) + `agenda` (3) + [`question` 5] + 2-4 slides de conteúdo + atividade + `pause`
- **Aula 2:** `question` + conteúdo + atividade + `pause`
- **Aula 3:** `question` + conteúdo + atividade + `about` (2) + `close` (4)
Com 2 ou 4 aulas na semana, repita o bloco (a semana do plano manda; veja o "Nº DE AULAS").
Cada aula do material da SEDUC vira um bloco: abertura (Virem e conversem) → "Foco no conteúdo" → "Na prática".

## Regras de conteúdo (importantes)
1. **Só use fatos que estão nos PDFs da aula.** Frases curtas, com as palavras do material (resumidas). Se completar algo
   truncado no PDF, mantenha a frase mínima e confira. Exemplos feitos por você (ex.: datas de uma linha do tempo de
   comunicação) devem ser marcados como "Exemplo ilustrativo" no próprio slide.
2. **Temas sensíveis (escravidão, racismo, desastres):** linguagem respeitosa ("pessoas escravizadas"), sem imagens chocantes.
3. **Pensar em TV de 50":** poucas palavras por card (≤ ~90 caracteres), nunca parágrafos. Se não couber, divida o slide.
4. **Um infográfico por aula, no mínimo** (flow, bars, timeline, versus, pyramid, hub, swords, three com número grande).
5. Faixa `key` ("Ideia-chave") nos slides de conteúdo ajuda a fixar e preenche o espaço.
6. Slide `pause` traz: o que ficou (3 itens), a próxima aula e uma pergunta de retomada ("Retome: ...").
7. Tempos: o do material (ex.: "Virem e conversem 5 min", "Atividade 25 min") vale; o resto é estimativa — avise a professora.
