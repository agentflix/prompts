#!/usr/bin/env python3
"""Biblioteca comum das medições multi-fase (plugin-re v2). Só stdlib + numpy + scipy (+ pedalboard p/ plugin real).

Não é CLI: é importada pelos scripts (PYTHONPATH=<skill>/scripts). Contém:
  Alvo        plugin real (pedalboard, regime estável, reset=False) OU recriação (--py/--exe) com a mesma interface
  ess/deconv  varredura senoidal exponencial (Farina) e deconvolução -> IR linear
  rt_bandas   EDC de Schroeder, RT60 (T30/T20/EDT) por banda de oitava, com correção de piso de ruído
  ned/iacc    densidade de ecos normalizada (Abel-Huang) e correlação interaural
  acha_ecos   ecos discretos em uma resposta (delay)
  demod_tom   demodulação AM/FM de um tom: taxa, profundidade, forma, fase entre canais
  tom_analise ganho e harmônicas de um tom em janela de bin inteiro
Convenções: áudio sempre (canais, amostras) float; SR padrão 48000; dB = 20*log10 em amplitude.
"""
import importlib.util, json, os, subprocess, tempfile
import numpy as np
from scipy import signal

db = lambda v: 20 * np.log10(np.maximum(np.abs(v), 1e-30))
BANDAS_OITAVA = (125, 250, 500, 1000, 2000, 4000, 8000)


# ---------------------------------------------------------------- alvo (plugin real ou recriação)
class Alvo:
    """Interface única: proc(x[canais,N]) -> y[canais,N]. Plugin: estado contínuo (reset=False)."""

    def __init__(self, sr=48000):
        self.sr = int(sr)
        self.nome = "?"
        self.tipo = "?"

    def proc(self, x):
        raise NotImplementedError

    def mudo(self, seg):
        """processa silêncio (limpa cauda e deixa rampas de parâmetro assentarem)"""
        return self.proc(np.zeros((2, int(seg * self.sr)), np.float32))


class Plugin(Alvo):
    def __init__(self, caminho, sr=48000, sets=None, settings=None, mix_auto=True):
        from pedalboard import load_plugin
        super().__init__(sr)
        self.tipo = "plugin"
        self.caminho = caminho
        self.fx = load_plugin(caminho)
        self.P = self.fx.parameters
        self.nome = getattr(self.fx, "name", os.path.basename(caminho))
        self.fx.reset()                               # UM reset só, no início
        self.alterados = {}
        self.padrao = {n: float(self.P[n].raw_value) for n in self.P.keys()}
        if settings:
            sets = {**json.load(open(settings)), **(sets or {})}
        self.mix_param = None
        if mix_auto:
            # efeito em 100 % molhado: a parte seca (LTI trivial) mascara reverb/delay/modulação
            self.mix_param = self.achar("mix", "dry/wet", "dry_wet", "wet")
            if self.mix_param and self.mix_param not in (sets or {}):
                self.setp(**{self.mix_param: 1.0})
        for n in self.P.keys():
            if "bypass" in n.lower() and n not in (sets or {}):
                try:
                    self.setp(**{n: 0.0})
                except Exception:
                    pass
        if sets:
            self.setp(**{k: float(v) for k, v in sets.items()})

    def achar(self, *chaves):
        for n in self.P.keys():
            if any(k in n.lower() for k in chaves) and "mixer" not in n.lower():
                return n
        return None

    def setp(self, **kw):
        for k, v in kw.items():
            self.P[k].raw_value = float(min(1.0, max(0.0, v)))   # raw_value NORMALIZADO 0..1
            self.alterados[k] = float(v)

    def proc(self, x):
        x = np.asarray(x, np.float32)
        if x.ndim == 1:
            x = np.tile(x[None], (2, 1))
        y = np.asarray(self.fx(x, self.sr, reset=False)).astype(np.float64)
        return y[:, :x.shape[1]]


