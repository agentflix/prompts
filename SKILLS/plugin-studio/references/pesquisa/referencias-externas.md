# External references: JUCE 8 + WebView plugin skill (for non-programmers)

Collected 2026-10-30. Legend: [V] = verified by fetch/search this session; [M] = from prior knowledge, re-check URL/licence before citing as fact.

---

## 1. JUCE 8: WebView UI, CMake, gotchas

### Official sources
- JUCE repo (AGPLv3 / commercial licence; JUCE 8 = AGPLv3 + paid tiers, free "Starter" tier has revenue cap) [M]: https://github.com/juce-framework/JUCE
- CMake API doc [V]: https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md
- Official WebView plugin demo [V]: `examples/Plugins/WebViewPluginDemo.h` in the JUCE repo — https://github.com/juce-framework/JUCE/blob/master/examples/Plugins/WebViewPluginDemo.h
- Frontend JS library ships inside JUCE [V]: `modules/juce_gui_extra/native/javascript/` (index.js: `getSliderState`, `getToggleState`, `getComboBoxState`, `getNativeFunction`). npm mirror types: https://app.unpkg.com/juce-framework-frontend-mirror@8.0.8-rc.1/files/index.d.ts
- API reference [V]:
  - WebSliderRelay: https://docs.juce.com/master/classjuce_1_1WebSliderRelay.html
  - WebControlRelays header (Slider/Toggle/ComboBox relays + `Web*ParameterAttachment`): https://docs.juce.com/master/juce__WebControlRelays_8h.html
  - WinWebView2 options: https://docs.juce.com/master/classWebBrowserComponent_1_1Options_1_1WinWebView2.html
  - Mirror (8.0.9 doxygen): https://ccoderun.ca/programming/doxygen/juce/classjuce_1_1WebSliderRelay.html
- JUCE tutorials index: https://juce.com/learn/tutorials/ (old `tutorial_web_browser_component` URL now 404) [V]
- JUCE 8 announcement thread: https://forum.juce.com/t/juce-8-is-available-now/61809 [V]

### Best community walkthrough
- Jan Wilczek (WolfSound) "JUCE WebView tutorial" repo + video series. Full working plugin: relays, native functions, events, resource provider, zipped UI in BinaryData, dev-server hot reload [V]: https://github.com/JanWilczek/juce-webview-tutorial — site: https://thewolfsound.com (check repo LICENSE before copying).

### Core pattern (summary)
1. Editor members in this order: relays → `WebBrowserComponent` → `Web*ParameterAttachment`s (attachments need relay + browser alive; C++ init order = declaration order).
2. `WebBrowserComponent::Options{}` builder:
   - `.withNativeIntegrationEnabled()` — required for relays/native functions/events.
   - `.withResourceProvider(callback, allowedOrigin)` — callback maps URL path → `std::optional<Resource>{ data bytes, mimeType }`. Load with `goToURL(WebBrowserComponent::getResourceProviderRoot())`.
   - `.withOptionsFrom(relay)` per `WebSliderRelay` / `WebToggleButtonRelay` / `WebComboBoxRelay` (name string = JS-side id).
   - `.withNativeFunction("name", [](args, completion){...})` — JS calls `Juce.getNativeFunction("name")(...)` returns Promise.
   - `.withEventListener("evt", ...)`, `emitEventIfBrowserIsVisible(...)` for C++→JS push (meters).
   - `.withInitialisationData(key, value)` → `window.__JUCE__.initialisationData`.
   - `.withUserScript(js)` runs before page load.
   - Windows: `.withBackend(Options::Backend::webview2)` + `.withWinWebView2Options(WinWebView2{}.withUserDataFolder(tempDir).withBackgroundColour(...))`.
3. Serve UI from BinaryData: either embed each file with `juce_add_binary_data`, or zip the `ui/` folder at build time and embed the zip, then read with `juce::ZipFile` in the resource provider (Wilczek repo shows both the CMake zip step and lookup) [V].
4. Dev loop: point `goToURL` at `http://127.0.0.1:<port>` (Vite dev server) for hot reload; switch to resource provider root for release. Pass dev origin as `allowedOrigin` so native integration works from dev server [V].

