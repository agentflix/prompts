# Paridade 1:1 ao recriar um plugin em JUCE (checklist e armadilhas)

Use depois de medir o original (`analisadores-sem-saida.md` para analisadores). Cada item abaixo apareceu num
caso real (Vitral x Spectrum 2) e custou uma rodada de teste no host.

## 1. Metadados antes de pixels
Rode `scripts/paramdump` no original e na réplica e `compare.py`. Corrija com `AudioParameter*Attributes`:
`withStringFromValueFunction` (textos como `40 ms`, `-192.00 dB`, `Yes/No`), `withAutomatable(false)` para extras
que o original não tem. Copie nomes exatos (`minDb`, `logBase`, `mix`) e passos (um `slope` de 5 passos é
`Choice`, não `Float` contínuo).

## 2. Buses
Copie exatamente os layouts aceitos pelo original em `isBusesLayoutSupported`, com entrada == saída. O
`paramdump` lista quais ele aceita (mono, estéreo, 5.1, 7.1, discreto). Suportar mais que o original é
divergência, não bônus.

## 3. Defaults e presets
Os defaults vêm do Init do original, não de palpite. Presets de fábrica costumam estar embutidos como XML
(`strings -a`). Valores que não aparecem no XML ficam como **suposição declarada**.

## 4. Nome e cor da faixa
Override `updateTrackProperties (const TrackProperties&)` (`name`, `colourARGB`). Prioridade: nome digitado >
nome do host > fallback. Roda na thread de mensagem. Se o original tem strings `channel name`/`channel color`,
ele faz o mesmo.

## 5. Programas
`setCurrentProgram` pode vir de qualquer thread e hosts reenviam o programa ao restaurar a sessão. Aplique os
valores via `AsyncUpdater` e ignore índice igual ao atual.

## 6. Armadilhas de código que quebram a paridade
| Erro | Efeito |
|---|---|
| `getRawParameterValue()` tratado como 0..1 (ex.: `* (N-1)`) para `Choice`/`Int` | o valor já é o índice real: Right vira Side, bloco 4096 vira 16384, programa fora da faixa; com UI que reenvia o valor, o parâmetro deriva sozinho |
| nº de canais do engine = `max(host, extras)` para decidir "tem canal R" | mono parece estéreo: Mid −6 dB, Side errado, fase 90° |
| bins calculados com um total e usados com outro (ex.: 512 e 384) | eixo de frequência esticado, tom de 1 kHz aparece em 4,7 kHz |
| decaimento de pico em dB multiplicando por coeficiente < 1 | o pico sobe até 0 dB em vez de cair; decaia em dB/s |
| estado de suavização compartilhado entre vários traços ou janelas | traços se contaminam, AVERAGE depende de quantos editores estão abertos |
| `prepare()` limpando buffers enquanto o timer da UI lê | use-after-free; proteja com lock curto do lado da UI |

## 7. Ponte WebView
Envie valores **reais** (índice para `Choice`) e só reenvie à UI o que o usuário mudou. Depois de cada
sincronização do host, `lastSent` = estado atual; trava curta (~350 ms) de sincronização após cada envio.
Não envie nada antes do primeiro estado vindo do host (senão os defaults da UI sobrescrevem a sessão).
Cor viva como `#RRGGBB` mais `alpha` separado (`toDisplayString(true)` devolve `AARRGGBB` sem `#`).

## 8. UI HTML: cliques e desempenho (WKWebView)
- Camada `position:absolute; inset:0` sobre uma barra engole os cliques dos botões abaixo: `pointer-events:none`
  na camada, `auto` nos filhos. Teste com `document.elementFromPoint` no centro de cada botão (Chrome headless
  com `--dump-dom` num HTML de prova).
- Canvas: resolução = `devicePixelRatio × escala CSS do contêiner`; nunca `shadowBlur` (traço largo e fraco por
  baixo); `quadraticCurveTo` para curvas lisas; valores no piso fora do clip, senão sobra uma linha na borda.
- Um redesenho por `requestAnimationFrame`; pular se `document.hidden`; tween visual só enquanto há movimento.
- DOM: não reescrever texto/CSS var por quadro; comparar assinatura dos parâmetros; `contain: layout paint` nos
  painéis; payload arredondado em 0,1 dB.
- Arco de knob: `ang = A0 + t*(A1-A0)` sem piso, arco vazio em t=0, ponteiro girando.

## 9. Fechar
Rode o paramdump de novo (deve só mostrar divergências intencionais), o teste numérico do motor e o `auval`.
