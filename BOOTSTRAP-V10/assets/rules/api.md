---
paths:
  - "<ex.: src/api/**>"
  - "<ex.: supabase/functions/**>"
  - "<ex.: app/Http/**>"
---
<!--
Molde de .claude/rules/api.md. Instale só se o projeto expõe ou consome API.
Este comentário não vai para o arquivo final. Resolva cada <...> com o dado real
(arquivo:linha do padrão existente). Se o padrão ainda não existe, diga isso na regra.
-->
# API

- **A1** Toda resposta, de sucesso ou de erro, sai no envelope JSON único do projeto: <arquivo:linha do envelope | "ainda não existe: a primeira rota define por decisão registrada">. Erro nunca volta como HTTP 200 nem expõe stack ou SQL.
- **A2** Rota ou chamada que lê ou altera dado de usuário exige sessão e permissão no mesmo diff que cria a rota. Estado atual: <arquivo:linha do middleware/guard>.
- **A3** Listagem pagina no servidor e devolve total e página. O cliente nunca baixa tudo para filtrar.
- **A4** A tela recebe o que precisa no menor número de chamadas. Waterfall de requisições e N+1 são defeito.
- **A5** Entrada externa é validada na borda (<lib de schema do projeto>). Filtro vai por parâmetro ou binding, nunca concatenado em string.
- **A6** Rota de escrita, login e consumo de token têm limite de taxa e de tentativas: <onde está | pendente>.
- **A7** Mensagem de erro para o usuário sai em <idioma>, diz o que fazer e passa por <componente de notificação>. Detalhe técnico vai para o log, não para a tela.

Por que estas regras são escritas e não descobertas: são invariantes de todo endpoint, e o revisor não consegue inventá-las na hora do review.
