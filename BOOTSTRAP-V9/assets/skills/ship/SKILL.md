---
name: ship
description: Valida e fecha uma mudança. Roda o gate completo, confere o diff contra o pedido ou a SPEC, aciona revisão independente proporcional ao risco, atualiza regras e decisões que o diff tornou falsas e commita. Use quando o usuário disser fechar, ship, finalizar, pode commitar, ou ao fim do modo spec.
---

# Ship

1. **Escopo.** `git status --short` e `git diff --stat HEAD`. Arquivo `??` é novo e não aparece no diff: leia inteiro. Aponte arquivo que o pedido ou a SPEC não justificam, e remoção que ninguém pediu. Teste existente modificado ou apagado é achado alto até ser explicado.
2. **Gate completo.** Rode `GATE_FULL` de `.claude/hooks/gates.conf`. Vermelho não commita. Gate que não pôde rodar entra no relatório com o motivo.
3. **Revisão, pelo risco do diff:**

   | Diff | Revisão |
   |---|---|
   | Pequeno, fora de área de risco | O gate basta |
   | Médio, ou toca área de risco do AGENTS.md | Subagente `revisor` contra a SPEC ou o pedido, se instalado. No Claude Code também serve `/code-review` |
   | Grande, fluxo crítico, ou pedido do usuário | Skill `code-review-confiavel`, se instalada; senão, `revisor` com pedido de revisão profunda |
   | Mudou interface | `/verify` ou Playwright, com screenshot |

   Achado bloqueante volta para correção, e a revisão roda de novo sobre o diff inteiro.
4. **Contexto em dia.** Se o diff tornou falsa alguma linha de `AGENTS.md`, `.claude/rules/` ou `.context/decisions/`, corrija no mesmo commit. Escolha nova com peso de arquitetura vira decisão em `.context/decisions/NNNN-slug.md`, a partir do `_TEMPLATE.md`, com o próximo número da sequência. Documentação que mente é pior que ausência, porque o agente confia nela.
5. **Fechar.** Remova `.claude/hooks/tests.lock`, `.claude/hooks/gate.pause`, `progress.md` e `features.json` se existirem. Na SPEC, marque `status: entregue`. Commit em Conventional Commits, com corpo listando os critérios atendidos. PR (`gh pr create`) só se o usuário pediu.

Resposta final: o que foi entregue, a saída resumida dos gates, os achados da revisão e o hash do commit.
