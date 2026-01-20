# 03 — Administration & Tenant Provisioning Module

> Governs the full tenant lifecycle on a single PostgreSQL schema, enforcing `company_id` isolation, plan licensing, integrations, and auditability for every customer workspace.

---

## 1. Module Scope

The Administration module is the source of truth for everything related to tenants (AgentFlix customers). It is restricted to `SUPER_ADMIN` operators and, when explicitly delegated, `COMPANY_OWNER` partners. The scope covers:

-   Creating and approving tenants, their first owner, billing profile, and default limits.
-   Assigning subscription plans, feature toggles, and storage/seat quotas.
-   Managing WhatsApp/API integrations, tokens, and operational states.
-   Enforcing tenant-aware authorization by guaranteeing that every domain record carries a `company_id`.
-   Capturing high-value audit events (creation, suspension, deletion, integration changes).

---

## 2. Domain Responsibilities

| Capability              | Description                                                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Tenant lifecycle        | Create, update, suspend, and delete tenants while preserving referential integrity across the single schema.                         |
| Plan & quota management | Store commercial plans, active modules (CRM, Chat, Agenda, RAG, AI), and quantitative limits such as maximum seats or conversations. |
| Integration management  | Register WhatsApp providers, API keys, and connection health for each tenant.                                                        |
| Observability           | Emit structured audit logs and metrics for governance agents.                                                                        |

---

## 3. Single-Schema Data Model

All tenant-specific tables share the same PostgreSQL schema. Isolation happens through a `company_id UUID` column plus a global scope that filters queries by the authenticated tenant.

### 3.1 `platform_tenants`

```sql
CREATE TABLE platform_tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    document VARCHAR(14) UNIQUE NOT NULL,          -- CPF/CNPJ sanitized
    timezone VARCHAR(64) NOT NULL DEFAULT 'America/Sao_Paulo',
    billing_email VARCHAR(255) NOT NULL,
    billing_phone VARCHAR(20),
    plan_id UUID NULL REFERENCES billing_plans(id),
    plan_cycle VARCHAR(10) NOT NULL DEFAULT 'monthly',
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending | active | suspended | cancelled
    modules JSONB NOT NULL DEFAULT '[]',           -- e.g. ["CRM","CHAT","AI"]
    max_active_users INTEGER NOT NULL DEFAULT 5,
    storage_quota_mb INTEGER NOT NULL DEFAULT 2048,
    primary_owner_id UUID NULL REFERENCES platform_users(id),
    billing_provider_customer_id VARCHAR(120),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deactivated_at TIMESTAMPTZ NULL
);
CREATE INDEX idx_platform_tenants_status ON platform_tenants(status);
CREATE INDEX idx_platform_tenants_plan ON platform_tenants(plan_id, status);
```

### 3.2 `platform_tenant_settings`

```sql
CREATE TABLE platform_tenant_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES platform_tenants(id) ON DELETE CASCADE,
    key VARCHAR(120) NOT NULL,
    value JSONB NOT NULL,
    UNIQUE (tenant_id, key)
);
```

Used for advanced toggles (business hours, default SLA, AI temperature). This table is loaded through the `TenantSettingsRepository` and cached per tenant.

### 3.3 `platform_tenant_users`

```sql
CREATE TABLE platform_tenant_users (
    tenant_id UUID NOT NULL REFERENCES platform_tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL,           -- company_owner | manager | attendant
    department_id UUID NULL REFERENCES crm_departments(id),
    active BOOLEAN NOT NULL DEFAULT true,
    invited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at TIMESTAMPTZ NULL,
    PRIMARY KEY (tenant_id, user_id)
);
CREATE INDEX idx_platform_tenant_users_role ON platform_tenant_users(tenant_id, role);
```

This pivot allows a global `users` directory while enforcing per-tenant RBAC.

### 3.4 `platform_integrations`

```sql
CREATE TABLE platform_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES platform_tenants(id) ON DELETE CASCADE,
    provider VARCHAR(40) NOT NULL,          -- codechat | evolution | zapi | custom
    label VARCHAR(120) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    phone_e164 VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT false,
    connection_state VARCHAR(20) NOT NULL DEFAULT 'disconnected',
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_synced_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_platform_integrations_state ON platform_integrations(tenant_id, is_active, connection_state);
```

### 3.5 Tenant-aware domain tables

Every multi-tenant table outside the platform namespace must include:

```php
Schema::table('crm_contacts', function (Blueprint $table) {
    $table->uuid('company_id')->index();
    $table->foreign('company_id')->references('id')->on('platform_tenants')->cascadeOnDelete();
});
```

A reusable trait keeps queries scoped:

```php
// app/Models/Concerns/BelongsToTenant.php
protected static function bootBelongsToTenant(): void
{
    static::addGlobalScope('tenant', function ($builder) {
        $builder->where($builder->qualifyColumn('company_id'), TenantContext::id());
    });
}
```

`TenantContext::id()` is hydrated by `TenantServiceProvider` based on the authenticated user and cached in the request container.

---

## 4. Tenant Lifecycle

### 4.1 Creation Flow

