# PREVEC — a metodologia

> **PREVEC é um workflow criado pelo ia-coders.** Este documento é a versão V8 dele,
> mantida junto do bootstrap para que o repositório não dependa de nenhuma fonte
> externa. Crédito ao ia-coders pela metodologia original.

Documento auto-contido: descreve **o que** o PREVEC é e **por que** ele é assim.
O **como** de cada fase mora nas skills — este arquivo não repete procedimento.

---

## O problema que ele resolve

Agent de código alucina quando precisa decidir. Quanto mais decisão pendente numa
instrução, mais espaço para inventar arquivo, padrão ou comportamento que não existe.

O PREVEC separa **quem decide** de **quem executa**, e usa o T.A.C.E como interface
entre os dois.

## O ciclo — as seis letras do PREVEC

O nome não é rótulo: **cada letra é uma fase**, e as seis somadas são o ciclo.

| Letra | Fase | O que acontece | Termina quando |
|---|---|---|---|
| **P** | **P**ré-Planning | Clarify: caçar lacunas, ambiguidades, riscos. Perguntar o que o código não responde | As lacunas estão fechadas |
| **P** | **P**lanning | Declarar o tamanho. Decompor em tasks T.A.C.E sem decisão pendente | O plano existe, e você escolheu salvar ou seguir |
| **R** | **R**eview | Revisar **o plano**, não o código: as tasks são executáveis por um modelo barato? | Zero task com decisão pendente |
| **E** | **E**xecution | Executar task a task. Loop. Nenhum review, nenhum commit no meio | Todas as tasks implementadas (🟡) |
| **V** | **V**alidation | Revisar a feature inteira: 7 revisores, gates completos, dano colateral | Zero achado bloqueante |
| **C** | **C**onfirm | Aplicar o delta de arquitetura, fechar as tasks, commitar, abrir PR | Feature entregue |

## As letras vivem nos três agents

**Três papéis cobrem as seis letras.** Nenhuma letra fica órfã, e nenhuma pertence a
dois agents — é o que evita handoff redundante:

| Agent | Letras que ele possui | Modelo | Por quê esse modelo |
|---|---|---|---|
| **PLANNER** | **P** · **P** — Pré-Planning e Planning | caro | A decisão é o produto: lacunas, tradeoffs, riscos, decomposição. Também coordena, porque coordenar é a continuação de planejar |
| **BUILDER** | **E** — Execution | barato | Se a task ficou boa, não sobrou decisão. É onde modelo barato entrega bem |
| **REVIEWER** | **R** · **V** · **C** — Review, Validation e Confirm | barato | Verificar contra critério explícito não exige invenção. Três letras porque as três são verificação: do plano, do código e do fecho |

```
      PLANNER              BUILDER            REVIEWER
    ┌─────────┐          ┌─────────┐       ┌───────────────┐
    │  P   P  │─── R ───▶│    E    │──────▶│   V       C   │
    └─────────┘   ▲      └─────────┘       └───────────────┘
                  │            │                    │
                  └────────────┴────────────────────┘
                    R reprova o plano → volta ao PLANNER
                    V reprova o código → volta ao BUILDER
```

O **R** é do REVIEWER mas acontece *antes* do **E**: é a única checagem independente
da decomposição, e existe porque o PLANNER não é bom juiz do próprio plano.

O PLANNER é o **thread principal**, não um subagent: o problema chega onde a conversa
acontece.

Os comandos são atalhos para grupos de letras — `/plan` cobre **P·P·R**, `/build`
cobre **E**, `/ship` cobre **V·C**. Nome curto, letras intactas.

## O T.A.C.E também se divide entre os três

Cada campo tem **um autor, um executor e um auditor**. É o que faz o campo ser
verificável em vez de decorativo:

| Campo | PLANNER escreve | BUILDER usa | REVIEWER audita |
|---|---|---|---|
| **T** — Tarefa | A frase imperativa, uma coisa só | Faz exatamente aquilo, nada mais | O que foi feito bate com o T |
| **A** — Arquivo | A lista específica + Referência + Imports autorizados | Só toca o que está na lista | Diff × união das seções A: arquivo fora é bloqueante |
| **C** — Comportamento | As cláusulas EARS, incluindo os casos de erro | Torna cada cláusula verdadeira | Cada cláusula tem evidência correspondente |
| **E** — Evidência | O comando exato e o resultado esperado | Roda e cola o output real | Roda o gate completo e confere o que o BUILDER reportou |

**A leitura importante:** o T.A.C.E não é formulário do PLANNER. É um contrato de três
vias — se um dos três não cumpre a sua coluna, o campo perde a função. Task com **A**
genérico não dá o que auditar; **E** sem comando não dá o que provar.

## T.A.C.E — a interface

