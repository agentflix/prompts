# Entrega

## Installer (macOS)

`scripts/make-installer.sh` (comes with the template): reads the version from `plugin/CMakeLists.txt`, builds VST3 + AU, `pkgbuild` one component per format (`/Library/Audio/Plug-Ins/VST3`, `/Library/Audio/Plug-Ins/Components`), `productbuild` with a `distribution.xml` (`customize="allow"`, `hostArchitectures="arm64"`), output `dist/<NAME>-<ver>.pkg` (gitignored). Tell the user that dev builds install to `~/Library/...` and the installer to `/Library/...`; keep only one copy or the DAW may load the old one.

Without an Apple Developer ID the installer is unsigned: macOS will warn; fine for personal use. To share or sell:
1. Apple Developer Program (US$ 99/ano), certificates **Developer ID Application** (bundles) and **Developer ID Installer** (pkg).
2. Build with `HARDENED_RUNTIME_ENABLED TRUE`; `codesign --force --options runtime --timestamp --sign "Developer ID Application: …"` each `.vst3`, `.component`, `.app` (nested code first).
3. `productbuild ... --sign "Developer ID Installer: …"`.
4. `xcrun notarytool submit <pkg> --keychain-profile notary --wait`, then `xcrun stapler staple <pkg>`; verify with `spctl -a -vvv -t install`.
Add a release checklist to `docs/RELEASE.md`: gates passed, DAW matrix (automation, freeze/bounce, save/reopen, export, buffers 32–2048, 44.1–96 kHz, multiple instances), CPU, clean-Mac installer test.

Windows (not supported in this version; if ever): `NEEDS_WEBVIEW2 TRUE` in `juce_add_plugin`, VST3 in `C:\Program Files\Common Files\VST3\`, Inno Setup or WiX, Authenticode signing, WebView2 runtime (static loader `JUCE_USE_WIN_WEBVIEW2_WITH_STATIC_LINKING=1`, `withUserDataFolder(temp)`).

## Licences to explain in plain words

- JUCE: sharing or selling a closed-source plugin needs a commercial JUCE licence (or releasing the code under AGPL/GPL). Check current tiers at juce.com before advising.
- Third-party code kept in `THIRD_PARTY_NOTICES.md` with its licence text; no GPL code in a closed plugin.
- No third-party brand names, logos or copied presets in the product.

## Docs and repo

- `CLAUDE.md` (pt-BR) in this format: objetivo, regras (pt-BR, sem commit sem pedido), Estado (Pronto / Falta, honest), Padrão de UI, Estrutura, Comandos, Conceito, Parâmetros table, Regras do DSP, Medições (with commands), Armadilhas, Licença.
- `README.md`: what it is, how to install, how to use, short.
- `docs/AUDICAO.md` with the listening log.
- Git **only when the user asks**: `git init -b main`, `.gitignore` (build/, dist/, audition/, .DS_Store), one commit with a clear message in Portuguese ("feat: plugin <NOME> com interface, DSP, testes e instalador"), then `gh repo create <owner>/<name> --private --source . --remote origin --push`, where owner is the user's own GitHub account or organisation. Confirm owner, name and visibility first. The installer identifiers use the bundle id of the chosen identity (`com.<empresa>.<name>.vst3`).

## Closing message to the user

Plain summary: what the plugin does, where it was installed, how to find it in the DAW, what was tested (numbers), what they approved by listening, what is still open (e.g. signing, more presets, Windows), and how to come back to change something ("é só me pedir 'muda o preset X' ou 'quero um botão de mix'").
