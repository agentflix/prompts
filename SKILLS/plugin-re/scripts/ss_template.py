#!/usr/bin/env python3
"""Harness de REGIME ESTÁVEL genérico (pedalboard). Importe ou rode como CLI.

Por que existe: o pedalboard chama reset() a cada fx(...) por padrão e muitos plugins ignoram
parâmetros ~0,3 s após o reset; a mudança só vale a partir do 2º process(). Então: um reset só,
aquece >= 3 s com o MESMO sinal, reset=False sempre, e só então mede.

Uso como módulo (PYTHONPATH=<skill>/scripts):
    from ss_template import Harness
    h = Harness("/Library/Audio/Plug-Ins/VST3/X.vst3", sr=96000)
    h.defaults({"input_gain_db": 1, "drive_db": 1/3})      # raw 0..1 normalizado
    h.setp(depth=0.5)                                       # raw 0..1
    h.setv("drive_db", 6.0)                                 # valor físico (usa get_raw_value_for)
    print(h.meas(-6, f=1000))   # ganho (dB), h[H2..H6] relativos a H1, pico, média (DC), rms

Canais: padrão 2 (L=R duplicado; mantém o teste de link estéreo honesto). Mono: Harness(..., canais=1) ou --mono.
Latência: `h.latencia()` lê fx.reported_latency_samples (após processar um bloco); `run()` devolve a saída
ALINHADA por essa latência (ver blackbox-pedalboard.md §8: com reset=False só a 1ª chamada sai compensada).

CLI (demo): ss_template.py PLUGIN --set nome=raw ... --amp -6 --freq 1000
"""
import argparse, json, sys
import numpy as np


class Harness:
    def __init__(self, path, sr=96000, canais=2, warm=3, janela_s=1.0):
        from pedalboard import load_plugin
        self.fx = load_plugin(path)
        self.P = self.fx.parameters
        self.sr, self.canais, self.warm = int(sr), int(canais), int(warm)
        self.N = int(round(sr * janela_s))
        self.t = np.arange(self.N) / self.sr
        self.w = np.hanning(self.N)
        self._padrao = {n: float(self.P[n].raw_value) for n in self.P.keys()}

    # --- parâmetros ---
    def setp(self, **kw):
        for k, v in kw.items():
            self.P[k].raw_value = float(min(1.0, max(0.0, v)))   # raw_value é normalizado 0..1

    def setv(self, nome, valor):
        # valor físico -> raw via get_raw_value_for (respeita taper e passos do plugin)
        self.P[nome].raw_value = float(self.P[nome].get_raw_value_for(valor))

    def defaults(self, base=None, **kw):
        # volta ao padrão de fábrica (ou ao dict base, raw) e aplica kw (raw)
        for n, v in self._padrao.items():
            self.P[n].raw_value = v
        if base:
            self.setp(**base)
        self.setp(**kw)

    # --- sinais ---
    def tone(self, amp_db, f=1000.0):
        return (10 ** (amp_db / 20) * np.sin(2 * np.pi * f * self.t)).astype(np.float32)

    def _blk(self, x):
        x = np.asarray(x, np.float32)
        return np.tile(x.reshape(1, -1), (self.canais, 1)) if x.ndim == 1 else x

    # --- latência ---
    def latencia(self, sr=None):
        # latência reportada (amostras). O pedalboard só atualiza o valor depois de processar áudio
        # (reconfiguração, ex.: troca de oversampling): processa um bloco curto antes de ler.
        self.fx(np.zeros((self.canais, 1024), np.float32), sr or self.sr, reset=False)
        return int(getattr(self.fx, "reported_latency_samples", 0) or 0)

    # --- execução em regime estável ---
    def run(self, x, warm=None, sr=None, alinhar=True):
        # Saída alinhada pela latência reportada L. Com reset=False só a 1ª chamada após reset sai
        # compensada (N-L amostras); as seguintes saem com N amostras atrasadas de L. Como a medida é a
        # chamada final (já "seguinte"), processa-se mais um bloco igual e recorta-se [L:L+N].
        sr = sr or self.sr
        b = self._blk(x)
        n = b.shape[1]
        self.fx.reset()                         # um reset só; depois reset=False
        nw = self.warm if warm is None else warm
        for _ in range(nw):
            self.fx(b, sr, reset=False)         # aquecimento com o mesmo sinal (>= 3 s)
        y = np.asarray(self.fx(b, sr, reset=False))[:, :n]
        self.lat = int(getattr(self.fx, "reported_latency_samples", 0) or 0)
        if alinhar and self.lat > 0 and nw > 0:
            y2 = np.asarray(self.fx(b, sr, reset=False))[:, :n]
            y = np.concatenate([y, y2], axis=1)[:, self.lat:self.lat + n]
        return y[0] if self.canais == 1 else y

    def meas(self, amp_db, f=1000.0, kmax=6):
        # ganho do fundamental e harmônicas H2..Hkmax relativas a H1; DC/pico no 2º meio da janela
        x = self.tone(amp_db, f)
        y = self.run(x)
        y1 = y if y.ndim == 1 else y[0]
        b = lambda A, k: A[max(0, int(round(k * f * self.N / self.sr)) - 2):int(round(k * f * self.N / self.sr)) + 3].max()
        Y, X = np.abs(np.fft.rfft(y1 * self.w)), np.abs(np.fft.rfft(x * self.w))
        h1 = b(Y, 1)
        seg = y1[self.N // 4:]
        return dict(gain=float(20 * np.log10(h1 / b(X, 1) + 1e-30)),
                    h=[float(b(Y, k) / h1) if k * f < self.sr / 2 else None for k in range(2, kmax + 1)],
                    peak=float(np.abs(seg).max()), mean=float(seg.mean()), rms=float(np.sqrt((seg ** 2).mean())))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--set", nargs="*", default=[], metavar="nome=raw", help="parâmetros em raw 0..1")
    ap.add_argument("--setv", nargs="*", default=[], metavar="nome=valor", help="parâmetros em valor físico")
    ap.add_argument("--amp", type=float, default=-6.0, help="nível do tom em dBFS (padrão -6)")
    ap.add_argument("--freq", type=float, default=1000.0)
    ap.add_argument("--sr", type=int, default=96000)
    ap.add_argument("--canais", type=int, default=2, help="canais (padrão 2; 1 = mono)")
    ap.add_argument("--mono", action="store_true", help="atalho para --canais 1")
    ap.add_argument("--warm", type=int, default=3, help="segundos de aquecimento (>=3)")
    a = ap.parse_args()
    h = Harness(a.plugin, a.sr, 1 if a.mono else a.canais, a.warm)
    h.defaults()
    h.setp(**{k: float(v) for k, v in (s.split("=") for s in a.set)})
    for s in a.setv:
        k, v = s.split("="); h.setv(k, float(v))
    r = h.meas(a.amp, a.freq)
    r['latencia_amostras'] = h.lat
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
