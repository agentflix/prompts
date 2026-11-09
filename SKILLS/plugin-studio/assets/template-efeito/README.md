# __PLUGIN_DISPLAY__

Efeito de áudio de __COMPANY__ (VST3, AU e Standalone para macOS), feito com JUCE 8.

Controles: **GAIN** (-24 a +24 dB), **TONE** (equalizador tilt, -12 a +12 dB), **MIX** (0 a 100 %) e **BYPASS**.
A interface fica em `ui/index.html` (HTML, CSS e JS puros) e também abre direto no navegador, com o medidor simulado.

## Compilar e testar

```bash
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release        # opcional: -DFETCHCONTENT_SOURCE_DIR_JUCE=/caminho/do/JUCE
cmake --build build
./build/__PLUGIN__Tests                       # motor de DSP
./build/__PLUGIN__ProcTests_artefacts/Release/__PLUGIN__ProcTests            # processador e ponte com a UI
```

A compilação assina (ad-hoc) e copia o plugin para `~/Library/Audio/Plug-Ins/VST3` e `~/Library/Audio/Plug-Ins/Components`.

## Validar

```bash
auval -v aufx __CODE__ __MFR__
pluginval --strictness-level 10 --validate-in-process ~/Library/Audio/Plug-Ins/VST3/__PLUGIN__.vst3
```

## Instalador

```bash
scripts/make-installer.sh          # gera dist/__PLUGIN__-<versão>.pkg
```

## Onde mexer

| O quê | Arquivo |
|---|---|
| Som (DSP) | `Source/dsp/Engine.h` |
| Parâmetros | `Source/Parameters.h` + tabela e `makeParam` em `ui/index.html` |
| Interface | `ui/index.html` (cor de destaque: `--accent`) |
| Identidade, versão | topo do `CMakeLists.txt` |
