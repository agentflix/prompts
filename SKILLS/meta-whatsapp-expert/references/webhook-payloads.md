# Payloads do Webhook (Meta Cloud API)

O webhook recebe um POST com a árvore `entry[] → changes[] → value`. Processe apenas `change.field === "messages"`.

## Estrutura de `value`

```jsonc
{
  "metadata": { "phone_number_id": "1234567890", "display_phone_number": "551199..." },
  "contacts": [ { "wa_id": "5511999999999", "profile": { "name": "Dani" } } ],
  "messages": [ /* mensagens recebidas do cliente (inbound) */ ],
  "statuses": [ /* status de mensagens que VOCÊ enviou (outbound) */ ]
}
```

- **`metadata.phone_number_id`** → resolve o canal e a organização (multi-tenant). Sem canal ativo, não há org/channel para gravar — apenas logue e siga (não derrube o lote).
- `messages` e `statuses` podem vir juntos ou separados. São **fluxos distintos** — trate em loops separados.

## Mensagens inbound (`value.messages[]`)

Campos comuns: `id` (external id, use para idempotência), `from` (telefone), `timestamp` (unix seconds), `type` (`text|image|audio|video|document|sticker|contacts|location|button|interactive|reaction|...`), e um objeto por tipo (`text.body`, `image.id`, etc.). Mídia vem como `id` → baixe via `GET {GRAPH}/{media_id}` e depois o binário.

- **`messages[].referral`** (CTWA): presente quando a conversa veio de um anúncio Click-to-WhatsApp. Traz `source_id`, `source_type`, `headline`, `ctwa_clid`. Marca janela de 72h.
- **`messages[].context`**: resposta/citação a outra mensagem (`context.id` = mensagem citada).
- **Reactions** (`type: "reaction"`) normalmente vão para uma tabela própria de reações, não para a de mensagens.

## Status outbound (`value.statuses[]`)

Campos: `id` (external id da mensagem enviada), `status` (`sent|delivered|read|failed`), `timestamp`, `recipient_id`, e:

- **`conversation.expiration_timestamp`** (unix seconds) + **`conversation.origin.type`** (`referral_conversion` = 72h CTWA; senão 24h). Capture aqui a janela absoluta da Meta.
- **`errors[]`** quando `status === "failed"`: `{ code, title, message, error_data.details }`. **Não** mapeie `failed` para `sent` — registre a falha e o código.

## Verificação de assinatura / handshake

- **GET (verificação):** a Meta chama com `hub.mode=subscribe`, `hub.verify_token`, `hub.challenge`. Responda o `hub.challenge` se o token bater.
- **POST (assinatura):** valide o header `X-Hub-Signature-256` (HMAC-SHA256 do corpo cru com o App Secret) quando aplicável.

## Checklist ao mexer no webhook

- [ ] Filtra `change.field === "messages"` e ignora o resto.
- [ ] Resolve canal/org por `phone_number_id`; ausência é logada, não quebra o lote.
- [ ] Idempotência por `external_id` + canal **antes** de inserir.
- [ ] Loops separados para `messages` e `statuses`.
- [ ] **Inbound de conteúdo renova a janela** (24h a partir de `timestamp`), com `GREATEST` e guard de "só se mudou". (Ver `customer-service-window.md`.)
- [ ] Mensagens de sistema/automáticas não contam como "mensagem do cliente".
- [ ] `failed` tratado como falha (não mascarado).
- [ ] Todo write usa id resolvido (conversa/canal), nunca telefone/nome (isolamento por org).
- [ ] Responde `200 OK` rápido; exceção em um item não aborta os demais nem provoca reentrega.
- [ ] Download de mídia trata erro de rede sem derrubar a mensagem.
