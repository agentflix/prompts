# Analisadores e plugins sem saída de áudio (medidor, espectro, scope)

Um analisador não altera o áudio: a única saída é o que ele desenha. Null test, THD e resposta ao impulso
não se aplicam. A comparação vira camadas, da mais exata para a mais cara. Pare quando a camada responder.

| Camada | Mede | Como | Tela? |
|---|---|---|---|
| 1. Metadados | nomes, defaults, faixas, passos, textos de valor, buses (mono/estéreo/5.1), latência, programas | `scripts/paramdump/` (host JUCE headless) + `compare.py` entre original e réplica | não |
| 2. Dados embutidos | presets de fábrica (XML), tooltips, rótulos, IDs, chaves como `channel name`/`channel color` | `strings -a "<plugin>/Contents/MacOS/<bin>"`, `otool -L` (OpenGL/Metal/WebKit) | não |
| 3. Física da réplica | tom a 0 dBFS cai no bin certo, janela, mono, balística, estados independentes | teste numérico do motor (console JUCE com sinais sintéticos) | não |
| 4. Display | forma da curva, suavização, atraso, o que cada modo mostra | `scripts/gen_sinais_analisador.py` + captura da janela dos dois plugins | sim |

## Camada 1 (a mais valiosa por custo)
O `paramdump` carrega o `.vst3` pelo `VST3PluginFormat`, cria a instância e imprime: buses, quais layouts
(mono, estéreo, 5.1, 7.1, discreto) aceita, latência, programas, e por parâmetro nome, default (texto com
unidade), passos, valores discretos e min/max. Roda a mesma coisa no original e na réplica e `compare.py`
mostra só as diferenças. Achados reais deste método (Spectrum 2 x Vitral): o original só aceita mono/estéreo
(a réplica aceitava 1..8), defaults diferentes (average 1, peak decay 1, minDb −192, maxDb −12, spectro gram),
nomes (`minDb`, `logBase`, `mix`), textos (`40 ms`, `-192.00 dB`, `Yes/No`), `slope` discreto de 5 passos.
Carregar a instância dá nomes e valores; o `paramID` string pode vir `?` em VST3 de terceiros.
Compile com `-DJUCE_DIR=<JUCE>`; precisa de `juce_audio_processors` e `JUCE_PLUGINHOST_VST3=1`.

## Camada 2
`strings` revela mais que o esperado: presets embutidos como XML (`<Spectrum2 channel="Mid" blockSize=... presetName=.../>`),
tooltips ("Use 0 dB for white noise or 3 dB for pink noise"), e se o plugin lê metadados do host
(`channel name`/`channel color` = `updateTrackProperties` do JUCE / `IInfoListener` do VST3).
`otool -L` diz como desenha: OpenGL/Metal = curva na GPU; WebKit = UI web. Código DSP compilado
(constantes de média e atraso) **não** aparece em `strings`: tratar como lacuna, nunca inventar.

## Camada 4: o que funciona e o que não
- `screencapture -x` falha com "could not create image from display" sem permissão de Gravação de Tela
  (ou sem sessão gráfica). Peça ao usuário para conceder à terminal, ou use capturas feitas por ele.
- `Component::createComponentSnapshot` não captura janelas nativas aninhadas de editores de plugin
  (devolve vazio/verde); com OpenGL é pior. Não use como medidor.
- Capturas por pixel só são comparáveis se os dois plugins usam os mesmos ajustes: RANGE manual e MIN/MAX
  iguais (dá a escala Y), SLOPE 0 dB, mesma janela. Sempre meça o original e a réplica com o **mesmo extrator**.
- Sinais calibrados: seno 1 kHz −20 dBFS (posição e nível), escada de tons (eixo), ruído branco/rosa (slope),
  burst 1 kHz + silêncio (balística de AVERAGE/PEAK DECAY em quadros sucessivos), L/−L (fase), varredura.
- Avançado, só com permissão e plugin licenciado: interceptar `glBufferData`/`glDrawArrays` num host próprio
  (`DYLD_INSERT_LIBRARIES`) devolve os vértices da curva sem captura de tela. Exige contexto gráfico.

## REAPER e outros hosts
- REAPER não expõe o valor que um analisador desenha. Serve para: renderização offline e null test de plugins
  de **áudio** (`reaper -renderproject`, ReaScript), e para conferir como o host entrega nome/cor da faixa e
  layouts de bus. Null test falha em plugins não lineares ou com aleatoriedade; use tolerância, não nulo exato.
  Ligue a opção do REAPER que informa aos VST que a renderização é offline, se o plugin se comporta diferente.
- Extensão `js_ReaScriptAPI` tem captura de janela para bitmap (LICE): possível rota de screenshot dentro do
  REAPER (não verificada aqui).
- Outras ferramentas: `pluginval` (validação de estabilidade), `auval` (AU), `minihost` e `Plugalyzer` (hosts de
  linha de comando), `pedalboard` (Python). Nenhuma lê o display de um analisador.

## Fontes
- JUCE forum: "Automated testing with REAPER on MacOS" (render + comparação com referência por SoX).
- JUCE forum: "Taking snapshots of a VST GUI", "Get screenshot of a plugin without open it".
- Repositórios: Tracktion/pluginval, shakfu/minihost.

## Camada 4 sem permissão: capturar a janela do PRÓPRIO processo (testado)

`screencapture` e `CGWindowListCreateImage` de outro processo exigem Gravação de Tela, e
`Component::createComponentSnapshot` sai **preto** em editores OpenGL/Metal. O que funciona sem permissão:
hospedar o plugin num app JUCE seu e capturar a **janela do seu próprio processo** com
`CGWindowListCreateImage` (carregado por `dlsym`: o SDK marca como obsoleto, o símbolo existe).
Código pronto em `scripts/snaphost/` (host + `grab.mm` + `analyze.py`). Procedimento:

1. Alimentar sinais controlados em tempo real (`burst`, `onset`, `ladder`, `noise`, `sweep`) e salvar PNGs a 40 ms.
2. Aplicar parâmetros **depois** do editor aparecer e forçando uma mudança (`1-v`, depois `v`): editores só
   sincronizam knobs em eventos de mudança.
3. Calibrar a geometria pelas linhas de grade (dB por pixel, década por pixel) e extrair séries por coluna.
4. Ajustar o modelo: queda linear em dB ou exponencial? por segundo ou **por atualização**? "trava" no fim do knob?
   Teste de ataque exige silêncio antes do tom (cuidado: o tom do pré-roll contamina o "onset").
5. Reproduzir os números no motor (`engine_test`) e rodar o mesmo host no plugin novo para comparar.

Resultados no Spectrum 2: AVERAGE N cai 80/N dB/s; PEAK DECAY N cai 3,2/N dB por atualização (8 = trava);
eixo ~7,2 Hz–Nyquist; GRAM com tempo na vertical, ~70 px/s. Janelas de trial/overlay cobrem parte do gráfico:
meça colunas fora delas.

Lições de medição adicionais (Spectrum 2):
- **Eixo:** meça as linhas de grade em VÁRIOS sample rates (44,1/48/96/192 kHz). Um modelo "até Nyquist" só se confirma assim; tons de teste confundem com harmônicos, prefira a grade em silêncio.
- **Cada modo de eixo tem sua faixa** (LOG BASE 2 começa em ~12,2 Hz; base 10 em ~7,35 Hz): meça os dois.
- **Ataque:** compare modelos (EMA em dB, EMA em potência, janela) por mínimos quadrados; em potência venceu.
- **Seu desenho também erra:** compare a altura de picos estreitos. Spline por pontos médios corta picos de 1 bin pela metade.
