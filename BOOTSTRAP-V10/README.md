# PREVEC V10

Bootstrap para Claude Code, Codex e OpenCode. Lê o projeto, instala as regras boas que ele já tem, e dá ao agente um plano padronizado para tarefa grande e caminho direto para tarefa pontual. A garantia fica em hook, não na memória do modelo.

> O PREVEC é um workflow do **ia-coders**. O V10 junta o V8 (plano T.A.C.E que deixa a execução sem decisão) e o V9 (pouco contexto fixo, verificação por máquina).

## Uso

Na raiz do projeto:

```
Leia e execute BOOTSTRAP-V10/bootstrap-v10.md
```

Wizard em caixas de opção (até quatro chamadas). Auditoria depois: `bash BOOTSTRAP-V10/assets/doctor.sh`. Teste do kit: `bash BOOTSTRAP-V10/assets/tests/hooks-test.sh` (102 casos).

## O fluxo

O agente classifica o pedido antes de agir:

| Tamanho | O que acontece |
|---|---|
| **Pontual** (1 a 3 arquivos, sem decisão) | Faz direto. Sem plano, sem arquivo. Teste afetado e entrega |
| **Médio** (já especificado, cabe na sessão, você mesmo executa) | Passos em uma linha cada, teste afetado por passo, `GATE_FULL` no fim. Sem arquivo |
| **Grande** (decisão a aprovar, delegação, várias sessões, módulo novo, área de risco) | Skill `plano` (`.context/planos/00001-<feature>.md`), `executar` (move para `work/`), `ship` (move para `done/`) |

"Testes primeiro" ou "spec" no pedido: a primeira fase do plano escreve os testes e os trava.

## O plano T.A.C.E 2.0

Um molde só (`skills/plano/references/plano.template.md`). O que faz a execução falhar menos:

- **Mapa**: o que o planejador já leu, com `path:line`. Cada executor recebe pronto e não levanta contexto de novo.
- Por task: **A** arquivos exatos, **Ref** vizinho a imitar, **C** comportamento em EARS com o caminho de erro, **E** comando que roda só o teste da task, `depende:`, `[P]` paralelo, `agente:` sugerido, **Cuidado** com a armadilha conhecida.
- **Pode dar errado** (só grande): pre-mortem curto.
- Checagem por máquina: o hook `prevec.sh plano` roda ao gravar o plano e acusa arquivo inexistente sem `(novo)`, task sem EARS ou sem comando, dependência circular e `[P]` que divide arquivo. Verificação determinística pega o que um revisor LLM deixa passar em texto fluente.
- O plano é também o estado: o hook marca 🔄 quando o agente edita um arquivo do A de uma task ou despacha subagente com `T3` na descrição, e ✅ quando o subagente volta `VEREDITO: ok` (inclusive em background, pelo `SubagentStop`) ou o E rodou e o trabalho passou para a próxima. Estado nunca regride. Sem `progress.md`, sem `features.json`.

## Orquestração por custo

Opus na conversa principal planeja, integra e revisa. Código delegado sai em Sonnet (`executor`) ou Haiku (`mecanico`), pela complexidade; o `revisor` é Opus.

- Delega quando compensa: leitura grande, task de 3+ arquivos com A, C e E fechados, ajuste repetido, tasks `[P]` em paralelo. Ajuste pontual e trabalho acoplado ficam na conversa principal, porque passar contexto e aquecer o subagente custa mais.
- O pedido leva o contexto pronto (task inteira, Mapa, `path:line`, prova). O executor lê só A e Ref; precisou de mais de 3 arquivos fora disso, devolve `bloqueado` dizendo o que faltou.
- Hook de ritmo: quando um turno da conversa principal passa de 5 arquivos editados ou 15 leituras sem editar, o agente recebe um aviso único para pesar delegar. Não bloqueia.
- Hook de rótulo: a descrição de cada subagente ganha o modelo na frente (`Sonnet high · Escrevendo testes`), e a lista de agentes mostra quem roda onde.

## Testes sem travar a máquina

