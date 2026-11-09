# Conhecimento de DSP (resumo técnico embutido)

Condensed design knowledge for the most common plugin types: formulas, ranges, targets and measurement protocols. Confidence labels: **[Fato]** (maths or primary source), **[Fonte secundária]**, **[Escolha de projeto]** (a sensible default to calibrate), **[Não verificado]**. Keep the label when you cite a number in the plugin's CLAUDE.md. Sources and licences: `pesquisa/referencias-externas.md`.

## Contents
1. Harmonics and saturation
2. Oversampling and anti-aliasing
3. Compressors and limiters
4. Compressor colour
5. EQ and filters
6. Reverb
7. Delay and modulation
8. Stereo, metering, console
9. Synths (subtractive)
10. Hardware reference numbers (published specs)

---

## 1. Harmonics and saturation

- HDn = A(n·f0)/A(f0); THD = √(Σ HDn²). 1 % = −40 dBc, 0.1 % = −60 dBc, 0.01 % = −80 dBc. [Fato]
- Odd-symmetric curve → only odd harmonics; asymmetric → even harmonics + DC (needs a DC blocker). `y = x + b·x²` gives HD2 = b·A/2; `y = x − a·x³` gives HD3 ≈ a·A²/4. Relative HD2 grows 1 dB per dB of level, HD3 2 dB per dB. [Fato]
- `tanh ≈ x − x³/3 + 2x⁵/15`; asymmetric tube-ish: `tanh(g(x + bias)) − tanh(g·bias)`. Padé `tanh ≈ x(27 + x²)/(27 + 9x²)` for |x| ≤ 3. [Fato]
- "Even = warm, odd = harsh" is folklore; what matters is amount, order and level dependence. Low orders with fast roll-off, more distortion at higher level, less in the bass (avoids mud). Perceived "distortion" saturates between ~0.5 % and ~1.6 % THD; roughness differentiates. [Fonte secundária]
- Direct control of H2/H3: `y = x + b·x² − a·x³`, `b = 2·h2/A_ref`, `a = 4·h3/A_ref²`. [Fato]
- Frequency-dependent ("transformer") saturation: integrate (flux ∝ ∫V), saturate, differentiate — bass saturates first (HD ∝ 1/f²). Cheap version: saturate a residual `u = y − 0.5·LP150(y)` or a flux-domain waveshaper. [Fato / Escolha de projeto]
- Recipe (drive + warmth + mix): drive 0–24 dB (log), optional HPF 80–150 Hz on the path into the shaper, asymmetric tanh with warmth = bias, DC blocker after (`y = x − x1 + R·y1`, `R ≈ 1 − 2π·fc/fs`, fc 5–20 Hz), anti-aliasing, gain compensation, phase-coherent parallel mix. [Escolha de projeto]
- A "drive" knob anchored on THD: 0 % < 0.02 %, 25 % ≈ 0.1 %, 50 % ≈ 0.5 %, 75 % ≈ 1.5 %, 100 % ≈ 5 % at the reference level. [Escolha de projeto]
- Soft clipper: drive → 2–4× oversampling → ADAA curve → decimate → ceiling (after decimation) → DC block only if biased. Hard-clip antiderivative `F(x) = x²/2` for |x| ≤ 1, `|x| − 1/2` outside; tanh antiderivative `ln cosh x`, stable as `|x| + log1p(e^(−2|x|)) − ln 2`. [Fato]
- Gain staging convention: 0 VU ≈ −18 dBFS ≈ +4 dBu. [Escolha de projeto]
- **"Warm" vs "fuzz" (field lesson, tube saturator, 2026).** v1 used an exponential asymmetric curve with a hard corner, a large intrinsic bias and +2.4 dB per drive step, calibrated on a −12 dBFS sine; on mastered music (peaks at 0 dBFS) drive 3 was > 25 % THD with H3 dominant and the user heard fuzz. What fixed it:
  - Curve `f(u) = tanh(u + b) − tanh(b)`, b ≈ 0.3 (smoothest knee, H2 dominant over the whole knob); ADAA antiderivative `ln cosh(u + b) − u·tanh(b)`. Avoid curves with a corner (exponential/diode pieces) when the brief says warm or subtle.
  - Scale anchored at mastered level: `u = g·x`, `g = 10^((sens + 3·drive − 28)/20)`. Measured on a −1 dBFS sine, Normal: drive 0 ≈ 0.5 %, 3 ≈ 1.5 %, 5 ≈ 3 %, 7 ≈ 6 %, 10 ≈ 14 % THD, H2 > H3 throughout; at −12 dBFS drive 5 ≈ 0.85 %. Always print the drive/THD table at −12 AND −1 dBFS before the user listens. Users want subtle by default; dirt only at the top of the knob or in a "High" sensitivity.
  - Pre/de-emphasis: 1st-order bilinear shelf, highs −6 dB above ~3 kHz before the shaper, the exact inverse after (swap numerator/denominator of the same bilinear transform: the pair cancels exactly in the linear regime). Highs saturate less → less "sand".
  - Round only what the shaper adds: `e = wet − dry` (both aligned at the same integer latency), DC blocker + 1st-order LPF (20 kHz at drive 0 → 10 kHz at drive max) only on `e`, output `dry + e`. The source passes untouched (linear phase, ±0.13 dB to 20 kHz); only the added harmonics are rounded. A plain LPF on the whole wet path dulls the source and shifts the group delay (latency check fails at 96/192 kHz).
  - Level match: normalise the curve's half-excursion at a reference amplitude (≈ 0.16), then a measured 1-D trim table per total gain in dB (sensitivity and drive fold into one gain): pink noise −18 dBFS RMS **high-passed at 20 Hz** (otherwise the DC blocker eats sub-audio energy and the trim ends ~0.7 dB loud), out RMS = in RMS; two measure-and-add rounds give ≤ 0.03 dB across the knob. [Medido]
