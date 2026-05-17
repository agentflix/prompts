# 🔍 Extract Stack — Projeto Existente

> **Quando usar**: A IA chamou este prompt porque detectou que o projeto já tem código-fonte.

## Instruções para a IA

Analise o projeto existente e gere o arquivo `.context/stack.yaml` com toda a stack detectada.

### Passo 1 — Detectar Arquivos de Configuração

Procure e leia estes arquivos (se existirem):

#### Backend
- `composer.json` → Laravel, PHP version, pacotes
- `package.json` (na raiz ou em subpastas) → Node.js, NestJS
- `requirements.txt` / `pyproject.toml` → Python
- `pom.xml` / `build.gradle` → Java/Kotlin
- `go.mod` → Go
- `Gemfile` → Ruby

#### Frontend
- `package.json` no diretório frontend → Angular, React, Vue, etc.
- `angular.json` → Angular específico
- `next.config.*` → Next.js
- `vite.config.*` → Vite
- `tsconfig.json` → TypeScript config

#### Infraestrutura
- `docker-compose.yml` → Serviços, bancos, cache
- `Dockerfile` / `Dockerfile.*` → Imagens
- `.env.example` / `.env.docker.example` → Variáveis de ambiente
- `Makefile` → Comandos disponíveis

#### Banco de Dados
- `database/migrations/` → Migrations (Laravel)
- `prisma/schema.prisma` → Prisma
- `*.sql` → Scripts SQL

### Passo 2 — Analisar Estrutura de Pastas

```bash
# Verifique a estrutura de diretórios (profundidade 2-3)
# Identifique:
# - Padrão arquitetural (DDD, MVC, Hexagonal, Clean)
# - Domínios/Módulos existentes
# - Separação de camadas (Controllers, Services, Models, Actions, DTOs)
# - Pasta de testes
# - Pasta de templates/referência UI
```

### Passo 3 — Detectar Padrões de Código

Analise 3-5 arquivos de cada camada para identificar:

| O que detectar | Onde procurar |
|---|---|
| Padrão de Controller | `*Controller.php`, `*.controller.ts`, `*_controller.rb`, etc. |
| Padrão de Service/Action | `*Action.php`, `*Service.ts`, `*_service.py`, etc. |
| Padrão de Model | Models, entities, schemas |
| DTOs/Data classes | `*DTO.php`, `*.dto.ts`, `*Schema.py`, etc. |
| Testes | `tests/`, `spec/`, `*.spec.ts`, `*.test.ts`, `*_test.py` |
| Validação | Requests, validators, schemas |
| Documentação inline | Headers de classes (phpDoc, jsDoc, docstrings) |
| Tipagem | `strict_types`, `any` usage, type hints |

### Passo 3.5 — Detectar Naming Conventions e Camadas (CRÍTICO)

> **Este passo é fundamental** — as conventions detectadas aqui serão usadas por TODOS os agents no Fase 2. NÃO assumir padrões; documentar o que REALMENTE EXISTE no código.

**Para o backend**, analise os nomes dos arquivos existentes e documente:

```yaml
# Exemplo: o que detectar
backend_conventions:
  controller: "{Domínio}{Entidade}Controller"      # ou "{entity}_controller", etc.
  service: "{Verbo}{Domínio}{Entidade}Action"       # ou "{Entity}Service", etc.
  model: "{Entidade}"                                # ou "{entity}.model", etc.
  dto: "{Entidade}DTO"                               # ou "{entity}.dto", etc.
  validation: "{Entidade}{Verbo}Request"             # ou "{entity}.validator", etc.
  test: "{Classe}Test"                               # ou "{classe}.spec", etc.
  
  # Estrutura de pastas por domínio/módulo
  folder_structure: |
    src/Domain/{Domínio}/
    ├── Actions/
    ├── Models/
    ├── DTOs/
    └── Http/Controllers/
    
  # OU para MVC
  folder_structure: |
    app/
    ├── Controllers/
    ├── Models/
    ├── Services/
    └── Requests/
```

**Para o frontend**, analise os nomes dos componentes existentes:

```yaml
frontend_conventions:
  component: "{domínio}-{entidade}-{tipo}.component.ts"   # ou "EntityComponent.tsx", etc.
  service: "{domínio}.service.ts"                         # ou "useEntity.ts", etc.
  model: "{entidade}.model.ts"                            # ou "entity.types.ts", etc.
  store: "{domínio}.store.ts"                             # ou "useEntityStore.ts", etc.
  page: "{entidade}-{page}.page.ts"                       # ou "EntityPage.tsx", etc.
  
  folder_structure: |
    src/app/domains/{domínio}/
    ├── components/
    ├── services/
    └── models/
```

**O que NÃO fazer**: Inventar conventions que não existem no código. Se o projeto usa MVC simples, documentar MVC — não transformar em DDD.

### Passo 4 — Detectar Gates de Qualidade

Procure em `composer.json`, `package.json`, `Makefile`, `Taskfile`, `Justfile`:
- Scripts de lint (pint, eslint, prettier, black, rubocop, etc.)
- Scripts de teste (pest, phpunit, vitest, jest, pytest, rspec, etc.)
- Scripts de análise estática (phpstan, larastan, mypy, tsc, etc.)
- Scripts compostos (`gate:all`, `check:all`, `ci`, `verify`)

### Passo 5 — Detectar Multi-Tenancy e Segurança

- Procure por tenant_id, organization_id, company_id em migrations e models
- Procure por traits/mixins de tenant isolation
- Procure por middleware de autenticação
- Identifique padrão de RBAC

### Passo 6 — Gerar `stack.yaml`

Com base em tudo que foi detectado, gere o `.context/stack.yaml` usando o template em [`stack-template.yaml`](./stack-template.yaml).

**Campos obrigatórios**:
- `project.name` — nome do diretório raiz
- `project.type` — `fullstack`, `backend`, `frontend`, `monorepo`
- `stack.*` — todas as tecnologias detectadas
- `stack.backend.patterns[]` — padrões detectados (ddd, mvc, hexagonal, etc.)
- `stack.backend.conventions` — naming conventions detectadas no Passo 3.5
- `stack.frontend.patterns[]` — padrões detectados
- `stack.frontend.conventions` — naming conventions detectadas no Passo 3.5
- `architecture.pattern` — o padrão identificado
- `architecture.domains` — os domínios/módulos encontrados
- `code_rules` — as regras que o projeto já segue
- `quality.gates` — os comandos de gate existentes

> **IMPORTANTE**: Documentar o que EXISTE, não o que DEVERIA existir.

### Passo 7 — Verificação

Confirme que o `stack.yaml` gerado:
- [ ] Reflete todas as tecnologias encontradas
- [ ] Tem os domínios corretos
- [ ] Tem os gates corretos
- [ ] Tem as convenções de código detectadas
- [ ] Se tem frontend, tem `template_base` preenchido (se detectado)

**Retorne para o INDEX.md após concluir.**
