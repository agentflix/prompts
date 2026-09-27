# Template — 03-journeys/JRN-NN-<slug>.md

> **Gerado por `scripts/render_md.py`.** Este template mostra o formato de saída e de onde vem cada parte; o autor preenche o JSON (`module.json` / `journeys.json`), nunca o `.md`.

```markdown
# JRN-03 — Franqueado emite uma licença nova

**Ator**: franqueado · **Módulos**: pessoas, licenciamento, email
**Pré-condições** (obrigatório, `preconditions`): cliente cadastrado; franquia ativa

| # | Tela | O que o usuário faz | API | Regras | Resultado |
|---|---|---|---|---|---|
| 1 | SCR-PES-003 | busca o cliente por CNPJ | API-PES-002 | REQ-PES-E001 | lista de clientes |
| 2 | SCR-LIC-002 | preenche aplicativo e vencimento, clica Salvar | API-LIC-007 | REQ-LIC-W003, REQ-LIC-E012 | licença criada |
| 3 | — | (assíncrono) email enviado | — | REQ-LIC-E010 | email ao contato |

**Caminhos alternativos**: <erros e desvios, com IDs>
**Casos de paridade**: PAR-LIC-001
```

Mesmo conteúdo em `journeys.json` (schema `journeys.schema.json`). Todo passo tem `result`.
