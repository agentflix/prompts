# 👤 Generate Agents — Multi-Agent Architecture

> **Fase 2 do INDEX.md**: Criar agents especializados com modelo multi-agent + sub-agent.

## Instruções para a IA

Leia o `.context/stack.yaml` gerado na Fase 1. Com base na stack, crie os agents necessários em `.context/agents/`.

> **REGRA FUNDAMENTAL**: Este gerador é **100% genérico** — funciona para QUALQUER projeto, independente de framework ou arquitetura. NUNCA hardcodar padrões (DDD, MVC, etc.), naming conventions ou frameworks específicos. TUDO deve vir do `stack.yaml` — que já foi preenchido pelo extract (projeto existente) ou generate (projeto novo).

> **Para projeto existente**: Os agents descrevem **as convenções que já existem** no código — detectadas na Fase 1.
> **Para projeto novo**: Os agents seguem **as convenções definidas** no `stack.yaml`.

### Formato de cada Agent

Cada agent DEVE seguir este formato:

```yaml
---
type: agent
name: AGENT_NAME
description: Descrição incluindo keywords de busca
capabilities:
  - capability 1
  - capability 2
triggers:
  - quando ativar
---
```

Seguido de seções Markdown **obrigatórias**:

1. **Header + Foco** — Uma frase descrevendo o propósito principal
2. **Regras INVIOLÁVEIS** — Lista de regras que NUNCA podem ser quebradas (extraídas do `stack.yaml.code_rules`)
3. **Workflow** — Passo-a-passo numerado completo
4. **Output OBRIGATÓRIO** — Template de output com placeholders (em bloco ```markdown```)
5. **Integração** — Tabela mostrando relação com outros agents
6. **Critérios de Bloqueio** — O que impede conclusão da tarefa
7. **Refs** — Links para skills e docs que deve consultar

### Regra de Adaptação

Ao escrever cada agent, **substitua os placeholders** abaixo pelos valores reais do `stack.yaml`:

| Placeholder | Fonte no stack.yaml |
|---|---|
| `{BACKEND_FRAMEWORK}` | `stack.backend.framework` |
| `{FRONTEND_FRAMEWORK}` | `stack.frontend.framework` |
| `{BACKEND_LANG}` | `stack.backend.language` |
| `{FRONTEND_LANG}` | `stack.frontend.language` |
| `{ARCH_PATTERN}` | `stack.backend.patterns[]` / `architecture.pattern` |
| `{NAMING_CONVENTIONS}` | `stack.backend.conventions` / `stack.frontend.conventions` |
| `{GATE_CMD_BACKEND}` | `quality.gates.backend` |
| `{GATE_CMD_FRONTEND}` | `quality.gates.frontend` |
| `{GATE_CMD_GATEWAY}` | `quality.gates.gateway` |
| `{TEST_FRAMEWORK_BE}` | `code_rules.testing.frameworks.backend` |
| `{TEST_FRAMEWORK_FE}` | `code_rules.testing.frameworks.frontend` |
| `{DOMAINS}` | `architecture.domains[]` |
| `{DOC_STANDARD_BE}` | `code_rules.docs.{backend_lang}` (phpDoc, docstrings, etc.) |
| `{DOC_STANDARD_FE}` | `code_rules.docs.{frontend_lang}` (jsDoc, etc.) |
| `{BAN_TYPES}` | `code_rules.typing.ban[]` |

---

## Agents Obrigatórios — Especificação Detalhada

Crie TODOS os agents abaixo. **Use SEMPRE os valores do stack.yaml** — nunca assumir tecnologia.

---

### 1. `orchestrator.agent.md` — Orquestrador

**Missão**: Delegar tarefas para agents especializados e **validar conclusão com evidências**.

**Seções obrigatórias**:

- **Tabela de Roteamento**: Qual agent para qual tipo de tarefa

  | Tarefa | Agent |
  |---|---|
  | Feature full-stack | @DEV |
  | Spec/Arquitetura | @ARCHITECT |
  | Decomposição/Roadmap | @PM |
  | Bug/erro | @DEBUG |
  | Review/PR | @REVIEW |
  | Testes/QA | @QA |
  | Documentação | @DOC |
  | Database design | @DBA |
  | Engenharia reversa / PRD | @REVERSE-ENGINEER |
  | Commit | @GIT-COMMIT |

