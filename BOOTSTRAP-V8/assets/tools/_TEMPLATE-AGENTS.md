<!--
_TEMPLATE-AGENTS.md → gera AGENTS.md na raiz

LIMITE: 80 linhas. Medido em dois dry-runs: 60 não cabe, e 70 fecha com folga ZERO num projeto de 3 módulos. O teto que importa é o de 32 KiB do Codex, com ~10x de folga — 80 dá margem sem virar manual. TETO: 32 KiB (o Codex trunca acima disso, em silêncio).

É o ÚNICO arquivo sempre carregado — por todos os agents e pelas três ferramentas.
Ele é ÍNDICE, não manual. Regra: aponta para onde a informação está; nunca a contém.

Ordem das seções é fixa. Não acrescente seção nova sem remover outra.
Ao terminar: wc -l AGENTS.md
-->

# [PROJECT_NAME]

[Uma linha: o que o sistema é.] Idioma de código, docs e commits: **[idioma]**.
Workflow: **PREVEC V8** (ia-coders) — 6 fases `P·P·R·E·V·C` em 3 agents. Metodologia: `.context/PREVEC.md`

| Deployable | Stack | Gate |
|---|---|---|
| `[path]` | [linguagem + framework] | `[comando]` |

## ⛔ Regras absolutas

1. Antes de qualquer decisão técnica: `.context/arch/rules.md` — é a constituição do projeto.
2. [Documento canônico do projeto, se houver] vence suposição. Contrariá-lo exige decisão registrada.
3. [O que é contrato público aqui] não muda sem decisão em `.context/arch/decisions/`.
4. REVIEWER aprova o plano antes da execução, e a feature antes do commit.
5. BUILDER não marca ✅, não commita, e não toca arquivo fora da seção **A** da task.
6. Toda ação concluída termina num bloco de `.context/formats/response.md`, com o próximo comando real.

## 🗂️ Contexto

| Path | Conteúdo |
|---|---|
| `.context/PREVEC.md` | **A metodologia**: ciclo, papéis, T.A.C.E, princípios |
| `.context/arch/rules.md` | Regras invioláveis, numeradas — a constituição |
| `.context/arch/overview.md` · `modules.yaml` | Camadas, módulos, o que cada um pode importar |
| `.context/arch/gates.md` · `flows.md` | Comandos de verificação · fluxos do usuário |
| `.context/arch/decisions/` | Por que não foi de outro jeito |
| `.context/formats/` | Formato do plano e das respostas |
| `.context/work/<feature>.md` | Feature em andamento (quando o plano é salvo) |
| `.claude/agents/` · `.codex/agents/` | Papéis canônicos · configuração nativa Codex |
| `.claude/skills/` · `.codex/skills` | Skills canônicas · symlink para o Codex |

## 🔄 Ciclo

| Letras | Comando | Quem |
|---|---|---|
| **P·P** Pré-Planning + Planning, **R** review do plano | `/plan <problema>` | PLANNER decompõe · REVIEWER revisa o plano |
| **E** Execution | `/build <feature>` | PLANNER despacha BUILDER, uma task por vez |
| **V·C** Validation + Confirm | `/ship <feature>` | REVIEWER: 7 revisores, gate completo, delta, commit, PR |

Histórico do dia: `git log --since=1.day --format='%h %s'`

## 🤖 Agents

| Agent | Claude · Codex | Papel |
|---|---|---|
| PLANNER | `opus` · `gpt-5.6-sol/high` | **P·P** — pensa, decompõe, despacha, supervisiona. Thread principal |
| BUILDER | `sonnet` · `gpt-5.6-terra/medium` | **E** — executa task já resolvida. Não decide |
| REVIEWER | `sonnet` · `gpt-5.6-sol/high` | **R·V·C** — audita o plano, o código e o fecho |

## 🧩 Skills

| Skill | Dispara quando |
|---|---|
| `plan` · `build` · `ship` | Fase do ciclo |
| `[arch-*]` | Task toca aquela camada — o handoff nomeia qual |
| `gates` | Antes de declarar algo pronto |
| `code-review-confiavel` | `/ship` — 7 revisores em subagents |

## 🧱 T.A.C.E — interface entre quem decide e quem executa

**T**arefa (imperativa) · **A**rquivo (específico + Referência + Imports autorizados) ·
**C**omportamento (**EARS**: `WHEN <evento> THE SYSTEM SHALL <resposta>`) · **E**vidência (comando + resultado).
Os quatro existem em qualquer tamanho. Task com **zero decisão pendente** — se o
executor precisa escolher, o planejamento falhou.
Definição: **`.context/PREVEC.md`** · Formato: `.context/formats/plan.md`
