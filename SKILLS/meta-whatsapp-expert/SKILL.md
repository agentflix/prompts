---
name: meta-whatsapp-expert
description: Expert em implementação do WhatsApp via Meta Cloud API (Graph API). Use when trabalhando em código de webhook Meta (entry/changes/value.messages/value.statuses), envio de mensagens ou mídia via Cloud API, templates HSM, janela de atendimento 24h/72h (CTWA), verificação/assinatura de webhook, ou edge functions meta-* (meta-whatsapp-webhook, meta-whatsapp-send, meta-whatsapp-templates). Triggers/frases típicas — 'webhook meta', 'janela de 24h não reseta', 'expiration_timestamp', 'template aprovado', 'CTWA', 'meta-whatsapp-send'. Cobre a semântica oficial da Meta (renovação da janela a cada mensagem inbound, códigos de erro, versão da Graph API pinada) e carrega ou gera as convenções específicas do projeto. Do NOT use for provedores não-Meta (uazapi, zapi) nem para chat interno/UI de inbox sem relação com a API da Meta.
license: CC-BY-4.0
metadata:
  author: Rafael Silva
  version: 1.0.0
  graph_api_version: v25.0
---

# Meta WhatsApp Expert

Guia autoritativo para implementar, depurar e revisar integrações WhatsApp via **Meta Cloud API (Graph API)**: webhook de recebimento, envio, templates e a janela de atendimento (24h / 72h CTWA). Combina a semântica **oficial da Meta** (portável) com as **convenções do projeto atual** (arquivo separado, gerado sob demanda).

Esta skill deve ser consultada sempre que o trabalho tocar código Meta WhatsApp. Ela existe porque erros nessa integração são silenciosos e caros: janelas que não reabrem, mensagens perdidas, falhas mascaradas e vazamento entre organizações.

## Passo 0 — Carregar (ou gerar) as convenções do projeto

Antes de qualquer análise ou mudança, leia `references/project-conventions.md`.

- **Se existir:** valide que ele descreve o repositório atual (os caminhos e nomes de edge functions citados existem de fato — confirme com um `ls`/`grep` rápido). Se estiver desatualizado (a skill foi copiada para outro projeto, ou o schema mudou), **regenere-o**.
- **Se NÃO existir** (ou não bater com o projeto): pare e avise o usuário que vai gerá-lo. Analise o projeto atual — procure por `graph.facebook.com`, `phone_number_id`, `value.messages`, `expiration_timestamp`, a tabela de mensagens e o campo que representa a janela — e escreva `references/project-conventions.md` seguindo o template em `references/project-conventions.template.md`. Só então prossiga.

Isso mantém a skill portável: o conhecimento da Meta é genérico; o mapeamento para tabelas, campos e caminhos vive no arquivo de convenções, único por projeto.

## Passo 1 — Fixar a versão da Graph API

A versão da Graph API é **pinada** e tratada como dependência versionada. Antes de mudar endpoints ou payloads, leia `references/graph-api-version.md` para saber a versão em uso e o checklist de upgrade. Nunca misture versões entre edge functions — todas devem apontar para a mesma `vNN.0`.

## Princípios inegociáveis (as lições que custaram caro)

1. **A janela de atendimento renova a CADA mensagem inbound do cliente.** Regra oficial da Meta: toda mensagem recebida do cliente abre/renova uma janela de serviço de 24h a partir do horário daquela mensagem. Não dependa apenas do `conversation.expiration_timestamp` que chega nos *status de saída* — se você só atualizar a janela nos callbacks de status, uma janela expirada nunca reabre quando o cliente responde, e o atendente fica travado ("não conseguimos responder"). Sempre renove a janela no processamento do **inbound** também. *(Este foi um bug real de produção — ver `CHANGELOG.md`.)*

2. **Nunca encurte uma janela válida.** Ao renovar, use `GREATEST(valor_atual, novo)`. Uma janela CTWA de 72h ainda válida não pode ser rebaixada para 24h por uma nova mensagem. E só emita o `UPDATE` quando o valor **mudar** — escrita redundante dispara Realtime e custa CPU.

3. **Duas fontes de verdade devem convergir, com fallback resiliente.** Se a UI decide a janela por um campo absoluto persistido, ela deve cair num cálculo por mensagens quando esse campo estiver ausente ou no passado — nunca confiar cegamente num timestamp que pode estar velho. Backend autoritativo + fallback de frontend = defesa em profundidade.

4. **Idempotência é obrigatória.** A Meta reentrega webhooks. Deduplique por `external_id` (id da mensagem Meta) + identificador do canal, antes de inserir. Responda `200 OK` rápido; processe defensivamente (um erro num item não pode derrubar o lote nem provocar reentrega infinita).

5. **Isolamento por organização (multi-tenant).** Resolva o canal pelo `value.metadata.phone_number_id` → organização. Todo `UPDATE`/`INSERT` derivado deve usar o **id já resolvido** (conversa/canal), **nunca** filtrar por telefone ou nome do contato — isso vaza dados entre organizações. Confirme explicitamente o escopo por org antes de fechar qualquer mudança.