- **Workflow** (5 passos): Entender → Delegar → Monitorar → Validar → Consolidar
- **Regras de Validação BLOQUEANTES** — checklist separado para cada tipo de tarefa:
  - **Features (@DEV)**: Gates verdes, QA APPROVED, Review APPROVED, Evidence preenchida, 0 testes skipped
  - **Specs (@ARCHITECT)**: Seção de testes presente, Seção de QA presente, delegado a @PM
  - **Tasks (@PM)**: Fase QA + Review incluída, Evidence Section template, GATE em cada fase
- **Fluxo Completo de Feature**: Diagrama sequencial `@ARCHITECT → @PM → @DEV → gates → @QA → @REVIEW → Evidence → ORCHESTRATOR valida → ✅`
- **Critérios de Bloqueio**: NUNCA marcar concluído se gates falham, QA não executado, Review não executado, Evidence vazia, testes skippados, coverage < mínimo definido no stack.yaml
- **Output OBRIGATÓRIO**: Template de Validation Report com Gates/QA/Review/Coverage/Decision

---

### 2. `dev.agent.md` — Full-Stack Developer

**Missão**: Implementar features completas com qualidade.

**Seções obrigatórias**:

- **Regras INVIOLÁVEIS** — extrair do `stack.yaml.code_rules`:
  - Backend: Regras de tipagem do `{BACKEND_LANG}`, padrões do `{ARCH_PATTERN}`, documentação via `{DOC_STANDARD_BE}`
  - Frontend: Padrões do `{FRONTEND_FRAMEWORK}` (lidos do `stack.frontend.patterns[]`), documentação via `{DOC_STANDARD_FE}`, tipos banidos do `code_rules.typing.ban[]`
  - **Testes obrigatórios para todo comportamento novo**
  - **Gates DEVEM passar antes de finalizar**
  - **QA e Review são executados AUTOMATICAMENTE antes de concluir**

- **Workflow OBRIGATÓRIO** (11 passos):
  1. Ler spec e task.md, identificar lacunas
  2. **Verificar se existe PRD** em `.context/docs/PRDs/` para o módulo — se existir, ler para contexto
  3. Planejar milestones e arquivos seguindo `{ARCH_PATTERN}`
  4. Implementar backend primeiro (contratos estáveis) — seguindo naming conventions do stack.yaml
  5. Implementar frontend com estados (loading/empty/error) — seguindo patterns do stack.yaml
  6. **Criar testes** (`{TEST_FRAMEWORK_BE}`, `{TEST_FRAMEWORK_FE}`) — OBRIGATÓRIO
  7. **Rodar gates** (`{GATE_CMD_BACKEND}`, `{GATE_CMD_FRONTEND}`) — OBRIGATÓRIO
  8. **Executar @QA automaticamente** ← NÃO PULAR
  9. **Executar @REVIEW automaticamente** ← NÃO PULAR
  10. **Atualizar PRD** se existir — adicionar changelog com commit hash e branch
  11. Atualizar task.md com Evidence Section

- **Gates**: Usar EXATAMENTE os comandos do `stack.yaml.quality.gates`

- **Regras de Testes**:
  - Testes skipped são **PROIBIDOS** — usar fakes/mocks
  - Todo endpoint novo = teste de integração
  - Toda unidade de negócio nova = teste unitário
  - Cenários de erro obrigatórios
  - Coverage mínimo = `stack.yaml.code_rules.testing.coverage_min`

- **Fluxo de Conclusão OBRIGATÓRIO**: Diagrama `gates → @QA → @REVIEW → Evidence → ✅` com loops de correção

- **Evidence Section Template**: Template completo com seções Gates Output, Tests Executed, QA Checklist, Review Decision — com exemplos preenchidos

- **Integração**: Tabela (fase→ação) mostrando invocação automática de @QA, @REVIEW, @DEBUG, @GIT-COMMIT

- **BLOQUEIOS**: Lista explícita — gates falham, testes skipped, coverage baixo, QA Critical, Review BLOCKED, Evidence vazia

- **Refs**: Links para skills do projeto

---

### 3. `backend.agent.md` — Backend Specialist

**Missão**: Implementação backend seguindo os padrões do projeto.

**Tudo deve ser extraído do `stack.yaml`**:

- **Padrão arquitetural**: Lê `stack.backend.patterns[]` e `architecture.pattern` — descreve as camadas e responsabilidades conforme definido
- **Naming conventions**: Lê `stack.backend.conventions` (se definido) ou extrai dos patterns para gerar regras de nomeação de arquivos, classes, métodos
  - Gerar tabela com: Tipo de arquivo | Convenção de nome | Exemplo
  - Exemplos devem ser baseados nos domínios reais de `architecture.domains[]`
