#!/usr/bin/env bash
# Verifica as ferramentas necessárias para criar, testar e calibrar um plugin (macOS).
# Não instala nada: só mostra o que está OK, o que falta e o comando sugerido para instalar.
#   bash verificar-dependencias.sh            # tabela legível
#   bash verificar-dependencias.sh --resumo   # uma linha por item: STATUS|item|detalhe|comando
# Código de saída = número de itens OBRIGATÓRIOS faltando.

set -u
RESUMO=0; [ "${1:-}" = "--resumo" ] && RESUMO=1
JUCE_TAG="${JUCE_TAG:-8.0.16-security}"
JUCE_DIR="${JUCE_DIR:-/tmp/juce-src}"
faltando=0

linha() {  # status item detalhe comando obrigatorio(1/0)
  local st="$1" item="$2" det="$3" cmd="$4" obr="$5"
  [ "$st" != "OK" ] && [ "$obr" = "1" ] && faltando=$((faltando + 1))
  if [ $RESUMO = 1 ]; then echo "$st|$item|$det|$cmd"; return; fi
  local tag; case "$st" in OK) tag="✓";; ANTIGO) tag="!";; *) tag="✗";; esac
  local o; [ "$obr" = "1" ] && o="obrigatório" || o="opcional"
  printf "%s %-26s %-11s %s\n" "$tag" "$item" "($o)" "$det"
  [ "$st" != "OK" ] && [ -n "$cmd" ] && printf "    → instalar: %s\n" "$cmd"
}

ver_ge() {  # ver_ge atual minima  -> 0 se atual >= minima
  [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]
}

[ "$(uname)" = "Darwin" ] || { echo "Este verificador é para macOS."; exit 1; }
[ $RESUMO = 1 ] || echo "Verificando ferramentas para criar plugins (macOS $(sw_vers -productVersion), $(uname -m))"; [ $RESUMO = 1 ] || echo

# Xcode command line tools (compilador, codesign, auval)
if xcode-select -p >/dev/null 2>&1 && command -v clang++ >/dev/null; then
  linha OK "Xcode Command Line Tools" "$(clang++ --version | head -1)" "" 1
else
  linha FALTA "Xcode Command Line Tools" "compilador da Apple" "xcode-select --install" 1
fi

# Homebrew (para instalar o resto)
if command -v brew >/dev/null; then linha OK "Homebrew" "$(brew --version | head -1)" "" 0
else linha FALTA "Homebrew" "gerenciador de pacotes" '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"' 0; fi

# CMake >= 3.22
if command -v cmake >/dev/null; then
  v=$(cmake --version | head -1 | awk '{print $3}')
  if ver_ge "$v" 3.22; then linha OK "CMake" "$v" "" 1; else linha ANTIGO "CMake" "$v (precisa ≥ 3.22)" "brew upgrade cmake" 1; fi
else linha FALTA "CMake" "monta o projeto" "brew install cmake" 1; fi

# Ninja
if command -v ninja >/dev/null; then linha OK "Ninja" "$(ninja --version)" "" 1
else linha FALTA "Ninja" "compila rápido" "brew install ninja" 1; fi

# Git
if command -v git >/dev/null; then linha OK "Git" "$(git --version | awk '{print $3}')" "" 1
else linha FALTA "Git" "versões do código" "xcode-select --install (ou brew install git)" 1; fi

# Node + npm >= 18 (interface: Vite/Svelte; scripts de screenshot)
if command -v node >/dev/null; then
  v=$(node --version | tr -d v)
  if ver_ge "$v" 18; then linha OK "Node.js" "$v" "" 1; else linha ANTIGO "Node.js" "$v (precisa ≥ 18)" "brew upgrade node" 1; fi
else linha FALTA "Node.js" "monta a interface" "brew install node" 1; fi

# Python 3 (medições e calibração)
if command -v python3 >/dev/null; then
  linha OK "Python 3" "$(python3 --version | awk '{print $2}')" "" 1
  miss=""
  for m in numpy scipy soundfile pyloudnorm; do python3 -c "import $m" 2>/dev/null || miss="$miss $m"; done
  if [ -z "$miss" ]; then linha OK "Python: numpy/scipy/soundfile/pyloudnorm" "instalados" "" 0
  else linha FALTA "Python: libs de medição" "faltam:$miss" "python3 -m venv tools/.venv && tools/.venv/bin/pip install$miss" 0; fi
else linha FALTA "Python 3" "medições" "brew install python" 1; fi