class Recriacao(Alvo):
    """Recriação: função Python f(x(2,N), sr)->(2,N) ('arq.py:func') ou executável em lote ('CMD {in} {out}',
    float32 cru estéreo entrelaçado em SR; exporta PLUGINRE_SR). Sem estado entre chamadas (cada chamada é uma
    renderização completa): por isso os scripts de captura mandam o sinal inteiro (sinal + cauda) em UMA chamada."""

    def __init__(self, py=None, exe=None, sr=48000):
        super().__init__(sr)
        self.tipo = "recriacao"
        self.fn = None
        self.exe = exe
        if py:
            arq, fn = py.rsplit(":", 1)
            spec = importlib.util.spec_from_file_location("recriacao_usuario", arq)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.fn = getattr(m, fn)
        self.nome = py or exe

    def proc(self, x):
        x = np.asarray(x, np.float64)
        if x.ndim == 1:
            x = np.tile(x[None], (2, 1))
        if self.fn:
            return np.asarray(self.fn(x, self.sr), np.float64)
        with tempfile.TemporaryDirectory() as d:
            fi, fo = os.path.join(d, "in.f32"), os.path.join(d, "out.f32")
            x.T.astype(np.float32).tofile(fi)
            subprocess.run(self.exe.format(**{"in": fi, "out": fo}), shell=True, check=True,
                           env=dict(os.environ, PLUGINRE_SR=str(self.sr)))
            return np.fromfile(fo, np.float32).reshape(-1, 2).T.astype(np.float64)


def abre_alvo(plugin=None, py=None, exe=None, sr=48000, sets=None, settings=None, mix_auto=True):
    if plugin:
        return Plugin(plugin, sr, sets, settings, mix_auto)
    return Recriacao(py, exe, sr)


def parse_sets(lista):
    """['nome=0.5', ...] -> {nome: 0.5}"""
    out = {}
    for s in lista or []:
        k, v = s.rsplit("=", 1)
        out[k] = float(v)
    return out


# ---------------------------------------------------------------- tons
def tom(sr, f, amp_db, seg, canais=2, fase=0.0):
    t = np.arange(int(round(seg * sr))) / sr
    return np.tile((10 ** (amp_db / 20) * np.sin(2 * np.pi * f * t + fase))[None], (canais, 1)).astype(np.float32)


def tom_analise(y, sr, f, kmax=6):
    """Ganho do fundamental (amplitude de pico) e harmônicas H2..Hkmax relativas a H1 (razão linear).
    y: 1D de duração tal que f*N/sr é inteiro (bin exato). Hann."""
    N = len(y)
    w = np.hanning(N)
    Y = np.abs(np.fft.rfft(y * w)) * 2 / w.sum()
    pk = lambda k: float(Y[max(0, int(round(k * f * N / sr)) - 2):int(round(k * f * N / sr)) + 3].max())
    h1 = pk(1)
    hs = [pk(k) / (h1 + 1e-30) if k * f < sr / 2 - 100 else None for k in range(2, kmax + 1)]
    return h1, hs


def fasor(y, f, sr):
    """amplitude complexa do componente em f (lock-in, janela retangular); exata se a janela tem ciclos inteiros"""
    t = np.arange(len(y)) / sr
    return 2 * np.mean(y * np.exp(-2j * np.pi * f * t))


# ---------------------------------------------------------------- varredura exponencial (Farina)
def ess(sr, f1=20.0, f2=None, T=3.0, amp_db=-12.0, fade_ms=10):
    f2 = f2 or min(20000.0, 0.45 * sr)
    R = np.log(f2 / f1)
    t = np.arange(int(T * sr)) / sr
    s = np.sin(2 * np.pi * f1 * T / R * (np.exp(t * R / T) - 1))
    nf = int(fade_ms * sr / 1000)
    g = np.ones_like(s)
    g[:nf] = np.hanning(2 * nf)[:nf]
    g[-nf:] = np.hanning(2 * nf)[nf:]
    return (10 ** (amp_db / 20) * s * g), (f1, f2)


