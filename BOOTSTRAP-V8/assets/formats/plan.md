<!--
Modelo de plano do PREVEC V8. Instalado em .context/formats/plan.md
Serve para as duas situações, com o MESMO formato:
  · plano que fica só na conversa (fix, tamanho XS/S)
  · plano salvo em .context/work/<feature>.md (tamanho M/L)
Referenciado pelo PLANNER e pela skill /plan. NÃO copiar o conteúdo para eles.

Seção que não se aplica ao tamanho NÃO existe — não fica vazia com "N/A".
-->

# Modelo de plano

## Os tamanhos

Fonte única da definição. O PLANNER declara o tamanho no início e ele decide quais
seções o plano tem — **nunca** quais campos a task tem.

| Tamanho | Qualifica quando | Extras obrigatórios |
|---|---|---|
| **XS** | Bugfix ou ajuste isolado, 1–2 arquivos, sem contrato novo | — · review do plano é opcional |
| **S** | 1–3 tasks, dentro de um único módulo | — |
| **M** | 4–8 tasks, ou toca contrato entre camadas | Review do plano · delta de arquitetura |
| **L** | Módulo novo, fluxo crítico de negócio, breaking change | + fases · design (se houver UI) · decisão registrada |

**Trava do XS:** não pode tocar contrato público, fluxo crítico, migration nem módulo
novo. Se toca, sobe para M ou L — sem exceção. Sem essa trava o XS vira o caminho
padrão e a documentação desaparece de verdade.

## As seções

Ordem fixa. As colunas dizem em que tamanho cada seção é obrigatória.

| Seção | XS | S | M | L |
|---|---|---|---|---|
| Problema | ✅ | ✅ | ✅ | ✅ |
| Decisões e lacunas | ✅ | ✅ | ✅ | ✅ |
| Escopo | — | ✅ | ✅ | ✅ |
| Abordagem e alternativas | — | — | ✅ | ✅ |
| Impacto | — | ✅ | ✅ | ✅ |
| Riscos | — | — | ✅ | ✅ |
| Fases | — | — | — | ✅ |
| Tasks | ✅ | ✅ | ✅ | ✅ |
| Pronto quando | ✅ | ✅ | ✅ | ✅ |
| Delta de arquitetura | — | — | ✅ | ✅ |

---

## Problema

Dois a quatro fatos observáveis do estado atual. O que está errado ou falta hoje —
sem solução embutida, sem adjetivo.

> Fix pequeno também tem problema declarado. "Corrigir o bug do login" não é
> problema; "o login aceita senha vazia quando o campo vem com espaço" é.

## Decisões e lacunas

**Decidido:** as escolhas que eu fiz para que o executor não tenha que fazer.
Uma linha cada, com o motivo.

**Assumido:** o que eu assumi por falta de resposta — para você discordar agora
e não depois.

## Escopo

**Dentro:** itens concretos.
**Fora (explícito):** o que alguém razoavelmente assumiria que entra, e o motivo
de não entrar. Esta é a linha que evita o crescimento silencioso.

## Abordagem e alternativas

A abordagem escolhida em prosa curta. Depois:

| Alternativa | Trade-off | Por que não |
|---|---|---|

Alternativa com peso arquitetural também vira arquivo em `arch/decisions/`.

## Impacto

| Deployable | Módulo | Camadas | Contrato público muda? |
|---|---|---|---|

Se alguma linha responde "sim" na última coluna: é BREAKING, e exige nomear quem
consome e registrar a decisão.

## Riscos

| Risco | O que quebra | Mitigação |
|---|---|---|

Inclua o risco de reversão: se isso der errado em produção, como se volta.

## Fases

Só no tamanho L. Cada fase é um recorte que **entrega valor e passa nos gates
sozinho** — não é "etapa do meio". Uma fase que não pode ser entregue isolada é
um sinal de que o recorte está errado.

| Fase | Entrega | Tasks |
|---|---|---|

## Tasks — no formato T.A.C.E

Cada task tem quatro campos: **T**arefa · **A**rquivo · **C**omportamento ·
**E**vidência. Eles existem em **qualquer tamanho** — o tamanho regula a extensão de
cada um, nunca o conjunto. Definição e o porquê: `.context/PREVEC.md`.

A razão de ser: o T.A.C.E é a **interface entre um modelo caro que pensa e um barato
que executa**. Cada campo fecha uma brecha de decisão — **A** elimina a busca por
onde mexer, **C** elimina a dúvida sobre o alvo, **E** elimina "pronto" como opinião.
Task com decisão pendente é falha de planejamento.

Tabela primeiro, para dar a visão:

| Task | Deployable | Módulo | Camada | Depende de |
|---|---|---|---|---|

Depois, uma seção por task com os quatro campos. **Nenhum é opcional em nenhum
tamanho** — o que muda com o tamanho é a extensão de cada um, nunca o conjunto.

### TASK-X.Y.Z — <título imperativo curto>

**T — Tarefa**
Uma frase no imperativo. Uma coisa só.

**A — Arquivo**
Lista completa e específica, marcando `(novo)` ou `(editar)`. "Vários arquivos" ou
um diretório sem arquivo reprova no review.

- `path/exato/arquivo.ext` (novo)
- `path/exato/outro.ext` (editar — <o que muda nele>)

**Referência:** `path/do/arquivo-modelo.ext` — o padrão a imitar.
**Imports autorizados:** <lista> · **Proibido:** <lista>

> Estes dois campos são o que impede o executor de sair procurando. Sem eles, o
> modelo barato explora o repositório e é aí que ele alucina.

**C — Comportamento** — em EARS, uma cláusula por comportamento

```
WHEN <evento> THE SYSTEM SHALL <resposta>
IF <condição de erro> THEN THE SYSTEM SHALL <resposta>
WHILE <estado> THE SYSTEM SHALL <resposta contínua>
WHERE <contexto> THE SYSTEM SHALL <resposta contextual>
```

Cobrir o caminho felizes **e** os de erro. Cada cláusula vira caso de teste no E —
se você não consegue escrever a cláusula, o comportamento não está definido.

**E — Evidência**

```bash
$ <comando exato>
# esperado: <resultado literal>
```

Nunca "funciona", "sem erros" ou "testado manualmente".
[Com TDD do vermelho: duas evidências — o comando falhando antes da implementação
e passando depois.]

**Idempotência** — só em task de fluxo crítico:
Chave: `<campo>`. Reprocessar o mesmo evento deve `<comportamento>`.

## Pronto quando

Critérios verificáveis de que a **feature** está entregue — não a soma das tasks.
Comando, rota, tela ou output. É o que o `/ship` confere no fim.

- [ ] <critério verificável>

## Delta de arquitetura

O que esta feature torna obsoleto em `.context/arch/`. O `/ship` aplica isto antes
de commitar — é o mecanismo que impede a arquitetura de virar ficção.

```
ADDED    arch/rules.md #<N>: <regra nova>
MODIFIED arch/modules.yaml: <módulo> passa a poder importar <módulo>
REMOVED  arch/flows.md: <fluxo que deixou de existir>
```

Nada mudou? Escreva `— nenhum`. Deixar a seção em branco é diferente de declarar
que não há delta.
