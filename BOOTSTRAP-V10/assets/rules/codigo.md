---
paths:
  - "<ex.: src/**/*.ts>"
  - "<ex.: src/**/*.tsx>"
---
<!--
Molde de .claude/rules/codigo.md. Este comentário não vai para o arquivo final.
Carrega só quando o agente toca um arquivo que casa com `paths:`.
Cada regra é uma afirmação verificável, com o motivo e com o reforço.
Se o reforço puder ser máquina (lint, hook, teste), configure a máquina e encurte a regra.
IDs estáveis (C1, C2…): não renumere; regra removida deixa o ID vago.
-->
# Código

- **C1** Sem `any`, `as any`, `@ts-ignore` ou `@ts-expect-error` sem motivo escrito na mesma linha. Desconhecido é `unknown` e estreita. O `strict` não pega `any` explícito. Reforço: <lint `no-explicit-any` | revisão>.
- **C2** Sem comentário que repete o código. Documente só função cuja assinatura não explica o que faz. Comentário redundante envelhece e mente. Reforço: revisão.
- **C3** Código novo imita o padrão do vizinho mais próximo que já faz a mesma coisa. Dois jeitos de fazer o mesmo é dívida. Reforço: revisão.
- **C4** Padrão que nenhuma regra cobre vira decisão em `.context/decisions/` antes de virar código, para não nascer um padrão por sessão. Reforço: revisão.
