// Host de captura sem Gravação de Tela: carrega um VST3, abre o editor, alimenta um sinal em tempo real
// e salva PNGs do componente (createComponentSnapshot) + dados numéricos opcionais.
// uso: SnapHost <plugin.vst3> <saida/> <cenario> [param=texto ...]
//   cenario: burst | tone | sweep | noise | silence | stepdown
#include <juce_audio_utils/juce_audio_utils.h>
#include <juce_audio_processors/juce_audio_processors.h>

bool grabOwnWindow (void*, const char*);

struct Host : juce::Timer
{
    std::unique_ptr<juce::AudioPluginInstance> plugin;
    std::unique_ptr<juce::DocumentWindow> win;
    juce::File out;
    juce::String scenario;
    double fs = 48000; int bs = 512;
    double t0 = 0, audioT = 0; double lastSnap = -1; int frame = 0;
    juce::Random rnd;
    double phase = 0;
    juce::AudioBuffer<float> buf { 2, 512 };

    float sample (double t)
    {
        const float a = std::pow (10.0f, -20.0f / 20.0f);
        if (scenario == "ladder")
        {
            // vários tons simultâneos para calibrar o eixo de frequência
            static const double fl[] = { 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000, 30000, 40000 };
            float acc = 0; for (double f : fl) if (f < fs * 0.49) acc += 0.05f * (float) std::sin (juce::MathConstants<double>::twoPi * f * t);
            return acc;
        }
        if (scenario == "onset")  return (lateDone && t >= 1.0 && t < 4.0) ? a * std::sin ((float) phase) : 0.0f;
        if (scenario == "tone")    return a * std::sin ((float) phase);
        if (scenario == "burst")   return (std::fmod (t, 8.0) < 3.0) ? a * std::sin ((float) phase) : 0.0f;
        if (scenario == "stepdown") return (t < 3.0 ? a : a * 0.1f) * std::sin ((float) phase);
        if (scenario == "noise")   return a * (rnd.nextFloat() * 2.0f - 1.0f);
        if (scenario == "sweep")   return 0; // tratado abaixo
        return 0.0f;
    }

    void tick()
    {
        const double now = juce::Time::getMillisecondCounterHiRes() * 0.001 - t0;
        while (audioT < now)
        {
            for (int i = 0; i < bs; ++i)
            {
                double t = audioT + i / fs;
                float s;
                if (scenario == "ladder") { s = sample (t); }
                else if (scenario == "sweep")
                {
                    double f = 20.0 * std::pow (1000.0, std::fmod (t, 10.0) / 10.0);
                    phase += juce::MathConstants<double>::twoPi * f / fs;
                    s = 0.1f * std::sin ((float) phase);
                }
                else
                {
                    phase += juce::MathConstants<double>::twoPi * 1000.0 / fs;
                    s = sample (t);
                }
                buf.setSample (0, i, s); buf.setSample (1, i, s);
            }
            juce::MidiBuffer m;
            plugin->processBlock (buf, m);
            audioT += bs / fs;
        }
    }

