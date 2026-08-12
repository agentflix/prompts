---
name: plan
description: Transforma um problema em plano executável — caça lacunas, declara o tamanho, decompõe em tasks T.A.C.E e pergunta se salva o plano ou segue direto para a implementação. Aceita também um plano já aprovado no modo plano da CLI. Triggers "planejar", "novo plano", "quero implementar X", "/plan". Do NOT use para implementar (use build) nem para revisar (use ship).
---

# /plan — **P**ré-Planning · **P**lanning · **R**eview do plano

## Iron Law

**NENHUMA TASK É GERADA ANTES DO CLARIFY.** Se você está decompondo sem ter listado
as lacunas e feito as perguntas, pare. Task com decisão pendente é a causa raiz de
modelo barato alucinando.

## Input

```
/plan <problema em texto>
/plan <feature>            # retomar um plano salvo
/plan                      # usar o plano aprovado no modo plano da CLI
```

## Fluxo

### 1. Clarify

Leia `.context/arch/rules.md` e `.context/arch/decisions/` — o tema já pode ter sido
decidido antes.

Produza o bloco `CLARIFY` de `.context/formats/response.md`: ambiguidades com
default proposto, decisões que você já tomou, riscos, e o que fica fora de escopo.

**Pergunte.** Só siga quando as lacunas estiverem fechadas ou o usuário disser
"assume os defaults".

> **Plano vindo do modo plano da CLI:** trate-o como entrada da seção Tasks e rode
> o clarify **sobre ele**. Plano aprovado não é plano completo — o modo plano da CLI
> não exige seção A com Referência, nem C em EARS, nem E com comando exato.

### 2. Tamanho

XS · S · M · L. A tabela de quais seções cada tamanho exige está em
`.context/formats/plan.md` — é a fonte única. Verifique a **trava do XS** declarada
no PLANNER: se toca contrato público, fluxo crítico, migration ou módulo novo, sobe.

### 3. Plano

Siga `.context/formats/plan.md`. A tabela de lá diz quais seções são obrigatórias
no tamanho declarado. Seção que não se aplica **não existe** — não fica com "N/A".

Para cada task, os quatro campos completos:

| Campo | Regra que o review aplica |
|---|---|
| **T** | Uma frase imperativa, uma coisa só |
| **A** | Lista específica + `Referência` + `Imports autorizados` |
| **C** | EARS, uma cláusula por comportamento, incluindo erro |
| **E** | Comando exato + resultado esperado |

Consulte `.context/arch/modules.yaml` antes de definir a seção A — task não pode
introduzir dependência proibida entre módulos.

### 4. Salvar ou seguir

Apresente o plano e pergunte, com o bloco `PLAN` de `.context/formats/response.md`:

```
Salvar este plano?
- `salvar` → .context/work/<feature>.md, rastro versionado
- `seguir` → implemento direto, plano só nesta conversa
```

Recomende `seguir` em XS/S e `salvar` em M/L — e ofereça as duas sempre.

`salvar` → grave usando `.context/work/_TEMPLATE.md`.
`seguir` → o plano fica na conversa; o despacho por task e o `/ship` funcionam igual.

### 5. Review do plano

Despache o REVIEWER em modo PLANO. Obrigatório de **M** para cima (é o limiar de `.context/formats/plan.md`, a fonte); recomendado em S; opcional em XS.

É a única checagem independente da decomposição — quem planejou não é bom juiz do
próprio plano. Reprovou: corrija **a task**, não o código.

## Output

Bloco `PLAN` de `.context/formats/response.md`, terminando em:

```
➡️ /build <feature>          # começar pela primeira task
```

## Error handling

- Pedido vago demais para decompor → fique no clarify, não gere task especulativa
- Feature já existe em `.context/work/` → pergunte se é continuação ou feature nova
- Decisão já registrada em `decisions/` contra a abordagem pedida → aponte a decisão e pergunte se é para revogá-la
- Módulo pedido violaria `modules.yaml` → reporte a regra e proponha alternativa
