# Versão da Graph API (pinada) e checklist de upgrade

A versão da Graph API é uma **dependência versionada**. Todas as edge functions Meta devem apontar para a **mesma** `vNN.0`. Misturar versões causa divergência silenciosa de payload.

## Versão em uso

- **Graph API: `v25.0`** (registrada em `SKILL.md` → `metadata.graph_api_version`).
- Constante típica no código: `const GRAPH_API = "https://graph.facebook.com/v25.0";`

> Ao regenerar `project-conventions.md`, confirme a versão real com:
> `grep -rInoE "graph\.facebook\.com/v[0-9]+\.[0-9]+" <dir-das-edge-functions>`

## Política

- A Meta lança uma versão nova a cada ~3 meses e deprecia versões após ~2 anos. Não deixe a versão vencer silenciosamente.
- Só faça upgrade deliberadamente, com o checklist abaixo, e registre em `CHANGELOG.md`.

## Checklist de upgrade de versão

1. Ler o **changelog oficial** da versão alvo (Graph API + WhatsApp Cloud API) e a lista de *breaking changes*.
2. Localizar **todas** as ocorrências de `graph.facebook.com/vNN.0` no repositório e atualizar juntas.
3. Revisar mudanças em: forma do webhook (`value.messages`/`statuses`/`conversation`), campos de janela/pricing, categorias de template, códigos de erro.
4. Testar em número/WABA de teste antes de produção (webhook de recebimento, envio de texto, template, mídia/áudio).
5. Atualizar `metadata.graph_api_version` no `SKILL.md` e a "Versão em uso" acima.
6. Registrar no `CHANGELOG.md` (data, versão antiga → nova, o que mudou, riscos).

## Sinais de que a versão precisa de atenção

- A Meta enviou aviso de deprecação no painel do app.
- Campos novos de webhook aparecendo (ex.: mudanças em `conversation`/pricing).
- Erros `100`/`400` novos após um período estável (possível mudança de contrato).
