# Modelar e validar: ajuste, hold-out, régua, música, motor

Modelo sem validação é opinião. O padrão (do X-Saturator, mais rigoroso que o de qualquer outro doc): ajustar em treino, validar em amostra aleatória **nova**, medir % dentro de uma régua explícita, repetir com música, registrar os limites que sobram.

## Índice
1. Fluxo
2. Ajuste (treino)
3. Régua
4. Hold-out aleatório
5. Música
6. Motor header-only em dsp-core e testes
7. Registro de limites
8. Armadilhas do ajuste

## 1. Fluxo
1. Medir grade de treino (`ss_template.py`/`ficha_comportamento.py`), guardar CSV de verdade (contrato abaixo).
2. Propor modelo com **fórmula checável** (poucos parâmetros, física plausível). Ajustar (`scipy.optimize`, mínimos quadrados) sobre a grade. Guardar os coeficientes e o script (`fit_*.py`).
3. Implementar no motor (`dsp-core/<Nome>Engine.h`), reproduzir a grade nos testes C++ (`tests/<Nome>Tests.cpp`) contra o CSV.
4. **Hold-out**: gerar amostra aleatória nova (`validar_modelo.py --gerar`), medir no **plugin real**, comparar com o motor (`--verdade ... --exe`).
5. **Música**: `teste_musica.py`.
6. Listar o que ficou fora da régua, o que não foi medido, e escrever o dossiê (`esqueleto_doc.md`).

## 2. Ajuste (treino)
- Separar o problema: núcleo (curva de transferência), pesos (parâmetros), dinâmica (rampas), I/O. Ajustar um de cada vez com os outros fixos.
- Preferir **domínio do tempo** (forma de onda para tom grande) para curvas não lineares: mostra assimetria, degraus, penhascos que a FFT mistura. O modelo do caminho ímpar do X-Saturator saiu de curvas no tempo com resíduo 1e-4.
- Medir o que o modelo ignora: DC, ganho de pequeno sinal, offset de quantização (+0,0013 dB nos knobs do X-Saturator).
- Evitar polinômios de grau alto sem física: passam no treino e falham no hold-out. Grau 5 foi necessário para um peso (w(h)), e só se justificou porque o hold-out melhorou (94 → 100 %).

## 3. Régua
Explícita e igual do início ao fim. Padrão: `|erro de ganho| <= 0,1 dB` e `|erro de cada harmônica relativa a H1| <= 0,005` (absoluto na razão). Reportar % de pontos dentro, p50/p90/máx de cada. Outras réguas por tipo: EQ `|erro de magnitude| <= 0,1 dB` por banda e fase; compressor `|erro de GR| <= 0,1 dB` em regime e τ ± 5 %; reverb RT60 ± 5 % por banda. A régua deve refletir **o que o ouvido nota**, não o que é fácil.

## 4. Hold-out aleatório
- Semente que o ajuste nunca viu (ex.: 31337), sorteio uniforme entre os **mesmos limites** dos parâmetros: `validar_modelo.py --gerar 4000 --limites lim.json --seed 31337 --saida rnd.csv --medir-plugin <plugin>`. Mede o plugin real no ponto (tempo: ~1 s/ponto; rodar em lote e em horário calmo, o host de plugins é compartilhado).
- Grade regular esconde sobreajuste; a aleatória revela cantos (ex.: headroom ligado com depth > 0,9 e ganho alto).
- Se um grupo discreto existe (bool, modo), gerar por grupo e reportar `grupo` no CSV.
- Quantizar parâmetros como o plugin faz (passo medido) antes de alimentar o motor, senão o erro é do harness.

### Contrato do CSV de verdade (`validar_modelo.py`)
`param1,param2,...,amp_db,gain_db,h2,h3,h4,h5,h6[,grupo]`: params em raw 0..1, `amp_db` dBFS do tom, `gain_db` ganho do fundamental, `h*` razões lineares relativas a H1. Motor por `--exe` em lote (CSV em stdin com params+amp_db, CSV em stdout `gain_db,h2,...`) ou `--py arq.py:func`.

## 5. Música
`teste_musica.py <plugin> <audio> --exe "<motor> {in} {out} ..." --settings s.json`: trechos de 10–20 s de 3 faixas diferentes (grave pesado, voz, percussão), ≥ 10 ajustes por plugin incluindo os extremos. Critério do X-Saturator: resíduo nulo ≤ −40 dB em ≥ 95 % das janelas de 100 ms (alcançou 100 % em 16/16 ajustes, −53…−146 dB). Aprendizado: música achou o erro do mix (seco passava pelo HP de DC no motor, não no plugin) que os tons não mostravam. Janelas com plugin < −60 dBFS são ignoradas (resíduo relativo explode em silêncio).

## 5b. Fechamento por classe (v2)
`teste_fechamento.py` generaliza o hold-out e a música: **régua** determinística (ganho/harmônicas), **resposta** (|H| por banda), **música** (resíduo nulo, só para partes determinísticas) e **estatístico** (EDC, RT60 por banda, pré-atraso, NED, espectro da cauda, IACC, modulação, ruído) para o que não casa amostra a amostra. Critério: ≥ 95 % por componente. Quando a classe é estocástica, **nunca** pedir null: ver `classes-de-sistema.md` §3. Cada componente é uma fase (FEC) no ledger (`ledger-confianca.md`); o fechamento só promove a "validado" se usar semente/pontos que o ajuste não viu.

## 6. Motor header-only em dsp-core e testes
- Local: `dsp-core/<Nome>Engine.h`, namespace `afx`, header-only, sem JUCE, sem alocação no `process`. Plugins incluem por **shim** fino; corrigir o som no `dsp-core`, nunca nos shims (`dsp-core-shared` na memória).
- Testes: `tests/<Nome>Tests.cpp` (checagens contra CSVs `tests/<nome>_truth*.csv`) e uma régua em C++ (`tests/<Nome>Ruler.cpp`: % dentro da régua por grupo). Build: `clang++ -std=c++17 -O2 -I. tests/<Nome>Tests.cpp -o /tmp/t && /tmp/t`. Depois, rodar os testes dos **consumidores** do motor.
- Parâmetros do motor com os mesmos limites e passos do plugin; opções extras do nosso lado (oversampling) ficam rotuladas `[Escolha de projeto]`.

## 7. Registro de limites
No dossiê, §8 Lacunas: faixas onde o erro passa da régua (com % de pontos), o que não foi medido (sidechain, SR extremos, modos), fenômenos conhecidos sem modelo. Declarar o que **não** foi medido vale tanto quanto o resultado.

## 8. Armadilhas do ajuste
- Medida contaminada pelo reset: refazer antes de ajustar.
- Mesmo conjunto para ajustar e validar.
- Régua em dB de uma harmônica minúscula: use erro absoluto na razão, ou dB só acima de um piso.
- Regime estável apenas: transientes e rampas são um modelo separado.
- Ajustar ruído de medida (3 casas decimais de THD de −100 dB).
