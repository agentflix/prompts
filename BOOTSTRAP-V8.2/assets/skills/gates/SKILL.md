---
name: gates
description: Use antes de declarar qualquer coisa pronta, ou ao decidir qual comando de verificação rodar. Traz o escopo de verificação de cada papel e os critérios de falha deste projeto.
---

# gates

Fonte dos comandos: **`.context/arch/gates.md`** — leia esse arquivo. Esta skill diz
como usá-lo, e de propósito **não repete nenhum comando**: comando duplicado divergiu
do projeto em toda instalação que tentou.

## Escopo é assimétrico de propósito

| Quem | Roda | Por quê |
|---|---|---|
| BUILDER, por task | Só o comando **filtrado** da task, da seção `Filtrado por task` | Loop rápido; é o único gate dentro do loop |
| REVIEWER, no fim | O gate **completo**, da seção `Completo` | Único que vê o que a soma das tasks quebrou |

Não inverta. BUILDER rodando o gate completo a cada task é desperdício; REVIEWER
rodando só o filtro da task deixa passar regressão.

## Como escolher o comando

1. Se o projeto tem mais de um deployable, identifique **qual** foi tocado — cada um tem a sua seção em `gates.md`.
2. Por task: a seção `Filtrado por task`.
3. No fim: a seção `Completo`, e o que mais estiver marcado como obrigatório antes de merge naquele projeto.

O `gates.md` lista só o que existe de verdade. Seção marcada como inexistente
(build, cobertura, análise estática) significa que aquele passo **não se aplica** —
não invente um comando para preencher a lacuna.

## Regras

- **Evidência é output colado.** "Testes passaram" não é evidência.
- **Gate que não rodou entra no relatório** com motivo e risco residual. Nunca omita.
- **Teste pulado não é evidência.** Skip sem justificativa explícita é achado.
- **Nunca ajuste o teste para passar.** Se o teste está errado, isso é uma decisão — vai para o PLANNER.
- **Nunca burle o hook de commit.** Hook que falha aponta problema real.

## Critérios de falha

Em `.context/arch/gates.md`, seção final. Qualquer um deles reprova a feature e
devolve as tasks afetadas para o BUILDER.
