---
name: spec
description: Conduz uma mudança no modo spec. Entrevista até fechar lacunas, escreve SPEC.md em .context/specs/ com critérios testáveis, escreve os testes antes do código, implementa e fecha com a skill ship. Use quando o usuário pedir spec ou documentação sólida, ou quando o modo do AGENTS.md é spec e a mudança não é trivial.
---

# Spec

A spec existe para virar teste. Critério que não vira comando verificável ainda não está pronto.

1. **Entender.** Leia o código envolvido e `.context/decisions/`. Pergunte só o que o código não responde, numa rodada, com um default proposto em cada pergunta. Use a ferramenta de pergunta da CLI quando existir. "Assume os defaults" encerra a entrevista.
2. **Escrever.** Crie `.context/specs/<feature>/SPEC.md` a partir de `references/SPEC.template.md`. Seção vazia sai do arquivo. Mostre a spec e espere o usuário aprovar.
3. **Provar primeiro.** Escreva os testes dos critérios de aceite seguindo `.claude/rules/testes.md`: um por critério, na fronteira, sem mock interno. Se o gate do fim de turno estiver instalado, crie antes `.claude/hooks/gate.pause`, porque ele reprovaria os testes vermelhos de propósito. Confirme que falham pelo motivo certo e apague o `gate.pause`. Com o usuário de acordo e o guard instalado, crie `.claude/hooks/tests.lock`: a partir daí o hook bloqueia a edição de teste existente. Por isso, escreva os testes da feature em arquivo novo. Se a spec for abandonada, apague o `tests.lock`.
4. **Implementar.** Para mudança grande, sugira uma sessão limpa (`/clear`) com "implemente a SPEC em <caminho>". Trabalho que passa de uma sessão segue `references/longa-duracao.md`.
5. **Fechar.** Com os critérios verdes, use a skill `ship`.

## Delegar para subagente

Só para trabalho independente em paralelo ou exploração grande. O subagente não vê a conversa, então o pedido leva tudo:

```
Tarefa: <uma frase>
Arquivos: <caminhos> · Padrão a imitar: <arquivo>
Pronto quando: <critério da SPEC> · Prove com: <comando>
Fora do escopo: <o que não tocar>
```

## Se travar

- Teste existente contradiz a spec: pare e mostre o conflito ao usuário. Não edite o teste.
- Critério de aceite impossível ou ambíguo no meio do caminho: volte ao passo 1 só para ele.
- A spec mudou durante a implementação: atualize o SPEC.md no mesmo diff.
