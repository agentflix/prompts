# UI fotorrealista: receitas que chegaram ao nível final (REELER, 2026-11)

O que o REELER (gravador de fita de rolo, painel 1672x941, Three.js em tempo real) aprendeu em 16 rodadas, organizado para que a **v1 de um plugin novo já saia** com textura fina, sombreamento medido, aço escovado e relevo 3D de verdade. Projeto de origem: `~/Documents/plugins/reelr/ui-pro/` (`CLAUDE.md` com medições por rodada; `src/art.js`, `panel.js`, `deck.js`).

Esta referência **complementa** `realistic-hardware-ui` e não repete o que já está lá:

| Assunto | Onde está |
|---|---|
| medir a foto, sistema de ref px, loop de screenshots, validador | `realistic-hardware-ui/SKILL.md` e `references/review.md` |
| fórmula do cromo/níquel, env de estúdio, mapas ripple/wear, knurl | `realistic-hardware-ui/references/chrome.md` |
| receitas-base (painel, parafuso com decalque Phillips, VU, balística, blob de contato) | `realistic-hardware-ui/references/components.md` |
| desgaste (limpo/leve/forte), helpers `scratches/smudges/fingerprint/grimeEdges` | `realistic-hardware-ui/references/wear.md` |
| vidro de display | `realistic-hardware-ui/references/displays.md` |
| armadilhas gerais | `realistic-hardware-ui/references/pitfalls.md` |

Scripts de medição genéricos: `scripts/foto/` (README lá). Divergências com a skill companheira: §14.

## Conteúdo
1. Perguntas que precisam ir cedo
2. Esqueleto da v1 (arquivos, unidade, câmera, paralaxe, flags)
3. Desempenho: render sob demanda (na v1, por padrão)
4. Luz e ambiente (cor neutra)
5. Texturas finas
6. Tabela de materiais
7. Sombras
8. Placas e chassi
9. Peças: knobs, parafusos, VU, LEDs, carretéis, cabeçote, guias, fita, madeira, topo
10. Ordem de construção da v1
11. Fluxo de rodadas
12. Checklist antes de mostrar ao dono
13. Armadilhas que custaram rodadas
14. Divergências com `realistic-hardware-ui`

---

## 1. Perguntas que precisam ir cedo (fase 2, junto com desgaste e presets)

| Pergunta | Por quê | Como |
|---|---|---|
| **Knobs retos ou vistos de cima (tampa deslocada, lateral zigrinada à mostra)?** | O dono pediu retos, aprovou, e depois escolheu "vistos de cima" como na referência: refazer knobs custou 2 rodadas. | `AskUserQuestion` com recorte da ref ao lado. Antes de trocar uma escolha aprovada: commit + tag (`git tag ui-pro-knobs-retos`) para poder voltar. |
| **A referência é imagem sua (gerada em IA, desenho próprio)?** | A regra "marca fictícia" vale para equipamento de terceiros. Se a imagem é do dono, a marca/logo dela pode ser copiada exatamente (o REELER copiou o "M" de 3 lâminas). | Perguntar; registrar a resposta no CLAUDE.md do projeto. |
| **Modelo 3D pronto (Tripo, Meshy etc.)?** | Malha única com textura colada, sem peças separadas, exportação paga: não serve para knobs/carretéis/agulhas que se movem. | Recomendar procedural (esta referência). Alternativa barata: a própria imagem como fundo + peças móveis 3D por cima. |
| **Quais elementos existem na ref e quais não?** | Inventar emenda/fresta que a ref não tem (placa do VU separada) e esquecer peças reais (placas laterais com grade, base mecânica do cabeçote, pedestal das guias) custou rodadas. | Antes da v1, liste peça por peça olhando a ref em 3x (`grid.mjs`); mostre a lista ao dono só se houver dúvida. |

## 2. Esqueleto da v1

- **Arquivos** (Vite + `vite-plugin-singlefile`, ver `como-construimos.md` §3): `layout.js` (tabela `POS` única em ref px + `HIT`/`hitTest`), `art.js` (canvas 2D: placas, madeira, face do VU, escalas), `panel.js` (cena, materiais, peças), `deck.js` ou equivalente (peças grandes de uma região), `helpers.js` (canvas, RNG, `lathe`, `texOf`), `main.js` (estado, simulação, gestos, HUD, `window.ui`), `bridge.js` (SPEC/PRESETS).
- **Unidade do mundo = 1 ref px**; z = altura em ref px. `WP(x, y, z) = (x - W/2, -(y - H/2), z)`.
- **Câmera quase ortográfica com frustum fora do eixo**: `PerspectiveCamera(10°)`, distância `d = 7000`, `projectionMatrix.makePerspective` recortado para o painel encher o quadro. Perspectiva leve = peças altas mostram a lateral do lado certo, sem distorcer o layout.
- **Compensação de paralaxe por altura**: tudo que fica alto (tampa do knob z 13, caixa elevada z 50-62, HUD z 70) é deslocado para cair onde a ref mede na pose de repouso:
  ```js
  const comp = (pw, z) => new THREE.Vector3(-(pw.x - CAM.x) * z / CAM.d, -(pw.y - CAM.y) * z / CAM.d, z);
  ```
- **Paralaxe do mouse**: ±1,5° no máximo, suavizada (`par.c += (par.t - par.c) * min(1, dt*7)`), volta a 0 no `pointerleave`.
- **Perspectiva própria de peça (vista de cima)**: grupo com matriz de **cisalhamento por z**, calculada para o topo cair no centro medido da ref (guias, miolo do carretel). Na tabela `POS`, guarde base e topo medidos (`{x,y}` da base, `{cx,cy}` do topo):
  ```js
  const b = WP(G.x, G.y), c = WP(G.cx, G.cy), px = (b.x - CAM.x) * H / CAM.d, py = (b.y - CAM.y) * H / CAM.d;
  const kx = (c.x - b.x - px) / H, ky = (c.y - b.y - py) / H;
  sh.matrixAutoUpdate = false; sh.matrix.set(1, 0, kx, b.x,  0, 1, ky, b.y,  0, 0, 1, 0,  0, 0, 0, 1);
  ```
- **HUD**: planos `MeshBasicMaterial` aditivos com canvas dinâmico (LEDs, ícone de power, texto do preset, brilho dos VUs), `depthTest:false`, `renderOrder 50`, redesenhados **só quando a chave de estado muda** (`hudKeys[name] !== key`). Preto num HUD aditivo = nada somado (use isso para "apagar" o bloom dentro de uma calha).
- **Flags de URL**: `?freeze` (carretéis no ângulo 0, agulhas em repouso, sinal zerado: obrigatório para comparar com a ref), `?debug` (estado/fps). Erro de WebGL vira barra visível na página (`WEBGL UNAVAILABLE: ...`), não tela branca muda.
- **Escalas, ticks e legendas fora do painel iluminado**: canvas transparente num plano `MeshBasic` sem tone mapping (z 0,7). No painel iluminado o texto escurece e muda de cor com a luz.

## 3. Desempenho: render sob demanda (já na v1)

O REELER rodava `requestAnimationFrame` a 60 fps sempre. Parado, aqueceu a máquina do dono: Chrome ~40 % CPU + GPU ~35 % + WindowServer ~33 %. VSM com 25 amostras, `pixelRatio` 2 e centenas de malhas custam isso a cada quadro, mesmo sem nada mudar. Regras para a v1:

