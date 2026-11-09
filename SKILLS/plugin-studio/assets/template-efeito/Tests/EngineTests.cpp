// Testes do motor de DSP (dsp/Engine.h), sem JUCE e sem framework.
// Saída: uma linha por grupo, falhas detalhadas e um resumo. Código de saída 0 = tudo passou.
#include "dsp/Engine.h"

#include <cmath>
#include <cstdio>
#include <limits>
#include <random>
#include <vector>

static int checks = 0, failures = 0;
#define CHECK(cond, ...) do { ++checks; if (! (cond)) { ++failures; std::printf ("   FALHOU (linha %d): ", __LINE__); std::printf (__VA_ARGS__); std::printf ("\n"); } } while (0)

using Buf = std::vector<float>;
static constexpr double SR = 48000.0;

static Buf noise (int n, unsigned seed, float amp = 0.5f)
{
    std::mt19937 rng (seed);
    std::uniform_real_distribution<float> d (-amp, amp);
    Buf b ((size_t) n);
    for (auto& x : b) x = d (rng);
    return b;
}

static bool allFinite (const Buf& b)
{
    for (auto x : b) if (! std::isfinite (x)) return false;
    return true;
}

static bool sameSamples (const Buf& a, const Buf& b)
{
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) if (a[i] != b[i]) return false;
    return true;
}

static fx::Params params (float g, float t, float m, bool byp = false)
{
    fx::Params p; p.gainDb = g; p.toneDb = t; p.mixPct = m; p.bypass = byp; return p;
}

// processa L/R em blocos de tamanho fixo, com parâmetros constantes
static void run (fx::Engine& e, Buf& l, Buf& r, int block)
{
    for (size_t i = 0; i < l.size(); i += (size_t) block)
    {
        const int n = (int) std::min ((size_t) block, l.size() - i);
        e.process (l.data() + i, r.data() + i, n);
    }
}