    void timerCallback() override
    {
        tick();
        if (! kicked && juce::Time::getMillisecondCounterHiRes() * 0.001 - t0 > 0.8)
        {
            // força um evento de mudança: o editor do Spectrum 2 só sincroniza os knobs quando o valor muda
            kicked = true;
            for (auto& kv : late)
                for (auto* p : plugin->getParameters())
                    if (p->getName (40).equalsIgnoreCase (kv.first))
                        p->setValueNotifyingHost (p->getValueForText (kv.second) < 0.5f ? 1.0f : 0.0f);
            return;
        }
        if (! lateDone && juce::Time::getMillisecondCounterHiRes() * 0.001 - t0 > 1.4)
        {
            lateDone = true; if (dumpFn) dumpFn ("apos");
            for (auto& kv : late)
                for (auto* p : plugin->getParameters())
                    if (p->getName (40).equalsIgnoreCase (kv.first)) { p->setValueNotifyingHost (p->getValueForText (kv.second)); }
            t0 = juce::Time::getMillisecondCounterHiRes() * 0.001; audioT = 0; lastSnap = -1; frame = 0;
            for (auto& f : out.findChildFiles (juce::File::findFiles, false, "*.png")) f.deleteFile();
            return;
        }
        const double now = juce::Time::getMillisecondCounterHiRes() * 0.001 - t0;
        if (now - lastSnap >= snapS && win != nullptr)
        {
            lastSnap = now;
            if (auto* peer = win->getPeer())
                grabOwnWindow (peer->getNativeHandle(), out.getChildFile (juce::String::formatted ("w%04d_%06d.png", frame, (int) (now * 1000))).getFullPathName().toRawUTF8());
            if (false)
            {
                auto* ed = win->getContentComponent();
                auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, 1.0f);
                juce::PNGImageFormat png;
                juce::FileOutputStream os (out.getChildFile (juce::String::formatted ("f%04d_%06d.png", frame, (int) (now * 1000))));
                if (os.openedOk()) png.writeImageToStream (img, os);
            }
            ++frame;
        }
        if (now > durationS) juce::JUCEApplicationBase::quit();
    }
    double durationS = 8.0, snapS = 0.1;
    std::function<void(const char*)> dumpFn; std::vector<std::pair<juce::String,juce::String>> late; bool lateDone = false, kicked = false;
};

class App : public juce::JUCEApplication
{
public:
    const juce::String getApplicationName() override { return "SnapHost"; }
    const juce::String getApplicationVersion() override { return "0.1"; }
    void initialise (const juce::String&) override
    {
        auto args = getCommandLineParameterArray();
        if (args.size() < 3) { std::printf ("uso: SnapHost plugin.vst3 out/ cenario [param=texto..]\n"); quit(); return; }
        host.out = juce::File (args[1]); host.out.createDirectory();
        host.scenario = args[2];
        juce::AudioPluginFormatManager fm; fm.addFormat (new juce::VST3PluginFormat());
        juce::OwnedArray<juce::PluginDescription> found;
        juce::VST3PluginFormat vst3; vst3.findAllTypesForFile (found, args[0]);
        juce::String err;
        for (int i = 3; i < args.size(); ++i)
            if (args[i].startsWith ("fs=")) host.fs = args[i].substring (3).getDoubleValue();
        host.plugin = fm.createPluginInstance (*found[0], host.fs, host.bs, err);
        if (! host.plugin) { std::printf ("ERRO %s\n", err.toRawUTF8()); quit(); return; }
        host.plugin->setPlayConfigDetails (2, 2, host.fs, host.bs);
        host.plugin->prepareToPlay (host.fs, host.bs);
        for (int i = 3; i < args.size(); ++i)
        {
            auto k = args[i].upToFirstOccurrenceOf ("=", false, false), v = args[i].fromFirstOccurrenceOf ("=", false, false);
            if (k == "fs") continue;
            if (k == "snapms") { host.snapS = v.getDoubleValue() / 1000.0; continue; }
            if (k == "duration") { host.durationS = v.getDoubleValue(); continue; }
            host.late.push_back ({ k, v });
        }
        auto dump = [&] (const char* tag) {
            for (auto* p : host.plugin->getParameters())
                std::printf ("%s %s = %s (%.3f)\n", tag, p->getName (40).toRawUTF8(), p->getText (p->getValue(), 40).toRawUTF8(), p->getValue());
        };
        auto* ed = host.plugin->createEditorIfNeeded();
        host.dumpFn = dump;
        if (ed == nullptr) { std::printf ("sem editor\n"); quit(); return; }
        host.win = std::make_unique<juce::DocumentWindow> ("snap", juce::Colours::black, 0);
        host.win->setUsingNativeTitleBar (false);
        host.win->setContentNonOwned (ed, true);
        host.win->setTopLeftPosition (50, 50);
        host.win->setVisible (true);
        host.t0 = juce::Time::getMillisecondCounterHiRes() * 0.001;
        host.startTimer (10);
        std::printf ("editor %dx%d\n", ed->getWidth(), ed->getHeight());
    }
    void shutdown() override { host.stopTimer(); host.win.reset(); if (host.plugin) host.plugin->editorBeingDeleted (nullptr); host.plugin.reset(); }
private:
    Host host;
};
START_JUCE_APPLICATION (App)