1. **Pausar com a janela oculta** (`visibilitychange`).
2. **Limitar a ~30 fps** quando algo anima (agulha, carretéis, lâmpada, paralaxe).
3. **Renderizar só quando suja** (dirty flag): gesto, `ui.set`, evento do host, resize, fim de carregamento de fonte.
4. **Animação contínua só quando necessária**: carretéis giram só ligados e com sinal (ou transporte rodando); agulha anima só enquanto fora do repouso ou com velocidade; simulação de medidor desligada quando o host manda `setMeter`.
5. **Sombras estáticas**: `renderer.shadowMap.autoUpdate = false`; `renderer.shadowMap.needsUpdate = true` uma vez **depois de montar a cena** (senão o mapa de sombra fica vazio) e de novo a cada mudança que **move sombra** (peça que se desloca ou muda de forma, luz que se move, resize do mapa). Peças que giram em torno do próprio eixo (carretel, tampa de knob) não mudam a sombra.
6. `pixelRatio = min(devicePixelRatio, 2)`; HUD por chave (§2).

> **Receita NÃO validada no REELER.** O REELER ainda usa `requestAnimationFrame` contínuo (`ui-pro/src/main.js`, `frame()`). O código abaixo é o desenho proposto para a v1 do próximo projeto: meça CPU/GPU antes e depois.

```js
renderer.shadowMap.autoUpdate = false;
let dirty = true, raf = 0, last = 0, animUntil = 0;
const STEP = 1000 / 30;                                         // limite ~30 fps
export function invalidate(ms = 0) {                            // gesto, ui.set, host, resize, fonte carregada
  dirty = true; animUntil = Math.max(animUntil, performance.now() + ms);
  if (!raf && !document.hidden) raf = requestAnimationFrame(frame);
}
export function shadowsChanged() { renderer.shadowMap.needsUpdate = true; invalidate(); }   // algo moveu sombra
document.addEventListener('visibilitychange', () => {
  if (document.hidden) { cancelAnimationFrame(raf); raf = 0; }  // oculta: laço para de vez
  else { last = performance.now(); invalidate(); }              // volta: sem salto de dt, redesenha
});
// carretéis giram só ligados e com sinal/transporte; agulha anima só fora do repouso ou com velocidade
const animating = () => (sim.power && (sim.signal || sim.transport)) || !sim.needlesAtRest();
function frame(now) {
  raf = 0; if (document.hidden) return;
  const moving = animating() || now < animUntil;               // + mola do paralaxe / lâmpada em transição via invalidate(ms)
  if (!moving && !dirty) return;                                // parado: laço morre até o próximo invalidate()
  if (now - last >= STEP - 1) {
    const dt = Math.min(.05, (now - last) / 1000); last = now;
    if (moving) step(dt);                                       // simulação só avança quando algo anima
    drawHud(); renderer.render(scene, camera); dirty = false;
  }
  raf = requestAnimationFrame(frame);                           // quadro pulado pelo limite: tenta no próximo
}
// depois de montar a cena (e de carregar fontes/texturas que mudam silhuetas):
shadowsChanged();
```
Chame `invalidate()` em `pointermove` (paralaxe: `invalidate(600)`), `pointerleave` (paralaxe volta ao centro: `invalidate(600)`), `pointerdown/up`, `wheel`, `ui.set`, `setMeter`, `resize` (resize também `shadowsChanged()`). `sim.power`, `sim.signal`, `sim.transport` e `sim.needlesAtRest()` são nomes ilustrativos: ligue-os ao estado real do projeto. Meta: com a UI parada, CPU do processo da página perto de 0 % no Monitor de Atividade; aberta e animando, abaixo de ~10 %. Se ainda pesar no host, o caminho é assar bitmaps (`como-construimos.md` §11).

## 4. Luz e ambiente (cor neutra)

**Regra:** o ambiente refletido é **neutro**; o calor fica só nas luzes (lâmpada, LEDs, bounce). Um env de estúdio levemente quente (`k, k*.93, k*.82`) tingiu **todo** metal de sépia/marrom. A luminância batia; só o croma (`chroma-probe.mjs`) mostrou. Neutro (`k, k*.985, k*.96`) devolveu placas com croma = ref (7,5 x 7,5).

| Item | Valor que funcionou |
|---|---|
| Renderer | `NeutralToneMapping`, `toneMappingExposure 0.85`, `SRGBColorSpace`, `VSMShadowMap`, clear `0x0c0a09` |
| `scene.environment` | `RoomEnvironment` (PMREM sigma .04), `environmentIntensity 0.32` |
| `metalEnv` (cromo, `chrome.md`) | mesmas caixas de estúdio, **cor por caixa `setRGB(k, k*.985, k*.96)`**; fundo `0x4a4a4a` |
| Sol | `DirectionalLight(0xfff0e6, 2.0)` em `(-900, 1400, 1500)`: luz de cima-esquerda, sombras para baixo-direita (copiar da ref, §7) |
| Sombra do sol | `mapSize 2048`, `radius 14`, `blurSamples 25`, `bias -0.0002`, `normalBias 0.4`, câmera ortográfica cobrindo o painel |
| Fill | `DirectionalLight(0xffe2c4, 0.2)` em `(1400, -500, 2000)` |
| Hemisfério | `HemisphereLight(0xf6f3f0, 0x1a1816, 0.18)` |
| Bounce quente | `PointLight(0xffc49a, 6, 300, 1)` baixo (z 40) perto da peça que "recebe" a lâmpada; difuso, nunca fio contínuo |

- **Cor dos materiais quase neutra.** Cor quente no material + luz quente = bronze/oliva (cabeçote 0xa29c9c, não 0xa89070). Um cinza lilás (`0xb6aebc`) virou roxo quando o env ficou neutro: medir de novo depois de mudar o env.
- **Meça direção e dureza da luz na ref**: quais quinas têm fio de luz (cima/esq.), para onde e quanto caem as sombras (`line-probe.mjs` atravessando a borda de uma peça alta), onde ficam os realces de uma tampa (`polar-probe.mjs`). Posicione o sol para reproduzir isso.
- **Fios de luz de bisel finos e quentes** (`232,226,216` a alfa ~.3; material do bisel `0x4a3d33`), nunca faixa branca (`174` chapado ficou falso).
- **Cobre/bounce**: material `0x9c8574`, `roughness .42`, `emissive 0x1c1008 @ .3`; arcos aditivos `0xc8783a` a .35-.75 embaixo de rolos. Sutil e difuso.

## 5. Texturas finas

**Regra do dono:** escovado **quase sub-pixel**, aparece só no brilho. Grão ou riscos grossos foram chamados de "grotesco" e "zoom demais". Exceção: **madeira** precisa de veio com desenho (catedral irregular), não riscos finos retos.