def deconv(y, s, comprimento, eps=1e-5):
    """IR linear por divisão espectral regularizada. y: gravado (>= len(s)+comprimento); s: varredura de entrada.
    nfft cobre len(y)+len(s): os termos harmônicos (lag negativo) caem no fim do vetor e são descartados.
    Retorna h[:comprimento] com lag 0 = instante de início da varredura (inclui latência do plugin)."""
    nfft = int(2 ** np.ceil(np.log2(len(y) + len(s))))
    Y, S = np.fft.rfft(y, nfft), np.fft.rfft(s, nfft)
    H = Y * np.conj(S) / (np.abs(S) ** 2 + eps * np.max(np.abs(S) ** 2))
    return np.fft.irfft(H, nfft)[:comprimento]


def captura_ess(alvo, T=3.0, cauda=6.0, amp_db=-12.0, flush=None, mono=True, f1=20.0):
    """grava a resposta a uma varredura (+ cauda de silêncio) e devolve (h[2,Ncauda], info). Plugin: antes, `flush`
    s de silêncio (padrão = cauda) limpam a cauda anterior e deixam as rampas de parâmetro assentarem."""
    sr = alvo.sr
    if alvo.tipo == "plugin":
        alvo.mudo(cauda if flush is None else flush)
    s, (f1, f2) = ess(sr, f1, None, T, amp_db)
    x = np.zeros((2, len(s) + int(cauda * sr)), np.float32)
    x[0, :len(s)] = s
    x[1, :len(s)] = s if mono else 0
    y = alvo.proc(x)
    h = np.vstack([deconv(y[c], s, int(cauda * sr)) for c in range(min(2, y.shape[0]))])
    if h.shape[0] == 1:
        h = np.vstack([h, h])
    return h, {"f1": f1, "f2": f2, "T": T, "amp_db": amp_db, "cauda": cauda}


def captura_impulso(alvo, cauda=6.0, amp=0.5, flush=None, mono=True, pos_s=0.0):
    sr = alvo.sr
    if alvo.tipo == "plugin":
        alvo.mudo(cauda if flush is None else flush)
    n = int(cauda * sr)
    x = np.zeros((2, n), np.float32)
    p = int(pos_s * sr)
    x[0, p] = amp
    if mono:
        x[1, p] = amp
    y = alvo.proc(x) / amp
    return y[:, p:], {"metodo": "impulso", "amp": amp}


# ---------------------------------------------------------------- análise de IR de reverb
def envelope_db(h, sr, hop_ms=1.0):
    """energia por passo de hop_ms em dB (relativo ao máximo)"""
    n = max(1, int(hop_ms * sr / 1000))
    m = len(h) // n
    e = (h[:m * n].reshape(m, n) ** 2).sum(1)
    return 10 * np.log10(np.maximum(e, 1e-30) / max(e.max(), 1e-30))


def onset_predelay(h, sr):
    """h: (2,N). Devolve dict: onset (1ª energia a -30 dB do pico), direto_detectado, pre_atraso_ms.
    Se há som direto (pico nos primeiros 2 ms que cai >40 dB logo depois), pré-atraso = início da parte reverberante."""
    e = h[0] ** 2 + h[1] ** 2
    ev = envelope_db(np.sqrt(e), sr, 1.0)            # em passos de 1 ms
    pk = int(np.argmax(ev))
    on = int(np.argmax(ev > -30))
    r = {"onset_ms": float(on), "pico_ms": float(pk)}
    direto = pk <= 2 and len(ev) > 20 and np.max(ev[8:]) < -20
    r["direto_detectado"] = bool(direto)
    if direto:
        g = int(np.argmax(ev[pk + 1:] < ev[pk] - 40)) + pk + 1
        rest = ev[g:]
        if len(rest):
            r["pre_atraso_ms"] = float(g + int(np.argmax(rest > rest.max() - 25)))
        else:
            r["pre_atraso_ms"] = None
    else:
        r["pre_atraso_ms"] = float(on)
    return r


