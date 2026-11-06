# PREVEC V9

Bootstrap para Claude Code, Codex e OpenCode. Ele lê o projeto e instala o contexto mínimo e as verificações automáticas de que um agente de código precisa em 2026.

> O PREVEC é um workflow do **ia-coders**. O V9 continua a linha do V8, com crédito à metodologia original.

## Uso

Abra o agente na raiz do projeto e peça:

```
Leia e execute BOOTSTRAP-V9/bootstrap-v9.md
```

O setup é um wizard em caixas de opções, com a recomendação já marcada, em três chamadas:
1. ferramentas, modo, postura e saída;
2. áreas de risco, skills de intenção e skills de trabalho longo;
3. o que ativar: proteções, statusline e notificação, regras por área e subagentes.

O que você desmarca não é instalado.

Para auditar o projeto depois (custo de contexto, placeholders, hooks):

```
bash BOOTSTRAP-V9/assets/doctor.sh
```

Para testar o próprio kit (hooks, gate, guard, format, statusline), rode `bash BOOTSTRAP-V9/assets/tests/hooks-test.sh`. São 41 casos, num diretório temporário próprio.

## A ideia em uma frase

Menos instrução, mais verificação. Modelos como Opus 5.5, Sonnet 5.5 e os da OpenAI de 2026 já não erram por falta de passo a passo; erram declarando pronto o que não está. O V9 gasta poucos tokens no que o modelo já sabe fazer e põe a garantia em hook, teste e revisor independente.

## Três modos

O projeto tem um modo padrão, escolhido no setup. Para trocar numa tarefa, basta pedir.

| Modo | Para quê | O que acontece |
|---|---|---|
| **vibe** | Protótipo, ajuste rápido, explorar | O agente faz direto, sem plano e sem arquivo. Os hooks continuam: gate no fim do turno, arquivos protegidos |
| **padrão** | Dia a dia | O agente planeja na conversa só quando vale a pena. Revisão pelo subagente `revisor` (ou `/code-review`) antes do commit de diff médio |
| **spec** | Projeto que exige documentação sólida | Skill `spec`: entrevista, `SPEC.md` com critérios testáveis, testes escritos antes e travados, implementação, revisor contra a spec, skill `ship` |

Em qualquer modo, mudança nas áreas de risco do projeto (migration, contrato, autenticação, pagamento) pede revisão independente antes do commit.

## Postura, saída e perguntas

São três eixos independentes do modo, escolhidos no setup.

- **Postura** muda o que o agente ousa fazer.
  - `conservador`: diff mínimo, sem dependência nova sem aprovação, pergunta antes de supor.
  - `equilibrado`: o padrão.
  - `criativo`: sugere até 3 ideias novas com ganho, custo e risco, e implementa só as aprovadas.
  - Troque com `/postura`.
  - A postura é escrita como regra de comportamento, não como adjetivo. Persona ("você é um engenheiro sênior conservador") não melhora a acurácia e tem efeito imprevisível (Zheng et al., EMNLP 2024). Regra explícita de quando perguntar e o que não mudar é verificável.
  - A postura criativa exige trade-off e a opção conservadora ao lado de cada ideia, porque persona "amigável" aumenta a bajulação (ACL 2026, *Too Nice to Tell the Truth*).
- **Saída curta** reduz o texto da resposta sem tocar no rigor.
  - No Claude Code, um output style `curto` com `keep-coding-instructions: true`.
  - No Codex, `model_verbosity = "low"`.
  - Se você já usa o caveman, ele cumpre o mesmo papel.
- **Perguntas em caixa**: toda lacuna vai para a ferramenta de pergunta da CLI (no Claude Code, `AskUserQuestion`), com opções clicáveis e a recomendada primeiro.

A garantia de verdade continua nos hooks: na postura conservadora, instalar dependência cai em `ask` no `settings.json`.

## Trabalho longo: andamento, pausa, cache e retro

