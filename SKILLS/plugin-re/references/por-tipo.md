# Mapa por tipo de plugin: o que medir, como e qual a métrica de fidelidade

Além da ficha padrão (`ficha-comportamento.md`) e da classificação (`classes-de-sistema.md`). Cada seção usa o mesmo formato: **o que medir / como / métrica de fidelidade**, depois armadilhas. Tudo em regime estável (`blackbox-pedalboard.md`). O tipo escolhe os protocolos; a CLASSE do sistema diz se a comparação final é amostra a amostra ou estatística.

## Índice
1. Saturador / distorção
2. EQ
3. Compressor
4. Limiter
5. Gate / expansor
6. Filtro
7. Reverb
8. Delay
9. Fita
10. Modulação (chorus, flanger, phaser, tremolo, vibrato)
11. Imager / utilitário
12. Medidor
13. Sintetizador
14. Channel strip / bus (composto)

## 1. Saturador / distorção
| Medir | Como | Métrica de fidelidade |
|---|---|---|
| Curva de transferência | tom 1 kHz, −60…0 dBFS: ganho e H2..H6 (`harmonicos_vs_nivel_freq.py`); forma no tempo com tom grande (clip ±1, tanh(kx), x−x³/3, assimétrico) | ganho ±0,1 dB, `|H|` ≤ 0,005, resíduo no tempo ~1e-3 |
| Joelho de THD | nível de 1 % e 5 % de THD | ±1,5 dB no joelho |
| Pares vs ímpares, DC | H2 com DC = assimetria; medir DC | par/ímpar ±20 % |
| Memória | THD de H3 em 110 Hz/1 k/5 k: igual = sem memória (`memoryless_provavel`) | espalhamento < 3 dB |
| IMD | SMPTE 60 Hz+7 kHz, CCIF 19+20 kHz (`--imd`) | ±3 dB nas bandas laterais |
| Aliasing | tom 7 kHz forte a 48 k vs 96 k; latência por modo de oversampling | ±3 dB de energia inarmônica |
| Ordem e mix | input −12/drive +12 vs input 0/drive 0; null do mix 0 vs bypass | ganho ±0,1 dB |
Armadilha: knobs quantizados (0,1 dB no X-Saturator); o HP de DC (~5 Hz) altera H em graves.

## 2. EQ
| Medir | Como | Métrica |
|---|---|---|
| Magnitude e fase por banda | ESS/ruído; sino: frequência central real, ganho vs knob, **Q vs ganho**, reciprocidade boost/corte; shelf: inclinação e platô | `|erro|` ≤ 0,1 dB, fase ±5° |
| Cramping | ganho a 18 kHz em 44,1/48/96 k | ±0,2 dB |
| Fase | mínima (cai com a magnitude) vs linear (latência, pré-ring simétrico) | IR: resíduo nulo |
| Coloração | THD com +12 dB em 3 níveis; null do EQ plano vs bypass (< −60 dB num EQ limpo) | `|H|` ≤ 0,005 |
| Interação entre bandas | duas bandas vizinhas: soma em dB aditiva? | ±0,1 dB |
| Quantização | passos de frequência/ganho | exato |
Tabelas: `ChannelStripEQCurveData` é LUT; guardar a tabela medida, não forçar fórmula. Fechamento: `teste_fechamento.py --componentes resposta,regua,musica` (classe a: casa amostra a amostra).

## 3. Compressor
| Medir | Como | Métrica |
|---|---|---|
| Curva estática | tom 1 kHz em degraus, ler a saída em regime: threshold, ratio efetiva, joelho | `|GR|` ≤ 0,1 dB |
| Tempos | degrau de nível, 63 % de ataque e release; auto-release com dois estágios | ±5 % |
| Detector | pico vs RMS (burst curto vs longo, mesma energia); HPF do sidechain (fc, ordem); stereo link; feed-forward/back | categoria + fc ±5 % |
| Coloração | THD vs nível com GR=0 e GR≠0 (`harmonicos_vs_nivel_freq.py`) | ±1,5 dB |
| Makeup/mix | ganho automático, paralelo | ±0,1 dB |
Armadilha: sidechain externo só em DAW (lacuna declarada). GR em dB lê-se de saída/entrada em regime. Classe c: o fechamento com música pega erros de transiente.

