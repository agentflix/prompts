# Template — adapter/ADAPTER.md

```markdown
# Adaptador — <sistema>

Gerado na Fase 0 por ras-legacy-extract. Commit: backend `<sha>`, frontend `<sha>`.

## Stack detectada
| Camada | Tecnologia / versão | Evidência |
|---|---|---|
| Linguagem backend | | `arquivo:linha` |
| Framework HTTP e registro de rotas | | |
| Wiring / DI (prova de "vivo") | | |
| Acesso a dados / ORM | | |
| Banco e como ler metadados | | |
| Frontend: framework, roteador, formulários, cliente HTTP | | |
| Fila / agendador | | |

## Superfícies
| kind | Existe? | Extrator | Contagem de controle (comando) | Itens | Controle | Status |
|---|---|---|---|---:|---:|---|
| http_endpoint | sim | extract_inventory.py:routes() | `grep -c ... config/routes.php` | | | |
| db_trigger | sim | db_metadata.sql | `SELECT COUNT(*) FROM ...` | | | |
| webhook | não | — | `grep -rn "callback\|webhook" apps/` → 0 | 0 | 0 | não existe |

## Atribuição a módulos
Regra usada para decidir o `module` de cada item (ex.: pasta, prefixo de rota, tabela dona).

## Como rodar
~~~bash
python3 adapter/extract_inventory.py > 00-inventory/inventory.json
~~~

## Limitações conhecidas
- <o que o extrator não consegue ver e como isso é compensado>
```