- Por task: só o teste afetado (campo E). Fim de turno: `GATE_FAST` por hook, com `{changed}`.
- Fim de fase: `tq.sh --fase`. Em monorepo, `GATE_PARTS` roda só as partes que o diff tocou; o `GATE_FULL` inteiro roda no fim do plano.
- `GATE_FULL` uma vez por estado do código: verde, a fila grava o estado; pedir de novo sem mudar código (revisor, ship) é negado pelo hook com a hora em que passou. `TQ_FORCE=1` força.
- **Fila `tq`**: uma suíte pesada por repositório por vez, valendo entre sessões, subagentes e worktrees. FIFO por ticket com `flock` (python3, macOS e Linux, sem daemon). Dono morto (crash, `kill -9`) não prende a fila. Quem espera não gasta token: o processo dorme e imprime "posição 2 de 3". O hook `fila.sh` reescreve o `GATE_FULL` e os comandos de `TQ_MATCH` para passar pela fila (`updatedInput`): o agente pede o comando normal e ele espera a vez sozinho, sem turno extra. Teste de um arquivo passa direto. Validado numa sessão real do Claude Code: com a fila ocupada, a suíte do agente esperou (`posição 2 de 2`) e rodou em seguida. Suíte longa roda em background e a notificação chega no fim.
- Por que não cron a cada 30 s: cada consulta seria um turno do modelo. Na fila, a espera é do processo, e a ordem é justa (`flock` sozinho não garante ordem).

## Statusline

```
reelr/api  |  main*5  |  Opus  |  ████░░░░░░ 35% (348k/1M)  |  +1201 -71
▶ 3/7 T3 Validar CPF no cadastro · editando cpf.py · ⇢ executor·Sonnet · gate ✓ 12s · fila 2 · cache 94%
```

- Pasta (com subpasta e worktree) na frente: o chat rola, a linha fica.
- Tarefa e ação gravadas por hook, não pela memória do modelo. Ordem: tarefa nativa (se a ferramenta tem), task do plano inferida pelo arquivo editado, o pedido atual (sem plano). Depois vem a ação em curso: `editando cli.py`, `testando`, `suíte na fila`, `delegando: …`.
- Achado na simulação: com os modelos 5.5, o Claude Code não expõe `TaskCreate`/`TodoWrite`. Por isso o V10 não depende da lista nativa; usa quando existe.
- Cada linha cabe em `$COLUMNS`; o texto da tarefa tem teto em `STATUS_TASK_MAX` (40). Faltou espaço, saem os itens do fim da linha antes de a tarefa ficar ilegível.
- `refreshInterval: 5` para fila e subagente aparecerem sem esperar evento.

## Estilo de resposta

`dev-claro` (recomendado no wizard): primeira linha é o resultado em linguagem simples; o importante (risco, algo quebrado, decisão sua) vem logo depois; o que mudou pelo comportamento; o técnico curto no fim (`path:line` e prova, sem código). Pedido que começa com "detalhe" (ou curto com a palavra) recebe, por hook, o aviso de modo técnico só naquela resposta.

Fonte única em `.claude/output-styles/dev-claro.md`, sem passar pelo `AGENTS.md` (que as três ferramentas leem e duplicaria tokens): Claude Code por `outputStyle` com `keep-coding-instructions: true`, OpenCode por `instructions` no `opencode.json`, Codex por `developer_instructions`. É regra de formato, não persona: persona não melhora resultado; formato explícito é verificável.

## Melhoria do próprio processo

- O hook `cmdlog` registra a assinatura de cada comando de shell (sem caminhos nem números), sem gastar token.
- Ao repetir a mesma sequência manual pela terceira vez, o agente propõe em uma linha um script ou alvo de Makefile. Cria só com aprovação.
- `/retro` conta as repetições, propõe script, hook ou poda de skill sem uso, e nunca edita `AGENTS.md`, regra ou skill sozinho.
- O que ficou de fora de propósito: skill gerada automaticamente e memória consolidada. O estudo da ETH (arXiv 2602.11988) mediu que arquivo de contexto escrito por LLM piora o resultado e sobe o custo; ACE (ICLR 2026) mostrou que reescrever o contexto inteiro perde detalhe. Por isso: proposta com evidência, aprovação, mudança de uma linha, hook antes de regra.

## Trava de escopo

