#include <juce_audio_processors/juce_audio_processors.h>
#include <cstdio>

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI init;
    juce::AudioPluginFormatManager fm;
    fm.addFormat (new juce::VST3PluginFormat());
    juce::OwnedArray<juce::PluginDescription> found;
    juce::VST3PluginFormat vst3;
    vst3.findAllTypesForFile (found, argv[1]);
    std::printf ("tipos: %d\n", found.size());
    for (auto* d : found)
    {
        juce::String err;
        auto p = fm.createPluginInstance (*d, 48000.0, 512, err);
        if (! p) { std::printf ("ERRO: %s\n", err.toRawUTF8()); continue; }
        std::printf ("plugin: %s | in=%d out=%d | latency=%d | tail=%.2f | programs=%d\n", d->name.toRawUTF8(),
                     p->getTotalNumInputChannels(), p->getTotalNumOutputChannels(), p->getLatencySamples(),
                     p->getTailLengthSeconds(), p->getNumPrograms());
        for (bool isInput : { true, false })
            for (int b = 0; b < p->getBusCount (isInput); ++b)
            {
                auto* bus = p->getBus (isInput, b);
                std::printf ("  %s bus %d '%s' layout=%s enabledByDefault=%d\n", isInput ? "IN " : "OUT", b,
                             bus->getName().toRawUTF8(), bus->getCurrentLayout().getDescription().toRawUTF8(),
                             (int) bus->isEnabled());
            }
        for (auto cfg : { juce::AudioChannelSet::mono(), juce::AudioChannelSet::stereo(), juce::AudioChannelSet::create5point1(),
                          juce::AudioChannelSet::create7point1(), juce::AudioChannelSet::discreteChannels (3) })
        {
            auto test = p->getBusesLayout();
            if (p->getBusCount (true) > 0) test.getChannelSet (true, 0) = cfg;
            if (p->getBusCount (false) > 0) test.getChannelSet (false, 0) = cfg;
            std::printf ("  suporta in=out=%s: %d\n", cfg.getDescription().toRawUTF8(), (int) p->checkBusesLayoutSupported (test));
        }
        std::printf ("parametros: %d\n", p->getParameters().size());
        for (auto* prm : p->getParameters())
        {
            juce::String line;
            if (auto* wi = dynamic_cast<juce::AudioProcessorParameterWithID*> (prm)) line << wi->paramID;
            else line << "?";
            line << " | " << prm->getName (40) << " | default=" << prm->getDefaultValue()
                 << " (" << prm->getText (prm->getDefaultValue(), 40) << prm->getLabel() << ")"
                 << " | steps=" << prm->getNumSteps() << " | discrete=" << (int) prm->isDiscrete();
            if (prm->isDiscrete() && prm->getNumSteps() <= 16 && prm->getNumSteps() > 1)
            {
                line << " | valores:";
                for (int i = 0; i < prm->getNumSteps(); ++i)
                    line << " [" << prm->getText ((float) i / (float) (prm->getNumSteps() - 1), 40) << "]";
            }
            else
                line << " | min=" << prm->getText (0.0f, 40) << " max=" << prm->getText (1.0f, 40);
            std::printf ("  %s\n", line.toRawUTF8());
        }
        std::printf ("programa atual: %d '%s'\n", p->getCurrentProgram(), p->getProgramName (p->getCurrentProgram()).toRawUTF8());
    }
    return 0;
}
