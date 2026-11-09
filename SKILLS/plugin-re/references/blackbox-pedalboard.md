# Black-box com pedalboard

A fonte do modelo quando o código está cifrado e o complemento que valida o que o RE estático sugere. Os scripts: `sonda_parametros.py`, `ss_template.py`, `ficha_comportamento.py`.

## Índice
1. Ambiente (venv)
2. Carregar e processar
3. Armadilhas (e o porquê)
4. Regime estável: o procedimento
5. Quantização de knobs
6. Suavização e rampas
7. Mapear taper raw→valor
8. Latência, estéreo, sidechain
9. Separar artefato de harness de comportamento do plugin
10. Instrumentos (MIDI)

## 1. Ambiente
```bash
python3 -m venv .venv && .venv/bin/pip install pedalboard numpy scipy matplotlib pillow
```
Scripts rodam com `PYTHONPATH=<skill>/scripts .venv/bin/python script.py` (um módulo local como `ss_template` precisa estar no path; **não** usar `python -I`, que o ignora). Pedalboard 0.9.x testado.

## 2. Carregar e processar
```python
from pedalboard import load_plugin
fx = load_plugin("/Library/Audio/Plug-Ins/VST3/X.vst3")    # AU: .component
P = fx.parameters                     # dict nome -> parâmetro
P["drive"].raw_value = 0.5            # NORMALIZADO 0..1
P["drive"].string_value               # texto que o plugin mostra ("6.0 dB")
P["drive"].get_raw_value_for(6.0)     # raw que produz o valor físico 6.0
y = fx(x_float32_canais_x_amostras, sr, reset=False)
```
`.range` = (min, max, passo), `.units`, `.valid_values`, `.type` (float/bool/str).

## 3. Armadilhas (aprendidas a duras penas)
| Armadilha | Efeito | Regra |
|---|---|---|
| `fx(...)` chama `reset()` por padrão | o plugin ignora parâmetros ~0,3 s após o reset; parecia "suavização de 1 s" (o X-Saturator inteiro foi medido errado assim) | `reset=False` em toda chamada; um `reset()` explícito só no começo |
| A mudança de parâmetro só vale a partir do 2º `process()` | medida "anômala" (+1,9 dB falso no Channel Strip) | nunca medir logo após setar |
| Sem aquecimento | estado (HP de DC, detectores, rampas) não assentou | aquecer ≥ 3 s com **o mesmo sinal** da medida |
| `raw_value` é normalizado | reescalar para dB/Hz trava no máximo | setar 0..1; taper por varredura (§7) |
| Knobs quantizados (0,1 dB no X-Saturator) | ajuste contínuo contra plugin em degraus gera erro falso | medir o passo (§5) e arredondar no motor |
| Parâmetro mestre mascara o do bloco (Sylenth1 `filterctl_cutoff`) | varrer o filtro "não faz nada" | varrer o mestre |
| Voz 0 = oscilador desligado | silêncio inesperado | mínimo útil ~ raw 0,125 |
| Latência não compensada | null "estoura" | medir latência com impulso e alinhar |
| Oversampling muda latência | null falha entre modos | medir no modo que vai usar |
| SR diferente | aliasing e cramping mudam | medir em 96 k e no SR de produção |
| 1 barramento só | sem sidechain externo ("does not support 4-channel output") | key externa só em DAW |
| Program-dependence | um nível não descreve | ≥ 3 níveis e ≥ 3 frequências |
| Janela de FFT | vazamento espectral | tom em bin inteiro (f·N/SR inteiro), Hann, 2º trecho |

## 4. Regime estável: o procedimento
1. `fx.reset()` **uma vez**.
2. Setar parâmetros.
3. Rodar ≥ 3 passagens de 1 s do **mesmo** sinal, `reset=False` (aquecimento).
4. Rodar a passagem de medida, `reset=False`, e medir (descartar o 1º quarto se houver DC assentando).
O `Harness.run` faz isso. Num lote de pontos, repetir o ciclo completo por ponto; custa ~1 s por ponto em plugins leves.

Quando música ou sinais longos: um reset, 1 s de preâmbulo **mudo** (pós-reset) descartado, depois `reset=False`.

## 5. Quantização de knobs
Duas camadas: (a) a **string** do parâmetro tem degraus (`sonda_parametros.py` marca `quantizado_string` e `passo_fino`); (b) o **DSP** realmente aplica o valor arredondado. (a) não prova (b): texto arredondado pode esconder valor contínuo. Prova: setar raw em pontos entre dois degraus consecutivos (ex.: 0,1 dB no X-Saturator) e ver se o ganho medido salta (degraus) ou varia suave. No X-Saturator o ganho saltava em 0,1 dB (+0,0013 dB de offset fixo), então o motor arredonda (`gainStepDb`).