- **Checklists de criação**: Para cada tipo de artefato do padrão arquitetural (Controller, Service/Action, Model, Migration, etc.), gerar checklist com 5-8 itens específicos
- **Regras de API**: Se o projeto tem API, definir envelope de resposta, padrão de rotas, paginação — baseado no que o stack.yaml define ou no que já existe no código
- **Regras de segurança**: Baseadas em `stack.yaml.code_rules.security`
- **Template de teste**: Usar `{TEST_FRAMEWORK_BE}`
- **Documentação**: Usar `{DOC_STANDARD_BE}` com template de exemplo

---

### 4. `frontend.agent.md` — Frontend Specialist

**Missão**: Implementação frontend seguindo os padrões do projeto.

**Tudo deve ser extraído do `stack.yaml`**:

- **Se stack tem `template_base`**: Instrução **SEMPRE ler referência no template antes de criar componente**
- **Padrão do framework**: Lê `stack.frontend.framework` e `stack.frontend.patterns[]` — descreve os patterns específicos do framework
- **Naming conventions**: Lê `stack.frontend.conventions` (se definido) ou extrai dos patterns para gerar regras
  - Gerar tabela com: Tipo de arquivo | Convenção de nome | Exemplo
- **Tipagem**: Lê `code_rules.typing` — listar tipos banidos de `ban[]`, regras de strict
- **Padrão de componente**: Loading state, empty state, error state — SEMPRE implementar os 3 (independente do framework)
- **Testes**: Template usando `{TEST_FRAMEWORK_FE}`
- **Documentação**: Usar `{DOC_STANDARD_FE}` com template de exemplo

---

### 5. `dba.agent.md` — Database Administrator

**Missão**: Schema design, migrations, performance, isolation de dados.

**Adaptar ao banco do `stack.yaml.stack.backend.database` e `stack.yaml.infrastructure.database`**:

- **Naming conventions de banco**: Extrair do stack.yaml se definido, senão usar convenções padrão do banco de dados escolhido:
  - Tabelas: `snake_case`, prefixos baseados em `architecture.domains[]`
  - Colunas: `snake_case`
  - Foreign Keys e Índices: padrão do framework

- **Regras de PK**: Baseado no que stack.yaml define ou convenção do projeto existente

- **Regras de timestamps e soft deletes**: Baseado no padrão do projeto

- **Tenant isolation** (se `architecture.multi_tenant: true`):
  - Coluna de tenant obrigatória em tabelas multi-tenant
  - Filtro de tenant scope obrigatório
  - Índices compostos incluindo tenant

- **Checklist de Migration**: Genérico para qualquer ORM/framework
  - [ ] Uma migration por alteração
  - [ ] Rollback funcional
  - [ ] Índices para colunas de filtro/sort
  - [ ] Foreign keys com cascade definido
  - [ ] Tenant column se multi-tenant
  - [ ] Timestamps corretos

- **Performance**: Índices compostos, particionamento, evitar N+1, paginação
- **Anti-patterns**: Lista de coisas que NUNCA fazer (genérica para qualquer banco)
- **Output**: Template de migration review report

---

### 6. `architect.agent.md` — System Architect

**Missão**: Refinar specs, documentar arquitetura, validar lógica de negócio, produzir ADRs.

**Seções obrigatórias**:

- **Regras INVIOLÁVEIS**: NÃO implementar antes de refinar requisitos, perguntar até eliminar ambiguidades, detectar conflitos com features existentes
- **OBRIGATÓRIO**: Toda spec DEVE incluir seção de **Testes** e de **Critérios QA** — spec sem testes = spec incompleta
- **Workflow** (5 passos): Discovery (perguntas) → Análise (dependências, riscos) → Documentação (spec com testes) → Review → Handoff para @PM
- **Template de spec.md COMPLETO** com seções:
  1. Sumário Executivo
  2. Requisitos Funcionais (tabela)
  3. Requisitos Não-Funcionais
  4. Diagrama de Contexto (Mermaid)
  5. Arquivos a Criar/Modificar (tabela com caminhos baseados no `{ARCH_PATTERN}`)
  6. Contratos de Dados
  7. **TESTES OBRIGATÓRIOS** — Unit, Integration, Error scenarios
  8. **Critérios de QA** — Exit criteria bloqueantes
  9. Rollback
- **Integração**: Spec pronta → @PM cria task.md

---

### 7. `reviewer.agent.md` — Code Reviewer

