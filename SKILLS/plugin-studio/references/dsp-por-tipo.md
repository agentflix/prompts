# DSP por tipo de plugin

Pick the row for the idea, read the matching sections of `conhecimento-dsp.md` (formulas, ranges, targets) and the references below (URLs and licences in `pesquisa/referencias-externas.md` §3).

## Licences (closed-source plugins)

- **MIT / BSD / ISC / public domain**: may adapt with the copyright notice in `THIRD_PARTY_NOTICES.md` (e.g. Signalsmith DSP, Airwindows, DaisySP, CloudSeed, r8brain).
- **LGPL / MPL**: avoid static inclusion; treat as study-only.
- **GPL / AGPL / no licence**: study only; re-implement from the paper or the maths (e.g. chowdsp DSP modules, Surge, Vital, Dexed, ChowTape, mverb, Rubber Band). Don't open unlicensed repos for code.
- Papers and textbooks: formulas are free to implement.
- JUCE itself: distributing closed source needs a commercial JUCE licence; say so at delivery.

## Map

| Idea | `conhecimento-dsp.md` | Core techniques | Good references |
|---|---|---|---|
| Compressor, limiter, bus/glue, vintage emulation | §3, §4, §10, §2 | Feed-forward log-domain gain computer with quadratic knee; decoupled attack/release; auto release; stereo link; sidechain HPF in the detector only; lookahead and true peak for limiters; colour after the gain element tied to gain reduction | Giannoulis/Massberg/Reiss 2012; Signalsmith limiter article (MIT); Airwindows compressors (MIT) |
| Saturation, distortion, clipper, tape/tube colour | §1, §2, §4 | Waveshaper symmetry rules, H2/H3 control, asymmetric tanh + DC blocker, frequency-dependent saturation, ADAA1/ADAA2, oversampling factor rule, gain compensation, drive anchored on THD | Parker/Zavalishin ADAA (DAFx-16); Bilbao et al. 2017; Airwindows curves (MIT) |
| EQ, filter | §5 | SVF/TPT in double for anything automated; matched-magnitude biquads near Nyquist; LR4 crossovers summing flat; clamp fc ≤ 0.49 fs | RBJ cookbook; Zavalishin "Art of VA Filter Design"; Cytomic SVF papers |
| Reverb | §6 | Modulated FDN tail, early reflections or short IR, RT per band, damping in the loop, tail width, calibrate total wet energy, report tail length | Dattorro 1997; Signalsmith "Let's write a reverb" (MIT); J. O. Smith FDN chapter; CloudSeed (MIT) |
| Delay, chorus, flanger, phaser, tremolo | §7 | Fractional delay, smoothed time changes, filtered feedback with soft limiter and DC blocker, tempo sync, ping-pong | Dattorro part 2; Signalsmith `delay.h` (MIT); `juce::dsp::DelayLine` |
| Gate, expander, transient shaper, de-esser, ducker | §3 (reuse detector and gain computer) | Expander/gate = gain computer below threshold with hysteresis and hold; transient shaper = fast vs slow envelope difference; de-esser = detector on a 5–8 kHz band; ducker = sidechain | Pirkle "Designing Audio Effect Plugins in C++"; calibrate with the dynamics protocol |
| Stereo, width, M/S, utility, metering | §8 | M/S, width, correlation, bass mono, LUFS (BS.1770), true peak 4× | ITU-R BS.1770, EBU Tech 3341 test signals |
| Console, channel strip, summing | §1, §5, §8 | Per-instance tolerances, frequency-dependent saturation, channel EQ ranges, gentle summing compression | Airwindows Console (MIT, study the curves) |
| Synth (subtractive, VA) | §9, §2 | Band-limited oscillators, unison/detune, ladder/SVF filters, exponential envelopes, LFO sync, voice modes and stealing | Välimäki/Huovilainen 2007; EarLevel wavetables; Martin Finke PolyBLEP; study Surge/Vital/Dexed (GPL) |
| Sampler, drum machine, sequencer | `como-construimos.md` §7 | Sampler voices, zones/velocity layers, windowed-sinc resampling (Hermite leaves audible residue when pitching), atomic pointer swap for sample data, PPQ-locked step scheduling | `juce::Synthesiser`/`SamplerVoice` docs; r8brain (MIT) |
| Pitch, time stretch | — | Phase vocoder / PSOLA; report latency | Signalsmith Stretch (MIT); Rubber Band (GPL/commercial) |
| Amp/cab, neural capture | — | Circuit model + small RNN, cab IR via `dsp::Convolution` loaded from the user's disk | NAM (MIT), RTNeural (BSD) |

## Types with less ready knowledge

Gates/transients/de-essers, multiband dynamics, pitch/time, spectral FFT effects, tape wow/flutter, lo-fi, advanced samplers, MIDI effects and MPE have no detailed recipe here. Research papers and MIT code first, write the chosen numbers with sources into CLAUDE.md, and lean harder on measurement and the user's listening.

## Quality checks no review skill does

After the safety reviews, check yourself:
- **Aliasing** of every non-linear stage (alias test in `validacao-e-calibracao.md`).
- **Smoothing**: no parameter jumps per block; mode switches crossfaded.
- **Latency**: reported = measured with an impulse at 44.1/48/96 kHz, constant within a mode (it may change with the oversampling mode, which is then non-automatable and reported to the host); dry path delayed by the same amount.
- **Bypass**: crossfade, bit-exact when fully bypassed after the latency, host bypass mapped to the internal one.
- **Feedback loops**: small-signal loop gain ≤ 1 and a soft limiter inside.

Manual safety checklist (when the review skills aren't installed): in `processBlock` and everything it calls, no `new`/`malloc`/container growth, no locks or waits, no file/network/console I/O, no `juce::String`/`DBG`, no `getRawParameterValue` lookups, no message-thread calls; denormals handled; NaN/Inf guarded; filters stable at extreme settings and fast automation; state reset in `prepareToPlay`.
