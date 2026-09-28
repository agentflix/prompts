# Gates do review

**Fonte única dos comandos: `.context/arch/gates.md`.** Leia esse arquivo — este
aqui só diz como usá-lo no review.

Não há comando de gate escrito nesta skill de propósito: comando duplicado divergiu
do projeto em toda instalação que tentou.

## Escopo alterado

```bash
git status --short && git diff --stat && git diff --name-only HEAD
```

As tasks da feature estão no working tree **sem commit** — o commit é do `/ship`.
Logo o diff não-commitado *é* o escopo do review.

## O que rodar

| Papel | Escopo | Onde está o comando |
|---|---|---|
| BUILDER, por task | Teste filtrado dos arquivos da task | `arch/gates.md` → "Filtrado por task" |
| REVIEWER, no fim | Completo: teste, lint, type-check, build, cobertura | `arch/gates.md` → "Completo" |

Rode o gate completo de **cada deployable tocado pelo diff** — não só o do último
arquivo que você olhou.

## Guardrail mecânico — antes dos revisores

Quatro checagens sem julgamento nenhum, que pegam o dano que nenhum teste novo acusa:

1. **Mexeu onde não devia** — diff × união das seções **A** de todas as tasks. Arquivo fora da união é bloqueante.
2. **Apagou algo** — `git diff --diff-filter=D --name-only HEAD` e os blocos removidos no diff. Remoção que nenhuma task pediu é bloqueante.
3. **Quebrou fora da feature** — suíte completa, não o filtro da task.
4. **Quebrou contrato entre tasks** — para cada assinatura, tipo ou envelope alterado por uma task, conferir as outras que consomem.

## Critérios de falha

Em `.context/arch/gates.md`, seção final. Qualquer um reprova a feature.

## Skills especialistas

O `SKILL.md` desta skill pode pedir para carregar uma skill especialista do
workspace. Neste projeto, os substitutos são:

| Referência genérica | Use |
|---|---|
| workflow / processo | `.claude/skills/ship/SKILL.md` |
| especialista da camada | a skill `arch-*` correspondente |
| regras do projeto | `.context/arch/rules.md`, citando por número |
