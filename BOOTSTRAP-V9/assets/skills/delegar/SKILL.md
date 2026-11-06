---
name: delegar
description: Decide se vale delegar a um subagente, qual agente e modelo usar, como escrever o pedido e como conferir a resposta. Use antes de abrir qualquer subagente, ao paralelizar trabalho, ou quando uma tarefa delegada falhou e precisa de escalada.
---

# Delegar

Subagente começa do zero: não vê a conversa nem os arquivos que você leu. Multiagente gasta muito mais token que um agente só (cerca de 15x num chat, segundo a Anthropic). Delegue quando isso compra algo.

## Quando delegar
- Leitura grande que poluiria seu contexto (mapear área, ler log longo): `explorador`.
- Partes independentes que podem andar em paralelo: um subagente por parte. Paralelo só para leitura, ou com `isolation: worktree` quando editar. O worktree nasce da branch padrão, não do seu estado atual: commite antes o que o subagente precisa ver (SPEC, código base). Quem junta é você, com `git merge` da branch do worktree, depois do gate.
- Revisão independente: `revisor`, que não viu a conversa.
- Trabalho maior que uma janela de contexto (auditoria, migração em massa): workflow, com Opus orquestrando e Sonnet executando.

Não delegue tarefa de menos de cerca de 10 passos, nem trabalho acoplado em que cada passo depende do anterior. Faça você.

Todo subagente lê o `AGENTS.md`. A seção Orquestração vale só para a conversa principal; o subagente segue o pedido e o próprio papel.

## Qual agente

| Tarefa | Agente | Modelo · effort |
|---|---|---|
| Achar, mapear, resumir, rodar comando que só lê | `explorador` | Haiku · medium |
| Rename, troca de import, ajuste repetido com prova automática | `mecanico` | Haiku · medium |
| Implementar item especificado | `executor` | Sonnet · high |
| Revisar diff, julgar regra, achar bug sutil | `revisor` | Opus · high |
| Precisa de quase tudo que você já leu | fork da conversa (Claude Code) | o seu, com o cache compartilhado; não aceita `model` nem `effort` por chamada |

Haiku não revisa nem decide design: em busca de defeito ele acerta bem menos que o Opus, e o barato sai caro.

No Codex e no OpenCode, os nomes dos agentes são os mesmos, mas o modelo vem da config de cada ferramenta. `model`, `effort`, `isolation` e fork por chamada são do Claude Code.

## O pedido

Prosa completa. Não comprima: é aqui que a perda vira trabalho errado.

```
Objetivo: <uma frase com o resultado esperado>
Pronto quando: <critério verificável>
Escopo: <arquivos ou pastas> · Não fazer: <o que fica de fora, regra que vale>
Já sabemos: <o que foi lido ou descartado, com path:line>
Prova: <comando que confirma>
Orçamento: <até N chamadas ou arquivos>
```

Dois subagentes em paralelo recebem fronteiras que não se cruzam. Sem isso, duplicam o trabalho.

## A resposta
- Cada agente devolve um bloco curto com veredito, achados com path:line, evidência e o que não foi verificado. O `executor` e o `mecanico` acrescentam arquivos e prova; o `revisor` usa aprovado ou reprovado.
- Não copie a resposta inteira para o usuário. Use a conclusão.
- Afirmação que decide algo crítico (bug confirmado, "testes passam", "não há outro uso"), confira você ou mande ao `revisor`. Subagente erra com a mesma confiança com que acerta.

## Escalada

1. Primeira tentativa no agente da tabela.
2. Falhou na prova ou o revisor reprovou: repita com effort maior na chamada (`effort: high` ou `xhigh`), levando a saída da falha no pedido. Mudar effort não quebra cache nos modelos 5.5.
3. Falhou de novo: suba o modelo na chamada (`model: opus`). Se já era Opus, como no `revisor`, vá para o passo 4.
4. Última tentativa: `model: fable`, avisando o usuário de que custa bem mais que o Opus.

O cache de subagente dura 5 minutos por padrão, mesmo na assinatura. Para delegações longas e repetidas, `subagentPromptCacheTtl: "1h"` no settings evita pagar o contexto de novo.

## O que não fazer
- Trocar `/model` no meio da sessão para "economizar": o cache da conversa inteira é perdido. O modelo muda por subagente.
- Deixar o advisor ligado por padrão: custo bem maior por ganho pequeno na medição da Anthropic.
- Abrir subagente para cada arquivo, ou cadeia de subagentes sem limite.
