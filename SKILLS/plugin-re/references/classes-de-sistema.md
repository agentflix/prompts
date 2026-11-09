# Classes de sistema: como identificar, o que medir, o que casa e como

O MÉTODO é o mesmo para qualquer plugin: **classificar o sistema, escolher os protocolos da(s) classe(s), medir em várias fases independentes, fechar o laço** (recriar e comparar). O tipo de plugin (reverb, fita, EQ...) só decide quais protocolos de `por-tipo.md` entram. `scripts/classificar_sistema.py` faz a classificação por testes curtos no plugin real; este arquivo explica o que cada veredito pede.

## Índice
1. Tabela das classes
2. Como o classificador decide (testes e limiares)
3. O que casa amostra a amostra e o que só casa em estatística
4. Combinações comuns
5. Limites do classificador

## 1. Tabela das classes
| Classe | Como identificar (empírico) | Métricas de fidelidade | Casa amostra a amostra? |
|---|---|---|---|
| **(a) linear e invariante no tempo (LTI)**: EQ, filtro, ganho, crossover | ganho do tom igual em todos os níveis (< 0,08 dB), THD < −75 dBc, IR igual se deslocada, sem bandas laterais | magnitude e fase por banda (`|erro| <= 0,1 dB`, fase ±5°), IR (resíduo nulo), cauda/latência | **sim**: null contra o plugin deve chegar a −60 dB ou menos |
| **(b) não linear sem memória**: saturador, clipper, waveshaper | ganho/harmônicas dependem do nível; assenta em poucos ms após degrau; THD de H3 igual em 110 Hz/1 k/5 k | curva estática, `|H2..H6| <= 0,005`, ganho ±0,1 dB, joelho de THD, IMD, aliasing | **sim**, em regime estável (com o mesmo oversampling) |
| **(c) não linear com memória**: compressor, limiter, gate, fita, válvula com polarização | nível dependente E ganho leva dezenas de ms a assentar após degrau; histerese; resposta depende do histórico | curva estática em regime, τ de ataque/release ±5 %, GR ±0,1 dB, THD sob GR, IMD de dois tons | **sim** se o detector/estado forem recriados; o resíduo cai em transientes |
| **(d) variante no tempo / modulado**: chorus, flanger, phaser, tremolo, vibrato, wow/flutter | bandas laterais AM/FM em tom puro (> −60 dBc) com pico de LFO; IR muda quando o clique é deslocado | taxa ±5 %, profundidade (dB AM, cents FM) ±20 %, forma, fase L-R ±10° | só se a fase do LFO for conhecida e reiniciável; senão **estatística** |
| **(e) com realimentação**: reverb, delay, eco, comb | cauda ≥ 250 ms na IR e/ou ≥ 3 ecos discretos | RT60 por oitava ±5 %, EDC (RMS ≤ 1,5 dB), tempo/feedback/filtro na malha, NED | delay determinístico: **sim**; reverb: só **EDC/RT60 e estatística** |
| **(f) estocástico**: reverb com modulação aleatória, ruído de fundo, dither, analógico com ruído | duas execuções após `reset()` com a mesma entrada diferem (> −60 dB) ou ruído com entrada muda > −80 dBFS | métricas ESTATÍSTICAS (abaixo) | **nunca**: comparar distribuições, não formas de onda |

Um plugin cai em **várias** classes (reverb Valhalla: d, e, f). O classificador devolve `sim`/`nao`/`inconclusivo` por classe e lista os protocolos. `inconclusivo` pede mais medição, não um palpite.