- **Andamento na tela.** Statusline do Claude Code em duas linhas: `main*5 | Opus | ████░░░░░░ 35% (348k/1M) | +1201 -71` e, embaixo, `▶ 7/30 valida CPF · gate ✓ 12s · cache 94% esfria em 3m`. O harness desenha a linha, então ela não gasta token do modelo. Os dados vêm do `features.json`, do registro do gate e dos campos `prompt_cache` e `context_window` que o Claude Code passa à statusline. A lista de tarefas nativa espelha o `features.json`. No Codex e no OpenCode, o bootstrap consulta a doc atual para ligar o equivalente.
- **Aviso.** O hook `Notification` dispara uma notificação do macOS (ou `notify-send` no Linux) quando o agente espera você ou termina.
- **Pausa e retomada.** O trabalho avança um critério por vez, com commit por critério verde.
  - Para pausar sem perder nada, diga "pausa": ele fecha o critério atual e para.
  - Para parar na hora, use `Esc`.
  - Para continuar em sessão nova, use `/retomar`.
- **Cache.** A statusline mostra a taxa de acerto, quanto falta para esfriar e a causa quando o cache cai. A regra de rodada longa evita o que invalida o cache: trocar modelo, mudar o esforço em modelo anterior à família 5.5, ligar ou desligar fast mode, mexer em MCP e compactar.
- **`/retro`.** Lê o registro de tempo e o resultado de cada gate, mais o progresso, e sugere até 5 melhorias com o dado que sustenta cada uma. Exemplos: gate lento, tarefas paralelizáveis, subagente `haiku` para trabalho mecânico, teste instável. Você escolhe numa caixa de opções.

## Orquestração e modelos

O thread principal (Opus 5.5, o padrão do Claude Code) orquestra. Cada subagente tem modelo fixo no frontmatter:

| Agente | Modelo · effort | Para quê |
|---|---|---|
| `explorador` | Haiku 5.5 · medium | Achar, mapear, resumir log, sem editar. Preferido ao Explore embutido, que roda no modelo da conversa principal |
| `mecanico` | Haiku 5.5 · medium | Rename e ajuste repetido, só com prova automática |
| `executor` | Sonnet 5.5 · high | Item especificado, inclusive em paralelo com worktree |
| `revisor` | Opus 5.5 · high | Revisão cética. Haiku aqui é falsa economia: na busca de defeito ele acerta bem menos que o Opus (doc *optimizing for cost and intelligence*) |

- **Como o orquestrador escolhe:** ao delegar, ele escolhe o agente, guiado pela skill `delegar`. Se a tarefa falha, repete com effort maior, depois com `model: opus` e, por último, `fable`.
- **Pedido completo, resposta curta:**
  - O pedido ao subagente vai em prosa completa: objetivo, pronto quando, escopo, o que não fazer, o que já sabemos, prova e orçamento.
  - A resposta volta telegráfica, em até 300 tokens, com veredito, `path:line` e o que não foi verificado. O detalhe vai para um arquivo fora do commit.
  - Por que não carregar o caveman inteiro nos subagentes: o ganho dele sobre um simples "seja conciso" é pequeno, e as regras custam tokens de entrada em cada subagente.
- **Regras de custo:**
  - Ajuste o effort antes de trocar de modelo. No SWE-bench Pro, o Opus 5.5 em medium fica cerca de 2,5 pontos abaixo do high, por 70% do custo.
  - O modelo muda por subagente, nunca por `/model` no meio da sessão, porque cada modelo tem cache próprio.
  - Fable 5.1 só entra como escalada.

Fontes: Anthropic, *How we built our multi-agent research system* (2025), *Effective context engineering* (2025) e *Harness design for long-running apps* (2026). Docs: platform.claude.com (*models overview*, *pricing*, *optimizing for cost and intelligence*) e code.claude.com (*sub-agents*, *model-config*, *prompt-caching*).

## O que o bootstrap gera

