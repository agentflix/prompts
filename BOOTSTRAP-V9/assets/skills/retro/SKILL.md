---
name: retro
disable-model-invocation: true
description: Analisa como foi uma rodada de trabalho e sugere mudanças concretas para o fluxo ficar mais rápido e barato, a partir do registro do gate, do progresso e do git. Invocada pelo usuário com /retro, de preferência ao fim de uma feature longa.
---

# Retro

Sugestão vem de dado medido, não de opinião. Junte primeiro:

- `"$(git rev-parse --git-path prevec)/gate-log.tsv"`: data, segundos, código de saída e resultado (`verde`, `vermelho`, `timeout`, `liberado`) de cada gate.
- `features.json` e `progress.md` da feature, se existirem, e `git log --since="<início da rodada>" --stat`.
- Se o usuário colar o `/usage` ou o `/context`, use também: taxa de cache e o que ocupa o contexto.

Procure estes sinais e proponha a correção correspondente:

| Sinal | Sugestão |
|---|---|
| Gate rápido com média acima de 30s | Rodar só os afetados (`{changed}`) ou mover o teste lento para o `GATE_FULL` |
| Muitos `vermelho` seguidos no mesmo arquivo | Tarefa grande demais: quebrar em critérios menores |
| `liberado` ou `timeout` | Teste instável ou gate que não fecha: investigar antes da próxima rodada |
| Tarefas sem dependência entre si, feitas em sequência | Rodar em paralelo, com subagentes em worktree |
| Tarefas mecânicas (renomear, migrar padrão, gerar teste repetitivo) | Delegar ao `mecanico`, com prova automática no pedido |
| Cache baixo na statusline ou no `/usage` | Ver a causa (statusline mostra). Evitar trocar modelo, fast mode ou MCP no meio da rodada |
| Pausas maiores que 5 min com chave de API | `"promptCacheTtl": "1h"` no settings: escrever no cache custa 2x em vez de 1,25x, mas a pausa deixa de cobrar o contexto inteiro |
| Contexto alto no `/context` | `/compact` entre blocos de tarefas, ou mover leitura grande para subagente |
| Regra de `.claude/rules/` violada mais de uma vez | Transformar a regra em lint ou hook |
| Muitas escaladas para Opus no mesmo tipo de tarefa | Mudar o `model:` daquele agente, ou criar um agente próprio para esse tipo |
| Subagente que voltou `bloqueado` por falta de contexto | Pedido incompleto: acrescentar "Já sabemos" e escopo; ou usar fork |
| `explorador` trouxe achado errado mais de uma vez | Subir o effort dele para high antes de trocar de modelo |

Resposta: no máximo 5 sugestões, ordenadas pelo ganho estimado. Cada uma com o dado que a sustenta e a mudança exata (arquivo e linha, ou comando). Não aplique nada sem o usuário escolher. Use a ferramenta de pergunta da CLI com as sugestões como opções, em múltipla escolha.
