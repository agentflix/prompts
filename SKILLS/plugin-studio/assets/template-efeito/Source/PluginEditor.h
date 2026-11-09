#pragma once
#include <juce_gui_extra/juce_gui_extra.h>
#include "PluginProcessor.h"

// Tamanho de projeto da interface (o mesmo do #panel em ui/index.html)
static constexpr int uiDesignWidth = 640, uiDesignHeight = 400;

class PluginEditor : public juce::AudioProcessorEditor, private juce::Timer
{
public:
    explicit PluginEditor (PluginProcessor&);
    ~PluginEditor() override;
    void resized() override;

private:
    void timerCallback() override;
    std::optional<juce::WebBrowserComponent::Resource> getResource (const juce::String& url) const;

    PluginProcessor& proc;

    // ORDEM IMPORTA: relays antes do navegador (as opções do navegador apontam para eles),
    // attachments depois (são destruídos primeiro).
    std::vector<std::unique_ptr<juce::WebSliderRelay>>       sliderRelays;
    std::vector<std::unique_ptr<juce::WebToggleButtonRelay>> toggleRelays;
    std::unique_ptr<juce::WebBrowserComponent> web;
    std::vector<std::unique_ptr<juce::WebSliderParameterAttachment>>       sliderAtt;
    std::vector<std::unique_ptr<juce::WebToggleButtonParameterAttachment>> toggleAtt;

    int lastMeter = std::numeric_limits<int>::min();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PluginEditor)
};
