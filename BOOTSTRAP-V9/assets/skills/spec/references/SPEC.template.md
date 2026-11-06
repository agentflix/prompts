---
feature: <nome-kebab>
status: rascunho | aprovada | em-implementacao | entregue
risco: baixo | medio | alto
---

# <Título>

## Objetivo
<Uma ou duas frases: o que passa a ser verdade para o usuário quando isto estiver pronto.>

## Contexto
<Dois a quatro fatos observáveis do estado atual. Sem solução embutida.>

## Critérios de aceite
Cada critério é verificável por comando, teste ou tela. EARS é opcional e ajuda em regra de negócio.

| # | Critério | Como provar |
|---|---|---|
| CA1 | <Quando X, o sistema faz Y> | `<comando de teste>` |
| CA2 | <Se erro Z, o sistema responde W> | `<comando>` |

## Não-objetivos
- <O que alguém razoavelmente esperaria que entrasse, e por que não entra.>

## Restrições e riscos
- <Contrato público, migration, dado de cliente, performance. Como reverter se der errado.>

## Decisões
- <Escolha e motivo em uma linha. Decisão com peso de arquitetura vira arquivo em .context/decisions/.>

## Plano
- [ ] <Passo que entrega algo verificável, com os arquivos principais>
- [ ] <Próximo passo>
