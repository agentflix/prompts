---
name: executar
description: Executa um plano de .context/work/ task a task, decidindo por custo entre fazer direto e delegar, rodando tasks [P] em paralelo, provando cada task com o teste afetado e o GATE_FULL só no fim da fase pela fila. Use depois da skill plano, ou quando o usuário pedir para executar, continuar ou retomar um plano.
---

# Executar

O plano já decidiu. Aqui é ritmo: cada task fecha com a própria prova e a conversa principal fica pequena.

## Preparar

1. Plano ativo: `.context/work/*.md`. Plano ainda em `.context/planos/`: mova para `.context/work/` e ponha `status: em-execucao`. Mais de um em `work/`: pergunte qual.
2. Estado: no Claude Code, o hook marca a task 🔄 no plano quando você edita um arquivo do A dela ou despacha um subagente com o código (`T3`) na descrição, e ✅ quando o subagente volta `ok` ou você roda o E dela e passa para a próxima. Você só marca ✅ à mão a última task, ou a que não editou arquivo. Se a ferramenta tem lista de tarefas nativa (TaskCreate, plano do Codex, `todowrite`), use o assunto começando pelo código: `T3 — Validar CPF`.
3. `git status --short`: mudança sem commit de antes é task pela metade. Leia o diff e decida com o usuário entre terminar e descartar.

## Para cada task, na ordem de dependência

Escolha quem faz. A conversa principal (Opus) planeja, integra e revisa; o código de task delegada sai em Sonnet ou Haiku, pela complexidade:

| Situação | Quem |
|---|---|
| `agente: direto`, ou 1 a 2 arquivos que você acabou de ler, ou acoplada à anterior | Você |
| Task com A, C e E fechados e 3+ arquivos, ou você já está com o contexto cheio | `executor` (Sonnet) |
| Task simples e bem delimitada: boilerplate de um molde, ajuste repetido, com prova automática | `mecanico` (Haiku) |
| Duas ou mais `[P]` prontas na mesma fase | Um subagente por task (o do campo `agente:`), em paralelo, no mesmo working tree: o checador garante que `[P]` não divide arquivo. Worktree só se as tasks geram o mesmo artefato (lockfile, código gerado) |

O pedido ao subagente é a task inteira copiada do plano, mais o **Mapa** e o que você já sabe dela. Formato na skill `delegar`. Ele não deve ler nada fora de A e da Ref.

Feche a task quando o comando de **E** passar, rodado por você ou visto na resposta do subagente com as linhas que provam. Na descrição do subagente, comece pelo código da task (`T3 — …`): é o que a statusline e o plano usam. Sem commit por task: o commit é do `ship` (ou por fase, se o usuário pediu).

## Se a task não fecha

- Faltou arquivo em A ou o executor devolveu `bloqueado` por decisão: o defeito é do plano. Corrija a task no plano (A, C ou Cuidado) e redespache com a correção. Repetir o mesmo pedido falha igual.
- E vermelho depois de duas tentativas: pare a fase e mostre o erro. Não avance; a próxima task herda o defeito.
- Descobriu trabalho fora do plano: vira task nova no plano, não entra escondido na atual.

## Fim de fase

Rode o `GATE_FULL` pela fila: `.claude/hooks/tq.sh "<GATE_FULL>"`, com `timeout: 600000` no Bash, ou em background se pode passar de 10 minutos. Vermelho: corrija antes da próxima fase. Na última fase, siga com a skill `ship`, levando a saída do `GATE_FULL` para ele não rodar de novo no mesmo estado.

## Pausa

"Pausa": termine a task atual, deixe a tarefa nativa e o plano em dia e pare. Em sessão nova, a skill `retomar` lê o plano e segue.