def edc_db(e):
    c = np.cumsum(e[::-1])[::-1]
    return 10 * np.log10(np.maximum(c / max(c[0], 1e-30), 1e-30))


def rt_banda(hb2, sr):
    """hb2: energia (amostras) da banda. Correção do piso de ruído + EDC; T30/T20/EDT em s (ou None)."""
    n = len(hb2)
    win = max(1, int(0.02 * sr))
    ruido = float(np.mean(hb2[int(0.9 * n):])) if n > 100 else 0.0
    # o fim da gravação só é "piso de ruído" se estiver plano; se ainda cai (RT longo, cauda curta), não subtrair nada
    fim = hb2[int(0.8 * n):]
    if len(fim) > 10 * win:
        m = len(fim) // win
        env = 10 * np.log10(fim[:m * win].reshape(m, win).mean(1) + 1e-30)
        decl = np.polyfit(np.arange(m) * win / sr, env, 1)[0]
        if decl < -3.0 and env.max() - env.min() > 1.0:
            ruido = 0.0
    suav = np.convolve(hb2, np.ones(win) / win, "same")
    pk = int(np.argmax(suav))
    abaixo = np.where(suav[pk:] < 2 * ruido)[0]
    tc = pk + int(abaixo[0]) if len(abaixo) else n
    nao_decaiu = len(abaixo) == 0
    e = np.maximum(hb2[:tc] - ruido, 0)
    if len(e) < win * 4 or e.sum() <= 0:
        return {"t30": None, "t20": None, "edt": None, "faixa_db": 0.0, "nao_decaiu": nao_decaiu}
    edc = edc_db(e)
    t = np.arange(len(edc)) / sr
    faixa = float(-edc[-1])

    def rt(a, b):
        i = np.where((edc <= a) & (edc >= b))[0]
        if len(i) < 10 or edc.min() > b:
            return None
        m = np.polyfit(t[i], edc[i], 1)[0]
        return float(-60.0 / m) if m < 0 else None
    return {"t30": rt(-5, -35), "t20": rt(-5, -25), "edt": rt(0, -10), "faixa_db": faixa, "nao_decaiu": nao_decaiu}


def rt_bandas(h, sr, bandas=BANDAS_OITAVA):
    """h: (2,N). RT60 por banda de oitava (energia L+R)."""
    out = {}
    for fc in bandas:
        lo, hi = fc / np.sqrt(2), min(fc * np.sqrt(2), 0.45 * sr)
        if hi <= lo:
            continue
        sos = signal.butter(4, [lo, hi], "band", fs=sr, output="sos")
        hb = signal.sosfiltfilt(sos, h, axis=1)
        out[str(fc)] = rt_banda((hb ** 2).sum(0), sr)
    return out


def rt_resumo(r):
    """escolhe T30, senão T20, senão EDT (rotula qual) por banda"""
    out = {}
    for k, v in r.items():
        for nome in ("t30", "t20", "edt"):
            if v[nome]:
                out[k] = {"rt60_s": round(v[nome], 3), "base": nome, "faixa_db": round(v["faixa_db"], 1)}
                break
        else:
            out[k] = {"rt60_s": None, "base": None, "faixa_db": round(v["faixa_db"], 1)}
    return out


def ned(h, sr, janela_ms=20.0, hop_ms=5.0):
    """densidade de ecos normalizada (Abel & Huang 2006), mono (soma L+R). Devolve (t_s, ned). Gaussiano -> 1."""
    x = h.sum(0) if h.ndim == 2 else h
    w = int(janela_ms * sr / 1000)
    hop = int(hop_ms * sr / 1000)
    win = np.hanning(w)
    erfc = 0.3173105078629141
    ts, v = [], []
    for i in range(0, len(x) - w, hop):
        seg = x[i:i + w]
        s = np.sqrt(np.sum(win * seg ** 2) / win.sum())
        if s <= 1e-12:
            break
        v.append(float(np.sum(win * (np.abs(seg) > s)) / win.sum() / erfc))
        ts.append(i / sr)
    return np.array(ts), np.array(v)


