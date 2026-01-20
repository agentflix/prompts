# Prompt de Execução: Administration & Tenant Provisioning Module

## Contexto (Role)

Aja como **Sênior Backend Dev especialista em Laravel**. Sua tarefa é implementar o módulo de administração e provisionamento multi-tenant para a plataforma AgentFlix, seguindo rigorosamente a arquitetura e as regras de negócio abaixo.

## Stack Obrigatória (Context Injection)

-   **Backend:** Laravel 11+ (PHP 8.3+)
-   **Design Patterns:** Service Pattern, Repository Pattern, DTOs (Spatie/laravel-data).
-   **Testes:** Pest (TDD é obrigatório).
-   **Banco de Dados:** PostgreSQL.
-   **Autenticação:** Laravel Sanctum.

---

## Instruções de Trabalho (The Loop)

1.  **Leia** a Spec Lógica completa abaixo.
2.  **TDD (Red):** Para cada serviço ou funcionalidade, crie primeiro um teste que falhe em `tests/Feature/Administration/`.
3.  **Code (Green):** Implemente a lógica mínima para o teste passar. Foque nos `Services` para a lógica de negócio. Mantenha os `Controllers` enxutos.
4.  **Refactor:** Otimize o código, aplique Clean Code e garanta que os padrões de design foram seguidos.
5.  **Verify:** Rode a suíte de testes completa para garantir que nada foi quebrado.

---

## Spec Lógica (Input Data)

### 1. Objetivo Principal

Construir o sistema de backend para gerenciar o ciclo de vida de `Tenants` (clientes da plataforma), garantindo isolamento de dados em um único schema de banco de dados através de uma coluna `company_id`.

### 2. Estrutura de Dados e Isolamento

#### 2.1. Migrations

Crie as migrations para as seguintes tabelas. Use UUIDs como chaves primárias.

-   **`platform_tenants`**: Armazena os dados principais de cada tenant.
    ```sql
    CREATE TABLE platform_tenants (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(120) UNIQUE NOT NULL,
        document VARCHAR(14) UNIQUE NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending | active | suspended | cancelled
        plan_id UUID NULL,
        max_active_users INTEGER NOT NULL DEFAULT 5,
        primary_owner_id UUID NULL,
        -- ... demais campos da spec
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    ```

-   **`platform_tenant_settings`**: Pares de chave-valor para configurações do tenant.
-   **`platform_tenant_users`**: Tabela pivô para vincular usuários globais a tenants com um `role`.
-   **`platform_integrations`**: Gerencia integrações de API (WhatsApp, etc.) por tenant.
-   **`platform_tenant_audits`**: Log de ações críticas realizadas no tenant.

#### 2.2. Isolamento de Dados (Trait `BelongsToTenant`)

Crie um trait `app/Models/Concerns/BelongsToTenant.php`. Ele deve aplicar um `Global Scope` que filtra automaticamente todas as queries pelo `company_id` do tenant autenticado.

```php
// app/Models/Concerns/BelongsToTenant.php
protected static function bootBelongsToTenant(): void
{
    static::addGlobalScope('tenant', function ($builder) {
        // A classe TenantContext será criada para obter o ID.
        if (app()->bound(TenantContext::class) && ($tenantId = TenantContext::id())) {
            $builder->where($builder->qualifyColumn('company_id'), $tenantId);
        }
    });
}
```

#### 2.3. Contexto do Tenant

Crie um `TenantContext` e um `TenantServiceProvider` para identificar e armazenar os dados do tenant atual (`id`, `plan`, `quotas`) em um singleton de requisição.

### 3. Core: Fluxo de Provisionamento (`TenantProvisioningService`)

Implemente o serviço `app/Services/Platform/TenantProvisioningService.php`. O método `create(array $data)` deve orquestrar o seguinte fluxo:

1.  **Validação:** Garanta que `document` e `slug` são únicos.
2.  **Persistência:** Insira o registro em `platform_tenants` com `status='pending'`.
3.  **Owner:** Crie o primeiro usuário (`role=company_owner`) na tabela `platform_tenant_users`.
4.  **Settings:** Insira as configurações padrão (`business_hours`, `sla`, etc.) em `platform_tenant_settings`.
5.  **Billing Sync:** Dispare um evento ou chame um serviço (mock por enquanto) para registrar o cliente no gateway de pagamento (Asaas).
6.  **Auditoria:** Registre o evento `tenant.created` na tabela `platform_tenant_audits`.
7.  **Ativação:** Crie um método `activate(Tenant $tenant)` que muda o status para `active` e enfileira jobs de onboarding.

### 4. API (Controllers & Segurança)

-   **Namespace:** `App\Http\Controllers\Administration`.
-   **Rotas:** Agrupadas sob `/v1/admin/` e protegidas por `auth:sanctum`.
-   **Controllers:**
    -   `TenantController`: CRUD para tenants.
    -   `TenantPlanController`: Upgrade/downgrade de planos.
    -   `TenantIntegrationController`: CRUD para integrações.
    -   `TenantAuditController`: Leitura dos logs de auditoria.
-   **Autorização:** Crie uma `TenantPolicy` com a permissão `manage-tenants` e aplique-a nos métodos dos controllers para garantir que apenas `SUPER_ADMIN` ou `COMPANY_OWNER` possam realizar operações.

### 5. Regras de Negócio e Safeguards

-   **Validação de Documento:** CPF/CNPJ devem ser sanitizados (somente dígitos) e ter o checksum validado antes de salvar.
-   **Idempotência:** O método `TenantProvisioningService::create` deve ser idempotente. Use um hash do payload de entrada para evitar a criação de tenants duplicados em caso de retentativas de API.
-   **Verificação de Quota:** Antes de criar recursos como usuários ou integrações, verifique os limites (`max_active_users`, etc.) definidos no plano do tenant. Lance uma `QuotaExceededException` (código 409 Conflict) se o limite for ultrapassado.
-   **Criptografia:** Todos os tokens e segredos na tabela `platform_integrations` devem ser criptografados usando o sistema nativo do Laravel (`$casts = ['access_token' => 'encrypted']`).
