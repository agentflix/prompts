# snaphost: captura do display de um plugin sem Gravação de Tela

`createComponentSnapshot` não pega OpenGL/Metal (sai preto). `screencapture` e `CGWindowListCreateImage` de
**outro** processo exigem Gravação de Tela. A janela do **próprio** processo não exige: o SnapHost hospeda o
plugin, então captura a sua janela (com GL/Metal) via `CGWindowListCreateImage` carregado por `dlsym`
(a API está marcada como obsoleta no SDK, mas o símbolo existe).

```
cmake -B build -DJUCE_DIR=/caminho/JUCE && cmake --build build -j8
./run.sh <saida/> <cenario> [param=texto ...] [duration=s] [snapms=ms] [fs=Hz]
PLUGIN=/caminho/Outro.vst3 ./run.sh ...
```

Cenários: `burst` (tom 3 s, silêncio), `onset` (silêncio, tom a partir de 1 s), `tone`, `noise`, `sweep`, `ladder`
(tons em 20…40 kHz para calibrar o eixo X), `stepdown`.

## Armadilhas

- Os parâmetros são aplicados 0,8 s depois do editor aparecer, **forçando uma mudança** (`1-v`, depois `v`): o editor do
  Spectrum 2 só sincroniza os knobs em eventos de mudança.
- O trial do Spectrum 2 cobre x 350–670 do gráfico. Meça colunas fora dele (1 kHz fica em x≈680).
- Capture 40 ms por quadro para medir queda/ataque; o PNG custa ~25 ms.
- `analyze.py`: geometria do Spectrum 2 (1,333 px/dB; −12 dB em y=91; curva = cor saturada). Ajuste para outro plugin.

## Resultados (Spectrum 2, 48 kHz, tom −20 dBFS a 1 kHz)

AVERAGE N → ataque EMA em potência (tau 0,25·N s), queda 80/N dB/s; PEAK DECAY N → 3,2/N dB por atualização (8 = trava); eixo fmin–Nyquist (7,35 Hz base 10; 12,2 Hz base 2);
GRAM com tempo na vertical (~70 px/s). Veja o README da raiz.
