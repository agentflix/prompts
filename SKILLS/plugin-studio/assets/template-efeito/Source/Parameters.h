#pragma once
#include <juce_audio_processors/juce_audio_processors.h>

// IDs, tipos e faixas IGUAIS aos makeParam() de ui/index.html (tabela no topo do script):
//   id      tipo    faixa real        padrão
//   gain    slider  -24..+24 dB       0
//   tone    slider  -12..+12 dB       0
//   mix     slider  0..100 %          100
//   bypass  toggle  off/on            off
// Padrões = preset 0 da UI ("Neutro"): o plugin abre sem "*" no nome do preset.
// Ao mudar um parâmetro, mude aqui, na tabela da UI, no makeParam e nos presets (os testes conferem).
namespace fx::ids
{
    inline const juce::String gain = "gain", tone = "tone", mix = "mix", bypass = "bypass";
}

namespace fx
{
    inline juce::AudioProcessorValueTreeState::ParameterLayout createLayout()
    {
        using namespace juce;
        std::vector<std::unique_ptr<RangedAudioParameter>> p;

        auto toNumber = [] (const String& t) { return t.retainCharacters ("-+0123456789.").getFloatValue(); };
        auto dbText   = [] (float v, int) { return (v > 0.049f ? "+" : "") + String (std::abs (v) < 0.05f ? 0.0f : v, 1) + " dB"; };
        auto pctText  = [] (float v, int) { return String (roundToInt (v)) + " %"; };

        auto addFloat = [&] (const String& id, const String& name, NormalisableRange<float> range, float def,
                             std::function<String (float, int)> text)
        {
            p.push_back (std::make_unique<AudioParameterFloat> (ParameterID { id, 1 }, name, range, def,
                AudioParameterFloatAttributes().withStringFromValueFunction (text).withValueFromStringFunction (toNumber)));
        };

        addFloat (ids::gain, "Gain", { -24.0f, 24.0f }, 0.0f, dbText);
        addFloat (ids::tone, "Tone", { -12.0f, 12.0f }, 0.0f, dbText);
        addFloat (ids::mix,  "Mix",  { 0.0f, 100.0f }, 100.0f, pctText);
        p.push_back (std::make_unique<AudioParameterBool> (ParameterID { ids::bypass, 1 }, "Bypass", false));

        return { p.begin(), p.end() };
    }
}
