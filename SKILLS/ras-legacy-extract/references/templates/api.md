# Template — apis.md (uma seção por API)

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
| Status | Quando | Corpo |
|---|---|---|
| 201 | sucesso | `{id, ...}` |
| 422 | vencimento no passado | `{"erro": "Data de vencimento inválida"}` |

### Regras aplicadas
REQ-LIC-E012, REQ-LIC-W003, REQ-LIC-O001

### Side-effects
- grava: LICENCAS, LICENCAS_HIST
- enfileira: envio de email de boas-vindas
- chama: <integração externa> (síncrono/assíncrono, timeout, o que acontece se falhar)
```
