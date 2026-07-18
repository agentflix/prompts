# Convenções do Projeto — Meta WhatsApp  (Suportefy / suportefy-supabase)

> Arquivo específico deste repositório. Se a skill for usada em outro projeto, **regenere** a partir de `project-conventions.template.md`.

## Fingerprint do projeto
- Repositório / caminho raiz: `/Users/rafael.silva/Documents/suportefy-supabase`
- Edge functions Meta:
  - `supabase/functions/meta-whatsapp-webhook/index.ts` (recebimento)
  - `supabase/functions/meta-whatsapp-send/index.ts` (envio/mídia)
  - `supabase/functions/meta-whatsapp-templates/index.ts` (templates)
  - `supabase/functions/test-channel/index.ts` (teste de canal)
- Graph API version pinada: **v25.0** (nas 4 functions acima)
- Data desta análise: 2026-07-07

## Camada de dados
- Tabela de mensagens: `public.messages` — colunas relevantes: `id`, `conversation_id`, `content`, `type`, `status ('sent'|'delivered'|'read')`, `external_id`, `channel_id`, `sender_id`, `created_at`, `is_internal`, `reply_to_id`.
- Tabela de conversas: `public.conversations` — thread. Campos de janela adicionados em `supabase/migrations/20260630000000_conversations_meta_window_dynamic.sql`.
- Tabela de tickets/atendimentos: `public.tickets` (tem `protocol`, `status`, `last_message_at`, `organization_id`, `conversation_id`).
- **Campo que representa a janela:** `conversations.meta_window_expires_at timestamptz` + tipo `conversations.meta_window_type text CHECK IN ('24h','72h')`.
- Campos CTWA/referral: `conversations.meta_referral_source_id / _source_type / _headline / _ctwa_clid`.
- Timestamp de "última mensagem" (só ordenação/exibição, NÃO é a janela): `tickets.last_message_at` (trigger `update_ticket_last_message_at`, ignora tickets fechados).

## Convenção de direção (inbound vs outbound)
- **Não existe** coluna `direction`/`is_agent`/`from_me`. A direção é INFERIDA por `sender_id`:
  - Cliente (inbound): `sender_id IS NULL`
  - Agente/IA (outbound): `sender_id = <uuid do usuário>`
  - Sistema: `type = 'system'` (inserida com `sender_id NULL` e, no caso de template enviado, `channel_id NULL`).
- **Filtro canônico de "última mensagem do cliente":** `sender_id IS NULL AND type <> 'system' AND channel_id IS NOT NULL`.
  Documentado em `supabase/migrations/20260617120000_fix_unread_count_null_sender.sql`.

## Fluxo do webhook (`meta-whatsapp-webhook/index.ts`)
- Parsing: `entry[] → changes[]`, filtra `change.field === "messages"`; resolve canal por `value.metadata.phone_number_id` (`resolveChannel`).
- Loop de **status** (~linhas 146–202): atualiza `messages.status`; captura janela via `status.conversation.expiration_timestamp` + `origin.type === 'referral_conversion'` → grava `conversations.meta_window_*` (~linha 189).
- Loop de **mensagens inbound** (~linhas 205–808): idempotência por `external_id` + `channel_id` (~218); insert com `sender_id: null`, `channel_id: channel.id` (~619–637).
- **Renovação da janela no inbound (correção 2026-07-07):** após o insert de conteúdo (`type !== 'system'`), `meta_window_expires_at = GREATEST(atual, msg.timestamp + 24h)`, mantendo `'72h'` enquanto maior; guard "só atualiza se mudou"; `.eq('id', conversationId)`.

## Envio / templates
- Envio: `meta-whatsapp-send/index.ts` — `POST {GRAPH}/{phone_number_id}/messages`. Áudio via `media_id` (nota de voz nativa) — `uploadAudioToMeta`.
- Templates: `meta-whatsapp-templates/index.ts`.
- **Gotcha atual:** o loop de status mapeia `failed → "sent"` (`statusMap`, ~linha 156) — mascara falhas de entrega. Candidato a corrigir (tratar `failed` como estado próprio).

## Realtime / performance
- `UPDATE` em `conversations` dispara Realtime → `useConversations.onConversationUpdate` faz merge in-place com short-circuit por igualdade. Projeto sensível a CPU (ver memória do incidente de tuning). Sempre guardar "só atualiza se o valor mudou".

## Frontend da janela
- Hook: `src/features/channels/hooks/useMetaWindow.ts` — Branch 1 (campo absoluto Meta), Branch 2 (CTWA pendente), Branch 3 (fallback por mensagens, 24h − 60s).
- **Correção 2026-07-07:** Branch 1 passa a cair no cálculo por mensagens quando `meta_window_expires_at` está no passado; preenche `lastInboundAt`.
- Banner/seletor de template: `src/features/channels/components/MetaTemplatePicker.tsx`.
- RPCs projetam `meta_window_*`: `supabase/migrations/20260706130000_chat_rpc_project_meta_window.sql` (aplicada).

## Isolamento por organização
- Regra crítica recorrente do projeto. Todo write no webhook usa `conversationId`/`channel.id` já resolvidos — nunca telefone/nome. Cuidado com overloads órfãos de função Postgres em multi-tenant (ver memória `postgres-function-overload-org-leak`).
