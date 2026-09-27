# Template — screens/SCR-<MOD>-NNN.md

> **Gerado por `scripts/render_md.py`.** Este template mostra o formato de saída e de onde vem cada parte; o autor preenche o JSON (`module.json` / `journeys.json`), nunca o `.md`.

```markdown
# SCR-LIC-002 — Nova licença

- **Rota**: `/licencas/nova` · **Menu**: Licenças › Nova
- **Fonte**: `frontend:src/pages/licencas/Nova.tsx:1-240`
- **Perfis**: franqueado, matriz (matriz vê campo "Desconto")
- **Objetivo**: <1 frase — obrigatório (`purpose`)>
- **Screenshot**: ![](SCR-LIC-002.png)

## Campos
| Label | Nome | Tipo | Obrig. | Máscara/formato | Padrão | Opções (origem) | Validação no front | Campo na API |
|---|---|---|---|---|---|---|---|---|
| Aplicativo | aplicativo_id | select | sim | — | — | API-APP-001 | — | aplicativo_id |
| Vencimento | vencimento | data | sim | dd/mm/aaaa | hoje+30 | — | ≥ hoje | vencimento |

## Listas / tabelas (se houver)
| Coluna | Ordenável | Filtro | Observação |
|---|---|---|---|

## Ações
| Botão/link | Pré-condição | Chama | Resultado / mensagem (obrigatório) | Vai para |
|---|---|---|---|---|
| Salvar | formulário válido | API-LIC-007 | "Licença criada" | SCR-LIC-001 |
| Cancelar | — | — | — | SCR-LIC-001 |

Toda ação precisa de **Resultado**: o que o usuário vê depois — mensagem literal, tela
seguinte, download, modal que fecha, recarga da lista. "—" não é resultado.

## Observações
- Validações só no front (sem equivalente na API): <lista> → FND-*
- Divergências código × tela real: <lista> → FND-*
```
