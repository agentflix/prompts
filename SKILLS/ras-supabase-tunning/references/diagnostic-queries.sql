-- =====================================================================
-- ras-supabase-tunning — SQL de diagnóstico (Supabase/Postgres)
-- Tudo LEITURA (não exige aprovação). Rode via MCP execute_sql, SQL Editor ou psql.
-- No Supabase, pg_stat_statements vive no schema `extensions`.
-- Sempre cast ::numeric antes de round() (round(double precision,int) não existe).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0) CPU vs I/O + config + conexões (é CPU-bound?)
-- ---------------------------------------------------------------------
SELECT
  (SELECT round(100*sum(heap_blks_hit)/nullif(sum(heap_blks_hit+heap_blks_read),0),2)
     FROM pg_statio_user_tables) AS cache_hit_pct,   -- ~100 => CPU-bound
  (SELECT count(*) FROM pg_stat_activity WHERE state='active') AS ativas,
  (SELECT count(*) FROM pg_stat_activity WHERE state='idle in transaction') AS idle_in_txn,
  (SELECT setting FROM pg_settings WHERE name='max_connections') AS max_conn,
  (SELECT setting||' '||unit FROM pg_settings WHERE name='shared_buffers') AS shared_buffers,
  (SELECT setting FROM pg_settings WHERE name='jit') AS jit;

-- statement_timeout por role (o teto que gera 57014)
SELECT r.rolname, cfg
FROM pg_roles r, LATERAL unnest(r.rolconfig) AS cfg
WHERE cfg LIKE 'statement_timeout=%'
  AND r.rolname IN ('authenticated','anon','authenticator','service_role','postgres');

-- ---------------------------------------------------------------------
-- 1) Maiores consumidores de TEMPO de banco (o que otimizar primeiro)
-- ---------------------------------------------------------------------
SELECT
  round((s.total_exec_time)::numeric,0) AS total_ms,
  round((100*s.total_exec_time/sum(s.total_exec_time) over ())::numeric,1) AS pct,
  s.calls,
  round((s.mean_exec_time)::numeric,1) AS mean_ms,
  round((s.max_exec_time)::numeric,0)  AS max_ms,   -- perto do statement_timeout => causa 57014
  round((s.rows::numeric/nullif(s.calls,0)),1) AS rows_call,
  left(regexp_replace(s.query,'\s+',' ','g'),140) AS query
FROM extensions.pg_stat_statements s
ORDER BY s.total_exec_time DESC
LIMIT 20;

-- Por FREQUÊNCIA (acha polling/refetch por evento)
SELECT s.calls, round((s.total_exec_time)::numeric,0) AS total_ms,
       round((s.mean_exec_time)::numeric,2) AS mean_ms,
       left(regexp_replace(s.query,'\s+',' ','g'),130) AS query
FROM extensions.pg_stat_statements s ORDER BY s.calls DESC LIMIT 15;

-- Ainda estoura o teto de 8s? (0 = sem statement timeout)
SELECT count(*) FILTER (WHERE max_exec_time >= 7900) AS queries_estouraram_8s,
       max(max_exec_time)::int AS pior_ms
FROM extensions.pg_stat_statements;

-- ---------------------------------------------------------------------
-- 2) Tabelas: seq scans, dead tuples, autovacuum
--    (tabela minúscula sempre faz seq scan — número gigante = VOLUME de chamadas)
-- ---------------------------------------------------------------------
SELECT relname AS tabela, n_live_tup AS vivas, n_dead_tup AS mortas,
       round(100*n_dead_tup::numeric/nullif(n_live_tup,0),0) AS dead_pct,
       seq_scan, seq_tup_read, idx_scan,
       last_autovacuum::timestamptz(0) AS last_vacuum,
       last_autoanalyze::timestamptz(0) AS last_analyze
FROM pg_stat_user_tables
ORDER BY seq_tup_read DESC NULLS LAST
LIMIT 25;

-- ---------------------------------------------------------------------
-- 3) Índices não usados / candidatos a drop (NÃO tocar schema auth)
-- ---------------------------------------------------------------------
SELECT s.relname AS tabela, s.indexrelname AS indice, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS tamanho
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE NOT i.indisunique AND NOT i.indisprimary
ORDER BY s.idx_scan ASC, pg_relation_size(s.indexrelid) DESC
LIMIT 30;

-- Todos os índices de uma tabela quente (achar duplicados/prefixos + o "keeper")
SELECT i.relname AS indice, pg_get_indexdef(i.oid) AS def, s.idx_scan
FROM pg_index x JOIN pg_class i ON i.oid=x.indexrelid
JOIN pg_class c ON c.oid=x.indrelid JOIN pg_namespace n ON n.oid=c.relnamespace
LEFT JOIN pg_stat_user_indexes s ON s.indexrelid=x.indexrelid
WHERE n.nspname='public' AND c.relname = 'messages'   -- <== troque a tabela
ORDER BY i.relname;

