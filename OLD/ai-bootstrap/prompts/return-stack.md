# 📤 Return Stack — Capturar Stack de uma Conversa de Arquitetura

> **Quando usar**: Você já está conversando com uma IA sobre a arquitetura de um projeto (discutindo tecnologias, padrões, domínios, etc.) e quer que ela retorne toda a stack no formato `stack.yaml` para usar com o `.ai-bootstrap`.

## Instruções para a IA

Baseado em **tudo que discutimos até agora** sobre este projeto — tecnologias escolhidas, padrões, convenções, domínios, frameworks, banco de dados, infraestrutura — retorne a stack completa no formato YAML abaixo.

**Regras**:
1. Preencha TODOS os campos baseado no que já foi discutido
2. Se algo não foi mencionado, pergunte antes de preencher
3. Se algo não se aplica, remova a seção inteira
4. Use EXATAMENTE este formato — ele será usado pelo sistema `.ai-bootstrap`

### Formato Esperado

Retorne um bloco de código YAML com exatamente esta estrutura:

```yaml
# ============================================
# stack.yaml — Gerado a partir de conversa IA
# Data: YYYY-MM-DD
# ============================================

project:
  name: ""                              # Nome do projeto
  type: ""                              # fullstack | backend | frontend | monorepo
  description: ""                       # Descrição breve (1-2 frases)

stack:
  frontend:                             # REMOVER se projeto backend-only
    framework: ""                       # angular | react | vue | next | svelte
    version: ""                         # Versão do framework
    language: "typescript"              # typescript | javascript
    styling: ""                         # tailwind | css-modules | styled-components | sass | vanilla
    testing: ""                         # vitest | jest | cypress | playwright
    template_base: ""                   # Caminho para pasta de templates UI (se houver)
    patterns: []                        # Ex: ["signals", "standalone-components", "onpush"]

  backend:                              # REMOVER se projeto frontend-only
    framework: ""                       # laravel | nestjs | express | fastapi | spring | rails
    version: ""                         # Versão do framework
    language: ""                        # php | typescript | python | java | ruby | go
    language_version: ""                # Ex: "8.3", "20", "3.12"
    database: ""                        # postgresql | mysql | mongodb | sqlite
    testing: ""                         # pest | phpunit | jest | pytest | junit
    patterns: []                        # Ex: ["ddd", "actions", "dto", "form-request"]

  gateway:                              # REMOVER se não houver gateway
    framework: ""                       # nestjs | express | kong
    language: ""                        # typescript | go
    testing: ""                         # jest | vitest

  infrastructure:
    database: ""                        # postgresql | mysql | mongodb
    cache: ""                           # redis | memcached (remover se não usar)
    queue: ""                           # redis-streams | rabbitmq | sqs | bullmq (remover se não usar)
    storage: ""                         # local | s3 | gcs (remover se não usar)

architecture:
  pattern: ""                           # ddd | mvc | hexagonal | clean
  multi_tenant: false                   # true | false
  domains: []                           # Ex: ["auth", "crm", "chat", "billing"]

conventions:
  language:
    responses: "pt-br"                  # Idioma das respostas da IA
    code: "en"                          # SEMPRE en
    docs: "en"                          # SEMPRE en
  commit: "conventional"                # conventional | angular | none
  branching: "gitflow"                  # gitflow | trunk-based | github-flow

code_rules:
  docs:
    php: "phpDoc"                       # SE usa PHP — phpDoc obrigatório
    typescript: "jsDoc"                 # SE usa TS — jsDoc obrigatório
    python: "docstrings"               # SE usa Python — docstrings obrigatórias
  typing:
    strict: true
    ban: ["any", "unknown"]            # SE usa TypeScript
    php_strict_types: true             # SE usa PHP — declare(strict_types=1)
  testing:
    mandatory: true
    coverage_min: 80
    frameworks:
      backend: ""                      # pest | phpunit | jest | pytest
      frontend: ""                     # vitest | jest | cypress
      gateway: ""                      # jest | vitest
  security:
    tenant_isolation: false            # true SE multi-tenant
    no_guarded_empty: true             # SE Laravel — NUNCA $guarded = []
    no_log_secrets: true               # NUNCA logar tokens/senhas

quality:
  gates:
    backend: ""                        # Ex: "composer gate:all"
    frontend: ""                       # Ex: "npm run gate:all"
    gateway: ""                        # Ex: "pnpm lint && pnpm test && pnpm build"
```

### Após retornar

Diga ao usuário:
1. Salve este conteúdo como `.context/stack.yaml` na raiz do projeto
2. Copie a pasta `.ai-bootstrap/` para a raiz do projeto
3. Abra uma nova sessão de IA e importe o `INDEX.md`
4. O `INDEX.md` vai pular a Fase 1 (detecção) pois o `stack.yaml` já existirá