- **Gain staging through non-linear stages**: the signal must be scaled into the shaper's musical zone (±0.1 to ±0.5 for `tanh`) BEFORE the waveshaper, and normalised AFTER. DC blocker mandatory after even-power terms. Pre-emphasis filter recommended to prevent low-frequency intermodulation. Full implementation chain and checklist in `como-construimos.md` §10. [Escolha de projeto, validado via análise LALA 3.1]

## 2. Oversampling and anti-aliasing

- With factor L, harmonic k·f0 above `L·fs/2` folds to `L·fs − k·f0`; minimum factor for a polynomial of order p: `L·fs > p·f_max + f_audio` (cubic at 48 kHz aliases above f0 ≈ 9.3 kHz without oversampling, clean with 2×; order 5 needs 4×). [Fato]
- The filter matters more than the factor: target stopband ≥ 90 dB. Linear-phase FIR half-band (latency, pre-ringing; default for mix/master) vs polyphase IIR (tiny latency, phase shift near Nyquist; "live" mode). [Fato]
- Latency of a FIR stage `(M−1)/2` samples at its rate; report the total with `setLatencySamples` and delay the dry path by the same amount; make the total an integer with a linear-phase pad on the wet path, not with an all-pass (see the JUCE note below). [Fato]
- ADAA first order: `y = (F(x[n]) − F(x[n−1]))/(x[n] − x[n−1])`, midpoint fallback when |Δx| < 1e-6, compute in double; adds half a sample of delay (delay the dry or apply ADAA only to the non-linear residual, otherwise a parallel path combs). ADAA2 adds one sample. Measured on a loud 9 kHz hard clip: naive −62.6 dBc, ADAA1 −90.6, ADAA2 −107.8. Common sweet spot: ADAA1 + 2×. [Fato]
- Typical cost on one modern core, stereo, 512 samples: FIR 4× ≈ 2–3 %, 16× ≈ 7 %, 64× ≈ 24 %. Some high tones (10–12.5 kHz) still alias around −51 dBc at 4× regardless of filter; only higher factors or higher-order ADAA help. [Fato, own measurements]
- JUCE `dsp::Oversampling(ch, order, filterHalfBandFIREquiripple, maxQuality, useIntegerLatency)`: with `useIntegerLatency = true` it adds a fractional-delay all-pass whose phase is NOT linear → a parallel dry/wet mix combs (≈ −2 dB at 20 kHz at 50 %). Use `false`, read the fractional latency (8× equiripple: 64.25 samples; 4×: 59.5), and complete the wet path to the next integer with a linear-phase delay at the oversampled rate: integer samples + a 2-sample average for a half sample (`(v[k−a] + v[k−a−1])/2`). With ADAA's half sample included: 8× → 64.25 + 1/16 + 0.6875 = 65. Dry delayed 65: mix 0/bypass bit-exact, partial mix exact in magnitude and phase. Don't align the dry with a cubic Lagrange fractional delay instead: it droops dB near Nyquist. [Medido]
- Measured on a soft-knee tube curve at 48 kHz, loud 7.3 kHz: hard-cornered curve 4× + ADAA1 −52 dB, 8× + ADAA1 −71 dB; soft tanh curve 8× + ADAA1 < −120 dB. 8× stereo ≈ 3 % of a core at 48 kHz, ≈ 6 % at 96 kHz. [Medido]
- Alias test: loud tones at 10/14/18 kHz with coherent bins, report the largest single spur (not the sum); passband ±0.05 dB with the non-linearity off; impulse peak at the reported latency; test 44.1/48/96 kHz. Keep test harmonics away from Nyquist or folding hides the result. [Fato]

