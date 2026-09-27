# Templates — 04-nfr/

Todo NFR é **medido ou citado**, nunca suposto. Cada item: ID `NFR-<AREA>-NNN`, fonte, data
da medição quando for runtime.

O ID é **definido** pela primeira coluna da tabela (`| NFR-SEC-001 | ...`), e cada área só
pode ser definida no seu arquivo: `SEC` → security.md, `PERF` → volumetry-performance.md,
`SRCH` → search.md, `AVL` → availability.md. O validador confere isso e rejeita qualquer
citação de NFR que não esteja definido.

## security.md (AREA = SEC)
| ID | Tema | Situação atual | Fonte | Risco | IDs afetados |
|---|---|---|---|---|---|
Cobrir: mecanismo de login e sessão; autorização por perfil; isolamento de tenant (listar
TODAS as queries sem filtro); tokens e expiração; armazenamento de senhas; dados sensíveis
em logs; segredos no código; validação de entrada; integrações e suas credenciais
(sempre `[REDACTED]`).

## volumetry-performance.md (AREA = PERF)
| ID | Tabela | Linhas | Medido em | Crescimento estimado | Consultas pesadas | Paginação |
|---|---|---:|---|---|---|---|
Mais: endpoints mais lentos ou mais pesados (se houver logs), jobs longos, relatórios.

## search.md (AREA = SRCH)
| ID | Pesquisa (tela/API) | Filtros | Query (fonte) | Índice usado | Observação |
|---|---|---|---|---|---|
Pesquisa sem índice que a suporte → NFR + finding.

## availability.md (AREA = AVL)
| ID | Componente | Tipo (fila/worker/cron/integração) | Retry | Timeout | Comportamento em falha | Fonte |
|---|---|---|---|---|---|---|
