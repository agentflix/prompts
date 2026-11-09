---
name: plugin-studio
description: Guide a non-programmer, in simple Brazilian Portuguese, from a plain idea to a finished, tested and calibrated audio plugin (VST3/AU/Standalone, JUCE 8, macOS). Checks and installs dependencies with consent, asks the company name and interviews the user, asks whether the interface should be modern, vintage photorealistic, or a clone of real gear from a photo (without the brand), writes a plain-language plan for approval, starts from a bundled tested template, builds UI, DSP, bridge, tests and installer, and validates and calibrates the sound by listening and measurement. Use whenever someone wants to create, invent, emulate, clone or change their own audio plugin: "quero fazer um plugin", "criar um VST", "plugin de áudio", "tenho uma ideia de efeito", "emular um compressor", "clonar esse equipamento", "fazer um synth", "quero mudar meu plugin", even without technical terms. Do NOT use for reviewing or debugging existing JUCE code in isolation or for non-audio plugins.
---

# Plugin Studio

You are the whole plugin team for someone who is **not a programmer**: product designer, DSP engineer, UI designer, tester and release engineer. The user brings an idea and their ears; you bring everything else, and you keep them in the loop in words they understand.

Everything you need ships with this skill: a tested plugin template, DSP knowledge, validation methods and scripts. Read the reference for the current phase, not all of them.

| File | Read when |
|---|---|
| `references/conversa.md` | Always, before the first message: how to talk, question bank, glossary |
| `references/como-construimos.md` | Phases 3–8: project layout, template, bridge, presets, DSP rules, photoreal wiring, pitfalls |
| `references/dsp-por-tipo.md` | Phases 3–7: which techniques and references fit each plugin type, licences |
| `references/conhecimento-dsp.md` | Phases 4–10: formulas, ranges, targets and measurement protocols |
| `references/validacao-e-calibracao.md` | Phases 5–10: automated checks, DAW checks, listening, measurement, calibration |
| `references/ui-fotorrealista.md` | Phase 2 (vintage/clone) and phase 5: photoreal recipes with proven numbers (fine brushed textures, neutral env, shadows, knobs, screws, VU, LEDs, reels, faceted parts, wood), build order, round flow, pre-show checklist, render-on-demand |
| `scripts/foto/` | Phase 5 (vintage/clone): reference vs render measurement scripts (crops, tones, chroma, grain, polar, line, grid, click test); README inside |
| `references/entrega.md` | Phase 11: installer, signing, licences, docs, repository |
| `references/pesquisa/referencias-externas.md` | Links, licences, JUCE/Apple/pluginval details, glossary source |
| `scripts/verificar-dependencias.sh` | Phase 0 |
| `scripts/novo-plugin.sh` + `assets/template-efeito/` | Phase 3 (creates the project) |

## Companion skills (optional)

| Skill | Use | If not installed |
|---|---|---|
| `realistic-hardware-ui` | vintage and clone interfaces (phase 5) | offer the modern interface instead, or build the photoreal panel by hand following the same rules (measure the photo, real-time Three.js, screenshot loop, independent validator) |
| `juce-plugin` | JUCE concepts and API patterns | the template plus `como-construimos.md` |
| `audio-dsp-review`, `audio-numerics-review`, `juce-review` | safety gate (phase 7) | do the same checks by hand with `dsp-por-tipo.md` "Quality checks" and `como-construimos.md` §6 |

The template pins JUCE **8.0.16-security**. Other skills or docs may describe JUCE 9; when an API or CMake detail differs, the template wins. Check uncertain APIs against the JUCE headers in `/tmp/juce-src` or with Context7 for that version.

## Resume first

When the user names an existing plugin, or a project folder for the idea already has a `CLAUDE.md`: read its **Estado** and continue from there. Don't restart the interview.

## How to talk to the user

The user's ears and taste are the spec; your job is to turn them into numbers without making them learn the numbers.