def ned_resumo(h, sr):
    t, v = ned(h, sr)
    if len(t) == 0:
        return {"t_ned_1_ms": None}
    ok = np.where(v >= 0.99)[0]
    at = lambda ms: float(np.interp(ms / 1000, t, v)) if t[-1] > ms / 1000 else None
    return {"t_ned_1_ms": round(float(t[ok[0]] * 1000), 1) if len(ok) else None,
            "ned_50ms": at(50), "ned_100ms": at(100), "ned_250ms": at(250)}


def iacc(h, sr, t0=0.0, t1=0.08, maxlag_ms=1.0, banda=None):
    """máximo da correlação cruzada normalizada L/R em ±1 ms, no trecho [t0,t1) s"""
    L, R = h[0], h[1]
    if banda:
        sos = signal.butter(4, [banda / np.sqrt(2), min(banda * np.sqrt(2), 0.45 * sr)], "band", fs=sr, output="sos")
        L, R = signal.sosfiltfilt(sos, L), signal.sosfiltfilt(sos, R)
    a, b = L[int(t0 * sr):int(t1 * sr)], R[int(t0 * sr):int(t1 * sr)]
    den = np.sqrt(np.sum(a ** 2) * np.sum(b ** 2))
    if den <= 1e-20 or len(a) < 8:
        return None
    c = signal.correlate(a, b, "full", method="fft") / den
    m = int(maxlag_ms * sr / 1000)
    mid = len(a) - 1
    return float(np.max(np.abs(c[mid - m:mid + m + 1])))


def espectro_oitavas(x, sr, bandas=(63,) + BANDAS_OITAVA + (16000,)):
    """energia por oitava (dB, relativa à banda de maior energia)"""
    r = {}
    for fc in bandas:
        hi = min(fc * np.sqrt(2), 0.45 * sr)
        if hi <= fc / np.sqrt(2):
            continue
        sos = signal.butter(4, [fc / np.sqrt(2), hi], "band", fs=sr, output="sos")
        r[str(fc)] = float(np.sum(signal.sosfilt(sos, x) ** 2))
    m = max(r.values()) + 1e-30
    return {k: round(float(10 * np.log10(v / m + 1e-30)), 2) for k, v in r.items()}


