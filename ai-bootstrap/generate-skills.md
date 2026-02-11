# ⚡ Generate Skills — Por Framework

> **Fase 3 do INDEX.md**: Criar skills específicas para cada framework da stack.

## Instruções para a IA

Leia o `.context/stack.yaml`. Para cada framework detectado, crie uma skill com documentação completa.

### Formato de cada Skill

```
.context/skills/{skill-slug}/
├── SKILL.md         # Instruções principais
├── templates/       # Templates de código (opcional)
└── examples/        # Exemplos reais (opcional)
```

O `SKILL.md` deve ter frontmatter YAML:

```yaml
---
type: skill
name: "Nome da Skill"
description: "O que esta skill ensina"
skillSlug: "nome-slug"
phases: [P, E, V]    # P=Planning, R=Review, E=Execution, V=Validation, C=Confirmation
generated: "YYYY-MM-DD"
status: filled
scaffoldVersion: "2.0.0"
---
```

### Skills por Framework

Crie skills baseadas no que existe no `stack.yaml`:

#### Se Backend = Laravel
**Skill: `laravel-ddd`**
- Controller → DTO → Action → Response pattern
- Naming: `{Domínio}{Entidade}Controller`, `{Verbo}{Domínio}{Entidade}Action`
- Template de Model com `$fillable`, `SoftDeletes`, `HasFactory`
- Template de Migration com UUID PK, timestamps, indices
- Template de FormRequest com `authorize()` e `rules()`
- Template de Resource
- Template de teste Pest
- Checklist: criando Controller, Action, DTO, Model, Migration

#### Se Backend = NestJS / Express
**Skill: `nestjs-api` ou `express-api`**
- Module, Controller, Service, DTO pattern
- Decorator patterns, Guards, Pipes
- Template de teste Jest

#### Se Backend = FastAPI
**Skill: `fastapi-api`**
- Router, Schema, Service pattern
- Pydantic models, dependency injection
- Template de teste Pytest

#### Se Frontend = Angular
**Skill: `angular-signals`**
- Standalone Components, OnPush
- Signals (`signal()`, `computed()`)
- `takeUntilDestroyed` para subscriptions
- CrudPageComponent pattern (se template_base existir)
- Template de componente, service, model
- Template de teste Vitest
- Referência visual: link para `template_base`

#### Se Frontend = React / Next.js
**Skill: `react-patterns` ou `nextjs-patterns`**
- Hooks, Context, Server Components
- Template de componente, hook, page
- Template de teste Jest/Vitest

#### Se Frontend = Vue
**Skill: `vue-composition`**
- Composition API, `ref()`, `computed()`
- Template de componente, composable
- Template de teste Vitest

#### Se Gateway = NestJS
**Skill: `nestjs-gateway`**
- Webhook processing, Redis Streams
- BullMQ jobs, WebSocket fan-out
- Template de controller, service, dto

### Skills Genéricas (SEMPRE criar)

Independente da stack, crie estas skills:

#### `code-review/SKILL.md`
- Checklist de review por camada (controller, model, component)
- Severidade: 🔴 Crítico (bloqueia), 🟡 Melhoria, 🟢 OK
- Formato de output do review
- Regras: phpDoc/jsDoc verificado, sem `any`/`unknown`, testes presentes

#### `commit-message/SKILL.md`
- Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Regras de scope: `feat(crm): add contact list`
- Exemplos bons e ruins

#### `test-generation/SKILL.md`
- Tipos de teste: Unit, Feature/Integration, E2E
- Patterns de teste por framework (Pest, Vitest, Jest)
- Coverage mínimo configurável
- Template de teste com arrange/act/assert
- Mock patterns

#### `bug-investigation/SKILL.md`
- Workflow: Reproduzir → Isolar → Root cause → Fix → Teste
- Template de bug report
- Coleta de evidências

#### `documentation/SKILL.md`
- phpDoc/jsDoc obrigatório em classes/interfaces públicas
- Formato de ADR (Architecture Decision Record)
- Formato de Feature Spec (lite e full)
- Idioma: código e docs em EN, descrições podem ser PT-BR

### README.md de Skills

Crie `.context/skills/README.md` com:
1. Tabela de todas as skills com link, fases (PREVC) e descrição
2. Guia: quando usar cada skill
3. Como criar custom skills
4. Integração com workflow PREVC

### Verificação Final

- [ ] Cada skill tem frontmatter YAML válido
- [ ] Skills específicas criadas para cada framework do stack.yaml
- [ ] Skills genéricas (code-review, commit-message, test-generation, bug-investigation) criadas
- [ ] README.md indexa todas as skills
- [ ] Templates são práticos e copiáveis

**Retorne para o INDEX.md após concluir.**
