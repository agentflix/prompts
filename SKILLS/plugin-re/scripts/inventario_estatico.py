#!/usr/bin/env python3
"""Inventário estático de um plugin de áudio (.vst3/.component/.clap/Mach-O) no macOS.

Só leitura: lê o binário e o bundle, nunca executa o plugin. Produz relatório
(Markdown no stdout, e com --out também inspect.md + inspect.json) com:
slices/sha256, otool -L, seções Mach-O com entropia, strings relevantes,
tecnologia de UI e conteúdo do bundle.
"""
import argparse, collections, hashlib, json, math, os, plistlib, re, struct, subprocess, sys

MH_MAGIC_64, FAT_MAGIC, FAT_MAGIC_64 = 0xfeedfacf, 0xcafebabe, 0xcafebabf
LC_SEGMENT_64 = 0x19
CPU = {0x01000007: "x86_64", 0x0100000c: "arm64", 0x0200000c: "arm64e"}

UI_TECH = [  # (nome, regex em strings/libs)
    ("JUCE", rb"juce::|JUCE v\d|JuceDemo|juce_"), ("iPlug2/iPlug", rb"IGraphics|iplug::|iPlug2"),
    ("VSTGUI", rb"VSTGUI|CViewContainer|VSTGUI::"), ("Qt", rb"QtCore|QWidget|QApplication"),
    ("WebKit/WebView", rb"WKWebView|WebView2|WebBrowserComponent"),
    ("Metal", rb"MTLDevice|MTKView"), ("OpenGL", rb"NSOpenGL|OpenGL\.framework|glBindTexture"),
    ("Skia", rb"SkCanvas|skia::"), ("NanoVG", rb"nvgBeginFrame|NanoVG"), ("HISE", rb"HISE|hise::"),
    ("CEF/Chromium", rb"libcef|Chromium Embedded"), ("Cocoa nativo", rb"NSView|NSWindow"),
]
LIB_UI = {"WebKit/WebView": ("webkit.framework",), "Metal": ("metal.framework", "metalkit.framework"),
          "OpenGL": ("opengl.framework",), "Qt": ("qtcore",), "CEF/Chromium": ("libcef", "chromium embedded")}
RE_URL = re.compile(rb"https?://[\x21-\x7e]{6,120}")
RE_VER = re.compile(rb"\b\d{1,2}\.\d{1,2}\.\d{1,3}(?:\.\d{1,4})?\b")
RE_ITA = re.compile(rb"(?:_ZTS|\bN(?=\d)|\b(?=\d))[0-9A-Za-z_]{6,120}")


def nome_itanium(b):
    # valida <len><nome> encadeado (nomes qualificados N..E): descarta ruído aleatório
    s = b.decode(errors="ignore")
    if s.startswith("_ZTS"):
        s = s[4:]
    if s.startswith("N"):
        s = s[1:]
    partes, i = [], 0
    while i < len(s) and s[i].isdigit():
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        n = int(s[i:j])
        if n < 3 or j + n > len(s):
            break
        partes.append(s[j:j + n]); i = j + n
    if partes and (i == len(s) or s[i:] in ("E", "") or s[i] in "EI") and sum(len(x) for x in partes) >= 8:
        return "::".join(partes)
    return None
RE_STR = re.compile(rb"[\x20-\x7e]{6,200}")
RE_PARAM = re.compile(rb"^(?:[a-z][a-z0-9]*(?:[_\-.][a-z0-9]+){1,4})$")
PALAVRAS_DSP = (b"cutoff", b"reson", b"drive", b"thresh", b"ratio", b"attack", b"release", b"gain", b"mix",
                b"depth", b"bypass", b"oversampl", b"latency", b"preset", b"tooltip", b"coef", b"biquad",
                b"saturat", b"tanh", b"filter", b"lfo", b"envelope", b"waveform", b"unison", b"detune")


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception as e:  # ferramenta ausente
        return f"(falhou: {e})"


def entropia(buf):
    # entropia de Shannon (bits/byte), amostrando até 4 MB em blocos para ser rápido
    if not buf:
        return 0.0
    if len(buf) > 4_000_000:
        passo = len(buf) // 16
        buf = b"".join(buf[i:i + 250_000] for i in range(0, len(buf), passo))
    c = collections.Counter(buf)
    n = len(buf)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def achar_binario(path):
    # devolve (caminho do Mach-O, bundle ou None)
    if os.path.isfile(path):
        return path, None
    plist = os.path.join(path, "Contents", "Info.plist")
    exe = None
    if os.path.exists(plist):
        with open(plist, "rb") as f:
            exe = plistlib.load(f).get("CFBundleExecutable")
    d = os.path.join(path, "Contents", "MacOS")
    if exe and os.path.exists(os.path.join(d, exe)):
        return os.path.join(d, exe), path
    if os.path.isdir(d) and os.listdir(d):
        return os.path.join(d, sorted(os.listdir(d))[0]), path
    sys.exit(f"sem binário em {path}")