## 6. Suavização e rampas
Medir em **fluxo contínuo sem reset**, blocos de 24 amostras (0,5 ms a 48 k): tom estável, muda o parâmetro num bloco, grava a envolvente do ganho nos blocos seguintes. Perguntas: a rampa é linear ou exponencial, de duração fixa ou ∝ degrau? No X-Saturator: lineares, duração fixa independente do degrau (3 ms ganho input+drive, 20 ms saída e mix, 60 ms depth/shape/harmonics). Um "overshoot" apareceu e era o *tump* de DC do caminho par lido pelo detector RMS, não overshoot da rampa. Sempre verificar se o artefato é do plugin ou do detector de medida.

## 7. Mapear taper raw→valor
Varrer raw 0..1 em 101–401 pontos lendo `string_value`; `sonda_parametros.py` grava `tapers.csv` e classifica linear/exponencial. Taper curvo: guardar a tabela (ou ajustar spline) em vez de forçar fórmula. Enum: listar todas as strings.

## 8. Latência, estéreo, sidechain
- Latência: ler `fx.reported_latency_samples` **depois de processar um bloco** (o valor só atualiza após reconfiguração, ex.: troca de oversampling); `Harness.latencia()` faz isso. NÃO medir pela posição do impulso: o pedalboard compensa a latência e dá sempre 0. Plugins com oversampling ou FIR fase-linear têm latência dependente do modo (SSL Native Bus Compressor 2: oversampling OFF/2x/4x = 0/35/41 amostras @48 kHz).
- Compensação com `reset=False`: só a **1ª** chamada após o reset sai compensada (N−L amostras úteis); as chamadas seguintes devolvem N amostras **atrasadas de L**. Medir em regime (chamada final) sem alinhar desloca fase/null em L amostras. `Harness.run` alinha: processa mais um bloco igual e recorta `[L:L+N]`.
- Estéreo: entrada mono duplicada, checar `max|L-R|`. L≠R pode ser decorrelação intencional (reverb, imager).
- Sidechain externo: não testável; documentar como lacuna.

## 9. Separar artefato de harness de comportamento do plugin
Antes de afirmar uma característica do plugin, perguntar: some se eu mudar o sinal de teste? mudar o bloco? aquecer mais? medir com outro SR? Se sim, é do harness. Regra prática: reproduzir a anomalia com um 2º método independente (ex.: domínio do tempo e FFT) antes de registrá-la.

## 10. Instrumentos (MIDI)
`load_plugin(path)` com `is_instrument`; renderizar com `fx(midi_msgs, duration, sr)` (lista de mensagens `mido`). Gotchas: parâmetros mestres, voz mínima, tempo de release (renderizar além da última nota), jitter de fase de oscilador (medir espectro de magnitude, não forma de onda). Detalhe em `por-tipo.md` (sintetizador).

## 11. Armadilhas descobertas nas medições multi-fase (v2)
- `reset()` **não reinicia** o LFO/semente de todos os plugins: duas execuções "idênticas" após reset podem diferir em reverb/delay modulado (ValhallaRoom, ValhallaDelay). Não é prova de aleatoriedade estrita; decidir pela proeminência do LFO (`classificar_sistema.py` T4/T6).
- Delay: após mudar o tempo o plugin faz glide por > 1 s; esperar (`analisa_delay.py --assenta`). O ruído de fundo precisa ser descontado das repetições fracas (pré-clique serve de medida).
- Reverb: a gravação do fim da cauda só é piso de ruído se estiver plana; com RT longo e cauda curta, subtrair o "piso" subestima o RT60 (corrigido em `medidas_comuns.rt_banda`).
- Tom puro através de efeito com `reset` recente: o plugin ignora ajustes por ~0,3 s; o preâmbulo silencioso após o reset resolve (T6).
- Distorção medida em sistema modulado/estocástico: sempre repetir o 1º ponto; se a repetição já difere, a não linearidade é inconclusiva.
- Detector por amostra: a GR em regime pode variar com o tempo (ripple/deriva do detector). Medir em regime, com janela longa (média), nunca um bloco curto.
- Release AUTO: a medida precisa de cauda ≥ 10 s; com menos, a baseline cai ~6 dB e o valor sai errado.
- CSV: `numpy.genfromtxt` renomeia colunas com `:` (e outros símbolos). Use nomes de coluna sem `:` (ex.: `razao_2_1`).
- Aliasing: um tom cujo 3º harmônico cai sobre ele mesmo (f0 submúltiplo exato do SR, ex.: f0 = SR/4: 3·f0 reflete em SR−3·f0 = f0) esconde o aliasing. Escolher f0 que não seja submúltiplo exato.
- Valores raw de enum: com N opções o raw do índice i é i/(N−1) (ex.: modo 4 de 11 → 0,4).