def analisa_ir(h, sr):
    """pacote completo de estatísticas de uma IR estéreo (usado por captura_ir e teste_fechamento)"""
    pre = onset_predelay(h, sr)
    hg = h.copy()
    if pre.get("direto_detectado") and pre.get("pre_atraso_ms") is not None:
        hg[:, :int(pre["pre_atraso_ms"] / 1000 * sr)] = 0      # RT60 da parte reverberante, sem o direto
    bandas = rt_bandas(hg, sr)
    n = h.shape[1]
    tfim = min(n / sr, 1.5)
    r = {"pre": pre, "rt60": rt_resumo(bandas), "ned": ned_resumo(hg, sr),
         "iacc_precoce_0_80ms": iacc(h, sr, 0.0, 0.08), "iacc_tardio_80ms_1s": iacc(h, sr, 0.08, tfim),
         "iacc_oitavas_tardio": {str(b): iacc(h, sr, 0.08, tfim, banda=b) for b in (250, 1000, 4000)},
         "espectro_cauda_oitavas_db": espectro_oitavas(hg[:, int(0.2 * sr):].sum(0), sr) if n > int(0.4 * sr) else None,
         "energia_L_menos_R_db": float(10 * np.log10((h[0] ** 2).sum() / ((h[1] ** 2).sum() + 1e-30) + 1e-30))}
    if n > int(0.4 * sr):
        r["energia_cauda_200ms_em_diante_db"] = round(float(10 * np.log10((hg[:, int(0.2 * sr):] ** 2).sum() / ((hg ** 2).sum() + 1e-30) + 1e-30)), 1)
    ev = envelope_db(np.sqrt(hg[0] ** 2 + hg[1] ** 2), sr, 10.0)
    ruido = float(np.median(ev[-max(3, len(ev) // 10):]))
    r["piso_ruido_db_rel_pico"] = round(ruido, 1)
    return r


# ---------------------------------------------------------------- ecos discretos (delay)
def acha_ecos(y, sr, t0=0.0, limiar_db=-60.0, sep_ms=5.0, sup_ms=1.0, acima_piso_db=15.0):
    """picos de envelope (RMS sup_ms) em y(1D) a partir de t0 s, acima de max(limiar_db, mediana+acima_piso_db). Devolve lista de (tempo_s sub-amostra, nível dB rel. maior)."""
    n = max(1, int(sup_ms * sr / 1000))
    env = np.sqrt(np.convolve(y ** 2, np.ones(n) / n, "same"))
    i0 = int(t0 * sr)
    e = env[i0:]
    if e.max() <= 0:
        return []
    ed = db(e / e.max())
    piso = float(np.median(ed))                              # piso = mediana do envelope (ecos esparsos): ruído/difusão não vira "eco"
    pk, _ = signal.find_peaks(ed, height=max(limiar_db, piso + acima_piso_db), distance=max(1, int(sep_ms * sr / 1000)), prominence=6)
    out = []
    for p in pk:
        if 0 < p < len(ed) - 1:                              # interpolação parabólica em dB
            a, b, c = ed[p - 1], ed[p], ed[p + 1]
            d = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
        else:
            d = 0.0
        out.append(((i0 + p + d) / sr, float(ed[p])))
    return out


# ---------------------------------------------------------------- demodulação de tom (LFO)
def _pico_espectral(x, sr, fmin=0.05, fmax=40.0, zp=8):
    x = x - x.mean()
    n = len(x)
    w = np.hanning(n)
    nf = n * zp
    X = np.fft.rfft(x * w, nf) * 2 / w.sum()
    f = np.fft.rfftfreq(nf, 1 / sr)
    m = (f >= fmin) & (f <= fmax)
    A = np.abs(X)
    idx = np.where(m)[0]
    i = idx[np.argmax(A[m])]
    if idx[0] < i < idx[-1]:                                   # parabólica em log
        a, b, c = np.log(A[i - 1] + 1e-30), np.log(A[i] + 1e-30), np.log(A[i + 1] + 1e-30)
        d = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    else:
        d = 0.0
    fp = float(min(max(f[i] + d * (f[1] - f[0]), fmin), fmax))
    prom = float(20 * np.log10(A[i] / (np.median(A[m]) + 1e-30)))
    return fp, float(A[i]), prom, f, A, X


def demod_tom(y, sr, f, aparar_s=0.1):
    """y: (canais, N) tom estável de f Hz atravessando o efeito. Demodula AM (envelope) e FM (fase) por Hilbert.
    Devolve taxa do LFO, profundidade AM (dB pico a pico) e FM (cents de pico), forma (razão dos harmônicos do LFO),
    banda lateral (dBc), proeminência do pico (dB) e fase/atraso entre canais."""
    y = np.atleast_2d(y)
    a = int(aparar_s * sr)
    res = {"canais": []}
    sinais = []
    bp0 = signal.butter(4, [0.7 * f, 1.3 * f], "band", fs=sr, output="sos")   # isola a portadora: harmônicas não entram
    for c in range(y.shape[0]):
        z = signal.hilbert(signal.sosfiltfilt(bp0, y[c]))[a:-a]
        t = np.arange(len(z)) / sr
        e = np.abs(z)
        ph = np.unwrap(np.angle(z))
        ph -= np.polyval(np.polyfit(t, ph, 1), t)             # tira a portadora (inclusive ligeiro desvio)
        # banda 0,2-60 Hz: deriva lenta/transiente de DC e batimentos rápidos não são LFO
        q = max(1, int(sr // 1000))                           # decima p/ ~1 kHz antes do passa-faixa (estabilidade numérica)
        s2 = sr / q
        hp = signal.butter(2, [0.2, 60.0], "band", fs=s2, output="sos")
        am = signal.sosfiltfilt(hp, signal.resample_poly(e / e.mean() - 1, 1, q))
        ph = signal.sosfiltfilt(hp, signal.resample_poly(ph, 1, q))
        dev = np.gradient(ph) * s2 / (2 * np.pi)               # Hz instantâneos
        cents = 1200 * np.log2(np.maximum(1 + dev / f, 1e-6))
        am_p, fm_p = _pico_espectral(am, s2, fmin=0.2), _pico_espectral(cents, s2, fmin=0.2)
        # a fonte dominante é a de maior proeminência espectral
        usa = "am" if am_p[2] >= fm_p[2] else "fm"
        pk = am_p if usa == "am" else fm_p
        x = am if usa == "am" else cents
        f_lfo, amp1, prom = pk[0], pk[1], pk[2]
        fr, A, X = pk[3], pk[4], pk[5]
        harm = {}
        for k in (2, 3):
            m = (fr > (k * f_lfo) * 0.97) & (fr < (k * f_lfo) * 1.03) & (fr < 60)
            harm[f"h{k}"] = float(A[m].max() / (amp1 + 1e-30)) if m.any() else None
        mb = (fr >= 0.2) & (fr <= 60)
        ip, _ = signal.find_peaks(np.where(mb, A, 0))
        ip = ip[np.argsort(A[ip])[::-1][:4]]
        picos = [{"hz": round(float(fr[i]), 3), "rel": round(float(A[i] / (A[ip[0]] + 1e-30)), 3)} for i in ip]
        m_am = float(np.sqrt(2) * am.std())
        b_fm = float(np.sqrt(2) * ph.std())
        res["canais"].append({
            "fonte_dominante": usa, "taxa_hz": round(f_lfo, 4), "proeminencia_db": round(prom, 1),
            "am_pico_a_pico_db": round(float(db((1 + np.percentile(am, 99)) / max(1 + np.percentile(am, 1), 1e-6))), 3),
            "fm_pico_cents": round(float((np.percentile(cents, 98) - np.percentile(cents, 2)) / 2), 3),
            "banda_lateral_dbc": round(float(db(min(max(m_am, b_fm), 2.0) / 2)), 1),
            "harmonicos_lfo": harm, "picos_espectro_modulacao": picos, "forma": classifica_forma(harm, prom)})
        sinais.append({'am': am_p, 'fm': fm_p})
    if y.shape[0] >= 2:
        # fase entre canais, no pico do canal 0, para AM e para FM (a fonte dominante pode diferir do que importa ao ouvido)
        for fonte in ("am", "fm"):
            a0, a1 = sinais[0][fonte], sinais[1][fonte]
            i = int(np.argmin(np.abs(a0[3] - a0[0])))
            d = float(np.angle(a1[5][i] / (a0[5][i] + 1e-30), deg=True))
            res[f"fase_L_R_graus_{fonte}"] = round(d, 1)
            res[f"atraso_L_R_ms_{fonte}"] = round(d / 360.0 / a0[0] * 1000, 2) if a0[0] > 0 else None
            res[f"proeminencia_{fonte}_db"] = round(a0[2], 1)
        dom = res["canais"][0]["fonte_dominante"]
        res["fase_L_R_graus"] = res[f"fase_L_R_graus_{dom}"]
        res["atraso_L_R_ms"] = res[f"atraso_L_R_ms_{dom}"]
    return res


def classifica_forma(h, prom):
    if prom < 12:
        return "aleatoria_ou_sem_lfo"
    h2, h3 = h.get("h2") or 0.0, h.get("h3") or 0.0
    if h2 > 0.3:
        return "dente_de_serra"
    if h3 > 0.22:
        return "quadrada"
    if h3 > 0.06:
        return "triangular"
    return "senoidal"
