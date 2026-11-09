#!/usr/bin/env python3
"""Decodifica bancos .fxb do Sylenth1 (formato FBCh / chunk 'syl1') para JSONL.
import sys as _s
if any(a in ("-h", "--help") for a in _s.argv[1:]):
    print(__doc__); raise SystemExit(0)
Cada preset: nome + 244 params normalizados (0..1), na ordem dos parâmetros do VST3.
Uso: python3 decode_sylenth_fxb.py saida.jsonl banco1.fxb [banco2.fxb ...]
Mapa de índice->nome: precisa dos nomes dos params (carregue o VST3 uma vez via pedalboard,
ou use a lista salva PK.json). Sem a lista, os params saem como p0..p243."""
import struct, zlib, json, os, sys

def inner_of(data: bytes):
    if data[8:12] != b'FBCh':            # fxMagic
        return None
    chunk = data[160:]                   # header fxBank = 160 bytes
    if chunk[:4] != b'1lys':             # tag 'syl1' em little-endian
        return None
    if chunk[8:10] in (b'\x78\x9c', b'\x78\x5e', b'\x78\xda'):   # zlib (bancos de fábrica)
        try: return zlib.decompress(chunk[8:])
        except Exception: return None
    return chunk                         # bancos comerciais: já descomprimido

def decode(data: bytes, pk=None):
    inner = inner_of(data)
    if not inner or inner[:4] != b'1lys':
        return []
    nProg, nParam = struct.unpack('<II', inner[8:16])   # header: syl1(4)+ver(4)+nProg(4)+nParam(4)
    if not (0 < nParam < 400 and 0 < nProg < 4000):
        return []
    body = inner[16:]
    rec = nParam * 4 + 36                 # 244 floats + 36 bytes de nome (4 nulos + 32 do nome)
    out = []
    for i in range(min(nProg, len(body)//rec)):
        r = body[i*rec:(i+1)*rec]
        f = struct.unpack('<%df' % nParam, r[:nParam*4])
        name = r[nParam*4+4:].split(b'\x00')[0].decode('latin-1', 'replace').strip()
        if not name or name == 'Init' or name.startswith(('=/', 'www.', 'over ', 'The full')):
            continue
        # f[0] é um valor líder (não é param do VST3); f[i+1] = param i da ordem do VST3
        if pk:
            params = {pk[j-1]: round(f[j], 5) for j in range(1, min(nParam, len(pk)+1))}
        else:
            params = {f'p{j-1}': round(f[j], 5) for j in range(1, nParam)}
        out.append({'name': name, 'cat': name.split()[0] if name.split() else '',
                    'nParam': nParam, 'params': params})
    return out

if __name__ == '__main__':
    out_path, banks = sys.argv[1], sys.argv[2:]
    pk = None
    pkf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'PK.json')
    if os.path.exists(pkf):
        pk = json.load(open(pkf))
    total = 0
    with open(out_path, 'w') as w:
        for b in banks:
            try: rows = decode(open(b, 'rb').read(), pk)
            except Exception: continue
            for r in rows:
                r['bank'] = os.path.basename(b)
                w.write(json.dumps(r, ensure_ascii=False) + '\n')
            total += len(rows)
    print('presets:', total, '->', out_path)