## 4. Limiter
| Medir | Como | Métrica |
|---|---|---|
| Teto / true-peak | tom de alta frequência com inter-sample peaks; oversampling | ±0,1 dB |
| Lookahead | latência por impulso/degrau | 0 amostras de erro |
| Release | degrau; program-dependent | ±5 % |
| Saturação do estágio | THD próximo ao teto | ±1,5 dB |

## 5. Gate / expansor
| Medir | Como | Métrica |
|---|---|---|
| Curva abaixo do threshold (ratio, range) | degraus de nível | ±0,1 dB |
| Histerese | threshold de abertura ≠ fechamento | ±0,5 dB |
| Ataque/hold/release | degrau | ±5 % |
| Lookahead e filtro de sidechain | impulso; resposta do SC | latência exata |

## 6. Filtro
| Medir | Como | Métrica |
|---|---|---|
| Magnitude e fase | ESS/impulso | ±0,1 dB |
| fc real vs knob, slope | varrer raw (exp?), ≥ 1 década acima | ±3 % de fc, ±7 % de slope |
| Ressonância e auto-oscilação | pico, Q, tom por ressonância | ±5 % |
| Saturação interna | THD vs nível com ressonância alta | ±1,5 dB |
| Transientes, key-tracking (synth) | clique; nota | ±5 % |

## 7. Reverb
Classe típica: e + f (+ d). A comparação final é **estatística** (`classes-de-sistema.md` §3).
| Medir | Como | Métrica de fidelidade |
|---|---|---|
| **Resposta ao impulso** | `captura_ir.py`: varredura senoidal exponencial (Farina) estéreo, deconvolução, IR linear; **em vários ajustes** (`--varre decay --valores ...`, depois size, damping, tipo/algoritmo); método `--metodo impulso` para conferir | IR por ajuste guardada (wav) |
| **RT60 por oitava** (125 Hz-8 kHz) | curva de decaimento de energia de Schroeder (integral reversa de h², correção do piso de ruído); T30 (−5 a −35 dB), T20, EDT, com **faixa dinâmica** reportada | ±5 % por banda; RT60 deve acompanhar o knob de decay |
| **Pré-atraso** | primeiro pico da parte reverberante (após o direto, se houver) | ±2 ms |
| **Early reflections** | picos isolados 0-80 ms: atrasos e níveis (`acha_ecos` sobre a IR), padrão por tipo de sala | ±2 ms, ±3 dB |
| **Densidade de ecos** | NED (Abel-Huang, janela 20 ms): tempo até NED=1 (mixing time) e curva | ±20 % |
| **Damping/filtros por banda** | RT60 por oitava (razão grave/agudo), espectro da cauda (≥ 200 ms), hicut/locut: fc e slope pela cauda | RT60 ±5 %; espectro ±1,5 dB |
| **Largura estéreo** | IACC precoce (0-80 ms) e tardio por banda; entrada só em L (`--so-L`) revela cross-feed | ±0,1 |
| **Modulação** | taxa/profundidade: `analisa_modulacao.py` com tom; variância da IR: `captura_ir.py --repete 2` (correlação da IR precoce) | banda lateral ±6 dB; taxa só se LFO periódico |
| **Estrutura do algoritmo** | FDN: nº de linhas ≈ densidade crescente e modos na cauda (picos espectrais da cauda; ecos nos tempos primos entre si); Schroeder: pente (periodicidade de ecos iniciais) + all-pass; Dattorro: tanque com 2 laços e saída por taps. Evidência: periodicidade da autocorrelação da IR em 0-100 ms, picos espectrais da cauda, strings/RTTI (`allpass`, `fdn`) | inferência (estático + BB concordam = confirmado) |
| **Níveis e não linearidade** | IR a −12 e −30 dB: igual (reverb linear) ou comprime/satura | ±0,25 dB |
Armadilhas: cauda longa exige gravar bem além do RT60 (e aquecer); `reset()` mata a cauda; entre ajustes, silêncio de duração ≥ cauda antes de medir; mix 100 % (o direto atrapalha a EDC); plugin que **não repete** a IR é modulado/aleatório: não pedir null. Fechamento: `teste_fechamento.py --componentes estatistico` (EDC, RT60 por banda, NED, espectro, IACC, modulação, ruído).

