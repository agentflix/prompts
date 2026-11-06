---
name: retomar
description: Retoma um trabalho longo que foi pausado ou interrompido. Lê progress.md, features.json e o git log da feature, confirma que o estado está verde e segue da próxima tarefa pendente. Use quando o usuário disser retomar, continuar de onde parou, ou abrir sessão nova no meio de uma feature longa.
---

# Retomar

1. **Achar a feature.** A pasta em `.context/specs/` cujo `features.json` ainda tem `"passa": false`. Se houver mais de uma, pergunte qual, com a ferramenta de pergunta da CLI.
2. **Ler o estado.** `progress.md` (a última entrada), `git log --oneline -10` e `git status --short`. Mudança sem commit é a tarefa que ficou pela metade: leia o diff e decida com o usuário entre terminar e descartar.
3. **Confirmar verde.** Rode o `GATE_FAST` de `.claude/hooks/gates.conf`. Se estiver vermelho por algo de antes, diga e pergunte antes de seguir.
4. **Seguir.** Uma tarefa por vez, na ordem do `features.json`, como em `.claude/skills/spec/references/longa-duracao.md`. Ao começar cada uma, escreva uma linha: `▶ N/T: <critério>`.

Primeira resposta: em que tarefa parou, o que já está verde e qual é a próxima. Até 5 linhas.
