#pragma once
#include <juce_audio_processors/juce_audio_processors.h>
#include "Parameters.h"
#include "dsp/Engine.h"

class PluginProcessor : public juce::AudioProcessor
{
public:
    PluginProcessor();
    ~PluginProcessor() override = default;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported (const BusesLayout&) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return "__PLUGIN_DISPLAY__"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    // O bypass do host usa o BYPASS interno (com crossfade) em vez do processBlockBypassed padrão.
    juce::AudioProcessorParameter* getBypassParameter() const override { return apvts.getParameter (fx::ids::bypass); }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram (int) override {}
    const juce::String getProgramName (int) override { return {}; }
    void changeProgramName (int, const juce::String&) override {}

    void getStateInformation (juce::MemoryBlock&) override;
    void setStateInformation (const void*, int) override;

    juce::AudioProcessorValueTreeState apvts;
    fx::Engine engine;   // público: o editor lê o medidor (atômico, sem lock)

private:
    fx::Params readParams() const;

    // guardados no construtor: a thread de áudio nunca procura parâmetro por nome
    std::atomic<float>* gainP = nullptr;
    std::atomic<float>* toneP = nullptr;
    std::atomic<float>* mixP = nullptr;
    std::atomic<float>* bypassP = nullptr;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PluginProcessor)
};