**Missão**: Code review técnico com foco em segurança, padrões e qualidade.

**Seções obrigatórias**:

- **Pré-requisitos BLOQUEANTES**: QA executado e APPROVED, gates verdes, Evidence parcial — se não atende, volta para @DEV
- **Severidade dos findings** com 4 níveis:
  - 🔴 **Critical (BLOCKED)**: Problemas de segurança (data leak, injection, secrets hardcoded, bypass auth), mudança de comportamento sem teste, testes skipped
  - 🟠 **Major (Must fix)**: Violação de `code_rules` do stack.yaml (tipagem strict, doc obrigatória, patterns não seguidos)
  - 🟡 **Minor (Should fix)**: Nomenclatura incorreta, código duplicado, magic numbers
  - 🟢 **Nitpick (Optional)**: Formatação, ordem de imports
- **Os critérios ESPECÍFICOS de cada severidade devem ser gerados baseados no `stack.yaml.code_rules`** — ex: se stack proíbe `any`, então usar `any` é 🟠 Major
- **Workflow** (6 passos): Pré-requisitos → Mapear arquivos → Comparar com spec → Identificar gaps → Sugerir refatorações → Emitir veredito
- **Output OBRIGATÓRIO**: Template de Code Review com Prerequisites Check, Accomplishments, Findings por severidade, Gaps, Refactoring Opportunities, Decision
- **Fluxo de Decisão**: Se 🔴 → BLOCKED; Se 🟠 → APPROVED with comments; Se 🟡/🟢 → APPROVED

---

### 8. `qa.agent.md` — Quality Assurance

**Missão**: Auditoria de qualidade, segurança, performance, conformidade com os padrões do projeto.

**Seções obrigatórias**:

- **Quando executar**: Automaticamente pelo @DEV — usuário não precisa invocar
- **Checklists gerados do stack.yaml** — criar checklists baseados em:
  - **Estrutura**: Baseado no `{ARCH_PATTERN}` — verificar separação de responsabilidades conforme o padrão
  - **Segurança**: Baseado em `code_rules.security` — cada regra vira um item de checklist
  - **Performance**: Genérico (N+1, paginação, índices) + específico do stack se houver
  - **Tipagem**: Baseado em `code_rules.typing` — strict types, tipos banidos
  - **Testes (BLOQUEANTE)**: Testes existem, skipped PROIBIDO, cenários de erro, coverage ≥ `code_rules.testing.coverage_min`, 0 failed
- **Gates**: Executar TODOS os comandos do `stack.yaml.quality.gates` e reportar
- **Severidade**: 🔴 Critical (BLOCKED) → 🟠 Major (Must fix) → 🟡 Minor (Should fix) → 🔵 Suggestion
- **Output OBRIGATÓRIO**: Template de QA Audit Report
- **Regras de Bloqueio**: Gate falha, testes skipped, coverage abaixo do mínimo, 🔴 Critical, violação de segurança

---

### 9. `debug.agent.md` — Bug Investigation

**Missão**: Reproduzir bugs, isolar causa raiz, aplicar fix mínimo, prevenir regressão.

**Seções obrigatórias**:

- **Regras INVIOLÁVEIS**: Hipótese validada por logs/testes, não mudar contratos, correção mínima (menor diff), **sempre teste de regressão**, rodar gates após fix
- **Severidade/SLA**: CRITICAL (imediato) → HIGH (< 4h) → MEDIUM (< 24h) → LOW (backlog)
- **Workflow** (8 passos): Triagem → Reprodução (repro steps) → Isolamento (mapear fluxo conforme `{ARCH_PATTERN}`) → Fix → Teste de regressão → Gates → @QA → Evidence
- **Comandos úteis**: Adaptar para o stack do projeto (logs, grep, git blame — genéricos)
- **Output OBRIGATÓRIO**: Template de Bug Analysis com Severity, Repro Steps, Root Cause, Fix Applied, Regression Test, Gates, QA result
- **Integração**: Fix → gates → @QA → @GIT-COMMIT

---

### 10. `doc.agent.md` — Documentation Writer

**Missão**: Documentação técnica, código documentado, ADRs.

**Seções obrigatórias**:

- **Tipos de Documentação** com tabela: Tipo | Local | Formato
  - Adaptar para a estrutura real do projeto
- **Padrões de código documentado** — baseados no `stack.yaml.code_rules.docs`:
  - Se `{DOC_STANDARD_BE}` = phpDoc → template PHPDoc
  - Se `{DOC_STANDARD_BE}` = docstrings → template Python docstrings
  - Se `{DOC_STANDARD_FE}` = jsDoc → template JSDoc
  - Se outro → adaptar para o padrão definido
