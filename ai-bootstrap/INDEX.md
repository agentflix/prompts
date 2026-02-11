# 🚀 AI Documentation Bootstrap — INDEX

> **Como usar**: Copie a pasta `.ai-bootstrap/` para a raiz de qualquer projeto. Abra sua IA de preferência (Claude, Copilot, Gemini, Codex) e envie este arquivo como contexto. A IA executará todas as fases automaticamente.

## Instruções para a IA

Você é um **Documentation Architect**. Sua missão é criar toda a estrutura de documentação para IA deste projeto, seguindo as fases abaixo **em ordem**. Ao final, o projeto terá uma documentação completa que permite a qualquer IA coding assistant entender o projeto e trabalhar nele de forma autônoma.

### Regras Inquebráveis

1. **Documentação NÃO gera código** — apenas especifica como criar, editar, testar, fazer gates e commitar
2. **Todo código deve ser testado** — Pest, Vitest, Jest ou equivalente
3. **phpDoc/jsDoc/Docstrings obrigatório** — em toda classe, interface e método público
4. **NUNCA usar `any` ou `unknown`** no TypeScript — tipagens explícitas sempre
5. **`declare(strict_types=1)`** em todo arquivo PHP
6. **Conventional Commits** — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
7. **Modelo Multi-Agent** — ORCHESTRATOR delega para sub-agents especializados
8. **Gates obrigatórios** — nenhuma tarefa é concluída com gate vermelho

---

## 📋 Fases de Execução

Execute todas as fases em ordem. Crie um arquivo `_progress.md` na raiz do projeto para rastrear o progresso.

### Fase 1 — Detecção e Stack

**Objetivo**: Entender o projeto e gerar `stack.yaml`

**Tarefas**:
- [ ] 1.1 — Detectar se o projeto é novo ou existente (verificar se há código-fonte)
- [ ] 1.2 — **Se existente**: ler o prompt `extract-stack.md` e executá-lo para analisar o codebase
- [ ] 1.3 — **Se novo**: ler o prompt `generate-stack.md` e perguntar ao usuário sobre a stack
- [ ] 1.4 — Gerar `.context/stack.yaml` com toda a configuração detectada/informada
- [ ] 1.5 — **REVISÃO**: Verificar se `stack.yaml` contém: `project`, `stack`, `architecture`, `conventions`, `code_rules`, `quality`

**Sub-prompts**: [`extract-stack.md`](./extract-stack.md) | [`generate-stack.md`](./generate-stack.md)

---

### Fase 2 — Agents (Multi-Agent Architecture)

**Objetivo**: Criar agents especializados com modelo multi-agent + sub-agent

**Tarefas**:
- [ ] 2.1 — Ler o prompt `generate-agents.md`
- [ ] 2.2 — Criar `.context/agents/README.md` com índice de agents
- [ ] 2.3 — Criar agents obrigatórios: `orchestrator`, `dev`, `backend`, `frontend`, `dba`, `architect`, `reviewer`, `qa`, `debug`, `doc`, `pm`, `git-commit`
- [ ] 2.4 — Ajustar agents para a stack específica (ex: se não tem frontend, não criar `frontend.agent.md`)
- [ ] 2.5 — **REVISÃO**: Verificar que ORCHESTRATOR referencia todos os sub-agents e que DBA está presente

**Sub-prompt**: [`generate-agents.md`](./generate-agents.md)

---

### Fase 3 — Workflow e Validação

**Objetivo**: Criar o workflow PREVC + fluxo de validação QA/Review

**Tarefas**:
- [ ] 3.1 — Ler o prompt `generate-workflow.md`
- [ ] 3.2 — Criar `.context/workflow/README.md` com índice
- [ ] 3.3 — Gerar `prevc.md` com as 5 fases: Planning, Review, Execution, Validation, Confirmation
- [ ] 3.4 — Gerar `validation-flow.md` com fluxo: GATES → QA → CODE REVIEW → EVIDÊNCIAS → DONE
- [ ] 3.5 — Gerar `task-template.md` com seções de Validation e Evidence
- [ ] 3.6 — **REVISÃO**: Verificar que o ORCHESTRATOR referencia este workflow e que gates são inegociáveis

**Sub-prompt**: [`generate-workflow.md`](./generate-workflow.md)

---

### Fase 4 — Skills

**Objetivo**: Criar skills específicas por framework da stack

**Tarefas**:
- [ ] 4.1 — Ler o prompt `generate-skills.md`
- [ ] 4.2 — Criar `.context/skills/README.md` com índice
- [ ] 4.3 — Para cada framework na stack, criar uma skill com `SKILL.md`, `templates/` e `examples/`
- [ ] 4.4 — Criar skills genéricas: `code-review`, `commit-message`, `test-generation`, `bug-investigation`
- [ ] 4.5 — **REVISÃO**: Verificar que cada skill tem frontmatter YAML válido e instruções claras

**Sub-prompt**: [`generate-skills.md`](./generate-skills.md)

---

### Fase 5 — Documentação Técnica

**Objetivo**: Gerar documentação técnica no `.context/docs/`

**Tarefas**:
- [ ] 5.1 — Ler o prompt `generate-docs.md`
- [ ] 5.2 — Criar `.context/docs/README.md` com índice de documentação
- [ ] 5.3 — Gerar `architecture.md` com DDD, camadas, data flow
- [ ] 5.4 — Gerar `testing-strategy.md` com tipos de teste, cobertura, frameworks
- [ ] 5.5 — Gerar `security.md` com tenant isolation, auth, data protection
- [ ] 5.6 — Gerar `development-workflow.md` referenciando `.context/workflow/`
- [ ] 5.7 — **REVISÃO**: Verificar que cada doc referencia a stack correta

