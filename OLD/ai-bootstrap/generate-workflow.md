# 🔄 Generate Workflow — Fluxo de Desenvolvimento e Validação

> **Incluído pela Fase 2 do INDEX.md**: Gerar o workflow completo de desenvolvimento, QA e Review.

## Instruções para a IA

Leia o `.context/stack.yaml`. Crie o workflow completo em `.context/workflow/` com fluxo PREVC e modelo de validação por evidências.

### Arquivos a criar

#### 1. `.context/workflow/README.md` — Índice

Tabela de todos os fluxos com link e descrição.

#### 2. `.context/workflow/prevc.md` — Workflow PREVC

O workflow principal de desenvolvimento. Todo agent deve respeitar:

```
┌──────────────────────────────────────────────────────┐
│                   PREVC WORKFLOW                      │
├──────────┬──────────┬──────────┬──────────┬──────────┤
│ Planning │ Review   │ Execution│ Validation│ Confirm  │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│ Ler spec │ Review   │ Codificar│ Gates    │ Commit   │
│ Decompor │ de       │ Testes   │ QA       │ Evidence │
│ em tasks │ approach │ Docs     │ Review   │ Close    │
│ Definir  │ antes de │          │ Fix      │          │
│ approach │ começar  │          │ issues   │          │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

Detalhar cada fase:

**P — Planning**
- Ler spec/PRD se existir
- Avaliar tamanho: Quick Fix (< 30min) / Small (< 1 dia) / Feature (> 1 dia)
- Se Feature: decompor em sub-tasks com PM agent
- Definir approach antes de codar
- Skills usadas: `api-design`, `documentation`, `feature-breakdown`

**R — Review (pré-execução)**
- Revisar approach com ARCHITECT (se Feature)
- Para Quick Fix / Small: auto-review (dev revisa próprio approach)
- Skills usadas: `api-design`, `code-review`

**E — Execution**
- Implementar código
- Criar/atualizar testes (OBRIGATÓRIO)
- Documentar (phpDoc/jsDoc) (OBRIGATÓRIO)
- Skills usadas: `laravel-ddd`, `angular-signals`, `test-generation`, etc.

**V — Validation**
- Rodar gates (comandos do `stack.yaml.quality.gates`) — INEGOCIÁVEL
- Se gate falha → corrigir antes de avançar
- QA agent executa: testes unitários + integração + coverage
- REVIEWER agent executa: code review com checklist
- Skills usadas: `code-review`, `test-generation`, `security-audit`

**C — Confirmation**
- Commit com Conventional Commits (`git-commit` agent)
- Evidência: preencher seção no task.md
- Fechar task

#### 3. `.context/workflow/validation-flow.md` — Fluxo de Validação

O fluxo que o ORCHESTRATOR segue para validar se uma tarefa foi realmente concluída:

```
┌──────────────┐
│ TASK DONE?   │
│ (Dev diz sim)│
└──────┬───────┘
       ▼
┌──────────────┐    ┌──────────────┐
│ GATES        │───▶│ Falhou?      │──▶ VOLTA para DEV
│ Executar     │    │              │    (corrigir)
│ todos os     │    └──────────────┘
│ gates        │
└──────┬───────┘
       ▼ (passou)
┌──────────────┐    ┌──────────────┐
│ QA REVIEW    │───▶│ Reprovou?    │──▶ VOLTA para DEV
│ @qa executa  │    │              │    (corrigir issues)
│ - Testes     │    └──────────────┘
│ - Coverage   │
│ - Edge cases │
└──────┬───────┘
       ▼ (aprovou)
┌──────────────┐    ┌──────────────┐
│ CODE REVIEW  │───▶│ Tem 🔴?     │──▶ VOLTA para DEV
│ @reviewer    │    │ (crítico)    │    (corrigir críticos)
│ executa      │    └──────────────┘
│ checklist    │
└──────┬───────┘
       ▼ (sem críticos)
┌──────────────┐
│ EVIDÊNCIAS   │
│ Preenchidas? │
│ - Screenshots│
│ - Test output│
│ - Gate output│
└──────┬───────┘
       ▼ (sim)
