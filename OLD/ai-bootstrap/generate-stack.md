# 📋 Generate Stack — Projeto Novo

> **Quando usar**: A IA chamou este prompt porque detectou que o projeto é novo (sem código-fonte).

## Instruções para a IA

Pergunte ao usuário sobre a stack do projeto e gere o `.context/stack.yaml`.

### Perguntas Obrigatórias

Faça as perguntas abaixo ao usuário. Se ele não souber responder alguma, sugira a opção mais comum.

#### 1. Informações do Projeto
- Qual o **nome** do projeto?
- Qual o **tipo**? (fullstack, backend, frontend, monorepo)
- Breve **descrição** (1-2 frases)

#### 2. Stack de Frontend (se aplicável)
- Qual **framework**? (Angular, React, Vue, Next.js, Svelte, outro)
- Qual **versão** do framework?
- Linguagem: TypeScript ou JavaScript?
- **Estilização**: Tailwind, CSS Modules, Styled Components, SASS, Vanilla CSS?
- **Testes**: Vitest, Jest, Cypress, Playwright?
- Tem um **template/codebase de referência** para UI? Se sim, qual o caminho?
  - Ex: `template-base/ANGULAR/src/app/views/`
- Padrões específicos? (Signals, Hooks, Composition API, etc.)

#### 3. Stack de Backend (se aplicável)
- Qual **framework**? (Laravel, NestJS, Express, FastAPI, Spring, Rails, Django, outro)
- Qual **versão**?
- Linguagem e versão? (PHP 8.3, Node 20, Python 3.12, Java 21, etc.)
- **Banco de dados**: PostgreSQL, MySQL, MongoDB, SQLite, outro?
- **Testes**: Pest, PHPUnit, Jest, Vitest, Pytest, RSpec, JUnit?
- **Padrão arquitetural**? (DDD, MVC, Hexagonal, Clean Architecture, CQRS, outro)
- **Naming conventions** que deseja adotar:
  - Como nomear Controllers? (ex: `{Entity}Controller`, `{entity}_controller`)
  - Como nomear Services/Actions? (ex: `Create{Entity}Action`, `{Entity}Service`)
  - Como nomear Models? (ex: `{Entity}`, `{entity}.model`)
  - Como nomear DTOs? (ex: `{Entity}DTO`, `{entity}.dto`)
  - Como nomear Validação? (ex: `{Entity}StoreRequest`, `{entity}.validator`)
  - Como nomear Testes? (ex: `{Entity}Test`, `{entity}.spec`)
- **Estrutura de pastas** preferida:
  - DDD: `src/Domain/{Domínio}/Actions/` + `src/Domain/{Domínio}/Models/`
  - MVC: `app/Controllers/` + `app/Models/`
  - Clean: `src/usecases/` + `src/entities/`
  - Outra?

#### 4. Gateway/Middleware (se aplicável)
- Tem gateway separado? (NestJS, Express, Kong, etc.)
- Gerencia webhooks?
- Comunicação com backend via quê? (Redis Streams, RabbitMQ, HTTP, gRPC)

#### 5. Infraestrutura
- Banco de dados principal?
- Cache/Fila? (Redis, RabbitMQ, SQS)
- Storage? (Local, S3, GCS)
- Docker? Docker Compose?

#### 6. Arquitetura
- Padrão principal? (DDD, MVC, Hexagonal, Clean, Monolítico, Microservices)
- Multi-tenant? Se sim, coluna de tenant? (tenant_id, organization_id, company_id)
- Quais **domínios/módulos** o projeto terá?

#### 7. Convenções e Code Rules
- Idioma de respostas da IA? (pt-br, en, etc.)
- Idioma do código? (en sempre recomendado)
- Padrão de commit? (Conventional Commits recomendado)
- Branching? (Gitflow, trunk-based, GitHub Flow)
- **Documentação inline**: (phpDoc para PHP, jsDoc para TS/JS, docstrings para Python — ou qual padrão?)
- **Tipagem strict**: (strict_types em PHP? strict mode em TS?)
- **Tipos banidos**: (ex: `any` e `unknown` em TS? `mixed` em PHP?)
- **Coverage mínimo**: (ex: 80%)

### Após obter as respostas

Gere o `.context/stack.yaml` usando o template em [`stack-template.yaml`](./stack-template.yaml), preenchendo:

- **TODAS** as seções de `stack.*` com frameworks e versões
- **`stack.backend.patterns[]`** e **`stack.frontend.patterns[]`** com padrões arquiteturais escolhidos
- **`stack.backend.conventions`** e **`stack.frontend.conventions`** com naming conventions — estas são **FUNDAMENTAIS** porque todos os agents usam como referência
- **`code_rules`** com regras de tipagem, documentação, testes, tipos banidos
- **`quality.gates`** com comandos de gate apropriados para o framework

### Verificação

- [ ] Todos os campos obrigatórios preenchidos
- [ ] `stack.backend.conventions` detalhado (naming + folder_structure)
- [ ] `stack.frontend.conventions` detalhado (se aplicável)
- [ ] `code_rules` configurado com regras da stack
- [ ] `quality.gates` com comandos apropriados
- [ ] `template_base` preenchido se frontend com template de referência

**Retorne para o INDEX.md após concluir.**