def slices(data):
    # lista (arch, offset, size); aceita fat e thin
    magic = struct.unpack(">I", data[:4])[0]
    if magic in (FAT_MAGIC, FAT_MAGIC_64):
        n = struct.unpack(">I", data[4:8])[0]
        out, off = [], 8
        for _ in range(n):
            if magic == FAT_MAGIC:
                cpu, _, o, s, _ = struct.unpack(">iiIII", data[off:off + 20]); off += 20
            else:
                cpu, _, o, s, _, _ = struct.unpack(">iiQQII", data[off:off + 32]); off += 32
            out.append((CPU.get(cpu & 0xffffffff, hex(cpu)), o, s))
        return out
    cpu = struct.unpack("<i", data[4:8])[0]
    return [(CPU.get(cpu & 0xffffffff, hex(cpu)), 0, len(data))]


def secoes(data, off):
    # parse de LC_SEGMENT_64 -> [(seg, sect, offset_no_slice, size)]
    if struct.unpack("<I", data[off:off + 4])[0] != MH_MAGIC_64:
        return []
    ncmds = struct.unpack("<I", data[off + 16:off + 20])[0]
    p, out = off + 32, []
    for _ in range(ncmds):
        cmd, size = struct.unpack("<II", data[p:p + 8])
        if cmd == LC_SEGMENT_64:
            seg = data[p + 8:p + 24].split(b"\0")[0].decode(errors="replace")
            nsects = struct.unpack("<I", data[p + 64:p + 68])[0]
            q = p + 72
            for _ in range(nsects):
                sn = data[q:q + 16].split(b"\0")[0].decode(errors="replace")
                sz, so = struct.unpack("<QI", data[q + 40:q + 52])
                out.append((seg, sn, so, sz))
                q += 80
        p += size
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin", help="caminho do .vst3/.component/.clap (bundle) ou do Mach-O")
    ap.add_argument("--out", help="pasta de saída (grava inspect.md e inspect.json)")
    ap.add_argument("--max-strings", type=int, default=40, help="máximo de itens por categoria de strings")
    a = ap.parse_args()

    binp, bundle = achar_binario(a.plugin)
    data = open(binp, "rb").read()
    R = {"plugin": os.path.abspath(a.plugin), "binario": binp, "tamanho": len(data)}
    R["lipo"] = sh(["lipo", "-info", binp]).strip()
    sl = []
    for arch, off, size in slices(data):
        sl.append({"arch": arch, "offset": off, "tamanho": size, "sha256": hashlib.sha256(data[off:off + size]).hexdigest()})
    R["slices"] = sl
    libs = [l.split(" (")[0].strip() for l in sh(["otool", "-L", binp]).splitlines()[1:] if l.strip()]
    R["libs"] = libs

    # seções + entropia do slice arm64 (ou o primeiro)
    alvo = next((s for s in sl if s["arch"].startswith("arm64")), sl[0])
    secs = []
    for seg, sn, so, sz in secoes(data, alvo["offset"]):
        buf = data[alvo["offset"] + so: alvo["offset"] + so + sz] if so else b""
        secs.append({"seg": seg, "sect": sn, "tamanho": sz, "entropia": round(entropia(buf), 2) if buf else None})
    R["secoes_slice"] = alvo["arch"]; R["secoes"] = secs

    # strings
    lim = a.max_strings
    todas = RE_STR.findall(data)
    rtti = sorted({n for m in RE_ITA.findall(data) if (n := nome_itanium(m))})
    # RTTI: tira templates do JUCE (ruído) e prefere nomes curtos = classes do fabricante
    proprias = [r for r in rtti if "juce" not in r.lower()]
    R["rtti_juce_total"] = len(rtti) - len(proprias)
    R["rtti"] = proprias[:lim * 2]
    R["urls"] = sorted({u.decode(errors="replace") for u in RE_URL.findall(data)})   # lista completa (arquivo); o terminal mostra resumo
    R["versoes"] = sorted({u.decode() for u in RE_VER.findall(data)})[:lim]
    par = [s.decode() for s in todas if RE_PARAM.match(s) and any(w in s.lower() for w in PALAVRAS_DSP)]
    R["nomes_tipo_parametro"] = sorted(set(par))[:lim * 2]
    msgs = [s.decode() for s in todas if any(w in s.lower() for w in (b"tooltip", b"license", b"licen", b"expired", b"error", b"warning")) and b" " in s]
    R["mensagens"] = sorted(set(msgs))[:lim]
    dsp = [s.decode() for s in todas if any(w in s.lower() for w in (b"sinf", b"tanh", b"biquad", b"coeff", b"fft", b"oversampl", b"convol"))]
    R["pistas_dsp"] = sorted(set(dsp))[:lim]
    joined = b"\n".join(todas[:2_000_000])
    # UI: "linkado" (otool -L) pesa mais que string solta (JUCE traz referências a quase tudo)
    ui = {}
    for n, rx in UI_TECH:
        em_lib = any(re.search(rx, l.encode()) or (k in l.lower()) for l in libs for k in LIB_UI.get(n, ()))
        em_str = bool(re.search(rx, joined))
        if em_lib or em_str:
            ui[n] = "linkado" if em_lib else "strings"
    R["ui"] = [f"{n} ({o})" for n, o in sorted(ui.items(), key=lambda kv: kv[1] != "linkado")]

    # bundle
    if bundle:
        info = {}
        pl = os.path.join(bundle, "Contents", "Info.plist")
        if os.path.exists(pl):
            with open(pl, "rb") as f:
                p = plistlib.load(f)
            for k in ("CFBundleIdentifier", "CFBundleName", "CFBundleShortVersionString", "CFBundleVersion",
                      "CFBundleExecutable", "NSHumanReadableCopyright", "AudioComponents", "LSMinimumSystemVersion"):
                if k in p:
                    info[k] = p[k]
        ext = collections.Counter(); tam = collections.Counter(); grandes = []
        for r, _, fs in os.walk(os.path.join(bundle, "Contents")):
            for fn in fs:
                fp = os.path.join(r, fn); e = os.path.splitext(fn)[1].lower() or "(sem ext)"
                s = os.path.getsize(fp); ext[e] += 1; tam[e] += s; grandes.append((s, os.path.relpath(fp, bundle)))
        R["bundle"] = {"info_plist": info, "extensoes": {k: [ext[k], tam[k]] for k in ext},
                       "maiores": [[s, p] for s, p in sorted(grandes, reverse=True)[:8]]}

    # relatório md
    L = [f"# Inventário estático: {os.path.basename(a.plugin)}", "", f"- binário: `{binp}` ({len(data)/1e6:.1f} MB)",
         f"- `{R['lipo']}`", ""]
    L += ["## Slices"] + [f"- {s['arch']}: {s['tamanho']} B, sha256 `{s['sha256']}`" for s in sl] + [""]
    L += ["## Linkagem (otool -L)"] + [f"- {l}" for l in libs] + [""]
    L += [f"## Seções ({alvo['arch']})", "| seg | seção | tamanho | entropia |", "|---|---|---|---|"]
    L += [f"| {s['seg']} | {s['sect']} | {s['tamanho']} | {s['entropia']} |" for s in secs] + [""]
    L += ["## Tecnologia de UI inferida", ", ".join(R["ui"]) or "(nada identificado)", ""]
    if bundle:
        L += ["## Bundle", "```json", json.dumps(R["bundle"], indent=1, ensure_ascii=False), "```", ""]
    L0 = list(L)
    for t, k in (("Classes (RTTI/Itanium)", "rtti"), ("Nomes tipo parâmetro", "nomes_tipo_parametro"), ("Pistas de DSP", "pistas_dsp"),
                 ("Mensagens/tooltips", "mensagens"), ("URLs", "urls"), ("Versões", "versoes")):
        L += [f"## {t}"] + [f"- `{x}`" for x in R[k]] + [""]
        if k == "urls":   # terminal: só domínios únicos (máx. 15); a lista completa fica em inspect.md/json
            doms = sorted({re.sub(r"^https?://([^/:?#]+).*", r"\1", u) for u in R["urls"]})
            L0 += [f"## {t} ({len(R['urls'])} no total, {len(doms)} domínios; lista completa em inspect.md/json)"] + \
                  [f"- `{d}`" for d in doms[:15]] + ([f"- ... +{len(doms) - 15} domínios"] if len(doms) > 15 else []) + [""]
        else:
            L0 += [f"## {t}"] + [f"- `{x}`" for x in R[k]] + [""]
    md = "\n".join(L)
    print("\n".join(L0))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        open(os.path.join(a.out, "inspect.md"), "w").write(md)
        json.dump(R, open(os.path.join(a.out, "inspect.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
