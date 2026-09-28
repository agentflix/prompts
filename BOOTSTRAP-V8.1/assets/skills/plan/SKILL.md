---
name: plan
description: Transforma um problema em plano executável — caça lacunas, declara o tamanho, decompõe em tasks T.A.C.E e pergunta se executa direto ou salva, e se roda o review do plano. Aceita também um plano já aprovado no modo plano da CLI. Triggers "planejar", "novo plano", "quero implementar X", "/plan". Do NOT use para implementar (use build) nem para revisar (use ship).
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

### 4. Executar direto e review — pergunte

Apresente o plano com o bloco `PLAN` de `.context/formats/response.md` e faça as
**duas perguntas** (com a ferramenta de pergunta da CLI, quando existir):

1. **Executar direto?** `executar` → o plano fica na conversa e o `/build` começa já
   pela primeira task · `salvar` → grave com `.context/work/_TEMPLATE.md` e pare.
2. **Revisar o plano antes?** `revisar` → passo 5 · `pular` → registre
   `Review do plano: ⏭️ pulado pelo usuário` e siga.

Recomende executar em XS/S/M e salvar em L; revisar em M/L e pular em XS/S. Recomendar
não é decidir: **nunca salve nem revise sem perguntar**. Se o usuário já respondeu na
mensagem ("executa direto", "sem review"), use a resposta e não pergunte de novo.

Com `executar` + `pular`, o próximo passo é o `/build` da primeira task, na mesma resposta.

### 5. Review do plano (só com `revisar`)

Despache o REVIEWER em modo PLANO. Roda depois das duas respostas e antes do primeiro `/build`.

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
