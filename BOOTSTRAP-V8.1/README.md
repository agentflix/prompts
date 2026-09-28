# PREVEC V8

Bootstrap AI-First agnóstico: lê o projeto (ou o `spec.md` dele) e gera o contexto
que agents de código precisam para trabalhar sem alucinar.

> **PREVEC é um workflow do ia-coders.**
> O V8 é uma evolução da modelagem, não uma reescrita independente.
> Créditos completos a incluir.

## O que muda do V7.1

| | V7.1 | V8 |
|---|---|---|
| Ciclo | 6 fases (PREVC), 4 agents | **as mesmas 6 letras** `P·P·R·E·V·C`, em **3 agents** |
| Agents | 4 (ORCHESTRATOR separado) | **3**: PLANNER **P·P** → BUILDER **E** → REVIEWER **R·V·C** |
| Skills do fluxo | 6 | **3** + skills de contexto sob demanda |
| Artefatos por feature | 8 templates | **1 work file** (+2 opcionais) |
| Onde vivem as skills | `.context/skills` + symlinks | **caminhos nativos** de cada ferramenta |
| Arquitetura | 9 arquivos, 4 derivados | **5 arquivos**, nenhum derivado |
| Campo C do T.A.C.E | prosa livre | **gramática EARS** |
| Atualizar a arquitetura | item de checklist | **delta aplicado pelo `/ship`** |

## Princípios

Os cinco princípios são definidos em **`assets/PREVEC.md`** — não os reproduza aqui
nem em outro lugar. O prompt do bootstrap os cita **por número**, então divergência
entre duas listas quebra a referência.

Em uma linha cada, só para você saber o que vai encontrar lá:
um fato um arquivo · skill é o veículo de contexto · o handoff carrega tudo ·
cerimônia proporcional ao risco · review no fim sobre a feature inteira.

Dois pilares atravessam os cinco, e também estão no `PREVEC.md`:

- **T.A.C.E é a interface entre modelo caro e barato.** O caro pensa e decompõe; o barato executa uma task sem decisão pendente.
- **Nativo, não proprietário.** `AGENTS.md` na raiz, agents nos formatos nativos de Claude e Codex, e `.claude/skills/` como fonte única (Claude Code e opencode leem direto; Codex usa symlink).

## Como usar

Abra o agent na raiz do projeto e passe o prompt:

```
Leia e execute BOOTSTRAP-V8/prompt-prevec-v8.md
```

O bootstrap detecta o projeto, faz as perguntas de setup e gera tudo.

## Estrutura desta pasta

```
BOOTSTRAP-V8/
├── prompt-prevec-v8.md      # o roteiro: 9 passos (0 a 8), execute na ordem
├── README.md                 # este arquivo
└── assets/
    ├── PREVEC.md             # A METODOLOGIA — leitura obrigatória antes do Passo 0
    ├── setup/                # os 9 passos, um arquivo cada + verify.sh
    ├── formats/              # contratos de formato: plan.md e response.md
    ├── agents/               # templates dos 3 papéis: Markdown Claude + TOML Codex
    ├── skills/               # fluxo (plan/build/ship) + contexto + externas
    ├── context/              # templates de arch/, work/ e decisions/
    └── tools/                # colas nativas: AGENTS, Claude settings, Codex config e opencode
```

## O que o bootstrap gera

```
AGENTS.md                     # contrato — até 80 linhas, sempre carregado
CLAUDE.md                     # @AGENTS.md
opencode.json                 # condicional
.claude/{agents,skills,settings.json}
.codex/config.toml                  # Codex: PLANNER padrão + defaults de modelo
.codex/agents/*.toml                # Codex: PLANNER, BUILDER e REVIEWER nativos
.codex/skills → ../.claude/skills   # Codex: skills compartilhadas
.context/
  PREVEC.md                   # a metodologia, auto-contida
  formats/{plan.md,response.md}
  arch/{overview.md,modules.yaml,rules.md,gates.md,flows.md}
  arch/decisions/             # o porquê e as alternativas descartadas
  work/<feature>.md           # spec + tasks + logs + review + delta
  design/                     # condicional
```

### Modelos padrão

| Agent | Claude Code | Codex | Racional |
|---|---|---|---|
| PLANNER | `opus` | `gpt-5.6-sol` · `high` | Decisão, risco e decomposição |
| BUILDER | `sonnet` | `gpt-5.6-terra` · `medium` | Execução delimitada com menor custo |
| REVIEWER | `sonnet` | `gpt-5.6-sol` · `high` | Contratos, edge cases e evidência |

No Claude, `settings.json` seleciona o agent `PLANNER`. No Codex não existe uma
chave nativa `default_agent`; o bootstrap configura a thread principal com o mesmo
modelo e injeta o comportamento do PLANNER via `developer_instructions`. Os agents
TOML ficam disponíveis para delegação nativa.