| Parâmetro | Valor |
|---|---|
| Canvas da arte do painel | `ART_K = 2` px de canvas por ref px |
| Escovado de placa | 1 linha de ruído = 0,5 ref px; 3 escalas em `overlay` com alfa **.12 / .16 / .12**; brilho largo `blur(10px)` a .3 |
| Fios (hairlines) | `brushHair`: ~1 fio a cada 34 ref px² de área, alfa .025-.095, comprimento 6-226 ref px (enviesado curto), 30 % da largura vazando na linha de baixo |
| Riscos de uso | 0,3-0,55 px, 18 % longos (30-220 px), resto 2-24 px; alfa .03-.1 |
| Martelado/grão | `multiply` com células de 2,5 e 7 ref px, alfa .14 e .07 |
| Anéis de torno (carretel, tampa de guia) | `lineWidth .35-.4` texel, passo .45-.8 texel, alfa .03-.15, mapa 1024-2048 |
| Mapa de relevo do painel | só grão fino (`noise N×N` + fios `N/8×N`), `bumpScale .35`, repeat ≈ 1 texel por 0,5 ref px. **Sem oitava média**: sob luz rasante virou ondas/manchas |
| Ferro fundido (trilho, placas laterais) | pites 0,3-1 ref px com meia-lua clara embaixo, ondulação 9 px a .14, "sal" claro raro (alfa .04-.12), sujeira `multiply` borrada |
| Filtragem | `MAX_ANISO = renderer.capabilities.getMaxAnisotropy()` (`panel.js:127`) só nos mapas de cor de arte/escovado/martelado/fita, via `texOf(c, { aniso: MAX_ANISO })` (`panel.js:187`, `deck.js:102`); `texOf` sem `aniso` usa 8 (`helpers.js:77`); mapas de ruído/rugosidade usam `anisotropy = 4` (`helpers.js:62`, `panel.js:21`) |

**Fios por pixel, não por stroke.** Milhares de `stroke()` num canvas grande travaram o rasterizador (~5 s de carga). Acumule em `Float32Array` e escreva um `ImageData`:
```js
const Lt = new Float32Array(W * H);                    // claro; outro array para escuro
for (let i = 0; i < n; i++) { const L = (6 + rnd() * rnd() * 220) * K, xs = rnd() * (W + L) - L, row = rnd() * H | 0, al = .025 + rnd() * .07, sp = rnd() * .7;
  for (let x = Math.max(0, Math.ceil(xs)); x <= Math.min(W - 1, xs + L); x++) { const t = (x - xs) / L, v = al * Math.min(1, t * 6, (1 - t) * 6);
    Lt[row * W + x] += v * (1 - sp); if (row + 1 < H) Lt[(row + 1) * W + x] += v * sp; } }
// -> ImageData com rgb 236 e alfa = Lt*255 (escuro: rgb 0, alfa x1.4); drawImage recortado na placa
```
`hot` opcional: elipses onde os fios claros ficam até 3x mais fortes (brilho escovado da barra do topo nos pontos medidos).

**Madeira (tábua de teca, veio catedral)**: canvas **256 x 4096** para ~45 x 925 ref px (~5,7 px por ref px nos dois eixos: os arcos não esticam). Camadas, em ordem: base `#6a3420` → 7 faixas largas de tom (onduladas, alfa .04-.14) → 70 veios longos ondulados com largura variável e lacunas → **arcos catedral** (7 famílias de parábolas aninhadas, vértice para cima, `blur(2.6px)`, alfa .4) → 1400 estrias curtas onduladas ("chama") → 520 fios longos quase retos irregulares → 3200 poros/flecks claros e escuros → `soft-light` .1 → 40 amassados de verniz + 30 riscos → bisel claro pintado só na lateral **interna** (degradê `rgba(255,215,175,.5)` no pico). Rugosidade: base 95 + manchas/riscos mais ásperos. Material: `MeshPhysical`, `color` HDR multiplicando o mapa (`(3.6, 4.3, 5.7)` esq.; `(2.65, 2.45, 2.35)` dir.), `clearcoat .5`, `clearcoatRoughness .26`. Alvo medido: teca ~130,62,28.

## 6. Tabela de materiais (todos com `envMap: metalEnv` salvo indicação)

| Peça | Material |
|---|---|
| Alumínio de flange (carretel) | `MeshPhysical`, mapa prata `#bcb1a4` com anéis finos + 260 riscos + 9 manchas, `color 0x7a7a7b`, `metalness 1`, `roughness .34` + `roughnessMap` de anéis (base 150, amp .3), **`anisotropy .45`** com `anisotropyMap` tangencial, `envMapIntensity 1.1`, + `conicMat` (§9.5) |
| Placa do miolo | mesmo alumínio mais escuro (`0x8c8884`), `anisotropy .5`, env .9 |
| Gunmetal (cilindro, topo do miolo) | `0x5c5a58` / parede `0x5a5856`, `roughness .3-.38`, env .8; escuro `0x2c2c2e` |
| Cromo de quina (anel fino) | `MeshStandard 0xc8c6c2`, `roughness .16`, env 1.2 |
| Preto lustroso (aro) | `0x121212`, `metalness .3`, `roughness .35`, `clearcoat .8/.2`, env .4 (preto acinzentado ~23 lum, não 0) |
| Aço do cabeçote (platô, asas, chanfros) | `MeshPhysical`, mapa escovado horizontal (6 px de canvas por ref px, rampa de tom medida), `metalness 1`, `roughness .28-.55`, `anisotropy .7` horizontal, env 1.05-1.4; cores quase neutras (`0xa29c9c` platô, `0xc0b4ac` asas, `0xeee8de` chanfro) |
| Parede do cabeçote (laterais das peças) | mesmo aço escovado, mas escuro e fosco: `0x504a44`, `roughness .42`, **env .55** (`deck.js:108`) |
| Tampa de guia | mapa concêntrico finíssimo `#c4bab0`, `color 0x8a837c`, `roughness .22`, `anisotropy .9`, env 1.1, `conicMat` (lóbulo 135°, lo .22, hi 3.3, pw 1.6) |
| Ferro fundido escuro | `0x948d86` / blocos `0x4a4542`, `metalness .85`, `roughness .45-.55`, mapa `hammered` |
| Bisel de placa (geometria) | `MeshStandard 0x4a3d33`, `metalness .8`, `roughness .5`, env .35 |
| Moldura do VU | tampa preta escovada `metalness .55 / roughness .5 / env .55`; lateral externa `0xa8a49e` com shader que clareia por `normal.y` (§9.3) |
| Corpo do knob (borracha) | `0x0a0908`/`0x0e0d0c`, `metalness .25-.3`, `roughness .35-.5`, `clearcoat .25-.5`, env .3 |
| Parafuso (domo) | `MeshStandard`, `RoomEnvironment` (não `metalEnv`): escuro `0x64574a` env .85 / grande `0x8c7b68` env 1.25, `roughness .12` + wearMap (seguir a ref: §14) |
| Botão lustroso | `0x17120e`, `clearcoat 1/.1`, `roughness .3`, room env .6 |
| Fita | `MeshStandard`, mapa cobre-marrom, `vertexColors` (brilho ao longo), `roughness .45`, env .12, **`emissiveMap` = o mesmo mapa a .3** (não some na sombra) |
| Fita enrolada (carretel) | mapa 2048 de espiras + 110 sulcos, `metalness .15`, `roughness .4`, `anisotropy .8`, env .25-.4 |
| Face do VU, tampa do knob, chanfro pintado | `MeshBasic`, `toneMapped:false`: cor exata, fixa em relação à luz |

**Escovado por objeto**: dê a cada objeto o seu ângulo/offset de mapa (`aluAng = [0, .5, 1.1, 2.2, 2.9]`), senão todos repetem o mesmo risco.

## 7. Sombras

**Regra:** sombras com blur e ângulo copiados da ref; **contato curto**; sombra projetada de peça sobre peça; queda de luz por placa.

