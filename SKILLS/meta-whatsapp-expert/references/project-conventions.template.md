# Convenções do Projeto — Meta WhatsApp  (TEMPLATE)

> Copie este template para `project-conventions.md` e preencha analisando o projeto atual. Regenere quando a skill for usada em outro repositório ou o schema mudar. Descubra os valores com buscas como:
> - `grep -rInoE "graph\.facebook\.com/v[0-9]+\.[0-9]+" <edge-functions-dir>`
> - `grep -rInoE "phone_number_id|value\.messages|expiration_timestamp|referral" <edge-functions-dir>`
> - inspecionar a tabela de mensagens/conversas (schema/migrations) para achar o campo de janela e a convenção de direção.

## Fingerprint do projeto
- Repositório / caminho raiz:
- Edge functions Meta encontradas (caminhos):
- Graph API version pinada:
- Data desta análise:

## Camada de dados
- Tabela de mensagens: `____` — colunas relevantes (`id`, conteúdo, tipo, status, external id, canal, timestamp): 
- Tabela de conversas/threads: `____`
- Tabela de tickets/atendimentos (se houver): `____`
- **Campo que representa a janela de atendimento:** `____` (tipo/coluna) + campo de tipo (24h/72h): `____`
- Outros campos Meta (referral/CTWA): `____`

## Convenção de direção (inbound vs outbound)
- Como o projeto marca uma mensagem do **cliente** (inbound): `____`  (ex.: `sender_id IS NULL`)
- Como marca mensagem do **agente/IA** (outbound): `____`
- Como marca mensagem de **sistema** (excluir de "última do cliente"): `____`  (ex.: `type = 'system'`)
- Filtro canônico de "última mensagem do cliente": `____`

## Fluxo do webhook
- Onde o inbound é inserido (arquivo:linha aprox.):
- Onde a janela é atualizada hoje (arquivo:linha aprox.):
- Idempotência: chave usada (`external_id` + `?`):
- Resolução de canal/organização: campo (`phone_number_id` →) e tabela:

## Envio / templates
- Edge function de envio: `____`
- Edge function de templates: `____`
- Particularidades (ex.: áudio via media_id, mapeamento de status):

## Realtime / performance
- A atualização de conversa dispara Realtime? Cuidados de CPU/re-render:
- Guardas de "só atualiza se mudou":

## Isolamento por organização
- Regra: todo write deve usar id resolvido (conversa/canal), nunca telefone/nome.
- Pontos onde já se verifica escopo por org:
