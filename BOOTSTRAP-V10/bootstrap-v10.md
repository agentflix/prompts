# PREVEC V10 — setup

Você vai instalar o PREVEC V10 no projeto aberto. Trabalhe na raiz do projeto. Neste roteiro, `$B` é o caminho absoluto desta pasta. O shell do agente não guarda variável entre comandos, então escreva o caminho completo, entre aspas, em cada comando.

O objetivo é pouco contexto fixo, regra que carrega só quando importa, verificação feita por máquina e plano bom o bastante para a execução não decidir nada. Ao escrever cada linha, faça duas perguntas:

1. Esta linha muda o que o agente faz?
2. Ele descobriria isso sozinho lendo o código?

Fica só o que responde sim à primeira e não à segunda.

## 1. Detectar

Leia antes de perguntar. Descubra no código, com arquivo de origem:

- Stack, gerenciador de pacotes e deployables.
- Comandos reais de typecheck, lint, teste de um arquivo, suíte completa, build e formatter, tirados de `package.json`, `composer.json`, `Makefile`, `pyproject.toml` ou do CI. Para o `GATE_FAST`, prefira o comando que roda só os testes afetados, com `{changed}` (veja os exemplos no `gates.conf`). Rode o candidato uma vez para confirmar que existe e quanto demora. O alvo é menos de 30 segundos. Se a suíte toda já passa disso, o `GATE_FAST` não roda a suíte toda. Anote também quanto demora o `GATE_FULL` e os comandos que rodam a suíte inteira (vão para `TQ_MATCH`) e o comando de teste de um arquivo (o planejador usa no campo E).
- Pasta de migrations, padrões de arquivo de teste e arquivos sensíveis (`.env*`, chaves, lockfiles).
- Se há API, banco ou UI. Para cada um, procure o padrão existente com `arquivo:linha`: envelope de resposta, middleware de autenticação, coluna ou policy de dono, componente de notificação, tokens de tema.
- Áreas de risco: migrations, contrato público, autenticação, pagamento, dado de cliente.
- O que já existe de IA:
  - `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.codex/`, `opencode.json`, `.context/`;
  - se existir `.context/PREVEC.md` ou `.claude/agents/PLANNER.md`, o projeto está no V8; se existir `.context/specs/` ou `.claude/skills/spec`, está no V9. Qualquer `.context/` ou doc de IA existente passa pela seção 2.

Depois, pergunte com a ferramenta de pergunta da CLI (no Claude Code, `AskUserQuestion`): opções clicáveis, a recomendada primeiro e marcada como recomendada. Até 4 perguntas por chamada e de 2 a 4 opções por pergunta. O normal são duas chamadas; a terceira só se o usuário quiser escolher item a item. Texto solto só se a ferramenta não existir.

Primeira chamada:
1. **Ferramentas** (múltipla escolha): Claude Code, Codex, OpenCode. Recomende as que já têm pasta no projeto, mais o Claude Code.
2. **Postura do agente:**
   - `conservador`, para empresa e produção (recomendado se houver CI, várias pessoas no git ou dado de cliente);
   - `equilibrado`;
   - `criativo`, para projeto pessoal e exploração.
3. **Áreas de risco** (múltipla escolha), com estas 4 opções e as detectadas já recomendadas: "Migrations e banco", "Contrato público da API", "Autenticação e permissão", "Pagamento e dado de cliente". O usuário acrescenta outra pelo campo livre.
4. **Trava de escopo** (edição fora dos arquivos da task ativa do plano):
   - `avisar` (recomendado): passa, com aviso para o agente corrigir o plano ou desfazer;
   - `bloquear`: para modelos mais fracos ou projeto regulado;
   - `desligado`.

Segunda chamada: o pacote, mais os conflitos que você achou (só os que se aplicam, cada um com o caso concreto).
1. **Pacote.** Monte o pacote recomendado a partir da detecção e mostre-o na descrição da opção, em uma linha: proteções (gate no fim do turno, guard, fila de testes se há suíte, formatter se o projeto tem um), statusline e notificação (com Claude Code), regras das áreas que o projeto tem, os 4 subagentes, `retomar` e `retro`, estilo de resposta `dev-claro`, e o `code-review-confiavel` só com postura conservadora ou contrato público. Opções:
   - "Instalar o pacote recomendado" (recomendado);
   - "Escolher item a item" (abre a terceira chamada).