1. **Validation** — ensure unique document, slug, billing email, and confirm plan availability.
2. **Persist Tenant** — insert into `platform_tenants` with `status=pending`.
3. **Bootstrap Owner** — create the first `platform_tenant_users` row and link to an existing `users` record (or invite).
4. **Seed Settings** — insert default records in `platform_tenant_settings` (business hours, SLA, AI defaults).
5. **Plan Sync** — call Billing service to create/update the product on Asaas and store the `billing_provider_customer_id`.
6. **Emit Audit** — log `tenant.created` with metadata (operator, payload checksum).
7. **Activate** — once payment is confirmed, update `status=active`, unlock modules, and enqueue onboarding jobs (sample contacts, default departments, welcome messages).

### 4.2 Update Flow

-   PATCH operations are limited to legal info, billing contacts, quotas, and module toggles.
-   Every change writes to `platform_tenant_audits` (see section 7) with the diff payload.
-   When plan or module changes affect quotas, `QuotaService` recomputes effective limits and updates cache keys consumed by guards (`MaxUsersGuard`, `MaxIntegrationsGuard`).

### 4.3 Suspension & Deletion

| Scenario               | Behaviour                                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Temporary suspension   | Set `status='suspended'`, revoke tokens, disable integrations, keep data. Nightly job cleans sessions.                                              |
| Permanent cancellation | Set `status='cancelled'`, queue anonymization job that deletes PII from `users`, `contacts`, `messages` but keeps aggregated metrics.               |
| Hard delete            | Only Super Admins can hard-delete after retention period. A background worker removes all `company_id` data by chunking tables to avoid long locks. |

### 4.4 Ownership transfer

-   Transfer is executed by `TenantOwnerService`. It reassigns `platform_tenants.primary_owner_id` and ensures there is exactly one `COMPANY_OWNER` flagged per tenant.
-   The outgoing owner is downgraded to `MANAGER` unless explicitly removed.

---

## 5. Controllers & Services

| Component                                                  | Responsibility                                                                                                                         |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `App\Http\Controllers\Administration\TenantController` | REST CRUD for `platform_tenants`, including filters (`status`, `plan_id`, `text`).                                                     |
| `TenantPlanController`                                     | Endpoints to upgrade/downgrade plans and recalculate quotas. Publishes `PlanChanged` events consumed by Billing and Notifier services. |
| `TenantIntegrationController`                              | CRUD for `platform_integrations`, restart/disconnect actions, and health checks against external providers.                            |
| `TenantAuditController`                                    | Paginated view of `platform_tenant_audits` for compliance teams.                                                                       |
| `TenantProvisioningService`                                | Orchestrates the creation flow described in section 4.1.                                                                               |
| `TenantContext`                                            | Request-scoped provider exposing current tenant id, plan, and quotas to downstream services.                                             |

All controllers live under `app/Http/Controllers/Administration/` and are protected by `auth:sanctum` + `can:manage-tenants` policies.

---

## 6. Validation & Safeguards

1. **Document hygiene** — CPF/CNPJ sanitized to digits, validated with checksum, and stored unformatted.
2. **Contact constraints** — `billing_email` must be company-owned (no free email providers in production) and `billing_phone` must be E.164.
3. **Quota gates** — attempts to create users/integrations beyond `max_active_users` or the plan limits raise `QuotaExceededException` before any DB write.
4. **Module compatibility** — enabling modules like `AI` or `RAG` performs capability checks (e.g., confirm embeddings quota, ensure S3 bucket configured).
5. **Idempotency** — `TenantProvisioningService::create` leverages a SHA-256 fingerprint of the payload to guarantee that repeated requests (e.g., retries from UI) do not create duplicates.

---

## 7. Observability & Auditing

### 7.1 Audit table

```sql
CREATE TABLE platform_tenant_audits (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES platform_tenants(id) ON DELETE CASCADE,
    action VARCHAR(60) NOT NULL,             -- tenant.created, tenant.updated.plan, integration.restarted
    actor_id UUID NULL REFERENCES users(id),
    actor_name VARCHAR(255),
    payload JSONB NOT NULL,
    ip VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_platform_tenant_audits_action ON platform_tenant_audits(tenant_id, action);
```

### 7.2 Log channels

`config/logging.php` defines `tenant_lifecycle` and `tenant_integrations` channels with 180-day retention. Every external call (Asaas, WhatsApp providers) logs request/response metadata redacting secrets.

### 7.3 Metrics

`TenantMetricsCollector` pushes Prometheus counters for `tenants_active_total`, `tenants_suspended_total`, and histograms for provisioning time. These metrics feed the governance pipeline described in `docs/architecture/08-testing-architecture.md`.

---

## 8. Next Steps

1. Implement the `BelongsToTenant` trait in every domain model that handles customer data.
2. Backfill `company_id` for legacy tables and remove any multi-schema logic (`account:db-create`, custom search paths, supervisor Gigatron password, etc.).
3. Review all jobs/queues to ensure `TenantContext` is serialized alongside payloads so workers run under the correct tenant.
4. Align documentation on Billing, Integrations, and AI modules with the new platform tables defined here.

_Previous: [02-data-structure.md](./02-data-structure.md)_
_Next: [04-authentication-module.md](./04-authentication-module.md)_
_Back to [Index](./00-index.md)_