## 2. Como o classificador decide
Todos em regime estável (um reset, `reset=False`, aquecimento), plugin a 100 % molhado se houver parâmetro de mix.
- **T1 tons** (1 kHz, 3 níveis + repetição do 1º): ganho e H2..H6 por nível. A **repetição do 1º nível** mede a repetibilidade da medida: se ela já varia mais que 0,25 dB (modulação/ruído), a não linearidade fica **inconclusiva**, pois não se separa de modulação. Isso evitou falso "não linear" em delay e reverb modulados.
- **T2 ruído** (2 níveis + repetição): |H(f)| por 1/3 de oitava e coerência; desvio entre níveis vs repetibilidade (homogeneidade/superposição).
- **T3 degrau** (+24 dB e volta): tempo até o ganho assentar a ±0,1 dB (janelas de 5 ciclos). `> 40 ms` com não linearidade = memória (c); senão (b). Se há cauda longa, o assentamento pode ser a cauda linear: declara `inconclusivo` com nota.
- **T4 tom estável**: demodulação AM/FM (Hilbert numa banda de 0,7-1,3 f), passa-faixa 0,2-60 Hz após decimação; banda lateral > −60 dBc e pico de LFO com proeminência > 12 dB = modulado (d); < −70 dBc = não.
- **T5 cliques**: cauda (10 ms RMS acima do piso), ecos discretos (picos acima da mediana +15 dB), invariância ao deslocamento (100 ms após o clique, alinhado pelo pico; descartada se a cauda anterior > −40 dB).
- **T6 determinismo**: mesma entrada após `reset()` 2x; depois com estado livre; ruído com entrada muda. Atenção: `reset()` do pedalboard **não reinicia** LFO/semente de todos os plugins, então "estocástico" pode ser LFO periódico livre (a nota do veredito aponta isso; decidir pela proeminência do LFO).
Limiares ficam no JSON (`limiares`), editáveis em `classificar_sistema.py:limiares()`.

## 3. O que casa amostra a amostra e o que só casa em estatística
**Casa amostra a amostra (régua determinística + resíduo nulo)**: parte linear (filtros, EQ), curva estática, detectores com estado reproduzível, delay sem modulação, ganho, mix, latência. Métricas: ganho/harmônicas (régua `|ganho| <= 0,1 dB`, `|H| <= 0,005`), resposta em frequência, resíduo nulo em janelas de 100 ms (≥ 95 % ≤ −40 dB).
**Só casa em estatística (nunca pedir null)**: reverb com modulação/semente aleatória (as reflexões individuais diferem a cada execução, e o ouvido não percebe), ruído de fundo, wow/flutter aleatório, dither. Métricas, com tolerância e como medir:
| Métrica | Como | Tolerância sugerida |
|---|---|---|
| EDC de Schroeder | `captura_ir.py` | RMS do desvio ≤ 1,5 dB (0 a −30 dB) |
| RT60 por oitava (T30/T20/EDT) | idem | ±5 % |
| Pré-atraso | idem | ±2 ms ou 10 % |
| Densidade de ecos (NED, tempo até 1) | idem | ±20 % |
| Espectro da cauda por oitava | idem | ±1,5 dB |
| IACC precoce e tardio | idem | ±0,1 |
| Estatística de modulação (banda lateral dBc; taxa e profundidade só se LFO periódico) | `analisa_modulacao.py` | ±6 dB; taxa ±5 %, profundidade ±20 % |
| Ruído de fundo (nível e espectro) | entrada muda | ±6 dB |
O `teste_fechamento.py` calcula essas métricas dos dois lados e reporta o % dentro da tolerância por componente.

## 4. Combinações comuns
- Reverb: e + f (+ d): `captura_ir.py` (variando decay/size/damping), `analisa_modulacao.py`, fechamento `estatistico`.
- Delay: e (+ d, + b na malha): `analisa_delay.py`, fechamento `regua` (sem malha) e `estatistico`/`resposta`.
- Fita: b + c + d + f: `harmonicos_vs_nivel_freq.py`, degraus, `analisa_modulacao.py` (wow/flutter), espectro de ruído.
- Compressor: c: degrau/curva estática; coloração com `harmonicos_vs_nivel_freq.py` sob GR.
- EQ/filtro: a (às vezes b se saturar): `ficha_comportamento.py freq`, fechamento `resposta`.
- Synth: instrumento (MIDI), fora do classificador; `por-tipo.md` §13.

## 5. Limites do classificador
- Efeito de áudio estéreo com um barramento; **sidechain externo** não é testado (compressor com detector externo fica lacuna declarada).
- **Instrumentos MIDI** não são classificados (`n/a`); medir por nota.
- Testes são **curtos** (segundos): thresholds foram calibrados em poucos plugins; ao divergir da expectativa, medir mais (`harmonicos_vs_nivel_freq.py`, `captura_ir.py`) em vez de mudar o limiar.
- Efeito com parâmetro de mix: classificado a 100 % molhado; mixes baixos "diluem" a classe no seco. Passe `--sem-mix` para o ajuste real.
- Plugins dependentes de tempo do host (sync BPM, transport) não aparecem.
