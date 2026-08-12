# PREVEC V8 — setup

> PREVEC é um workflow do **ia-coders**. Créditos completos a incluir.

Bootstrap AI-First agnóstico: lê este projeto (ou o `spec.md` dele) e gera o
contexto que agents de código precisam para trabalhar sem alucinar.

Este arquivo é só o roteiro. **Cada passo mora no seu próprio arquivo** — leia e
execute um por vez, na ordem. Não leia todos de antemão.

---

## ⚠️ LEIA ISTO ANTES DO PASSO 0

### `assets/PREVEC.md` — a metodologia é o seu conhecimento de trabalho

Não é um documento para copiar no fim. **É o que ensina você a construir tudo o que
vem depois.** O ciclo, os três papéis, o T.A.C.E e os cinco princípios são a teoria
que decide como cada agent, cada skill e cada arquivo de contexto deve ser escrito.

**Leia `assets/PREVEC.md` inteiro agora.** Preste atenção especial à seção *"Como
esta metodologia dita a documentação"*: ela mapeia cada arquivo que você vai gerar ao
campo do T.A.C.E que ele existe para alimentar.

### A pergunta que você faz a cada arquivo que escrever

Não é *"isto está bem documentado?"*. É:

> **Com este arquivo na mão, o PLANNER consegue escrever uma task em que o executor
> não precise decidir nada?**

Um arquivo pode parecer completo e ainda falhar nessa pergunta. `arch/modules.yaml`
com módulos genéricos, `arch/gates.md` sem o comando real, `arch/rules.md` com
conselho em vez de afirmação verificável — todos os três *parecem* documentação e
nenhum dos três serve ao T.A.C.E.

### Os dois fluxos que ditam tudo

| Fluxo | O que ele governa no seu trabalho |
|---|---|
| **PREVEC** — 6 fases: **P**ré-Planning · **P**lanning · **R**eview · **E**xecution · **V**alidation · **C**onfirm | Quais artefatos existem, quem escreve cada um, e em que ordem. As 6 letras se distribuem em 3 agents: **P·P** no PLANNER, **E** no BUILDER, **R·V·C** no REVIEWER |
| **T.A.C.E** — **T**arefa · **A**rquivo · **C**omportamento · **E**vidência | Por que cada arquivo de contexto existe e o quão específico ele precisa ser. Cada campo tem autor (PLANNER), executor (BUILDER) e auditor (REVIEWER) |

**Ao escrever cada agent, declare as letras dele.** O agent não é "um papel genérico
que planeja": ele é dono de fases nomeadas, e a soma dos três reconstrói o PREVEC.
O mesmo vale para o T.A.C.E — cada agent tem a sua coluna em cada campo.

Tudo neste bootstrap deriva desses dois. Se um passo parecer arbitrário, volte ao
`PREVEC.md` — a razão está lá.

---

## Diretório de trabalho

Você trabalha **na raiz do projeto**, não dentro desta pasta. Os passos escrevem
`.context/`, `.claude/`, `AGENTS.md` e `CLAUDE.md` na raiz.

Os comandos dos passos citam assets como `assets/...` por legibilidade. **Prefixe
com o nome desta pasta** ao executar:

```bash
B=BOOTSTRAP-V8            # ou o nome real desta pasta, se você a renomeou
cp $B/assets/tools/CLAUDE.md CLAUDE.md
```

Defina `B` uma vez, no Passo 1, e use em todos os passos seguintes.

---

## Regras deste bootstrap

Cinco regras, e as cinco **derivam do PREVEC** — não são lista à parte:

| Regra | De onde vem |
|---|---|
| 1. **Um fato, um arquivo, N referências.** Escrevendo a mesma informação em dois arquivos? Um deve apontar para o outro | Princípio 1 do PREVEC |
| 2. **Nada derivado.** Dado calculável do repositório ou do git não é materializado | Princípio 1 do PREVEC |
| 3. **Nada genérico.** Todo valor vem do `spec.md` ou do código real. Não detectou? **Pergunte** — nunca invente, nunca deixe placeholder | T.A.C.E: campo vago não permite task sem decisão pendente |
| 4. **Formato estrito onde há `_TEMPLATE`** — seções, ordem e limite. Não improvise estrutura | Princípio 4: cerimônia proporcional, mas forma previsível |
| 5. **Cenário C respeita o que existe.** Nunca sobrescreva conteúdo especializado escrito à mão | Regra vigente só muda por decisão registrada |

---

## Os passos

Cada passo indica **qual parte do PREVEC ou do T.A.C.E ele serve**. Se você não sabe
por que está gerando um arquivo, a resposta está nessa coluna.

