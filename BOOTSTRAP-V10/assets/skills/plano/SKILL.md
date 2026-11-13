---
name: plano
description: Transforma um pedido grande em plano executável no formato T.A.C.E (arquivo exato, referência, comportamento em EARS, comando de prova, dependência e [P] paralelo), checado por máquina antes de executar. Use quando há decisão a aprovar, trabalho para subagentes, várias sessões, módulo novo ou área de risco, ou o usuário pede plano, spec ou testes primeiro. Não use para pontual nem para médio já especificado que você mesmo executa nesta sessão.
---

# Plano

Plano bom é o que deixa a execução sem decisão: cada task diz onde mexer, o que imitar, o que tem de ser verdade e como provar. Decisão empurrada para a execução vira retrabalho, e subagente que precisa decidir explora o repositório e erra.

## 1. Levantar uma vez

Leia o código envolvido até saber responder, para cada task: quais arquivos, qual vizinho imitar, qual comando de teste de um arquivo. Para área grande, mande o `explorador` com a pergunta exata. Tudo que você leu e importa vai para a seção **Mapa** do plano, com `path:line`: é o que poupa cada executor de ler de novo.

Leia `.context/decisions/` só se o pedido mexe em padrão ou arquitetura.

## 2. Perguntar uma vez

Só o que o código não responde e muda o plano. Uma rodada, com a ferramenta de pergunta da CLI, a opção recomendada primeiro. Sem resposta possível: decida, e registre em **Decidido** como "(assumido)".

## 3. Escrever

Arquivo `.context/planos/NNNNN-<feature>.md` a partir de `references/plano.template.md`. `NNNNN` é o número sequencial com 5 dígitos: o maior número em `.context/planos/`, `.context/work/` e `.context/done/` mais 1 (o primeiro é `00001`). O número nunca muda.

A pasta diz a fase: `.context/planos/` em planejamento, `.context/work/` em execução, `.context/done/` entregue. O arquivo só muda de pasta, com o mesmo nome. Seção vazia sai. Sempre: Objetivo, Mapa, tasks, Pronto quando. Decidido e Fora só se houver o que dizer. Várias sessões, módulo novo ou área de risco: **Pode dar errado** (pre-mortem: "a entrega falhou; por quê?") e fases, cada uma entregando algo que passa no `GATE_FULL` sozinha.

Cada task:

- Título `### T<n> — <verbo + o quê> · [P] · depende: T<m> · agente: <executor|mecanico|direto> · estado: ⬜`. `[P]` só quando não divide arquivo com outra `[P]` da fase nem depende dela. `depende:` só quando a task usa algo que a outra cria (arquivo, função, tabela, rota); estar na mesma fase não é dependência. A fase marca onde roda o gate. O checador sugere tirar dependência que não divide nem cita arquivo.
- **A**: arquivos exatos, `(novo)` ou `(editar: o que muda)`. Teste da task também entra.
- **Ref**: o vizinho a imitar, com linhas.
- **C**: cláusulas EARS (`QUANDO … O SISTEMA DEVE …`, `SE <erro>, ENTÃO …`), incluindo o caminho de erro. Cláusula que você não sabe escrever é comportamento não definido: volte ao passo 2.
- **E**: o comando que roda só o teste desta task e o resultado esperado. Nunca a suíte inteira. Task de área de risco (dinheiro, baixa, autorização, dado pessoal, migração): acrescente a prova de mutação, "apague a asserção principal (ou inverta a condição em `<arquivo:linha>`) e o teste falha". Fora disso, não: mutação em toda task custa tempo e raramente acha algo.
- **Cuidado**: a armadilha concreta, se houver.

Tamanho de task: o que um executor fecha em uma rodada, com 1 a 5 arquivos. Maior: quebre.

## 4. Checar

O hook `prevec.sh plano` roda sozinho ao gravar o arquivo e devolve os problemas (arquivo inexistente sem `(novo)`, task sem EARS ou sem comando, dependência circular, `[P]` dividindo arquivo). Fora do Claude Code, rode `.claude/hooks/prevec.sh plano <arquivo do plano>`. Corrija até o hook parar de listar problemas (na linha de comando, até sair "plano ok").

Depois, releia como executor: alguma task obriga a escolher arquivo, padrão ou comportamento? Se sim, a decisão é sua, agora.

## 5. Aprovar e seguir

Mostre o plano em até 15 linhas (tasks com agente e `[P]`, decisões assumidas, riscos). Pergunte numa caixa ("executar" recomendado, "ajustar", "só salvar") só quando há decisão "(assumido)", área de risco ou tamanho grande; senão, siga. Para executar, mova o arquivo para `.context/work/` (`git mv` se já versionado), ponha `status: em-execucao` e siga com a skill `executar` na mesma resposta. Se o usuário já disse "executa direto", não pergunte.

Grande ou área de risco: ofereça revisão do plano pelo `revisor` antes de executar ("revise este plano: alguma task tem decisão pendente, arquivo errado ou prova fraca?").

## Testes primeiro (spec)

Quando o pedido diz spec ou testes primeiro, a Fase 1 é só de testes, um por critério de **Pronto quando**, seguindo `.claude/rules/testes.md`. Antes dela, crie `.claude/hooks/gate.pause` (o gate reprovaria os testes vermelhos de propósito). Confirme que falham pelo motivo certo, apague o `gate.pause` e, com o usuário de acordo, crie `.claude/hooks/tests.lock`: o guard passa a bloquear edição de teste existente, então as próximas tasks escrevem teste novo em arquivo novo.
