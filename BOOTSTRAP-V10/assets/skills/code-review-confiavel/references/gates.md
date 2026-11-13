# Gates do review

Os comandos ficam em `.claude/hooks/gates.conf` (`GATE_FAST`, `GATE_FULL`). Esta skill não repete comando: comando duplicado diverge do projeto.

## Escopo alterado

```bash
git status --short && git diff HEAD --stat
```

Arquivo marcado `??` é novo e não aparece no `git diff`: leia inteiro. O escopo do review é o working tree contra `HEAD`, mais os arquivos novos.

## O que rodar

O `GATE_FULL` inteiro. Em monorepo ele encadeia os deployables; não rode só o do último arquivo olhado.

## Guardrail mecânico, antes dos revisores

1. **Mexeu onde não devia:** arquivo que o pedido ou a seção A do plano não justificam.
2. **Apagou algo:** `git diff --diff-filter=D --name-only HEAD` e os blocos removidos. Remoção que ninguém pediu é bloqueante.
3. **Enfraqueceu teste:** teste existente modificado ou apagado (padrões `TESTS` do `gates.conf`).
4. **Quebrou fora da feature:** a suíte completa, não só o teste da mudança.
5. **Quebrou contrato interno:** assinatura, tipo ou formato alterado e quem consome.

## Fontes do projeto

| Referência genérica | Use |
|---|---|
| workflow / processo | `.claude/skills/ship/SKILL.md` |
| regras do projeto | `.claude/rules/*.md` da área tocada, citando o ID (A2, D1…) |
| critério de aceite | **Pronto quando** e C de `.context/planos/NNNNN-<feature>.md`, ou o pedido original |
| decisões | `.context/decisions/` |
