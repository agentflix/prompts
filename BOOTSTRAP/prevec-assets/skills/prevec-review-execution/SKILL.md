---
name: prevec-review-execution
description: Revisa a implementação de uma task no workflow PREVEC usando code-review-confiavel com 7 revisores em subagent distinto. Lê a seção da task no session file da feature — não re-lê arquivos de origem. Detecta alucinações, quebras de contrato, erros e regressões antes do CONFIRM. Obrigatório após todo prevec-execute-task. Triggers: "revisar task", "review da execução", "prevec-review-execution". Do NOT use para revisar feature docs ou tasks não implementadas (use PLANNER/REVIEWER diretamente).
metadata:
  author: prevec
  version: '2.0.0'
---

# prevec-review-execution

Valida a implementação de uma task com 7 revisores especializados antes do CONFIRM.
Lê a seção da task no session file da feature — zero re-leitura de arquivos de origem.

## Input

```
/prevec-review-execution [feature] [TASK-X.Y.Z]
```

Exemplo: `/prevec-review-execution importacao-csv TASK-3.1.1`

## Por que este passo é obrigatório

- Detecta alucinações: imports inexistentes, assinaturas erradas, dead code
- Verifica quebra de contrato entre camadas (API ↔ frontend, Domain ↔ Infrastructure)
- Garante grounding: código implementado bate com T.A.C.E da task
- Captura regressões antes do commit
- Reduz falsos positivos via meta-review

## Pré-condições

- Task está 🔄 Em Progresso
- Session file existe em `.context/.session/[feature]-session.md`
- Seção `## TASK-X.Y.Z` tem BUILDER Log preenchido e gates passando

## Processo

### 1. CRÍTICO — Executar em subagent distinto

Este review DEVE ser feito em subagent separado para não contaminar o contexto da implementação.

### 2. Carregar contexto do session file

Ler `.context/.session/[feature]-session.md`.

Localizar a seção `## TASK-X.Y.Z` — contém tudo que precisa:
- **Architecture Snapshot** (no topo do arquivo): stack, regras invioláveis, dependências de módulo
- **T.A.C.E da task**: tarefa, arquivos, comportamento, evidências
- **BUILDER Log**: arquivos modificados, decisões, notas para o reviewer

**NÃO re-ler:** tasks.md, feature.md, project-brain.yaml, architecture.md, dependencies.yaml.
O session file já tem o contexto serializado.

### 3. Carregar skill de review

Ler a skill `code-review-confiavel` instalada no projeto (`.claude/skills/code-review-confiavel/SKILL.md` ou equivalente) completamente antes de iniciar.

### 4. Identificar escopo e determinar tier de review

```bash
git diff --stat
git status
```

Calcular linhas alteradas:

```bash
LINES=$(git diff --stat | tail -1 | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
```

Determinar tier:

| Condição | Tier | Revisores |
|---|---|---|
| < 50 linhas, task simples (1 arquivo ou 1 camada) | **FAST** | 3 |
| 50–200 linhas, task normal | **STANDARD** | 5 |
| > 200 linhas OU cross-camada OU task crítica | **FULL** | 7 |

### 5. Executar revisores por tier

Abrir subagents conforme `references/reviewers.md` da skill `code-review-confiavel` instalada.

Passar para cada revisor o **Architecture Snapshot** + **T.A.C.E** do session — não o arquivo tasks.md original.

**Tier FAST (3 revisores):**
1. **Especialização** — arquitetura e regras do workspace
2. **Grounding** — T.A.C.E do session atendido
3. **Meta-review** — remover achados sem prova

**Tier STANDARD (5 revisores):**
1. **Especialização** — arquitetura e regras
2. **Grounding** — T.A.C.E do session
3. **Second Pass** — releitura integral, omissões
4. **Rastreabilidade** — diff bate com seção A e critérios E
5. **Meta-review** — remover achados sem prova

**Tier FULL (7 revisores — todos):**
1. **Especialização** — arquitetura e regras do workspace
2. **Grounding** — aderência a AGENTS.md, skills, T.A.C.E do session
3. **Second Pass** — releitura integral, omissões, bugs silenciosos
4. **Precision** — filtrar falsos positivos (confiança ≥ 80%)
5. **Human-in-the-Loop** — o que precisa de decisão humana
6. **Rastreabilidade** — diff bate com seção A e critérios E do session
7. **Meta-review** — revisar o review, remover achados sem prova

### 6. Executar gates

Rodar gates conforme `.context/WORKFLOW/validation-flow.md` para o workspace alterado.

### 7. Preencher REVIEWER Log no session

Atualizar a subseção **REVIEWER Log** na seção `## TASK-X.Y.Z` de `.context/.session/[feature]-session.md`:

- Resultado: aprovado sim/não
- Contagem de achados por severidade
- Achados bloqueantes com arquivo:linha (se houver)
- Dados prontos para CHANGELOG (tipo, escopo, descrição)
- Dados prontos para MEMORY (decisão/aprendizado, se houver)

### 8. Decisão

**Aprovado:** nenhum achado bloqueante → atualizar cabeçalho da seção para `Fase PREVC: CONFIRM` → prosseguir

**Reprovado:** achados bloqueantes → manter `Fase PREVC: EXECUTION` → retornar:
```
❌ Review reprovado — [N] bloqueantes:
1. [arquivo:linha] [severidade]: [problema]. [correção sugerida]
2. ...
➡️  Corrigir e rodar: /prevec-execute-task [feature] TASK-[X.Y.Z]
```

## Output (aprovado)

```
✅ Review aprovado — TASK-[X.Y.Z]
📋 Tier: [FAST / STANDARD / FULL] — [N] revisores
📋 Gates: [lista com resultados]
📋 Achados: [N bloqueantes=0 | N médios | N baixos]
📋 Session: .context/.session/[feature]-session.md atualizado
➡️  Próximo: /prevec-finalize-execution [feature] TASK-[X.Y.Z]
```

## Error Handling

- Session ausente: rodar prevec-execute-task novamente para recriar
- Seção TASK-X.Y.Z não encontrada no session: task pode não ter sido iniciada — checar prevec-execute-task
- Subagent indisponível: fazer review local seguindo os 7 escopos e informar limitação
- Gate não pode rodar: registrar motivo e risco residual no session — nunca ignorar silenciosamente
- Achado sem evidência: classificar como pergunta no session, não como bug
