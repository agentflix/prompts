# Como construímos um plugin

The bundled template `assets/template-efeito/` is a complete, tested effect (GAIN, TONE, MIX, BYPASS, meter, presets) that builds VST3/AU/Standalone, passes its tests, `auval` and `pluginval`. Start every project from it and change it; don't write the skeleton from scratch.

## Contents
1. Creating the project
2. Layout and build
3. Interface (moderna and photoreal)
4. The WebView bridge
5. Parameters, presets, state
6. DSP engine rules
7. Extensions: instrument, sidechain, oversampling
8. Pitfalls that cost real rounds
9. iPlug2 — framework alternativo
10. Gain staging e saturação controlada
11. Interface fotorrealista em bitmaps (editor nativo)

## 1. Creating the project

```
bash <skill>/scripts/novo-plugin.sh "$PROJETOS/<pasta>" <NOME> <CODIGO4> "<Empresa>" <FABRICANTE4> <bundle-prefix>
# ex.: novo-plugin.sh ~/Plugins/ecodor ECODOR Ecdr "Sonora Labs" Snrl com.sonoralabs
```
It validates the codes, refuses to overwrite, copies the template and replaces the placeholders (`__PLUGIN__`, `__PLUGIN_ID__`, `__CODE__`, `__COMPANY__`, `__MFR__`, `__BUNDLE__`). Build once untouched to prove the toolchain works before changing anything.

## 2. Layout and build

```
<pasta>/
  CLAUDE.md  README.md  .gitignore
  ui/index.html                     # the whole interface: HTML/CSS/JS in one file, no build step
  CMakeLists.txt                    # identity variables at the top (PLUGIN_NAME, PLUGIN_ID, codes, company, bundle, version)
  Source/Parameters.h  PluginProcessor.*  PluginEditor.*  dsp/Engine.h     # C++ namespace `fx`
  Tests/EngineTests.cpp  ProcessorTests.cpp
  scripts/make-installer.sh
  docs/ (AUDICAO.md, measurements)  tools/ (calibration scripts)  audition/ (WAVs, gitignored)
```

