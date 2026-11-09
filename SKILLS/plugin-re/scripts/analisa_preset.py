#!/usr/bin/env python3
"""Forense de arquivo de preset/estado de plugin (.fxb/.fxp/.vstpreset/.aupreset/blobs): descobre o formato.

Passos: assinatura (VST2 FBCh/FPCh/CcnK, VST3 'VST3'+lista de chunks, plist, JSON/XML), entropia,
streams zlib embutidos (e descompressão), strings legíveis, plausibilidade de float32 (vetor de params 0..1?)
e do uint32. Não decodifica sozinho o chunk opaco: aponta onde olhar. Ver references/ui-e-presets.md.
Uso: analisa_preset.py arquivo [--out dir]   (grava os blobs descomprimidos em <out>/)
"""
import argparse, collections, math, os, plistlib, re, struct, sys, zlib


def entropia(b):
    if not b:
        return 0.0
    c = collections.Counter(b); n = len(b)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def strings(b, minimo=5, maximo=25):
    return [m.decode() for m in re.findall(rb"[\x20-\x7e]{%d,}" % minimo, b)][:maximo]


def floats_plausiveis(b):
    # fração de float32 (LE e BE) finitos em [0,1]: vetor de parâmetros normalizados parece ~100 % em [0,1]
    out = {}
    n = len(b) // 4
    if n == 0:
        return out
    for nome, fmt in (("LE", "<f"), ("BE", ">f")):
        k = 0
        for i in range(0, min(n, 4000) * 4, 4):
            v = struct.unpack(fmt, b[i:i + 4])[0]
            if v == v and 0.0 <= v <= 1.0:
                k += 1
        out[nome] = round(k / min(n, 4000), 3)
    return out


def procura_zlib(b):
    achados = []
    for m in re.finditer(rb"\x78[\x01\x5e\x9c\xda]", b):
        try:
            d = zlib.decompressobj().decompress(b[m.start():])
            if len(d) > 16:
                achados.append((m.start(), d))
        except Exception:
            pass
    return achados


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo"); ap.add_argument("--out")
    a = ap.parse_args()
    b = open(a.arquivo, "rb").read()
    print(f"arquivo: {a.arquivo}  ({len(b)} B)  entropia {entropia(b):.2f}/8")
    print("primeiros 32 B:", b[:32].hex(" "), "|", repr(b[:32]))
    if b[:4] == b"CcnK":
        magic = b[8:12]
        fx = {b"FBCh": "banco com chunk opaco", b"FPCh": "programa com chunk opaco", b"FxBk": "banco de parâmetros", b"FxCk": "programa de parâmetros"}.get(magic, "?")
        ver, fxid, fver, n = struct.unpack(">4i", b[12:28])
        print(f"VST2: {magic.decode()} ({fx}) formato v{ver}, fxID={b[16:20]!r}, fxVersion={fver}, nº {'programas' if magic[:2]==b'FB' or magic==b'FxBk' else 'params'}={n}")
        if magic == b"FBCh":
            tam = struct.unpack(">i", b[156:160])[0]
            print(f"  chunk opaco: {tam} B a partir de 160; assinatura {b[160:168]!r}")
    elif b[:4] == b"VST3":
        ver = struct.unpack("<i", b[4:8])[0]; cid = b[8:40]; off = struct.unpack("<q", b[40:48])[0]
        print(f"VST3 preset v{ver}, classID={cid!r}, lista de chunks em {off}")
        if b[off:off + 4] == b"List":
            n = struct.unpack("<i", b[off + 4:off + 8])[0]
            for i in range(n):
                tag, o, s = struct.unpack("<4sqq", b[off + 8 + i * 20:off + 8 + (i + 1) * 20])
                print(f"  chunk {tag!r}: offset {o}, {s} B")
    else:
        for nome, fn in (("plist", lambda: plistlib.loads(b)),):
            try:
                print(f"{nome}: {str(fn())[:300]}"); break
            except Exception:
                pass
        if b[:1] in (b"{", b"["):
            print("parece JSON"); 
        if b[:5] == b"<?xml" or b[:1] == b"<":
            print("parece XML")
    print("strings:", strings(b))
    print("floats em [0,1] (fração) no arquivo inteiro:", floats_plausiveis(b))
    zs = procura_zlib(b)
    for i, (off, d) in enumerate(zs[:6]):
        print(f"zlib @ {off}: {len(d)} B descomprimidos, entropia {entropia(d):.2f}, strings {strings(d, 5, 6)}, floats {floats_plausiveis(d)}")
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            open(os.path.join(a.out, f"zlib_{off}.bin"), "wb").write(d)
    if not zs:
        print("nenhum stream zlib; se a entropia for ~8 pode ser cifrado/compactado por outro método")


if __name__ == "__main__":
    main()