int main()
{
    std::printf ("Testes do motor de DSP\n");

    std::printf ("1) saída finita nos extremos (ganhos máximos, entrada enorme, NaN e Inf na entrada)\n");
    {
        const float gains[] { -24.0f, 24.0f, 1000.0f, -1000.0f }, tones[] { -12.0f, 12.0f, 99.0f }, mixes[] { 0.0f, 50.0f, 100.0f, 400.0f };
        bool ok = true;
        for (auto g : gains) for (auto t : tones) for (auto m : mixes)
        {
            fx::Engine e; e.setParams (params (g, t, m)); e.prepare (SR);
            Buf l = noise (4096, 1, 1.0f), r = noise (4096, 2, 1.0f);
            l[100] = 1.0e30f; r[200] = -1.0e30f;
            l[300] = std::numeric_limits<float>::quiet_NaN(); r[400] = std::numeric_limits<float>::infinity();
            run (e, l, r, 512);
            ok = ok && allFinite (l) && allFinite (r);
        }
        CHECK (ok, "alguma combinação extrema gerou NaN/Inf");

        fx::Engine e; e.setParams (params (0, 0, 100)); e.prepare (SR);
        fx::Params bad; bad.gainDb = std::numeric_limits<float>::quiet_NaN(); bad.toneDb = std::numeric_limits<float>::infinity(); bad.mixPct = -std::numeric_limits<float>::infinity();
        e.setParams (bad);
        Buf l = noise (2048, 3), r = noise (2048, 4);
        run (e, l, r, 256);
        CHECK (allFinite (l) && allFinite (r), "parâmetros NaN/Inf geraram saída inválida");
    }

    std::printf ("2) silêncio entra, silêncio sai\n");
    {
        bool ok = true;
        for (auto p : { params (24, 12, 100), params (-24, -12, 30), params (6, 3, 0), params (0, 0, 100, true) })
        {
            fx::Engine e; e.setParams (p); e.prepare (SR);
            Buf l (8192, 0.0f), r (8192, 0.0f);
            run (e, l, r, 333);
            for (size_t i = 0; i < l.size(); ++i) ok = ok && l[i] == 0.0f && r[i] == 0.0f;
        }
        CHECK (ok, "entrada zerada deveria gerar saída zerada");

        // depois de sinal forte, a cauda do filtro tem que morrer e não virar denormal eterno
        fx::Engine e; e.setParams (params (12, 12, 100)); e.prepare (SR);
        Buf l = noise (4800, 5), r = noise (4800, 6);
        run (e, l, r, 512);
        Buf zl (48000, 0.0f), zr (48000, 0.0f);
        run (e, zl, zr, 512);
        CHECK (std::abs (zl.back()) < 1.0e-20f && std::abs (zr.back()) < 1.0e-20f, "a cauda não decaiu (%g)", (double) zl.back());
        CHECK (e.latencySamples() == 0, "latência deveria ser zero");
    }

    std::printf ("3) bit a bit: MIX 0 %% e ajustes neutros devolvem a entrada exata\n");
    {
        for (auto p : { params (12, 6, 0), params (-24, -12, 0), params (0, 0, 100) })
        {
            fx::Engine e; e.setParams (p); e.prepare (SR);
            const Buf inL = noise (9000, 7), inR = noise (9000, 8);
            Buf l = inL, r = inR;
            run (e, l, r, 480);
            CHECK (sameSamples (l, inL) && sameSamples (r, inR), "gain %.1f tone %.1f mix %.0f deveria ser identidade", (double) p.gainDb, (double) p.toneDb, (double) p.mixPct);
        }
        // mono (r == nullptr)
        fx::Engine e; e.setParams (params (0, 0, 100)); e.prepare (SR);
        const Buf in = noise (3000, 9);
        Buf m = in;
        e.process (m.data(), nullptr, (int) m.size());
        CHECK (sameSamples (m, in), "mono neutro deveria ser identidade");

        // depois de uma rampa, o neutro volta a ser exato (a suavização encosta no alvo)
        fx::Engine e2; e2.setParams (params (9, -5, 70)); e2.prepare (SR);
        Buf a = noise (4800, 10), b = noise (4800, 11);
        run (e2, a, b, 256);
        e2.setParams (params (0, 0, 100));
        Buf c = noise (24000, 12), d = noise (24000, 13);
        run (e2, c, d, 256);
        const Buf c2 = noise (24000, 14), d2 = noise (24000, 15);
        Buf c3 = c2, d3 = d2;
        run (e2, c3, d3, 256);
        // o filtro guarda estado, mas com ganhos 1 o termo dele é multiplicado por zero
        CHECK (sameSamples (c3, c2) && sameSamples (d3, d2), "neutro depois de rampa deveria ser identidade");
    }

    std::printf ("4) mesmo resultado para blocos de 1, 7, 64, 512 e 4096 amostras\n");
    {
        const Buf inL = noise (20000, 20), inR = noise (20000, 21);
        Buf refL, refR;
        bool ok = true;
        for (int block : { 1, 7, 64, 512, 4096 })
        {
            fx::Engine e; e.setParams (params (0, 0, 100)); e.prepare (SR);
            e.setParams (params (7.5f, -4.0f, 70.0f));        // começa com rampa: a suavização entra no teste
            Buf l = inL, r = inR;
            run (e, l, r, block);
            if (refL.empty()) { refL = l; refR = r; }
            else if (! sameSamples (l, refL) || ! sameSamples (r, refR)) { ok = false; std::printf ("   bloco %d difere\n", block); }
        }
        CHECK (ok, "a saída depende do tamanho de bloco");
    }

    std::printf ("5) suavização sem saltos (GAIN -24 -> +24 dB, BYPASS liga e desliga)\n");
    {
        fx::Engine e; e.setParams (params (-24, 0, 100)); e.prepare (SR);
        e.setParams (params (24, 0, 100));
        Buf l ((size_t) SR / 4, 0.25f), r ((size_t) SR / 4, 0.25f);   // DC: a saída é 0.25 * ganho
        run (e, l, r, 64);
        const double total = 0.25 * (std::pow (10.0, 24.0 / 20.0) - std::pow (10.0, -24.0 / 20.0));
        double maxStep = 0.0;
        for (size_t i = 1; i < l.size(); ++i) maxStep = std::max (maxStep, (double) std::abs (l[i] - l[i - 1]));
        CHECK (maxStep < 0.01 * total, "salto de %.4f por amostra (limite %.4f)", maxStep, 0.01 * total);
        const double target = 0.25 * std::pow (10.0, 24.0 / 20.0);
        CHECK (std::abs (l.back() - target) < 1.0e-4 * target, "ganho não chegou ao alvo (%.5f de %.5f)", (double) l.back(), target);
        // ~5 ms de constante de tempo: em 50 ms já está a menos de 0.1 % do alvo
        CHECK (std::abs (l[(size_t) (0.05 * SR)] - target) < 1.0e-3 * target, "suavização lenta demais");

        // bypass: rampa de ~15 ms, sem degrau, e termina exatamente na entrada
        fx::Engine b; b.setParams (params (12, 0, 100)); b.prepare (SR);
        b.setParams (params (12, 0, 100, true));
        Buf bl ((size_t) (0.05 * SR), 0.25f), br ((size_t) (0.05 * SR), 0.25f);
        run (b, bl, br, 32);
        double bStep = 0.0;
        for (size_t i = 1; i < bl.size(); ++i) bStep = std::max (bStep, (double) std::abs (bl[i] - bl[i - 1]));
        const double wet = 0.25 * std::pow (10.0, 12.0 / 20.0);
        CHECK (bStep < 0.01 * (wet - 0.25), "bypass com salto de %.4f", bStep);
        CHECK (bl[(size_t) (0.012 * SR)] > 0.25f, "crossfade do bypass terminou cedo demais");
        CHECK (bl.back() == 0.25f, "bypass deveria terminar na entrada exata (%.6f)", (double) bl.back());
    }

    std::printf ("\n%d verificações, %d falhas\n", checks, failures);
    std::printf (failures == 0 ? "TUDO PASSOU\n" : "HÁ FALHAS\n");
    return failures == 0 ? 0 : 1;
}
