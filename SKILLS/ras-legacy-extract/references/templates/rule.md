# Template — rules.md

```markdown
# Regras — <módulo>

| ID | Tipo | Requisito | Fonte | Valores | Confiança | Critic |
|---|---|---|---|---|---|---|
| REQ-LIC-W003 | Indesejado | SE ..., ENTÃO o sistema DEVE ... | `backend:arq:88` | vencimento < hoje | ✅ | approved |

## REQ-LIC-W003 — Rejeitar vencimento no passado
**Requisito**: SE a data de vencimento for anterior à data atual, ENTÃO o sistema DEVE
rejeitar com HTTP 422 e a mensagem "Data de vencimento inválida".

**Fonte**: `backend:apps/.../LicencaValidator.php:88-93`

**Evidência** (trecho curto, sem segredos):
~~~
if ($vencimento < new DateTime()) { throw new ValidationException('Data de vencimento inválida'); }
~~~

**Valores concretos**: comparação estrita `<` com data e hora atuais do servidor.
**Confiança**: ✅ verified (código + PAR-LIC-003) · **Critic**: approved
**Findings**: FND-012 (usa hora do servidor, não fuso da franquia)
```

## Resumo de valores (fim do arquivo)

| Tipo | Valor | Fonte | Contexto |
|---|---|---|---|
| Limite / prazo / percentual | | | |
| Mensagem de erro | | | |
| Chave de config | | | |