```
AGENTS.md                      35–55 linhas, fonte única para as três ferramentas
CLAUDE.md                      @AGENTS.md + instruções de compactação
.claude/
  settings.json                hooks + deny de permissão
  hooks/                       gates.conf · _lib.sh · gate.sh (Stop) · guard.sh (PreToolUse) · format.sh (PostToolUse)
                               statusline.sh + statusline.py · notify.sh (Notification)
  rules/                       codigo · testes · api · dados · ui — cada uma com paths:, carrega só ao tocar a área
  skills/                      spec · ship · postura · delegar · retomar · retro · code-review-confiavel · corrigir · investigar · construir · refatorar · migrar · verificar
  output-styles/curto.md       só com saída curta
  agents/                      explorador e mecanico (Haiku) · executor (Sonnet) · revisor (Opus, Edit e Write bloqueados)
.agents/skills → ../.claude/skills     Codex
.codex/{config.toml,hooks.json,agents/*.toml}   Codex: os mesmos hooks e os 4 agentes
.opencode/agents/*.md                  OpenCode: os 4 agentes
.context/
  decisions/                   o porquê, em ADR curto
  _arquivo/                    contexto antigo arquivado na migração; nada do V9 aponta para cá
  specs/<feature>/SPEC.md      só no modo spec; progress.md e features.json só em trabalho de várias sessões
```

## O que mudou do V8.2

### Saiu
| V8.2 | Por quê |
|---|---|
| PLANNER (Opus) como agente principal fixo | Forçava plano em tudo, inclusive no vibecoding. O plan mode nativo cobre quando você quer |
| BUILDER como subagente, um por task | Subagente "para resposta melhor" não melhora a resposta (doc do Claude Code) e repete contexto a cada despacho. O thread principal executa |
| T.A.C.E obrigatório com "zero pensamento" | Premissa de 2024. A Anthropic hoje recomenda instrução geral a passo prescrito. O T.A.C.E sobrevive só como formato curto de handoff para subagente |
| Iron Laws em CAPS | Nos modelos atuais, ênfase faz a regra ser aplicada além da conta. O que não pode falhar virou hook |
| `PREVEC.md` e `formats/` copiados em cada projeto | É teoria para humano. O agente pagava tokens por ela em todo turno |
| Resposta em 5 blocos fixos, duas perguntas no fim de todo plano | Saída longa e fricção repetida. Agora a entrega pede evidência e concisão |
| `overview.md`, `modules.yaml`, `flows.md` | O estudo da ETH (arXiv 2602.11988) mostrou que visão geral do repositório não melhora o resultado e sobe o custo em mais de 20% |
| Modelos fixos (`gpt-5.6-*`) | Nome de modelo muda a cada release. O V9 usa o padrão da conta e regula o esforço |

### Diminuiu
- `AGENTS.md`: de 80 para 35–55 linhas.
- `rules.md`, com 23 regras (8 do projeto e 15 invariantes) lidas antes de toda decisão: virou 5 arquivos com `paths:`, cada um carregado só quando você toca a área dele.
- Bootstrap: de 9 passos e 166KB para 4 passos e cerca de 75KB, fora o `code-review-confiavel`.
- Custo fixo por sessão: de cerca de 8 mil tokens para algo entre 1 e 1,7 mil, conforme o que o wizard ativa (o doctor mede o valor real).

### Ficou melhor
- Os 15 invariantes do V8.2 (dados, API, segurança e código) continuam, divididos por área com ID estável (C, A, D, U), e ganharam a política de testes (T). Parte deles agora tem barreira de máquina:
  - migration versionada não é editada;
  - `.env` não é lido nem editado pelas tools de arquivo;
  - teste existente fica travado no modo spec.

  A barreira cobre as tools de edição. Um comando de shell que reescreve o arquivo ainda passa, e por isso a regra escrita continua.
