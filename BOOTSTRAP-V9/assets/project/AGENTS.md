<!--
Molde do AGENTS.md. Este comentário não vai para o arquivo final.
Alvo: 40 a 60 linhas, com o bloco de postura e a orquestração. É o único arquivo carregado em toda sessão, por Claude Code,
Codex e OpenCode, então cada linha custa tokens em todo turno.
Entra só o que o agente não descobre lendo o código. Não descreva a arquitetura,
a árvore de pastas nem a stack: o modelo lê isso sozinho, e o estudo da ETH
(arXiv 2602.11988) mediu que visão geral do repositório não ajuda e encarece.
Sem CAPS, sem "IMPORTANT", sem "NUNCA": escreva a regra com o motivo.
-->
# <Projeto>

<Uma linha: o que o sistema faz e para quem.> Idioma de código, mensagens ao usuário e commits: <pt-BR>.

## Verificação

Os comandos ficam em `.claude/hooks/gates.conf` (`GATE_FAST`, `GATE_FULL`).
Rode o `GATE_FAST` antes de encerrar um turno com mudança. No Claude Code e no Codex um hook já faz isso; se ele falhar, corrija antes de encerrar.
Antes de qualquer commit, rode o `GATE_FULL`.

## Modo de trabalho

O padrão deste projeto é **<vibe | padrão | spec>**. O usuário troca o modo pedindo ("modo vibe", "faz com spec").

- **vibe**: faça direto, sem plano e sem arquivo de spec. Pare quando funcionar e o gate passar.
- **padrão**: planeje na conversa só quando a mudança tocar vários módulos ou houver ambiguidade real. Antes do commit de um diff médio ou maior, peça revisão ao subagente `revisor` (no Claude Code, `/code-review` também serve; no Codex, `/review`).
- **spec**: use a skill `spec` (entrevista, `SPEC.md`, testes primeiro, implementação, revisão contra a spec) e feche com a skill `ship`.

O modo decide a cerimônia (plano, spec, arquivos); a postura, abaixo, decide o risco (quando perguntar, dependência, ação irreversível). Se os dois conflitarem, a postura vale para risco e o modo vale para cerimônia.

Lacuna ou escolha que é do usuário: pergunte com a ferramenta de pergunta da CLI (no Claude Code, `AskUserQuestion`), com 2 a 4 opções e a recomendada primeiro. Pergunta em texto solto só quando a ferramenta não existir.

Mudança em <migrations, contrato público da API, autenticação, pagamento> pede revisão independente antes do commit, em qualquer modo, porque o erro ali chega ao cliente. Avise em uma linha quando isso acontecer.

<Seção ## Postura: cole aqui o bloco de assets/skills/postura/references/<postura>.md. Troca depois com /postura.>

## Orquestração

- Vale para a conversa principal; subagente segue o pedido e o próprio papel.
- Antes de abrir subagente, use a skill `delegar`: tarefa curta ou acoplada você faz direto.
- O modelo vem do agente (no Claude Code: `explorador` e `mecanico` em Haiku, `executor` em Sonnet, `revisor` em Opus). Escalada é por chamada, conforme a skill. Não troque `/model` no meio da sessão, porque o cache da conversa inteira se perde.
- Ajuste o effort antes de trocar de modelo.

## Não óbvio neste projeto

- <convenção fora do padrão ou armadilha real, com o motivo>
- <outra, se existir; apague a linha se não existir>
- Regras por área ficam em `.claude/rules/` (código, testes, API, dados, UI). O Claude Code carrega ao ler um arquivo da área. Antes de criar arquivo novo (migration, rota, tela) e nas outras ferramentas, leia a regra cujo `paths:` casa com o caminho.
- Decisões já tomadas ficam em `.context/decisions/NNNN-slug.md`. Leia antes de propor mudança de arquitetura ou de padrão.

## Entrega

- Termine com o que mudou, a evidência (o comando e a saída relevante) e o risco que sobrou. Seja conciso.
- Commits seguem Conventional Commits em <pt-BR>. Push e PR só com pedido explícito.
- Antes de escrever teste, leia `.claude/rules/testes.md`: teste só com motivo (critério, risco ou bug), na fronteira, com mock só no que é externo.
- Se um teste existente parecer errado, pare e diga por quê. Não edite o teste para passar.