-- FKs sem índice de suporte (só vale indexar se a tabela for GRANDE)
SELECT c.conrelid::regclass AS tabela, a.attname AS coluna_fk
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=ANY(c.conkey)
WHERE c.contype='f' AND c.connamespace='public'::regnamespace
  AND NOT EXISTS (SELECT 1 FROM pg_index i WHERE i.indrelid=c.conrelid AND a.attnum=i.indkey[0])
ORDER BY 1,2;

-- Índices INVÁLIDOS (falha de CREATE ... CONCURRENTLY)
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;

-- ---------------------------------------------------------------------
-- 4) RLS: policies permissivas múltiplas (Postgres avalia TODAS por linha)
-- ---------------------------------------------------------------------
SELECT tablename, cmd, count(*) AS n_policies, string_agg(policyname,' | ') AS policies
FROM pg_policies
WHERE schemaname='public' AND permissive='PERMISSIVE'
GROUP BY tablename, cmd HAVING count(*) > 1
ORDER BY n_policies DESC, tablename LIMIT 40;

-- Policies com auth.<fn>() NÃO encapsulado em (SELECT ...) => reavaliado por linha
SELECT tablename, policyname, cmd
FROM pg_policies
WHERE schemaname='public'
  AND ( (qual ~ 'auth\.(uid|jwt|role)\(\)' AND qual !~ 'select\s+auth\.')
     OR (with_check ~ 'auth\.(uid|jwt|role)\(\)' AND with_check !~ 'select\s+auth\.') )
LIMIT 50;

-- ---------------------------------------------------------------------
-- 5) Realtime: escopo da publicação (tabelas de alta escrita aqui = wal2json caro)
-- ---------------------------------------------------------------------
SELECT p.pubname, string_agg(c.relname, ', ' ORDER BY c.relname) AS tabelas
FROM pg_publication p
LEFT JOIN pg_publication_rel pr ON pr.prpubid=p.oid
LEFT JOIN pg_class c ON c.oid=pr.prrelid
GROUP BY p.pubname;

-- REPLICA IDENTITY (FULL => eventos UPDATE trazem o registro antigo completo)
SELECT c.relname,
  CASE c.relreplident WHEN 'd' THEN 'default(pk)' WHEN 'f' THEN 'FULL'
       WHEN 'i' THEN 'index' WHEN 'n' THEN 'nothing' END AS replica_identity
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND c.relkind='r' AND c.relname IN ('messages','tickets','conversations');

-- ---------------------------------------------------------------------
-- 6) Funções/RPCs: corpo + overloads órfãos (multi-tenant: DROP o antigo!)
-- ---------------------------------------------------------------------
SELECT p.proname, pg_get_function_identity_arguments(p.oid) AS args,
       p.provolatile AS vol, CASE WHEN p.prosecdef THEN 'definer' ELSE 'invoker' END AS security
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE n.nspname='public' AND p.proname = 'get_chat_tab_counts'   -- <== troque a função
ORDER BY p.proname;
-- corpo: SELECT pg_get_functiondef('public.get_chat_tab_counts'::regproc);

-- EXPLAIN do corpo da RPC quente: reconstrua a query com literais reais e rode:
--   EXPLAIN (ANALYZE, BUFFERS) <corpo com valores literais>;
-- Compare nova vs antiga; valide EQUIVALÊNCIA por conjuntos antes de trocar:
--   (SELECT ... corpo_antigo) EXCEPT (SELECT ... corpo_novo)  -- deve dar 0
--   e o inverso também 0, em vários (org, usuário) reais.

-- ---------------------------------------------------------------------
-- 7) Utilitários de execução segura
-- ---------------------------------------------------------------------
-- Testar permissão de escrita do MCP (no-op; falha com 25006 se read-only):
--   CREATE TEMP TABLE _probe(n int); DROP TABLE _probe;

-- Testar se CONCURRENTLY é permitido no ambiente (no-op inofensivo):
--   DROP INDEX CONCURRENTLY IF EXISTS public.__probe_inexistente;

-- Índice parcial típico (filtro quente) — CONCURRENTLY, sem lock (psql/MCP autocommit):
--   CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_unread
--     ON public.messages (conversation_id) WHERE status <> 'read' AND type <> 'system';

-- Marco de medição: resetar e comparar em 24h (comparar MESMO horário do dia):
--   SELECT extensions.pg_stat_statements_reset();
