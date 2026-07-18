# Changelog — meta-whatsapp-expert

Formato: [semver da skill] — data. Registra tanto a evolução da skill quanto mudanças relevantes da Meta.

## [1.0.0] — 2026-07-07

Criação da skill. Graph API pinada em **v25.0**.

Conhecimento destilado de um bug real de produção (ticket ATD-038677):
- **Causa:** a janela de atendimento (`conversations.meta_window_expires_at`) só era escrita a partir do `conversation.expiration_timestamp` dos status de **saída**; mensagens **inbound** do cliente não renovavam a janela. Após a janela expirar, novas mensagens do cliente não a reabriam na UI → atendente travado.
- **Correção (3 camadas):** webhook renova a janela no inbound com `GREATEST` + guard anti-Realtime; frontend cai no fallback por mensagens quando o campo está no passado; backfill das conversas travadas.
- **Escala do incidente:** 26 conversas travadas em 3 organizações no momento do diagnóstico.

Princípios registrados no `SKILL.md` (1–9), com destaque para: renovar janela a cada inbound, nunca encurtar, fallback resiliente, idempotência, isolamento por org, não mascarar `failed`.

Gotcha aberto documentado em `project-conventions.md`: `statusMap` mapeia `failed → "sent"` (mascara falhas de entrega) — candidato a correção futura.

---

## Como registrar mudanças da Meta

Ao fazer upgrade da Graph API ou reagir a mudança anunciada pela Meta, adicione uma entrada com: data, versão antiga → nova, o que mudou (webhook/pricing/template/erros), risco e o que foi testado. Bumpe `metadata.version` e `metadata.graph_api_version` no `SKILL.md`. Siga `references/graph-api-version.md`.
