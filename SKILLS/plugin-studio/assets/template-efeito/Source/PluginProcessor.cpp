#include "PluginProcessor.h"
#include "PluginEditor.h"

PluginProcessor::PluginProcessor()
    : AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                                       .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "STATE", fx::createLayout())
{
    gainP   = apvts.getRawParameterValue (fx::ids::gain);
    toneP   = apvts.getRawParameterValue (fx::ids::tone);
    mixP    = apvts.getRawParameterValue (fx::ids::mix);
    bypassP = apvts.getRawParameterValue (fx::ids::bypass);
    jassert (gainP != nullptr && toneP != nullptr && mixP != nullptr && bypassP != nullptr);
}

// entrada e saída iguais: mono ou estéreo
bool PluginProcessor::isBusesLayoutSupported (const BusesLayout& l) const
{
    const auto& in = l.getMainInputChannelSet();
    return in == l.getMainOutputChannelSet()
        && (in == juce::AudioChannelSet::mono() || in == juce::AudioChannelSet::stereo());
}

void PluginProcessor::prepareToPlay (double sampleRate, int)
{
    engine.setParams (readParams());
    engine.prepare (sampleRate);          // começa já nos valores atuais, sem rampa
    setLatencySamples (engine.latencySamples());
}

fx::Params PluginProcessor::readParams() const
{
    fx::Params p;
    p.gainDb = gainP->load();
    p.toneDb = toneP->load();
    p.mixPct = mixP->load();
    p.bypass = bypassP->load() > 0.5f;
    return p;
}

void PluginProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    for (int c = getTotalNumInputChannels(); c < getTotalNumOutputChannels(); ++c)
        buffer.clear (c, 0, buffer.getNumSamples());

    auto bus = getBusBuffer (buffer, true, 0);
    const int n = bus.getNumSamples(), ch = bus.getNumChannels();
    if (ch < 1 || n < 1) return;

    engine.setParams (readParams());
    engine.process (bus.getWritePointer (0), ch > 1 ? bus.getWritePointer (1) : nullptr, n);
}

juce::AudioProcessorEditor* PluginProcessor::createEditor() { return new PluginEditor (*this); }

void PluginProcessor::getStateInformation (juce::MemoryBlock& dest)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, dest);
}

void PluginProcessor::setStateInformation (const void* data, int size)
{
    if (auto xml = getXmlFromBinary (data, size))
        if (xml->hasTagName (apvts.state.getType()))
            apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new PluginProcessor(); }
