# Templates dos arquivos da raiz de saída

## Estrutura completa

```
reverse/
├── README.md              # índice, como ler, legenda de confiança
├── manifest.json          # contrato: versão, repos + commits, módulos, status das fases
├── coverage.md            # gerado por validate_coverage.py --write (não editar à mão)
├── decisions-v2.md        # manter / reescrever / descartar — preenchido pelo usuário
├── findings.md            # FND-*: bugs suspeitos, quirks, código morto, divergências
├── unknowns.md            # UNK-*: perguntas abertas para quem conhece o negócio
├── glossary.md            # termos do negócio
├── adapter/               # ADAPTER.md + extratores (Fase 0)
├── 00-inventory/          # inventory.json + resumos .md por kind
├── 01-database/           # db-metadata.json, tables.md, volumetry.md, indexes.md,
│                          # triggers.md, sequences.md, views.md, procedures/PRC-<MOD>-NNN.md
├── 02-modules/<mod>/      # module.json, README.md, apis.md, rules.md, flows.md, data.md,
│                          # acceptance.feature, verification-log.md, screens/SCR-*.md|png
├── 03-journeys/           # journeys.json + JRN-NN-<slug>.md
├── 04-nfr/                # security.md, volumetry-performance.md, search.md, availability.md
└── 05-parity/             # README.md + cases/PAR-*.json
```

## manifest.json

```json
{
  "contract_version": "1.1.0",
  "system": "nome-do-sistema",
  "language": "pt-BR",
  "output_root": "docs/reverse",
  "has_frontend": true,
  "created_at": "2026-09-27",
  "updated_at": "2026-09-27",
  "environments": {"browser": "homolog|local|prod-readonly|none", "db": "local-readonly"},
  "approvals": {"adapter": {"by": "Nome de quem aprovou", "date": "2026-09-27"}},
  "repos": [
    {"name": "backend", "path": "../..", "commit": "55226983", "role": "api"},
    {"name": "frontend", "path": "/abs/path/front", "commit": "abc1234", "role": "ui"}
  ],
  "modules": [
    {"code": "LIC", "name": "licenciamento", "status": "pending", "depends_on": ["pessoas"]}
  ],
  "phases": {
    "0": {"status": "pending"}, "1": {"status": "pending"}, "2": {"status": "pending"},
    "3": {"status": "pending"}, "4": {"status": "pending"}, "5": {"status": "pending"},
    "6": {"status": "pending"}, "7": {"status": "pending"}, "8": {"status": "pending"}
  }
}
```

`repos[].path` relativo é resolvido a partir da raiz de saída (`reverse/`).
`approvals.adapter` só é preenchido depois que o usuário aprovar o `ADAPTER.md`; sem ele o
validador bloqueia as fases 1 a 8.

## README.md

```markdown
# Extração do legado — <sistema>

Commit(s) fixado(s): backend `<sha>`, frontend `<sha>`. Contrato `1.1.0`.

## Como ler
- Comece por `03-journeys/` (o que o usuário faz) e desça para telas, APIs e regras.
- `module.json` é a fonte da verdade; os `.md` são a leitura humana.
- Confiança: ✅ verified · 🟡 inferred · ❓ unknown (ver unknowns.md).

## Índice
| Módulo | Status | APIs | Regras | Telas | Link |
|---|---|---:|---:|---:|---|

## Números
Ver `coverage.md`. Findings abertos: N. Perguntas abertas: N.
```

## decisions-v2.md

```markdown
# Decisões para a versão nova

Legenda: manter (mesma regra) · reescrever (regra muda) · descartar (não vai para a v2).
Prioridade de paridade: alta | média | baixa.

## Por módulo
| Módulo | Decisão | Prioridade | Observação |
|---|---|---|---|
| licenciamento | | | |

## Por requisito (quando a decisão do módulo não basta)
| ID | Resumo | Decisão | Nova regra (se reescrever) |
|---|---|---|---|
```

## findings.md

```markdown
# Findings

| ID | Tipo | Descrição (1 linha) | Fonte | Afeta |
|---|---|---|---|---|
| FND-001 | bug-suspeito | Filtro de tenant ausente na listagem | backend:apps/x/Y.php:88 | API-LIC-004 |
```
O finding é definido pela linha da tabela que começa com `| FND-NNN |`.
Tipos: `bug-suspeito`, `quirk`, `codigo-morto`, `dormente`, `divergencia-tela`,
`validacao-so-front`, `nome-enganoso`, `seguranca`.

## unknowns.md

```markdown
# Perguntas abertas

## UNK-001 — <pergunta curta>
- **Contexto**: <1–2 frases>
- **O que o código faz**: <comportamento> (`backend:arquivo:linha`)
- **Dúvida**: <exata>
- **Opções**: a) ... b) ... c) outra
- **Afeta**: REQ-LIC-E004, SCR-LIC-002
- **Já verificado**: <buscas feitas antes de perguntar>
- **Resposta**: _(pendente)_
```
A pergunta é definida pelo título `## UNK-NNN`. O arquivo é obrigatório mesmo vazio ("nenhuma pergunta aberta" é uma afirmação).

## glossary.md

```markdown
| Termo | Significado no negócio | Nome no código/banco | Observação |
|---|---|---|---|
```

## 05-parity/cases/PAR-<MOD>-NNN.json

```json
{
  "id": "PAR-LIC-001",
  "api": "API-LIC-007",
  "requirements": ["REQ-LIC-E012", "REQ-LIC-W003"],
  "captured_at": "2026-09-27T14:00:00Z",
  "environment": "homolog",
  "preconditions": "franquia com licença ativa do aplicativo X",
  "request": {"method": "POST", "path": "/licencas", "body": {"...": "mascarado"}},
  "response": {"status": 201, "body": {"...": "mascarado"}},
  "notes": "campos voláteis ignorados na comparação: id, created_at"
}
```
