#!/usr/bin/env python3
"""Teste com música: plugin real vs motor, resíduo nulo em janelas de 100 ms.

Por que: tons simples escondem erros que material real expõe (transientes, DC, mix, rampas).
Fluxo: carrega o trecho -> plugin (um reset, 1 s de preâmbulo mudo descartado, reset=False) ->
motor -> alinha por correlação cruzada (±200 amostras) -> resíduo por janela de 100 ms relativo ao
RMS do plugin na janela -> % de janelas <= --limite dB (padrão -40), só janelas com plugin > -60 dBFS.

Motor (escolha um; sem nenhum, compara o plugin contra a ENTRADA = sanidade "plugin altera o sinal?"):
  --exe "CMD {in} {out}"   comando que lê {in} e grava {out}: float32 cru ESTÉREO ENTRELAÇADO na taxa --sr
                           (exporta PLUGINRE_SR). Ex.: --exe "./xsat_drv {in} {out} 0 6 1 .5 0 1 0 0"
  --py ARQ.py:FUNC         f(x: ndarray (2,N) float64, sr: int) -> ndarray (2,N)
Ajustes do plugin: --settings JSON {param: raw 0..1} aplicado após o padrão de fábrica.
Entrada: qualquer arquivo que o pedalboard leia (wav/flac/aiff/mp3) ou --raw-f32 (estéreo entrelaçado).
"""
import argparse, importlib.util, json, os, subprocess, sys, tempfile
import numpy as np
from scipy import signal

db = lambda v: 20 * np.log10(np.asarray(v) + 1e-30)


def carrega(path, sr, raw, ini, dur):
    if raw:
        x = np.fromfile(path, np.float32).reshape(-1, 2).T.astype(np.float64)
    else:
        from pedalboard.io import AudioFile
        with AudioFile(path) as f:
            x = f.read(f.frames).astype(np.float64); sr0 = int(f.samplerate)
        if x.shape[0] == 1:
            x = np.vstack([x, x])
        x = x[:2]
        if sr0 != sr:
            x = signal.resample_poly(x, sr, sr0, axis=1)
    a = int(ini * sr)
    return x[:, a:a + int(dur * sr)] if dur > 0 else x[:, a:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin"); ap.add_argument("audio")
    ap.add_argument("--exe"); ap.add_argument("--py")
    ap.add_argument("--settings"); ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--raw-f32", action="store_true"); ap.add_argument("--inicio", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=10.0, help="duração do trecho em s (0 = até o fim)")
    ap.add_argument("--limite", type=float, default=-40.0, help="limite do resíduo por janela em dB (padrão -40)")
    ap.add_argument("--janela-ms", type=float, default=100.0)
    ap.add_argument("--json", help="grava o resumo")
    a = ap.parse_args()
    from pedalboard import load_plugin
    sr = a.sr
    x = carrega(a.audio, sr, a.raw_f32, a.inicio, a.dur)
    fx = load_plugin(a.plugin); P = fx.parameters
    for k, v in (json.load(open(a.settings)) if a.settings else {}).items():
        P[k].raw_value = float(v)
    fx.reset()
    fx(np.zeros((2, sr), np.float32), sr, reset=False)            # preâmbulo mudo (pós-reset), descartado
    yp = np.asarray(fx(x.astype(np.float32), sr, reset=False)).astype(np.float64)
    # motor
    if a.exe:
        with tempfile.TemporaryDirectory() as d:
            fi, fo = os.path.join(d, "in.f32"), os.path.join(d, "out.f32")
            x.T.astype(np.float32).tofile(fi)
            subprocess.run(a.exe.format(**{"in": fi, "out": fo}), shell=True, check=True, env=dict(os.environ, PLUGINRE_SR=str(sr)))
            ye = np.fromfile(fo, np.float32).reshape(-1, 2).T.astype(np.float64)
    elif a.py:
        arq, fn = a.py.split(":")
        spec = importlib.util.spec_from_file_location("motor_usuario", arq); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        ye = np.asarray(getattr(m, fn)(x, sr), np.float64)
    else:
        ye = x.copy()
    n = min(yp.shape[1], ye.shape[1]); yp, ye = yp[:, :n], ye[:, :n]
    # alinhamento por xcorr no canal L (até 10 s)
    k = min(n, 10 * sr); cc = signal.correlate(yp[0, :k], ye[0, :k], "full", method="fft")
    lags = signal.correlation_lags(k, k); msk = np.abs(lags) <= 200
    lag = int(lags[msk][np.argmax(cc[msk])])
    if lag:
        ye = np.roll(ye, lag, axis=1)   # lag>0: plugin atrasado em relação ao motor -> atrasa o motor
    W = int(sr * a.janela_ms / 1000); nw = n // W
    res = ye - yp
    wr = np.array([db(np.sqrt((res[:, i * W:(i + 1) * W] ** 2).mean()) / (np.sqrt((yp[:, i * W:(i + 1) * W] ** 2).mean()) + 1e-12)) for i in range(nw)])
    wp = np.array([db(np.sqrt((yp[:, i * W:(i + 1) * W] ** 2).mean())) for i in range(nw)])
    ok = wp > -60
    out = {"plugin": a.plugin, "audio": a.audio, "sr": sr, "duracao_s": round(n / sr, 2), "lag_amostras": lag,
           "modo": "motor" if (a.exe or a.py) else "plugin_vs_entrada",
           "residuo_global_db": round(float(db(np.sqrt((res ** 2).mean()) / np.sqrt((yp ** 2).mean()))), 2),
           "janelas_validas": int(ok.sum()), "mediana_janela_db": round(float(np.median(wr[ok])), 2) if ok.any() else None,
           "p90_janela_db": round(float(np.percentile(wr[ok], 90)), 2) if ok.any() else None,
           f"pct_janelas_<=_{a.limite:g}dB": round(float(100 * (wr[ok] <= a.limite).mean()), 2) if ok.any() else None,
           "pico_plugin_dbfs": round(float(db(np.abs(yp).max())), 2)}
    print(json.dumps(out, indent=1))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
