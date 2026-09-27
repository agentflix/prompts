# Convenção de IDs

IDs são estáveis: uma vez publicado, um ID não muda de significado nem é reaproveitado.
Item removido fica marcado como `removed`, não some.

`<MOD>` = sigla do módulo, 2 a 6 letras/dígitos maiúsculos, definida no `manifest.json`
(ex.: `LIC` para licenciamento). Numeração com 3 dígitos por tipo e módulo.

| Prefixo | Formato | Exemplo | Significado |
|---|---|---|---|
| `API` | `API-<MOD>-NNN` | `API-LIC-007` | endpoint / contrato de entrada |
| `REQ` | `REQ-<MOD>-<T>NNN` | `REQ-LIC-E012` | requisito EARS; `<T>` = tipo EARS |
| `FLW` | `FLW-<MOD>-NN` | `FLW-LIC-03` | fluxo de caso de uso |
| `SCR` | `SCR-<MOD>-NNN` | `SCR-LIC-001` | tela |
| `JRN` | `JRN-NN` | `JRN-04` | jornada ponta a ponta (cruza módulos) |
| `PRC` | `PRC-<MOD>-NNN` | `PRC-LIC-001` | procedure/trigger/view com lógica |
| `NFR` | `NFR-<AREA>-NNN` | `NFR-SEC-004` | requisito não funcional (`SEC`, `PERF`, `SRCH`, `AVL`) |
| `FND` | `FND-NNN` | `FND-031` | finding (bug suspeito, quirk, código morto) |
| `UNK` | `UNK-NNN` | `UNK-012` | pergunta aberta |
| `PAR` | `PAR-<MOD>-NNN` | `PAR-LIC-002` | caso de paridade |

Tipos EARS em `<T>`: `U` ubíquo, `E` evento, `W` indesejado (erro/validação), `S` estado,
`O` opcional (configuração/feature).

Regex usada pelo validador:

```
API|SCR|PAR : ^(API|SCR|PAR)-[A-Z0-9]{2,6}-\d{3}$
REQ         : ^REQ-[A-Z0-9]{2,6}-[UEWSO]\d{3}$
FLW         : ^FLW-[A-Z0-9]{2,6}-\d{2}$
PRC|NFR     : ^(PRC|NFR)-[A-Z0-9]{2,6}-\d{3}$
JRN         : ^JRN-\d{2}$
FND|UNK     : ^(FND|UNK)-\d{3}$
```

## Referências cruzadas

- API → requisitos que aplica (`requirements`).
- Tela → APIs que chama (`actions[].api`).
- Fluxo → APIs e requisitos envolvidos.
- Jornada → passos com `screen`, `api`, `requirements`.
- Finding/Unknown → IDs afetados.

Toda referência precisa resolver para um ID existente (validado por `validate_ids.py`),
seja num JSON, seja em qualquer `.md` da saída (exceto `verification-log.md`, que pode citar
IDs rejeitados, e `adapter/`).

## Onde cada ID é definido

| Prefixo | Definido em | Forma da definição |
|---|---|---|
| `API` `REQ` `FLW` `SCR` | `02-modules/<mod>/module.json` | objeto com `id` |
| `JRN` | `03-journeys/journeys.json` | objeto com `id` |
| `PAR` | `05-parity/cases/` | nome do arquivo `PAR-*.json` = `id` |
| `PRC` | `01-database/procedures/` | nome do arquivo `PRC-*.md` + linha **Objeto** com `<TIPO> <NOME>` em crase (ver `templates/procedure.md`) |
| `NFR` | `04-nfr/<arquivo da área>.md` | primeira coluna de uma linha de tabela (`NFR-SEC-001`) |
| `FND` | `findings.md` | primeira coluna de uma linha de tabela (`FND-001`) |
| `UNK` | `unknowns.md` | título `## UNK-001 — ...` |

Citar um ID em outro lugar (texto, tabela de "afeta") não o define.

## Chaves do inventário (`key`)

Chave natural, estável e única. Para objetos de banco é obrigatório o formato
`<tipo>:<NOME>` com `table`, `view`, `procedure`, `trigger` ou `sequence` (o validador
compara com o `db-metadata.json`). Para o resto, o adaptador escolhe e documenta no
`ADAPTER.md` (ex.: `GET /licencas/{id}`, `screen:/licencas/nova`, `job:portal_trabalhos`).

## Fonte (`source`)

```json
{"repo": "backend", "file": "apps/x/Arquivo.php", "line": 42, "end_line": 58}
```

`repo` é o nome registrado em `manifest.json.repos[]`. Para banco, use
`{"repo": "db", "object": "PROCEDURE CALC_COMISSAO", "line": 12}`. Para evidência de tela ou
rede, use `{"repo": "runtime", "capture": "05-parity/cases/PAR-LIC-001.json"}`.
