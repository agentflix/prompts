#!/bin/bash
# Gera dist/<NOME>-<versão>.pkg, que instala o VST3 e o AU em /Library/Audio/Plug-Ins.
# Uso: scripts/make-installer.sh    (compila o que faltar antes)
# Nome, versão e bundle id vêm do CMakeLists.txt.
# Observação: o pacote sai sem assinatura de Developer ID e sem notarização;
# para distribuir a terceiros, assine com productsign e notarize com notarytool.
set -euo pipefail
cd "$(dirname "$0")/.."

cmake_var() { grep -m1 -E "^set\($1 " CMakeLists.txt | sed -E 's/^[^"]*"([^"]*)".*/\1/'; }
NAME=$(cmake_var PLUGIN_NAME)
ID=$(cmake_var PLUGIN_ID)
VERSION=$(cmake_var PLUGIN_VERSION)
IDENT="$(cmake_var BUNDLE_PREFIX).$ID"
ART="build/${NAME}_artefacts/Release"

[ -d build ] || cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build --target "${NAME}_VST3" "${NAME}_AU"

W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/vst3" "$W/au" dist
cp -R "$ART/VST3/$NAME.vst3"    "$W/vst3/"
cp -R "$ART/AU/$NAME.component" "$W/au/"

pkgbuild --root "$W/vst3" --identifier "$IDENT.vst3" --version "$VERSION" --install-location /Library/Audio/Plug-Ins/VST3       "$W/vst3.pkg"
pkgbuild --root "$W/au"   --identifier "$IDENT.au"   --version "$VERSION" --install-location /Library/Audio/Plug-Ins/Components "$W/au.pkg"

cat > "$W/dist.xml" <<XML
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
  <title>$NAME $VERSION</title>
  <options customize="allow" hostArchitectures="arm64"/>
  <choices-outline><line choice="vst3"/><line choice="au"/></choices-outline>
  <choice id="vst3" title="VST3" description="Instala em /Library/Audio/Plug-Ins/VST3"><pkg-ref id="$IDENT.vst3"/></choice>
  <choice id="au" title="Audio Unit (AU)" description="Instala em /Library/Audio/Plug-Ins/Components"><pkg-ref id="$IDENT.au"/></choice>
  <pkg-ref id="$IDENT.vst3">vst3.pkg</pkg-ref>
  <pkg-ref id="$IDENT.au">au.pkg</pkg-ref>
</installer-gui-script>
XML

productbuild --distribution "$W/dist.xml" --package-path "$W" "dist/$NAME-$VERSION.pkg"
echo "Pronto: dist/$NAME-$VERSION.pkg"