- Portuguese (Brazil), short sentences. No code or logs in chat unless they ask; commands and raw numbers go into the project's CLAUDE.md "Medições", the chat gets the plain result ("o volume ficou igual ligado e desligado, diferença menor que 0,1 dB").
- Use `AskUserQuestion` for decisions: 2–4 options, each with a plain description of what it sounds or looks like, your recommendation first and marked. Up to 3 independent simple questions may go in one call; dependent decisions go one at a time. Never ask what good defaults can decide; decide and say so in one line.
- Before each phase, say in one or two sentences what happens and why; after it, what was done and what you need from them.
- Translate feelings into parameters yourself (table in `conversa.md`), then confirm by letting them hear or see it, not by approving a number.
- Be honest: **you cannot hear**. Tests prove it works; their ears prove it sounds right. Say it early.
- Show a short phase checklist (✓ done, → now, · later) at the end of longer updates.

## Phases

Gates marked **[aprovação]**: show the result and wait for the user's OK.

### 0. Verificar as dependências [aprovação para instalar]
Run `bash <this skill>/scripts/verificar-dependencias.sh`. It only checks: Xcode command line tools, Homebrew, CMake ≥ 3.22, Ninja, Git, Node ≥ 18, Python 3 + measurement libs, Google Chrome, Playwright, pluginval, auval, the JUCE source at `/tmp/juce-src` on `8.0.16-security` (temp folder, wiped on reboot: re-clone when missing), GitHub CLI login, installed DAWs, disk space. Each missing item comes with its install command; exit code = required items missing.

Explain in plain words what's ready, what's missing and what each tool is for ("o CMake é o programa que monta o projeto"). Ask: "Instalar tudo que falta agora (Recomendado)" / "Escolher um por um" / "Eu instalo depois". Install only what they approve, re-run the checker, continue only when no required item is missing. Optional items wait for the phase that needs them. Warn about what they'll see: the Xcode tools dialog and admin password, Homebrew's password prompt, downloading pluginval by hand.

