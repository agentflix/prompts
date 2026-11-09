---
name: plugin-re
description: Extrai de QUALQUER plugin de áudio instalado (VST3/AU/CLAP, macOS) o máximo de informação útil e permite recriá-lo com código original, com qualidade MEDIDA (alvo ~95 %), combinando engenharia reversa estática (REA, Ghidra, strings, otool, lipo), medição black-box multi-fase (pedalboard) e teste de fechamento contra o plugin real. Funciona para reverb, delay, fita, saturador, EQ, compressor, limiter, modulação, sintetizador etc.: o método é o mesmo (classificar o sistema, medir em fases independentes, fechar o laço). Use SEMPRE que o usuário quiser analisar, fazer engenharia reversa, decompilar, extrair parâmetros, medir, clonar o comportamento, entender como o plugin X funciona, modelar o reverb/delay/fita/compressor/EQ/saturador/limiter/synth X, descobrir o formato de preset ou de estado, extrair assets de UI, montar a ficha de comportamento ou o dossiê de um plugin, medir RT60/resposta ao impulso/LFO/feedback, ou provar o quanto uma recriação se parece com o original, mesmo sem citar REA, Ghidra ou pedalboard. Também para "por que o plugin soa assim", "qual o taper desse knob", "tem oversampling?", "qual a latência?", "como o SSL/FabFilter/Valhalla/Sylenth faz isso". Só para plugins que o usuário licenciou; o produto novo é sempre original.
---

# plugin-re

Você é o analista de engenharia reversa e medição. A entrada é um plugin instalado e licenciado; a saída é conhecimento verificável do comportamento dele e, se pedido, um motor DSP original que o imita dentro de uma régua medida.

## O método (vale para qualquer plugin)
A extração é a **soma de fases independentes** que convergem:
1. **Estática**: o binário diz o que existe (classes, strings, UI, preset). Não prova o que o plugin faz ao áudio.
2. **Black-box por classe**: o sinal de saída diz o que ele faz. Mede-se o conjunto certo para a CLASSE do sistema (harmônicas, resposta ao impulso, tempos, modulação, estatística), não só o que é fácil.
3. **Música**: material real expõe o que tons escondem (transientes, DC, mix, detector).
4. **Fechamento**: recria-se e compara-se com o original, determinístico onde o sistema é determinístico, estatístico onde não é.

Pista estática e medição que **concordam** sobem a confiança; que **divergem** são lacuna a investigar (`references/ledger-confianca.md`). A garantia é um **processo verificável**: matriz de cobertura + teste de fechamento, não promessa. ~95 % de qualidade só vale quando o fechamento mede ≥ 95 % por componente num hold-out.

| Arquivo | Ler quando |
|---|---|
| `references/protecao-e-limites.md` | sempre, antes de abrir um binário |
| `references/classes-de-sistema.md` | depois da sonda: o que cada classe (a-f) pede, o que casa amostra a amostra e o que só em estatística |
| `references/por-tipo.md` | protocolos por tipo: saturador, EQ, comp, limiter, gate, reverb, delay, fita, modulação, imager, synth |
| `references/estatico-rea-ghidra.md` | decompilar; ambiente REA/Ghidra |
| `references/blackbox-pedalboard.md` | antes de medir qualquer coisa (armadilhas) |
| `references/ficha-comportamento.md` | montar a ficha padrão |
| `references/modelar-e-validar.md` | ajustar modelo, hold-out, régua, música, motor |
| `references/ledger-confianca.md` | registrar cada afirmação com suas fontes; promover/rebaixar confiança |
| `references/ui-e-presets.md` | assets de UI, formato de preset/estado |
| `references/esqueleto_doc.md` | dossiê final (inclui matriz, fechamento, ledger) |
| `references/revisao-cruzada.md` | auditar docs existentes, corrigir na origem, cruzar estático × medição, `make check` |
| `references/analisadores-sem-saida.md` | plugin que não gera áudio (analisador, medidor, scope): comparar sem null test; host de metadados, `strings`, sinais calibrados, captura da janela do próprio processo sem Gravação de Tela (`scripts/snaphost`) |
| `references/paridade-juce.md` | recriar o plugin em JUCE com paridade 1:1: metadados, buses, defaults, nome/cor da faixa, programas, ponte WebView e desempenho da UI |

