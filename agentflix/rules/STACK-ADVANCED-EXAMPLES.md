# Exemplos Avançados: Do e Don't por Stack (AgentFlix)

Este arquivo é referenciado por CONTEXT.md, GEMINI.md e AGENT.md e contém exemplos concisos do que **fazer** (Do) e **evitar** (Don't) em cada stack usada pelo projeto.

## 1. Laravel (Backend Core)
Do:
- Usar Services/Actions para lógica; Controllers finos.
- Aplicar cache inteligente (tags/chave composta) e invalidar por evento de domínio.
- Job idempotente e pequeno; usar retries + backoff exponencial.
- Configurar Horizon com filas separadas (critical, default, low).
- Usar `route:cache`, `config:cache`, `octane` (se preciso) em produção.
Don't:
- Colocar regra de negócio pesada dentro de Model observers.
- Usar N+1 em loops sem `with()`/`lazy()`.
- Misturar acesso direto a Models em Controllers com regra complexa.
- Reprocessar jobs que não são idempotentes.

## 2. FastAPI (Serviço IA)
Do:
- Separar camadas: routers / dependencies / services / repositories / schemas.
- Usar drivers assíncronos (asyncpg) + pool configurado.
- Centralizar DI (dependências) para DB sessão e auth (JWT/OAuth2).
- Utilizar `asyncio.gather` para múltiplas chamadas externas.
- Implementar rate limiting + caching via Redis.
Don't:
- Misturar lógica de negócio diretamente dentro de funções de rota.
- Bloquear event loop com chamadas síncronas pesadas sem `run_in_executor`.
- Usar `*` em CORS em produção.

## 3. Angular 19 (Frontend)
Do:
- Usar Signals para estado local e derivado (`computed`, `effect`).
- Criar serviços com sinais para estado compartilhado; NgRx SignalStore se complexidade alta.
- Componentes standalone modulares com imports mínimos.
- Usar `@defer` para lazy load de partes não críticas.
- Seletores acessíveis: `getByRole` (Playwright) e atributos `aria-*`.
Don't:
- Colocar lógica de estado complexa em múltiplos componentes duplicados.
- Abusar de RxJS para simples estados locais onde Signals bastam.
- Deixar componentes com imports genéricos não utilizados.

## 4. PostgreSQL + pgvector
Do:
- Definir `lists` IVFFlat ≈ total_registros/1000 como base e ajustar `probes`.
- Usar HNSW para baixa latência em conjunto < milhões ativos.
- `EXPLAIN ANALYZE` rotineiro para queries de similaridade + filtros.
- Normalizar embeddings (inner product) e criar índices apropriados.
- Particionar ou segmentar por tenant se volume extremo.
Don't:
- Construir índice antes de carga em massa inicial.
- Usar filtro super restritivo sem validar recall (iterative_scan).
- Misturar JSONB não indexado com busca vetorial crítica.

## 5. Redis (Cache / Filas)
Do:
- Padrão de chave: `tenant:{id}:domain:{entidade}:{id}`.
- Implementar lock (SET NX PX) para evitar cache stampede.
- Streams para filas duráveis + consumer groups.
- Rate limiting com Lua (token/sliding window) para atomicidade.
- Usar RedisBloom para pré-filtrar duplicatas.
Don't:
- Guardar blobs gigantes (usar storage adequado).
- Deixar TTL ausente em chaves voláteis relevantes.
- Reprocessar itens de fila sem idempotência.

## 6. Tailwind CSS
Do:
- Centralizar design tokens no `tailwind.config.js` (cores, spacing, radius).
- Criar utilitários compostos com `@apply` para padrões repetidos.
- Usar JIT + purge configurado para produção.
- Ordenar classes de forma consistente (layout -> spacing -> typo -> color -> misc).
Don't:
- Duplicar sequências extensas de utilitários em múltiplos componentes.
- Criar CSS custom sem necessidade (preferir utilitários).

## 7. Docker / Compose
Do:
- Multi-stage builds (builder + runtime mínimo).
- Definir `USER` não-root no estágio final.
- Healthcheck por serviço crítico (API, IA, DB proxy).
- Separar compose base e compose.prod overrides.
- `.dockerignore` robusto (excluir .git, artefatos locais, .env).
Don't:
- Incluir dependências de build no image final.
- Usar secrets em Dockerfile ou commitá-los.
- Confiar apenas em start order sem healthcheck.

## 8. Testes (Pest / Jest / Playwright)
Do:
- Pest: usar testes de arquitetura para garantir camadas (Models, Services, Controllers).
- Jest: limpar mocks (`clearAllMocks`) e usar `test.each` para casos.
- Playwright: fixtures custom para login e dados isolados por worker.
- Priorizar testes de jornada (E2E) em fluxos críticos e unit tests para lógica pura.
Don't:
- Snapshot indiscriminado em componentes voláteis.
- Reutilizar usuário/dados mutáveis entre testes paralelos.
- Abusar de waits estáticos (usar auto-wait Playwright).

## 9. Observabilidade & Segurança
Do:
- Centralizar logs estruturados (JSON) + correlação (trace id).
- Monitorar latência p95/p99 de busca vetorial e filas.
- Aplicar SAST/Dependency Scan em CI.
Don't:
- Expor stack traces completos em produção.
- Ignorar métricas de fila (profundidade / taxa de erro).

---
Este arquivo deve ser mantido curto e objetivo; alterações extensas exigem revisão do AGENT.md.
