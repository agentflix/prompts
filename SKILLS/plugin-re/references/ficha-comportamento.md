# Ficha de comportamento padrão

Campos comparáveis entre plugins. O objetivo é um esqueleto numérico de como plugins bons se comportam (e onde colorem), não só descrever cada um. `scripts/ficha_comportamento.py` cobre os campos automatizáveis; o resto vai à mão com `ss_template.py`.

## Índice
1. Campos
2. Como medir cada um
3. Formato de saída
4. Comparar entre plugins

## 1. Campos
| # | Campo | Pergunta |
|---|---|---|
| 1 | Ganho unitário no neutro | com tudo no padrão/transparente, entrada = saída? |
| 2 | Faixa e taper de I/O | input/output trim: faixa em dB, linear em dB ou curvo, passo |
| 3 | Coloração no neutro | null contra bypass e contra a entrada |
| 4 | THD/harmônicos vs nível | H2..H6 em ≥ 3 ajustes (suave/médio/forte) e ≥ 5 níveis |
| 5 | Pares vs ímpares | razão (H2+H4)/(H3+H5); quem domina |
| 6 | Dependência de frequência | memoryless? THD muda em 110 Hz/1 k/5 k? |
| 7 | Aliasing/oversampling | % de energia inarmônica com tom agudo forte; modos 1x/2x/4x |
| 8 | Latência | impulso; por modo |
| 9 | Suavização/rampas | tipo (linear/exp), duração por parâmetro |
| 10 | Quantização | passo dos knobs, no texto e no DSP |
| 11 | Bypass | transparente? ramp/fade? latência mantida? |
| 12 | Estéreo / mono | L=R com entrada mono? processa M/S, link? |
| 13 | DC | offset na saída; HP de DC (fc) |
| 14 | Ruído de fundo | RMS com entrada muda |
| 15 | Dependência de SR | aliasing, cramping de EQ, tempos de envelope em 44,1/48/96 k |
| 16 | Nível/headroom | pico onde clipa/limita; escala interna (ex.: 6 dB headroom) |
| 17 | Mix/paralelo | dry/wet linear? seco passa por HP/latência? |
| 18 | Ordem dos blocos | o que vem antes do quê (ganhos antes/depois do não linear) |

## 2. Como medir cada um
1. Ganho unitário: tom 1 kHz −12 dBFS, padrão e "neutro real" (zerar o que colore). Padrão de fábrica pode já colorir (ex.: depth 50 %); por isso `--settings` aceita `neutro_real`.
2. I/O: `sonda_parametros.py` dá faixa/taper; confirmar com tom: ganho medido vs valor do knob (linear em dB? desvio de pequeno sinal?).
3. Coloração: ruído branco −20 dBRMS, null contra bypass (o parâmetro `bypass` do plugin, não do host) e contra entrada. −60 dB ≈ transparente; −40 dB audível em fones.
4–5. `meas()` em tom 1 kHz, níveis −40…0 dBFS; THD = raiz da soma dos quadrados de H2..H6. Observar o **joelho** (nível em que a THD passa de 1 % e 5 %).
6. Repetir 4 em 110/1k/5k Hz. THD igual = memoryless; THD cresce com f = filtro dentro do laço; cai = pré/pós-ênfase.
7. Tom ~7 kHz, −3 dBFS, ajuste forte, SR 48 k: energia fora de k·f. Repetir a 96 k e comparar com 1x do plugin (se alias cai muito, há oversampling interno ou o alias do 48 k era do filtro).
8. Impulso (`ficha_comportamento.py latencia`) por modo de qualidade.
9. Degrau de parâmetro em fluxo contínuo (`blackbox-pedalboard.md` §6).
10. Varrer raw entre dois degraus e medir ganho (§5 do mesmo arquivo).
11. Bypass: comparar saída com bypass ligado vs entrada; medir fade por degrau no bypass.
12. Entrada mono duplicada; depois L≠R para ver link de detector.
13. Entrada muda e tom com offset DC; fc do HP por resposta a degrau.
14. Entrada muda 4 s; RMS dBFS.
15. Repetir 4/7 e o EQ a 44,1/48/96 k.
16. Tom crescente até pico máximo; ver tapete.
17. Mix 0/50/100 %: seco = x·g? seco passa por HP? (No X-Saturator só o molhado passa pelo HP de 4,8 Hz.)
18. Ganhos grandes de input e output: se output grande muda THD, a ordem é "não linear depois"; se input muda, "antes".

## 3. Formato de saída
`ficha.json` (blocos: neutro, thd por ajuste, freq por ajuste, latência, estéreo, aliasing, ruído/DC; blocos sem aplicação viram `{"n/a": motivo}`) e `ficha.md` com tabelas. No dossiê, cada número cita o comando (`ficha_comportamento.py ... --settings s.json`) e o arquivo de saída.

## 4. Comparar entre plugins
Montar uma tabela por tipo com as colunas acima (um plugin por linha) em `plugins-kb/esqueleto-<tipo>.md`. O que o esqueleto responde: quanto de THD um saturador "bom" faz em −12 dBFS no ajuste médio? o neutro é transparente (< −60 dB de null)? quantos ms de rampa? As faixas típicas só valem com ≥ 3 plugins do mesmo tipo medidos pelo mesmo harness.
