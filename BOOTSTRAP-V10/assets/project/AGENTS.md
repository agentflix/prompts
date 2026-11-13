<!--
Molde do AGENTS.md (PREVEC V10). Este comentário não vai para o arquivo final.
Alvo: 40 a 60 linhas. É o único arquivo carregado em toda sessão por Claude Code, Codex e OpenCode.
Entra só o que o agente não descobre lendo o código. Sem árvore de pastas, sem descrição da stack
(arXiv 2602.11988: visão geral do repositório não ajuda e encarece). Sem CAPS: regra com motivo.
-->
# <Projeto>

<Uma linha: o que o sistema faz e para quem.> Idioma de código, mensagens ao usuário e commits: <pt-BR>.

## Tamanho decide o fluxo

Antes de agir, classifique o pedido. Diga o tamanho em uma linha só quando não for pontual.

- **Pontual** (1 a 3 arquivos, sem decisão de design, sem área de risco): faça direto, sem plano. Rode o teste afetado e entregue.
- **Médio** (vários arquivos, cabe nesta sessão, nada a decidir com o usuário, você mesmo executa): sem arquivo de plano. Liste os passos em uma linha cada, execute, teste afetado por passo, `GATE_FULL` no fim.
- **Grande** (decisão a aprovar, delegação a subagentes, várias sessões, módulo novo ou área de risco): skill `plano` (arquivo em `.context/planos/`), depois `executar`.

Com "spec" ou "testes primeiro" no pedido, o plano escreve os testes antes do código e os trava (skill `plano`).

Bug de causa desconhecida: junte evidência e teste a hipótese mais barata antes de editar. Corrija quando uma causa explicar tudo.
Investigação tem fim: quando já dá para decidir, decida. Não documente o que o `git log` e o código já contam.
Trabalho manual que você repetiu pela terceira vez (a mesma sequência de comandos, a mesma busca): proponha em uma linha um script ou alvo de Makefile que faça tudo, com o ganho. Crie só com aprovação. `/retro` faz a análise completa.

## Testes e verificação

Comandos em `.claude/hooks/gates.conf`.
- Por task ou fix: só o teste afetado (o campo **E** da task). No Claude Code e no Codex o hook roda o `GATE_FAST` no fim do turno.
- `GATE_FULL`: só no fim de cada fase e no `ship`, sempre pela fila: `.claude/hooks/tq.sh "<comando>"`. A fila deixa uma suíte por vez neste repositório. Passe `timeout: 600000` no Bash; se pode passar de 10 minutos, rode em background e espere a notificação.
- Antes de escrever teste, leia `.claude/rules/testes.md`. Teste existente que parece errado: pare e diga por quê, não edite para passar.

## Orquestração

A conversa principal decide e integra; ela fica pequena para durar a sessão inteira. Delegue quando o subagente custa menos do que fazer aqui:
- **Faça direto:** ajuste pontual, trabalho acoplado em que cada passo depende do anterior, ou quando passar o contexto custa mais que fazer.
- **Delegue:** leitura grande (`explorador`), task de plano com A, C e E fechados (`executor`), ajuste repetido com prova (`mecanico`), tasks `[P]` em paralelo, revisão (`revisor`).
- O pedido leva o contexto pronto: a task inteira, o Mapa do plano, `path:line` do que já foi lido e o comando de prova. O subagente executa sem levantar nada de novo. Formato na skill `delegar`.
- O modelo vem do agente (`explorador` e `mecanico` em Haiku, `executor` em Sonnet, `revisor` em Opus). Não troque `/model` no meio da sessão: o cache inteiro se perde.

Lacuna ou escolha que é do usuário: pergunte com a ferramenta de pergunta da CLI (`AskUserQuestion` no Claude Code), 2 a 4 opções, a recomendada primeiro.

Mudança em <migrations, contrato público da API, autenticação, pagamento> pede revisão independente antes do commit, em qualquer tamanho. Avise em uma linha.

<Seção ## Postura: cole aqui o bloco de assets/skills/postura/references/<postura>.md.>

## Não óbvio neste projeto

- <convenção fora do padrão ou armadilha real, com o motivo; apague se não existir>
- Regras por área em `.claude/rules/` (código, testes, API, dados, UI). O Claude Code carrega ao tocar a área. Nas outras ferramentas e antes de criar arquivo novo, leia a regra cujo `paths:` casa com o caminho.
- Decisões de arquitetura em `.context/decisions/`. Leia antes de mudar padrão.

## Entrega

- Termine com o que mudou, a evidência (comando e saída relevante) e o risco que sobrou. Seja conciso.
- Conventional Commits em <pt-BR>. Push e PR só com pedido explícito.