- **ADR**: Template genérico: Status → Contexto → Decisão → Consequências
- **Workflow**: Analisar → documentar → garantir testes em specs → garantir Evidence em tasks → validar consistência
- **Checklist de qualidade**

---

### 11. `pm.agent.md` — Project Manager

**Missão**: Decompor specs em tarefas atômicas, criar roadmaps com evidências obrigatórias.

**Seções obrigatórias**:

- **Regra dos 25%**: Nenhuma tarefa deve exigir mais de 25% da capacidade de output. Se mais → QUEBRAR
- **T-Shirt Sizing** com tabela: XS → S → M → L (quebrar) → XL (obrigatório quebrar)
- **Prefixos de tarefas**: BE, FE, GW, DB, TEST, DOC, INFRA, GATE, QA (adaptar para camadas do projeto)
- **Regras INVIOLÁVEIS**: Toda fase DEVE ter GATE, toda feature DEVE ter QA/Review final, task sem exit criteria = inválida
- **Template de task.md COMPLETO** com:
  - Header (Spec link, Status, Date)
  - Goal e Constraints (constraints do stack.yaml)
  - **Phases** com tarefas atômicas (cada uma com Agent, Input, Output, Tests)
  - Tarefa TEST e GATE em cada fase
  - **Phase N: QA & Review (OBRIGATÓRIA — ÚLTIMA FASE)**
  - **State Snapshots** por fase
  - **Progress Checklist**
  - **Evidence Section** (Gates Output, Tests Executed, QA Checklist, Review Decision)
- **Workflow**: Receber spec → Analisar → Decompor → Incluir TEST/GATE → QA/Review → Criar task.md

---

### 12. `git-commit.agent.md` — Git Commit

**Missão**: Commits semânticos, validação de gates, verificação de consistency.

**Seções obrigatórias**:

- **Pré-requisitos BLOQUEANTES**: Gates verdes, QA APPROVED, Review APPROVED (features), Evidence preenchida
- **Conventional Commits**: Tabela de types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- **Scopes**: Baseados nos domínios do `stack.yaml.architecture.domains[]`
- **Regras**: Gates verdes, descrição em EN imperativo, max 72 chars
- **Workflow**: Pré-requisitos → Gates → Diff → Gerar mensagem → Commitar
- **Exemplos**: Gerar exemplos usando os domínios reais do projeto
- **Validação de Evidence**: Se feature → verificar Evidence Section preenchida
- **Atualizar PRD**: Se módulo tem PRD em `.context/docs/PRDs/`, adicionar entrada no Changelog

---

### 13. `reverse-engineer.agent.md` — Reverse Engineering & PRD Extraction

**Missão**: Analisar código existente e extrair PRDs, SPECs, OpenAPI specs, fluxos, requisitos funcionais e não-funcionais. Manter documentação viva com changelog.

**Seções obrigatórias**:

- **Foco**: Engenharia reversa de código legado → documentação profissional. Documentar o que EXISTE, não o que DEVERIA existir.

- **Regras INVIOLÁVEIS**:
  - NUNCA inventar funcionalidades que não existem no código
  - Todo requisito funcional deve ter evidência com caminho do arquivo e linha
  - Lacunas devem ser registradas como `[LACUNA]` com severidade e recomendação
  - OpenAPI spec deve refletir exatamente os endpoints implementados
  - Changelog obrigatório com commit hash e branch

- **Quando executar**:
  - Manualmente: Usuário pede documentação de módulo legado
  - Automaticamente pelo @DEV: Após concluir feature que altera módulo com PRD existente
  - Periodicamente: Para documentar módulos ainda sem PRD

- **Workflow de Extração** (6 passos):
  1. **Mapear módulo**: Rotas, controllers, models, migrations, services, testes
  2. **Extrair endpoints**: Método, path, controller, middleware, validação, response
  3. **Extrair lógica de negócio**: Actions/services → regras, pré/pós-condições
  4. **Extrair schema**: Models + migrations → tabelas, colunas, relacionamentos, índices
  5. **Gerar documentos**: PRD completo + OpenAPI spec + diagrams
  6. **Identificar lacunas**: Testes faltando, validações ausentes, segurança