## 3. Compressors and limiters

- Gain computer in dB with soft knee W (Giannoulis 2012): [Fato]
  ```
  2(x−T) < −W : y = x
  2|x−T| ≤ W  : y = x + (1/R − 1)(x − T + W/2)² / (2W)
  2(x−T) > W  : y = T + (x−T)/R
  gain reduction = y − x        (limiter: 1/R = 0; hard knee: W = 0)
  ```
- Detector: `α = exp(−1/(τ·fs))`, 10–90 % ≈ 2.2 τ. Decoupled, smooth: `y1 = max(x, αR·y1 + (1−αR)·x)`, `yL = αA·yL + (1−αA)·y1`, on gain reduction in dB. [Fato]
- Feed-forward log-domain detector as default; feedback as an option for vintage behaviour. Auto release: a fast (50–100 ms) and a slow (0.5–2 s) constant weighted by current GR or crest factor. [Escolha de projeto]
- Stereo link max/average/M-S, partial link `gr_i = lerp(own, linked, link)`; sidechain HPF 60–150 Hz in the detector only. [Escolha de projeto]
- Lookahead: delay audio L samples, sliding-minimum deque of required gain plus a moving average of length L, report latency. True peak (BS.1770-4): 4× oversampled detector (48-tap polyphase FIR); ~0.1 ms of lookahead keeps overshoot near 0.1 dB; compute gain at 1× and apply to the oversampled signal to save CPU. Ceiling −1 dBTP costs ~0.8 LU of loudness. [Fato / Fonte secundária]
- Smoothing of user controls 10–50 ms; denormal floor 1e-15…1e-18. [Escolha de projeto]
- Validation protocol (works for any dynamics plugin): [Escolha de projeto, from published methods]
  - P1 sanity: ratio 1:1 identity, latency by cross-correlation, no change below threshold (±0.05 dB).
  - P2 static curve: 1 kHz, −60 → 0 dBFS in 1 dB steps, settle ≥ 5× release, RMS of the last third; repeat at 100 Hz and 5 kHz.
  - P3 attack/release: 0.5 s below threshold, 1 s at +10 dB, 2 s below; gain envelope via Hilbert; 63 %/90 % times at 3/6/10/20 dB GR.
  - P4 program-dependent release: bursts 10 ms–5 s and trains.
  - P5 THD/IMD: exponential sweep, SMPTE 60 Hz + 7 kHz, CCIF 19 + 20 kHz.
  - P6 frequency response under GR; P7 stereo link/crosstalk; P8 noise; P9 music vs reference (null/ESR, loudness error).
  - Acceptance: static curve ≤ 0.5 dB (≤ 0.2 dB above knee), ratio ±5 %, attack/release ±15 % or ±1 ms, loudness ≤ 0.5 LU on music, harmonics ±3 dB, THD ±20 %; no NaN at 44.1/48/96 kHz and blocks 64–1024.