| Tipo | Receita | Números |
|---|---|---|
| Sol (VSM) | penumbra larga para peças altas | §4 |
| `blob(x, y, rin, pen, dx, dy, a)` | plano com disco opaco (.7) de raio `rin` + penumbra `pen` (.35 → .1 → 0), deslocado para baixo-direita | carretel `(R-8, 28, 8, 13, 1)`; guia `(r+4, 16, 6, 10, 1)` + `(r+9, 6, 2, 3, .6)`; knob `(B*.97, 4, 2, 3, .3)`; parafuso `(7, 5, 1.5, 2.5, .8)` |
| `rectBlob(x0,y0,x1,y1, blur, dx, dy, a)` | retângulo `filter: blur` num canvas próprio | caixa do VU `(7, 3, 6, .8)`; cabeçote `(8, 5, 9, .8)`; trilho `(4, 2, 4, .6)` |
| `well()` (contato do knob, pintado) | gradiente radial deslocado `(+2, +3.5)`, sai só ~6 px além da base, sem halo | `.6 → .22 → 0` |
| Sombra de placa (pintada) | `shadowBlur 8`, offset `(2, 3)`, `rgba(0,0,0,.85)` no canvas da arte (`art.js:120`). **Atenção:** `shadowBlur`/`shadowOffset` do canvas ignoram o `g.scale(ART_K)`: são px de canvas, ≈ blur 4 e offset `(1; 1,5)` em ref px com `ART_K = 2`. Mudar `ART_K` muda a sombra em ref px (ou multiplique por `ART_K`, como `art.js:24`) | placas elevadas: blur 13 |
| Sombra projetada medida | plano gradiente (`depthTest:false`) com alfa por y medido na ref | barra do topo sobre os carretéis: `.85` em y 84 → `.48` em 96 → `.3` em 104 → `.05` em 120 → `0` em 140 |
| AO de poço | disco com gradiente radial `0 → .35 → .9` no fundo de cavidades | miolo do carretel, poço de knob |
| Sombra própria fina | tira gaussiana (alfa .7) 3 px mais larga que a peça, deslocada `(2.5, 4.5)` | fita |

**Queda de luz por placa** (`vig = [topo, base, borda dir.]` em `metalPlate`): topo levemente claro (alfa ~.05-.1 de `240,238,234`), base e borda direita escurecem (preto .1-.25 nos últimos 90 px), manchas largas de tom com `grain(46 px)` a .05. Na ref, nenhuma placa tem tom uniforme.

## 8. Placas e chassi

`metalPlate(g, x0, y0, x1, y1, r, opts)` em `art.js`, nesta ordem: base com sombra → rampa linear (`lin`) e elipses de luz (`lights`) medidas na ref → `shade` (escurece em x) → `vig` (§7) → `brushFine` → `brushHair` → martelado `multiply` → `wearPlate` (se o dono pediu desgaste) → `plateBevel` pintado.

- **Bases neutras e escuras**: grafite `#3f3a36`, `#4b4541`, faixa `#3b3835`; luzes `234,224,214`. A cena aquece ~x(.7,.6,.45) sozinha.
- **Chanfro REAL além do pintado**: `plateFrame()` = faixa de 2,6 px em volta da placa, inclinada (borda externa z 0, interna z `w*.6`); a luz acende cima/esq. pelas normais. Placa elevada: z compensado.
- **Placa contínua quando a ref é contínua**: A + VU + C viraram uma placa só (máscara suave 1140-1176 para trocar de tom). Fresta só onde a ref tem.
- **Placa POWER clara** (`#8d8883`) num rebaixo escuro (`pocket`) com chanfro quase branco + frame `0xb4b0aa`.
- **Desgaste fino** (`wearPlate`, nível entre leve e forte): sujeira borrada na fresta (`blur 5px`, alfa .42) e cantos (raio ≤ 70), manchas pretas e claras pequenas, 1-3 digitais leves (.06), riscos curtos em qualquer direção (área/700, alfa .04-.15, `lw .38`), riscos ao longo do escovado (área/1100), poucos longos (área/20000), pites (área/900). Tudo neutro; escala com a resposta de desgaste da fase 2.
- **Placas laterais do deck**: `ExtrudeGeometry` com bisel, mapa `hammered` + bump, frestas recortadas como furos (contar na ref: eram 6, não 8), parafusos na própria placa.
- **Placas de cor saturada (vermelho, azul) não são `metalPlate` cinza tingido.** Com luz e env neutros sobre um difuso vermelho, o croma lavou e a placa virou rosa. O que funcionou no REELER 37:
  - Painel `MeshPhysical` com a arte como **EMISSIVO** (.92), difuso fraco (.32) e especular .25 / env .15.
  - A luz de baixa frequência da placa vem da própria ref: `scripts/make-lightmap.py` do `reelr/ui-37` tira a mediana do canal R por célula de 20-25 px e gera `src/lightmap.js`. O script tem as caixas das placas e as exclusões (knobs, LEDs, parafusos) fixas no código: copie e reme para a ref nova. Use a ref só como luz de baixa frequência, nunca como textura.
  - O escovado e o desgaste por cima continuam procedurais e finos, com fios e luzes na cor da placa.
  - Bata L* e croma com o `chroma-probe` (ref × render dentro de ~6).
  - Cuidado para não passar do ponto: a v4 ficou `d00514` contra `b21016` na ref (ΔE 10-13).
- **Plugin irmão com outra ref** (REELER → REELER 37, mesmo repositório): copie o esqueleto da UI aprovada (src, scripts, package.json) para uma pasta nova (`ui-37/`), sem `node_modules`, `backups`, `shots` e `dist`. Depois reme o `layout.js` inteiro na ref nova e reaproveite as peças (makeKnob, makeReel, deck), remedindo cada uma. Não mexa na pasta da UI irmã.
- **Ordens de grandeza medidas** (lum 0-255, ref): placa grafite meio 42-44, borda iluminada 85-102, placa C 56-61, faixa inferior 26-35, deck 23-51, POWER 73-95.

## 9. Peças

### 9.1 Knobs vistos de cima (versão final aprovada)

Medir na ref por knob: centro e raio `B` da **base preta**, `cap` = raio da tampa / B (.72-.8), `off` = centro da tampa − centro da base (ex.: input `[-11, -.5]` com B 77, ~14 % de B; a tampa vai para o lado da câmera, a lateral aparece do lado oposto).

| Parte | Receita |
|---|---|
| Base | cilindro preto reto (`lathe`, h 5, quina arredondada .5-1) **maior que a tampa, borda nítida** (AA de 1 ref px, nada de sombra difusa no lugar da borda) |
| Topo da base | anel pintado por pixel (`knobRingTex`, 6 px por ref px): preto lustroso, brilho suave à esq., reflexo de clearcoat definido, fio de luz na quina externa (forte em cima-esq.), fio laranja fino colado na tampa (lâmpada) |
| Corpo zigrinado | `lathe` de `RWb = B-8` (pequenos `B-5.5`) até `cr`, 384 segmentos; cada vértice desloca do centro da base ao centro da tampa conforme a altura; textura por ângulo (`knurlTex`, `MeshBasic`): estrias só no lado iluminado, laranja junto da tampa |
| Tampa | `MeshBasic` pintada e **fixa em relação à luz**; só o indicador gira. Gradiente cônico com contraste **~3:1** (vales ~80, picos ~223 lum; 22 paradas `CAP_STOPS`), 3600 riscos radiais (.03-.09) + anéis concêntricos (passo .7, .1-.12), tinta quente leve `CAPT (1, .86, .75)` |
| Chanfro da tampa | lathe de largura `max(2.6, cr*.08)`, textura 1D por ângulo: prata clara em cima-esq. (120-230 lum), laranja só embaixo/dir.; fio escuro na aresta externa e na quina interna |
| Reflexos fixos | 2 traços brancos (1h e 7h, 17-19 px) com pontas suaves em input/output |
| Indicador | barra preta curta (ou linha branca + entalhe, conforme a ref) |
| Escala | ticks `#f2ebe0` 3,2 px `butt` de B+1,5 a B+13, no plano sem luz |
| Alturas | base 5, tampa 13 (grandes) / 11 (pequenos); compensação `comp(z)` |