### CMake essentials [V]
- Minimum CMake 3.22.
- `juce_add_plugin(... FORMATS AU VST3 Standalone PLUGIN_MANUFACTURER_CODE Abcd PLUGIN_CODE Abc1 NEEDS_WEBVIEW2 TRUE NEEDS_WEB_BROWSER TRUE COPY_PLUGIN_AFTER_BUILD TRUE HARDENED_RUNTIME_ENABLED TRUE BUNDLE_ID com.company.product IS_SYNTH FALSE VST3_CATEGORIES Fx AU_MAIN_TYPE kAudioUnitType_Effect)`.
  - `PLUGIN_CODE` default is random per configure: ALWAYS set it (else DAW sees new plugin each build, sessions break).
  - AU: manufacturer code needs ≥1 uppercase; plugin code exactly 1 uppercase.
  - `NEEDS_WEB_BROWSER` = Linux WebKit only; `NEEDS_WEBVIEW2` = Windows only.
  - `HARDENED_RUNTIME_ENABLED` required for notarization.
- Compile defs: `JUCE_WEB_BROWSER=1`, `JUCE_USE_CURL=0`, `JUCE_VST3_CAN_REPLACE_VST2=0`, Windows `JUCE_USE_WIN_WEBVIEW2_WITH_STATIC_LINKING=1` (avoids shipping WebView2Loader.dll).
- Link `juce::juce_recommended_config_flags`, `..._lto_flags`, `..._warning_flags`.
- FetchContent: official doc only documents `add_subdirectory` / `find_package`; FetchContent works the same way (`FetchContent_Declare(JUCE GIT_REPOSITORY https://github.com/juce-framework/JUCE GIT_TAG 8.0.x)` + `FetchContent_MakeAvailable(JUCE)`). Pin exact tag. Popular template doing this: Pamplejuce (MIT) https://github.com/sudara/pamplejuce [M] — CI, pluginval, signing, notarization, Catch2 already wired.