┌──────────────┐
│ ✅ CONCLUÍDO │
│ Commit +     │
│ Close task   │
└──────────────┘
```

Detalhar cada bloco:

**GATES (obrigatório, inegociável)**
```bash
# Executar TODOS os gates do stack.yaml
# Backend:  composer gate:all (ou equivalente)
# Frontend: npm run gate:all (ou equivalente)
# Gateway:  pnpm lint && pnpm test && pnpm build (ou equivalente)
```
- Se QUALQUER gate falha → task NÃO pode avançar
- DEV deve corrigir e re-executar
- NÃO perguntar ao usuário se quer pular

**QA REVIEW (@qa agent)**
O QA agent verifica:
- [ ] Testes unitários existem para todo código novo
- [ ] Testes de integração para APIs
- [ ] Coverage >= mínimo configurado no stack.yaml
- [ ] Edge cases cobertos (null, empty, boundary values)
- [ ] Testes de tenant isolation (se multi-tenant)
- [ ] 0 testes skipped

Output do QA:
```markdown
## QA Report
- **Status**: ✅ APPROVED | ❌ REJECTED
- **Coverage**: XX%
- **Tests**: XX passed, 0 failed, 0 skipped
- **Issues found**: (lista se houver)
- **Evidence**: (output dos testes)
```

**CODE REVIEW (@reviewer agent)**
O reviewer verifica com severidade:
- 🔴 **Crítico** (bloqueia): segurança, logic bugs, missing tests, `any`/`unknown`
- 🟡 **Melhoria**: performance, readability, naming
- 🟢 **OK**: nada a reportar

Checklist por camada:
- [ ] phpDoc/jsDoc em classes e métodos públicos
- [ ] Sem `any`/`unknown` no TypeScript
- [ ] `strict_types` em PHP
- [ ] Tenant isolation respeitada
- [ ] Eager loading (sem N+1)
- [ ] `$fillable` explícito (nunca `$guarded = []`)
- [ ] Validação via FormRequest/DTO

Output do Review:
```markdown
## Code Review Report
- **Status**: ✅ APPROVED | ⚠️ APPROVED WITH NOTES | ❌ CHANGES REQUESTED
- **Críticos (🔴)**: X issues
- **Melhorias (🟡)**: X suggestions
- **Detalhes**: (lista de issues)
```

**EVIDÊNCIAS**
Para a task ser considerada concluída, o ORCHESTRATOR exige:
```markdown
## Evidence
- **Gates**: (output colado)
- **Tests**: (output colado)
- **QA**: APPROVED by @qa
- **Review**: APPROVED by @reviewer
- **Screenshots**: (se UI, screenshots do resultado)
```

#### 4. `.context/workflow/task-template.md` — Template de Task

Template que o PM agent usa para criar tasks:

```markdown
# Task: {TÍTULO}

## Context
<!-- Breve descrição do que precisa ser feito -->

## Requirements
- [ ] Requisito 1
- [ ] Requisito 2

## Approach
<!-- Como será implementado (preencher no P do PREVC) -->

## Sub-tasks
- [ ] Sub-task 1
- [ ] Sub-task 2

## Tests Required
- [ ] Teste 1
- [ ] Teste 2

## Gates
- [ ] Backend gates
- [ ] Frontend gates

## Validation
- [ ] QA Review: PENDING
- [ ] Code Review: PENDING

## Evidence
<!-- Preenchido após conclusão -->
- Gates output:
- Test output:
- QA Status:
- Review Status:
- Screenshots:
```

### Verificação Final

- [ ] `prevc.md` criado com todas as 5 fases detalhadas
- [ ] `validation-flow.md` criado com fluxo GATES → QA → REVIEW → EVIDÊNCIA → DONE
- [ ] `task-template.md` criado com seções de Validation e Evidence
- [ ] README.md indexa todos os documentos
- [ ] Fluxo especifica que gates são inegociáveis
- [ ] QA report tem formato padronizado
- [ ] Code review report tem formato padronizado
- [ ] ORCHESTRATOR referencia este workflow

**Retorne para o INDEX.md após concluir.**
