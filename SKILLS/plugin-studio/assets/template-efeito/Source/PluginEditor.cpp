#include "PluginEditor.h"
#include <BinaryData.h>

namespace
{
    std::vector<std::byte> toBytes (const char* data, int size)
    {
        return { reinterpret_cast<const std::byte*> (data), reinterpret_cast<const std::byte*> (data) + size };
    }

    // pico linear -> dB x10 inteiro (-900 = silêncio)
    int peakDb10 (float lin)
    {
        if (! (lin > 1.0e-4f)) return -900;
        return juce::jlimit (-900, 240, (int) std::lround (200.0f * std::log10 (lin)));
    }
}

PluginEditor::PluginEditor (PluginProcessor& p) : AudioProcessorEditor (&p), proc (p)
{
    using namespace fx::ids;
    // deve bater com os makeParam() de ui/index.html (o teste do processador confere)
    const juce::StringArray sliders { gain, tone, mix }, toggles { bypass };

    for (auto& id : sliders) sliderRelays.push_back (std::make_unique<juce::WebSliderRelay> (id));
    for (auto& id : toggles) toggleRelays.push_back (std::make_unique<juce::WebToggleButtonRelay> (id));

    auto options = juce::WebBrowserComponent::Options{}
        .withNativeIntegrationEnabled()
        .withResourceProvider ([this] (const auto& url) { return getResource (url); });
    for (auto& r : sliderRelays) options = options.withOptionsFrom (*r);
    for (auto& r : toggleRelays) options = options.withOptionsFrom (*r);

    web = std::make_unique<juce::WebBrowserComponent> (options);
    addAndMakeVisible (*web);

    for (int i = 0; i < sliders.size(); ++i)
        sliderAtt.push_back (std::make_unique<juce::WebSliderParameterAttachment> (*p.apvts.getParameter (sliders[i]), *sliderRelays[(size_t) i], nullptr));
    for (int i = 0; i < toggles.size(); ++i)
        toggleAtt.push_back (std::make_unique<juce::WebToggleButtonParameterAttachment> (*p.apvts.getParameter (toggles[i]), *toggleRelays[(size_t) i], nullptr));

    web->goToURL (juce::WebBrowserComponent::getResourceProviderRoot());

    setResizable (true, true);
    getConstrainer()->setFixedAspectRatio ((double) uiDesignWidth / uiDesignHeight);
    setResizeLimits (uiDesignWidth / 2, uiDesignHeight / 2, uiDesignWidth * 2, uiDesignHeight * 2);
    setSize (uiDesignWidth, uiDesignHeight);
    startTimerHz (30);
}

PluginEditor::~PluginEditor() { stopTimer(); }

void PluginEditor::resized() { web->setBounds (getLocalBounds()); }

std::optional<juce::WebBrowserComponent::Resource> PluginEditor::getResource (const juce::String& url) const
{
    auto path = url.upToFirstOccurrenceOf ("?", false, false).trimCharactersAtStart ("/");
    if (path.isEmpty()) path = "index.html";

    if (path == "index.html")
        return juce::WebBrowserComponent::Resource { toBytes (BinaryData::index_html, BinaryData::index_htmlSize), "text/html" };
    if (path == "js/juce/index.js")
        return juce::WebBrowserComponent::Resource { toBytes (BinaryData::index_js, BinaryData::index_jsSize), "text/javascript" };
    if (path == "js/juce/check_native_interop.js")
        return juce::WebBrowserComponent::Resource { toBytes (BinaryData::check_native_interop_js, BinaryData::check_native_interop_jsSize), "text/javascript" };
    return std::nullopt;
}

// Evento "meter" para a UI: { p: pico de saída em dB x10 }. Só envia quando o valor muda.
void PluginEditor::timerCallback()
{
    const int v = peakDb10 (proc.engine.takePeak());
    if (v == lastMeter) return;
    lastMeter = v;

    auto* o = new juce::DynamicObject();
    o->setProperty ("p", v);
    web->emitEventIfBrowserIsVisible ("meter", juce::var (o));
}
