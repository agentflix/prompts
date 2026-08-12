<!--
_TEMPLATE.md → copie para .context/work/<feature>.md

Substitui, do V7: PRD + feature doc + arquivo de tasks + session file.
Só existe quando o plano foi SALVO — em XS/S o plano costuma ficar na conversa.

REGRAS:
1. As seções seguem .context/formats/plan.md. Aquele arquivo manda no formato;
   este é a versão com os campos de execução (log, review, delta aplicado).
2. Seção que não se aplica ao tamanho NÃO EXISTE — não fica com "N/A".
3. Estado da task: ⬜ pendente → 🔄 em execução → 🟡 implementada → ✅ concluída.
   BUILDER marca até 🟡. Só o /ship marca ✅, e marca todas em bloco.
4. O /ship preenche a seção Fecho (hash, PR, delta aplicado) e SÓ DEPOIS remove o
   arquivo — o Fecho existe para montar o corpo do PR, não para ficar em disco.
   O commit, o PR, o delta em arch/ e a decisão registrada são o que sobrevive.
-->

---
feature: [nome-kebab]
tamanho: [XS | S | M | L]
status: [planejando | em-execucao | em-review | ✅ concluida]
modulos: [modulo, modulo]
deployables: [nome, nome]
data: [YYYY-MM-DD]
---

# [Título da feature]

| Task | Deployable | Módulo | Camada | Depende de | Estado |
|---|---|---|---|---|---|
| TASK-1.1 | [qual] | [qual] | [qual] | — | ⬜ |

**Progresso:** ⬜ [N] · 🔄 [N] · 🟡 [N] · ✅ [N]
**Review do plano:** [⏳ pendente / ✅ aprovado / ❌ com ajustes]

---

## Problema

[2-4 fatos observáveis. Sem solução embutida.]

## Decisões e lacunas

**Decidido:** [escolha — motivo]
**Assumido:** [o que foi assumido por falta de resposta]

## Escopo

*(do tamanho S para cima)*

**Dentro:** [itens]
**Fora (explícito):** [item — por que não entra]

## Abordagem e alternativas

*(do tamanho M para cima)*

[Abordagem em prosa curta.]

| Alternativa | Trade-off | Por que não |
|---|---|---|

## Impacto

*(do tamanho S para cima)*

| Deployable | Módulo | Camadas | Contrato público muda? |
|---|---|---|---|

## Riscos

*(do tamanho M para cima)*

| Risco | O que quebra | Mitigação |
|---|---|---|

## Fases

*(só no tamanho L — cada fase entrega valor e passa nos gates sozinha)*

| Fase | Entrega | Tasks |
|---|---|---|

---

## TASK-1.1 — [título imperativo]
<!-- Formato T.A.C.E: Tarefa · Arquivo · Comportamento · Evidência.
     Os quatro campos existem em qualquer tamanho. Definição: .context/PREVEC.md -->

> Estado: ⬜ · Deployable: [qual] · Módulo: [qual] · Camada: [qual]

**T** — [uma frase imperativa, uma coisa só]

**A**
- `[path exato]` (novo)
- `[path exato]` (editar — [o que muda])

**Referência:** `[arquivo cujo padrão imitar]`
**Imports autorizados:** [lista] · **Proibido:** [lista]

**C** — EARS, uma cláusula por comportamento
```
WHEN [evento] THE SYSTEM SHALL [resposta]
IF [condição de erro] THEN THE SYSTEM SHALL [resposta]
```

**E**
```bash
$ [comando exato]
# esperado: [resultado literal]
```

**Idempotência** *(só em fluxo crítico)* — chave: `[campo]`; reprocessar deve [comportamento]

### Log do BUILDER
> Preenchido ao marcar 🟡.

**Arquivos:** `[path]` — [o que mudou]
**Decisões que fui obrigado a tomar:** [ou —]
**Teste:** `[comando]` → [resultado colado]
**Não coberto:** [ou —]
**Para o review:** [edge case, risco, dívida — ou —]

---

## Pronto quando

Critérios da **feature**, não a soma das tasks. É o que o `/ship` confere.

- [ ] [critério verificável]

## Delta de arquitetura

O que esta feature torna obsoleto em `.context/arch/`. O `/ship` **aplica** isto
antes de commitar. Nada mudou? escreva `— nenhum`.

```
ADDED    arch/rules.md #[N]: [regra nova]
MODIFIED arch/modules.yaml: [mudança]
REMOVED  arch/flows.md: [o que saiu]
```

---

## Review da feature
> Preenchido pelo REVIEWER no fim, sobre o diff acumulado. Rodada: [N]

**Resultado:** [aprovado / reprovado]
**Achados:** bloqueantes [N] · médios [N] · baixos [N]

**Guardrail mecânico**
- Escopo: diff dentro da união das seções A? [sim / os arquivos fora]
- Remoções não pedidas: [N / quais]
- Suíte completa: [resultado]
- Contrato entre tasks: [verificado, sem quebra / o que foi encontrado]

**7 revisores:** Especialização · Grounding · Second Pass · Precision · Human-in-the-Loop · Rastreabilidade · Meta-review

**Bloqueantes**
- [TASK-X.Y] `arquivo:linha` — [problema] · Correção: [o quê] · Origem: [execução | planejamento]

**Gates:** [deployable]: `[comando]` → [resultado]

## Fecho
> Preenchido pelo /ship.

- Tasks fechadas: [N] · Commit: [hash] · PR: [url]
- Delta aplicado: [sim / — nenhum]
- Decisão registrada: [arquivo em decisions/ ou —]