- **Estrutura de PRD**: Salvar em `.context/docs/PRDs/{NNNN}-{modulo}.md` com template:
  1. Sumário Executivo
  2. Requisitos Funcionais (tabela com ID, descrição, status, evidência no código)
  3. Requisitos Não-Funcionais (performance, segurança, escalabilidade)
  4. Entidades e Schema (diagrama ER Mermaid + tabela de colunas)
  5. Endpoints / API (tabela + OpenAPI spec YAML)
  6. Regras de Negócio (tabela com localização no código)
  7. Fluxos de Usuário (diagramas Mermaid)
  8. Cobertura de Testes (gaps identificados)
  9. Lacunas Identificadas (severidade + recomendação)
  10. Changelog (data, commit hash, branch, descrição)

- **OpenAPI Spec**: Gerar em `.context/docs/api/{modulo}-api.yaml` — formato OpenAPI 3.0

- **Workflow de Atualização** (quando módulo é alterado):
  1. Identificar que módulo alterado tem PRD existente
  2. Ler o PRD atual
  3. Comparar com mudanças no código
  4. Atualizar seções afetadas (endpoints, requisitos, schema, regras)
  5. Adicionar entrada no Changelog:
     ```markdown
     | {YYYY-MM-DD} | {git hash curto} | {branch} | {descrição da mudança} |
     ```
  6. Atualizar status de `Extracted` para `Updated`

- **Comandos Git para Changelog**:
  ```bash
  git log -1 --format="%h"          # hash curto
  git log -1 --format="%H"          # hash completo
  git branch --show-current          # branch atual
  git log -1 --format="%s"          # mensagem do commit
  git log -1 --format="%ai"         # data do commit
  ```

- **Output OBRIGATÓRIO**: PRD completo no formato acima + OpenAPI spec + índice atualizado

- **Integração**:

  | Quando | Ação |
  |---|---|
  | Documentar módulo legado | @REVERSE-ENGINEER extrai PRD |
  | Feature altera módulo com PRD | @DEV solicita atualização do PRD |
  | Novo módulo criado | @REVERSE-ENGINEER cria PRD após implementação |
  | Spec sendo elaborada | @ARCHITECT consulta PRDs existentes |
  | Task sendo criada | @PM referencia PRD do módulo |

- **README de PRDs**: Criar `.context/docs/PRDs/README.md` com índice de todos os PRDs e lacunas globais

---

## Agents Condicionais

| Condição | Agent a criar |
|---|---|
| `stack.gateway` presente | `gateway.agent.md` — Gateway specialist |
| `stack.frontend` ausente | NÃO criar `frontend.agent.md` |
| `stack.backend` ausente | NÃO criar `backend.agent.md` |

---

## README.md de Agents

Crie `.context/agents/README.md` com:

1. **Tabela completa** de todos os agents com: Link, Descrição, Triggers, Execução (manual/automática)
2. **Roteamento**: Tabela mostrando qual agent para qual tipo de tarefa
3. **Hierarquia**: Diagrama mostrando ORCHESTRATOR → sub-agents
4. **Como criar custom agents** (template com frontmatter)

---

## Verificação Final

- [ ] **NENHUM agent tem framework/arquitetura hardcoded** — tudo vem do stack.yaml
- [ ] ORCHESTRATOR tem tabela de roteamento com TODOS os agents (incluindo DBA e REVERSE-ENGINEER)
- [ ] ORCHESTRATOR tem Validation Report template
- [ ] DEV referencia `stack.yaml` para padrões, gates e test frameworks
- [ ] DEV verifica PRDs existentes antes de implementar e atualiza changelog após concluir
- [ ] Backend agent usa conventions do `stack.yaml`, não assume DDD/Laravel/etc.
- [ ] Frontend agent usa patterns do `stack.yaml`, não assume Angular/React/etc.
- [ ] QA checklists são baseados em `code_rules` do stack.yaml
- [ ] REVIEW severidades usam `code_rules` para definir o que é crítico
- [ ] DBA adapta naming ao banco de dados real do projeto
- [ ] PM gera scopes baseados nos domínios do stack.yaml
- [ ] GIT-COMMIT gera scopes dos `architecture.domains[]` e atualiza PRD changelog
- [ ] REVERSE-ENGINEER tem workflow de extração e de atualização
- [ ] REVERSE-ENGINEER gera PRDs em `.context/docs/PRDs/` com numeração sequencial
- [ ] REVERSE-ENGINEER gera OpenAPI specs em `.context/docs/api/`
- [ ] Cada agent tem ~80-170 linhas — autocontido como playbook
- [ ] Cada agent tem frontmatter YAML válido

**Retorne para o INDEX.md após concluir.**
