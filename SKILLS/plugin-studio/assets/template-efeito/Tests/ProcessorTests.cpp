// Testes do processador real (sem interface aberta), sem framework.
// Confere a ponte com ui/index.html lendo o TEXTO do arquivo, padrões = preset 0, estado,
// barramentos mono/estéreo e bypass. Código de saída 0 = tudo passou.
#include "PluginProcessor.h"

#include <cstdio>
#include <map>
#include <random>
#include <regex>
#include <set>
#include <string>

static int checks = 0, failures = 0;
#define CHECK(cond, ...) do { ++checks; if (! (cond)) { ++failures; std::printf ("   FALHOU (linha %d): ", __LINE__); std::printf (__VA_ARGS__); std::printf ("\n"); } } while (0)

static std::string readFile (const char* path) { return juce::File (path).loadFileAsString().toStdString(); }

using Preset = std::map<std::string, double>;   // id do parâmetro -> valor real (bool vira 0/1)

// lê "const PRESETS=[ {n:"...",gain:0,...}, ... ];" do HTML
static std::vector<std::pair<std::string, Preset>> parsePresets (const std::string& html)
{
    std::vector<std::pair<std::string, Preset>> out;
    const auto start = html.find ("const PRESETS = [");
    if (start == std::string::npos) return out;
    const auto end = html.find ("];", start);
    const std::string body = html.substr (start, end - start);

    std::regex obj ("\\{n:\"([^\"]*)\",([^}]*)\\}"), kv ("(\\w+):(-?[0-9.]+|true|false)");
    for (std::sregex_iterator it (body.begin(), body.end(), obj), e; it != e; ++it)
    {
        Preset p;
        const std::string fields = (*it)[2];
        for (std::sregex_iterator k (fields.begin(), fields.end(), kv), ke; k != ke; ++k)
        {
            const std::string v = (*k)[2];
            p[(*k)[1]] = v == "true" ? 1.0 : v == "false" ? 0.0 : std::stod (v);
        }
        out.emplace_back ((*it)[1], p);
    }
    return out;
}

static std::string kindOf (juce::RangedAudioParameter* p)
{
    if (dynamic_cast<juce::AudioParameterBool*>   (p) != nullptr) return "toggle";
    if (dynamic_cast<juce::AudioParameterChoice*> (p) != nullptr) return "combo";
    if (dynamic_cast<juce::AudioParameterFloat*>  (p) != nullptr) return "slider";
    return "?";
}

static float realDefault (juce::RangedAudioParameter* p) { return p->convertFrom0to1 (p->getDefaultValue()); }
static void setReal (juce::RangedAudioParameter* p, float v) { p->setValueNotifyingHost (p->convertTo0to1 (v)); }

static juce::AudioBuffer<float> noiseBuffer (int ch, int n, unsigned seed)
{
    std::mt19937 rng (seed);
    std::uniform_real_distribution<float> d (-0.5f, 0.5f);
    juce::AudioBuffer<float> b (ch, n);
    for (int c = 0; c < ch; ++c) for (int i = 0; i < n; ++i) b.setSample (c, i, d (rng));
    return b;
}

static bool sameBuffers (const juce::AudioBuffer<float>& a, const juce::AudioBuffer<float>& b)
{
    if (a.getNumChannels() != b.getNumChannels() || a.getNumSamples() != b.getNumSamples()) return false;
    for (int c = 0; c < a.getNumChannels(); ++c)
        for (int i = 0; i < a.getNumSamples(); ++i)
            if (std::islessgreater (a.getSample (c, i), b.getSample (c, i))) return false;   // comparação exata
    return true;
}

// processa em blocos de 512 com o layout pedido; devolve false se o layout foi recusado
static bool processWithLayout (PluginProcessor& proc, const juce::AudioChannelSet& set, juce::AudioBuffer<float>& buf)
{
    juce::AudioProcessor::BusesLayout layout;
    layout.inputBuses.add (set);
    layout.outputBuses.add (set);
    if (! proc.setBusesLayout (layout)) return false;
    proc.prepareToPlay (48000.0, 512);
    juce::MidiBuffer midi;
    for (int pos = 0; pos < buf.getNumSamples(); pos += 512)
    {
        const int n = std::min (512, buf.getNumSamples() - pos);
        juce::AudioBuffer<float> view (buf.getArrayOfWritePointers(), buf.getNumChannels(), pos, n);
        proc.processBlock (view, midi);
    }
    proc.releaseResources();
    return true;
}

