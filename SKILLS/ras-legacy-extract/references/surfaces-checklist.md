# Checklist de superfícies (qualquer stack)

Toda superfície abaixo precisa aparecer no `ADAPTER.md` com **um extrator** ou com
**"não existe neste sistema" + a busca que prova**. Superfície esquecida aqui é superfície
esquecida na migração.

O campo `kind` é o valor usado em `inventory.json`.

## Entradas (quem chama o sistema)

| kind | O que procurar | Pistas comuns |
|---|---|---|
| `http_endpoint` | Rotas HTTP/REST/GraphQL/SOAP/RPC | arquivo de rotas, anotações/decorators, controllers, router |
| `webhook` | Endpoints chamados por sistemas externos | rotas com token fixo, "callback", "notify", "hook" |
| `cli_command` | Comandos de terminal | scripts, entrypoints, `bin/`, console commands |
| `scheduled_job` | Rotinas agendadas | crontab, scheduler, supervisor, CI agendado |
| `queue_consumer` | Consumidores de fila/eventos | workers, subscribers, listeners, jobs |
| `screen` | Telas/páginas do frontend | router do front, pastas pages/views, menus |

## Lógica e dados

| kind | O que procurar |
|---|---|
| `db_table` | Tabelas (do banco, não só das classes ORM) |
| `db_view` | Views |
| `db_procedure` | Stored procedures / functions / packages |
| `db_trigger` | Triggers (lógica invisível para quem lê só o código da aplicação) |
| `db_sequence` | Sequences / generators / auto-increment |
| `db_constraint` | Checks e FKs com regra de negócio (ex.: `CHECK (valor > 0)`) |
| `inline_sql` | SQL escrito direto no código (fora do ORM) |
| `business_constant` | Enums, status, tabelas de domínio, constantes de regra (percentuais, prazos) |

## Saídas (quem o sistema chama)

| kind | O que procurar |
|---|---|
| `integration` | Clientes HTTP/SDK para sistemas externos (direção, protocolo, autenticação) |
| `outbound_email` | Envio de email / SMS / WhatsApp / push, com templates |
| `file_io` | Leitura/escrita de arquivos, uploads, geração de PDF/planilha, storage |
| `queue_producer` | Publicação em fila/tópico |

## Configuração e operação

| kind | O que procurar |
|---|---|
| `config_key` | Toda chave de config / variável de ambiente lida pelo código |
| `feature_flag` | Flags que ligam/desligam comportamento |
| `auth_mechanism` | Login, sessão, tokens, perfis, permissões, middlewares/guards/traits |
| `log_audit` | Logs de auditoria com valor de negócio (quem fez o quê) |

## Superfícies fáceis de esquecer

- Lógica em **trigger** ou **procedure** do banco.
- **Jobs** que rodam fora do fluxo HTTP (cron, fila) e alteram dados.
- **Webhooks** de entrada de parceiros.
- **Relatórios** e exportações (a regra de cálculo costuma estar só ali).
- **Validação só no frontend** (sem equivalente no backend).
- **Templates de email/PDF** com regra embutida (condicionais, cálculos).
- **Scripts de manutenção** usados manualmente pela equipe.
- **Configuração por tenant/cliente** que muda comportamento.
- Código **dormente**: registrado mas desligado por flag/config.

## Contagem de controle

Para cada `kind` presente, o adaptador define uma contagem independente do extrator
(normalmente um `grep`/`find`/consulta bruta) e registra o comando em
`inventory.json.control_counts`. O objetivo é pegar extrator que "pulou" itens.
