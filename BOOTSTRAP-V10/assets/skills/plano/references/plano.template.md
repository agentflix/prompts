---
feature: <nome-kebab>
status: rascunho | em-execucao | entregue
---

# <Título>

## Objetivo
<Uma ou duas frases: o que passa a ser verdade quando isto estiver pronto.>

## Decidido
Opcional.
- <escolha> — <motivo>. Inclua o que você assumiu por falta de resposta, marcado "(assumido)".

## Fora
Opcional.
- <o que alguém esperaria que entrasse, e por que não entra>

## Mapa
O que já foi lido, para nenhuma task precisar levantar de novo. Fato com `path:line`.
- <padrão de rota: `src/routes/cep.ts:12-48` valida com zod e responde envelope `{data, error}`>
- <comando de teste de um arquivo: `npx vitest run <arquivo>`>

## Pode dar errado
Várias sessões, módulo novo ou área de risco. Pre-mortem: imagine que a entrega falhou. Por quê?
- <risco> → <como o plano evita ou detecta>

## Fase 1 — <entrega que funciona sozinha>

### T1 — <verbo no imperativo + o quê> · depende: — · agente: executor · estado: ⬜
**A** `caminho/exato.ts` (novo) · `caminho/outro.ts` (editar: <o que muda>)
**Ref** `caminho/modelo.ts:10-40` (<o que imitar>)
**C**
- QUANDO <evento>, O SISTEMA DEVE <resposta observável>
- SE <erro>, ENTÃO O SISTEMA DEVE <resposta>
**E** `<comando que roda só o teste desta task>` → <resultado esperado>. Área de risco: + mutação (inverter `<arquivo:linha>` faz o teste falhar)
**Cuidado** <armadilha concreta, se houver; senão apague a linha>

### T2 — <...> · [P] · depende: T1 · agente: mecanico · estado: ⬜
**A** ...
**C** ...
**E** ...

Fim da fase: `GATE_FULL` pela fila (`.claude/hooks/tq.sh`).

## Pronto quando
- [ ] <critério da feature inteira, verificável por comando, rota ou tela>
