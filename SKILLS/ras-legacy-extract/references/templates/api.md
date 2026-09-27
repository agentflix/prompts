# Template — apis.md (uma seção por API)

> **Gerado por `scripts/render_md.py`.** Este template mostra o formato de saída e de onde vem cada parte; o autor preenche o JSON (`module.json` / `journeys.json`), nunca o `.md`.

As tabelas **Parâmetros** e **Respostas** são obrigatórias em toda API e espelham
`params[]` e `responses[]` do `module.json`. Respostas incluem redirects (302 + destino) e
páginas renderizadas em caso de erro (200 + qual tela/mensagem). Sem parâmetros: escreva
"Sem parâmetros" e use `params: []`.

```markdown
## API-LIC-007 — Criar licença
`POST /licencas` · ✅ verified · Critic: approved

- **Fonte**: `backend:apps/licenciamento/control/LicencasResource.php:120-188`
- **Autenticação/permissão**: usuário logado + franquia vinculada (<mecanismo>)
- **Chamada por**: SCR-LIC-002 (botão "Salvar"), JRN-03 passo 4 — ou `no_screen_reason`

### Parâmetros
| Campo | Onde | Tipo | Obrigatório | Validação | Descrição |
|---|---|---|---|---|---|
| aplicativo_id | body | int | sim | existe e ativo | |

### Respostas
| Status | Quando | Corpo / destino | Mensagem literal | Regras |
|---|---|---|---|---|
| 201 | sucesso | `{id, ...}` | "Licença criada" | REQ-LIC-E012 |
| 422 | vencimento no passado | `{"erro": ...}` | "Data de vencimento inválida" | REQ-LIC-W003 |
| 302 | sessão expirada | `/login` | — | REQ-AUTH-W002 |

### Regras aplicadas
REQ-LIC-E012, REQ-LIC-W003, REQ-LIC-O001

### Side-effects
- grava: LICENCAS, LICENCAS_HIST
- enfileira: envio de email de boas-vindas
- chama: <integração externa> (síncrono/assíncrono, timeout, o que acontece se falhar)
```