2. **Statusline**, se o usuário já tem `statusLine` própria (em `~/.claude/settings.json` ou `$CLAUDE_CONFIG_DIR/settings.json`):
   - "Usar a do V10" (recomendado: pasta, branch, modelo, contexto e linhas, mais a tarefa atual vinda de hook, subagente com modelo, gate, fila e cache);
   - "Manter a minha".
3. **Estilo de resposta.** Opções:
   - "Claro em camadas (`dev-claro`)" (recomendado): primeiro o resultado em linguagem simples, o importante logo depois, o técnico curto no fim; "detalhe" pede a versão técnica;
   - "Curto (`curto`)": só enxuto;
   - "Manter o meu", quando o usuário já usa um plugin de saída curta (ex.: caveman). Mostre o nome do plugin.
   Com `dev-claro` e plugin de saída curta ativo, avise que os dois brigam e desligue o plugin só neste projeto, em `.claude/settings.json`: `"enabledPlugins": {"<plugin>@<marketplace>": false}` (o nome exato está no `enabledPlugins` do settings do usuário).
4. **Git**, se o `.gitignore` ignora `.claude/` ou `.agents/`: "Versionar o V10" (recomendado) ou "Manter ignorado".

Instruções que já existem (`CLAUDE.md` em subpastas, `.cursor/rules`, `.context/`) são decididas na seção 2, por grupo; não pergunte aqui. Nunca apague nem mova sem resposta.

Terceira chamada, só com "Escolher item a item". As quatro de múltipla escolha, com as recomendadas marcadas:
1. **Proteções:** "Gate no fim do turno", "Guard de arquivos protegidos", "Fila de testes pesados", "Formatter automático".
2. **Visibilidade** (só com Claude Code): "Statusline", "Notificação no desktop".
3. **Regras por área:** "Código e testes", "API", "Dados e migrations", "Interface".
4. **Subagentes e skills:** "Explorador e mecânico (Haiku)", "Executor (Sonnet)" e "Revisor (Opus)" juntos como uma opção, "Retomar e retro", "Code review com 8 revisores".

O que o usuário desmarcar não é copiado nem ligado no `settings.json`.

Dado que o código não responde e o usuário não sabe: deixe fora e registre como pendência no relatório. Não invente valor.

## 2. Migrar o contexto que já existe

Vale para qualquer `.context/` ou documentação de IA que já exista: V8, V7.1, outra ferramenta ou formato próprio. Faça antes de gerar, para que o passo 3 não mescle configuração velha (como `"agent": "PLANNER"`) nem sobrescreva conteúdo escrito à mão.

