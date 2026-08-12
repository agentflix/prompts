# Passo 3 — Agents

São três papéis com duas representações nativas:

- `.claude/agents/*.md`: especificação canônica e completa do comportamento;
- `.codex/agents/*.toml`: identidade, modelo e instrução para carregar a especificação canônica.

Gere os Markdown sempre que Claude **ou** Codex foi selecionado, porque os TOML do
Codex apontam para eles e evitam duplicar prompts extensos. Molde em `assets/agents/`:
siga exatamente e substitua toda variável `[...]` por dado real do Passo 0.

| Agent | Modelo | Onde roda | Papel |
|---|---|---|---|
| `PLANNER.md` | `opus` | **Thread principal**, via `agent` no `settings.json`. Nunca spawnado como subagent | Recebe o problema, caça lacunas, decompõe em fases e tasks, monta o handoff, supervisiona |
| `BUILDER.md` | `sonnet` | Subagent, um por task | Executa a task já resolvida. Roda só os testes da feature |
| `REVIEWER.md` | `sonnet` | Subagent, duas vezes: no plano e no fim | Guardrail: reprova task fraca antes; caça dano colateral depois |

Quando Codex foi selecionado, gere também:

| Agent TOML | Modelo | Esforço | Papel |
|---|---|---|---|
| `planner.toml` | `gpt-5.6` | `high` | Planejamento profundo e coordenação |
| `builder.toml` | `gpt-5.6-terra` | `medium` | Execução delimitada, rápida e econômica |
| `reviewer.toml` | `gpt-5.6` | `high` | Revisão de contratos, risco e evidência |

```bash
mkdir -p .codex/agents
for f in planner builder reviewer; do
  cp "$B/assets/agents/codex/$f.toml" ".codex/agents/$f.toml"
done
# Substitua [PROJECT_NAME] nos três arquivos; não deixe placeholder.
```

## Alocação de modelo

No Claude, `opus` fica onde a decisão é o produto e `sonnet` executa ou verifica
contra critério explícito. No Codex, `gpt-5.6/high` cobre decisão e auditoria;
`gpt-5.6-terra/medium` reduz custo e latência da execução mecânica.

> No Claude, os 7 revisores do `code-review-confiavel` herdam o modelo do REVIEWER.
> No Codex, o default de subagent em `.codex/config.toml` é
> `gpt-5.6-terra/medium`; um spawn explícito ou um agent TOML pode sobrescrevê-lo.

**Preserve `model:` no Markdown e `model` + `model_reasoning_effort` nos TOML.**
Esses campos tornam a alocação explícita e verificável.

## O que NÃO vai para dentro do agent

| Conteúdo | Onde mora | O agent faz |
|---|---|---|
| Comandos de gate | `.context/arch/gates.md` | referencia o path |
| Regras invioláveis | `.context/arch/rules.md` | referencia, e o handoff cita as 2–4 que se aplicam à task |
| Dependência entre módulos | `.context/arch/modules.yaml` | referencia o path |
| Tabela de paths do contexto | `AGENTS.md` | nada — já está sempre carregado |

Agent que copia essas coisas cria a duplicação que este bootstrap existe para
matar. Se você se pegar escrevendo um comando de gate dentro de um agent, pare.

> **Regra específica que o dry-run expôs:** os agents falam do gate **pelo papel**,
> nunca pelo comando literal. Escreva "o gate completo", "o teste desta task" —
> jamais `make gate`, `pnpm gate`, `composer quality`. O comando literal vive em
> **dois** lugares e ponto: `arch/gates.md` (fonte) e a tabela de deployables do
> `AGENTS.md` (índice). É fácil violar isto sem perceber, porque nomear o comando
> numa proibição parece inofensivo — e é assim que ele acaba em 4 arquivos.

## Iron Law no topo

Cada agent abre com a sua regra não-negociável, redigida como **recusa** em maiúscula
— não como recomendação no meio do texto. É detalhe de engenharia de prompt que muda
comportamento:

- PLANNER: `NENHUMA TASK É DESPACHADA COM DECISÃO PENDENTE.`
- BUILDER: `NÃO TOQUE EM ARQUIVO FORA DA SEÇÃO A.` · `NÃO MARQUE ✅ E NÃO COMMITE.`
- REVIEWER: `NÃO REVISE FEATURE INCOMPLETA.` · `ACHADO SEM EVIDÊNCIA NÃO É ACHADO.`

## Adaptar ao projeto

O template traz a estrutura; o conteúdo específico vem da detecção:

- **PLANNER**: `[ORDEM_CANONICA]` (a sequência de camadas de cada deployable), `[CONTRATO_PUBLICO]` (o que é intocável — API, schema, protocolo), `[FLUXO_CRITICO]` (módulos onde erro custa caro)
- **BUILDER**: a tabela "Se algo não fecha" deve refletir as armadilhas reais detectadas no Passo 0
- **REVIEWER**: a lista de achados sempre bloqueantes vem de `rules.md` — mas **por referência numerada**, não copiada

## Verificar

```bash
for f in PLANNER BUILDER REVIEWER; do
  grep -q "^model:" ".claude/agents/$f.md" || echo "FALTA model: em $f"
done
grep -rlE '\[[A-Z_]{3,}\]' .claude/agents/ && echo "^^ variáveis não substituídas"

for f in planner builder reviewer; do
  test -f ".codex/agents/$f.toml" || echo "FALTA agent Codex: $f.toml"
done
python3 -c 'import pathlib,tomllib; [tomllib.loads(p.read_text()) for p in pathlib.Path(".codex").rglob("*.toml")]'
```

➡️ Próximo: `assets/setup/4-skills.md`