### Known gotchas
- WebView2 user data folder: plugin hosts may deny default location; set `withUserDataFolder(tempDirectory)` [V] (JUCE docs).
- WebView2 Runtime must exist on user machine (Win10 may lack it; Win11 has it). Check `WebBrowserComponent::areOptionsSupported(options)` and show fallback message [V forum: https://forum.juce.com/t/webview2-does-not-use-edge-but-ie/50492].
- Repeated open/close of editor with fast timer crashed demo on WebView2 (JUCE 8.0.0 era report) [V]: https://forum.juce.com/t/juce-8-webview-bug-webviewplugindemo-crashes-when-repeatedly-launched/62131 — stop timers in editor destructor, keep JUCE updated.
- macOS WKWebView: page loads async; first parameter values arrive via relay events, not instantly — UI must handle "not ready yet". Keyboard focus/shortcuts in some DAWs (Logic, Ableton) can be swallowed by webview [M].
- Never call audio thread from JS handlers; native functions run on message thread. Meter data: atomics in processor, timer in editor pushes via `emitEventIfBrowserIsVisible` [M].
- Relay names must match exactly between C++ and JS; mismatch = silent no-op [M].
- MIME types: return correct `text/html`, `text/javascript`, `text/css`, else WebView refuses module scripts [M].
- Use relative asset paths in bundler config (Vite `base: './'`) so files resolve under resource provider root [M].

---

## 2. Validation tools and how DAWs break plugins

### pluginval (Tracktion) — GPLv3 tool (using it is fine; not linking) [V]
- Repo: https://github.com/Tracktion/pluginval ; releases page has binaries.
- CI doc: https://github.com/Tracktion/pluginval/blob/develop/docs/Adding%20pluginval%20to%20CI.md
- Non-dev GUI guide: https://github.com/Tracktion/pluginval/blob/develop/docs/Testing%20plugins%20with%20pluginval.md
- Strictness 1–10; **5 = minimum for host compatibility**; higher adds parameter fuzzing, repeated state restore, slower tests. Use 10 before release.
- CLI: `pluginval --strictness-level 10 --validate "/path/My.vst3"`; also `validate` subcommand form; `--skip-gui-tests` (headless CI), `--output-dir`, `--junit-xml`, `--json-results`. `-h` lists rest (`--timeout-ms`, `--sample-rates`, `--block-sizes`, `--randomise`, `--repeat`, `--validate-in-process` [M]). Exit 0 = pass, 1 = fail.
- GUI: keep "Validate in process" OFF so crash does not kill log.

### Apple auval [M]
- `auval -a` lists AUs; `auval -v aufx Abc1 Abcd` validates (type, subtype=PLUGIN_CODE, manufacturer=PLUGIN_MANUFACTURER_CODE). Types: `aufx` effect, `aumu` instrument, `aumf` MIDI effect.
- `auvaltool`/`auval -strict` for stricter run. If AU not found after install: `killall -9 AudioComponentRegistrar` and re-run.
- Logic Pro runs auval itself; failure = plugin disabled in Logic (Plugin Manager can "Reset & Rescan").
- Apple doc: https://developer.apple.com/documentation/audiotoolbox/audio_unit_v3_plug-ins (search "auval" in Logic Pro user guide for plug-in manager).

### Steinberg VST3 validator [V]
- Console tool `validator` built with VST3 SDK (SDK CMake can run it post-build). `validator path/My.vst3`. Options include `-list`, `-selftest`, `-snapshots`.
- FAQ: https://steinbergmedia.github.io/vst3_dev_portal/pages/FAQ/Miscellaneous.html ; SDK overview https://steinbergmedia.github.io/vst3_doc/sdk.overview.html
- GUI "VST3PluginTestHost" runs far more tests (speaker arrangements, param changes) than CLI [V forum]: https://forums.steinberg.net/t/host-compatibility-testing/201661
- CI example (GitHub Actions): https://dev.classmethod.jp/en/articles/vst3-ci-using-validator-on-github-actions/
- Reported: VST 3.8 SDK moved to MIT licence (Oct 2025) — third-party claim, verify on https://github.com/steinbergmedia/vst3sdk.

### How DAWs commonly break plugins (checklist) [M, consolidated from pluginval tests + JUCE forum experience]
- **State restore**: `setStateInformation` called before editor exists, before `prepareToPlay`, multiple times, with old-version data, or with empty data. Must be version-tolerant (store version tag; missing params use defaults). Pluginval level ≥ 6 does repeated restore.
- **Sample rate change**: 44.1/48/88.2/96/192 kHz; `prepareToPlay` may be called again without `releaseResources`. Recompute all coefficients, resize delay buffers there (never in `processBlock`).
- **Block size**: actual block can be smaller than `maximumExpectedSamplesPerBlock`, vary every call, be 1 sample, or 0. FL Studio / Reaper send variable sizes. Never assume fixed size.
- **Bus layouts**: mono→mono, stereo→stereo, mono→stereo; `isBusesLayoutSupported` must reject what code cannot handle. Logic and Pro Tools test mono strictly.
- **Bypass**: host bypass calls `processBlockBypassed`; provide `getBypassParameter()` so host bypass and plugin bypass are same parameter; bypass must keep latency compensation (delay dry signal by reported latency).
- **Latency**: call `setLatencySamples()` in `prepareToPlay` (oversampling/lookahead); changing it while playing triggers host re-sync — avoid at runtime.
- **Tail**: `getTailLengthSeconds()` for reverbs/delays, else host cuts tail on offline render.
- **Denormals / NaN**: use `juce::ScopedNoDenormals`; silence input must give silence (or decaying tail), not CPU spike.
- **Parameter automation** from non-message thread; editor may never be opened (render offline); multiple instances share statics (avoid globals).
- **Offline render** faster than realtime; `isNonRealtime()`.
- **Reset**: `reset()` on transport jumps — clear filter states/delay lines.

---

## 3. DSP references by plugin type (licences matter: user plugins are closed source)

Licence rule of thumb:
- **MIT / BSD / ISC / Unlicense / public domain / WTFPL**: may copy into closed-source; keep copyright notice (MIT/BSD) in credits/licence file.
- **LGPL**: dynamic linking OK; static inclusion in plugin binary is risky — treat as study-only for plugins.
- **GPL / AGPL**: study only. Do NOT copy code into closed-source plugin. Re-implement from the paper/math, not from code.
- Papers/books: ideas and formulas are free to implement; text/code listings follow their own copyright.

### General / multi-purpose
| Resource | Licence | Use |
|---|---|---|
| juce::dsp module (IIR, StateVariableTPTFilter, Compressor, Limiter, Reverb (Freeverb), DelayLine, Oversampling, Chorus, Phaser, LadderFilter, WaveShaper, Convolution) | JUCE licence (same as your JUCE licence) | Use directly. Docs: https://docs.juce.com/master/group__juce__dsp.html [M] |
| Signalsmith DSP (delay, filters, FFT, envelopes, spectral, windows) | MIT [V] | Copy OK. https://github.com/Signalsmith-Audio/dsp |
| chowdsp_utils | per module: BSD for core/params/state/presets; **GPLv3 for compressor, eq, filters, reverb, waveshapers (ADAA), dsp_utils (delay)** [V] | DSP modules study only (or buy licence: chowdsp@gmail.com). https://github.com/Chowdhury-DSP/chowdsp_utils |
| Airwindows (300+ plugins: saturation, comps, reverbs, dither) | MIT [M] | Copy OK with notice. https://github.com/airwindows/airwindows |
| DaisySP (Electrosmith; oscillators, filters, effects) | MIT [M] | Copy OK. https://github.com/electro-smith/DaisySP |
| Faust standard libraries | per-function (MIT, LGPL, STK-4.3) [M] | Check each function header. https://github.com/grame-cncm/faustlibraries |
| Surge XT, Vital | GPLv3 [M] | Study only. https://github.com/surge-synthesizer/surge , https://github.com/mtytel/vital |
| musicdsp.org archive | mixed / unspecified | Study; reimplement. https://www.musicdsp.org |
| Julius O. Smith online books (filters, physical audio, spectral) | free online text | Theory. https://ccrma.stanford.edu/~jos/ |
| Will Pirkle "Designing Audio Effect Plugins in C++" (2nd ed.) | book | Best plain textbook for comps, filters, reverbs, delays. |

### Compressors / limiters
- Giannoulis, Massberg, Reiss, "Digital Dynamic Range Compressor Design — A Tutorial and Analysis", JAES 2012 — static curve with soft knee, attack/release detector topologies (decoupled vs branching, peak vs RMS). Reference for implementation. [M] https://www.eecs.qmul.ac.uk/~josh/documents/2012/GiannoulisMassbergReiss-dynamicrangecompression-JAES2012.pdf
- juce::dsp::Compressor / Limiter: simple baseline (no knee, no lookahead) [M].
- Signalsmith blog "limiter" article (lookahead, peak-hold + smoothing) — MIT code [M]: https://signalsmith-audio.co.uk/writing/2022/limiter/
- chowdsp_compressor (GPL) — study level detectors/gain computers.
- Airwindows (MIT) — many character comps (Pressure, ButterComp, etc.).
- True-peak limiter: oversample detector ×4 per BS.1770 annex.

### Saturation / waveshaping / ADAA
- Parker, Zavalishin, Le Bivic, "Reducing the Aliasing of Nonlinear Waveshaping Using Continuous-Time Convolution", DAFx-16 (first-order ADAA) [M]: https://www.dafx.de/paper-archive/2016/dafxpapers/20-DAFx-16_paper_41-PN.pdf
- Bilbao, Esqueda, Parker, Välimäki, "Antiderivative Antialiasing for Memoryless Nonlinearities", IEEE SPL 2017 [M].
- Jatin Chowdhury blog/articles on ADAA (explanations free; code GPL) [M]: https://jatinchowdhury18.medium.com/practical-considerations-for-antiderivative-anti-aliasing-d5847167f510
- Practical: oversample ×2–×8 + tanh/asymmetric shaper + DC blocker; ADAA lets you use less oversampling.

### EQ / filters
- RBJ Audio EQ Cookbook (W3C Note; formulas free to implement) [M]: https://www.w3.org/TR/audio-eq-cookbook/
- Vadim Zavalishin, "The Art of VA Filter Design" rev 2.1.x (free PDF, Native Instruments) — TPT/zero-delay-feedback SVF, ladder, theory [M]: https://www.native-instruments.com/fileadmin/ni_media/downloads/pdf/VAFilterDesign_2.1.2.pdf
- Andrew Simper (Cytomic) technical papers — linear trapezoidal SVF, all RBJ shapes from one SVF, modulation-safe [M]: https://cytomic.com/technical-papers/ (SvfLinearTrapOptimised2.pdf)
- juce::dsp::StateVariableTPTFilter and IIR::Coefficients (cookbook-based) — use directly.
- Tip: SVF/TPT for anything automated; biquad direct form only for static filters; use double precision for low-frequency shelves.
- Linear-phase EQ: FIR via `juce::dsp::Convolution` / FFT (adds latency — report it).

### Reverb
- Jon Dattorro, "Effect Design Part 1: Reverberator and Other Filters", JAES 1997 — plate reverb topology (copy topology freely; it is published algorithm) [M]: https://ccrma.stanford.edu/~dattorro/EffectDesignPart1.pdf ; Part 2 (delay/chorus/flange): https://ccrma.stanford.edu/~dattorro/EffectDesignPart2.pdf
- Freeverb (Jezar, public domain) — Schroeder/Moorer combs + allpasses; `juce::Reverb` is based on it [M]. Original: https://ccrma.stanford.edu/~jos/pasp/Freeverb.html
- FDN: Julius Smith "Feedback Delay Networks" chapter [M]: https://ccrma.stanford.edu/~jos/pasp/Feedback_Delay_Networks_FDN.html
- Signalsmith "Let's Write a Reverb" (ADC21 talk + article, MIT example code) — best beginner path to good FDN reverb [M]: https://signalsmith-audio.co.uk/writing/2021/lets-write-a-reverb/
- Valhalla DSP blog (design notes, no code) [M]: https://valhalladsp.com/blog/
- CloudSeed (MIT, by Ghost Note Audio) algorithmic reverb [M]: https://github.com/ValdemarOrn/CloudSeed

### Delay / modulation
- juce::dsp::DelayLine (Lagrange3rd / Thiran / Linear interpolation) — use directly.
- Signalsmith `delay.h` (MIT) — interpolators.
- Dattorro Part 2 (above) for chorus/flanger/vibrato.
- Pirkle book chapters for ping-pong, tape-style feedback filtering.
- Tip: smooth delay-time changes (crossfade or slewed read pointer) to avoid zipper/clicks.

### Pitch / time
- Signalsmith Stretch — MIT, high quality polyphonic pitch/time [M]: https://github.com/Signalsmith-Audio/signalsmith-stretch
- Rubber Band — GPLv2+ or commercial licence [M]: https://breakfastquay.com/rubberband/
- SoundTouch — LGPL-2.1 (avoid static link in closed plugin) [M]: https://codeberg.org/soundtouch/soundtouch
- Bungee — MPL-2.0 (file-level copyleft; usable if Bungee files stay open) [M]: https://github.com/bungee-audio-stretch/bungee
- Theory: phase vocoder (Laroche & Dolson 1999), PSOLA. Pitch-shift adds latency — report it.

### Synth / oscillators
- PolyBLEP: Välimäki & Huovilainen, "Antialiasing Oscillators in Subtractive Synthesis", IEEE SPM 2007; Martin Finke tutorial (clear code walk-through) [M]: https://www.martin-finke.de/articles/audio-plugins-018-polyblep-oscillator/
- Wavetable with mip-maps: Nigel Redmon EarLevel series [M]: https://www.earlevel.com/main/category/digital-audio/oscillators/wavetable-oscillators/
- BLIT/minBLEP: Brandt "Hard Sync Without Aliasing" (ICMC 2001) [M].
- JUCE `Synthesiser` / `MPESynthesiser` classes for voice management; juce::dsp::Oscillator is NOT band-limited (lookup naive) — fine for LFO only.
- Study (GPL): Surge XT, Vital, Dexed. Copy-OK: DaisySP (MIT).

### Oversampling
- juce::dsp::Oversampling — polyphase IIR (low latency, non-linear phase) or FIR equiripple (linear phase, more latency); call `getLatencyInSamples()` and add to `setLatencySamples` [M].
- HIIR (Laurent de Soras) — half-band polyphase IIR, SIMD; licence WTFPL per author readme [M, verify in download]: http://ldesoras.free.fr/prod.html#src_hiir ; designer tool https://github.com/paulfd/hiir-designer
- r8brain-free-src (Aleksey Vaneev) — MIT, high-quality resampler [M]: https://github.com/avaneev/r8brain-free-src

---

## 4. Calibration and measurement

### Standards
- ITU-R BS.1770-5 (loudness LUFS + true peak; K-weighting, gating, 4× oversampled true peak) [M]: https://www.itu.int/rec/R-REC-BS.1770
- EBU R 128 (−23 LUFS broadcast) + EBU Tech 3341/3342 (meter, LRA) [M]: https://tech.ebu.ch/publications/r128
- Streaming targets (approx.): Spotify −14 LUFS-I, Apple Music −16, YouTube −14; true peak ≤ −1 dBTP.

### Methods
- **Exponential sine sweep** (Farina, AES 2000): one sweep + inverse filter gives impulse response, frequency response and separated harmonic distortion orders [M]: https://www.researchgate.net/publication/2456363_Simultaneous_Measurement_of_Impulse_Response_and_Distortion_With_a_Swept-Sine_Technique
- **THD / THD+N**: single sine (e.g. 1 kHz at −18 dBFS, then −6, 0), FFT with window (Blackman-Harris), sum harmonic power / fundamental. Check aliasing: sweep 1–20 kHz, look for non-harmonic lines folding down.
- **Frequency response**: impulse or white/pink noise in, FFT out/in; compare with design curve (e.g. RBJ magnitude formula).
- **Null test**: same input through plugin A and reference (or old version), invert one, sum; residual level (dBFS) shows difference. Needs sample-accurate alignment and latency compensation. Good regression test between builds (bit-exact = −inf).
- **Compressor static curve**: feed stepped sine levels (−60…0 dBFS, 1 dB steps), measure steady-state output; plot in vs out; check threshold, ratio, knee width.
- **Attack/release timing**: tone burst (e.g. −30 dBFS then step to −10 dBFS); measure time for gain reduction to reach 63% (1 time constant) or 10–90%. State which definition the knob uses.
- **Latency check**: impulse in, find peak offset in output; must equal reported `getLatencySamples()`.
- **Loudness**: render through plugin, measure integrated LUFS + true peak with BS.1770 meter.

### Tools
- Plugin Doctor (DDMF, paid, Mac/Win) — linear/nonlinear analysis, harmonics, dynamics curve, oscillator mode; ideal for non-programmer [M]: https://ddmf.eu/plugindoctor/
- REW Room EQ Wizard (free) — sweeps, THD, can loop through DAW [M]: https://www.roomeqwizard.com
- Python stack:
  - numpy/scipy (`scipy.signal` for sweeps, filters, `freqz`, windows) — BSD.
  - soundfile (BSD) to read/write WAV; pedalboard (Spotify, GPLv3 — tool use only) can host VST3/AU in Python for automated render tests [M]: https://github.com/spotify/pedalboard
  - pyloudnorm (MIT) BS.1770 loudness [M]: https://github.com/csteinmetz1/pyloudnorm
  - libebur128 (MIT, C) [M]: https://github.com/jiixyj/libebur128
  - DawDreamer (GPLv3) offline host for testing [M]: https://github.com/DBraun/DawDreamer
- Free meters inside DAW: Youlean Loudness Meter (free tier), Voxengo SPAN (free spectrum) [M].

### Simple listening validation for non-technical user
1. **Level-match** before judging (louder always sounds "better"): use plugin output gain until LUFS/peak equal with bypass.
2. **A/B with bypass** quickly, several times; better: blind (ask someone else to toggle, or use ABX tool).
3. **Reference tracks**: 2–3 well-known commercial songs in same genre; compare tone/loudness at matched level.
4. **Extreme settings first** (max drive, fastest attack, max feedback) to hear artifacts: clicks, distortion, noise, "zipper" when turning knobs.
5. **Automation test**: draw fast automation on each knob; listen for clicks.
6. **Mono check**: sum to mono (DAW utility); sound must not vanish or go hollow.
7. **Silence test**: stop input; plugin must go quiet (or reverb tail decays), no hiss/DC/CPU spike.
8. **Sample rate test**: open project at 44.1 and 96 kHz; sound should match.
9. Low and normal monitoring volume; headphones + speakers.

---

## 5. Glossário em português (Brasil) — uma frase por termo

- **Threshold (limiar)**: nível a partir do qual o compressor começa a agir.
- **Ratio (razão)**: quanto o compressor reduz o que passa do limiar; 4:1 = a cada 4 dB acima, sai só 1 dB.
- **Attack (ataque)**: rapidez com que o compressor começa a reduzir quando o som passa do limiar.
- **Release (soltura/recuperação)**: rapidez com que o compressor para de reduzir quando o som cai.
- **Knee (joelho)**: quão suave é a transição entre "não comprimir" e "comprimir"; joelho macio = mais natural.
- **Makeup gain (ganho de compensação)**: volume adicionado depois da compressão para recuperar o nível.
- **Gain reduction (redução de ganho)**: quantos dB o compressor está tirando naquele momento.
- **Limiter (limitador)**: compressor extremo que impede o som de passar de um teto.
- **Ceiling / teto**: nível máximo que o limitador deixa sair.
- **Lookahead (antecipação)**: o plugin "olha à frente" alguns milissegundos para reagir antes do pico, ao custo de latência.
- **Wet/Dry (molhado/seco) ou Mix**: proporção entre som processado e som original.
- **Latência**: atraso causado pelo plugin entre entrada e saída; a DAW compensa se o plugin informar.
- **Sample rate (taxa de amostragem)**: quantas amostras por segundo o áudio tem (44,1 kHz, 48 kHz...).
- **Buffer / block size (tamanho de bloco)**: quantas amostras o plugin processa de cada vez; menor = menos atraso, mais CPU.
- **dBFS**: escala de volume digital em que 0 é o máximo absoluto antes de distorcer.
- **Headroom (margem)**: espaço entre o nível atual e o máximo (0 dBFS) antes de clipar.
- **Clipping**: distorção dura que acontece quando o sinal passa do máximo.
- **Saturação**: distorção suave e agradável que adiciona harmônicos e "calor".
- **Harmônicos**: frequências extras múltiplas da nota original, que dão cor ao som.
- **Aliasing**: distorção indesejada e "metálica" que aparece quando o processamento cria frequências acima do limite digital.
- **Oversampling (superamostragem)**: processar internamente em taxa mais alta para reduzir aliasing, gastando mais CPU.
- **EQ (equalizador)**: ferramenta que aumenta ou corta faixas de frequência (graves, médios, agudos).
- **Q / largura de banda**: quão estreita ou larga é a faixa de frequência que o EQ afeta.
- **Shelf (prateleira)**: filtro que sobe ou desce tudo acima (ou abaixo) de uma frequência.
- **High-pass / Low-pass (passa-altas / passa-baixas)**: filtros que cortam graves ou agudos, respectivamente.
- **Reverb**: simulação do som refletindo em uma sala ou ambiente.
- **Pre-delay**: tempo entre o som original e o início da reverberação.
- **Decay / Tail (decaimento / cauda)**: quanto tempo o efeito (reverb, delay) leva para sumir.
- **Feedback (realimentação)**: quanto do eco volta para gerar novas repetições.
- **LFO**: oscilador lento que movimenta automaticamente um parâmetro (vibrato, chorus).
- **LUFS**: medida de volume percebido pelo ouvido, usada por streaming e TV.
- **True peak**: pico real do sinal depois de convertido para analógico; pode passar de 0 dBFS mesmo se a amostra não passar.
- **Mono compatibility (compatibilidade mono)**: o som continua bom quando os dois canais são somados em um só.
- **Fase**: alinhamento no tempo entre ondas; fases opostas se cancelam.
- **Bypass**: desliga o efeito temporariamente para comparar com o som original.
- **Automação**: gravar na DAW os movimentos de um botão ao longo da música.
- **Preset**: configuração salva de todos os botões do plugin.
- **DAW**: programa de gravação e mixagem (Logic, Ableton, Reaper, FL Studio, Pro Tools).
- **VST3 / AU**: formatos de plugin; VST3 funciona na maioria das DAWs, AU é exigido pelo Logic no Mac.

---

## 6. Distribution basics

### macOS plugin folders [V Steinberg + M]
- VST3: `/Library/Audio/Plug-Ins/VST3/` (system; user alt `~/Library/Audio/Plug-Ins/VST3/`). https://www.steinberg.help/r/vst-plug-in-locations-on-mac-os-x-and-macos
- AU: `/Library/Audio/Plug-Ins/Components/` (`.component`).
- AAX: `/Library/Application Support/Avid/Audio/Plug-Ins/` (needs PACE signing; separate).
- Standalone app: `/Applications/`.

### Code signing + notarization (macOS)
- Need Apple Developer Program (US$99/yr) with two certificates: **Developer ID Application** (sign `.vst3`, `.component`, `.app`) and **Developer ID Installer** (sign `.pkg`) — not interchangeable [V forum/tool].
- Steps:
  1. Build with `HARDENED_RUNTIME_ENABLED TRUE` (JUCE CMake) [V].
  2. `codesign --force --options runtime --timestamp --sign "Developer ID Application: Name (TEAMID)" My.vst3` (also `.component`). Sign nested frameworks/dylibs first (or `--deep` cautiously).
  3. Build pkg: `pkgbuild --root <payload> --identifier com.co.product.vst3 --install-location /Library/Audio/Plug-Ins/VST3 vst3.pkg` per format, then `productbuild --distribution dist.xml --package-path . --sign "Developer ID Installer: Name (TEAMID)" Product.pkg` (or `productsign`).
  4. Notarize outer container only: `xcrun notarytool submit Product.pkg --keychain-profile "notary" --wait`; store creds once with `xcrun notarytool store-credentials`.
  5. Staple: `xcrun stapler staple Product.pkg`; verify `spctl -a -vvv -t install Product.pkg` and `pkgutil --check-signature`.
- Apple docs [M]:
  - Notarizing macOS software: https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
  - Customizing notarization workflow (notarytool): https://developer.apple.com/documentation/security/customizing-the-notarization-workflow
- Forum pitfalls [V]: invalid nested signature rejects whole pkg https://developer.apple.com/forums/thread/128854 ; stapling issues https://developer.apple.com/forums/thread/688119
- Helpers: Pamplejuce CI (sign+notarize in GitHub Actions); Packages app by Stéphane Sudre (GUI pkg builder) http://s.sudre.free.fr/Software/Packages/about.html [M]; Melatonin blog "How to code sign and notarize macOS audio plugins in CI" https://melatonin.dev/blog/how-to-code-sign-and-notarize-macos-audio-plugins-in-ci/ [M].
- Universal binary: `-DCMAKE_OSX_ARCHITECTURES="arm64;x86_64"`; set `CMAKE_OSX_DEPLOYMENT_TARGET` (e.g. 11.0).

### Windows (brief)
- VST3 folder: `C:\Program Files\Common Files\VST3\` [V].
- Installer: Inno Setup (free) https://jrsoftware.org/isinfo.php or WiX https://wixtoolset.org [M].
- Signing: Authenticode with OV/EV certificate or Azure Trusted Signing; `signtool sign /fd sha256 /tr <timestamp-url> /td sha256 ...` on `.vst3` DLL and installer, to reduce SmartScreen warnings [M].
- WebView2 Runtime: present on Win11; for Win10 bundle Evergreen bootstrapper in installer [M]: https://developer.microsoft.com/microsoft-edge/webview2/
- Static-link WebView2 loader (`JUCE_USE_WIN_WEBVIEW2_WITH_STATIC_LINKING=1`) to avoid shipping `WebView2Loader.dll`.

---

## Open items to re-verify before skill ships
- HIIR exact licence text (believed WTFPL).
- VST 3.8 SDK MIT relicensing (third-party claim).
- JUCE 8 licence tiers/revenue cap (check https://juce.com/get-juce/).
- pluginval flags beyond `--strictness-level`, `--skip-gui-tests`, `--output-dir`, `--junit-xml`, `--json-results` (run `pluginval -h`).
- Jan Wilczek repo LICENSE.