Quatro campos, e **nenhum é opcional em nenhum tamanho**:

| Campo | O que fecha |
|---|---|
| **T**arefa | O que fazer. Uma frase imperativa, uma coisa só |
| **A**rquivo | Onde mexer — lista específica, mais o padrão a imitar e os imports autorizados. Elimina a busca |
| **C**omportamento | O resultado observável, em EARS: `WHEN <evento> THE SYSTEM SHALL <resposta>`. Elimina a dúvida sobre o alvo |
| **E**vidência | Comando exato e resultado esperado. Elimina "pronto" como opinião |

**A regra que decorre:** uma task deve conter zero pensamento. Se o executor precisa
decidir algo, o planejamento falhou — aquela decisão pertencia ao PLANNER.

O tamanho da mudança (XS · S · M · L) regula **os documentos em volta** da task —
nunca os campos dela.

## Os cinco princípios

1. **Um fato, um arquivo, N referências.** Nada é derivado e materializado. Agents e skills apontam para a fonte; nunca reproduzem o conteúdo.
2. **Skill é o veículo de contexto.** Uma skill custa uma linha de descrição e só carrega o corpo quando o assunto aparece. O contexto profundo não fica no prompt sempre.
3. **O handoff carrega tudo.** O prompt do subagent traz arquivos, regras aplicáveis, padrão a imitar e comando de teste. Handoff genérico força o executor a explorar, e explorar é onde ele alucina.
4. **Cerimônia proporcional ao risco.** XS não gera artefato nenhum; L gera spec, design e decisão registrada.
5. **Review no fim, sobre a feature inteira.** É o único escopo que enxerga a quebra de contrato *entre* tasks — e é re-invocável quantas vezes forem necessárias.

## Como esta metodologia dita a documentação

**Esta é a parte que governa o bootstrap.** Nenhum arquivo de contexto existe porque
"é bom documentar". Cada um existe porque **um campo do T.A.C.E precisa dele para ser
preenchível sem que o executor pense**:

| Arquivo gerado | Existe para alimentar | Se ele for vago ou ausente |
|---|---|---|
| `arch/overview.md` · `arch/modules.yaml` | O campo **A** — quais arquivos, qual camada, quais imports são permitidos | O PLANNER não sabe listar a seção A, e o executor sai procurando. É onde ele alucina |
| `arch/rules.md` | O campo **C** e as "regras que valem aqui" do handoff — numeradas para serem citadas, não copiadas | O handoff vira genérico ou despeja 30 regras para usar 3 |
| `arch/gates.md` | O campo **E** — comando exato e resultado esperado | "Pronto" volta a ser opinião |
| `arch/flows.md` | A fase PLAN — não esquecer um caminho ao decompor | Fluxo esquecido é task esquecida |
| `arch/decisions/` | O clarify — saber o que já foi decidido antes de decidir de novo | A mesma discussão se repete, e regra revogada volta por engano |
| `AGENTS.md` | O índice: onde cada coisa está. Único arquivo sempre carregado | Todo agent carrega tudo, ou não carrega nada |
| `formats/plan.md` · `formats/response.md` | A forma fixa do plano e das respostas | Cada resposta vem diferente, e não há onde bater o olho |
| `work/<feature>.md` | O estado da feature entre sessões, quando o plano é salvo | O contexto se perde entre uma sessão e a próxima |

**A consequência prática para quem gera a documentação:** ao escrever qualquer um
desses arquivos, a pergunta não é "isto está bem documentado?". É:

> *Com este arquivo na mão, o PLANNER consegue escrever uma task em que o executor
> não precise decidir nada?*

Se a resposta é não, o arquivo está vago — independentemente de parecer completo.

**E ao escrever agents e skills:** eles não repetem esse conteúdo. Eles **apontam**
para os arquivos acima e citam regra **por número**. Um agent que copia a regra cria
duas fontes que divergem na primeira alteração.

## O que ele deliberadamente não tem

- **Fase de PRD.** Virou seção do plano, ou uma decisão registrada.
- **Changelog em pasta.** Com um commit e um PR por feature, é `git log`.
- **Arquivo de sessão entre agents.** O plano — na conversa ou no work file — já é o canal.
- **Agent coordenador separado.** Ele funde no PLANNER.
- **Procedimento neste documento.** O passo a passo de cada fase vive na skill correspondente: `plan`, `build`, `ship`.

## Histórico

- **V7.1** — 6 fases (PREVC), 4 agents, 6 skills de fluxo, 8 artefatos por feature.
- **V8** — as mesmas 6 letras, agora em 3 agents e 3 skills de fluxo, com 1 work file. Contexto por referência e por skill; caminhos nativos de cada ferramenta; T.A.C.E com C em EARS; delta de arquitetura aplicado no fecho.