Knobs retos (versão anterior, tag `ui-pro-knobs-retos`): mesma base e tampa, sem `off`, sem lateral zigrinada.

### 9.2 Parafusos

Base em `components.md` §6 (domo lathe + decalque Phillips que abraça o domo). Acréscimos:
- Domo `SR 7`, altura `.5 + 2.7*(1-(r/SR)²)^.85`; escala por local (chassi x1.1, cabeçote x1.18, caixa pequena x.6).
- **Arruela/rebaixo escuro** r 13 (preto até 9,6, some em 13) com lábio claro fino só embaixo (`rgba(190,165,140,.45)`).
- Grandes (cabeçote, VU): rebaixo escuro + toro preto em relevo em volta.
- Rotação fixa por posição: `hashRot(x, y) = fract(sin(x*12.9898 + y*78.233)*43758.5453)*π`.
- Parafuso numa peça elevada: cheque que não "vaza" através da peça de cima (um do chassi atravessava a caixa TAPE TYPE).

### 9.3 VU

Base (escala, balística ω 17 / ζ .78 / 1/480 s, lâmpada) em `components.md` §7.
- **Caixa 3D**: moldura `ExtrudeGeometry` (furos = janelas, `depth 4`, bisel 2/2,2) com material duplo `[tampa preta escovada, aço]`; UV da tampa = coordenadas do shape via `repeat (1/FW, -1/FH)` e `offset`.
- **Quina externa** em aço claro por shader: `outgoingLight *= clamp(.42 + .75*normal.y - .1*normal.x, .12, 1)` fora das janelas (cima/esq. claras, baixo escuro) + emissivo neutro por normal.
- **Chanfro das janelas** ("quadro" de ~8 px caindo de z 6 até a face em z 1, meia-esquadria) com textura **pintada por lado** a partir de um degradê medido na ref. Embaixo: âmbar junto da face → grafite → prata `#a8a197` → faixa escura → fio claro `#cdc7bc` na aresta. Em cima: escuro com brilho âmbar. **Prata só em fios**, o resto grafite: sem faixa branca chapada (o dono reclamou do branco estourado).
- **Fio cromado** de 1,1 px na base de cada janela, sumindo nas pontas (gradiente com alfa 0 nas extremidades).
- **Paredes internas** com `emissiveMap` âmbar (forte em cima, concentrado no centro embaixo) ligado à lâmpada.
- **Face com luz atrás**: `MeshBasic`, `toneMapped:false`, `color = (.1 + .9*lamp) * 1.12`. Por pixel: paleta medida (âmbar profundo `40,16,0` → creme `255,253,214`), vinheta lateral/superior/quinas, foco elíptico embaixo-centro, miolo creme largo, fibra de papel `multiply` .04.
- **Dois arcos**: externo 4 px de -20 a 0, interno 2,2 px paralelo (R 225 / 218,5), marcas penduradas no interno, cunha vermelha que engrossa de 7 a 11,5 px, números 500 20,5 px em R+23,5.
- **Agulha**: preta 2,2 px, do raio 100 (escondida sob a faixa) ao 219, ponta mais fina, sombra própria. Se a ref mostra a agulha em repouso inclinada (não radial ao pivô), gire também em torno da ponta (grupo `tilt`) e volte a radial em 0 VU.
- **Vidro**: só aditivo (`displays.md`); fio de baixo âmbar, sem branco.

### 9.4 LEDs segmentados e bloom (HUD)

- Calha pintada na arte: fundo preto, sombra interna em cima, fio de luz embaixo, células apagadas `#261b12` com ranhuras.
- Célula acesa = `sub` ranhuras (8 por célula, ~3,1 px) com degradê horizontal `#e27400 → #ffa610 → #fff4a8 (centro) → #ffa610 → #e27400`; bordas sup./inf. escurecidas; **divisória preta de 2,3 px** entre células.
- Resposta por sub-ranhura (`n*sub` passos): o valor continua contínuo entre células; curvas por barra (`pow 1.6`) para o padrão acender como a ref.
- **Bloom só fora da calha**: retângulo `blur(8px)` `#ff8410` a .85 e depois a calha em preto (HUD aditivo: preto não soma); vazamento de 16 px na célula vizinha; fio de brilho nas paredes.
- LED-ponto: núcleo quase branco r 3,6 + aro laranja + halo r 12. Anel de LED (DRIVE): arco 3,8 px, amarelo só perto do topo, laranja nas pontas, juntas escuras a cada 45°, bloom curto `blur(3px)`.

### 9.5 Carretéis

- **Medir por perfil radial** da borda (centro, R, achatamento vertical `sq` ~.92 pela perspectiva) e as **janelas no desenrolado polar** (`[centro°, meia-largura°, r0, r1]`, setores de ângulo constante, cantos 10/12). Não presuma janelas iguais.
- Flange: `ExtrudeGeometry` (furo central + janelas, `depth 4`, bisel 2,2/1,8, `curveSegments 96`) com **UV planar** (`uvPlanar`).
- **Aro grosso em volta de cada janela** (extrude arredondado de 4,5 px, z acima do disco): o bisel redondo acende um fio de luz de um lado e escurece o outro. Aro externo saliente (lathe, sobe ~3 px, topo arredondado) + filete escuro por dentro. Nada de anéis desenhados por cima ("cara de alvo").
- **Reflexo cônico parado em relação à luz enquanto o carretel gira**: lóbulos calculados no espaço do MUNDO (não giram com a malha):
  ```js
  m.onBeforeCompile = sh => { /* uniforms uC (centro no mundo), uL (lóbulo), uLo, uHi, uPw; varying vWp = modelMatrix * position */
    sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>', `#include <map_fragment>
      float thC = atan(vWp.x - uC.x, vWp.y - uC.y);
      diffuseColor.rgb *= mix(uLo, uHi, pow(.5 + .5 * cos(2.0 * (thC - uL)), uPw));`); };
  m.customProgramCacheKey = () => 'conic';
  ```
  Valores medidos por setor: esq. lóbulo 20°, lo .62, hi 1.75; dir. 95°, .45, 2.5; `pw 2`. Anisotropia tangencial forte (.95) fazia um raio reto de luz saindo do miolo (entregava o CG): use .45 e deixe o cônico fazer os lóbulos.
- **Miolo 3D em degraus** (grupo cisalhado por z, gira junto): placa prata r ~104 com sulco e 6 Phillips em r 95 → aro preto lustroso largo (80 → 59) → cilindro de parede escura (altura ~23) com **anel cromado fino na quina** → topo gunmetal com anéis → poço escuro com AO → cruz de 4 raios finos → porca r 10 com furo e sombra. 2 entalhes pretos se a ref tiver. Sem cruz/hélice desenhada.
- Fita enrolada: disco abaixo do flange com espiras finas + sulcos irregulares; cor por carretel medida (um era marrom-avermelhado, o outro marrom-escuro, não preto).

