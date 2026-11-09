#!/usr/bin/env python3
"""Gera sinais de teste calibrados (WAV 32-bit float estéreo, 48 kHz) para comparar analisadores.

Toque cada arquivo no host, com os MESMOS ajustes nos dois plugins (range manual, mesmo MIN/MAX),
e compare as capturas do Spectrum 2 e do Vitral.

  tone_1k_-20dB.wav      seno 1 kHz a -20 dBFS: posição X do pico e nível (0 dB = fundo de escala)
  tones_ladder.wav       100 Hz, 1 kHz, 10 kHz a -20 dBFS: mapeamento do eixo de frequência
  pink_-20dB.wav         ruído rosa: efeito do SLOPE (3 dB deixa a curva plana)
  white_-20dB.wav        ruído branco: efeito do SLOPE (0 dB deixa a curva plana)
  burst_1k.wav           1 kHz por 2 s, 6 s de silêncio: balística do AVERAGE e do PEAK DECAY
  phase_inverted.wav     L = seno, R = -seno: leitura de fase (180 graus) e Side
  sweep_20_20k.wav       varredura log: resposta ao longo de todo o eixo
"""
import math, random, struct, wave, sys, os

SR = 48000
out = sys.argv[1] if len(sys.argv) > 1 else "signals"
os.makedirs(out, exist_ok=True)

def write(name, left, right):
    with wave.open(os.path.join(out, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(4); w.setframerate(SR)
        # WAV PCM 32-bit inteiro (suportado por todos os hosts); 0 dBFS = 2^31
        k = 2**31 - 1
        frames = bytearray()
        for l, r in zip(left, right):
            frames += struct.pack("<ii", int(max(-1, min(1, l)) * k), int(max(-1, min(1, r)) * k))
        w.writeframes(bytes(frames))

amp = 10 ** (-20 / 20)
secs = lambda s: range(int(s * SR))

sine = lambda f, a=amp: [a * math.sin(2 * math.pi * f * i / SR) for i in secs(10)]
s = sine(1000); write("tone_1k_-20dB.wav", s, s)

ladder = [amp * (math.sin(2*math.pi*100*i/SR) + math.sin(2*math.pi*1000*i/SR) + math.sin(2*math.pi*10000*i/SR)) / 3 for i in secs(10)]
write("tones_ladder.wav", ladder, ladder)

random.seed(7)
white = [random.uniform(-1, 1) for _ in secs(10)]
wr = [amp * 1.7 * x for x in white]
write("white_-20dB.wav", wr, wr)

# ruído rosa (Voss-McCartney simplificado)
rows = [0.0] * 12; total = 0.0; pink = []
for i in secs(10):
    for r in range(12):
        if i % (1 << r) == 0:
            total -= rows[r]; rows[r] = random.uniform(-1, 1); total += rows[r]
    pink.append(total / 12 * 1.2)
pk = [amp * 2 * x for x in pink]
write("pink_-20dB.wav", pk, pk)

b = [amp * math.sin(2*math.pi*1000*i/SR) if i < 2 * SR else 0.0 for i in secs(8)]
write("burst_1k.wav", b, b)

p = sine(1000)
write("phase_inverted.wav", p, [-x for x in p])

n = 10 * SR; f0, f1 = 20.0, 20000.0; ph = 0.0; sw = []
for i in range(n):
    f = f0 * (f1 / f0) ** (i / n); ph += 2 * math.pi * f / SR; sw.append(amp * math.sin(ph))
write("sweep_20_20k.wav", sw, sw)
print("sinais gravados em", out)
