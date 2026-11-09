# UI, assets e formato de preset/estado

Duas entregas do RE que não dependem do DSP e que quase sempre funcionam mesmo com binário protegido: a arte/estrutura da UI (embutida como dados) e o formato do preset (arquivo no disco).

## Índice
1. Tecnologia de UI
2. Carving de assets embutidos
3. Filmstrips e medidas
4. Presets e estado: método geral
5. Receita: VST2 .fxb/.fxp
6. Receita: VST3 .vstpreset e estado do host
7. Do preset ao dataset
8. Limites

## 1. Tecnologia de UI
`inventario_estatico.py` infere por linkagem e strings. Linkado pesa mais que string solta (JUCE traz referências a quase tudo).
- **JUCE** (`juce::`): arte quase sempre em `BinaryData` dentro do Mach-O.
- **iPlug2** (`IGraphics`), **VSTGUI** (`VSTGUI::`), **Qt**, **HISE** (`hise::`).
- **WebView** (`WKWebView`, `WebBrowserComponent`): UI em HTML/JS, procurar HTML/CSS/JS nos recursos ou embutido (gzip/base64).
- **Metal/OpenGL/Skia/NanoVG**: renderização própria; a arte ainda costuma vir como bitmap.
O bundle (`Contents/Resources`) pode ter `.nib`, `.png`, `.pdf`, presets, IRs, `.wav`; `inventario_estatico.py` lista extensões e tamanhos.

## 2. Carving de assets embutidos
Arte fora de `Resources/` está embutida: extrair por assinatura. `scripts/carve_ui.py <binário> <pasta>` varre PNG (`\x89PNG`..`IEND`), JPEG (`FFD8FF`..`FFD9`) e WebP (`RIFF....WEBP`), deduplica por hash e grava com offset, hash e dimensões no nome. `scripts/classify_ui.py <pasta> "<título>"` valida a decodificação e classifica por proporção provável (fundo, knob, botão, medidor) e gera README. Precisa de Pillow. Use o **slice thin** (ou o universal; duplicatas saem por hash).
Binário com código cifrado: o carving continua legível, porque os dados não necessariamente são cifrados; conferir. Ele é só leitura de bytes.

## 3. Filmstrips e medidas
- Knob = **sprite sheet vertical**: N quadros quadrados empilhados (ex.: Channel Strip 90×5490 = 61 quadros de 90 px; Bus Comp quadros de 68 px). N = altura/largura. Quadro i ~ valor i/(N−1).
- O fundo do painel é um PNG grande com os rótulos impressos: dá coordenadas de pixel de cada controle direto do bitmap (centroide de knob, caixas de botão).
- Medir: resolução @1x/@2x, nº de quadros, ângulo de varredura (comparar quadro 0 e N−1), paleta (cores dominantes), tipografia (identificar fonte pelo traçado, sem copiar).
- Uso no projeto novo: **referência de medida**, não arte final. A arte do produto é refeita (marca fictícia); skill `realistic-hardware-ui` faz a parte photoreal.
- Guardar em `_re-corpus/<p>/ui_assets/` com um README (função de cada arquivo, dimensões).

## 4. Presets e estado: método geral
1. **Achar** os arquivos: `~/Library/Application Support/<Fabricante>/<Plugin>/`, `/Library/Audio/Presets`, `/Library/Application Support/<Fabricante>`, dentro do bundle. Ou salvar um preset pelo plugin/DAW.
2. **Forense**: `scripts/analisa_preset.py arquivo --out dir`. Dá assinatura, entropia, streams zlib, strings, plausibilidade de float32.
3. **Hipótese de layout** (cabeçalho, contagem, registros) e **validação**: mudar UM parâmetro no plugin real (pedalboard) e salvar de novo ou comparar o vetor decodificado com `raw_value` lido; mapear índice → parâmetro. Meta: 100 % de coincidência numa amostra (ex.: 40/40).
4. Se o host `get_state/program change` não restaura valores (o Sylenth1 devolveu lixo via pedalboard), decodificar o **arquivo** diretamente.

## 5. Receita: VST2 .fxb/.fxp
Cabeçalho big-endian: `CcnK`, tamanho, magic (`FxCk` programa de params, `FxBk` banco de params, `FPCh` programa com chunk, `FBCh` banco com chunk), versão, `fxID` (4cc do plugin), `fxVersion`, nº de programas/params, depois chunk (`FBCh`: tamanho em offset 156, dados a partir de 160). O chunk é **opaco** e específico do plugin.
Caso Sylenth1 (decodificado): chunk com tag `syl1` (LE `1lys`), bancos de fábrica em **zlib**, comerciais sem compressão → header (nProg, nParam=244) → registros de `nParam × float32` + 36 B de nome. Mapa: `float[i+1]` = parâmetro VST3 `i` (validado 40/40). Exemplo em `scripts/exemplo_decoder_fxb_sylenth1.py`. O `analisa_preset.py` já achou o zlib nos bancos de fábrica, com 99,5 % dos float32 em [0,1].

## 6. Receita: VST3 .vstpreset e estado do host
`.vstpreset`: `VST3` + versão + classID (32 B) + offset da lista; lista `List` de chunks (`Comp` = estado do componente, `Cont` = controller). `Comp` pode ser: vetor de floats, XML/JSON, blob proprietário (JUCE: `getStateInformation` costuma ser XML ou ValueTree binário com magic `VC2!`). AU `.aupreset` é plist. Procurar o parâmetro conhecido (mudar um e comparar bytes: diff de binário) é o jeito mais rápido.
Estado do host (`fx.raw_state` no pedalboard) segue o mesmo método.

## 7. Do preset ao dataset
Com o decoder: JSONL de milhares de presets (170 708 do Sylenth1 em 1260 bancos), com nome + vetor. Estatísticas por categoria (o nome do preset costuma trazer a categoria: BS, LD, PD, KY...) revelam práticas: pads = ataque/release longos + unison + reverb; baixos/drums = ataque instantâneo + pouco unison; leads = unison máximo. Esses números alimentam presets **originais** do produto novo; **não** redistribuir presets de terceiros.

## 8. Limites
- Estado cifrado ou assinado: parar.
- Presets com samples/IR embarcados: tratar como conteúdo licenciado.
- Formato decodificado ≠ permissão para reempacotar o conteúdo.