### 9.6 Cabeçote facetado

- **Sólido de facetas** (`facetMesh`): lista de polígonos 3D `{m: material, p: [[x,y,z],...]}`, triangulados com a normal virada para fora (`out` dá a dica), um `BufferGeometry` por material. Platô z 31, facetas inclinadas para as asas, asas z 26 com parafusos, facetas inferiores das asas até z 22,5, `ringAndWalls()` = chanfro de 3 px em todo o contorno + parede vertical até a base.
- **Sem faixa de luz de borda dura**: normal por faceta acendia uma tira clara chapada. Solução: platô + facetas laterais com **normal forçada para +z** (opção `up`), tom vindo só do mapa escovado (rampa de cor medida), e a transição platô → asa em **perfil S** (14 tiras, `smoothstep`).
- **Base mecânica** que a ref tem: placa de montagem atrás (só a borda aparece, com fio de luz), trapézio inferior facetado, suportes, trilho chanfrado, blocos em ferro fundido. Perceber o que falta é parte da v1.
- Fio de luz = `TubeGeometry` r .75 na aresta de cima (`0xfff6ea`, env 1.6, emissivo fraco); fio de cobre r .7 nas arestas inferiores, discreto.

### 9.7 Guias (rolos)

Cilindro **alto** (h 40) num grupo cisalhado (§2): a lateral aparece de um lado. Pedestal escuro baixo e largo, chanfro claro (`0xc8c0b6`, `roughness .18`), topo com anéis finíssimos + `conicMat` em cruz, UM sulco escuro em r .57. Guias externas com tambor escuro baixo e largo (r 53, h 13,6) que esconde a ponta da fita, e arco de cobre aditivo embaixo. Nada de anéis brancos desenhados.

### 9.8 Fita entre as guias

Lâmina **plana** (12 px de largura medida, z 12) em **trechos retos tangentes**, sempre **por trás** das guias e do cabeçote: as pontas terminam sob a tampa de uma guia, dentro de um tambor ou sob o cabeçote. Sem laço, sem seção redonda, sem arco em volta da guia. Textura: seção quase uniforme (cobre-marrom), bordas escurecem ~7 %, fio claro numa borda, fibras longitudinais. Brilho acetinado ao longo por `vertexColors` (`f0 → pico no meio → f1`). Sombra própria (§7). Se a ref mostra um caminho fisicamente impossível, copie o visual e anote.

### 9.9 Topo elevado e madeira

- Barra/caixa elevada = plano "oclusor" com a mesma arte (recorte por `repeat/offset`) em z 50-62, compensado em paralaxe, projetando sombra medida (§7) sobre o que passa por baixo.
- Brilho escovado da barra: reflexo largo e difuso de baixo contraste (2 elipses a .13/.07) + `brushHair` com `hot` nos pontos medidos; sem raio duro.
- Madeira: tábua `ExtrudeGeometry` (`rrShape r 4.5`, `depth 14`, bisel 2/1,5), `uvPlanar`, `scale.y = -1` para casar com y para baixo; mapa §5.

### 9.10 Botões, teclas e rodapé

- Botão POWER redondo: `lathe` abaulado escuro lustroso (r 31, altura 4,7) + lábio de toro fino claro (`0x8a8178`, r+1,3) em volta; ícone e brilho laranja interno no HUD, apagando com a lâmpada.
- Teclas `<` `>` do preset: relevo separado (degradê `#47413c → #1b1917`, contorno, fio de luz em cima, sombra embaixo); campo do nome rebaixado como vidro escuro (sombra interna em cima, fio claro embaixo); texto no HUD (400, quase branco).
- LED de seleção (radio): poço r 9,5 com lábio claro embaixo + LED aceso r 7,6 no HUD.
- Rodapé abaixo da última placa: quase preto (`#0b0908 → #050404`) + sombra borrada da placa; sem faixa clara de chassi que a ref não tem.

## 10. Ordem de construção da v1

1. Medir a ref: `grid.mjs` por região, tabela `POS` completa (centros, raios, bases/topos, janelas, alturas), lista de peças (§1).
2. Esqueleto (§2) + render sob demanda (§3) + `?freeze`/`?debug` + `window.ui` + `click-test` verde.
3. Luz e env neutros (§4), sol na direção medida.
4. Arte do painel: placas com `metalPlate` completo, chanfro real, escalas no plano sem luz.
5. Peças 3D com relevo real: knobs (na vista escolhida), parafusos, VU completo, carretéis, deck (cabeçote, guias, fita), madeira, topo.
6. Sombras: sol + blobs + sombras projetadas medidas + AO.
7. HUD: LEDs, bloom, lâmpada, preset.
8. Rodada de tons já na v1: `tone-probe` + `chroma-probe` com 30-70 caixas antes de mostrar.
9. Validador independente → aplicar só o que a foto confirma → mostrar ao dono.

## 11. Fluxo de rodadas (o que funcionou)

### 11.0 Laço validar → corrigir (REELER 37, 2026-11: "melhorou um absurdo" em 2 voltas)

Depois da v1, cada rodada é sempre o mesmo ciclo, sem temas fixos:

1. **Validador novo** (subagente que não edita nada e trabalha na scratchpad `.../vN/`): mede TUDO o que ainda difere, ranqueado pelo peso visual, com foco em **iluminação, sombreamento, ângulo, textura e reflexo**, mais a geometria que ainda estiver errada. Ele também lista as **regressões em relação à versão anterior** (passe `shots/v(N-1)/` e a tone-table antiga).
   - O brief exige medir a **FORMA da luz** e não só a média. Use perfis polares nos discos (carretel em r 150/200/250, miolo, tampas de guia e de knob) e perfis de linha atravessando o cabeçote e o trilho.
   - Ele também mede a sombra: direção, comprimento, desfoque e contato.
   - Saída: itens com região, coordenadas, ref × render, correção em números e evidência; no fim, os 8 obrigatórios da rodada.
   - Liste as diferenças intencionais (escala, controles cortados, valores) para ele não reportar.
2. **Corretor** (um subagente, depois do validador): faz backup de `src/` em `backups/v(N-1)/` e confere cada item na ref antes de mudar. Se discordar, recusa e explica. Prioridade: **causa antes de remendo**; quando várias peças erram do mesmo jeito (ex.: tudo aceso por baixo), procure o eixo/luz/textura comum.
   - Entrega `shots/vN/` com full, side-by-side, `cmp-*`, tone e chroma table, `click-test` verde (rodado sozinho, sem processo pesado junto) e a Rodada vN no CLAUDE.md.
3. **Orquestrador**: abre a versão no Chrome e o side-by-side para o dono, olha o side-by-side e conta ao dono o que melhorou e o que piorou. Depois lança o próximo validador.

**Antes da 1ª rodada, anote no CLAUDE.md do projeto:**
- **Contrato de luz** medido na ref: de onde vem a luz (quinas com fio de luz, direção e comprimento das sombras com `line-probe`), e uma tabela **por peça redonda** com os ângulos dos lóbulos e vales (`polar-probe` em 2-3 raios). No REELER 37 cada carretel tinha 4 lóbulos estreitos em ângulos próprios, e cada tampa de guia tinha um eixo bimodal diferente. Um eixo global (ou 2 lóbulos largos para todos) deixou os discos chapados e derrubou a tone-table. Modele cada peça com a sua medida.
- **Lista de diferenças intencionais** (escala cortada, controle removido, valores padrão, preferências de textura do dono). Cole a lista em todo brief de validador para ele não reportar isso.

