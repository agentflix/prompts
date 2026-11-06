---
paths:
  - "<ex.: supabase/migrations/**>"
  - "<ex.: database/**>"
  - "<ex.: src/**/repositories/**>"
  - "<ex.: **/*.sql>"
---
<!--
Molde de .claude/rules/dados.md. Instale só se o projeto tem banco.
Este comentário não vai para o arquivo final.
D1 e D2 já são garantidas por máquina (guard.sh e deny de permissão); aqui ficam curtas.
-->
# Dados

- **D1** Banco muda só por migration nova e versionada. Migration já versionada não é editada: o hook `guard.sh` bloqueia, e a correção é outra migration.
- **D2** Sem SQL avulso por console ou CLI, nem "só para ver". O histórico do banco é o histórico das migrations. Reforço: deny de permissão para <psql | supabase db execute | mysql>.
- **D3** Antes de criar tabela, coluna ou índice, escreva no cabeçalho da migration a análise curta: normalização, PK e FK explícitas, índice para o filtro que a tela usa de verdade, e o que ficou redundante.
- **D4** Isolamento de dono: todo acesso filtra por <coluna de tenant/dono> dentro da query ou da <RPC/policy>, nunca depois do fetch. <arquivo:linha da policy existente>.
- **D5** Migration de mudança destrutiva (drop, rename, mudança de tipo) segue expandir, migrar, verificar e só depois contrair, em passos separados. O passo de contrair exige pedido explícito.
- **D6** Operação reprocessável (webhook, job, fila) é idempotente por <chave>. Reprocessar o mesmo evento não duplica efeito.
