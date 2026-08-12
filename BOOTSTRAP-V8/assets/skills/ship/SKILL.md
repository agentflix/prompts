---
name: ship
description: Fecha a feature — despacha o REVIEWER com os 7 revisores sobre o diff acumulado, roda os gates completos, caça dano colateral, aplica o delta de arquitetura, commita e abre o PR. Roda só no fim, com todas as tasks 🟡, e é re-invocável a cada rodada de correção. Triggers "fechar feature", "revisar e commitar", "/ship". Do NOT use com task pendente nem para revisar task isolada.
---

# /ship — **V**alidation · **C**onfirm

## Iron Laws

**NÃO FECHE FEATURE INCOMPLETA.** Task ⬜ ou 🔄 → pare e liste o que falta.

**NÃO COMMITE COM GATE VERMELHO OU ACHADO BLOQUEANTE.** Nem com `--no-verify`.

**APLIQUE O DELTA DE ARQUITETURA ANTES DO COMMIT.** Sem isso `arch/` começa a
mentir — e mentira em `arch/` é pior que ausência, porque o agent confia.

## Input

```
/ship <feature>
/ship <feature> --no-commit    # revisa e para, para você inspecionar
```

## Fluxo

### 1. Porteiro

Todas as tasks 🟡? Plano salvo: `grep -nE "⬜|🔄" .context/work/<feature>.md`.
Plano na conversa: confira o estado de cada task despachada.

Alguma pendente → pare com a lista.

### 2. Escopo

As tasks estão no working tree sem commit — o commit é deste passo. Então o diff
não-commitado **é** o escopo:

```bash
git status --short && git diff --stat && git diff --name-only HEAD
```

### 3. Guardrail mecânico — antes dos revisores

Quatro checagens sem julgamento. São o que pega o dano que nenhum teste novo acusa:

| Checagem | Comando / método | Bloqueante quando |
|---|---|---|
| Mexeu onde não devia | Diff × união das seções **A** de todas as tasks | Existe arquivo fora da união |
| Apagou algo | `git diff --diff-filter=D --name-only HEAD` + blocos removidos no diff | Remoção que nenhuma task pediu |
| Quebrou fora da feature | Suíte completa + build de `.context/arch/gates.md` | Regressão em módulo não tocado de propósito |
| Quebrou contrato entre tasks | Para cada assinatura/tipo/envelope alterado, conferir quem consome | Task N quebrou o que a task M usa |

A última é a razão de o review ser no fim: nenhum review por task a enxerga.

### 4. Os 7 revisores

Despache o REVIEWER, que abre **7 subagents** conforme
`.claude/skills/code-review-confiavel/`. Nunca inline, nunca menos de 7.

Cada revisor recebe: o diff da feature, o T.A.C.E de todas as tasks, e as regras
aplicáveis de `.context/arch/rules.md` — citadas por número.

### 5. Gates completos

Todos os comandos de `.context/arch/gates.md`, para cada deployable tocado. Gate que
não pôde rodar entra no relatório com motivo e risco residual — nunca é omitido.

### 6. Decisão

**Bloqueante** → bloco `REPROVADO` de `.context/formats/response.md`, com a origem
de cada achado marcada (execução ou planejamento). Tasks afetadas voltam para 🔄.
Depois da correção, **rode `/ship` de novo sobre a feature inteira** — a correção
pode ter mexido em contrato que outra task consome.

**Limpo** → siga.

### 7. Aplicar o delta de arquitetura

Leia a seção `Delta de arquitetura` do plano e **aplique em `.context/arch/`**:

```
ADDED    → acrescente a regra/módulo/fluxo no arquivo certo
MODIFIED → edite a linha existente
REMOVED  → remova o que deixou de valer
```

Declarou `— nenhum`? Confirme lendo o diff: mudou camada, dependência entre módulos
ou regra sem declarar? Então o delta estava incompleto — corrija agora.

### 8. Fechar

1. Todas as tasks ✅ em bloco
2. Decisão arquitetural, se houve, em `.context/arch/decisions/`
3. **Um commit da feature**: `tipo(escopo): descrição imperativa` + corpo com uma linha por task. **Um por feature, sem exceção** — é o que sustenta a ausência de changelog (`git log` = histórico)
4. PR com resumo, tasks entregues, validação e como testar
5. Preencher a seção **Fecho** do work file (hash, PR, delta aplicado) — ela alimenta o corpo do PR — e **então** remover `.context/work/<feature>.md`. O commit e o PR contam a história; o que merecia sobreviver virou `decisions/` ou delta em `arch/`

Com `--no-commit`: pare depois do passo 7 e reporte.

## Output

Bloco `SHIP` de `.context/formats/response.md`, terminando em:

```
➡️ /plan <próximo problema>
```

## Error handling

- Task pendente → porteiro barra
- Diff vazio → nada foi implementado; não há o que fechar
- `gh` ausente → forneça o corpo do PR para o usuário abrir manualmente
- Hook de commit falhou → corrija o que ele apontou, nunca `--no-verify`
- Delta declarado mas o arquivo de `arch/` não tem a seção citada → o delta está errado; conserte antes de commitar
