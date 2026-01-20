# Technical Plan: Administration & Tenant Provisioning Module

## 1. Análise de Impacto

### Arquivos Afetados (Novos e Modificados)

-   **Migrations:**
    -   `create_platform_tenants_table`
    -   `create_billing_plans_table` (implied dependency)
    -   `create_platform_tenant_settings_table`
    -   `create_platform_tenant_users_table`
    -   `create_platform_integrations_table`
    -   `create_platform_tenant_audits_table`
    -   Update existing domain tables (e.g., `crm_contacts`) to add `company_id`.

-   **Models (app/Models):**
    -   `Platform/Tenant`
    -   `Platform/TenantSetting`
    -   `Platform/TenantUser`
    -   `Platform/Integration`
    -   `Platform/TenantAudit`
    -   `Billing/Plan` (implied dependency)
    -   `User` (modification for tenant relationship)

-   **Concerns/Traits (app/Models/Concerns):**
    -   `BelongsToTenant.php` (novo)

-   **Services (app/Services):**
    -   `Platform/TenantProvisioningService.php` (novo)
    -   `Platform/TenantOwnerService.php` (novo)
    -   `Platform/QuotaService.php` (novo)

-   **Context & Providers (app/Providers):**
    -   `Platform/TenantContext.php` (novo)
    -   `TenantServiceProvider.php` (novo)

-   **Controllers (app/Http/Controllers/Administration):**
    -   `TenantController.php` (novo)
    -   `TenantPlanController.php` (novo)
    -   `TenantIntegrationController.php` (novo)
    -   `TenantAuditController.php` (novo)

-   **Policies (app/Policies):**
    -   `TenantPolicy.php` (novo, para `can:manage-tenants`)

-   **Exceptions (app/Exceptions):**
    -   `QuotaExceededException.php` (novo)

-   **Config:**
    -   `config/logging.php` (adição dos canais `tenant_lifecycle` e `tenant_integrations`)

-   **Testes (Pest):**
    -   `tests/Feature/Administration/TenantProvisioningTest.php`
    -   `tests/Unit/Services/QuotaServiceTest.php`
    -   `tests/Unit/Models/Concerns/BelongsToTenantTest.php`

### Novas Dependências

-   **Externas (implícitas):** SDK ou Client HTTP para integração com o gateway de pagamento **Asaas**.
-   **Internas:** Módulo de Faturamento (`billing_plans`) precisa existir antes deste.

## 2. Estratégia de Implementação (Backend - Laravel)

1.  **Estrutura de Dados:**
    -   Criar as 5 migrations para as tabelas da plataforma (`platform_*`).
    -   Criar os Models correspondentes (`Tenant`, `TenantSetting`, etc.). Usar DTOs do Spatie para validação e consistência.

2.  **Isolamento Multi-Tenant (Core):**
    -   Implementar o trait `BelongsToTenant.php` com o `Global Scope` que filtra por `company_id`.
    -   Criar o `TenantContext` para atuar como um singleton de requisição, armazenando o `tenant_id` atual.
    -   Criar o `TenantServiceProvider` para popular o `TenantContext` a partir do usuário autenticado a cada requisição.

3.  **Serviços de Domínio (TDD):**
    -   Desenvolver o `TenantProvisioningService` com TDD, cobrindo o fluxo de criação completo (validação, persistência, owner, settings, sync com billing, auditoria e ativação). Garantir a idempotência.
    -   Implementar o `QuotaService` para calcular e verificar limites (usuários, armazenamento).

4.  **API (Controllers & Rotas):**
    -   Criar os 4 controllers no namespace `Administration` para gerenciar Tenants, Planos, Integrações e Auditoria.
    -   Definir as rotas no `routes/api.php` agrupadas sob um prefixo `/v1/admin/` e protegidas pelo middleware `auth:sanctum`.

5.  **Segurança e Autorização:**
    -   Criar a `TenantPolicy` e registrar a habilidade `manage-tenants`.
    -   Aplicar a policy nos controllers usando `->authorize()`.
    -   Implementar as validações (hygiene de documentos, e-mails, quotas) usando Form Requests.

6.  **Observability:**
    -   Criar um `Listener` ou usar `Observers` nos models para registrar eventos na tabela `platform_tenant_audits`.
    -   Configurar os canais de log customizados em `config/logging.php`.

7.  **Finalização e Refatoração:**
    -   Executar um script para popular a coluna `company_id` nas tabelas de domínio existentes (ex: `crm_contacts`).
    -   Aplicar o trait `BelongsToTenant` em todos os models relevantes.
    -   Revisar Jobs e Queues para garantir que o `TenantContext` seja passado corretamente para processos em background.

## 3. Checklist de Segurança

-   [x] **Validação de Input (FormRequest):** A especificação exige validações estritas para documentos (CPF/CNPJ), e-mails, telefones e idempotência via hash do payload.
-   [x] **Autorização (Policies):** O acesso aos controllers de administração será restrito a `SUPER_ADMIN` e `COMPANY_OWNER` através da policy `manage-tenants`.
-   [x] **Isolamento de Dados:** O `Global Scope` no trait `BelongsToTenant` é o principal mecanismo para prevenir vazamento de dados entre tenants.
-   [x] **Segredos:** Tokens e chaves de API na tabela `platform_integrations` devem ser criptografados no banco de dados usando os recursos nativos do Laravel.
