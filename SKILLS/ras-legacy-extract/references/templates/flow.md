# Template — flows.md

```markdown
## FLW-LIC-02 — Renovar licença

**Gatilho**: usuário clica "Renovar" em SCR-LIC-004 (ou job X, ou webhook Y)
**APIs**: API-LIC-009 · **Regras**: REQ-LIC-S002, REQ-LIC-O001, REQ-LIC-E015

~~~mermaid
sequenceDiagram
  actor U as Usuário
  participant T as SCR-LIC-004
  participant A as API-LIC-009
  participant DB as Banco
  participant Q as Fila
  U->>T: clica "Renovar"
  T->>A: POST /licencas/{id}/renovar
  A->>DB: lê LICENCAS (filtro franquia_id)
  alt licença suspensa (REQ-LIC-S002)
    A-->>T: 409 "Licença suspensa"
  else saldo insuficiente (REQ-LIC-O001)
    A-->>T: 422 "Saldo insuficiente"
  else ok
    A->>DB: atualiza LICENCAS, insere LICENCAS_HIST
    Note over DB: trigger TRG_X recalcula vencimento (PRC-DB-004)
    A->>Q: enfileira email de renovação
    A-->>T: 200
  end
~~~

**Falhas e bordas**: <o que acontece se a fila estiver fora, se a integração falhar>
```

Inclua sempre: ramos de erro, triggers do banco, filas, integrações externas.
