---
name: delegar
description: Decide por custo se vale delegar a um subagente, qual agente usar, e escreve o pedido com o contexto já levantado para o subagente executar sem explorar. Use antes de abrir subagente, ao paralelizar tasks [P], ou quando uma delegação falhou e precisa de escalada.
---

# Delegar

Subagente começa do zero. Ele custa o pedido que você escreve, mais o que ele lê, mais o aquecimento. Compensa quando poupa mais contexto da conversa principal do que custa, ou quando roda em paralelo.

## Fazer direto ou delegar

Faça direto quando:
- é ajuste de 1 a 2 arquivos que você já leu;
- cada passo depende do anterior;
- escrever o pedido daria quase o mesmo trabalho que fazer.

Delegue quando:
- a leitura é grande e só a conclusão importa (`explorador`);
- a task do plano tem A, C e E fechados e toca 3+ arquivos (`executor`);
- é o mesmo ajuste em muitos lugares, com prova automática (`mecanico`);
- há tasks `[P]` prontas: uma por subagente, em paralelo, no mesmo working tree (A disjuntos, o checador do plano garante). `isolation: worktree` só quando geram o mesmo artefato; o worktree nasce da branch padrão, então commite antes o que ele precisa ver e junte com `git merge` depois do teste;
- é revisão: `revisor`, que não viu a conversa.

| Agente | Modelo · effort | Para quê |
|---|---|---|
| `explorador` | Haiku · medium | Achar, mapear, resumir log. Não edita |
| `mecanico` | Haiku · medium | Ajuste repetido com prova automática |
| `executor` | Sonnet · high | Task especificada |
| `revisor` | Opus · high | Revisar diff ou plano. Não edita |

Haiku não revisa nem decide design. No Codex e no OpenCode os nomes são os mesmos; o modelo vem da config de cada um.

## O pedido: contexto pronto, nada a levantar

O que você já sabe vai no pedido. Cada fato que o subagente precisa descobrir sozinho custa leituras e abre espaço para ele errar.

```
Task: <T3 — título> do plano <.context/planos/00003-x.md>
A: <arquivos exatos, novo/editar> · Ref: <arquivo:linhas a imitar>
C: <cláusulas EARS copiadas do plano>
E: <comando> → <resultado esperado>
Já sabemos: <fatos do Mapa com path:line; trecho curto do padrão se for decisivo>
Não fazer: <o que fica fora; regras de .claude/rules/ que valem aqui, por ID>
Leia só: A e Ref. Precisou de outro arquivo: pare e devolva bloqueado.
```

Para o `explorador`: a pergunta exata, onde procurar primeiro e o formato da resposta. Dois subagentes em paralelo recebem fronteiras que não se cruzam.

## A resposta

- Volta curta: veredito, `path:line`, prova, o que não foi verificado. Use a conclusão; não copie a resposta para o usuário.
- Afirmação que decide algo ("testes passam", "não há outro uso"): confira o comando ou mande ao `revisor`. Subagente erra com a mesma confiança com que acerta.

## Escalada

1. `bloqueado` por decisão ou arquivo faltando: o pedido estava incompleto. Corrija o pedido (e a task no plano), não o agente.
2. Falhou na prova: repita com `effort: xhigh`, levando a saída da falha.
3. Falhou de novo: `model: opus`. Depois, `model: fable`, avisando o usuário do custo.

Não troque `/model` no meio da sessão para economizar: o cache da conversa inteira se perde. Não abra subagente por arquivo nem cadeia sem limite.
