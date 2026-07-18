# Envio, Mídia e Templates (Meta Cloud API)

Base: `https://graph.facebook.com/vNN.0` (versão pinada — ver `graph-api-version.md`). Autenticação: `Authorization: Bearer <access_token>`. Todo corpo de envio inclui `"messaging_product": "whatsapp"`.

## Enviar mensagem

`POST {GRAPH}/{phone_number_id}/messages`

```jsonc
// Texto (só dentro da janela de 24h aberta)
{ "messaging_product": "whatsapp", "to": "5511999999999", "type": "text", "text": { "body": "..." } }
```

- **Fora da janela**, texto livre é rejeitado — use `type: "template"`.
- A resposta traz `messages[0].id` → guarde como `external_id` para casar com os status de entrega.

## Mídia

- **Enviar por `media_id` (recomendado para áudio):** primeiro `POST {GRAPH}/{phone_number_id}/media` (multipart: `messaging_product`, `file`, `type`) → recebe `id` → envie `{"type":"audio","audio":{"id": media_id}}`. Enviar áudio por `media_id` faz o WhatsApp exibir como **nota de voz nativa**; por `link`, vira anexo de arquivo.
- **Baixar mídia inbound:** `GET {GRAPH}/{media_id}` retorna uma URL temporária → baixe o binário com o mesmo Bearer.

## Templates (HSM)

- Listagem/criação: `GET|POST {GRAPH}/{waba_id}/message_templates`.
- Categorias: `MARKETING`, `UTILITY`, `AUTHENTICATION` (afeta pricing e aprovação).
- Componentes: `header` (text/image/video/document), `body` (com `{{1}}` variáveis), `footer`, `buttons` (quick reply / URL / phone).
- Enviar: `type: "template"`, com `template.name`, `template.language.code` e `components[]` preenchendo as variáveis na ordem.
- Só templates **APROVADOS** podem ser enviados. Template é a única forma de reabrir conversa com janela fechada.

## Códigos de erro comuns (`errors[].code`)

| Código | Significado | Ação |
|---|---|---|
| 131047 | Re-engagement: fora da janela de 24h | Enviar template aprovado |
| 131026 | Mensagem não entregue (destinatário não pode receber) | Verificar número/opt-in |
| 131051 | Tipo de mensagem não suportado | Revisar payload |
| 132xxx | Erros de template (não existe, não aprovado, params errados) | Revisar nome/idioma/componentes |
| 190 | Access token expirado/inválido | Renovar token |
| 100 | Parâmetro inválido | Revisar corpo da requisição |
| 80007 / 130429 | Rate limit | Backoff e reenvio |

Sempre logue `code`, `title` e `error_data.details`. **Nunca** transforme `failed` em `sent`/`delivered` — isso esconde a falha do operador.

## Boas práticas

- Trate erro HTTP e `errors[]` do corpo separadamente (a Meta pode retornar 200 com erro no corpo).
- Idempotência no envio: evite reenviar em retry cego; case pela resposta `messages[0].id`.
- Respeite rate limits por número; implemente backoff exponencial em 429.
