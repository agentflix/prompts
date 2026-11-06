# Trabalho que passa de uma sessão

Padrão do artigo da Anthropic "Effective harnesses for long-running agents" (2025-11-26). O estado mora em arquivo e no git, não na conversa.

## Na primeira sessão

1. Crie `.context/specs/<feature>/features.json` com um item por critério de aceite, todos com `"passa": false`:

```json
[
  { "id": "CA1", "criterio": "<texto do critério>", "prova": "<comando>", "passa": false }
]
```

JSON e não Markdown, porque o modelo corrompe menos a estrutura ao editar.

2. Crie `.context/specs/<feature>/progress.md`, curto:

```
## <data> — sessão N
Feito: <o que ficou verde>
Estado: <o que está pela metade e onde>
Próximo: <o primeiro passo da próxima sessão>
```

## Em cada sessão

1. Leia `progress.md`, `git log --oneline -10` e `features.json`. Rode o gate para confirmar que o estado está verde antes de mexer.
2. Espelhe os critérios pendentes na lista de tarefas nativa da ferramenta: a de tarefas do Claude Code, o plano do Codex e o `todowrite` do OpenCode. É ela que mostra o andamento na tela. O `features.json` continua sendo a fonte que sobrevive entre sessões.
3. Pegue um critério com `"passa": false`. Faça um por vez, na ordem do arquivo. Ao começar, marque a tarefa como em andamento e escreva uma linha: `▶ N/T: <critério>`.
4. Marque `"passa": true` só depois de rodar a prova e ver passar. Nunca altere `criterio` nem `prova`. Marque a tarefa nativa como concluída.
5. Commit por critério verde. Atualize `progress.md` antes de encerrar.

## Pausar e retomar

- O usuário pede pausa: termine o critério atual, commite, atualize `progress.md` e pare. Não comece o próximo.
- O usuário interrompe no meio (`Esc`): o critério fica sem commit. Na volta, o diff sem commit mostra onde parou; decida com o usuário entre terminar e descartar.
- Em sessão nova: skill `retomar`, se instalada; senão, siga "Em cada sessão" acima.

## Cache

Rodada longa fica barata quando o começo do contexto não muda. Segundo a doc do Claude Code, estas ações invalidam o cache, e o contexto inteiro volta a ser cobrado:
- trocar de modelo, ou mudar o esforço em modelo anterior à família 5.5;
- ligar ou desligar o fast mode;
- conectar ou remover um MCP;
- compactar.

Evite essas ações no meio da rodada. Editar `CLAUDE.md` não quebra o cache, mas só vale depois de `/clear` ou `/compact`: anote a mudança de regra no `progress.md` e aplique no `ship`. Pausa maior que o TTL do cache (5 minutos com chave de API, 1 hora na assinatura) também esfria tudo; a statusline mostra "esfria em". Pause no fim de um critério.

## Ao fechar

A skill `ship` remove `progress.md` e `features.json`. O que vale guardar fica no SPEC.md, nas decisões e no `git log`.