1. **Inventário.** Liste `.context/**`, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/`, `.cursor/rules/`, `.github/copilot-instructions.md` e `docs/` de arquitetura ou de IA, se existirem.
2. **Classifique cada arquivo** num destino do V10:

   | Conteúdo | Destino no V10 |
   |---|---|
   | Regra verificável (faça ou não faça) | `.claude/rules/<área>.md`, com `paths:`. Regra escrita à mão mantém a redação, exceto CAPS: troque a ênfase pelo motivo. Área que o wizard não ativou: crie o arquivo dessa área só com as regras migradas e avise o usuário |
   | Comando de build, teste ou lint | `.claude/hooks/gates.conf` |
   | Decisão com motivo (ADR) | `.context/decisions/NNNN-slug.md`, em sequência na ordem cronológica |
   | Plano ainda não iniciado | `.context/planos/NNNNN-<feature>.md`, `status: rascunho` |
   | Plano ou feature em andamento | `.context/work/NNNNN-<feature>.md` (um arquivo só) no formato da skill `plano`, numerado em sequência a partir de `00001` na ordem de início, com `status: em-execucao`: o que está feito vira task `✅`, o que falta vira task `⬜` com A, C e E. Rode `prevec.sh plano` nele |
   | Fato não óbvio (armadilha, convenção fora do padrão) | Seção "Não óbvio" do `AGENTS.md` |
   | Plano entregue que o usuário quer manter | `.context/done/NNNNN-<feature>.md`, como está, só renomeado com o número |
   | Visão geral, árvore de pastas, descrição da stack, metodologia, formato de resposta, changelog | Arquivo morto |

3. **Mostre a tabela preenchida** (arquivo, conteúdo, destino) e pergunte com a ferramenta de pergunta, por grupo. Para o arquivo morto:
   - mover para `.context/_arquivo/` (recomendado: é reversível, e nenhum arquivo do V10 aponta para essa pasta);
   - apagar, porque o git guarda o histórico;
   - manter onde está.
4. **Aplique** o que o usuário escolheu. Ao mover conteúdo, reescreva no formato do destino, sem CAPS e com o motivo de cada regra. Nada é apagado sem confirmação.

Mapa direto do V9:

| V9 | V10 |
|---|---|
| `.context/specs/<f>/` em andamento (`SPEC.md`, `features.json`, `work.md`) | Um arquivo `.context/work/NNNNN-<f>.md`, e a pasta sai: critérios viram **Pronto quando**, a seção Plano vira tasks T.A.C.E |
| `features.json` · `progress.md` | Saem. O estado mora no plano (marcado por hook a partir das tarefas nativas) |
| `.claude/skills/spec` | Sai. A skill `plano` cobre, com "testes primeiro" |
| `.claude/hooks/*` | Substitua pelos do V10 e mescle o `gates.conf`: as variáveis novas (`TQ_*`, `ESCOPO`, `RITMO_*`, `STATUS_TASK_MAX`) entram com o padrão; as antigas mantêm o valor |
| Modo `vibe/padrão/spec` no `AGENTS.md` | Seção "Tamanho decide o fluxo" do molde novo |

Mapa direto do V8:

| V8 | V10 |
|---|---|
| `.context/arch/rules.md` | Divida por área em `.claude/rules/{codigo,testes,api,dados,ui}.md`, com `paths:`. Regra escrita à mão vai junto e mantém a redação, exceto CAPS |
| `.context/arch/gates.md` | Os comandos vão para `.claude/hooks/gates.conf` |
| `.context/arch/decisions/` | `.context/decisions/` |
| `.context/work/<feature>.md` em andamento | Fica em `.context/work/`, renomeado para `NNNNN-<feature>.md`. As tasks T.A.C.E do V8 já estão quase no formato: ajuste o título (`### T1 — … · depende: … · estado: ⬜`) e troque `WHEN/SHALL` por `QUANDO/DEVE` só se quiser; o checador aceita os dois |
| `overview.md` · `modules.yaml` · `flows.md` | Fato não óbvio vai para "Não óbvio" do `AGENTS.md`. Restrição de import vira regra de lint se o usuário quiser. O resto sai |
| `.context/PREVEC.md` · `.context/formats/` | Saem. A metodologia fica neste bootstrap, não no projeto |
| `.claude/agents/{PLANNER,BUILDER,REVIEWER}.md` · `.codex/agents/*` | Saem. O revisor substitui o REVIEWER |
| `"agent": "PLANNER"` em `.claude/settings.json` · `developer_instructions` do PLANNER no Codex | Saem. O thread principal é o agente nativo |
| `.claude/skills/{plan,build,ship,gates,arch-*,design}` | Saem. `ship` é substituída pela nova. `arch-*` e `design` viraram `.claude/rules/` |
| `.codex/skills` (symlink) | Sai. O Codex lê `.agents/skills` |
| `opencode.json` com `agent` | Corrija para `agents`, ou remova se só apontava para os agents do V8 |
| `.context/work/done/` e features já entregues | `.context/done/` com número, ou arquivo morto (pergunte): o commit e o PR contam a história |

Antes de apagar qualquer arquivo, mostre a lista completa e espere o usuário confirmar. Arquivo com conteúdo escrito à mão que não cabe em nenhum destino: pergunte o que fazer.

## 3. Gerar

| Origem em `$B/assets` | Destino | Como |
|---|---|---|
| `project/AGENTS.md` | `AGENTS.md` | Preencha. Remova o comentário de molde. Ajuste o que cita item não instalado (lista abaixo da tabela). Cole na seção Postura o bloco de `skills/postura/references/<postura>.md`. De 40 a 60 linhas. Linha sem conteúdo real sai. Se já existe um `AGENTS.md`, aproveite dele só o que passa no filtro das duas perguntas do topo, e mostre ao usuário o que saiu |
| `project/CLAUDE.md` | `CLAUDE.md` | Se não existe, copie. Se existe sem `@AGENTS.md`: mova o conteúdo útil para o `AGENTS.md` (com o mesmo filtro), deixe no `CLAUDE.md` só o que é específico do Claude e ponha `@AGENTS.md` na primeira linha |
| `project/settings.json` | `.claude/settings.json` | Só com Claude Code. Remova do molde os hooks e a `statusLine` que o usuário desmarcou no wizard. Se já existe, mescle chave a chave. Em `permissions.deny` e `ask`, una as listas sem repetir. Em `hooks`, acrescente cada evento só se nenhum hook dele já chama o mesmo script; hook duplicado roda duas vezes. Acrescente ao `deny` o cliente de banco do projeto (`Bash(psql *)`, `Bash(supabase db execute *)`…) quando houver banco. Postura `conservador`: acrescente ao `ask` o comando de instalar dependência do projeto. Estilo de resposta: `"outputStyle": "dev-claro"` ou `"curto"`; com "manter o meu", sem `outputStyle`. A `statusLine` do projeto substitui a do usuário. A do V10 traz na primeira linha pasta, branch, modelo, janela de contexto e linhas da sessão, e na segunda a tarefa atual (gravada por hook), o subagente ativo, gate, fila e cache. Se o usuário tem `statusLine` própria (procure em `~/.claude/settings.json` ou em `$CLAUDE_CONFIG_DIR/settings.json`), mostre as duas e pergunte qual fica |
| `output-styles/dev-claro.md` ou `output-styles/curto.md` | `.claude/output-styles/` | O estilo escolhido, com qualquer ferramenta: é a fonte única do formato de resposta. O Claude Code lê pelo `outputStyle`, o OpenCode pelo `instructions` e o Codex pelo `developer_instructions`. Não copie o formato para o `AGENTS.md`: ele é lido pelas três ferramentas e duplicaria tokens. Com `dev-claro`, apague a linha "Termine com o que mudou…" da seção Entrega do `AGENTS.md` |
| `hooks/*` | `.claude/hooks/` | Copie `_lib.sh`, `gates.conf`, `prevec.sh` e `prevec.py` (estado para a statusline, ritmo, escopo, rótulo de subagente, registro de comandos e checagem de plano; sempre) e o script de cada item ativado no wizard: `gate.sh`, `guard.sh`, `format.sh`, `fila.sh` com `tq.sh` e `tq.py`, `statusline.sh` com `statusline.py`, e `notify.sh`. Statusline e notify só com Claude Code. Rode `chmod +x .claude/hooks/*.sh .claude/hooks/*.py`. Preencha todas as variáveis do `gates.conf`: comandos confirmados, `TQ_MATCH` com os comandos de suíte inteira do projeto, `ESCOPO` do wizard e os padrões `PROTECTED`, `MIGRATIONS` e `TESTS` reais. Passo inexistente fica com string vazia (`""`), nunca com o `<ex.: …>`. Rode cada comando de gate uma vez antes de seguir: o que falha por configuração (limite de memória do PHPStan, flag de CI, variável de ambiente) se corrige no próprio comando ou na config da ferramenta (`--memory-limit=1G`), senão cada executor descobre sozinho. Falha de código que já existia: registre e avise o usuário, sem corrigir. Sem fila: `TQ_ON=0` e tire o `fila.sh` do settings |
| `rules/codigo.md` | `.claude/rules/codigo.md` | Conforme o wizard. Remova o comentário de molde, como em toda regra. `paths:` com as extensões do código-fonte. Em C1, o reforço é o lint se o projeto já tem `no-explicit-any` (ou equivalente) ligado; senão, `revisão` |
| `rules/testes.md` | `.claude/rules/testes.md` | Junto com "Código e testes", se o projeto tem testes. Remova o comentário de molde. `paths:` com os padrões de arquivo de teste. Ajuste os exemplos de fronteira de mock ao projeto |
| `rules/api.md` · `dados.md` · `ui.md` | `.claude/rules/` | Conforme o wizard. Remova o comentário de molde. `paths:` com as pastas reais. Cada `<...>` vira `arquivo:linha` ou "ainda não existe" |
| `skills/plano` · `skills/executar` · `skills/ship` · `skills/postura` | `.claude/skills/` | Copie. No `plano`, ajuste o exemplo de comando de teste de um arquivo do `references/plano.template.md` ao do projeto |
| `skills/retomar` · `skills/retro` · `skills/code-review-confiavel` | `.claude/skills/` | Conforme o wizard |
| `agents/{explorador,mecanico,executor,revisor}.md` | `.claude/agents/` | Conforme o wizard, com qualquer ferramenta: é a especificação que os agentes do Codex e do OpenCode leem. Sem revisor, o `ship` usa `/code-review`. Ajuste a seção Orquestração do `AGENTS.md` e a tabela da skill `delegar` aos agentes instalados |
| `skills/delegar` | `.claude/skills/delegar` | Sempre que houver ao menos um subagente instalado |
| `context/decision.template.md` | `.context/decisions/_TEMPLATE.md` | Copie. Crie também `.context/planos/`, `.context/work/` e `.context/done/` vazias, com `.gitkeep` |
| `codex/config.toml` · `codex/hooks.json` · `agents/codex/*.toml` | `.codex/config.toml` · `.codex/hooks.json` · `.codex/agents/` | Só com Codex, e só os agentes escolhidos. Preencha o `model` de cada agente com o modelo rápido e o de uso geral que a doc atual do Codex recomenda para subagentes; sem certeza, deixe sem a linha, e o agente herda o modelo da sessão. Skills: veja "Skills que o projeto já tem" abaixo da tabela. Saída `normal`: apague `model_verbosity`. Estilo `dev-claro`: cole em `developer_instructions` o corpo de `.claude/output-styles/dev-claro.md`, sem o frontmatter; outro estilo: apague o bloco |
| `agents/opencode/*.md` | `.opencode/agents/` | Só com OpenCode, e só os agentes escolhidos. Confira na doc atual se os IDs `anthropic/claude-*-5-5#effort` ainda valem. O OpenCode V2 já lê `AGENTS.md` e `.claude/skills` sozinho. Não crie `opencode.json` sem necessidade |
| `opencode/opencode.json` | `opencode.json` | Só com OpenCode e estilo `dev-claro`: aponta `instructions` para `.claude/output-styles/dev-claro.md`. Se já existe, acrescente o caminho à lista `instructions` |

Ajustes no `AGENTS.md` conforme o que não foi instalado:
- sem gate: na seção "Testes e verificação", tire a frase "No Claude Code e no Codex o hook roda o `GATE_FAST` no fim do turno" e escreva "Rode o `GATE_FAST` antes de encerrar um turno com mudança";
- sem fila: tire a frase da fila e o comando do `tq.sh`;
- sem `revisor`: na lista "Delegue" e na linha de área de risco, troque `revisor` por `/code-review` (Claude Code) ou `/review` (Codex);
- sem subagentes: a seção Orquestração vira uma linha ("Faça você mesmo; leitura grande vai para o Explore embutido");
- sem `testes.md`, sai a linha que manda lê-lo;
- regra de área ausente sai da lista.

Skills que o projeto já tem:
- **Pasta real em `.agents/skills`** (gerenciada por `npx skills`, com `skills-lock.json`) **e symlinks em `.claude/skills`:** não troque essa estrutura. Copie as skills do V10 como pastas reais em `.claude/skills/<nome>`. Com Codex, crie um symlink por skill em `.agents/skills/<nome>` apontando para `../../.claude/skills/<nome>`, em vez de substituir a pasta.
- **`.agents/skills` não existe e há Codex:** `mkdir -p .agents && ln -sfn ../.claude/skills .agents/skills`.

`.gitignore` que ignora `.claude/` ou `.agents/` inteiros: o V10 só funciona para quem clonar se for versionado. Pergunte (segunda chamada do wizard) e, se a resposta for versionar, acrescente as exceções sem tirar o que já está ignorado:

```
!.claude/
.claude/*
!.claude/settings.json
!.claude/hooks/
!.claude/rules/
!.claude/agents/
!.claude/output-styles/
!.claude/skills/
.claude/skills/*
!.claude/skills/<cada skill do V10>/
```

Crie as pastas antes de copiar: `mkdir -p .claude/hooks .claude/rules .claude/skills .claude/agents .claude/output-styles .context/decisions .context/planos .context/work .context/done`, mais `.codex/agents` e `.opencode/agents` conforme as ferramentas.

Lista de tarefas nativa, para mostrar o andamento de trabalho longo:
- **Claude Code:** já vem pronta, a lista de tarefas nativa mais o hook de status e a statusline do V10.
- **Codex e OpenCode:** a forma de ligar muda entre versões. Antes de configurar, consulte a doc atual da versão instalada, pelo Context7 ou pela doc oficial (learn.chatgpt.com/docs e opencode.ai/docs). Descubra:
  1. qual ferramenta nativa de plano ou tarefas existe: no Codex, o plano da sessão; no OpenCode, o `todowrite`, que pode precisar de flag;
  2. se precisa ser ativada na config;
  3. se há statusline ou equivalente.

  Configure o que existir e registre no relatório o que você achou, com a URL. A skill `executar` já manda criar uma tarefa nativa por task do plano. Nessas ferramentas não há hook de status: a tarefa atual não aparece sozinha, e o estado no plano depende do agente marcar.

Alcance dos hooks por ferramenta. Diga isso no relatório, sem prometer mais:
- No Claude Code, os hooks valem para Edit e Write, e o `deny` vale para Read e Bash.
- No Codex, guard e escopo valem só para `apply_patch`; edição feita por Bash (`sed -i`) passa. A fila precisa do nome da tool de shell no `matcher` do `.codex/hooks.json`: confira na doc atual e troque o placeholder; sem certeza, apague esse bloco e deixe a fila só no `AGENTS.md`. Status e ritmo são só do Claude Code.
- O OpenCode fica sem hooks. Lá o gate, a fila e as proteções dependem do `AGENTS.md`.

Adicione ao `.gitignore`: `.claude/hooks/tests.lock`, `.claude/hooks/gate.pause`, `.claude/settings.local.json` e `.context/done/` se o time não quer versionar plano entregue. São estado da sua máquina, não do projeto.

`.claude/` é a pasta canônica de hooks, regras e skills, mesmo sem o Claude Code. Sem ele, não gere `CLAUDE.md`, `settings.json`, statusline nem output style.

Com Codex e OpenCode juntos, o OpenCode lê `.claude/skills` e também `.agents/skills`, que é o symlink do Codex, e veria as skills duas vezes. Consulte na doc atual do OpenCode como limitar as pastas de skills. Se não houver opção, avise o usuário.

Regra que dá para garantir por máquina não fica só no texto. Se o projeto tem linter, proponha ligar `no-explicit-any` (ou o equivalente da stack) e, se o usuário aceitar, encurte a regra C1 para citar o linter.

## 4. Verificar e relatar

1. Rode `bash "<caminho absoluto desta pasta>/assets/doctor.sh"` na raiz e corrija toda FALHA.
2. Teste o gate. Com `GATE_FAST` preenchido:
   - primeiro, rode o comando do `GATE_FAST` direto no shell, trocando `{changed}` por um arquivo de código do projeto. Ele precisa passar;
   - o hook só faz sentido com a instalação commitada: os arquivos novos do kit entrariam no `{changed}`. Se o usuário ainda não quer commitar, pule os próximos passos e registre a pendência;
   - faça uma mudança inofensiva num arquivo de código;
   - rode `echo '{}' | .claude/hooks/gate.sh; echo "exit $?"`;
   - confirme que o gate rodou de verdade: `test -f "$(git rev-parse --git-path prevec/gate-ok)"` só passa se o `GATE_FAST` executou e ficou verde;
   - desfaça a mudança.
   Se só uma parte do gate está vermelha antes de qualquer mudança (um alvo de teste entre vários), monte o `GATE_FAST` só com as partes verdes e registre a vermelha como pendência, com o comando e o número de falhas. Se tudo está vermelho, ponha `GATE_ON_STOP=0` no `gates.conf` e registre como pendência. Assim o hook não prende o agente consertando código que não é dele. Religue quando o gate ficar verde.
3. Teste o guard: `echo '{"tool_input":{"file_path":".env"}}' | .claude/hooks/guard.sh; echo "exit $?"` deve sair com 2.
4. Teste a fila, se instalada: `echo '{"tool_input":{"command":"<um comando de TQ_MATCH>"}}' | .claude/hooks/fila.sh; echo "exit $?"` deve imprimir um JSON com `updatedInput` cujo `command` começa pelo caminho do `tq.sh`; `.claude/hooks/tq.sh 'echo ok'` deve imprimir `ok`.
5. Teste o checador de plano: `.claude/hooks/prevec.sh plano .claude/skills/plano/references/plano.template.md` deve listar problemas (o molde tem placeholders); isso prova que ele roda.

Relate em até 15 linhas:
- o que foi detectado;
- o que foi gerado;
- o custo fixo estimado que o doctor mostrou;
- as pendências (dado que ninguém soube responder);
- o que o usuário precisa fazer: no Codex, abrir `/hooks` e confiar nos hooks; no Claude Code, `/hooks` mostra o que está ligado.

Termine com três exemplos de pedido: um pontual ("corrige X": faz direto), um médio ("implementa Y": plano e executar) e um com testes primeiro.