**Sub-prompt**: [`generate-docs.md`](./generate-docs.md)

---

### Fase 6 — AGENTS.md + Symlinks

**Objetivo**: Consolidar tudo em `AGENTS.md` na raiz + criar `CLAUDE.md`

**Tarefas**:
- [ ] 6.1 — Ler o prompt `generate-agents-md.md`
- [ ] 6.2 — Gerar `AGENTS.md` na raiz com: Stack, Rules, Domains, Shared Components, Paths, Gates, Workflow, Agents, Refs
- [ ] 6.3 — Criar symlink `CLAUDE.md → AGENTS.md`
- [ ] 6.4 — **REVISÃO**: Verificar que AGENTS.md tem no máximo ~300 linhas e referencia `.context/`

**Sub-prompt**: [`generate-agents-md.md`](./generate-agents-md.md)

---

### Fase 7 — Sincronização para Ferramentas

**Objetivo**: Distribuir `.context/` para `.github/`, `.claude/`, `.gemini/`

**Tarefas**:
- [ ] 7.1 — Ler o prompt `sync-tools.md`
- [ ] 7.2 — Gerar `.github/copilot-instructions.md` + `.github/agents/*.agent.md`
- [ ] 7.3 — Gerar `.claude/agents/*.md` + `.claude/settings.json`
- [ ] 7.4 — Gerar `.gemini/GEMINI.md` + `.gemini/settings.json`
- [ ] 7.5 — Criar `scripts/sync-context.sh` para automação futura
- [ ] 7.6 — **REVISÃO**: Verificar que os formatos estão corretos para cada ferramenta

**Sub-prompt**: [`sync-tools.md`](./sync-tools.md)

---

### Fase 8 — Auto-Revisão Final

**Objetivo**: Verificar completude e qualidade de tudo que foi gerado

**Tarefas**:
- [ ] 8.1 — Verificar que `.context/` contém: `stack.yaml`, `agents/`, `skills/`, `docs/`, `workflow/`
- [ ] 8.2 — Verificar que cada `README.md` indexa corretamente os conteúdos da pasta
- [ ] 8.3 — Verificar que `AGENTS.md` e `CLAUDE.md` existem na raiz
- [ ] 8.4 — Verificar que `.github/`, `.claude/`, `.gemini/` foram sincronizados
- [ ] 8.5 — Verificar que as regras inquebráveis estão documentadas em AGENTS.md
- [ ] 8.6 — Verificar que o modelo multi-agent com DBA está completo
- [ ] 8.7 — Verificar que o workflow PREVC + validation-flow existem
- [ ] 8.8 — Gerar relatório final no `_progress.md` com status de cada fase
- [ ] 8.9 — Informar o usuário que pode remover a pasta `.ai-bootstrap/`

---

## Checklist Final de Revisão

Antes de considerar o trabalho concluído, marque TODOS os itens:

```markdown
## ✅ Checklist Final

### Estrutura
- [ ] `.context/stack.yaml` existe e está completo
- [ ] `.context/agents/` tem todos os agents necessários
- [ ] `.context/skills/` tem skills por framework
- [ ] `.context/docs/` tem documentação técnica
- [ ] `AGENTS.md` na raiz com ≤ 300 linhas
- [ ] `CLAUDE.md` → symlink para `AGENTS.md`

### Ferramentas
- [ ] `.github/copilot-instructions.md` gerado
- [ ] `.github/agents/*.agent.md` sincronizados
- [ ] `.claude/agents/*.md` sincronizados
- [ ] `.gemini/GEMINI.md` gerado

### Conteúdo
- [ ] Multi-agent com ORCHESTRATOR + sub-agents
- [ ] Agent DBA presente
- [ ] Workflow PREVC completo
- [ ] Validation flow (GATES → QA → REVIEW → EVIDENCE)
- [ ] Task template com seções Validation e Evidence
- [ ] phpDoc/jsDoc documentado nas regras
- [ ] `any`/`unknown` proibido nas regras
- [ ] Gates obrigatórios documentados
- [ ] Testes obrigatórios documentados
- [ ] Conventional Commits nas regras
- [ ] Template base referenciado (se frontend)

### Qualidade
- [ ] Nenhum arquivo vazio
- [ ] Todos os READMEs indexam seus conteúdos
- [ ] Referências cruzadas corretas
- [ ] Stack reflete a realidade do projeto
```

---

## 📁 Sub-prompts disponíveis nesta pasta

| Arquivo | Fase | Descrição |
|---|---|---|
| [`extract-stack.md`](./extract-stack.md) | 1 | Extrair stack de projeto existente |
| [`generate-stack.md`](./generate-stack.md) | 1 | Gerar stack.yaml para projeto novo |
| [`generate-agents.md`](./generate-agents.md) | 2 | Criar agents multi-agent |
| [`generate-workflow.md`](./generate-workflow.md) | 3 | Workflow PREVC + fluxo QA/Review |
| [`generate-skills.md`](./generate-skills.md) | 4 | Criar skills por framework |
| [`generate-docs.md`](./generate-docs.md) | 5 | Gerar documentação técnica |
| [`generate-agents-md.md`](./generate-agents-md.md) | 6 | Consolidar AGENTS.md |
| [`sync-tools.md`](./sync-tools.md) | 7 | Sincronizar ferramentas |
| [`stack-template.yaml`](./stack-template.yaml) | Ref | Template de stack.yaml |
| [`prompts/return-stack.md`](./prompts/return-stack.md) | Aux | Capturar stack de conversa |

> **Após concluir todas as fases**, remova esta pasta `.ai-bootstrap/` do projeto — ela não é necessária após a geração.
