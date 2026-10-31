#!/bin/bash
# Recorta a foto em quadrado (rosto no topo) e reduz para 700px. Uso: crop_photo.sh foto-original.jpg foto.jpg
# Funciona no macOS (sips). Se o rosto ficar cortado, ajuste o offset (segundo numero = vertical).
set -e
IN="$1"; OUT="${2:-foto.jpg}"
W=$(sips -g pixelWidth "$IN" | awk '/pixelWidth/{print $2}'); H=$(sips -g pixelHeight "$IN" | awk '/pixelHeight/{print $2}')
SIDE=$(( W < H ? W : H )); [ "$SIDE" -gt 1000 ] && SIDE=1000
sips -c $SIDE $SIDE --cropOffset 60 70 "$IN" --out "$OUT" >/dev/null
sips -Z 700 "$OUT" >/dev/null
echo "Foto pronta: $OUT"