int main()
{
    juce::ScopedJuceInitialiser_GUI juceInit;
    std::printf ("Testes do processador\n");

    const auto html = readFile (PLUGIN_UI_HTML);
    CHECK (! html.empty(), "não consegui ler %s", PLUGIN_UI_HTML);

    std::printf ("1) ponte: cada makeParam da UI existe no plugin com o mesmo tipo (e vice-versa)\n");
    {
        PluginProcessor proc;
        std::set<std::string> uiIds;
        std::regex re ("makeParam\\(\"(\\w+)\",\\s*\"(\\w+)\"");
        for (std::sregex_iterator it (html.begin(), html.end(), re), e; it != e; ++it)
        {
            const std::string id = (*it)[1], kind = (*it)[2];
            uiIds.insert (id);
            auto* p = proc.apvts.getParameter (id);
            CHECK (p != nullptr, "a UI usa '%s', mas o plugin não tem esse parâmetro", id.c_str());
            if (p != nullptr) CHECK (kindOf (p) == kind, "'%s': UI diz %s, plugin é %s", id.c_str(), kind.c_str(), kindOf (p).c_str());
        }
        CHECK (! uiIds.empty(), "nenhum makeParam encontrado na UI");
        for (auto* ap : proc.getParameters())
            if (auto* rp = dynamic_cast<juce::RangedAudioParameter*> (ap))
                CHECK (uiIds.count (rp->paramID.toStdString()) == 1, "o parâmetro '%s' do plugin não aparece na UI", rp->paramID.toRawUTF8());
        std::printf ("   %zu parâmetros na UI, %d no plugin\n", uiIds.size(), (int) proc.getParameters().size());
    }

    std::printf ("2) padrões do plugin = preset 0 da UI; presets dentro das faixas\n");
    {
        PluginProcessor proc;
        const auto presets = parsePresets (html);
        CHECK (presets.size() == 8, "esperados 8 presets na UI (achei %zu)", presets.size());
        if (! presets.empty())
        {
            int compared = 0;
            for (auto& [id, v] : presets[0].second)
                if (auto* p = proc.apvts.getParameter (id))
                {
                    ++compared;
                    CHECK (std::abs (realDefault (p) - v) < 1.0e-3, "'%s': padrão %.3f, preset 0 (%s) %.3f", id.c_str(), (double) realDefault (p), presets[0].first.c_str(), v);
                }
            CHECK (compared > 0, "o preset 0 não tem nenhum id de parâmetro");
        }
        for (auto& [name, preset] : presets)
            for (auto& [id, v] : preset)
            {
                auto* p = proc.apvts.getParameter (id);
                CHECK (p != nullptr, "preset '%s' usa '%s', que não é parâmetro", name.c_str(), id.c_str());
                if (p != nullptr)
                {
                    const auto& r = p->getNormalisableRange();
                    CHECK (v >= r.start - 1.0e-6 && v <= r.end + 1.0e-6, "preset '%s': %s = %.3f fora de %.3f..%.3f", name.c_str(), id.c_str(), v, (double) r.start, (double) r.end);
                }
            }
        auto* byp = proc.apvts.getParameter ("bypass");
        CHECK (byp != nullptr && proc.getBypassParameter() == byp, "getBypassParameter() deveria devolver o 'bypass' interno");
        if (byp != nullptr) CHECK (byp->getValue() < 0.5f, "o plugin deveria abrir sem bypass");
    }

    std::printf ("3) estado: salvar e restaurar devolve os mesmos valores\n");
    {
        PluginProcessor a;
        std::mt19937 rng (42);
        std::uniform_real_distribution<float> u (0.0f, 1.0f);
        for (auto* ap : a.getParameters())                     // valores legais (bool vira 0 ou 1)
            if (auto* p = dynamic_cast<juce::RangedAudioParameter*> (ap))
                p->setValueNotifyingHost (p->convertTo0to1 (p->convertFrom0to1 (u (rng))));
        juce::MemoryBlock state;
        a.getStateInformation (state);
        CHECK (state.getSize() > 0, "estado vazio");

        PluginProcessor b;
        b.setStateInformation (state.getData(), (int) state.getSize());
        bool same = a.getParameters().size() == b.getParameters().size();
        for (int i = 0; same && i < a.getParameters().size(); ++i)
            same = std::abs (a.getParameters()[i]->getValue() - b.getParameters()[i]->getValue()) < 1.0e-6f;
        CHECK (same, "os parâmetros restaurados diferem dos salvos");

        juce::MemoryBlock again;
        b.getStateInformation (again);
        CHECK (again == state, "salvar de novo deveria gerar o mesmo estado");

        PluginProcessor c;
        c.setStateInformation ("lixo", 4);   // estado inválido não pode quebrar nem mudar nada
        CHECK (std::abs (c.apvts.getParameter ("gain")->getValue() - c.apvts.getParameter ("gain")->getDefaultValue()) < 1.0e-9f, "estado inválido mudou parâmetros");
    }

    std::printf ("4) barramentos: mono e estéreo (entrada = saída), neutro é identidade\n");
    {
        PluginProcessor proc;
        auto layout = [] (const juce::AudioChannelSet& in, const juce::AudioChannelSet& out)
        {
            juce::AudioProcessor::BusesLayout l; l.inputBuses.add (in); l.outputBuses.add (out); return l;
        };
        CHECK (proc.checkBusesLayoutSupported (layout (juce::AudioChannelSet::mono(), juce::AudioChannelSet::mono())), "mono deveria ser aceito");
        CHECK (proc.checkBusesLayoutSupported (layout (juce::AudioChannelSet::stereo(), juce::AudioChannelSet::stereo())), "estéreo deveria ser aceito");
        CHECK (! proc.checkBusesLayoutSupported (layout (juce::AudioChannelSet::mono(), juce::AudioChannelSet::stereo())), "mono->estéreo deveria ser recusado");

        for (auto set : { juce::AudioChannelSet::mono(), juce::AudioChannelSet::stereo() })
        {
            const int ch = set.size();
            const auto in = noiseBuffer (ch, 4800, 7);
            auto buf = in;
            CHECK (processWithLayout (proc, set, buf), "layout %s recusado", set.getDescription().toRawUTF8());
            CHECK (sameBuffers (buf, in), "%s neutro deveria ser identidade", set.getDescription().toRawUTF8());

            setReal (proc.apvts.getParameter ("gain"), 6.0f);
            auto loud = in;
            processWithLayout (proc, set, loud);
            const float ratio = loud.getMagnitude (0, 4000, 800) / in.getMagnitude (0, 4000, 800);
            CHECK (std::abs (ratio - std::pow (10.0f, 6.0f / 20.0f)) < 0.01f, "%s: GAIN +6 dB deu razão %.3f", set.getDescription().toRawUTF8(), (double) ratio);
            setReal (proc.apvts.getParameter ("gain"), 0.0f);
        }
        CHECK (proc.getLatencySamples() == 0, "latência deveria ser zero");
    }

    std::printf ("5) bypass: saída idêntica à entrada (com ajustes fortes)\n");
    {
        PluginProcessor proc;
        setReal (proc.apvts.getParameter ("gain"), 18.0f);
        setReal (proc.apvts.getParameter ("tone"), -9.0f);
        setReal (proc.apvts.getParameter ("mix"), 80.0f);
        setReal (proc.apvts.getParameter ("bypass"), 1.0f);
        const auto in = noiseBuffer (2, 9600, 11);
        auto buf = in;
        processWithLayout (proc, juce::AudioChannelSet::stereo(), buf);
        CHECK (sameBuffers (buf, in), "bypass deveria ser bit a bit");
    }

    std::printf ("\n%d verificações, %d falhas\n", checks, failures);
    std::printf (failures == 0 ? "TUDO PASSOU\n" : "HÁ FALHAS\n");
    return failures == 0 ? 0 : 1;
}
