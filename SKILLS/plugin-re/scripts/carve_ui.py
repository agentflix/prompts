"""Carve embedded UI images (PNG/JPEG/WebP) from a Mach-O (JUCE BinaryData).
Dedup by content hash; report dimensions. Usage: carve_ui.py <binary> <outdir>"""
import sys as _s
if any(a in ("-h", "--help") for a in _s.argv[1:]):
    print(__doc__); raise SystemExit(0)
import sys, os, struct, hashlib, zlib

binpath, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
data = open(binpath, "rb").read()
print(f"scan {binpath}  ({len(data)} bytes)")

def png_dims(b):
    # IHDR at offset 16: width,height big-endian
    try:
        if b[12:16]==b"IHDR":
            w,h=struct.unpack(">II", b[16:24]); return w,h
    except Exception: pass
    return None

found=[]
# --- PNG ---
PNG_SIG=b"\x89PNG\r\n\x1a\n"; IEND=b"IEND\xaeB`\x82"
i=0
while True:
    i=data.find(PNG_SIG,i)
    if i<0: break
    j=data.find(IEND,i)
    if j<0: break
    blob=data[i:j+8]
    found.append(("png",i,blob))
    i=j+8
# --- JPEG ---
i=0
while True:
    i=data.find(b"\xff\xd8\xff",i)
    if i<0: break
    j=data.find(b"\xff\xd9",i)
    if j<0: break
    blob=data[i:j+2]
    if 200<len(blob)<30_000_000: found.append(("jpg",i,blob))
    i=j+2
# --- WebP ---
i=0
while True:
    i=data.find(b"RIFF",i)
    if i<0: break
    if data[i+8:i+12]==b"WEBP":
        sz=struct.unpack("<I",data[i+4:i+8])[0]+8
        found.append(("webp",i,data[i:i+sz]))
        i+=sz
    else: i+=4

seen=set(); kept=[]
for kind,off,blob in found:
    h=hashlib.sha1(blob).hexdigest()[:10]
    if h in seen: continue
    seen.add(h)
    dims=png_dims(blob) if kind=="png" else None
    name=f"{kind}_{off:08x}_{h}"
    if dims: name+=f"_{dims[0]}x{dims[1]}"
    name+="."+kind
    open(os.path.join(outdir,name),"wb").write(blob)
    kept.append((kind,off,len(blob),dims,name))

kept.sort(key=lambda r:-(r[3][0]*r[3][1] if r[3] else r[2]))
print(f"\n{len(found)} brutos, {len(kept)} unicos salvos:")
for kind,off,sz,dims,name in kept:
    d=f"{dims[0]}x{dims[1]}" if dims else "?"
    print(f"  {kind:4} @0x{off:08x} {sz:>9} B  {d:>12}  {name}")