**Modelo de brief do validador** (subagente novo, `model: "sonnet"`, sem editar nada):
> Você é validador visual independente. NÃO edite nada em `<projeto>`. Trabalhe só em `<scratchpad>/vN/`. Objetivo: achar TUDO que ainda difere da ref, ranqueado pelo peso visual, com atenção especial a iluminação, sombreamento, ângulo, textura e reflexo, e à geometria ainda errada. Diga também o que PIOROU de v(N-1) para vN. Arquivos: ref `ref/ref.png`; render `shots/vN/full.png` (DPR 1, mesma escala), `full-dpr2.png`, `cmp-*.png`, `tone-table.txt`; anterior `shots/v(N-1)/`. Ferramentas: `<skill>/scripts/foto/` (polar, line, blend, grid, tone, chroma), com saída na scratchpad. Meça a FORMA da luz: polares nos discos (carretéis em r 150/200/250, miolo, tampas de guia e de knob) e linhas através do cabeçote e do trilho. Intencionais, não reporte: `<lista>`. Regra do dono: texturas finas, nunca sugira grão. Cada item: região, coordenadas, ref × render (perfil), correção em números, evidência. Saída: (a) regressões, (b) ranking (máx. 12-15), (c) 3 coisas boas, (d) 8 obrigatórios.

**Modelo de brief do corretor** (um subagente; `model: "sonnet"` se o dono pediu):
> Leia o CLAUDE.md do projeto inteiro. Faça backup de `src/` em `backups/v(N-1)/`. Não mexa em `<outras pastas>`. Não use `// comentário` no meio de uma linha com vários comandos (já foram `<n>` vezes). Para conferir a ARMADILHA, rode build e shot depois de cada edição. A versão `<v(N-1)>` é a base aprovada pelo olho do dono: mudanças pequenas e direcionadas, nada volta atrás. Texturas finas: contraste vem de luz/lóbulo/tom. Confira cada item na ref; se discordar, não mexa e explique. Procure a causa comum quando várias peças erram igual. `<itens do validador com números e caminho das evidências>`. Ao terminar: `shots/vN/` (shoot + compare), tone e chroma table, `click-test` sozinho e verde, CLAUDE.md com a Rodada vN e "Ainda difere". Resposta: o que mudou (antes × depois), o que recusou, placar de tons, click-test.

**Regressão entre versões:** os scripts aceitam `REF=` para comparar duas versões do render, por exemplo `REF=shots/v3/full.png node blend.mjs shots/v4/full.png out.png x y w h 3 diff`.

**Validadores erram.** Na v3 do REELER 37, 4 dos 14 itens não batiam com a ref quando o corretor mediu (borda de face, onde termina um trilho, faixa clara só no centro, copo "cinza" só em parte do anel). E um item "corrigido" numa rodada (copo do miolo clareado) voltou como erro na seguinte. O corretor precisa medir antes, e o orquestrador precisa relatar ao dono o que foi recusado.

**Auditoria de peças (inventário e camadas), a cada ~3 rodadas ou quando o dono pedir:** o validador de luz e tom não vê o que falta. No REELER 37 v5, a auditoria achou:
- **Peças faltando:** placas mecânicas laterais do deck com parafusos, colunas duplas na borda, flange cromado sob as guias, fita curva na borda do carretel.
- **Peças inventadas:** um "H-H" quebrado e serrilhas no aro dos carretéis e nos knobs.
- **Formas erradas:** grade com 4 fendas inteiras em vez de 3 cápsulas por fileira, e a placa de trás do cabeçote, que é um trapézio.
- **Parafusos:** domo cromado onde a ref tem furo sextavado fosco.

O brief: "região por região, liste CADA peça com coordenadas e marque OK | FALTANDO | DIFERENTE | INVENTADA; conte parafusos, fendas e ticks; depois verifique a ordem das camadas (o que fica na frente do quê) e os encaixes (vão, contato, emendas que a ref não tem)". O orquestrador abre os 2-3 recortes mais duvidosos antes de mandar corrigir.

**Validadores se contradizem entre rodadas.** O validador da v3 mandou remover as "pontes" da grade; a auditoria da v5 mostrou que a ref tem 3 cápsulas por fileira, ou seja, as pontes existiam. O mesmo aconteceu com a placa de trás do cabeçote: trapézio → retângulo → trapézio. Antes de aplicar uma mudança de FORMA, o orquestrador olha o recorte ampliado da ref.

**Quando parar o laço:** quando o dono aprovar, quando o validador só listar itens baixos (≤ ~10 lum, sem regressão) ou quando 2 rodadas seguidas não mudarem a impressão do dono. Nesse ponto, ofereça ao dono uma rodada final de tons (§11.1 passo 3) e o commit + tag.

Regras que vieram do dono:
- **Textura nunca é corrigida perseguindo o `sd` (contraste local) da ref.** Ao pedir "mais contraste local", o corretor engrossou riscos e anéis, e o dono reclamou que "tá meio grosseiro". Instrua desde o brief: contraste vem de luz, lóbulo e tom; textura fica fina e só aparece no brilho.
- O dono acompanha pelo navegador no meio da rodada. Se ele reclamar, mande a correção ao corretor que está rodando (SendMessage) em vez de esperar o fim.
- Uma tone-table que cai (48 → 41/65) junto com um aspecto que melhora muito para o olho do dono não é motivo para reverter: o olho do dono decide; a próxima rodada ajusta os tons sobre a versão nova.
- Subagentes em Sonnet quando o dono pedir. Um subagente Opus já em andamento não troca de modelo: lance um Sonnet novo com brief completo, apontando o CLAUDE.md do projeto.

### 11.1 Ordem usada no REELER (primeira UI, antes do laço)

1. **v1 completa** (§10). Commit + tag de cada versão aprovada.
2. **Um elemento por rodada**, na ordem de impacto: knobs → chassi/placas → VU → faixa inferior/parafusos → carretéis → deck → topo/madeira. Backup de `src/*.js` antes de cada rodada (`backups/rN-nome/`).
3. **Rodada só de tons e cores** (nenhuma forma muda): `tone-probe` com ~67 caixas (claro e escuro de cada material; `hi`/`lo` quando a caixa mistura dois materiais), meta **|Δlum| ≤ 6** na maioria (o REELER chegou a 53/67, ΔE típico 1-4), depois `chroma-probe` (croma dos claros/escuros = ref).
4. **Passada final de forma** (tamanhos, posições, perfis): `blend.mjs half`, `line-probe` nas bordas.
5. **Auditoria completa ponto a ponto** por região (cor/textura; knobs + VU; carretéis + deck) com recortes 3x.

Em todo passo:
- Recortes **3x ref x render lado a lado** (`compare.mjs`) da família mexida, olhados por você antes de descrever.
- **Validador independente** (subagente novo, só imagens + mapa do código, ver `review.md`). Cruze cada sugestão com a foto: validadores erram números e às vezes contradizem a foto. Diga ao dono o que foi descartado.
- **Prints de recorte do dono** = verdade daquele elemento: reconstrua a peça a partir deles.
- **Um subagente por vez.**
- Registre no CLAUDE.md do projeto, por rodada: o que mudou, medidas ref x render, "ainda difere" ranqueado (vira a pauta da próxima).

Que script responde a qual pergunta (`scripts/foto/`, coordenadas em ref px):

