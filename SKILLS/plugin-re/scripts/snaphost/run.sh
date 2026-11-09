#!/bin/sh
# uso: run.sh <saida/> <cenario> [param=texto ...]   (plugin = $PLUGIN, padrão Spectrum 2)
D=$(cd "$(dirname "$0")" && pwd); O=$1; shift
rm -rf "$O"; perl -e 'alarm 120; exec @ARGV' "$D/build/SnapHost_artefacts/Release/SnapHost.app/Contents/MacOS/SnapHost" "${PLUGIN:-/Library/Audio/Plug-Ins/VST3/Spectrum 2.vst3}" "$O" "$@"
