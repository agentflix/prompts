# __PLUGIN_DISPLAY__

## Identidade
- Nome: __PLUGIN_DISPLAY__ (alvo/bundle: `__PLUGIN__`, id: `__PLUGIN_ID__`)
- Empresa: __COMPANY__ (fabricante `__MFR__`, plugin `__CODE__`)
- Bundle id: `__BUNDLE__.__PLUGIN_ID__`
- Formatos: VST3, AU, Standalone (macOS arm64, 11.0+), JUCE 8.0.16-security

## Objetivo
<!-- Em uma ou duas frases, o que o plugin faz e para quem. Ex.: "Saturação suave para voz, com um knob só." -->
- ...

## Estado
### Pronto
- Esqueleto: GAIN, TONE (tilt), MIX, BYPASS, medidor de pico, 8 presets, testes de motor e de processador.

### Falta
- ...

## Parâmetros
<!-- Esta tabela, Source/Parameters.h e a tabela no topo do script de ui/index.html têm que bater. -->
| id | tipo | faixa real | padrão (preset 0) | o que faz |
|---|---|---|---|---|
| gain | slider | -24..+24 dB | 0 | ganho de saída |
| tone | slider | -12..+12 dB | 0 | tilt em 800 Hz (>0 clareia) |
| mix | slider | 0..100 % | 100 | seco/processado |
| bypass | toggle | off/on | off | desliga com crossfade de 15 ms |

## Comandos
```bash
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_JUCE=/tmp/juce-src
cmake --build build
./build/__PLUGIN__Tests
./build/__PLUGIN__ProcTests_artefacts/Release/__PLUGIN__ProcTests
auval -v aufx __CODE__ __MFR__
pluginval --strictness-level 10 --validate-in-process ~/Library/Audio/Plug-Ins/VST3/__PLUGIN__.vst3
scripts/make-installer.sh
```

## Regras do DSP
- Nada de alocação, lock, log ou I/O na thread de áudio (`process()`).
- Parâmetros lidos por `std::atomic<float>*` guardados no construtor.
- Toda mudança de ganho é suavizada; bypass com crossfade.
- Ajustes neutros e MIX 0 % são bit a bit iguais à entrada.
- Saída sempre finita; resultado igual para qualquer tamanho de bloco.
- Latência informada ao host = latência real.
- ...

## Medições
<!-- Anote aqui cada medição/calibração: data, sinal de teste, resultado, referência. -->
| data | o que foi medido | resultado | referência |
|---|---|---|---|
| ... | ... | ... | ... |
