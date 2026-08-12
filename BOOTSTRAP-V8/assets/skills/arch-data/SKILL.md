---
name: arch-data
description: "[ADAPTAR] Use ao criar ou alterar schema, migration, índice ou query pesada em [PROJECT_NAME]. Traz a convenção de migration, o isolamento de dados e a regra de teste com banco."
---

<!--
TEMPLATE. Adapte ou não instale se o projeto não tem banco.
Referencie arch/ — não copie. Corpo curto.
-->

# arch-data

Fonte: **`.context/arch/rules.md`** e **`.context/arch/overview.md`**.
Banco: [DATABASE].

## Onde a migration vai

[CONVENCAO_DE_LOCAL — ex: subpasta por schema, e como ela é descoberta pelo framework]

## Convenção obrigatória

[CONVENCOES_REAIS — ex: toda coluna declarada recebe comentário descritivo no
idioma do projeto; migration é reversível com up e down]

## Isolamento de dados

[REGRA_DE_ISOLAMENTO — ex: multi-tenant, dado de cliente vive na conexão resolvida
por X, nunca cruzar dados entre tenants]

Esta é a regra onde erro não aparece em teste e aparece em produção. Se a task não
diz como o dado é isolado, pergunte antes de implementar.

## Portar schema legado

Fidelidade ao schema, **mas** não replique artefato histórico sem consumidor no
código. Encontrou coluna que ninguém lê? Documente a simplificação no cabeçalho da
migration em vez de arrastar o problema.

## Teste com banco

[ESTRATEGIA_REAL — ex: cobertura vem de teste unitário puro com mock; teste que
precisa de banco usa transação por teste, nunca recriação de schema — que é lento e
gera lock]

## Query

Toda query mora na camada que `.context/arch/rules.md` define. Nenhuma camada acima
monta query direto — se a task pede isso, a task está errada.

Antes de otimizar: meça. Índice adicionado por intuição é dívida com custo de escrita.