| # | Passo | Roteiro | Serve a |
|---|---|---|---|
| 0 | Detectar e perguntar | `assets/setup/0-detect.md` | A matéria-prima de tudo: sem detecção real, todo arquivo sai genérico |
| 1 | Estrutura e colas nativas | `assets/setup/1-structure.md` | Princípio 1: uma fonte por ferramenta, sem hub que duplica |
| 2 | Arquitetura | `assets/setup/2-arch.md` | Os campos **A**, **C** e **E** do T.A.C.E — cada arquivo alimenta um |
| 3 | Agents | `assets/setup/3-agents.md` | Os três papéis, e o princípio 3: o handoff carrega tudo |
| 4 | Skills | `assets/setup/4-skills.md` | Princípio 2: skill é o veículo de contexto, carregado sob demanda |
| 5 | Contrato | `assets/setup/5-contract.md` | O índice: onde cada coisa está, para o agent não carregar tudo |
| 6 | Metodologia e templates | `assets/setup/6-templates.md` | O PREVEC viaja no repositório; a forma do plano e das respostas fica fixa |
| 7 | Verificar | `bash assets/setup/verify.sh` | Provar que os princípios foram respeitados, não só declarados |
| 8 | Reportar | `assets/setup/8-report.md` | Entregar o que o usuário precisa saber para começar |

---

## Templates de formato estrito

> ⚠️ **O comentário de cabeçalho do molde NÃO viaja para o arquivo final.** Todo
> `_TEMPLATE` abre com um bloco `<!-- ... -->` de instruções para você — ele contém
> `[PLACEHOLDER]` e some no arquivo gerado. Copiar o cabeçalho junto reprova no
> verificador do Passo 7 ("Variáveis de template não substituídas") e, pior, deixa
> instrução de bootstrap dentro da documentação do projeto.
>
> Regra: leia o comentário, aplique o que ele manda, **descarte-o**. O arquivo final
> começa no primeiro `#` ou no primeiro campo de dado.

Não improvise a estrutura destes arquivos — cada um tem molde:

| Gera | Molde |
|---|---|
| `AGENTS.md` | `assets/tools/_TEMPLATE-AGENTS.md` |
| `.context/arch/overview.md` | `assets/context/arch/_TEMPLATE-overview.md` |
| `.context/arch/modules.yaml` | `assets/context/arch/_TEMPLATE-modules.yaml` |
| `.context/arch/rules.md` | `assets/context/arch/_TEMPLATE-rules.md` |
| `.context/arch/gates.md` | `assets/context/arch/_TEMPLATE-gates.md` |
| `.context/arch/flows.md` | `assets/context/arch/_TEMPLATE-flows.md` |
| `.context/work/<feature>.md` | `assets/context/work/_TEMPLATE.md` |
| `.context/arch/decisions/*.md` | `assets/context/decisions/_TEMPLATE.md` |
| `.claude/agents/*.md` | `assets/agents/{PLANNER,BUILDER,REVIEWER}.md` |
| `.codex/config.toml` | `assets/tools/codex-config.toml` — copie/mescle quando Codex foi selecionado |
| `.codex/agents/*.toml` | `assets/agents/codex/{planner,builder,reviewer}.toml` |
| `.context/formats/plan.md` | `assets/formats/plan.md` — copie como está |
| `.context/formats/response.md` | `assets/formats/response.md` — copie como está |
| `.context/PREVEC.md` | `assets/PREVEC.md` — copie como está. É a definição canônica da metodologia e do T.A.C.E |

---

## O modelo, em uma tela

**O ciclo são as 6 letras do PREVEC**, distribuídas em 3 agents — nenhuma letra fica
órfã, nenhuma pertence a dois:

| Agent | Letras | Claude · Codex | Onde roda |
|---|---|---|---|
| PLANNER | **P**ré-Planning · **P**lanning | `opus` · `gpt-5.6/high` | Thread principal |
| BUILDER | **E**xecution | `sonnet` · `gpt-5.6-terra/medium` | Subagent, 1 por task |
| REVIEWER | **R**eview · **V**alidation · **C**onfirm | `sonnet` · `gpt-5.6/high` | Subagent, antes e depois do E |

Os comandos são atalhos para grupos de letras: `/plan` = **P·P·R** · `/build` = **E**
· `/ship` = **V·C**. Nome curto, letras intactas.

**Por que assim:** o T.A.C.E é a interface entre um modelo caro que pensa e um
barato que executa. Task com decisão pendente é falha de planejamento — e é o que
faz modelo barato alucinar.

**PLANNER padrão por ferramenta:** Claude seleciona o agent diretamente pela chave
`agent`. Codex não expõe `default_agent`; `.codex/config.toml` fixa o modelo da
thread principal e usa `developer_instructions` para assumir o PLANNER. Não invente
uma chave inexistente para simular essa seleção.

**Cerimônia proporcional:** XS não gera artefato; L gera spec, design e decisão
registrada. A escala regula os documentos em volta, **nunca os campos da task**.

---

## EXECUTE AGORA

Leia `assets/setup/0-detect.md` e comece.