## 8. Delay
Classe: e (+ d pela modulação, + b se a malha satura). Determinístico sem modulação: casa amostra a amostra.
| Medir | Como | Métrica |
|---|---|---|
| **Tempo** | `analisa_delay.py`: clique, mediana dos espaços entre ecos (picos de envelope RMS 1 ms com interpolação parabólica); varrer o knob (`--varre`) para o taper; em sync, varrer notas e BPM | ±1 ms; jitter reportado |
| **Latência fixa** | 1º eco menos T (sem direto) | exata |
| **Feedback** | razão de energia entre ecos consecutivos (ruído descontado) → ganho linear por repetição | ±0,5 dB |
| **Filtros na malha** | razão espectral eco k+1 / eco k por 1/3 de oitava: fc (−3 dB), inclinação dB/oit; "escurece a cada repetição?" | ±1 dB/oit, fc ±10 % |
| **Saturação/compressão na malha** | feedback a dois níveis de clique (−12 e −30 dBFS): difere? | indício se > 1 dB |
| **Ping-pong/estéreo** | entrada só em L (`--entrada L`): energia por eco alterna entre L e R? spread/largura | alternância e razão |
| **Sync** | tempo vs nota/BPM (precisa de transporte: pedalboard sem BPM de host; lacuna declarada) | ±1 ms |
| **Ducking** | tom contínuo + clique: feedback cai enquanto o sinal entra? degrau de nível na entrada e envelope do eco (protocolo manual) | τ ±10 % |
| **Modulação do tempo** | jitter dos espaços e deriva; tom estável (`analisa_modulacao.py`) | ±20 % |
| **Glide ao mudar o tempo** | mudar o knob em fluxo contínuo e medir frequência instantânea (Hilbert) de um tom: crossfade (sem glide) vs pitch-shift | qualitativa + duração ±10 % |
Armadilhas: delay < 20 ms vira comb/flanger (usar §10); após mudança de tempo o plugin pode levar > 1 s para assentar (`--assenta`); o `reset()` limpa a malha entre medições; ruído de fundo precisa ser descontado das repetições fracas.

## 9. Fita
Classe: b + c + d + f. Maior parte do "caráter" vem de histerese, compressão suave, curva de resposta por velocidade e flutuação.
| Medir | Como | Métrica |
|---|---|---|
| **Histerese / THD vs frequência e nível** | `harmonicos_vs_nivel_freq.py` (grade nível × frequência); na fita THD sobe no grave (satura por fluxo, HD ~ 1/f²); formato e fase das harmônicas por tom grande no tempo (laço de histerese: saída vs entrada) | ±1,5 dB por H; forma do laço |
| **IMD de dois tons** | `--imd` (SMPTE e CCIF) | ±3 dB |
| **Compressão por degrau** | degrau de +24 dB (`classificar_sistema.py` T3): tempo de assentamento e ganho final alto vs baixo | τ ±10 %, ganho ±0,1 dB |
| **Head bump e curvas por velocidade** | magnitude por ruído/ESS em cada velocidade (7,5/15/30 ips): bump em 40-100 Hz, roll-off de agudos | ±0,5 dB por banda |
| **Wow/flutter** | tom alto estável (3-10 kHz, melhor sensibilidade FM) → demodulação FM (`analisa_modulacao.py --freq 3150,8000`): taxa, desvio em cents, espectro do desvio (wow < 4 Hz, flutter 4-20+ Hz), % ponderado | cents ±20 %; espectro da modulação ±6 dB |
| **Espectro do ruído** | entrada muda, `welch` em 1/3 de oitava: hiss (+ hum 50/60 Hz e harmônicas), nível rms | ±3 dB por banda, ±6 dB total |
| **Bias / tipo de fita** | varrer knob de bias/tape type em tom e ruído: muda H2/H3, HF, ruído e head bump | tabela por tipo |
| **Estéreo/azimute** | L≠R: diferença de fase em HF, crosstalk | ±1 dB, ±5° |
Armadilhas: wow/flutter aleatório não casa amostra a amostra (estatística do desvio de frequência); ruído de fundo precisa de reset antes (cauda); saturação por fluxo muda com a frequência: nunca generalizar de 1 kHz.

