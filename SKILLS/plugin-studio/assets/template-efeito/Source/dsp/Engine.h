#pragma once
// Motor de DSP do __PLUGIN_DISPLAY__. Só C++ padrão (sem JUCE): os testes compilam este header sozinho.
//
// Cadeia por amostra:  entrada -> TONE (tilt de 1 polo) -> GAIN -> MIX (seco/processado) -> BYPASS (crossfade)
// Regras:
//   - nada de alocação, lock ou I/O em process()
//   - ganhos suavizados (~5 ms) para não estalar; bypass com crossfade de ~15 ms
//   - MIX 0 % e ajustes neutros (GAIN 0 dB, TONE 0 dB, MIX 100 %) devolvem a entrada bit a bit
//   - latência zero; saída nunca é NaN/Inf
#include <algorithm>
#include <atomic>
#include <cmath>

namespace fx
{
    // valores reais (as mesmas unidades da tabela de parâmetros)
    struct Params
    {
        float gainDb = 0.0f;    // -24..+24 dB
        float toneDb = 0.0f;    // -12..+12 dB: >0 clareia (agudos sobem, graves descem), <0 escurece
        float mixPct = 100.0f;  // 0..100 %
        bool  bypass = false;
    };

    class Engine
    {
    public:
        static constexpr double pivotHz   = 800.0;  // frequência de cruzamento do tilt
        static constexpr double smoothMs  = 5.0;    // constante de tempo da suavização dos ganhos
        static constexpr double bypassMs  = 15.0;   // duração do crossfade do bypass
        static constexpr int    maxChannels = 2;

        void prepare (double sampleRate)
        {
            sr = sampleRate > 0.0 ? sampleRate : 48000.0;
            lpCoef = 1.0 - std::exp (-2.0 * pi * pivotHz / sr);
            const double k = 1.0 - std::exp (-1.0 / (smoothMs * 0.001 * sr));
            gain.coef = lo.coef = hi.coef = mix.coef = k;
            bypassStep = 1.0 / (bypassMs * 0.001 * sr);
            reset();
        }

        // zera filtros e leva todos os valores suavizados direto ao alvo
        void reset()
        {
            for (auto& s : lp) s = 0.0;
            gain.snap(); lo.snap(); hi.snap(); mix.snap();
            bypassPos = bypassTarget;
            peak.store (0.0f);
        }

        // pode ser chamado a cada bloco (thread de áudio)
        void setParams (const Params& p)
        {
            const double g = clampFinite (p.gainDb, -24.0, 24.0);
            const double t = clampFinite (p.toneDb, -12.0, 12.0);
            gain.target = dbToGain (g);
            lo.target   = dbToGain (-0.5 * t);
            hi.target   = dbToGain ( 0.5 * t);
            mix.target  = clampFinite (p.mixPct, 0.0, 100.0) / 100.0;
            bypassTarget = p.bypass ? 1.0 : 0.0;
        }

        // processa no lugar; r == nullptr para mono
        void process (float* l, float* r, int n)
        {
            if (l == nullptr || n <= 0) return;
            float* ch[maxChannels] = { l, r };
            const int numCh = r != nullptr ? 2 : 1;
            float pk = 0.0f;

            for (int i = 0; i < n; ++i)
            {
                const double g = gain.next(), gl = lo.next(), gh = hi.next(), m = mix.next();
                stepBypass();
                const double b = bypassPos;

                for (int c = 0; c < numCh; ++c)
                {
                    const float raw = ch[c][i];
                    const double in = std::isfinite (raw) ? (double) raw : 0.0;

                    double& s = lp[c];
                    s += lpCoef * (in - s);
                    if (! std::isfinite (s) || std::abs (s) < 1.0e-30) s = 0.0;   // NaN e denormais
                    const double high = in - s;

                    // com gl == gh == 1 os termos somados são zero: TONE neutro devolve a entrada exata
                    const double tilted = in + (gl - 1.0) * s + (gh - 1.0) * high;
                    const double wet = tilted * g;

                    double y = m >= 1.0 ? wet : (m <= 0.0 ? in : in + (wet - in) * m);
                    if (b >= 1.0)      y = in;
                    else if (b > 0.0)  y += (in - y) * b;
                    if (! std::isfinite (y)) y = 0.0;

                    const float out = (float) y;
                    ch[c][i] = out;
                    pk = std::max (pk, std::abs (out));
                }
            }

            // pico de saída desde a última leitura (um escritor: a thread de áudio)
            float prev = peak.load (std::memory_order_relaxed);
            while (pk > prev && ! peak.compare_exchange_weak (prev, pk, std::memory_order_relaxed)) {}
        }

        // lido pela interface (thread de mensagens): devolve o pico linear e zera
        float takePeak() { return peak.exchange (0.0f, std::memory_order_relaxed); }

        int latencySamples() const { return 0; }

    private:
        static constexpr double pi = 3.14159265358979323846;

        struct Smoothed
        {
            double cur = 1.0, target = 1.0, coef = 1.0;
            void snap() { cur = target; }
            double next()
            {
                if (std::islessgreater (cur, target))   // "!=" sem aviso de -Wfloat-equal
                {
                    cur += coef * (target - cur);
                    if (std::abs (target - cur) <= 1.0e-7 * std::max (1.0, std::abs (target))) cur = target;
                }
                return cur;
            }
        };

        static double dbToGain (double db) { return std::pow (10.0, db / 20.0); }
        static double clampFinite (double v, double a, double b) { return std::isfinite (v) ? std::clamp (v, a, b) : a; }

        void stepBypass()
        {
            if (bypassPos < bypassTarget)      bypassPos = std::min (bypassTarget, bypassPos + bypassStep);
            else if (bypassPos > bypassTarget) bypassPos = std::max (bypassTarget, bypassPos - bypassStep);
        }

        double sr = 48000.0, lpCoef = 0.1, bypassStep = 1.0, bypassPos = 0.0, bypassTarget = 0.0;
        double lp[maxChannels] {};
        Smoothed gain, lo, hi, mix;
        std::atomic<float> peak { 0.0f };
    };
}
