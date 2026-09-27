# Template — 01-database/procedures/PRC-<MOD>-NNN.md

Um arquivo por procedure, trigger, view ou function **que tenha lógica de negócio**. O nome
do arquivo é o ID. A linha `**Objeto**` é obrigatória: o validador confere se o objeto
existe no `db-metadata.json`.

Os requisitos EARS do objeto ficam no `module.json` do módulo dono (com fonte
`{"repo": "db", "object": "<TIPO> <NOME>", "line": N}`); este arquivo descreve o objeto e
lista esses requisitos.

```markdown
# PRC-LIC-001 — Recalcular vencimento ao renovar

**Objeto**: `TRIGGER TRG_LICENCAS_BU`
**Tipo**: trigger BEFORE UPDATE em `LICENCAS` · posição 0 · ativo
**Módulo dono**: licenciamento
**Chamado por**: toda atualização em LICENCAS (API-LIC-009, job X)

## O que faz
<2–4 frases de comportamento, sem transcrever o código>

## Requisitos
REQ-LIC-S004, REQ-LIC-E021

## Efeitos
- lê: <tabelas>
- grava: <tabelas>
- exceções que lança: <nome e mensagem literal>

## Pontos de atenção
- <quirks, dependência de ordem de triggers, FND-*>
```
