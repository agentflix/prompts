<!--
_TEMPLATE.md → copie para .context/arch/decisions/YYYY-MM-DD-<tema-kebab>.md

Este é o único artefato que guarda o que o git NÃO guarda: a alternativa descartada
e o porquê. O commit conta o que mudou; isto conta por que não foi de outro jeito.

QUANDO ESCREVER:
- Escolha técnica com alternativa real descartada
- Armadilha que já custou tempo e vai custar de novo se esquecida
- Regra nova ou revogada em arch/rules.md (obrigatório)

QUANDO NÃO ESCREVER:
- Decisão óbvia sem alternativa real
- O que o código já diz sozinho
- Decisão que vale só para esta feature (vai no plano, não aqui)

Uma decisão por arquivo. Decisão errada é DELETADA, não acumulada — contexto
obsoleto engana mais que contexto ausente.
-->

# [Título: a decisão, não o tema]

| Campo | Valor |
|---|---|
| **Tipo** | Decisão \| Aprendizado \| Armadilha |
| **Data** | [YYYY-MM-DD] |
| **Contexto** | [feature ou task que provocou] |
| **Regras afetadas** | [`rules.md` #N, ou —] |
| **Tags** | `[modulo:x]` `[camada:y]` `[tema:z]` |

## Situação

O que estava em jogo. Fatos: qual código, qual restrição, qual sintoma. Aponte
arquivo e linha quando existir. Sem narrativa.

## Decisão

O que ficou decidido, no imperativo e sem ambiguidade. Se passa a valer para casos
futuros, diga isso explicitamente — é a diferença entre uma nota e uma regra.

## Alternativas consideradas

| Alternativa | Por que foi descartada |
|---|---|
| [opção] | [motivo concreto — não "não gostei"] |

Sem alternativa real descartada, isto não é decisão: é anotação. Considere não
registrar.

## Consequências

- **Positivas:** [o que fica melhor]
- **Custo aceito:** [o que fica pior, e por que aceitamos]
- **Revisitar quando:** [condição concreta e observável — não "no futuro"]

## Referências

- `.context/arch/rules.md` #[N] — [regra criada ou alterada por esta decisão]
- [documento canônico do projeto, seção]
- Decisões relacionadas: `[YYYY-MM-DD-outro-tema.md]`
