# GEMINI.md - AgentFlix Project

## Project Overview

This repository contains the master documentation for **AgentFlix**, a multi-tenant SaaS platform designed to provide small and medium-sized businesses with a unified solution for CRM, chat, and AI-powered automation.

The project follows a documentation-driven development approach, where Product Requirements Documents (PRDs) and Technical Specification Documents (TSDs) are created before implementation.

### Architecture

AgentFlix is built on a microservices-oriented architecture:

*   **Core Backend:** A monolithic backend built with **Laravel (PHP)**, following a Domain-Driven Design (DDD-Light) approach. It handles the main business logic for CRM, user management, etc.
*   **AI Service:** A dedicated microservice built with **Python** and **FastAPI** to handle intensive AI/ML tasks.
*   **Frontend:** A reactive, standalone-component-based single-page application (SPA) built with **Angular (TypeScript)**.
*   **Database:** **PostgreSQL** with the `pgvector` extension for vector similarity searches (likely for RAG).
*   **Infrastructure:** The entire stack is containerized with **Docker** and orchestrated with **Docker Compose**. A **Nginx** container acts as a reverse proxy, routing requests to the appropriate backend or frontend service.

### Technology Stack

| Category | Technology | Version/Padrão |
| :--- | :--- | :--- |
| **Backend (Core)** | PHP / Laravel | 8.2+ / 11+ |
| **Backend (IA)** | Python / FastAPI | 3.11+ / 0.100+ |
| **Frontend** | TypeScript / Angular | 5.2+ / 19+ |
| **Banco de Dados** | PostgreSQL + pgvector | 16+ |
| **Cache/Filas** | Redis | 7+ |
| **Estilo (CSS)** | Tailwind CSS + daisyUI | 4+ / 5+ |
| **Gráficos (FE)** | ApexCharts (ng-apexcharts) | - |
| **Container** | Docker / Docker Compose | - |
| **Testes (BE)** | Pest | - |
| **Testes (FE)** | Jest (Unit) + Playwright (E2E) | - |
| **Code Style (BE)**| Laravel Pint | - |
| **Code Style (FE)**| ESLint + Prettier | - |

## Building and Running

The project is designed to be run entirely within a Dockerized environment.

**Prerequisites:**
*   Docker Engine
*   Docker Compose

**Setup & Execution:**

1.  **Environment Files:** Ensure you have the necessary `.env` files for the `backend` and `ai_service` directories as specified in the documentation.
2.  **Build and Start Containers:** Run the following command from the project root to build the images and start all services in detached mode.
    ```bash
    docker-compose up -d --build
    ```
3.  **Accessing the Application:**
    *   The **Angular Frontend** should be accessible at `http://localhost:4200`.
    *   The **Nginx Reverse Proxy** listens on `http://localhost:80`, routing API calls to the correct services:
        *   `/api/core/` -> Laravel Backend
        *   `/api/ai/` -> Python AI Service
4.  **Stopping the Environment:**
    ```bash
    docker-compose down
    ```
5.  **Executing Commands in Services:**
    You can run commands directly inside a running container using `docker-compose exec`.
    ```bash
    # Example: Run Laravel migrations
    docker-compose exec backend php artisan migrate

    # Example: Install a Python dependency
    docker-compose exec ai_service pip install pandas
    ```

## Development Conventions

*   **Documentation First:** New features or modules begin with a PRD (What to build) and a TSD (How to build it).
*   **Domain-Driven Design (DDD-Light):** The Laravel backend is organized by business domains. Logic should be encapsulated in Service classes, keeping Controllers thin.
*   **Contracts (Interfaces):** Use interfaces to abstract concrete implementations, promoting flexibility and testability.
*   **Standalone Components:** The Angular frontend favors `standalone` components and leverages `Signals` for state management.
*   **Database:**
    *   Primary keys are UUIDs.
    *   Multi-tenancy is enforced with a `company_id` column on relevant tables.
    *   Soft deletes (`deleted_at` column) are used.
*   **API:** Endpoints are versioned (e.g., `/api/v1/`) and secured with Sanctum.
*   **Code Style:** Code style is enforced using **Laravel Pint** for the backend and **ESLint/Prettier** for the frontend.

## Advanced Stack Guidelines (Resumo)
Consulte detalhes e exemplos de Do/Don't em `rules/STACK-ADVANCED-EXAMPLES.md`.
- **Laravel:** Services/Actions; cache tagueado; filas separadas por criticidade; evitar N+1.
- **FastAPI:** DI + async all the way; `asyncio.gather`; evitar bloqueio de event loop.
- **Angular 19:** Signals para estado local/derivado; standalone components; `@defer` e SSR hydration estratégica.
- **PostgreSQL/pgvector:** Ajuste de `lists`/`probes`; escolha HNSW vs IVFFlat por perfil; `EXPLAIN ANALYZE` rotineiro.
- **Redis:** Padrões de chave; Streams para durabilidade; rate limiting com Lua; evitar objetos gigantes.
- **Tailwind:** Tokens centralizados; purge/JIT; evitar duplicação massiva de util classes.
- **Docker/Compose:** Multi-stage; usuário não-root; healthchecks; separar compose.prod.
- **Testes:** Pest arquitetura; Jest mocks limpos; Playwright fixtures isoladas e locators acessíveis.