- O "gate completo nunca é pulado" virou hook `Stop`, que roda sozinho e não depende de o modelo lembrar.
- O delta de arquitetura virou o passo "contexto em dia" do `ship`: o commit corrige a documentação que ele tornou falsa.
- O review continua no fim e sobre a feature inteira, agora proporcional ao risco: gate, revisor ou 8 revisores.
- Skills, `AGENTS.md` e revisor funcionam nas três ferramentas. Os mesmos hooks rodam no Claude Code e no Codex. O OpenCode ainda fica sem hooks; lá o gate depende do `AGENTS.md`. No Codex as skills vêm de `.agents/skills`, que o V8 apontava errado.

### Entrou
- Os três modos.
- Skills de intenção no estilo TechLead: curtas, sem CAPS, com condição de parada.
- Testes primeiro e travados no modo spec. Isso combate o reward hacking: quando o teste contradiz a spec, modelos editam o teste em cerca de 50% dos casos (ImpossibleBench, 2025).
- Política de testes (`.claude/rules/testes.md`): o que testar (por risco e por critério de aceite), o que não testar e onde é permitido mock. Agentes adicionam mock em 36% dos commits contra 26% dos humanos (Hora & Robbes, MSR 2026), e cobertura não mede valor (Meta ACH, 2025).
- Gate rápido com `{changed}`, que roda só os testes afetados pela mudança (vitest `related`, jest `--findRelatedTests`, pytest `--testmon`, pest `--dirty`).
- Padrão de tarefa longa da Anthropic (`features.json` + `progress.md` + commit por critério).
- `doctor.sh`, que mede o custo de contexto e acha placeholder, CAPS e restos do V8.

## Princípios do V9

1. **Contexto é orçamento.** Só carrega sempre o que muda o comportamento e não se descobre lendo o código.
2. **Regra que importa vira máquina.** Hook, deny, lint e teste garantem; texto orienta.
3. **Cerimônia por escolha, risco por regra.** O modo é seu. A área de risco sobe a revisão em qualquer modo.
4. **Prova, não afirmação.** Pronto é o comando que passou, rodado por quem não escreveu o código.
5. **Um fato, um arquivo.** Herança do V8: quem precisa aponta, não copia.

## Tendência 2027 e manutenção

- **Revise o harness a cada modelo novo.** A Anthropic tirou etapas inteiras do próprio harness quando saiu o Opus 4.6. A cada geração, teste remover uma regra e veja se algo piora. O doctor ajuda a ver o que pesa.
- **Portabilidade.** `AGENTS.md`, skills no formato `SKILL.md` e hooks de linha de comando são hoje o padrão comum entre as ferramentas. Evite recurso que só uma delas tem quando houver equivalente comum.
- **Memória nativa primeiro.** Auto memory do Claude Code e Memories do Codex cobrem o pessoal; `.context/decisions/` cobre o do time. Trate memória como entrada não confiável e revise o que entra.
- **Mais autonomia, gates mais fortes.** Rodadas longas (`/goal`, `/loop`, workflows) só valem com gate automático e revisor independente. É por isso que o V9 começa pelos hooks.
- **Próximo passo natural:** empacotar skills, hooks e o revisor como plugin do Claude Code, para atualizar todos os projetos de uma vez. O que é específico de cada projeto (`gates.conf`, `rules/`, `AGENTS.md`) continua local.

## Fontes principais
- Anthropic, *Effective context engineering for AI agents* (2025-09-29) e *Effective harnesses for long-running agents* (2025-11-26)
- Anthropic, *Harness design for long-running apps* (2026-03-24)
- code.claude.com/docs: best-practices, memory, hooks, skills, sub-agents, costs
- platform.claude.com: prompting best practices (seção sobre ênfase e overtriggering)
- Gloaguen et al., *Evaluating AGENTS.md* (arXiv 2602.11988, ICLR 2026)
- ImpossibleBench (arXiv 2510.20270)
- learn.chatgpt.com/docs (Codex: skills, hooks, subagents) · opencode.ai/docs (V2)
- Böckeler, *Understanding SDD tools* (martinfowler.com, 2025-10-15)
