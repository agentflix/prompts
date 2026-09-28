# Passo 2 — `.context/arch/`

## Por que exatamente estes cinco arquivos

Nenhum deles existe porque "é bom documentar arquitetura". **Cada um existe porque um
campo do T.A.C.E precisa dele para ser preenchível sem que o executor pense.** Essa é
a lógica que decide o que entra e o que é vago:

| Arquivo | Alimenta | O que acontece se ficar vago |
|---|---|---|
| `overview.md` + `modules.yaml` | Campo **A** — quais arquivos, qual camada, quais imports | O PLANNER não consegue listar a seção A e o executor sai procurando. É exatamente onde ele alucina |
| `rules.md` | Campo **C** + as "regras que valem aqui" do handoff | O handoff vira genérico, ou despeja 30 regras para usar 3 |
| `gates.md` | Campo **E** — comando exato e resultado esperado | "Pronto" volta a ser opinião |
| `flows.md` | A fase PLAN — não esquecer um caminho ao decompor | Fluxo esquecido é task esquecida |

**A pergunta a fazer a cada arquivo que você escrever aqui:**

> Com este arquivo na mão, o PLANNER consegue escrever uma task em que o executor não
> precise decidir nada?

Se a resposta é não, o arquivo está vago — mesmo que pareça completo. `modules.yaml`
com módulos genéricos e `gates.md` sem o comando real *parecem* documentação e não
servem ao T.A.C.E.

## Os cinco arquivos

Um assunto cada, **nenhum derivado**. Cada um tem `_TEMPLATE` nos assets — siga a
estrutura.

| Arquivo | Assunto exclusivo | Molde | Não pode conter |
|---|---|---|---|
| `overview.md` | Diagrama Mermaid das camadas reais + invariantes de fluxo + mapa de módulos | `_TEMPLATE-overview.md` | Comandos de gate, definição de módulo |
| `modules.yaml` | Módulos, o que cada um importa, o que é proibido | `_TEMPLATE-modules.yaml` | Diagrama, regras de código |
| `rules.md` | Regras invioláveis, numeradas, com onde são reforçadas | `_TEMPLATE-rules.md` | Comandos, dependências de módulo |
| `gates.md` | Comandos reais de verificação por deployable + critérios de falha | `_TEMPLATE-gates.md` | Regras de arquitetura |
| `flows.md` | Fluxos do usuário e o fluxo crítico fim-a-fim | `_TEMPLATE-flows.md` | Camadas, módulos |

## Proibido gerar

| Arquivo | Por quê |
|---|---|
| `modules.md` | Derivado de `modules.yaml`. O diagrama de módulos vai em `overview.md` |
| `context-snapshot.md` | Cache de outros arquivos. As regras ficam em `rules.md`; o resumo, no `AGENTS.md` |
| `project-state.yaml` | Métrica mantida à mão divergindo do repositório na primeira semana |
| `context-version.yaml` | Existia para gerenciar a regeneração de derivados. Sem derivados, não tem função |

O `verify.sh` do Passo 7 falha se algum destes existir.

## `rules.md` é a constituição

É o arquivo que mais custa errar, porque todo agent decide a partir dele.

- Cada regra é uma **afirmação verificável**, não um conselho. "Toda query mora no repositório" e não "prefira repositórios".
- Cada regra diz **onde é reforçada** quando houver: linter, script de auditoria, teste, revisão manual.
- Regra só muda por **decisão explícita** registrada em `decisions/`.
- Se o projeto tem documento canônico próprio (um `PATTERN.md`, um guia de arquitetura), **referencie a seção dele** em vez de reescrever a regra. Regra copiada é a origem de toda divergência.

### O bloco "Dados, API, segurança e código"

O `_TEMPLATE-rules.md` traz um bloco final de 15 regras — erro em português, envelope
JSON, `fallback`, sem `any`, migration em vez de SQL avulso, paginação no servidor,
escape de filtro, ameaça modelada, RPC para cruzar registro, gate em dado de usuário,
análise de DBA, sem comentário, e "boa prática" não escrita vira decisão.

**Copie o bloco inteiro** quando o projeto tem API, banco ou consumo de dado externo.
São invariantes que valem em toda task: é exatamente o tipo de coisa que o BUILDER
reescreve por conta própria se a task não citar, e que o REVIEWER não consegue
inventar na hora do review.

Adapte **só** o que está marcado `[ADAPTAR]` — idioma, componente de notificação,
mecanismo de RPC, coluna do tenant, config do linter, e o estado atual do gate. O
resto vai literal, e apontar o arquivo do projeto onde o padrão já está implementado
(quando existe) vale mais que descrever o padrão de novo.

Projeto **sem** API e **sem** banco — biblioteca, CLI offline — pula o bloco e deixa
uma linha no arquivo dizendo que pulou, para não parecer esquecimento.

Duas honestyades que o bloco impõe, e que valem para qualquer regra nova:

1. **Sem âncora mecânica, escreva "revisão".** Na primeira geração quase nenhuma tem
   linter, porque o projeto ainda não tem o código que o linter verificaria. Prometer
   reforço que não existe é pior que não prometer.
2. **Se o objeto da regra ainda não existe no código — envelope de API, gate, schema —
   diga isso na regra.** O agente precisa saber que aquilo é decisão pendente, não
   premissa.

## Ordem de escrita

`modules.yaml` → `rules.md` → `gates.md` → `flows.md` → `overview.md` por último,
porque o diagrama depende de você já ter fechado camadas e módulos.

## Nada de resumo

Não gere nenhum arquivo cujo conteúdo seja "o resumo de outros". O resumo que os
agents leem sempre é o `AGENTS.md`, e ele é gerado no Passo 5 — depois destes, e
apontando para eles.

➡️ Próximo: `assets/setup/3-agents.md`
