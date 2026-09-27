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
| `PRC` | `PRC-<MOD>-NNN` | `PRC-DB-001` | procedure/trigger com lógica |
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

Toda referência precisa resolver para um ID existente (validado por `validate_ids.py`).

## Fonte (`source`)

```json
{"repo": "backend", "file": "apps/x/Arquivo.php", "line": 42, "end_line": 58}
```

`repo` é o nome registrado em `manifest.json.repos[]`. Para banco, use
`{"repo": "db", "object": "PROCEDURE CALC_COMISSAO", "line": 12}`. Para evidência de tela ou
rede, use `{"repo": "runtime", "capture": "05-parity/cases/PAR-LIC-001.json"}`.
