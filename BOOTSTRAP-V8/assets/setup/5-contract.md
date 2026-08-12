# Passo 5 — Contrato: `AGENTS.md`

É o **único arquivo sempre carregado** — por todos os agents e pelas três
ferramentas. Ele é índice, não manual.

Molde estrito: `assets/tools/_TEMPLATE-AGENTS.md`. Siga as seções e a ordem.

## Limite: 80 linhas

```bash
wc -l AGENTS.md
```

Passou? Corte nesta ordem:

1. Descrições da tabela de skills → 3 palavras
2. Regras absolutas que já estão em `arch/rules.md` → remova daqui, mantenha o link
3. Tabela de deployables → vira link para `arch/overview.md`
4. Framework T.A.C.E → vira link para `work/_TEMPLATE.md`

## Teto real do Codex

O Codex trunca o conjunto de `AGENTS.md` em **32 KiB** (`project_doc_max_bytes`).
Contrato gordo não é só caro em contexto — é silenciosamente cortado numa das três
ferramentas, e você não recebe aviso.

## O que entra e o que não entra

| Entra | Fica de fora, referenciado |
|---|---|
| Identidade em 3 linhas: o projeto, o idioma, e **o workflow que governa o repositório** — `PREVEC V8 (ia-coders)` com o ciclo | Descrição longa do domínio |
| Deployables: path · stack · gate | Comandos completos → `arch/gates.md` |
| Até 6 regras absolutas | As demais → `arch/rules.md` |
| Mapa de contexto: uma linha por path | Conteúdo de qualquer um deles |
| Ciclo PLAN→BUILD→SHIP com o comando de cada fase | Detalhe de cada fase → a skill |
| Agents: nome · modelos Claude/Codex · papel em uma linha | Regras de cada agent → o arquivo do agent |
| Skills: nome · quando dispara | O corpo da skill |
| T.A.C.E em 3 linhas, com C em EARS | Template completo → `work/_TEMPLATE.md` |

## As 6 regras absolutas

Escolha as que valem em **toda** decisão, não as mais importantes do domínio.
Candidatas típicas:

1. Ler `.context/arch/rules.md` antes de decidir — é a constituição do projeto
2. O documento canônico do projeto (se houver) vence qualquer suposição
3. O que é contrato público não muda sem decisão registrada
4. REVIEWER aprova o plano antes da execução e a feature antes do commit
5. BUILDER não marca ✅, não commita, e não toca arquivo fora da seção A
6. Todo agent termina mostrando o próximo comando com argumentos reais

## Atribuição do workflow

A linha que identifica o **PREVEC V8 (ia-coders)** vive no `AGENTS.md` e **só ali**.

Ele é lido por todos os agents e pelas três ferramentas, então uma linha basta.
Repetir o crédito em cada agent e em cada skill seria exatamente a duplicação que
este bootstrap existe para matar — e quem chega no repositório descobre o workflow
no primeiro arquivo que abre, que é este.

## `CLAUDE.md`

Uma linha:

```
@AGENTS.md
```

Nada mais. Duas fontes de contrato é o começo da divergência — e o Claude Code
resolve o import nativamente.

## Nota do changelog

Inclua no `AGENTS.md`, na seção do ciclo, a linha que substitui a pasta de
changelog:

```
Histórico do dia: git log --since=1.day --format='%h %s'
```

➡️ Próximo: `assets/setup/6-templates.md`
