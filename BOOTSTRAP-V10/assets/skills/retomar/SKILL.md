---
name: retomar
description: Retoma um plano pausado ou interrompido. Lê o plano em execução e o git, confirma que o estado está verde e segue da próxima task. Use quando o usuário disser retomar, continuar de onde parou, ou abrir sessão nova no meio de um plano.
---

# Retomar

1. **Plano.** `.context/planos/*.md` com `status: em-execucao`. Mais de um: pergunte qual, com a ferramenta de pergunta da CLI.
2. **Estado.** No plano, a task `🔄` é a que ficou pela metade, `✅` está feita, `⬜` falta. `git log --oneline -5` e `git status --short`: diff sem commit é a task pela metade; leia e decida com o usuário entre terminar e descartar.
3. **Verde?** Rode o teste do **E** da última task `✅`. Vermelho por algo de antes: diga e pergunte antes de seguir.
4. **Seguir** com a skill `executar`, recriando as tarefas nativas das tasks pendentes.

Primeira resposta, até 5 linhas: onde parou, o que está verde, qual é a próxima.
