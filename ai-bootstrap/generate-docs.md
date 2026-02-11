# 📚 Generate Docs — Documentação Técnica

> **Fase 4 do INDEX.md**: Gerar documentação técnica em `.context/docs/`.

## Instruções para a IA

Leia o `.context/stack.yaml`. Gere documentação técnica adaptada à stack do projeto.

### Documentos Obrigatórios

Crie todos os documentos abaixo em `.context/docs/`:

#### 1. `README.md` — Índice de Documentação

Tabela com todos os documentos, descrição e status. Quick links para os mais importantes.

Incluir seções:
- Quick Links (tabela)
- Para Agentes IA: instruções de leitura obrigatória
- Templates disponíveis
- Status de cada documento

#### 2. `architecture.md` — Arquitetura do Sistema

Baseado no `stack.yaml`, gerar:
- Overview da arquitetura (diagrama mermaid)
- Estrutura de pastas detalhada (baseada no `architecture.pattern`)
- Camadas e responsabilidades (Controller, Action/Service, Model, DTO, etc.)
- Domínios do projeto (tabela com responsabilidades)
- Convenções de código por camada
- Data flow entre camadas
- Decisões arquiteturais (ADR format, se relevante)

**Se DDD**: Incluir template de estrutura Domain com Actions, Models, DTOs, Repositories, Policies, Http

**Se MVC**: Incluir template de estrutura com Controllers, Models, Views, Services

#### 3. `testing-strategy.md` — Estratégia de Testes

Baseado no `stack.yaml.code_rules.testing`:
- Tipos de teste (Unit, Feature, E2E, Architecture)
- Framework de teste por camada
- Coverage mínimo obrigatório
- Onde criar testes (`tests/Unit`, `tests/Feature`, `*.spec.ts`)
- Padrão de teste (Arrange/Act/Assert)
- Mocking patterns
- Gates de qualidade e comandos
- O que testar e o que NÃO testar

#### 4. `security.md` — Segurança

Baseado no `stack.yaml.code_rules.security`:
- Autenticação (método usado)
- Autorização (RBAC, Policies, Guards)
- Tenant isolation (se multi-tenant)
- Mass assignment protection
- Input validation
- Secrets management (NUNCA logar)
- CORS, Rate limiting
- Checklist de segurança por camada

#### 5. `development-workflow.md` — Fluxo de Desenvolvimento

- Workflow PREVC: Planning → Review → Execution → Validation → Confirmation
- Workflow de commit (conventional commits)
- Avaliação de tamanho: Quick Fix / Small / Feature
- Quality gates obrigatórios (comandos do stack.yaml)
- Exit criteria por tipo de tarefa
- Quando criar spec, quando pular

#### 6. `glossary.md` — Glossário (Opcional mas Recomendado)

- Termos de domínio do projeto
- Entidades principais
- Conceitos de negócio
- Abreviações usadas

### Templates

Crie em `.context/docs/templates/`:

#### `feature-spec-lite.md`
Template para features de 1-2 dias: Overview, Tarefas, Testes, Exit Criteria

#### `feature-spec-full.md`
Template para features de 3+ dias: Overview, Requisitos, Arquitetura, API Contract, UI Wireframes, Testes, Riscos, Exit Criteria

### Configuração e Regras nos Docs

Todos os documentos devem reforçar as regras inquebráveis:

| Regra | Onde documentar |
|---|---|
| phpDoc/jsDoc obrigatório | `architecture.md`, `development-workflow.md` |
| NUNCA `any`/`unknown` | `architecture.md` (convenções de código) |
| `strict_types` em PHP | `architecture.md` (convenções de código) |
| Todo código testado | `testing-strategy.md` |
| Gates obrigatórios | `development-workflow.md` |
| Conventional Commits | `development-workflow.md` |
| NUNCA logar secrets | `security.md` |
| Tenant isolation | `security.md`, `architecture.md` |

### Verificação Final

- [ ] `README.md` indexa todos os documentos
- [ ] `architecture.md` reflete a stack real
- [ ] `testing-strategy.md` tem frameworks corretos do stack.yaml
- [ ] `security.md` aborda tenant isolation se multi-tenant
- [ ] `development-workflow.md` tem gates com comandos reais
- [ ] Templates criados em `templates/`
- [ ] Regras inquebráveis presentes em todos os docs relevantes

**Retorne para o INDEX.md após concluir.**