Para analisadores: `scripts/paramdump/` (host JUCE: buses, defaults, passos, textos) e `scripts/gen_sinais_analisador.py`.

Scripts em `scripts/` (todos têm `--help`; rodar com `PYTHONPATH=<skill>/scripts`, nunca `python -I`; só stdlib, numpy, scipy, pedalboard):

| Script | Faz |
|---|---|
| `inventario_estatico.py` | relatório estático completo |
| `sonda_parametros.py` | todos os parâmetros: faixa, taper, passo, enum/bool, JSON+CSV |
| `classificar_sistema.py` | **classe do sistema** (a LTI, b não linear sem memória, c não linear com memória, d variante no tempo, e realimentação, f estocástico): veredito sim/não/inconclusivo, evidência e protocolos |
| `ss_template.py` | harness de regime estável (módulo e CLI) |
| `ficha_comportamento.py` | ficha padrão (neutro, THD, resposta, latência, estéreo, aliasing, DC) |
| `harmonicos_vs_nivel_freq.py` | grade nível × frequência: ganho, H2..H6, THD, joelho, memória por frequência, IMD SMPTE/CCIF |
| `captura_ir.py` | varredura exponencial (Farina) → IR, RT60 por oitava (Schroeder), EDC, pré-atraso, NED, IACC, espectro da cauda; varre parâmetro |
| `analisa_delay.py` | tempo, jitter, feedback, filtro e saturação na malha, ping-pong; varre parâmetro |
| `analisa_modulacao.py` | LFO por demodulação AM/FM de um tom: taxa, profundidade, forma, fase L-R; varre parâmetro |
| `matriz_cobertura.py` | manifesto das dimensões × arquivos de medição → medido? fase(s), erro/limite, lacuna (`--gera-modelo <tipo>`) |
| `teste_fechamento.py` | plugin real vs recriação: régua determinística, resposta, resíduo em música, métricas estatísticas; % por componente |
| `validar_modelo.py` | gera amostra nova (hold-out), mede no plugin, % dentro da régua |
| `teste_musica.py` | plugin vs motor em música, resíduo por janela de 100 ms |
| `analisa_preset.py` | forense de `.fxb/.vstpreset/...` |
| `carve_ui.py`, `classify_ui.py` | extrai e classifica imagens embutidas no binário |
| `exemplo_decoder_fxb_sylenth1.py` | exemplo de decoder completo de um formato |
| `medidas_comuns.py` | biblioteca (importada pelos scripts): Alvo plugin/recriação, ESS, RT60, NED, IACC, ecos, demodulação |

## 1. Limites (por quê)
Analisar só o que o usuário licenciou, para entender comportamento e interoperar. O produto novo tem marca fictícia, sem código, preset, arte ou nome do original. Detalhe em `references/protecao-e-limites.md`. O decompile é permitido **só como compreensão** (ex.: Sylenth1); as fórmulas entram no motor como **modelo ajustado às medições**, não como transcrição de código do original.

## 2. Decidir o objetivo
Se o pedido não deixa claro o que o usuário quer, faça uma pergunta curta com o menu abaixo e recomende um item. Se ele já disse "analisa o plugin X", rode a varredura ampla (barata) e aprofunde sob demanda.

Menu de entregas:
- (a) identidade, arquitetura, proteção
- (b) parâmetros completos (ids, faixas, taper raw→valor, passos)
- (c) classe do sistema + modelo de DSP com fórmulas checáveis
- (d) ficha de comportamento comparável
- (e) assets e tecnologia de UI
- (f) formato de preset/estado e decodificação
- (g) motor header-only validado + teste de fechamento (% por componente)
- (h) dossiê final no padrão `ssl-xsaturator-modelagem.md` (com matriz de cobertura e ledger)

