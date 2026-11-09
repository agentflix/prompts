#!/usr/bin/env python3
"""Compara o dump de parâmetros/buses de dois plugins (saída de paramdump).

Uso:
  paramdump "/Library/Audio/Plug-Ins/VST3/Spectrum 2.vst3" > ref.txt
  paramdump "$HOME/Library/Audio/Plug-Ins/VST3/Vitral.vst3" > novo.txt
  python3 compare.py ref.txt novo.txt
"""
import re, sys

def parse(path):
    lines = open(path).read().splitlines()
    buses = sorted(l.strip() for l in lines if ' bus ' in l or 'suporta' in l)
    params = {}
    for l in lines:
        m = re.match(r'\s+(\S+) \| (.*?) \| default=([\d.e+-]+) \((.*?)\) \| steps=(\d+) \| discrete=(\d) \| (.*)', l)
        if m:
            steps = 'cont' if m.group(5) == '2147483647' else m.group(5)
            params[m.group(2).lower()] = (m.group(4).strip(), steps, m.group(7).strip())
    return buses, params

ref_b, ref_p = parse(sys.argv[1])
new_b, new_p = parse(sys.argv[2])
print("buses:", "iguais" if ref_b == new_b else "DIFERENTES")
for x in sorted(set(ref_b) ^ set(new_b)): print("   ", x)
bad = 0
for k in sorted(set(ref_p) | set(new_p)):
    if ref_p.get(k) == new_p.get(k): print("OK  ", k)
    else: bad += 1; print("DIFF", k, "| ref =", ref_p.get(k), "| novo =", new_p.get(k))
sys.exit(1 if bad else 0)
