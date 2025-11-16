# Resumo de Contexto do Projeto AgentFlix

## 1. Objetivo

Este documento é um "snapshot" do contexto atual do projeto AgentFlix, destinado a restaurar o estado da sessão caso ela seja interrompida. Ele resume as principais decisões de negócio, arquitetura e escopo.

## 2. Persona do Agente

-   **Nome:** SUPER-AGENTE
-   **Função:** Agente técnico multidisciplinar (Arquiteto, DBA, DevOps, Dev Backend/Frontend, QA).
-   **Diretriz Principal:** Ser extremamente rígido e intolerante a ambiguidades, seguindo um processo de refinamento de requisitos (Perguntas -> PRD -> TSD).

## 3. Stack Tecnológica Principal

-   **Backend (Core):** Laravel 11+ / PHP 8.2+
-   **Backend (IA):** Python 3.11+ / FastAPI
-   **Frontend:** Angular 19+
-   **Banco de Dados:** PostgreSQL 16 com extensão `pgvector`
-   **Estilo (CSS):** Tailwind CSS 4+ e daisyUI 5+
-   **Gráficos:** ApexCharts (via `ng-apexcharts`)
-   **DevOps:** Docker / Docker Compose

## 4. Decisões de Arquitetura Chave

-   **Autenticação:** Laravel Sanctum para autenticação de SPA. Sessão com `access_token` de 15 min e `refresh_token` de 8 horas.
-   **Estrutura Backend:** DDD-Light, com lógica de negócio em `Services`.
-   **Classes Base:** Uso de `BaseModel` (para UUIDs e multi-tenancy automático), `BaseCrudService` e `BaseCrudController` para padronização de CRUDs.
-   **Multi-tenancy:** Isolamento de dados a nível de banco de dados, com um `company_id` em todas as tabelas relevantes, filtrado automaticamente por um `Global Scope`.
-   **Chaves Primárias:** UUIDs são o padrão para todas as tabelas.
-   **Documentação:** Uso do `context7 mcp` para consultar documentação atualizada.

-   **Esquema do Banco de Dados:** TSD de migrações (`v2/03-database-migrations.md`) refatorada para separar `tenants` de `crm_companies`, com comentários e índices.

## 5. Estado dos Módulos

### Módulo de Autenticação
-   **Status:** PRD concluído (`v2/modules/01-authentication.prd.md`).
-   **Escopo:** Onboarding via `SUPER_ADMIN`, login padrão, 2FA (TOTP).
-   **Papéis Definidos:** `SUPER_ADMIN`, `TENANT_ADMIN`, `MANAGER`, `AGENT`.

### Módulo CRM
-   **Status:** PRD e TSD atualizados (`v2/modules/02-crm.prd.md`, `v2/modules/02-crm.tsd.md`).
-   **Escopo do MVP:** Abrangente. Inclui `Contatos`, `Empresas` (CRM), `Pipelines`, `Deals`, `Produtos`, `Motivos de Perda`, `Dashboard` e `Propostas PDF`.
-   **Funcionalidades Chave:** Kanban, Fechamento Rápido de Negociação (Mark as Won/Lost).
-   **Permissões:** "Modelo Aberto" para o MVP.
-   **Fora do Escopo (adiado):** Módulo de Tarefas/Agenda.

### Módulo Layout Shell & Navegação
-   **Status:** TSD concluída (`v2/22-frontend-layout-shell.md`).
-   **Escopo:** Define a estrutura principal da aplicação com uma sidebar vertical à esquerda (expansível/recolhível) e área de conteúdo.
-   **Decisões:** O menu é dinâmico com base nos papéis do usuário. O perfil/logout fica na parte inferior da sidebar. A rota padrão após login é o Dashboard.

### Tela de Login
-   **Status:** Especificação de Tela (SS) concluída (`v2/modules/01-authentication/screens/01-login-screen.ss.md`).
-   **Escopo:** Tela de autenticação de usuários.
-   **Decisões:** Layout de card centralizado, inputs de e-mail/senha, link "Esqueceu a senha", botão "Entrar". Fluxo de interação detalhado com validações, mensagens de erro e estados de carregamento.

### Tela de Contatos
-   **Status:** Especificação de Tela (SS) concluída (`v2/modules/02-crm/screens/01-contacts-screen.ss.md`).
-   **Escopo:** Tela CRUD avançada para gerenciamento de contatos.
-   **Decisões:** Layout com abas ("Ativos"/"Arquivados"), filtros em modal, tabela com checkboxes para ações em massa (arquivar/excluir), avatares de contato (com fallback para Gravatar), e funcionalidade de importação via CSV.

## 6. Regras Operacionais

-   **Arquivo de Regras:** Todas as diretrizes operacionais do agente estão consolidadas no arquivo `AGENT.md`.
-   **Regra de Frontend:** Foi adicionada uma regra especial e rigorosa para o levantamento de requisitos de frontend, detalhando 10 áreas de questionamento obrigatório (Estrutura, Componentes, Fluxos, etc.).
-   **Atualização de Contexto:** O agente deve manter este arquivo (`CONTEXT.md`) sempre atualizado.

## 7. Próximos Passos Pendentes

-   Refinar o próximo módulo funcional (ex: Chat, Faturamento, etc.).
-   Criar a TSD para as rotas da API (`05-backend-api-routes.md`).

## 8. Referência de Regras Avançadas
Para consulta rápida de práticas expert por stack (Laravel, FastAPI, Angular, PostgreSQL/pgvector, Redis, Tailwind, Docker/Compose, Testes) usar o arquivo `rules/STACK-ADVANCED-EXAMPLES.md`. Este contexto assume adoção das boas práticas ali listadas (ex: jobs idempotentes, Signals para estado local, IVFFlat/HNSW tuning, multi-stage builds, testes de arquitetura Pest).