- JUCE `8.0.16-security` via CMake FetchContent; locally `-DFETCHCONTENT_SOURCE_DIR_JUCE=/tmp/juce-src` avoids re-downloading.
- C++20, macOS 11+, arm64 (universal is an option). Formats VST3, AU, Standalone.
- The JUCE JavaScript library (`modules/juce_gui_extra/native/javascript/index.js` and `check_native_interop.js`) is taken from the JUCE source at configure time and embedded with `ui/index.html`; configure stops with an error if a future JUCE moves them.
- POST_BUILD ad-hoc signs and copies the plugin into `~/Library/Audio/Plug-Ins/{VST3,Components}` (macOS on Apple Silicon refuses unsigned binaries).
- Build: `cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_JUCE=/tmp/juce-src`, then `cmake --build build`. Rebuild the plugin after every UI change (the HTML is binary data).
- Never leave `PLUGIN_CODE` unset (JUCE's default is random per configure and breaks saved sessions).

## 3. Interface

**Moderna (template).** Dark panel, rotary knobs (vertical drag, Shift = fine, double-click = reset, wheel), toggles, peak meter, preset bar (◀ name ▶, ` *` when modified), company signature. Colours come from CSS variables: change `--accent` and the signature for the user's brand. Add controls by copying an existing knob block and adding its `makeParam` line and table row. The design size is fixed in CSS and the C++ editor keeps the same aspect ratio; change both together.

**Photoreal (vintage or clone).** Designed with the `realistic-hardware-ui` skill (real-time Three.js, page = only the panel, `window.ui` bridge with `get/set/onChange/setMeter/state`). Wired end to end once (a tube saturator cloned from a photo, 2026); still plan extra visual rounds. What worked:
- Vite + `vite-plugin-singlefile` builds `ui/index.html` with `three` from npm and the fonts as local woff2 files inlined (`assetsInlineLimit: Infinity`, `base: './'`, `emptyOutDir: false` to keep `ui/js/juce/`). Source split: `src/panel.js` (scene, all positions in photo pixels in one `POS` table), `src/bridge.js` (parameter table comment, `makeParam`, presets, `matches()`), `src/main.js` (interaction, display, menu, manual, `window.ui`). A Vite `transformIndexHtml` hook appends the raw `bridge.js` as `<script type="text/plain" id="fonte-bridge">` so the C++ tests can parse it from the minified page.
- The approved preset strip lives inside the 3D scene (dark bar under the panel): small knobs, ◀ ▶ buttons, a display drawn on a canvas texture (shows the value while a knob turns, ` *` when modified), `?` opens an HTML manual overlay, clicking the display opens an HTML preset menu. Pick targets by projecting each control's centre with the camera.
- A lamp/meter driven by an editor event (30 Hz, value 0..1, only when changed); the page simulates it without a host.
- Measure the reference photo's colours in the same boxes on the render (mean RGB) to match luminance before material tweaks; run the independent validator after the first full render.
- Aging/wear is a user choice asked in phase 2 (limpo / leve / forte); recipe and helpers in `realistic-hardware-ui/references/wear.md`. It goes into canvas textures (keycap overlay, fader tops, panel art, glass overlay) and roughness maps, so it costs no geometry.
- Redesign of an existing plugin UI: parallel folder `ui-pro/` (own Vite project, `dist/index.html`), same IDs and `SPEC`; never edit the current `ui/`. Layout table `L` in design px = the current UI's screenshot at half size; side-by-side crops against that screenshot per control.
1. Make the page self-contained: no CDN inside a plugin. Inline Three.js (or bundle it with a single-file build) and embed fonts as data URLs.
2. Keep the template's `makeParam` table, presets and `matches()` in the page script; `window.ui.get/set` call those objects. Real-value log parameters pass `lg=[lo,hi]` (JUCE JS sliders are linear over the real range); button groups map to choice parameters; drags call `begin()/end()`.
3. Meters: the editor's 30 Hz event calls `ui.setMeter(db)`; without a host the page keeps its simulation.
4. Presets UI: what was approved in phase 2 (e.g. a slim strip under the panel).
5. The processor tests still parse `makeParam("id","kind"` from the page text, so keep those calls literal.

## 4. The WebView bridge

C++ editor: relays (`WebSliderRelay`, `WebToggleButtonRelay`, `WebComboBoxRelay`) declared **before** the `WebBrowserComponent`, attachments created after it; `withNativeIntegrationEnabled()`, a resource provider serving `index.html`, `js/juce/index.js`, `js/juce/check_native_interop.js` with correct MIME types, `withOptionsFrom(relay)` for each; `goToURL(getResourceProviderRoot())`; a 30 Hz timer pushing meters with `emitEventIfBrowserIsVisible` only when values changed. UI → DSP commands as events that set atomic flags; non-parameter data (curves, files, big state) through native functions.

UI `makeParam(id, kind, init, lg)`: uses JUCE's `getSliderState/getToggleState/getComboBoxState` when `window.__JUCE__` exists, otherwise a local value for the browser demo.
- JUCE JS doesn't echo a local `set`: fire listeners yourself.
- Sliders are linear over the real range: log parameters need `lg=[lo,hi]` + `getScaledValue()`; C++ uses a range with conversion lambdas for host display.
- `begin()/end()` around drags (host automation gestures).
- `getChoiceIndex()` can be `-0` or negative before choices arrive: clamp; combos can't take −1.
- Inside a host the UI must **not** apply the first preset on open: detect the current preset with `matches()` (tolerances per unit), retried at 300 ms and 1.2 s.
- A red "SEM PONTE COM O PLUGIN" bar appears when not on `file://` and the bridge failed: it's how you notice a missing JS file inside the plugin.

## 5. Parameters, presets, state

- Short lowercase IDs identical in UI and `Parameters.h`, `ParameterID{id, 1}`; the table (ID | tipo | faixa real | mapeamento | padrão) lives in the UI script comment, `Parameters.h` and CLAUDE.md. Never rename, reorder or re-range after sessions exist; add new IDs, bump a schema value and migrate.
- Avoid IDs that collide with C/C++ names in namespaces (`ceil`, `sync`, `kill`…).
- APVTS defaults = first preset; `getBypassParameter()` returns the internal bypass.
- Presets in the UI script: id, name, one-line description, values; ` *` when modified. Larger products: factory presets in JSON shared by UI, plugin and calibration scripts; user presets in `~/Documents/<Empresa>/<NOME>/Presets`; per-preset output gain to level-match. Calibrate presets by measurement.
- State: APVTS XML; extra data (curves, samples) as ValueTree properties or JSON. Hosts restore many times and from odd threads.

## 6. DSP engine rules

- `Source/dsp/Engine.h`: header-only, no JUCE; `struct Params` (real units, defaults = first preset); `Engine { prepare(sr); reset(); setParams(); process(l, r, n); meters; }`. Testable with plain clang.
- Processor caches `std::atomic<float>*` from `getRawParameterValue` **in the constructor**, builds `Params` each block; stereo or mono in = out.
- Audio thread: no allocation, locks, file I/O, `juce::String`, `DBG`, `setLatencySamples`, `setValueNotifyingHost`; `ScopedNoDenormals`; non-finite → reset/0. Store the sample rate in `prepareToPlay`.
- Bit-exact neutral/mix 0; block-size independence (control tick every 16–32 samples counted from stream start); smoothing (gains ~5 ms, frequencies in log 10–15 ms, mix/bypass 15–20 ms ramps reaching exact 0/1, mode switches crossfaded).
- Latency: zero when possible. It may differ per oversampling/quality mode (the `XSatEngine` in `dsp-core` has 0/32/48 samples via `latencySamples()`); inside a mode it is constant. Padding every mode up to the largest (as BUSSR does up to 30) is optional and costs latency in the cheapest mode: decide and write it in the plan. The latency MUST be reported to the host and the dry path delayed by the same amount. The control that changes it (oversampling) is not automatable: `AudioParameterChoiceAttributes().withAutomatable(false)`.
- Latency that changes live: call `setLatencySamples` only on the message thread (APVTS `Listener` + `isThisTheMessageThread()`, else `AsyncUpdater`; never from `processBlock`, and `triggerAsyncUpdate()` can allocate if a host sets the parameter from the audio thread), also in `prepareToPlay` and `setStateInformation`. Avoid changing it during render/bounce: the host re-prepares or re-aligns tracks and may cut audio; the click on switching modes is expected. Test: impulse latency measured per mode at 3 sample rates equals the reported value.
- Non-linear stages: ADAA and/or oversampling only around them; DC blocker after asymmetric shapers. Modulated filters: SVF/TPT in double.
- Meters: the audio thread accumulates (peak max, sum of squares); the editor reads and zeroes with `exchange`.

## 7. Extensions

**Instrument (synth, sampler).** In CMake: `IS_SYNTH TRUE`, `NEEDS_MIDI_INPUT TRUE`, AU type `kAudioUnitType_MusicDevice` (`aumu`), VST3 category `Instrument|Synth` (or `Sampler`); no audio input bus. Use `juce::Synthesiser` with custom voices (or `MPESynthesiser`), band-limited oscillators, `juce::ADSR` or exponential envelopes, voice stealing, all-notes-off on reset/panic, sample-accurate MIDI by splitting the block at event times, host tempo from `AudioPlayHead`. Tests: silence without notes, note-off releases and tails end, max polyphony, pitch accuracy, MIDI timing. Samples and big data: load off the audio thread, swap with an atomic pointer, free old objects on the message thread only.

**Sidechain.** Add a second input bus (disabled by default) in the processor's `BusesProperties`, accept it in `isBusesLayoutSupported`, read it with `getBusBuffer(buffer, true, 1)` when enabled, fall back to the main input otherwise. Detector filtering on the sidechain only. Explain the DAW routing to the user (`validacao-e-calibracao.md` §2).

**Oversampling.** `juce::dsp::Oversampling` around the non-linear block only, built in `prepareToPlay`, latency reported and dry delayed. With a dry/wet mix use `useIntegerLatency = false` plus a linear-phase pad to the next integer (the integer-latency all-pass combs the mix); see `conhecimento-dsp.md` §2.

## 8. Pitfalls that cost real rounds

- The JUCE JS files must be embedded and served, or the UI silently runs in demo mode inside the plugin.
- Declare JS state before use (one "Cannot access X before initialization" kills the whole UI); unique DOM ids.
- UI design size and the C++ editor aspect ratio must match, or black bars appear.
- Hosts (Ableton in particular) keep the old plugin in memory: quit completely after installing; copies in both `/Library` and `~/Library` conflict.
- Changing latency while playing makes hosts cut audio.
- Meters that store only the last block show a fraction of the audio.
- ADAA on a full curve in a parallel path delays the clean part half a sample → comb filter.
- Step sequencers: host PPQ jitter double-fires steps; remember the last scheduled index.
- Calibrating at one level hides distortion blow-ups at others; test several levels and real music.
- A UI tested only against a fake backend isn't done: always test inside a real DAW.
- `juce::dsp::Oversampling` with `useIntegerLatency = true` makes a parallel mix comb (non-linear-phase all-pass); recipe in `conhecimento-dsp.md` §2.
- A saturator calibrated on a −12 dBFS sine sounded like fuzz on the user's mastered music. Calibrate drive at −1 dBFS too (`conhecimento-dsp.md` §1 "Warm vs fuzz").
- A clone keeps the hardware but not the maker's text: replace title/model, badge and "by …" credit; no Google Fonts link inside a plugin (inline woff2).

## 9. iPlug2 — framework alternativo

When the user chooses iPlug2 (see SKILL.md §2b), follow this section instead of §1–4 and §8. Sections §5–7 (DSP engine, extensions, pitfalls) apply to both frameworks; the DSP engine is framework-free by design.

### 9.1 Quando usar iPlug2

| Use iPlug2 | Use JUCE |
|---|---|
| Plugin leve (binário 2–5 MB) | GUI complexa (WebView, componentes nativos) |
| Licença BSD obrigatória (sem royalty, sem splash) | Projeto grande com muitos módulos DSP prontos |
| Deploy web (WAM/WebAudio) | Instrumento com MPE, sampler pesado |
| Controle total do DSP sem framework pesado | Equipe (mais devs conhecem JUCE) |
| Prototipagem rápida de efeitos | Formatos LV2, Standalone robusto |
| Referência: Analog Obsession (100+ plugins grátis) | Referência: maioria dos plugins comerciais |

### 9.2 Setup do iPlug2

```bash
# Clone (uma vez, mantém em /tmp como o JUCE)
git clone --recursive https://github.com/iPlug2/iPlug2.git /tmp/iplug2-src
cd /tmp/iplug2-src && git submodule update --init --recursive

# Dependências adicionais ao checker (verificar-dependencias.sh)
# - Python 3 (já coberto)
# - JUCE não é necessário
# - iPlug2 usa seu próprio sistema de build
```

O checker de dependências (`verificar-dependencias.sh`) detecta automaticamente se iPlug2 está em `/tmp/iplug2-src`; se não, oferece clonar.

### 9.3 Criando o projeto iPlug2

iPlug2 tem seu próprio scaffolder:

```bash
cd /tmp/iplug2-src
python3 Scripts/duplicate.py \
  "IPlugEffect" "<NOME>" "<FABRICANTE4>" "<pasta-destino>"
# ou para instrumento:
python3 Scripts/duplicate.py \
  "IPlugInstrument" "<NOME>" "<FABRICANTE4>" "<pasta-destino>"
```

Depois ajustar em `config.h`:
```cpp
#define PLUG_NAME       "<Nome>"
#define PLUG_MFR        "<Empresa>"
#define PLUG_VERSION_HEX  0x00010000  // 1.0.0
#define PLUG_UNIQUE_ID    '<Code>'    // 4 chars, ex: 'Lvlr'
#define PLUG_MFR_ID       '<Mfr4>'
#define PLUG_CHANNEL_IO   "2-2"       // stereo in/out
```

### 9.4 Layout do projeto iPlug2

```
<pasta>/
  CLAUDE.md  README.md  .gitignore
  config.h                              # identidade e configuração do plugin
  <Nome>.h / <Nome>.cpp                 # processador (equivale a PluginProcessor)
  <Nome>_DSP.h                          # motor DSP (header-only, sem framework)
  resources/                            # UI assets (imagens, fontes)
    main.svg / *.png                    # gráficos da interface
  installer/                            # scripts de instalação
  scripts/                              # build, teste
```

### 9.5 Build iPlug2 (macOS)

```bash
cd <pasta>/projects
# Xcode:
open <Nome>-macOS.xcodeproj
# ou CMake (se configurado):
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

iPlug2 usa projetos Xcode por padrão. CMake é possível mas não é o caminho oficial. Para builds automatizados, usar `xcodebuild`:

```bash
xcodebuild -project projects/<Nome>-macOS.xcodeproj \
  -scheme "<Nome> (VST3)" -configuration Release build
```

### 9.6 Interface no iPlug2

**Opções de GUI:**

1. **IGraphics (NanoVG + Metal)** — padrão do iPlug2. Leve, vetor, controles customizáveis. Usado pelo Analog Obsession (LALA, etc.).
2. **IGraphicsWeb** — HTML/CSS/JS via WebView, similar ao approach JUCE+WebView.
3. **Sem GUI** — para processamento headless.

Para interface **moderna**: usar IGraphics com controles vetor (knobs SVG, meters, presets).
Para interface **photoreal (Three.js)**: usar IGraphicsWeb com o mesmo approach do JUCE (WebView + bridge), ou exportar filmstrips do Three.js e usar IGraphics com bitmaps.

**Bridge iPlug2 (IGraphics):**
```cpp
// No construtor do plugin:
pGraphics->AttachControl(new IVKnobControl(bounds, kParamGain));
// Parâmetros definidos no construtor:
GetParam(kParamGain)->InitDouble("Gain", 0., -24., 24., 0.1, "dB");
```

**Bridge iPlug2 (WebView):**
```cpp
// Mensagens UI ↔ DSP via SendArbitraryMsgFromUI / SendArbitraryMsgFromDelegate
// ou via parâmetros nativos (mais simples)
```

### 9.7 DSP no iPlug2

O motor DSP (`<Nome>_DSP.h`) segue as mesmas regras do §6 (header-only, sem framework):

```cpp
// <Nome>_DSP.h — mesma estrutura do Engine.h
struct Params { double gain = 0; double mix = 1; /* ... */ };

class DSPEngine {
public:
  void prepare(double sampleRate) { /* ... */ }
  void reset() { /* ... */ }
  void setParams(const Params& p) { /* ... */ }
  void process(double* left, double* right, int numSamples) { /* ... */ }
};
```

O processador chama o motor:
```cpp
void <Nome>::ProcessBlock(double** inputs, double** outputs, int nFrames) {
  // Ler parâmetros: GetParam(kParamGain)->Value()
  Params p;
  p.gain = GetParam(kParamGain)->Value();
  engine.setParams(p);
  engine.process(outputs[0], outputs[1], nFrames);
}
```

### 9.8 Testes no iPlug2

Sem framework de testes bundled. Criar manualmente:

```cpp
// Tests/EngineTests.cpp — idêntico ao template JUCE (testa só o header DSP)
// Compilar com: clang++ -std=c++20 -I../Source Tests/EngineTests.cpp -o tests && ./tests
```

Para validação:
- `auval -v aufx <Code> <Mfr>` (AU)
- `pluginval --strictness-level 10 --validate-in-process <path>.vst3`
- Mesmos scripts de medição Python (pedalboard)

### 9.9 O que aprendemos do LALA (referência iPlug2)

Da análise do binário do LALA 3.1 (Analog Obsession):

**Arquitetura observada:**
- Framework: iPlug2 com IGraphics (NanoVG + Metal)
- Processamento: todo em `double` (64-bit)
- Classes DSP separadas: `compressor`, `envFollower`, `TubeLine`, `OSAA`, `Biquad`, `VUClass`
- GUI e DSP desacoplados (padrão iPlug2)

**Padrões úteis:**
- Envelope detector: `coeff = 0.01^(1/(time_ms × sr × 0.001))` — convergência a -40 dB
- Waveshaper valvulado: `y = x + 0.01·tanh(x³) + 0.9·tanh(x⁴)` — pares dominam
- Oversampling: filtro half-band FIR polyphase (~60 taps) na classe `OSAA`
- Compressor feed-forward com soft knee quadrático
- Conversão dB: `20/ln(10) = 8.6858...` e `ln(10)/20 = 0.11512...`
- Sidechain: 5 biquads (2× HPF 750 Hz, peak EQ, shelf, pré-ênfase HF)

**Limitações identificadas (oportunidades de melhoria):**
- Sem modelo de célula óptica com memória (release fixo, não bifásico)
- Sem driver de luminescência separado
- Sem impedância CdS não-linear
- Sem transformador saturável (IIR fixo)

### 9.10 Pitfalls iPlug2

- iPlug2 submodules são obrigatórios (`--recursive`); clone incompleto = build falha silenciosamente.
- Xcode projects gerados pelo scaffolder às vezes precisam de ajuste manual nos paths.
- Documentação é escassa: ler os exemplos em `Examples/` é mais útil que a wiki.
- Sem WebView nativo maduro como JUCE; para UI Three.js, considere filmstrip export.
- Não há `FetchContent` como JUCE; o source precisa estar local.
- Formato VST2 requer licença Steinberg separada (legacy); VST3 é o padrão.
- Menos testado em hosts que JUCE; testar em Ableton, Logic, Reaper e LUNA.

## 10. Gain staging e saturação controlada

Applies to both JUCE and iPlug2. Every plugin with a non-linear stage (waveshaper, tube saturation, tape, transformer, clipper) must follow these rules. Without them the plugin sounds too aggressive and distorted at normal DAW levels. These rules come from analysing the LALA 3.1 (Analog Obsession) binary and comparing with the template engine.

### 10.1 The problem

DAW signals arrive at up to 0 dBFS (±1.0 peak) or louder (inter-plugin headroom). A `tanh()` or similar waveshaper has a "musical zone" between ±0.1 and ±0.5 input. Above ±0.7 the harmonics dominate the signal. At ±1.0 the result is harsh digital clipping, not analogue warmth.

| Input level | Distortion character |
|---|---|
| ±0.1 (−20 dBFS) | Clean, subtle coloration |
| ±0.3 (−10 dBFS) | Warm, gentle harmonics |
| ±0.5 (−6 dBFS) | Audible saturation |
| ±0.7 (−3 dBFS) | Aggressive |
| ±1.0 (0 dBFS) | Harsh, digital feel |

### 10.2 The five rules

#### Rule 1: Scale input BEFORE the non-linear stage

Bring the signal into the shaper's musical zone. The scale factor depends on the shaper and the desired character.

```cpp
// drive_scale puts a 0 dBFS signal at ~0.3 inside the shaper
constexpr double drive_scale = 0.3;

double x = input * drive_scale;
double shaped = waveshaper(x);
```

For user-adjustable drive: map the knob to `drive_scale` (e.g. 0.1–0.8), never let it reach 1.0 unless "destroy" is the intent. The LALA's TubeLine uses an IIR pre-filter that also controls level — filtering and scaling combined.

#### Rule 2: Normalise output AFTER the non-linear stage

The shaper adds energy (harmonics). Without compensation the plugin is louder with saturation on, fooling the ear into "sounds better" comparisons and causing gain-staging problems downstream.

```cpp
// Method A: compensate by the input scale (simple, approximate)
shaped /= drive_scale;

// Method B: compensate by the shaper's gain at unity (exact for tanh)
shaped *= 1.0 / tanh(drive_scale);

// Method C: calibrate empirically (best for complex shapers)
// Measure RMS at -18 dBFS input, adjust output_gain until bypass matches
shaped *= output_gain;  // calibrated constant
```

The LALA multiplies the TubeLine output by a calibrated factor (2.37) that accounts for the IIR filter + shaper combined gain.

#### Rule 3: DC blocker after asymmetric distortion

Any waveshaper with even-power terms (`x²`, `x⁴`, `tanh(x⁴)`) generates DC offset because even powers are always ≥ 0. DC offset wastes headroom, moves speakers, and breaks downstream processing.

```cpp
// One-pole DC blocker (~5 Hz cutoff)
// In prepare():
dc_coeff = 1.0 - (2.0 * M_PI * 5.0 / sampleRate);

// In process(), after the shaper:
dc_state = shaped + dc_coeff * dc_state;  // integrator
double clean = shaped - dc_state;           // remove DC
// (This is the standard DC blocker: y[n] = x[n] - x[n-1] + R*y[n-1], R ≈ 0.9997)
```

Alternative (LALA approach): process zero through the same shaper and subtract its output. More expensive but removes the exact DC the shaper's internal state produces.

#### Rule 4: Pre-emphasis filter before the shaper

Raw distortion applies equally to all frequencies. Low frequencies produce muddy intermodulation; high frequencies produce harsh aliasing products. A pre-emphasis filter (tilt, shelf, or bandpass) before the shaper shapes *what* gets distorted.

```cpp
// Simple approach: tilt EQ before shaper, inverse tilt after
// Attenuate lows and boost highs going IN → fewer low-frequency IM products
// Restore balance coming OUT

double pre = tiltFilter.process(input, +3.0);  // +3 dB high tilt
double shaped = waveshaper(pre * drive_scale) / drive_scale;
double post = tiltFilter.process(shaped, -3.0); // -3 dB (restore)
```

The LALA uses a 4th-order IIR (modelling the input transformer + tube amp response) as its pre-filter. This shapes both frequency response and amplitude before the `tanh()` stage.

#### Rule 5: Test at multiple levels, not just one

A shaper calibrated at −18 dBFS may blow up at 0 dBFS or disappear at −30 dBFS. Always test:

| Test signal | Level | What to check |
|---|---|---|
| 1 kHz sine | −30 dBFS | Shaper nearly transparent |
| 1 kHz sine | −18 dBFS | Gentle harmonics, THD < 3% |
| 1 kHz sine | −6 dBFS | Audible warmth, no harshness |
| 1 kHz sine | 0 dBFS | Controlled saturation, no hard clip |
| 1 kHz sine | +6 dBFS | Graceful limiting (tanh plateaus) |
| Pink noise | −18 dBFS | No spectral tilt change |
| Full mix | −14 dBFS RMS | Musical result, no intermod mud |

### 10.3 Complete gain-staging chain (template)

```cpp
// Inside Engine::process(), for any non-linear stage:

// 1. Input scaling — bring signal into shaper's musical zone
double x = input * drive_scale;           // drive_scale: 0.1–0.5

// 2. Pre-emphasis filter (optional but recommended)
x = preFilter.process(x);                 // tilt, shelf, or bandpass

// 3. Waveshaper — in the controlled zone
double shaped = x + a * tanh(x*x*x)      // odd harmonics (a ≈ 0.01)
                  + b * tanh(x*x*x*x);   // even harmonics (b ≈ 0.1–0.9)
// tanh() self-limits: max added energy = a + b regardless of input

// 4. DC blocker — remove offset from even-power terms
dc_state = shaped + dc_coeff * dc_state;
shaped -= dc_state;

// 5. Post-emphasis filter (inverse of pre-emphasis)
shaped = postFilter.process(shaped);

// 6. Output normalisation — match bypassed level
shaped *= output_compensate;               // calibrated to unity at ref level

// 7. Dry/wet mix
output = input * (1.0 - mix) + shaped * mix;
```

### 10.4 Reference: LALA waveshaper weights

The LALA uses `y = x + 0.01·tanh(x³) + 0.9·tanh(x⁴)`:

- `0.01` on odd harmonics (3rd, 5th, 7th…) — barely audible, adds "air"
- `0.9` on even harmonics (2nd, 4th, 6th…) — dominant, warm tube character
- Even with extreme input, max added distortion = 0.91 (tanh saturates at 1.0)
- The even/odd ratio 90:1 matches real tube amplifier harmonic profiles

For different characters, adjust the weights:

| Character | Odd weight (a) | Even weight (b) | Notes |
|---|---|---|---|
| Clean tube preamp | 0.005 | 0.05 | Subtle warmth |
| Driven tube (LALA) | 0.01 | 0.9 | Strong even harmonics |
| Tape saturation | 0.1 | 0.3 | More balanced odd/even |
| Transformer | 0.02 | 0.15 | Soft, low-order |
| Guitar amp | 0.5 | 0.3 | Odd-dominant, aggressive |
| Symmetric clipper | 0.5 | 0.0 | Pure odd harmonics |

### 10.5 Common mistakes checklist

Before shipping any plugin with saturation, verify:

- [ ] Signal scaled to ±0.3 before reaching `tanh()` / waveshaper at 0 dBFS input
- [ ] Output level matches bypass at −18 dBFS reference (within ±0.5 dB)
- [ ] DC blocker present after any even-power or asymmetric shaper
- [ ] No hard clip at +6 dBFS input (graceful saturation)
- [ ] THD at −18 dBFS input is under 3% (unless "heavy distortion" is the goal)
- [ ] Pre-emphasis filter prevents low-frequency intermodulation mud
- [ ] Drive knob range does not allow signal above ±0.7 into the shaper at 0 dBFS input
- [ ] Tested with sine, pink noise AND full mix at multiple levels (§10.2 Rule 5 table)
- [ ] Oversampling active around the non-linear stage (§7) to prevent aliasing of generated harmonics

## 11. Interface fotorrealista em bitmaps (editor nativo)

A WebView com Three.js remonta a cena a cada abertura do editor (processo web, parse, shaders, valores do host chegando depois), e o usuário vê o plugin "se remontando". Plugins da indústria desenham bitmaps prontos. Para interface vintage/clone, o caminho recomendado é: assar o painel em PNG (fundo estático + sprite sheet por controle + `manifest.json`) e usar um **editor JUCE nativo** (DSP, processador, testes e instalador não mudam). Receita completa, com o hook `?export`, o script `export-bake.mjs`, a ligação JUCE (`ParameterAttachment`, VU com mola de 2ª ordem a 60 Hz, cache estático de imagens) e a regra anti-texto-borrado em retina (fundo na resolução FÍSICA, redução em passos de até 2x, largura máxima = tamanho de referência): `realistic-hardware-ui/references/bitmap-nativo.md`.

Regras que valeram no LEVELR (2026-10-30): usar `background-static.png`, janela com largura máxima igual à referência (1326), `NEEDS_WEB_BROWSER FALSE`, snapshot offscreen do editor no teste de processador para olhar o texto e as emendas dos sprites antes de abrir o DAW.