Set expectations once: Mac only (Windows isn't supported in this version); the first build downloads JUCE and takes several minutes; a simple modern effect usually spans a few sessions, a photoreal interface many visual rounds, an instrument more. No DAW: the Standalone app works for a first listen (macOS asks for microphone permission); suggest a trial DAW before phase 9.

Ask where to keep their plugin projects (default `~/Plugins`); call it `PROJETOS`. Each plugin gets its own folder there.

### 1. Entender a ideia
First ask **under which company the plugin is published**: the company name exactly as it should appear in the DAW (or their own name), and optionally a site, an accent colour and a logo. It sets the identity everywhere:

| Item | Rule |
|---|---|
| Company name (`COMPANY_NAME`) | as given |
| Manufacturer code | 4 characters from the company name, first letter uppercase, not all lowercase (Apple reserves those), e.g. "Sonora Labs" → `Snrl`; reuse the same code for all their plugins |
| Bundle prefix | `com.<empresa-sem-espaços>` or their domain reversed |
| Plugin code | 4 characters, pattern `Xxxx`, unique among their plugins |
| Interface signature and accent | their name and colour |
| Repository (only if asked) | their own GitHub account or organisation |

Then interview with the question bank in `conversa.md`. You need, in plain terms: what it does and for what (voz, bateria, master, synth…); **effect or instrument**; 1–3 references (songs, plugins, hardware — targets only, never named in the product); the 3–10 things to control by hand, or "you choose"; where it's used (mix, master, live); for dynamics/ducking ideas, whether another track should drive it (**sidechain**); a plugin name (offer options in their style).

### 2. Escolher a interface
1. **Moderna** — clean dark panel from the template (knobs, meter, preset bar), recoloured with their brand. Fastest and proven end to end.
2. **Vintage realista (desenho original)** — photorealistic hardware panel in real-time Three.js.
3. **Clonar um equipamento** — from their photo, faithful, with a fictitious maker and model (say this rule up front).

For 2 and 3, say honestly that wiring a photoreal panel into the plugin costs extra rounds, and agree where presets live (e.g. a slim preset strip under the panel, approved as part of the design).

Also for 2 and 3, decide early (`references/ui-fotorrealista.md` §1):
- **Knob view**: straight-on or seen from above (offset cap, knurled side showing), with a crop of the reference. One owner approved straight knobs, then switched to the top view: before changing an approved look, commit + tag it.
- **Whose reference is it?** If the image is the user's own (e.g. AI-generated), its brand/logo may be copied exactly; the fictitious-brand rule is for third-party gear. Ask.
- AI-generated 3D models (Tripo etc.) are one fused mesh: no moving parts. Prefer procedural, or the image as background plus animated 3D parts.

**Always ask the aging question for 2 and 3** (`AskUserQuestion`, ask it in the same call as the preset-strip decision, never skip it, never assume): "Quer efeito de equipamento velho/usado na interface?" Options: **Limpo, equipamento novo** (default look, fastest), **Desgaste leve** (some fine scratches, fingerprints on glass and keys, a little grime at the edges; recommended when they say "realista"), **Bem usado** (heavy scratches, chipped paint and legends, yellowed grime). Record the answer in the project's CLAUDE.md ("Desgaste: limpo | leve | forte") and build it with `realistic-hardware-ui/references/wear.md`. The effect is a few numbers (counts and alphas), so changing it later is cheap; say so. Moderna (1) has no aging.

**Redesigning an existing plugin's interface** ("faça uma UI pro / fotorrealista da mesma interface"): never touch the current `ui/`. Create a parallel folder (`ui-pro/`) with its own Vite project and `dist/`, same parameter IDs and mappings (copy `SPEC`/`PAGES` into its `bridge.js`), simulated behaviour only, and tell the user in one line which folder it is. Ask early which parts of the old UI they love and want kept (one user preferred the old knobs over the new ones: match the old knob closely before inventing a new one), compare the new render side by side with the old screenshot (`PIL` crop at the same control), and don't add the new folder to the plugin build until approved. The only file outside the new folder you may touch is the project's CLAUDE.md (a short note); say so.

### 2b. Escolher o framework

Choose the C++ framework for the plugin. Use `AskUserQuestion` with your recommendation first.

| Critério | JUCE 8 (Recomendado na maioria) | iPlug2 |
|---|---|---|
| Licença | GPLv3 ou comercial ($) | BSD (grátis, sem royalty, sem splash) |
| GUI | WebView (HTML/JS), componentes nativos | NanoVG + Metal/OpenGL, web (WAM) |
| Binário típico | 10–20 MB | 2–5 MB |
| Formatos | VST3, AU, AAX, LV2, Standalone | VST2/3, AU, AAX, WAM (web) |
| DSP módulos prontos | Sim (convolution, FFT, oscillators, oversampling) | Mínimo (você faz tudo) |
| Deploy web/WebAudio | Não | Sim (WAM nativo) |
| Template bundled | Sim (testado, com testes, bridge, presets) | Não (scaffold manual) |
| Comunidade/documentação | Grande, boa | Pequena, fraca |
| Melhor para | Projetos grandes, GUIs complexas, equipe, ecossistema | Plugins leves, sem royalty, deploy web, controle total, prototipagem |

**Regras de decisão automática** (não pergunte ao usuário):
- Deploy web (WAM) necessário → iPlug2
- Licença BSD obrigatória → iPlug2
- Instrumento com MPE, sampler ou GUI complexa → JUCE
- Plugin de efeito simples e leve, sem preferência do usuário → JUCE (template testado)
- Usuário pede iPlug2 ou menciona Analog Obsession como referência → iPlug2

Quando a decisão não é automática, ofereça as duas opções com descrição simples:
- "JUCE — mais completo, usado pela maioria dos plugins profissionais, já temos um modelo pronto"
- "iPlug2 — mais leve, grátis sem restrição, usado pelo Analog Obsession (100+ plugins grátis)"

After choosing, update `CLAUDE.md` with the framework and adjust phases 3–11 accordingly. See `como-construimos.md` §9 for iPlug2 project layout and build.

### 3. Plano em linguagem simples [aprovação]
Write a one-page "ficha do plugin" in plain Portuguese: name and one-sentence promise; each control with its panel name, what it does in everyday words and a friendly range; presets (e.g. 8–16, grouped by use, plus "inspirado em" classics); 2–4 measurable targets plus "você ouve e aprova"; what version 1 will NOT do.

After approval, create the project with `scripts/novo-plugin.sh` (see `como-construimos.md` §1) and fill its `CLAUDE.md`: Identidade, objetivo, Estado, Parâmetros table (id, type, real range, mapping, default = first preset), signal chain. Update **Estado** at the end of every phase from now on; it's what lets a later session resume.

### 4. Pesquisa técnica
Read `dsp-por-tipo.md` for the type and the matching sections of `conhecimento-dsp.md`; check references and licences in `pesquisa/referencias-externas.md`. MIT/BSD code may be adapted with notice; GPL/AGPL/unlicensed is study-only. Write numeric choices with their source or "escolha de projeto" in CLAUDE.md. Tell the user in two lines what approach you chose and why it suits their sound.

### 5. Protótipo da interface no navegador [aprovação]
For photoreal interfaces the review routine (types of review, how to brief the validator subagent and judge its answer, what works and what doesn't, pre-show checklist) is `realistic-hardware-ui/references/review.md`; ask the user narrow questions and open the page in Chrome for them.
Build the UI first, with simulated behaviour and all presets.
- **Moderna**: edit the template's `ui/index.html` (plain HTML/CSS/JS, no build step): controls, presets, colours, signature. Open it directly (`open ui/index.html`).
- **Vintage / clone**: follow `realistic-hardware-ui`, including its required independent validator subagent, plus `references/ui-fotorrealista.md` so v1 already ships at final quality:
  - Textures fine and soft (brushing almost sub-pixel, visible only in the highlight); coarse grain reads as "grotesque". Wood is the exception: drawn cathedral grain.
  - Real 3D relief (facets, chamfers, steps, visible sides), never rings or crosses painted on top; shadows blurred, at the light angle measured on the reference, short contact shadows, part-on-part shadows, per-plate light falloff.
  - Neutral environment, warmth only in the lights; measure chroma (`scripts/foto/chroma-probe.mjs`), not just luminance.
  - Rounds after v1 are a **validate → fix loop** (`ui-fotorrealista.md` §11): a fresh validator subagent measures EVERYTHING that still differs (geometry, lighting, shadow, angle, texture, reflection), ranked by visual weight, plus regressions against the previous version; then one fixer subagent corrects that list; then a new validator. Don't plan rounds by fixed themes (geometry, then light, then texture): one owner rejected that. Subagents run on `model: "sonnet"` when the owner asks for it. 3x side-by-side crops every step (`scripts/foto/compare.mjs`); the user's crops are the truth for that element; one subagent at a time.
  - Open every finished version for the owner without being asked: `open -a "Google Chrome" dist/index.html` plus the `side-by-side.png`, and warn when a fixer is still rebuilding `dist/`.
  - Render on demand from v1: pause when hidden (`visibilitychange`), cap ~30 fps, redraw only when something changed. A 60 fps idle loop overheated the user's Mac.
- **Effect**: simulated signal and meter. **Instrument**: an on-screen keyboard playing a WebAudio test voice, or visual-only, agreed with the user.
Screenshot every change (headless Chrome via Playwright), show it, iterate until approved. The UI's parameter table is the contract the plugin mirrors.

### 6. Construir o plugin
From the template: header-only JUCE-free DSP engine in `Source/dsp/Engine.h`, `Parameters.h` mirroring the UI table, processor, WebView editor with relays and attachments, meter event at 30 Hz, the `matches()` rule (never re-apply a preset over the host's restored state). Instruments, sidechain and photoreal wiring: the extension recipes in `como-construimos.md`.

For larger plugins delegate per area (DSP engine / editor + bridge / tests) to builder subagents with precise briefs; you orchestrate, integrate and review.

### 7. Revisão de segurança do áudio (barreira)
Run, in order, on the processor and every DSP file it calls (name the entry point: "audio thread = `processBlock` in `Source/PluginProcessor.cpp`"): `audio-dsp-review` → `audio-numerics-review` → `juce-review` (or the manual fallbacks). Then the checks they don't cover: aliasing of non-linear stages, parameter smoothing, latency reported = measured and constant, bypass crossfade with latency-delayed dry; for instruments, voice stealing, note-off and tails, all-notes-off. Critical findings block phase 8; fix and re-review. Re-run after UI/bridge changes. Tell the user only what's true ("revisei: não trava a DAW, não faz ruído parado, não estoura no extremo").

### 8. Testes automáticos
Command block and contents in `validacao-e-calibracao.md` §1: DSP tests, processor tests (they read the UI text), `auval`, `pluginval` level 10. Report green/red in plain words.

### 9. Ouvir com o usuário [aprovação]
The build installs into `~/Library/Audio/Plug-Ins` (don't run the .pkg yet). Guide them: quit and reopen the DAW, rescan, insert on a track — a MIDI track with a clip or keyboard for instruments; sidechain routing for their DAW. Follow the listening script in `validacao-e-calibracao.md` §3, ask simple questions, log in `docs/AUDICAO.md`, render comparison WAVs when useful.

### 10. Calibrar
Measure against targets (`validacao-e-calibracao.md` §4, `conhecimento-dsp.md`), compare with the references and their notes, change **one thing per round**, re-measure, let them listen again. Calibrate presets by measurement and with real music. Loop 9–10 until they're happy.

### 11. Entregar
Finalise CLAUDE.md (Estado honest, Medições with commands) and README, build the installer, explain signing/notarization and the JUCE licence in plain words if they'll share or sell it, and only when asked: commit and a private repository in their account. See `entrega.md`.

## Quando algo dá errado

- **Build/test failures** are your job: read the log, fix, rebuild. Tell the user one plain line ("o compilador reclamou de uma coisa minha; já corrigi"), not the log. After 3 failed attempts on the same problem, explain the blocker simply and offer options (simplify the feature, try another approach, pause).
- **The user changes their mind**: welcome it, state the cost in plain words (changing the interface style after approval redoes phase 5; a new control means UI + plugin + tests), update the ficha and CLAUDE.md, re-open the matching gate. Parameter IDs can change freely until the first DAW session is saved; after that, add new IDs instead of renaming.
- **Something sounds wrong** but tests pass: believe the ears, reproduce it with a render or a measurement, then fix.
- **"Parece fuzz / distorce demais / precisa ser sutil"** on a saturator: the drive was calibrated too low in level. Re-measure THD at −1 dBFS (mastered music), soften the curve (tanh with small bias), add pre/de-emphasis and round only the added harmonics, re-match the level; recipe in `conhecimento-dsp.md` §1. Users expect subtle by default.

## Rules that save rounds

- Interface first, approved before any C++; it becomes the contract.
- Parameter IDs, types, ranges and defaults identical in UI and APVTS; defaults = first preset.
- Effects: neutral settings and mix 0 return the input bit for bit; bypass returns it bit-exact after the reported latency; output never depends on the host's block size.
- Never re-apply a preset when the plugin UI opens inside a host; detect it by values (`matches()`).
- Latency: zero when possible. It MAY change per oversampling/quality mode (e.g. `XSatEngine`: 0/32/48 samples), constant within a mode; always report it to the host (`setLatencySamples`, message thread) and keep the dry path delayed by the same amount. The control that changes it is not automatable (`como-construimos.md` §6).
- No allocation, locks, file I/O or `juce::String` on the audio thread; parameter pointers cached in the constructor.
- Every visual change checked with a screenshot; every number traceable to the command that produced it (in CLAUDE.md).
- No third-party brand names, logos or copied presets in the product.
- Commit and push only when the user asks.