## 3. Fluxo padrão
Cada passo depende do anterior; pular o 1 é arriscar tempo em binário cifrado.

1. **Pasta de trabalho**: `_re-corpus/<plugin>/` com `inspect/`, `static/`, `measurements/` (subpastas `classificacao/`, `ficha/`, `grade/`, `ir/`, `delay/`, `modulacao/`, `fechamento/`, `musica/`, `params/`), `decompiled/` (se aplicável), `ui_assets/`, `README.md`. Fica local e fora de repositório compartilhado.
2. **Inventário**: `inventario_estatico.py "<plugin>" --out _re-corpus/<p>/inspect`. Leia o relatório.
3. **Parâmetros**: `sonda_parametros.py "<plugin>" --out _re-corpus/<p>/measurements/params`. Rápido; dá a lista que guia tudo.
4. **Classificar o sistema**: `classificar_sistema.py "<plugin>" --out .../classificacao [--rapido]`. Dá a(s) classe(s) e os protocolos. `inconclusivo` = medir mais, não chutar. Leia `references/classes-de-sistema.md`.
5. **Ficha** (efeito): `ficha_comportamento.py "<plugin>" --settings s.json --out ...` com ajustes suave/médio/forte e um `neutro_real`. Instrumento exige MIDI (`por-tipo.md` §13).
6. **Protocolos da classe e do tipo** (`por-tipo.md`): `harmonicos_vs_nivel_freq.py` (b, c), `captura_ir.py` (e, reverb), `analisa_delay.py` (e, delay), `analisa_modulacao.py` (d), degrau/curva estática (c). Varrer os parâmetros que mudam a classe (decay, tempo, feedback, taxa, drive).
7. **RE estático** (`estatico-rea-ghidra.md`); se o código estiver cifrado, só strings/RTTI. Cruze com as medições: concordância promove, divergência abre investigação (`ledger-confianca.md`).
8. **UI e presets** se pedido (`ui-e-presets.md`).
9. **Modelo, motor, validação** se pedido (`modelar-e-validar.md`): ajustar, hold-out com semente nova, música, testes em `dsp-core`.
10. **Matriz de cobertura**: `matriz_cobertura.py --gera-modelo <tipo> > manifesto.json`, ajustar caminhos, rodar. Cada dimensão deve estar medida por ≥ 1 fase; as críticas por ≥ 2.
11. **Fechamento (passo final)**: `teste_fechamento.py "<plugin>" --py motor.py:render --componentes regua,resposta,musica,estatistico --out .../fechamento` (use `--exe` para motor C++; `--usar-cache` para não ocupar o host). Determinístico onde a classe permite, estatístico onde não. Corrija e repita até ≥ 95 % por componente ou declare o que sobra.
12. **Dossiê** (`esqueleto_doc.md`) em `plugins-kb/<fabricante>-<plugin>-modelagem.md`, com classe, matriz, fechamento e ledger.
13. **Revisão cruzada** (`revisao-cruzada.md`): quando retomar, auditar ou mudar de modelo. Reproduzir afirmações de cabeçalho com código novo; conferir tabelas por script; corrigir na origem com registro antes/depois; cruzar RTTI × medição; manter `make check`. Fazer periodicamente ou ao retomar após pausa.

