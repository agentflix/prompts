---
name: postura
disable-model-invocation: true
description: Troca a postura do agente neste projeto entre conservador, equilibrado e criativo, reescrevendo a seção Postura do AGENTS.md. Invocada pelo usuário com /postura.
---

# Postura

1. Se o usuário não disse qual, pergunte com a ferramenta de pergunta da CLI, com três opções:
   - conservador: empresa, produção, pouco risco;
   - equilibrado: o padrão;
   - criativo: projeto pessoal, explorar ideias.
2. Substitua a seção `## Postura: …` do `AGENTS.md` pelo conteúdo de `references/<postura>.md`. Mantenha o resto do arquivo.
3. Ajuste `.claude/settings.json`:
   - conservador: acrescente ao `ask` o comando de instalar dependência do projeto (ex.: `Bash(npm install *)`, `Bash(pnpm add *)`, `Bash(composer require *)`);
   - equilibrado e criativo: remova essas entradas.
4. Responda em uma linha qual postura ficou ativa. A troca vale a partir da próxima sessão; nesta, siga a nova postura a partir de agora.