## 10. Modulação (chorus, flanger, phaser, tremolo, vibrato)
Classe: d (+ e se há feedback).
| Medir | Como | Métrica |
|---|---|---|
| **LFO: taxa** | `analisa_modulacao.py`: tom estável → AM (envelope) e FM (fase) por Hilbert, pico espectral com interpolação; varrer o knob de taxa e reportar a razão `taxa medida / knob` (pode ser múltiplo fixo: vozes em quadratura) | ±5 % |
| **Profundidade** | AM em dB pico a pico, FM em cents de pico; para chorus em ms (cents → atraso) | ±20 % |
| **Forma** | razão dos harmônicos 2 e 3 do LFO: senoidal, triangular (h3 ≈ 1/9), quadrada (h3 ≈ 1/3), dente de serra (h2 ≈ 1/2), aleatória (proeminência < 12 dB) | categoria |
| **Fase estéreo** | fase L-R no pico do espectro de modulação (AM e FM): 90° = quadratura | ±10° |
| **Feedback e mix** | IR / varredura com feedback em 0 e alto; mix 0/50/100 % | ±1 dB |
| **Sync** | taxa vs BPM/nota (precisa de transporte) | lacuna declarada |
| **Dependência de frequência** | `--freq 250,1000,4000`: flanger/phaser têm notches que cruzam o tom (AM profundo, fase salta); medir a profundidade por frequência | ver picos em `picos_espectro_modulacao` |
Armadilhas: LFO < 0,3 Hz exige janela longa (`--dur`); LFO de fase livre não reinicia no `reset()`; modos que deslocam pitch (SpaceModulator "Up") tiram o tom da banda: escolher outro modo ou ajustar `--freq`; delay modulado de verdade tem notches (usar `captura_ir.py` para a comb).

## 11. Imager / utilitário
| Medir | Como | Métrica |
|---|---|---|
| Largura | entrada L≠R; correlação L/R e M/S vs knob; mono-compatibilidade (L+R com largura 200 %) | ±0,5 dB, ±0,05 |
| Pan law | −3/−4,5/−6 dB no centro | ±0,1 dB |
| Inversão de fase, ganho, mute/solo | tom | exato |
| Crossover de bandas | frequências de corte, fase | ±5 % |
| Utilitário | precisão do ganho (passo), DC, latência | ±0,05 dB |

## 12. Medidor
Balística (VU: 300 ms; PPM; RMS; LUFS 400 ms/3 s), calibração (tom −18 dBFS = qual leitura), true-peak, correlação, espectro (FFT, janela, suavização). O medidor não altera o áudio: null vs entrada < −100 dB. Leituras vêm de parâmetros de saída (pedalboard) ou áudio. Métrica: ±0,1 dB na calibração, tempos ±5 %.

## 13. Sintetizador
| Medir | Como | Métrica |
|---|---|---|
| **Osciladores** | cada forma de onda e nota (C2, C4, C6), 2 s: rolloff harmônico (saw ~ 1/n), H2 vs ideal, **aliasing** em notas agudas, PWM, sync; unison: nº e posição de picos (detune em cent), spread estéreo | ±1,5 dB, ±1 cent |
| **Filtros** | cutoff vs raw (exp?), slope 12/24, ressonância, auto-oscilação, saturação (drive), key-tracking; o **mestre** pode mascarar o bloco | ±3 %, slope ±7 % |
| **Envelopes** | ataque/decay/release por degrau (exp/linear); tempo vs raw | ±10 % |
| **LFO** | taxa vs raw, formas, sync, retrigger | ±5 % |
| **Matriz de modulação** | fonte → destino → profundidade, medida no efeito em cutoff/pitch | ±10 % |
| **Efeitos internos** | medir como §7/§8/§10 com nota sustentada | por tipo |
| **Voz** | nº de vozes, voice stealing, portamento | exato |
| **Presets** | decodificar `.fxb/.fxp/.vstpreset` e estatísticas por categoria (`ui-e-presets.md`); "program change" pode não restaurar valores | formato validado |
Armadilhas: parâmetros são raw 0..1; voz = 0 desliga o oscilador (mínimo útil raw ≈ 0,125); jitter de fase entre notas (comparar magnitude espectral); release longo exige render além da nota; velocity e modwheel fixos. Scripts de efeito não cobrem instrumento: ver `blackbox-pedalboard.md` §10 e o harness `_re-corpus/sylenth1/measurements/measure_syl.py`. **Lacuna da skill**: instrumentos MIDI não têm classificador nem fechamento automáticos.

## 14. Channel strip / bus (composto)
Medir cada bloco isolado (desligar os outros), depois a **ordem do sinal** (EQ antes/depois do comp; ordem dos filtros) com ajustes extremos e ver o efeito cruzado. Modos de console (Harrison, Brown, Black) e coloração de pré-amp (MicPre): uma ficha por modo. Classe: composta (a + b + c): classificar com cada bloco ligado sozinho.