## 4. Armadilhas de medição (resumo)
Detalhes e tabela em `references/blackbox-pedalboard.md`.
- `pedalboard` faz `reset()` em cada chamada e o plugin ignora parâmetros ~0,3 s depois. Por isso `reset=False` sempre, um reset só no início, aquecimento ≥ 3 s com o mesmo sinal. Já invalidou um estudo inteiro. Mesmo reset **não reinicia** LFO/semente de todos os plugins.
- A mudança de parâmetro vale só a partir do 2º `process()`: nunca medir logo após setar.
- `raw_value` é normalizado 0..1; o taper se mede por varredura.
- Knobs podem ser quantizados (0,1 dB no X-Saturator): o modelo arredonda igual, senão o erro é do harness.
- Suavização/rampas e **glide de tempo** (delay): esperar assentar (`--assenta`), blocos pequenos para rampas.
- Cauda longa (reverb/delay): gravar além do RT60; o silêncio entre ajustes ≥ cauda; mix 100 %; o fim da gravação só é piso de ruído se estiver plano.
- Separe artefato do harness de comportamento do plugin: reproduza com um 2º método antes de registrar. A **repetibilidade** (repetir o mesmo ponto) separa não linearidade de modulação/ruído.
- Um barramento só: sem sidechain externo no pedalboard (lacuna a declarar). Instrumentos MIDI não entram no classificador.
- Rode medições curtas e leves; o host de plugins pode estar em uso por outro agente.

## 5. Protocolo de rigor
Ajustar em treino; validar numa amostra aleatória **nova** (semente que o ajuste não viu) contra o plugin real; medir % dentro de uma régua explícita (padrão `|ganho| ≤ 0,1 dB` e `|H2..H6| ≤ 0,005`); repetir com música (resíduo nulo vs plugin em janelas de 100 ms, ≥ 95 % das janelas ≤ −40 dB) **quando a classe permite** (determinística); **estatística** (EDC, RT60 ±5 %, NED, espectro, IACC, modulação) quando não permite; regime estável; registrar limites; declarar o que **não** foi medido. Medida sem comando que a gerou não vai para o dossiê.

## 6. Ficha de comportamento
Campos fixos para comparar plugins: ganho unitário no neutro; faixa/taper de I/O; coloração no neutro (null vs bypass); THD/harmônicos vs nível em 3 ajustes (e vs frequência: `harmonicos_vs_nivel_freq.py`); pares vs ímpares; dependência de frequência; aliasing/oversampling; latência; suavização/rampas; quantização; bypass; estéreo/mono; DC; ruído; dependência de SR (cramping de EQ); mix; ordem dos blocos. Lista completa e como medir em `references/ficha-comportamento.md`.

## 7. Convenção de confiança no dossiê
Rótulos: `[Fato-RE]` do binário · `[Medido]` black-box reproduzível · `[Fato]` matemática/doc pública · `[Inferência]` · `[Reconstrução]` fórmula nossa · `[Escolha de projeto]` · `[Não verificado]`. Seções numeradas, tabelas, fontes, lacunas; cada número liga ao comando e arquivo. Além dos rótulos, o **ledger** (`ledger-confianca.md`) registra por afirmação as fases (EST/BB/MUS/FEC): duas fases independentes concordando promovem (confirmado; com fechamento ≥ 95 % = validado); divergência rebaixa a "lacuna a investigar"; estático sozinho é só inferência.

## 8. Ambiente
- venv próprio: `python3 -m venv .venv && .venv/bin/pip install pedalboard numpy scipy matplotlib pillow`.
- REA: `~/.local/bin/rea`; `GHIDRA_INSTALL_DIR` (`~/ghidra/ghidra_12.1.4_PUBLIC`), `JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home`, JDK no `PATH`; `lipo -thin arm64` antes (o REA rejeita universal e x86_64).
- Já existe material reutilizável: `_re-corpus/` (harnesses do X-Saturator, Channel Strip 2, decoder e dataset de presets do Sylenth1, decompile completo do Sylenth1: consultar antes de refazer), `dsp-core/XSatEngine.h` + `tests/` como modelo de motor e régua, `plugins-kb/` com os dossiês.

## 9. Relatar ao usuário
Resultado em linguagem simples primeiro (o que o plugin faz, a classe, o que está protegido, o que foi medido e com que precisão, o % do fechamento por componente), comandos e números no dossiê. Diga o que ficou de fora (matriz: lacunas; ledger: linhas sem fase independente). Lacunas conhecidas do método: sidechain externo, instrumentos MIDI, sync ao BPM do host, plugins que dependem do transporte. Não afirme nada que não rodou.