# Google Chrome (screenshots headless da interface)
if [ -d "/Applications/Google Chrome.app" ]; then linha OK "Google Chrome" "para screenshots da interface" "" 1
else linha FALTA "Google Chrome" "screenshots da interface" "brew install --cask google-chrome" 1; fi

# Playwright (usado pelos scripts de screenshot das skills, ex.: scripts/foto)
# Os scripts resolvem o playwright A PARTIR DO PROJETO DA UI (node_modules dela); um global não é visto pelo Node.
# PLAYWRIGHT_DIR (ou UI_DIR) = pasta da UI; padrão = pasta atual.
PW_DIR="${PLAYWRIGHT_DIR:-${UI_DIR:-$PWD}}"
if command -v node >/dev/null && (cd "$PW_DIR" 2>/dev/null && node -e "require.resolve('playwright')" >/dev/null 2>&1); then
  linha OK "Playwright" "resolvível em $PW_DIR" "" 0
elif npm ls -g playwright >/dev/null 2>&1; then
  linha FALTA "Playwright (no projeto)" "só global; os scripts não o enxergam a partir de $PW_DIR" "cd <pasta da UI> && npm i -D playwright" 0
else linha FALTA "Playwright" "automatiza o Chrome nos testes visuais" "cd <pasta da UI> && npm i -D playwright" 0; fi

# pluginval
PV=""; for p in /Applications/pluginval.app /Applications/Pluginval.app; do [ -d "$p" ] && PV="$p"; done
if [ -n "$PV" ]; then linha OK "pluginval" "$PV" "" 1
else linha FALTA "pluginval" "testa o plugin como uma DAW" "baixar em https://github.com/Tracktion/pluginval/releases e arrastar para /Applications" 1; fi

# auval (vem com o macOS)
if command -v auval >/dev/null; then linha OK "auval" "validador AU da Apple" "" 1
else linha FALTA "auval" "validador AU" "vem com o macOS / Xcode CLT" 1; fi

# JUCE (fonte local para builds rápidos)
if [ -d "$JUCE_DIR/.git" ]; then
  t=$(git -C "$JUCE_DIR" describe --tags --exact-match 2>/dev/null || git -C "$JUCE_DIR" rev-parse --short HEAD)
  if [ "$t" = "$JUCE_TAG" ]; then linha OK "JUCE ($JUCE_TAG)" "$JUCE_DIR" "" 1
  else linha ANTIGO "JUCE" "$JUCE_DIR está em $t, esperado $JUCE_TAG" "git -C $JUCE_DIR fetch --depth 1 origin tag $JUCE_TAG && git -C $JUCE_DIR checkout $JUCE_TAG" 1; fi
else linha FALTA "JUCE ($JUCE_TAG)" "biblioteca dos plugins" "git clone --depth 1 --branch $JUCE_TAG https://github.com/juce-framework/JUCE.git $JUCE_DIR" 1; fi

# GitHub CLI (só para criar repositório)
if command -v gh >/dev/null; then
  if gh auth status >/dev/null 2>&1; then linha OK "GitHub CLI" "logado" "" 0
  else linha FALTA "GitHub CLI (login)" "instalado, sem login" "gh auth login" 0; fi
else linha FALTA "GitHub CLI" "criar repositório" "brew install gh && gh auth login" 0; fi

# DAW (para ouvir)
daws=""
shopt -s nullglob
for a in /Applications/Ableton\ Live*.app /Applications/Logic\ Pro*.app /Applications/REAPER*.app /Applications/FL\ Studio*.app \
         /Applications/Studio\ One*.app /Applications/Bitwig\ Studio*.app /Applications/Cubase*.app /Applications/GarageBand.app; do
  daws="$daws, $(basename "$a" .app)"
done
shopt -u nullglob
if [ -n "$daws" ]; then linha OK "DAW" "${daws#, }" "" 0
else linha FALTA "DAW" "nenhuma encontrada; dá para testar no app Standalone" "REAPER tem teste grátis: https://www.reaper.fm" 0; fi

# Espaço em disco (JUCE + builds ~ 5 GB)
livre=$(df -g "$PWD" | awk 'NR==2{print $4}')
if [ "${livre:-0}" -ge 5 ]; then linha OK "Espaço em disco" "${livre} GB livres" "" 1
else linha FALTA "Espaço em disco" "${livre} GB livres (precisa ~5 GB)" "liberar espaço" 1; fi

[ $RESUMO = 1 ] || { echo; [ $faltando = 0 ] && echo "Tudo pronto para começar." || echo "$faltando item(ns) obrigatório(s) faltando."; }
exit $faltando
