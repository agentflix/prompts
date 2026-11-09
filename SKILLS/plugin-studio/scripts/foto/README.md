# Scripts de medição da UI fotorrealista (ref x render)

Tirados do REELER (2026-11). Node ≥ 18 + Playwright com Google Chrome: `npm i -D playwright` **na pasta da UI** (o Node resolve o playwright a partir do projeto; um playwright só global não serve). Rode **de dentro da pasta da UI** (ex.: `<projeto>/ui-pro`), com a foto em `ref/ref.png` e o build em `dist/index.html`, ou aponte o projeto com `UI_DIR=<projeto>/ui-pro`. Sem playwright no projeto, o script para com uma mensagem dizendo isso (código 2). Copie a pasta inteira (`_comum.mjs` é usado por todos) ou chame pelo caminho da skill:

```bash
S=<this skill>/scripts/foto
node $S/shoot.mjs shots/r3 '{"knobs":[60,525,520,265]}'
node $S/shoot.mjs --help      # todo script: imprime o uso e sai, sem abrir navegador nem criar pastas
```

Coordenadas sempre em **ref px** (pixels da foto). Variáveis: `REF` (foto), `REF_W`/`REF_H` (tamanho de projeto, padrão = tamanho da foto), `PAGE` (arquivo ou URL), `Q` (query, padrão `?freeze` = animação parada; `Q=` desliga), `SEL` (palco, padrão `#stage`; recortes do `shoot` são relativos a ele), `WAIT` (ms), `UI_DIR` (projeto da UI, padrão = pasta atual). A página precisa aceitar `?freeze` (carretéis/agulhas em repouso) para os shots serem comparáveis.

| Script | Uso | Para quê |
|---|---|---|
| `shoot.mjs <dir> [recortes]` | full DPR 1 + recortes DPR 3 + erros do console | smoke test de toda rodada |
| `compare.mjs <dir> <pref> <recortes>` | `{"nome":[x,y,w,h,esc]}`; `FULL=1`, `STACK=1`, `DPR=4` | recortes ref x render lado a lado (o instrumento principal; mande estes ao validador e ao dono) |
| `tone-probe.mjs <render.png> <caixas> [--shoot]` | `{"nome":[x,y,w,h]}` ou `[x,y,w,h,"hi"/"lo",t]`. Render existente: só mede (nunca sobrescreve); inexistente: fotografa nele; `--shoot` refaz e sobrescreve; `SKIP=1` nunca fotografa | tabela de tons: Δlum, ΔE, Δa/Δb, contraste local (sd) |
| `chroma-probe.mjs <render.png> <caixas>` | mesmo caixas.json | croma dos claros/escuros: pega metal sépia/marrom |
| `grain-probe.mjs <render.png> <caixas>` | mesmo caixas.json | grão fino e direção do escovado (dx/dy) |
| `polar-probe.mjs <img> cx cy r [passo]` | ref e render | lóbulos/vales de tampa de knob, flange, anel de LED |
| `line-probe.mjs <img> '[[x0,y0,x1,y1]]'` | ref e render | bordas, largura de bisel/fita, fio de luz, raio de peça |
| `grid.mjs <out> x y w h [esc]` | `IMG=` para o render | medir posição/tamanho com grade de 10 px |
| `blend.mjs <render> <out> x y w h [esc] [half\|diff]` | | sobreposição: deslocamentos e tamanhos |
| `probe.mjs <img> '{caixas}'` | | média RGB rápida numa imagem |
| `click-test.mjs <roteiro>` | `[{"t":"..","drag":[x,y,dy]},{"click":[x,y]},{"expect":{..}}]` | gestos reais + `window.ui.state()`; código 1 se falhar |

Rotina por rodada: `shoot` (console limpo) → `compare` da família mexida → `tone-probe` + `chroma-probe` na rodada de tons → `click-test` se mexeu em layout/hit. Guarde ~30-70 caixas em `scripts/tone-boxes.json` do projeto (claro e escuro de cada material, separando com `hi`/`lo` quando a caixa mistura dois materiais). Receitas e metas: `references/ui-fotorrealista.md`.
