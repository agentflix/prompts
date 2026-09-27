# Templates — 04-nfr/

Todo NFR é **medido ou citado**, nunca suposto. Cada item: ID `NFR-<AREA>-NNN`, fonte, data
da medição quando for runtime.

## security.md (AREA = SEC)
| ID | Tema | Situação atual | Fonte | Risco | IDs afetados |
|---|---|---|---|---|---|
Cobrir: mecanismo de login e sessão; autorização por perfil; isolamento de tenant (listar
TODAS as queries sem filtro); tokens e expiração; armazenamento de senhas; dados sensíveis
em logs; segredos no código; validação de entrada; integrações e suas credenciais
(sempre `[REDACTED]`).

## volumetry-performance.md (AREA = PERF)
| Tabela | Linhas | Medido em | Crescimento estimado | Consultas pesadas | Paginação |
|---|---:|---|---|---|---|
Mais: endpoints mais lentos ou mais pesados (se houver logs), jobs longos, relatórios.

## search.md (AREA = SRCH)
| Pesquisa (tela/API) | Filtros | Query (fonte) | Índice usado | Observação |
|---|---|---|---|---|
Pesquisa sem índice que a suporte → NFR + finding.

## availability.md (AREA = AVL)
| Componente | Tipo (fila/worker/cron/integração) | Retry | Timeout | Comportamento em falha | Fonte |
|---|---|---|---|---|---|
