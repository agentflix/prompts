# Template — 02-modules/<mod>/README.md

> **Gerado por `scripts/render_md.py`.** Este template mostra o formato de saída e de onde vem cada parte; o autor preenche o JSON (`module.json` / `journeys.json`), nunca o `.md`.

```markdown
# Módulo <nome> (<CODE>)

Código descrito: `<caminho do módulo>` (commit `<sha>`). Status: <status>.

## Objetivo
<2–3 frases, linguagem de negócio>

## Entradas e saídas
| Tipo | Quantidade | Arquivo |
|---|---:|---|
| APIs | | apis.md |
| Regras | | rules.md |
| Fluxos | | flows.md |
| Telas | | screens/ |
| Tabelas | | data.md |
| Exclusões (morto/dormente) | | abaixo |

## Dependências
- Usa: <módulos, integrações>
- É usado por: <módulos, jobs>

## Exclusões
| Item do inventário | Status | Motivo | Evidência (comandos) |
|---|---|---|---|

## Pontos de atenção
- <quirks importantes, findings e unknowns que afetam o módulo>
```

## data.md

```markdown
# Dados — <módulo>

| Tabela | Acesso | Filtro de tenant | Onde | Observação |
|---|---|---|---|---|
| CLIENTES | RW | sim (`franquia_id`) | `backend:arquivo:linha` | |
```
Ausência de filtro de tenant em dado multi-tenant → `NFR-SEC-*` + `FND-*`.

## acceptance.feature (escrito à mão, não é gerado)

Um cenário Gherkin por requisito relevante, com o ID na tag:

```gherkin
@REQ-LIC-W003
Cenário: rejeitar vencimento no passado
  Dado uma franquia com licença ativa
  Quando o usuário informa vencimento "2020-01-01"
  Então a resposta é 422 com a mensagem "Data de vencimento inválida"
```