6. **Não confunda mensagem de sistema com mensagem do cliente.** A convenção de direção do projeto (ex.: quem é "inbound") está em `references/project-conventions.md`. Mensagens de sistema/automáticas costumam compartilhar o marcador de "inbound" mas ter `type = 'system'` — exclua-as de qualquer lógica de "última mensagem do cliente" (janela, unread, auto-reply).

7. **Não mascare falhas de entrega.** Se o status `failed` da Meta for mapeado para `sent`/`delivered`, o operador nunca vê a falha. Trate `failed` como estado próprio e registre o `errors[].code`/`title` da Meta. Ver a tabela de códigos em `references/sending-and-templates.md`.

8. **Produção viva.** Há usuários reais agora. Migration antes do código; para RPC/campo novo, fallback resiliente; preserve auth/sessão. Toda operação destrutiva de dados passa por dry-run + aprovação (skill `db-safety-guard`).

9. **Fora da janela, só template aprovado.** Quando a janela de 24h está fechada, a Meta rejeita mensagens de texto livre — só template HSM aprovado reabre a conversa. A UI deve refletir isso, mas a decisão real de "aberto/fechado" tem que espelhar a semântica da Meta (princípios 1–3), senão você bloqueia envio possível ou permite envio que a Meta vai rejeitar.

## Fluxos de uso

### Implementar/alterar o webhook de recebimento
1. Passo 0 + Passo 1. 2. Leia `references/webhook-payloads.md` para a forma de `entry → changes → value` (messages, statuses, contacts, referral/CTWA). 3. Garanta idempotência (princípio 4), renovação de janela no inbound (princípio 1) e escopo por org (princípio 5). 4. Verifique-se com o checklist em `references/webhook-payloads.md`.

### Enviar mensagem / mídia / template
Leia `references/sending-and-templates.md` (endpoints, `messaging_product`, voice note via `media_id`, categorias e componentes de template, códigos de erro). Respeite a janela (princípio 9).

### Depurar "janela não reabre" / "não consigo responder"
Este é o sintoma clássico do princípio 1. Roteiro em `references/customer-service-window.md` (seção Troubleshooting): confira o valor persistido da janela vs. a última mensagem inbound real do cliente, e se o inbound atualiza a janela.

### Revisar um PR que toca Meta
Rode os princípios 1–9 como checklist. Um achado só conta com evidência (linha/arquivo). Confirme isolamento por org e idempotência sempre.

## Versionamento da skill

- **Graph API pinada:** registrada no frontmatter (`metadata.graph_api_version`) e detalhada em `references/graph-api-version.md`.
- **Changelog interno:** toda mudança relevante da Meta (deprecação de versão, novo campo de webhook, mudança de regra de janela/pricing) e toda evolução da skill entram em `CHANGELOG.md`, com bump de `metadata.version` (semver).
- Quando a Meta anunciar mudança, siga o checklist de upgrade em `references/graph-api-version.md` e registre no changelog.

## Exemplos (Examples)

### Exemplo 1 — "A janela expirou mas o cliente respondeu hoje"
Usuário: "chamado aberto há 3 dias, cliente respondeu e a janela de 24h não resetou."
Ações: (1) Passo 0. (2) Consultar o campo de janela persistido vs. o horário da última mensagem inbound de conteúdo do cliente. (3) Verificar se o handler de **inbound** renova a janela — se só o handler de **status de saída** escreve a janela, esse é o bug (princípio 1). (4) Corrigir no inbound com `GREATEST` (princípio 2) + fallback de UI (princípio 3) + backfill dos travados (princípio 8).
Resultado: janela reabre a cada mensagem do cliente; UI destrava.

### Exemplo 2 — "Mensagens duplicadas no inbox"
Ações: verificar a dedupe por `external_id` + canal antes do insert (princípio 4). Meta reentrega em caso de timeout — confirmar que a função responde 200 rápido.

### Exemplo 3 — "Cliente não recebeu, mas o sistema diz 'enviado'"
Ações: procurar mapeamento `failed → sent` (princípio 7); tratar `failed` como estado próprio e logar `errors[].code`. Ver códigos em `references/sending-and-templates.md`.

## Troubleshooting

- **Janela nunca reabre:** princípio 1 — inbound não renova a janela. Ver `references/customer-service-window.md`.
- **72h virou 24h sozinha:** faltou `GREATEST` (princípio 2).
- **Enxurrada de webhooks repetidos / reentrega:** função não respondeu 200 ou lançou exceção no lote; e/ou falta idempotência (princípio 4).
- **Dado de outra organização aparecendo:** filtro por telefone/nome em vez de id resolvido (princípio 5).

## Arquivos de referência

- `references/project-conventions.md` — **específico do projeto** (gerado no Passo 0). Tabelas, campos, caminhos, convenção de direção.
- `references/project-conventions.template.md` — template para gerar o arquivo acima em qualquer projeto.
- `references/customer-service-window.md` — regras de janela 24h/72h CTWA + troubleshooting.
- `references/webhook-payloads.md` — forma dos payloads de webhook + checklist.
- `references/sending-and-templates.md` — envio, mídia, templates HSM, códigos de erro.
- `references/graph-api-version.md` — versão pinada da Graph API + checklist de upgrade.
- `CHANGELOG.md` — histórico da skill e das mudanças da Meta.
