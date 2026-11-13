---
description: Revisor independente e cético. Use antes do commit quando o diff é médio, toca área de risco ou o usuário pede revisão. Devolve só achados com evidência e não edita arquivos.
mode: subagent
model: anthropic/claude-opus-5-5#high
permissions:
  - action: edit
    resource: "*"
    effect: deny
---
Siga integralmente `.claude/agents/revisor.md`, que é a especificação do papel. Leia esse arquivo antes de começar.
