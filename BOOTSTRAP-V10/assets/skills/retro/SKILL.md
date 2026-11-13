---
name: retro
disable-model-invocation: true
description: Analisa como foi uma rodada de trabalho e sugere mudanças concretas para o fluxo ficar mais rápido e barato, a partir do registro do gate, do progresso e do git. Invocada pelo usuário com /retro, de preferência ao fim de uma feature longa.
---

# Retro

Sugestão vem de dado medido, não de opinião. Junte primeiro:

- `"$(git rev-parse --git-path prevec)/gate-log.tsv"`: data, segundos, código de saída e resultado (`verde`, `vermelho`, `timeout`, `liberado`) de cada gate.
- `"$(git rev-parse --git-path prevec)/cmds.tsv"`: data, sessão, agente e assinatura de cada comando de shell (caminhos, números e textos trocados por P, N, S). Conte as assinaturas repetidas.
- O plano da rodada (`.context/planos/`), a fila de testes (`.claude/hooks/tq.sh --status`) e `git log --since="<início da rodada>" --stat`.
- Se o usuário colar o `/usage` ou o `/context`, use também: taxa de cache e o que ocupa o contexto.

Procure estes sinais e proponha a correção correspondente:

| Sinal | Sugestão |
|---|---|
| Gate rápido com média acima de 30s | Rodar só os afetados (`{changed}`) ou mover o teste lento para o `GATE_FULL` |
| Muitos `vermelho` seguidos no mesmo arquivo | Task grande demais ou C mal definido: quebrar a task, melhorar o C |
| Task que voltou `bloqueado` ou foi refeita | Defeito de plano: qual campo faltou (A, Ref, C, Mapa). Reforçar esse campo no próximo plano |
| `GATE_FULL` rodado mais de uma vez por fase | Alguém rodou a suíte por task: mover para o fim da fase |
| `liberado` ou `timeout` | Teste instável ou gate que não fecha: investigar antes da próxima rodada |
| Tarefas sem dependência entre si, feitas em sequência | Rodar em paralelo, com subagentes em worktree |
| Tarefas mecânicas (renomear, migrar padrão, gerar teste repetitivo) | Delegar ao `mecanico`, com prova automática no pedido |
| Cache baixo na statusline ou no `/usage` | Ver a causa (statusline mostra). Evitar trocar modelo, fast mode ou MCP no meio da rodada |
| Pausas maiores que 5 min com chave de API | `"promptCacheTtl": "1h"` no settings: escrever no cache custa 2x em vez de 1,25x, mas a pausa deixa de cobrar o contexto inteiro |
| Contexto alto no `/context` | `/compact` entre blocos de tarefas, ou mover leitura grande para subagente |
| Regra de `.claude/rules/` violada mais de uma vez | Transformar a regra em lint ou hook. Hook não gasta token e não é ignorado; regra escrita é o último recurso |
| Mesma assinatura em `cmds.tsv` 3+ vezes em sessões diferentes, ou a mesma sequência de 3+ comandos repetida | Script em `scripts/agente/<nome>` (ou alvo no Makefile/package.json) que faz a sequência inteira; skill só se precisar de julgamento entre os passos. Cite a contagem |
| Skill ou regra do projeto sem uso nas últimas rodadas | Remover: cada descrição de skill custa tokens em toda sessão |
| Muitas escaladas para Opus no mesmo tipo de tarefa | Mudar o `model:` daquele agente, ou criar um agente próprio para esse tipo |
| Subagente que voltou `bloqueado` por falta de contexto | Pedido incompleto: acrescentar "Já sabemos" e o Mapa; ou usar fork |
| Muitos avisos de ritmo e pouca delegação | Turnos longos na conversa principal: delegar tasks de 3+ arquivos |
| `explorador` trouxe achado errado mais de uma vez | Subir o effort dele para high antes de trocar de modelo |

Nunca edite `AGENTS.md`, regra ou skill por conta própria: proponha a mudança exata e aplique só a escolhida. Regra reescrita inteira por modelo perde detalhe; mude só a linha.

Resposta: no máximo 5 sugestões, ordenadas pelo ganho estimado. Cada uma com o dado que a sustenta e a mudança exata (arquivo e linha, ou comando). Não aplique nada sem o usuário escolher. Use a ferramenta de pergunta da CLI com as sugestões como opções, em múltipla escolha.
