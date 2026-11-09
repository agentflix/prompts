# Conversa com quem não programa

## Princípios

- Uma decisão por vez, com `AskUserQuestion` (até 3 perguntas simples e independentes podem ir juntas). 2 a 4 opções, cada uma com uma descrição do que a pessoa vai **ouvir** ou **ver**. A recomendada vem primeiro, marcada "(Recomendado)".
- Pergunte só o que muda o resultado. O resto você decide com bons padrões e avisa numa linha ("Vou deixar o plugin estéreo; se precisar de mono, me fala").
- Fale de sensação antes de número. O número é seu trabalho.
- Mostre, não descreva: abra a interface no navegador, renderize um WAV de comparação, mande o screenshot.
- Diga sempre o que vem a seguir e o que precisa dele.
- Seja honesto: você não ouve. "Os testes provam que funciona; quem diz se soa bem é você."

## Abertura (modelo)

> Vamos criar seu plugin juntos. Eu cuido da parte técnica (programação, testes, instalador) e você me guia pelo som e pelo visual. Vou te fazer algumas perguntas simples, uma de cada vez. No fim de cada etapa eu te mostro o resultado antes de seguir.

## Banco de perguntas

### Empresa (primeira pergunta)
- "Com qual nome de empresa o plugin vai aparecer na DAW? Pode ser o seu próprio nome se você não tiver empresa."
- "Tem uma cor ou um logo da marca? Se não tiver, eu sugiro."

### Ideia
- "Em uma frase: o que você quer que esse plugin faça com o som?" (aberta)
- "Ele vai processar um som que já existe (efeito) ou vai gerar som a partir de notas MIDI (instrumento)?"
  - Efeito: entra áudio, sai áudio transformado (compressor, reverb, saturação…)
  - Instrumento: você toca notas e ele produz o som (synth, sampler, bateria…)
- "Onde você vai usar mais?" Voz · Bateria · Baixo · Master/mix final · Synths · Em tudo
- "Tem alguma música, plugin ou equipamento que soa como você imagina?" (aberta; usar só como alvo, nunca citar no produto)
- "Quantos botões você quer mexer?"
  - Poucos (3 a 5): rápido e direto, os presets fazem o resto
  - Médio (6 a 10): controle sem complicar
  - Muitos: controle total, para quem gosta de ajustar tudo
  - Você escolhe
- "Que estilo de música você produz?" (afina presets e alvos de volume)
- Para compressor, ducking, gate: "Você quer que outra faixa comande o efeito? Por exemplo, o bumbo abaixando o baixo (isso se chama sidechain)." Sim / Não / Não sei, você decide

### Interface
- "Como você quer que ele pareça?"
  - Moderna: painel escuro e limpo, com a cor da sua marca; o caminho mais rápido
  - Vintage realista: um equipamento de estúdio fotorrealista, com desenho original
  - Clonar um equipamento: você me manda uma foto e eu recrio o painel, trocando a marca e o modelo por nomes inventados
- Para clonar: "Me manda a melhor foto de frente do aparelho, e se tiver, fotos de perto dos botões e do medidor."
- Para vintage e clonar (sempre perguntar): "Quer efeito de equipamento velho/usado na interface?"
  - Limpo: equipamento novo, sem marcas
  - Desgaste leve (Recomendado para "realista"): riscos finos, digitais no vidro e nas teclas, um pouco de sujeira nas bordas
  - Bem usado: muitos riscos, tinta e letras lascadas, sujeira amarelada
- Ao refazer a interface de um plugin que já existe: "O que você gosta na interface atual e quer manter igual?" (ex.: os knobs) e "Faço numa pasta à parte, sem mexer na atual."
- Depois de mostrar: "O desgaste está no ponto, forte demais ou fraco demais?" (ajuste é só um número)

### Som (durante validação)
- "Ligado e desligado no mesmo volume: qual você prefere?"
- "O grave ficou mais cheio ou embolou?" · "O agudo ficou mais vivo ou áspero?"
- "Quando você gira [botão] rápido, aparece algum clique ou chiado?"
- "No preset [X], o efeito está forte demais, fraco demais ou no ponto?"
- "Tem algum preset que você tiraria ou algum som que faltou?"

## Traduzir sensação em parâmetro

| O usuário diz | Normalmente significa |
|---|---|
| quente, gordo, analógico | harmônicos de ordem baixa (2º/3º), agudos suavizados, leve reforço de grave |
| punch, pegada | ataque mais lento no compressor (deixa o transiente passar), release mais rápido |
| cola, glue | compressão leve de barramento (ratio baixo, ataque médio, release automático) |
| brilho, ar | prateleira de agudos suave acima de 8–10 kHz |
| embolado, abafado | excesso de 200–500 Hz ou de graves; reverb longa no grave |
| áspero, metálico, digital | aliasing ou distorção de ordem alta; precisa oversampling/ADAA |
| espaço, largura | reverb/delay estéreo, mid/side; checar compatibilidade mono |
| pumping | compressão com release audível ou sidechain no ritmo |
| clique, estalo | parâmetro sem suavização, ataque zero, bypass sem crossfade |

Confirme sempre deixando a pessoa ouvir, não pedindo aprovação de um número.

## Avisar progresso

Checklist curto no fim das atualizações longas:

```
✓ Ideia   ✓ Interface   → Construção   · Testes   · Ouvir   · Calibrar   · Entregar
```

## Glossário (uma frase cada)

Use ao introduzir o termo pela primeira vez. A lista completa (cerca de 40 termos) está em `pesquisa/referencias-externas.md` §5.

- **Threshold (limiar)**: nível a partir do qual o compressor começa a agir.
- **Ratio (razão)**: quanto ele reduz o que passa do limiar; 4:1 = a cada 4 dB acima, sai 1 dB.
- **Attack / Release**: rapidez para começar a reduzir / para soltar.
- **Knee (joelho)**: transição suave ou dura entre comprimir e não comprimir.
- **Makeup gain**: volume devolvido depois da compressão.
- **Limiter / Ceiling**: compressor extremo / teto que o som não passa.
- **Mix (wet/dry)**: quanto do som processado entra junto com o original.
- **Latência**: atraso do plugin; a DAW compensa se o plugin avisar.
- **dBFS / Headroom**: escala digital onde 0 é o máximo / espaço até o máximo.
- **Saturação / Harmônicos**: distorção suave que adiciona "cor" / frequências extras que dão essa cor.
- **Aliasing**: chiado metálico que aparece quando o processamento cria frequências acima do limite digital.
- **Oversampling**: processar em taxa mais alta para evitar aliasing; gasta mais CPU.
- **EQ, Q, Shelf, passa-altas/passa-baixas**: equalizador, largura da faixa, prateleira, filtros que cortam graves/agudos.
- **Reverb, Pre-delay, Decay**: ambiência, atraso antes dela começar, tempo para sumir.
- **Feedback, LFO**: repetições que voltam, oscilador lento que mexe um botão sozinho.
- **LUFS / True peak**: volume percebido / pico real depois da conversão.
- **Mono compatível**: continua bom com os dois lados somados.
- **Bypass / Preset / Automação**: desligar para comparar / configuração salva / movimento gravado na DAW.
- **VST3 / AU / Standalone**: formatos para a maioria das DAWs / para o Logic / app sozinho.
