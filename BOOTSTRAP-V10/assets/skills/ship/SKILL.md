---
name: ship
description: Valida e fecha uma mudança. Confere o diff contra o pedido ou o plano, roda o GATE_FULL pela fila (uma vez), aciona revisão proporcional ao risco, corrige regra ou decisão que o diff tornou falsa e commita. Use quando o usuário disser fechar, ship, finalizar, pode commitar, ou ao fim da skill executar.
---

# Ship

1. **Escopo.** `git status --short` e `git diff --stat HEAD`. Arquivo `??` é novo e não aparece no diff: leia inteiro. Com plano, compare com a união das seções A; arquivo fora sem motivo é achado. Remoção que ninguém pediu e teste existente modificado ou apagado são achados altos até serem explicados.
2. **Gate completo, uma vez.** Se a skill `executar` trouxe o `GATE_FULL` verde e nada mudou depois, use essa saída. Senão rode `.claude/hooks/tq.sh "<GATE_FULL>"` (`timeout: 600000` no Bash, ou background se pode passar de 10 minutos). Vermelho não commita.
3. **Revisão, pelo risco:**

   | Diff | Revisão |
   |---|---|
   | Pequeno, fora de área de risco | O gate basta |
   | Médio, ou toca área de risco do AGENTS.md | `revisor` contra o plano ou o pedido, com a saída do `GATE_FULL` no pedido para ele não rodar de novo. No Claude Code também serve `/code-review` |
   | Grande, fluxo crítico, ou pedido do usuário | Skill `code-review-confiavel`, se instalada; senão, `revisor` com pedido de revisão profunda |
   | Mudou interface | `/verify` ou Playwright, com screenshot |

   Achado bloqueante volta para correção; a revisão roda de novo só sobre o que mudou.
4. **Contexto em dia.** Se o diff tornou falsa alguma linha de `AGENTS.md`, `.claude/rules/` ou `.context/decisions/`, corrija no mesmo commit. Escolha nova com peso de arquitetura vira `.context/decisions/NNNN-slug.md`. Só isso: o resto o commit conta.
5. **Fechar.** Remova `.claude/hooks/tests.lock` e `.claude/hooks/gate.pause` se existirem. No plano, `status: entregue`, e mova-o de `.context/work/` para `.context/done/` com o mesmo nome e número (ou apague, se o usuário preferir). Commit em Conventional Commits, com corpo listando o que ficou pronto. PR só se o usuário pediu.

Resposta final, curta: o que foi entregue, gate (comando → resultado), achados da revisão e o hash.