## 4. Compressor colour

- Character comes mostly from gain modulation and the circuit around the gain element, not a static waveshaper; release time dominates the character (slow release cleans odd harmonics). [Fato]
- Profiles: opto (H3 under GR, distorts during release), FET (H3 with H2 rising with GR, much more distortion at 50 Hz than at 1 kHz), VCA (nearly clean, mostly H2, THD 0.005–0.03 %), variable-mu (H2 ≈ H3, low). [Fonte secundária]
- Put saturation after the gain element with drive = f(GR): `h2(GR) = h2₀ + (h2max − h2₀)(GR/GRmax)^p`, p 1–1.5, h2max 1–3 %. Never inside the detector. [Escolha de projeto]
- Opto cell model idea: emitter low-pass ~10 ms; fast state 10–60 ms and slow 1–15 s with memory (`τslow = τ0(1 + k·state)`), resistance `R = R0·s^(−γ)` with γ 0.7–0.9. Validate attack ≈ 33–81 ms, release ≈ 0.45–1.7 s at 6 dB GR. [Fonte secundária]
- Calibrate at several levels, not only −18 dBFS: a model tuned at one level can distort wildly louder.

## 5. EQ and filters

- RBJ biquads cramp near Nyquist at 44.1/48 kHz: e.g. a 16 kHz high shelf is +3.2 dB off at 20 kHz, a 12 kHz bell (Q 1) −4.5 dB. Use matched-magnitude designs (Vicanek) or oversample when the top octave matters. [Fato, own measurements]
- Anything automated or modulated: SVF/TPT (Zavalishin/Simper) in double; direct-form biquads can explode under fast automation. Clamp fc ≤ 0.49 fs. [Fato]
- SVF TPT core: `g = tan(π·fc/fs)`, `k = 1/Q` (Butterworth k = √2). [Fato]
- Linkwitz-Riley 4 crossovers: two cascaded Butterworth 2nd order (Q 0.707), −6 dB at fc, LP + HP sums to an all-pass; three or more bands need all-pass compensation. [Fato]
- Classic console channel EQ ranges (from published manuals): HPF 16–350 Hz; low shelf 30–450 Hz ±17 dB; low-mid 200 Hz–2.5 kHz; high-mid 600 Hz–7 kHz; high shelf 1.5–16 kHz ±17 dB; mid Q 0.1–3.5. Some designs make Q proportional to gain. [Fonte secundária]
- Low-frequency shelves need double-precision coefficients. [Fato]

## 6. Reverb

- Algorithmic halls/plates are not convolution: modulation keeps the tail alive; early and late parts are independent, each with its own EQ. [Fato]
- Late tail: modulated feedback delay network (FDN) with orthogonal mixing matrix; RT per band (bass multiplier below a crossover, high cut inside the loop), slow random modulation (≈ 1–2 Hz, small depth in ms), diffusion all-passes, constant-power width matrix for the tail. Early part: tapped reflections or a short IR (first ~100 ms). [Fato / Escolha de projeto]
- Calibration: Schroeder backward integration for T60 per band; match **total wet energy** to the reference; feed the impulse into both channels when measuring (FDNs mix L/R). Report tail length to the host (`getTailLengthSeconds`). CPU ≈ 2–3 % of a core is achievable. [Fato, own measurements]
- Published topologies to implement from papers: Dattorro plate (1997), Schroeder/Moorer, Jot FDN. [Fato]

## 7. Delay and modulation

- Fractional delay: Lagrange 3rd order or Thiran all-pass; smooth delay-time changes (crossfade two taps or slew the read pointer). [Fato]
- Ranges: flanger 0.1–10 ms with feedback; chorus 10–30 ms modulated; vibrato is chorus without dry; phaser = cascade of all-passes with LFO-swept corner; Haas widening 5–30 ms. [Fonte secundária]
- Feedback: filtered (HP/LP in the loop), soft limiter in the loop, DC blocker, small-signal loop gain ≤ 1; stable at 95–97 % feedback for 30 s. [Escolha de projeto]
- Tempo sync from `AudioPlayHead` (BPM, PPQ): lock phase at block start; stopped transport → free-run at host BPM; no host → 120 BPM. Note divisions incl. dotted/triplet. [Fato]