| Pergunta | Script |
|---|---|
| Onde fica, que tamanho tem? | `grid.mjs` (ref) e `IMG=shots/rN/full.png grid.mjs` (render); `blend.mjs ... half` |
| A borda/o bisel/a fita tem quantos px? Onde está o fio de luz? | `line-probe.mjs` atravessando a peça na ref e no render |
| Onde estão os lóbulos/vales da tampa, flange, anel? | `polar-probe.mjs img cx cy r 10` (ex.: tampa de knob em r ≈ .6 do raio) |
| O tom bate? | `tone-probe.mjs` (Δlum, ΔE, sd) |
| O metal está sépia? | `chroma-probe.mjs` (croma dos claros) |
| O escovado está grosso ou na direção errada? | `grain-probe.mjs` (grão, dx/dy) |
| Parece igual? | `compare.mjs` 3x lado a lado (`FULL=1` para a tela toda) |
| Os controles respondem? | `click-test.mjs` com roteiro + `expect` |

## 12. Checklist antes de mostrar ao dono

- [ ] Console limpo (`shoot.mjs`), `click-test` verde, hit areas conferidas depois de qualquer mudança de tamanho.
- [ ] Recortes 3x ref x render de cada família mexida, olhados um por um.
- [ ] Textura: nenhum escovado/grão visível como listra ou ruído grosso em 1x; `grain-probe` com grão ≤ ref.
- [ ] Relevo: nada que deveria ser 3D está desenhado chapado (anéis, cruzes, chanfros pintados onde a ref mostra lateral).
- [ ] Sombras: direção igual à da ref, contato curto, sombras projetadas entre peças, cada placa com queda de luz.
- [ ] Luz: o polar de cada peça redonda (carretel, miolo, tampa de guia, tampa de knob) tem os lóbulos nos ÂNGULOS do contrato de luz (§11.0); nenhuma peça acesa por baixo quando a luz da ref vem de cima.
- [ ] Cor: `chroma-probe` sem metal sépia; nenhum branco estourado em cromo; fios de luz finos e quentes.
- [ ] Nada inventado (emendas, frestas, peças) e nada faltando da lista de peças.
- [ ] `?freeze` igual à ref em repouso (agulhas, carretéis, valores padrão = primeiro preset).
- [ ] Parado, a página não consome CPU/GPU (render sob demanda funcionando; aba oculta = laço parado).
- [ ] Desgaste no nível escolhido; marca conforme a regra (fictícia ou do dono).
- [ ] Pergunta estreita ao dono ("o chanfro do VU ficou no ponto ou ainda branco demais?"), não "gostou?".

## 13. Armadilhas que custaram rodadas

| Armadilha | Correção |
|---|---|
| `// comentário` colado no meio de uma linha com vários comandos apaga o resto da linha. Aconteceu **5 vezes**: `restore()` perdido pintou placas de preto, variável indefinida deu tela branca | Comentário só no fim da linha, nunca antes de código na mesma linha. Depois de editar linhas longas, `shoot.mjs` e procure `WEBGL UNAVAILABLE`/console |
| Milhares de `stroke()` no canvas (fios de escovado) | acumular por pixel (§5) |
| `filter: blur` + `multiply` num canvas grande pintou a placa de preto (GPU) | sem blur em canvas grande; `grain` em célula grande já é suave |
| `anisotropyMap` com UV padrão do lathe = direção errada | `latheZ()`: lathe deitado com **UV planar** (`.5 + x/2R`) |
| Anisotropia tangencial .95 num disco grande | raio reto de luz saindo do centro: .45 + `conicMat` |
| Normal por faceta | faixa de luz de borda dura: normal +z e tom pelo mapa; perfil S |
| Cor quente no material | bronze/oliva com luz quente: material quase neutro |
| `Math.random()` ou RNG global compartilhado | texturas mudam entre builds e mudar uma textura altera outra: seed fixo e **RNG próprio por módulo/textura nova** |
| Texto/ticks no painel iluminado | escurecem e mudam de cor: plano `MeshBasic` sem tone mapping |
| Peças altas fora do lugar medido | perspectiva da câmera: `comp(z)` ou cisalhamento calculado |
| Peça de baixo aparecendo através de peça elevada | conferir z/oclusão de cada parafuso e HUD sob caixas elevadas |
| Valor padrão mudado só na UI (flutter .65) | atualizar também o C++ (`Parameters.h`/presets): defaults = primeiro preset dos dois lados |
| Laço a 60 fps sempre | máquina quente: §3 |
| Carretéis, miolo e tampas das guias **acesos por baixo** (REELER 37 v3). A ref tem luz de cima | Causa: o eixo do lóbulo cônico (`lobe`) estava espelhado (115/125 contra ~78/92 na polar da ref), e o miolo herdava esse eixo. Meça o ângulo dos lóbulos com `polar-probe` na ref e no render e compare o ÂNGULO, não a média. PointLights baixas não eram a causa (zerá-las não mudou nada) |
| Mapa emissivo pintado (brilho das lâmpadas na moldura do VU) que nunca aparece | Ele foi criado mas nunca ligado ao material (`emissiveMap`). Confira no render que cada mapa novo aparece |
| Corretor engrossou riscos e anéis para chegar ao `sd` da ref | O dono achou grosseiro. Ver §11.0: contraste vem de luz/lóbulo, nunca de grão |
| `// comentário` no meio da linha continuou (mais 4 vezes no REELER 37, 9 no total) | Diga no brief de TODO corretor, com o número de vezes |

## 14. Divergências com `realistic-hardware-ui` (a lição nova vale para a plugin-studio)

| Lá | Aqui (REELER) | Como conciliar |
|---|---|---|
| `chrome.md` §6 (e, antes da correção, `pitfalls.md` "Metal too silver"): cor do metal levemente quente | env neutro + cor do material quase neutra; calor só nas luzes | Use base quente só se `chroma-probe` mostrar o metal com croma abaixo da ref |
| `components.md` §9: período do escovado acima de ~1,2 ref px senão "persiana" | fibras de 0,5 ref px funcionaram e foram pedidas pelo dono | O problema é contraste, não período: alfa ≤ .16 em overlay + anisotropia máxima; contraste alto em qualquer período vira listra |
| `components.md` §9: tampa repuxada com `anisotropy ~0.7` | discos grandes: .45 + cônico em espaço de mundo; tampas de knob: textura cônica pintada fixa à luz | Anisotropia física para peças pequenas e sem giro; cônico/pintado quando a peça gira ou o raio de luz aparece |
| `components.md` §6 / `chrome.md` §5: parafuso cromo claro venceu, cinza escuro rejeitado | ref do REELER tinha domos escuros (`0x64574a`) | Siga a ref de cada projeto; meça o domo |
| `components.md` §7: moldura do VU cinza médio, rugosa, facetas de contraste baixo | moldura preta + aço claro na quina externa + chanfro cromado pintado com degradê medido, sem branco chapado | Depende da ref; nunca faixa branca uniforme |
| `SKILL.md`: tempo real por padrão | tempo real **sob demanda** (§3) | Mesmo modo, laço diferente |
| `SKILL.md:71` e `render-modes.md:8`: `VSMShadowMap` com `radius` ~7 | sol com `radius 14` e `blurSamples 25` (`panel.js:154`) para penumbra larga de peças altas | ~7 para controles baixos; 14/25 quando a ref tem penumbra larga (custa mais por quadro: mais um motivo para o render sob demanda) |
