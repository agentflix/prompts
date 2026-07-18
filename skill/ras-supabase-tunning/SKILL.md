---
name: ras-supabase-tunning
description: >-
  Metodologia replicável de diagnóstico e tuning de performance de Postgres/Supabase
  em produção (foco em CPU), destilada de um caso real de incidente resolvido. Use quando:
  banco lento / CPU alta, erros de statement timeout (57014 "canceling statement due to
  statement timeout"), relato "o servidor fica lento às vezes", ANTES de escalar hardware,
  ou para auditar o volume de requisições que um app faz. Cobre diagnóstico (pg_stat_statements,
  seq scans, índices, RLS, Realtime, tipo de instância), correção priorizada por risco/ganho
  (índices → reescrita de RPC → frontend → arquitetura), medição honesta (reset + comparar
  mesmo horário do dia, contar 57014 nos logs, auditoria de rede no navegador) e as armadilhas
  que custam caro (vazamento cross-user ao otimizar no cliente, instância burstable, CONCURRENTLY,
  MCP read-only, população mista pós-deploy). NÃO use para modelagem de schema nova do zero nem
  para bugs funcionais sem componente de performance.
---

# Tuning de performance Supabase/Postgres (RAS)

Playbook destilado de um incidente real: Postgres de produção saturando CPU (100%), enxurrada de
`57014` (statement timeout), app travando. Resolvido **sem trocar hardware** — de ~100% para ~15%
no pico — via diagnóstico dirigido por dados + correções priorizadas + medição honesta.

**Princípio central:** **meça antes de mexer, e mexa do menor risco pro maior.** A maior parte do
ganho vem de eliminar trabalho repetido (queries por evento, re-scans), não de "otimizar SQL" solto.

**Regra de ouro (aprendida na dor):** **isolamento é sagrado.** Qualquer otimização que mova lógica
do servidor para o cliente (contadores, surface de itens, cache) DEVE replicar a visibilidade que a
RPC/RLS aplicava (org, papel `is_agent`, `assigned_agent_id`, participante). Senão vaza dado entre
usuários/orgs — e isso é pior que lentidão. Ver a Fase 4 e as Armadilhas.

---

## Fluxo (5 fases)

### Fase A — Diagnóstico (nunca pule; meça primeiro)

Objetivo: descobrir **onde o tempo vai** e se é CPU ou I/O. Tudo leitura — pode rodar direto.

1. **CPU ou I/O?** `cache_hit_ratio` ~100% ⇒ **CPU-bound** (quase nada vem de disco; o tempo é
   processamento: funções STABLE repetidas, seq scans em memória, RLS por linha). Confira `jit=off`.
2. **Quem consome tempo de banco:** `pg_stat_statements` ordenado por `total_exec_time`.
   - No Supabase a view fica no schema **`extensions`** (`extensions.pg_stat_statements`).
   - `round(double precision, int)` não existe → **cast `::numeric`**.
   - PostgREST manda **RPC como POST**, **update como PATCH**, e SELECT como GET. Muitas vezes o
     **GET é irrelevante** e o custo está em **POST (RPCs)** e **PATCH (heartbeats)**.
3. **O que causa os `57014`:** `max_exec_time` perto do `statement_timeout` do papel
   (Supabase default: `authenticated`=8s, `anon`=3s). Query batendo em ~8000ms = a que é cancelada.
4. **Seq scans:** `pg_stat_user_tables` por `seq_tup_read`. **Cuidado:** tabela minúscula (dezenas de
   linhas) SEMPRE faz seq scan (é o certo) — número gigante ali = **volume de chamadas** (ex.: RLS
   helper `is_org_member` por linha), NÃO falta de índice.
5. **Índices:** `pg_stat_user_indexes` — `idx_scan=0` (não usados → dropar, economiza CPU de escrita)
   e duplicados/prefixos redundantes. **Não** dropar índices do schema `auth`.
6. **RLS:** conte **policies permissivas múltiplas** por tabela/comando (o Postgres avalia TODAS e
   faz OR → custo por linha, ainda mais se cada uma chama `is_org_member`/`has_org_role`). Procure
   `auth.uid()` **não** encapsulado em `(SELECT auth.uid())` (reavaliado por linha).
7. **Realtime:** quais tabelas estão na publicação `supabase_realtime`; `wal2json` com volume enorme =
   publicação larga + tabelas de alta escrita (heartbeats!) sendo decodificadas.
8. **Hardware:** tipo de instância. Famílias `t*` (ex.: `t4g`) são **burstable** (base baixa + burst);
   no Supabase, **Micro/Small/Medium = 2 cores compartilhados**; só **Large+** é CPU dedicada e
   **XL = 4 cores**. **Subir de Small→Medium adiciona só RAM, não núcleos** — não resolve CPU.

> Advisors: `get_advisors(security)` funciona; o de `performance` pode falhar com bug interno
> (`syntax error near 'storage.buckets'`) — nesse caso compute os sinais via SQL (queries acima).

### Fase B — Índices (baixo risco, reversível) — faça primeiro

- **Índice parcial** para o filtro quente (ex.: não-lidas: `WHERE status<>'read' AND type<>'system'`)
  — costuma ser o maior ganho isolado.
- **Dropar** duplicados/não-usados (confirme que o "keeper" existe antes de dropar o "prefixo").
- **FK sem índice**: só crie se a tabela for grande E a coluna for filtrada; em tabela de poucos
  milhares de linhas, índice de FK **não ajuda leitura e adiciona custo de escrita** — pule.
- `CONCURRENTLY` (sem lock) **não roda dentro de transação** → SQL Editor e `db push` embrulham em
  transação e falham; use **psql** ou o **MCP `execute_sql`** (que é autocommit por chamada).
  Verifique validade depois (`SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid`).

### Fase C — Reescrever as RPCs quentes (ganho alto)

Pegue a RPC nº1 por `total_exec_time`/`mean` e rode `EXPLAIN (ANALYZE, BUFFERS)` do corpo dela com
valores reais (reconstrua com literais, ou simule o viewer). Padrões que mais pesam e como atacar:

- **CTE materializada re-escaneada N vezes** → o Postgres materializa CTE referenciada mais de uma
  vez; produzir+reler custa muito. Reduza referências ou reestruture.
- **Anti-join correlacionado por linha** (`NOT EXISTS (... por ticket)`) → troque por **array
  pré-computado** + `NOT (x = ANY(array))`, e booleanos do viewer computados **uma vez**.
- **`SET work_mem` maior**: só se os sorts **derramam em disco** (`Sort Method: external`). Se é
  `quicksort ... Memory`, NÃO mexa (aumenta pressão de RAM à toa).
- **Preserve a assinatura** da função → frontend não muda. `CREATE OR REPLACE` com a MESMA assinatura
  (senão vira **overload órfão** e pode vazar entre orgs).
- **Validação antes de trocar:** prove equivalência. Se só mudou um CTE, compare os **conjuntos**
  (EXCEPT nos dois sentidos) em vários (org, usuário) reais — `only_old=only_new=0`. Depois EXPLAIN
  novo vs antigo pra confirmar a queda de tempo.

### Fase D — Frontend / arquitetura (o maior ganho estrutural, o maior risco)

O gargalo real costuma ser **fan-out**: N clientes recalculando o mesmo estado da org a cada evento
de realtime = `O(N × eventos)`. Alavancas:

- **Heartbeats** (presença/sessão): aumentar o intervalo (ex.: 30s→60s) corta escrita → menos WAL →
  menos `wal2json`. **Cuidado com thresholds dependentes** (ex.: `STALE_THRESHOLD` que marca offline;
  mantenha a razão ~3× o heartbeat). Confirme que não há reaper server-side por heartbeat velho.
- **Debounce + trava de in-flight** no refetch de realtime (não empilhar consultas sob carga). Útil,
  mas **não reduz frequência** sob eventos contínuos — é paliativo.
- **Cache** (React Query staleTime; ou memoização) para deduplicar buscas repetidas (ex.: mesmo
  contato aberto em vários componentes).
- **Estado incremental** (a mudança arquitetural de verdade): o cliente atualiza contador/lista a
  partir do **evento que já recebe**, em vez de re-perguntar ao servidor; com **reconciliação
  periódica** (ex.: 60–120s) como rede contra drift. Isso tira o `O(N×eventos)`.

> ⚠️ **A lição cara:** ao mover lógica pro cliente (surface de conversa nova, contadores locais),
> **replique a visibilidade do servidor**. No caso real, o surface inseria qualquer ticket `open` da
> org na aba checando só os filtros de UI — mas a RPC restringia por papel `is_agent`
> (`NOT is_agent OR assigned_agent_id IS NULL OR assigned_agent_id = uid`). Resultado: **agente via
> chamado de outro agente** → tivemos que fazer **rollback**. Antes de reintroduzir: bootstrap de
> `is_agent`/`dept_ids` do viewer e aplique a MESMA regra da RPC no cliente. Sempre valide isolamento
> com 2 usuários/orgs simultâneos.

### Fase E — Medir (honestamente) e iterar

- `SELECT extensions.pg_stat_statements_reset();` e anote o marco. Compare em 24h.
- **Compare mesmo horário do dia** (pico manhã vs pico manhã) — senão você confunde melhora real com
  "menos gente à noite" (efeito diurno).
- Conte `57014` nos logs (`get_logs(postgres)`), ou via `max_exec_time >= 7900` no pg_stat_statements
  (`0` = sem timeout).
- **Auditoria de rede no navegador** (browser-harness/CDP): conte GET/POST/PATCH por cliente e agrupe
  por rota/RPC. É como se descobre o fan-out real ("página parada disparando 13 RPCs/min").
- **População mista:** depois do deploy do frontend, clientes antigos e novos coexistem até
  recarregarem — a melhora entra gradual.

---

## Armadilhas (todas custaram tempo no caso real)

- **Projeto linkado errado:** `supabase/config.toml` (`project_id`) pode divergir do link real
  (`supabase/.temp/project-ref`). O `db push` usa o link. **Confirme o `project-ref` antes.**
- **MCP pode estar read-only:** escritas vão por migration (`db push`) + SQL Editor. Teste a permissão
  com um no-op inofensivo: `CREATE TEMP TABLE _probe(n int)` (falha com `25006` se read-only).
- **`db push` aplica TODAS as migrations pendentes** — liste antes (`list_migrations` vs arquivos
  locais) pra não empurrar feature de terceiro num deploy de performance.
- **CONCURRENTLY** não roda em transação (SQL Editor / db push). Use psql ou MCP autocommit.
- **GET não é o vilão** — quase sempre são POST (RPCs) e PATCH (heartbeats). Não se engane com a
  pergunta "quantos GET".
- **Burstable / RAM:** `t*` é burstable; subir RAM (Small→Medium) **não** adiciona CPU. Para CPU real,
  precisa de tier dedicada com mais núcleos (XL). Software costuma resolver antes de gastar nisso.
- **Isolamento cross-user/cross-org** ao otimizar no cliente (ver Fase D). Sempre valide com 2 orgs.
- **Reversibilidade:** trabalhe em commits pequenos e revertíveis; tenha o `git revert` pronto. Um
  ganho de performance que vaza dado deve ser revertido **imediatamente** — correção > performance.
- **Gate de CI:** ao mudar comportamento, atualize os testes que fixavam o comportamento antigo
  (senão o CI de cobertura quebra). Rode typecheck + lint + suíte + build antes de commitar.

---

## Ordem recomendada de execução

1. **Diagnóstico completo** (Fase A) — documente o baseline (top queries, % CPU, 57014).
2. **Índices** (Fase B) — alívio imediato, reversível.
3. **Reescrita da RPC nº1** (Fase C) — valide equivalência antes de trocar.
4. **Reset do pg_stat_statements + medir** (Fase E) — veja o efeito.
5. **Frontend/arquitetura** (Fase D) — com a regra de isolamento na frente.
6. **Medir de novo no pico** e decidir se ainda precisa (hardware vira último recurso).

O SQL de diagnóstico pronto está em `references/diagnostic-queries.sql`.