## 8. Stereo, metering, console

- M/S: `M = (L+R)/√2`, `S = (L−R)/√2`; width `S' = S·w` (0 mono, 1 original, ≤ 2); back `L = (M'+S')/√2`, `R = (M'−S')/√2`. Correlation `r = Σ(L·R)/√(ΣL²·ΣR²)`. Keep bass mono below ~120–150 Hz. [Fato]
- Loudness (ITU-R BS.1770-4/5): K-weighting at any rate, momentary 400 ms, short-term 3 s, integrated with −70 LUFS absolute and −10 LU relative gates; true peak via 4× oversampling. Check the meter with EBU Tech 3341 (1 kHz at −23 dBFS reads −23.0 ±0.1 LUFS). Streaming references (approx., they change): −14 LUFS integrated, −1 dBTP. [Fato]
- VU: RMS-like ballistics ~300 ms rise, ~1.5 % overshoot; 0 VU at the chosen reference level. [Fato]
- Meters across threads: the audio thread accumulates (peak max, sum of squares); the UI timer reads and zeroes with an atomic exchange. Reading only the last block shows a fraction of the audio. [Fato]
- "Analog" console flavour ingredients (ranked by usefulness, [Não verificado]): frequency-dependent bass saturation, gentle peak rounding (more RMS for the same peak), slight summing compression, small bass bump, top smoothing, noise. Per-instance tolerances (seeded) make channels differ slightly.

## 9. Synths (subtractive)

- Waveforms: sine; triangle (odd harmonics 1/n²); saw (all harmonics 1/n); pulse (odd for square, width-dependent). Band-limit them: PolyBLEP/minBLEP or wavetables with mip-maps; naive oscillators alias audibly (metallic highs). [Fato]
- Detune `f2 = f1·2^(cents/1200)`; 10 cents ≈ 0.58 %; musical unison spread ~20–30 cents; hard sync; 2-op FM (sidebands `fc ± n·fm`; integer ratio = harmonic, non-integer = metallic/bell); ring mod `f1 ± f2`. [Fato]
- Filters: LP/BP/HP 12/24 dB/oct, resonance up to self-oscillation, drive, key tracking; ladder = 4 poles with feedback (resonance steals bass: compensate). [Fato]
- Envelopes: exponential segments sound natural; attack ≥ 1–5 ms avoids clicks; sustain 0 = percussive. LFOs with host sync. Voice modes poly/mono/legato, glide, voice stealing (oldest/quietest), panic/all-notes-off. [Fato / Escolha de projeto]
- Design questions for any patch: does it die or sustain? what harmonic material? does the filter move? does touch (velocity) matter? where in space? Symptoms: metallic highs = aliasing; click = attack 0; mud = reverb or unison on the sub. [Escolha de projeto]
- Open-source synths to study (GPL, study only): Surge XT, Vital, Dexed, OB-Xd.

## 10. Hardware reference numbers (published specs, for "inspired by" presets)

Use only as calibration targets, never with brand names in the product.
- Classic FET limiter: ratios 4/8/12/20 (+ "all buttons"), attack ~20–800 µs, release 50 ms–1.1 s, THD < 0.5 % static. [Fonte secundária]
- Classic opto leveller: two-stage release (~60 ms to 50 %, then 0.5–5 s), attack ~10 ms nominal (measured 33–81 ms on units), up to ~40 dB GR. [Fonte secundária]
- Classic VCA bus compressor: attack 0.1/0.3/1/3/10/30 ms, release 0.1–1.2 s + auto, ratio 2/4/10. [Fonte secundária]
- Classic RMS VCA compressor: attack 15/5/3 ms for 10/20/30 dB of overshoot; release ≈ 125 dB/s. [Fonte secundária]
- Variable-mu: attack 25–70 ms, recovery 0.2–8 s, ~1.5:1 compress up to ~20:1 limit. [Fonte secundária]
