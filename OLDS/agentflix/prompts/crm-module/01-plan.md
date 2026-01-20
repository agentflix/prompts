# Technical Plan: CRM Module

## 1. Análise de Impacto

### Arquivos Afetados (Novos e Modificados)

-   **Nota sobre Arquitetura:** A especificação menciona `{schema}`. Seguiremos a arquitetura de **single-schema multi-tenancy** já estabelecida, onde cada tabela afetada receberá uma coluna `company_id` e usará o trait `BelongsToTenant`.

-   **Migrations:**
    -   `create_crm_contacts_table`
    -   `create_crm_companies_table`
    -   `create_crm_funnels_table`
    -   `create_crm_funnel_steps_table`
    -   `create_crm_segments_table`
    -   `create_crm_sources_table`
    -   `create_crm_reason_losses_table`
    -   `create_crm_negotiations_table`
    -   `create_crm_product_services_table` (implícito)
    -   `create_crm_negotiation_products_table`
    -   `create_crm_activity_logs_table` (implícito)

-   **Models (app/Models/Crm):**
    -   `Contact`, `Company`, `Funnel`, `FunnelStep`, `Negotiation`, etc. (um para cada nova tabela).
    -   Todos os models multi-tenant deverão usar o trait `App\Models\Concerns\BelongsToTenant`.

-   **Controllers (app/Http/Controllers/Crm):**
    -   `ContactController.php`
    -   `CompanyController.php`
    -   `NegotiationController.php`
    -   `FunnelController.php` (para gerenciamento dos funis e etapas)

-   **Services (app/Services/Crm):**
    -   `ContactService.php` (para lógica de negócio, incluindo integração com WhatsApp).
    -   `ContactImportService.php` (para importação de CSV).
    -   `NegotiationService.php` (para orquestrar a lógica de `win`, `lose`, `move`).
    -   `TimelineService.php` (para montar a timeline do contato).

-   **Events (app/Events/Crm):**
    -   `NegotiationMoved`, `NegotiationWon`, `NegotiationLost`.

-   **Testes (Pest):**
    -   `tests/Feature/Crm/ContactManagementTest.php`
    -   `tests/Feature/Crm/NegotiationManagementTest.php`
    -   `tests/Unit/Services/ContactImportServiceTest.php`

### Novas Dependências
-   Nenhuma nova dependência externa de pacotes. A implementação dependerá de integrações de WhatsApp já existentes na plataforma (`IntegrationFactory`).

## 2. Estratégia de Implementação (Backend - Laravel)

1.  **Estrutura do Banco de Dados:**
    -   Criar todas as migrations para as tabelas do CRM, garantindo a adição do `company_id` e a aplicação de índices conforme a especificação.
    -   Definir os Models correspondentes no namespace `App\Models\Crm`, aplicando o trait `BelongsToTenant` e definindo os relacionamentos (`hasMany`, `belongsTo`, etc.).

2.  **Módulo de Contatos (Core):**
    -   Implementar o `ContactController` com os endpoints `GET`, `POST`, `PUT`, `DELETE`.
    -   Para o `GET`, construir um `QueryBuilder` dinâmico que aplica os filtros (search, type, source, etc.) de forma eficiente. Implementar os `scopes` no `Contact` Model.
    -   Para o `POST`, encapsular a lógica de verificação de duplicatas e busca de dados no WhatsApp dentro do `ContactService`.
    -   Para o `DELETE`, garantir a verificação de negociações ativas antes do soft delete.

3.  **Módulo de Importação/Exportação:**
    -   Desenvolver o `ContactImportService` para processar arquivos CSV em background (usando um Job) para evitar timeouts. O Job deve retornar um relatório de sucesso e erros.
    -   Implementar o endpoint de sincronização de contatos do WhatsApp.
    -   Implementar o endpoint de exportação para CSV, utilizando `StreamedResponse` para lidar com grandes volumes de dados sem esgotar a memória.

4.  **Módulo de Negociações (Pipeline):**
    -   Implementar CRUDs simples para as entidades de suporte: `Funnels`, `FunnelSteps`, `Segments`, `Sources`, `ReasonLosses`.
    -   Desenvolver o `NegotiationController` e o `NegotiationService`.
    -   **Endpoint de Kanban:** A lógica deve ser otimizada para evitar N+1 queries. Agrupar as negociações por `funnel_step_id` e agregar os totais no lado do servidor.
    -   **Ações de `win`/`lose`/`move`:** A lógica de negócio deve ser encapsulada no `NegotiationService` e executada dentro de `DB::transaction()` para garantir a consistência atômica das operações (ex: atualizar negociação, atualizar LTV do contato, disparar evento).

5.  **Módulo de Timeline:**
    -   Criar o `TimelineService` que irá coletar dados de múltiplas tabelas (`activity_logs`, `negotiation_history`, `tasks`, `calleds`), uni-los em uma única coleção e ordená-los por data para construir a visão unificada.

## 3. Checklist de Segurança

-   [x] **Validação de Input (FormRequest):** Cada endpoint `POST`/`PUT` terá um FormRequest dedicado para validar os dados de entrada.
-   [x] **Autorização (Policies):** Será criada uma `CrmPolicy` para controlar o acesso. Por exemplo, um usuário só pode ver/editar contatos e negociações dos quais ele é responsável ou que pertencem ao seu departamento, a menos que ele tenha permissão de administrador.
-   [x] **Prevenção de N+1:** Todos os endpoints de listagem que retornam dados relacionados (`GET /api/crm/contact`, `GET /api/crm/negotiation/kanban`) devem usar `with()` para eager load das relações e evitar múltiplas queries.
-   [x] **Escopo de Tenant:** O uso obrigatório do trait `BelongsToTenant` em todos os models do CRM é a principal garantia de que uma empresa não poderá acessar dados de outra.
-   [x] **Tratamento de Erros:** Usar `try-catch` e transações de banco de dados, especialmente em operações complexas como importações e o fluxo de `win`/`lose` de negociações, para fornecer feedback claro em caso de falha.