`ESCOPO=avisar` (padrão): edição fora da seção A da task ativa passa, com aviso para o agente acrescentar o arquivo ao plano com o motivo ou desfazer. `bloquear` nega a edição: para modelos mais fracos, que é onde o V8 brilhava. `desligado` tira.

## O que o bootstrap gera

```
AGENTS.md                      45–65 linhas, fonte única para as três ferramentas
CLAUDE.md                      @AGENTS.md + instruções de compactação
.claude/
  settings.json                hooks + deny + statusline
  hooks/                       gates.conf · _lib.sh · gate.sh · guard.sh · format.sh · notify.sh
                               fila.sh + tq.sh + tq.py (fila de testes)
                               prevec.sh + prevec.py (status, ação, ritmo, escopo, rótulo, cmdlog, checagem de plano)
                               statusline.sh + statusline.py
  rules/                       codigo · testes · api · dados · ui, com paths:
  skills/                      plano · executar · ship · delegar · postura · retomar · retro · code-review-confiavel
  agents/                      explorador e mecanico (Haiku) · executor (Sonnet) · revisor (Opus)
.context/
  planos/NNNNN-<feature>.md    em planejamento (número sequencial, nunca muda)
  work/NNNNN-<feature>.md      em execução: plano e estado
  done/NNNNN-<feature>.md      entregue, depois do ship
  decisions/                   só decisão de arquitetura
.codex/ · .opencode/           os mesmos agentes; no Codex, os mesmos hooks
```

## O que mudou do V9

| V9 | V10 | Por quê |
|---|---|---|
| Statusline lia `features.json` (só no modo spec) | Hooks gravam pedido, task do plano e ação em curso; pasta e subagente com modelo; ajuste à largura | O modelo esquecia de atualizar; a linha cortava |
| Delegação só por texto | Regra de custo no `AGENTS.md`, hook de ritmo, pedido com Mapa | O modelo fazia tudo na conversa principal |
| Plano livre fora do modo spec | Molde T.A.C.E 2.0 com checagem por máquina | Plano sem padrão deixava decisão para a execução |
| Modos vibe, padrão, spec | Tamanho decide (pontual, médio, grande) | Só grande cria arquivo de plano, sempre no mesmo molde |
| SPEC + `features.json` + `progress.md` | Um arquivo de plano, estado marcado por hook | Menos documento para escrever |
| `GATE_FULL` no revisor e no ship | Uma vez por fase, pela fila | Projeto com suíte de 20 minutos |
| — | Fila `tq` | Duas suítes ao mesmo tempo travavam a máquina |
| — | Trava de escopo | Vantagem do V8 para modelos mais fracos |

## Alcance por ferramenta

- **Claude Code**: tudo.
- **Codex**: gate, guard, format, escopo e checagem de plano por hook; a fila precisa do nome da tool de shell no `.codex/hooks.json` (o bootstrap confere na doc). Sem status, ritmo e rótulo.
- **OpenCode**: sem hooks; gate, fila e escopo dependem do `AGENTS.md`.

## Princípios

1. **Contexto é orçamento.** A conversa principal fica pequena; o subagente recebe o contexto pronto.
2. **Regra que importa vira máquina.** Hook, deny, lint, teste, checador de plano.
3. **Plano bom poupa execução.** Decisão tomada no plano não vira retrabalho.
4. **Cerimônia pelo tamanho, revisão pelo risco.**
5. **Prova, não afirmação.**

## Fontes

- Anthropic: *Effective context engineering* (2025), *Effective harnesses for long-running agents* (2025), *How we built our multi-agent research system* (2025).
- Cognition, *Multi-Agents: What's Actually Working* (2026-04): escrita em um fio só, leitura e revisão em paralelo.
- GitHub spec-kit (`[P]`, caminho exato por task, testes antes), Kiro (EARS).
- code.claude.com/docs: hooks, statusline, sub-agents, settings · learn.chatgpt.com/docs (Codex hooks e subagents) · opencode.ai/docs (agents, plugins).
- Fila: GitLab `resource_group` (`oldest_first`), `flock` sem ordem justa, propostas de lock de suíte em plugins de agente (trustmybot #2092, bkit #848).
