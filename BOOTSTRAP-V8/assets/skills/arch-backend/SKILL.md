---
name: arch-backend
description: "[ADAPTAR] Use ao implementar ou revisar qualquer coisa na camada de servidor de [PROJECT_NAME] — [liste as camadas reais: ex. Controller, Action, Service, Repository], endpoint, job, integração. Traz a ordem das camadas, o que cada uma pode fazer e o que é proibido."
---

<!--
TEMPLATE de skill de contexto. O bootstrap adapta ao projeto detectado.

REGRAS DE OURO ao gerar:
1. Esta skill REFERENCIA arch/, não copia. Se você colar aqui a lista de regras
   de rules.md, criou a duplicação que o V8 existe para matar.
2. A description é o gatilho — diga QUANDO usar, não o que contém.
3. Corpo curto. Se passou de ~40 linhas, você está copiando conteúdo de arch/.
4. Renomeie a skill para a camada real do projeto. Sem backend? não instale.
-->

# arch-backend

Fonte: **`.context/arch/overview.md`** (camadas) e **`.context/arch/rules.md`**
(regras numeradas). Leia-os quando precisar do detalhe.

## Ordem das camadas

```
[ORDEM_REAL_DAS_CAMADAS]
```

## O que cada camada pode

| Camada | Responsabilidade | Proibido |
|---|---|---|
| [camada] | [o que faz] | [o que nunca faz] |

## Ordem de implementação

[SEQUENCIA_CANONICA — ex: migration → model → repositório → serviço → caso de uso → controller → rota → testes]

Implementar fora de ordem gera retrabalho: a camada de baixo define a assinatura
que a de cima consome.

## Antes de criar arquivo novo

1. Abra o **arquivo de Referência** que a task indica e imite o padrão. Código novo não inventa um segundo jeito de fazer o que já existe.
2. Confira `.context/arch/modules.yaml` — o módulo desta task pode importar o que você está importando?
3. Respeite os **Imports autorizados** da task. O que não está lá é proibido.

## Regras aplicáveis

As de `.context/arch/rules.md` que o handoff citou por número. Se o handoff não
citou nenhuma e você está em dúvida, leia o arquivo — mas não presuma regra que
não está escrita.

## Testes

Comandos em `.context/arch/gates.md`. Você roda só os desta task.
[ESTRATEGIA_DE_TESTE_DO_PROJETO — ex: cobertura vem de teste unitário puro; teste
que precisa de banco usa transação, nunca recriação de schema]
