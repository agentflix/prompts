# Validação e calibração

Three layers, in order: **automatic** (code proves it works), **in the DAW** (hosts don't break it), **with the user's ears** (it sounds right). Then calibrate and loop.

## 1. Automatic tests

Harness style: no framework, a `CHECK(cond, fmt...)` macro counting checks/failures, numbered sections printed in pt-BR, final "N verificações, M falhas", exit code ≠ 0 on failure. Signals generated in code (sine, noise, synthetic kick/bass/hat/pad).

**`<NOME>Tests` (engine only, `Tests/EngineTests.cpp`, plain executable without JUCE)**: invariants (finite output at extremes, silence in → silence/decaying tail out, reset determinism), measurements vs targets, `--bench` CPU; optional `--thd`, `--tune`.

**`<NOME>ProcTests` (real processor, `Tests/ProcessorTests.cpp`)**:
1. Bridge: parse the built `ui/index.html` text for every `makeParam("id","kind"` → parameter exists, type/range/mapping/choices match, presets parse and apply, defaults = preset 0, replica of `matches()`.
2. Buses: mono, stereo, sidechain.
3. Effects: neutral and mix 0 bit-exact (`memcmp`); bypass bit-exact against the input delayed by the reported latency. Instruments instead: silence with no notes, note-off releases and tails end, voice stealing at max polyphony, all-notes-off/panic, pitch accuracy (A4 = 440 Hz within a few cents), sample-accurate MIDI timing.
4. Latency reported = measured with an impulse at several rates and settings.
5. Every preset: finite, invariants hold (e.g. ceiling), metric vs target printed.
6. State save → new instance → restore → identical; restore ×20 with audio running.
7. Block sizes 1…9000 give identical output; sample rates 44.1–192 kHz.
8. Stress: automation every block at extremes → finite, no clicks (max inter-sample jump vs steady state).
9. Meters; CPU budget with parameters moving; editor create/destroy while audio runs.

**UI** (there is no automated UI test script in this skill; the ids/types/ranges check lives in the template's `ProcessorTests.cpp`, "UI ⇄ APVTS"): do it by hand and say so. Open `ui/index.html` in Chrome (check Chrome in phase 0), then headless: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --screenshot=/tmp/ui.png --window-size=W,H file://…/ui/index.html` and `--dump-dom` to confirm that every control id exists. In the real plugin check: opens on preset 0 without `*`, emits nothing on open, log sliders show correct values, events reach the DOM. Optional (not shipped): a script that injects a fake `window.__JUCE__` backend. For photoreal UIs, the `realistic-hardware-ui` screenshot loop.

**Host validators**:
```
auval -v aufx <CODE> <MFR>           # instruments: aumu; MFR = manufacturer code
/Applications/pluginval.app/Contents/MacOS/pluginval --strictness-level 10 --timeout-ms 600000 --validate-in-process ~/Library/Audio/Plug-Ins/VST3/<NOME>.vst3
```
Level 5 is the minimum for host compatibility; 10 before delivery. If an AU isn't found: `killall -9 AudioComponentRegistrar`.

Standard command block (from the project folder; the tests read `ui/index.html` directly):
```
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_JUCE=/tmp/juce-src
cmake --build build                      # plugin (VST3, AU, Standalone, signed and installed in ~/Library) + tests
./build/<NOME>Tests
./build/<NOME>ProcTests_artefacts/Release/<NOME>ProcTests
auval -v aufx <CODE> <MFR>
/Applications/pluginval.app/Contents/MacOS/pluginval --strictness-level 10 --timeout-ms 600000 --validate-in-process ~/Library/Audio/Plug-Ins/VST3/<NOME>.vst3
```
On a busy machine pluginval level 10 can fail a background-thread test on its default 30 s timeout; rerun with `--timeout-ms 600000` before suspecting the plugin, and if it still fails, investigate a real hang.

Tell the user the result in plain words ("todos os 1.243 testes passaram; o validador da Apple e o pluginval no nível máximo aprovaram"). A test that can never fail is not evidence; thresholds change only with the user's decision.

## 2. In the DAW (with the user)

Guide step by step; they may never have done this.
1. Close the DAW completely (Ableton keeps the old plugin in memory).
2. Open it, rescan plugins if needed, find `<NAME>` under the user's company name.
3. Put it on a track with a loop they know.
   - Instrument: create a MIDI track, put the plugin on it, play a clip or a MIDI keyboard (no keyboard: draw notes in the piano roll).
   - Sidechain: Ableton — on the plugin's track open the sidechain section (the triangle in the device title) and choose the source track in "Audio From"; Logic — choose the source track in the plugin window's "Side Chain" menu; REAPER — route the source track to channels 3/4 of the plugin's track.
4. Checklist (each item is a yes/no question to them):
   - opens and the interface shows the controls moving;
   - automation: draw fast automation on each knob → no clicks;
   - save the project, close, reopen → same settings and sound;
   - change buffer size (64 → 1024) and sample rate (44.1 → 96 kHz) → still works, same sound;
   - several instances at once; freeze/bounce/export;
   - CPU meter reasonable.

## 3. Listening script (for non-technical users)

Instruments: replace 1–2 with "play the same phrase in each preset and compare with a reference sound at the same volume"; add sustained notes, fast repeated notes, many notes at once (chords) and the lowest/highest notes.

1. **Same volume first**: compare on/off level-matched (louder always sounds "better"). Use the plugin's output/gain or the preset's built-in gain.
2. Switch on/off several times; better, have someone else switch without saying which is which.
3. Compare with 2–3 reference songs of the same style at the same volume.
4. Extreme settings: everything at maximum/minimum → listen for clicks, harshness, noise.
5. Turn each knob fast while playing → no zipper, no clicks.
6. Mono: sum to mono (DAW utility) → nothing disappears or goes hollow.
7. Silence: stop the music → plugin goes quiet (or the tail fades), no hiss, no CPU spike.
8. Every preset: "forte demais / fraco demais / no ponto / tirar".
9. Headphones and speakers, low and normal volume.

Log in `docs/AUDICAO.md`:

| data | DAW / buffer / taxa | fones ou monitores | o que ouvir | resultado (APROVADO / AJUSTAR / REMOVER) | nota |
|---|---|---|---|---|---|

Render WAVs into `audition/` (gitignored) when comparing versions helps.

## 4. Measurement and calibration

Measure before tuning, change one thing per round, report numbers only with the command that produced them. Python tools: numpy/scipy, soundfile, pyloudnorm (BS.1770); Spotify pedalboard (GPL, tool use only) or a render executable to run the plugin offline. Plugin Doctor is the friendliest GUI if the user has it.

| What | How | Typical acceptance |
|---|---|---|
| Latency | impulse in, peak offset out, at 44.1/48/96 kHz; when the wet path has minimum-phase filters (shelves, LPF) use the group delay from the phase at 1 kHz instead of the peak | equals reported (±0.25 sample), constant across modes |
| Static curve (dynamics) | 1 kHz sine, −60 → 0 dBFS in 1 dB steps, settle ≥ 5× release, RMS of the last third; also 100 Hz and 5 kHz | ≤ 0.5 dB error (≤ 0.2 dB above knee), ratio ±5 % |
| Attack/release | burst 0.5 s below, 1 s at +10 dB, 2 s below; gain envelope; 63 % / 90 % times at 3/6/10/20 dB GR | ±15 % or ±1 ms of target |
| Harmonics / THD | coherent sine `f = k·fs/N` (N = 65536), Blackman-Harris, H2–H10 in dBc, sweep −40 → 0 dBFS in 3 dB steps; always report the drive table at −12 dBFS (mix level) and −1 dBFS (mastered music) | per design target; harmonics ±3 dB, THD ±20 %. Subtle/warm saturator at −1 dBFS: mid-knob ≈ 3 %, H2 > H3 (`conhecimento-dsp.md` §1) |
| Parallel mix (dry/wet) | complex response G of the wet at low level; mix 50 % must equal (dry·e^(−jωL) + G)/2 in magnitude and phase, 100 Hz–20 kHz | ≤ 0.1 dB deviation (otherwise comb filter) |
| Level-matched drive | pink noise −18 dBFS RMS high-passed at 20 Hz, output RMS per drive; add the error to a trim table and repeat | ≤ 0.5 dB across the knob |
| Aliasing | loud tones at 10/14/18 kHz, look for non-harmonic lines | ≥ 60–80 dB below the fundamental (≥ 90 for final) |
| Frequency response | sweep or impulse, compare with the design curve; with the non-linearity off | ±0.05 dB passband where it should be flat |
| DC / silence | mean of output; silent input | DC ≈ 0; silence or decaying tail |
| Loudness | integrated LUFS and true peak of renders; meter checked with EBU 3341 (1 kHz at −23 dBFS = −23.0 ±0.1 LUFS) | presets hit their stated targets; ≤ 0.5 LU on music |
| Reverb | Schroeder backward integration T60 per band; total wet energy | per target/reference |
| Emulation vs hardware | null test / ESR with pre-emphasis / MR-STFT against reference recordings | per project |

The full dynamics protocol P1–P9 with acceptance criteria is in `conhecimento-dsp.md` §3; harmonics and alias tests in §1–2.

**Presets by measurement**: reference WAV → measure features (level, spectral centroid, harmonic ratios, envelope, LUFS, GR) → recipe → render → compare → change one thing → the user listens. Calibrate on real music, not only synthetic signals (synthetic material can measure 1–2 LU off real music).

Record final numbers in the plugin's CLAUDE.md "Medições" with the command used, and what remains open.

### Lições de medição black-box (plugin real como referência)

Measured against a commercial plugin through `pedalboard` (X-Saturator study, 2026-10/11); they apply to any black-box measurement.
- **Reset and warm-up**: `pedalboard` calls `reset()` on every call by default, and the plugin ignored parameter changes for ~0.3 s after it (this looked like a "1 s smoothing" and inflated aliasing from 17 % to 21 %). Use `reset=False`, set the parameters, warm up ≥ 3 s with the same tone, then measure. A parameter change also only counts from the second `process()` call.
- **Quantised knobs**: gain knobs can be quantised (input/drive/output in 0.1 dB steps). A continuous model against a quantised plugin shows false errors near corners (clip ceiling); quantise the model the same way or discover the step with a fine raw-value sweep.
- **Fresh random validation**: fit on a grid, then validate on random points that never entered the fit (separate fit, own hold-out and final hold-out with fixed seeds; look at the final one only at the end). A grid that passes 100 % can hide overfitting.
- **Music test**: tones miss interactions (e.g. a wrong dry path at partial mix passed on 1 kHz tones). Render real music (several tracks, normalised to −1 dBFS peak) through plugin and model with the same settings, align by cross-correlation, and report the null residual `RMS(model − plugin)/RMS(plugin)` in dB, overall and in 100 ms windows (median and % of windows below −40/−30 dB), plus level, LUFS, DC and per-octave band difference.
