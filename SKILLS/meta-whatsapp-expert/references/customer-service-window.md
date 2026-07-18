# Janela de atendimento (Customer Service Window) — 24h / 72h CTWA

A "janela" é o intervalo em que você pode enviar mensagens de **texto livre** (não-template) para o cliente. Fora dela, a Meta rejeita texto livre; só um **template HSM aprovado** reabre a conversa.

## Regras oficiais da Meta

- **Janela de serviço de 24h:** toda mensagem **recebida do cliente** abre ou renova uma janela de 24h, contada a partir do horário daquela mensagem (`messages[].timestamp`, unix seconds). Enquanto houver janela aberta, o negócio responde livremente.
- **Janela CTWA de 72h:** conversas iniciadas por *Click-to-WhatsApp Ads* (lead de anúncio) ganham uma janela de entrada gratuita de **72h**. Na Cloud API isso aparece como `origin.type === 'referral_conversion'` no objeto `conversation` dos status, e a mensagem inbound traz `messages[].referral`.
- **`conversation.expiration_timestamp`:** a Meta envia esse campo (unix seconds) dentro de `value.statuses[].conversation` nos callbacks de **status de mensagens de saída**. É a expiração *absoluta* da janela corrente segundo a Meta. Útil, mas **insuficiente sozinho**: só chega quando você envia algo e recebe status de volta.

## A armadilha central (bug real de produção)

Se a janela persistida só for escrita a partir do `expiration_timestamp` dos **status de saída**, então:

1. A janela expira (ex.: 72h do lead acabaram).
2. O cliente manda uma nova mensagem → do lado da Meta, abre uma janela de 24h nova.
3. Mas o campo persistido continua no valor **velho e expirado**, porque nenhum status de saída novo chegou.
4. A UI lê o campo expirado, mostra "janela expirada" e **bloqueia o envio** — mesmo a janela estando aberta na Meta. Deadlock: o atendente não consegue responder.

**Correção:** renove a janela **no processamento do inbound** também — `janela = max(atual, timestamp_da_mensagem_inbound + 24h)`. Nunca encurte (`GREATEST`). Só faça `UPDATE` se o valor mudar (evita Realtime/CPU desnecessários). Mantenha o tipo `72h` enquanto a janela de 72h ainda for maior que a nova de 24h.

## Defesa em profundidade (3 camadas)

1. **Backend autoritativo:** o webhook renova a janela em toda inbound de conteúdo (não-sistema).
2. **Frontend resiliente:** se o campo absoluto estiver ausente ou no passado, a UI cai num cálculo por mensagens (última inbound + 24h) em vez de confiar cegamente no campo. `isOpen = (campo no futuro) OU (última inbound + 24h no futuro)`.
3. **Backfill:** ao introduzir a correção em produção viva, recalcule a janela das conversas já travadas (janela no passado, mas com inbound recente). Sempre dry-run + aprovação (`db-safety-guard`) antes do `UPDATE`.

## Troubleshooting: "janela não reabre / não consigo responder"

1. Localize o campo/coluna que representa a janela e o campo de tipo (24h/72h). Ver `project-conventions.md`.
2. Compare: valor persistido da janela **vs.** horário da última mensagem **inbound de conteúdo** do cliente (excluindo mensagens de sistema).
3. Se a última inbound é recente (< 24h) mas o campo está no passado → o inbound **não** está renovando a janela. É o bug acima.
4. Verifique se o handler de inbound faz a renovação; se só o handler de status escreve a janela, corrija.
5. Para desbloquear já: backfill das conversas com janela no passado + inbound nas últimas 24h.

## Notas

- Use sempre o `timestamp` da própria mensagem inbound como base (não o horário de processamento), com fallback para "agora" se ausente/inválido.
- Categorias de conversa e pricing da Meta mudam periodicamente — a *regra de janela* aqui é estável, mas confira o changelog da Meta em upgrades (`graph-api-version.md`).
