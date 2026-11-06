# PREVEC V9 — setup

Você vai instalar o PREVEC V9 no projeto aberto. Trabalhe na raiz do projeto. Neste roteiro, `$B` é o caminho absoluto desta pasta. O shell do agente não guarda variável entre comandos, então escreva o caminho completo, entre aspas, em cada comando.

O objetivo é pouco contexto fixo, regra que carrega só quando importa e verificação feita por máquina. Ao escrever cada linha, faça duas perguntas:

1. Esta linha muda o que o agente faz?
2. Ele descobriria isso sozinho lendo o código?

Fica só o que responde sim à primeira e não à segunda.

## 1. Detectar

Leia antes de perguntar. Descubra no código, com arquivo de origem:

- Stack, gerenciador de pacotes e deployables.
- Comandos reais de typecheck, lint, teste de um arquivo, suíte completa, build e formatter, tirados de `package.json`, `composer.json`, `Makefile`, `pyproject.toml` ou do CI. Para o `GATE_FAST`, prefira o comando que roda só os testes afetados, com `{changed}` (veja os exemplos no `gates.conf`). Rode o candidato uma vez para confirmar que existe e quanto demora. O alvo é menos de 30 segundos. Se a suíte toda já passa disso, o `GATE_FAST` não roda a suíte toda.
- Pasta de migrations, padrões de arquivo de teste e arquivos sensíveis (`.env*`, chaves, lockfiles).
- Se há API, banco ou UI. Para cada um, procure o padrão existente com `arquivo:linha`: envelope de resposta, middleware de autenticação, coluna ou policy de dono, componente de notificação, tokens de tema.
- Áreas de risco: migrations, contrato público, autenticação, pagamento, dado de cliente.
- O que já existe de IA:
  - `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.codex/`, `opencode.json`, `.context/`;
  - se existir `.context/PREVEC.md` ou `.claude/agents/PLANNER.md`, o projeto está no V8; qualquer `.context/` ou doc de IA existente passa pela seção 2.

Depois, pergunte com a ferramenta de pergunta da CLI (no Claude Code, `AskUserQuestion`): opções clicáveis, a recomendada primeiro e marcada como recomendada. Ela aceita até 4 perguntas por chamada e de 2 a 4 opções por pergunta, então o wizard tem até quatro chamadas. Texto solto só se a ferramenta não existir.

Primeira chamada:
1. **Ferramentas** (múltipla escolha): Claude Code, Codex, OpenCode. Recomende as que já têm pasta no projeto, mais o Claude Code.
2. **Modo padrão:**
   - `padrão`, para o dia a dia (recomendado);
   - `vibe`, para protótipo;
   - `spec`, para projeto regulado, equipe grande ou contrato público.
3. **Postura do agente:**
   - `conservador`, para empresa e produção (recomendado se houver CI, várias pessoas no git ou dado de cliente);
   - `equilibrado`;
   - `criativo`, para projeto pessoal e exploração.
4. **Saída:** `curta` (recomendado) ou `normal`.

Segunda chamada:
1. **Áreas de risco** (múltipla escolha), com estas 4 opções e as detectadas já recomendadas: "Migrations e banco", "Contrato público da API", "Autenticação e permissão", "Pagamento e dado de cliente". O usuário acrescenta outra pelo campo livre.
2. **Skills de trabalho longo** (`/retomar` e `/retro`): `instalar` (recomendado) ou `não instalar`.

Terceira chamada: o que ativar. As quatro perguntas são de múltipla escolha e vêm com as opções recomendadas marcadas como recomendadas.
1. **Proteções:** "Gate no fim do turno", "Guard de arquivos protegidos", "Formatter automático". Recomende as três, e o formatter só se o projeto tem um.
2. **Visibilidade** (só com Claude Code): "Statusline (branch, contexto, tarefa, gate, cache)", "Notificação no desktop". Recomende as duas.
3. **Regras por área:** "Código e testes", "API", "Dados e migrations", "Interface". Recomende só as áreas que o projeto tem.
4. **Subagentes** (cada um com modelo fixo, que o orquestrador escolhe ao delegar):
   - "Explorador e mecânico, em Haiku" (recomendado);
   - "Executor, em Sonnet" (recomendado);
   - "Revisor, em Opus" (recomendado);
   - "Code review com 8 revisores" (recomendado com postura conservadora ou modo spec).

O que o usuário desmarcar não é copiado nem ligado no `settings.json`.

Quarta chamada: conflitos com o que já existe. Faça só as perguntas que se aplicam, cada uma com o caso concreto que você achou:
1. **Statusline:** o usuário já tem `statusLine` própria (em `~/.claude/settings.json` ou `$CLAUDE_CONFIG_DIR/settings.json`). Opções:
   - "Usar a do V9" (recomendado, porque traz branch, modelo, contexto e linhas, mais tarefa, gate e cache);
   - "Manter a minha".
2. **Saída curta:** o usuário já usa um plugin de saída curta (ex.: caveman). Opções:
   - "Manter o meu" (recomendado);
   - "Usar o `curto` do V9".
3. **Instruções que já existem** (`CLAUDE.md` na raiz ou em subpastas, `.cursor/rules`). Opções:
   - "Manter onde estão" (recomendado se forem específicas de uma subpasta);
   - "Migrar para o formato V9" (seção 2).

   Nunca apague nem mova sem essa resposta.
4. **Git:** o `.gitignore` ignora `.claude/` ou `.agents/`. Opções:
   - "Versionar o V9" (recomendado);
   - "Manter ignorado".

Dado que o código não responde e o usuário não sabe: deixe fora e registre como pendência no relatório. Não invente valor.

## 2. Migrar o contexto que já existe

Vale para qualquer `.context/` ou documentação de IA que já exista: V8, V7.1, outra ferramenta ou formato próprio. Faça antes de gerar, para que o passo 3 não mescle configuração velha (como `"agent": "PLANNER"`) nem sobrescreva conteúdo escrito à mão.

1. **Inventário.** Liste `.context/**`, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/`, `.cursor/rules/`, `.github/copilot-instructions.md` e `docs/` de arquitetura ou de IA, se existirem.
2. **Classifique cada arquivo** num destino do V9:

   | Conteúdo | Destino no V9 |
   |---|---|
   | Regra verificável (faça ou não faça) | `.claude/rules/<área>.md`, com `paths:`. Regra escrita à mão mantém a redação, exceto CAPS: troque a ênfase pelo motivo. Área que o wizard não ativou: crie o arquivo dessa área só com as regras migradas e avise o usuário |
   | Comando de build, teste ou lint | `.claude/hooks/gates.conf` |
   | Decisão com motivo (ADR) | `.context/decisions/NNNN-slug.md`, em sequência na ordem cronológica |
   | Plano ou feature em andamento | `.context/specs/<feature>/SPEC.md` com `status: em-implementacao`. Pendências viram a seção Plano e também o `features.json` (um item por pendência, `"passa": false`), para que `/retomar` e a statusline enxerguem a feature |
   | Fato não óbvio (armadilha, convenção fora do padrão) | Seção "Não óbvio" do `AGENTS.md` |
   | Visão geral, árvore de pastas, descrição da stack, metodologia, formato de resposta, plano concluído, changelog | Arquivo morto |

3. **Mostre a tabela preenchida** (arquivo, conteúdo, destino) e pergunte com a ferramenta de pergunta, por grupo. Para o arquivo morto:
   - mover para `.context/_arquivo/` (recomendado: é reversível, e nenhum arquivo do V9 aponta para essa pasta);
   - apagar, porque o git guarda o histórico;
   - manter onde está.
4. **Aplique** o que o usuário escolheu. Ao mover conteúdo, reescreva no formato do destino, sem CAPS e com o motivo de cada regra. Nada é apagado sem confirmação.

Mapa direto do V8:

| V8 | V9 |
|---|---|
| `.context/arch/rules.md` | Divida por área em `.claude/rules/{codigo,testes,api,dados,ui}.md`, com `paths:`. Regra escrita à mão vai junto e mantém a redação, exceto CAPS |
| `.context/arch/gates.md` | Os comandos vão para `.claude/hooks/gates.conf` |
| `.context/arch/decisions/` | `.context/decisions/` |
| `.context/work/<feature>.md` em andamento | Como na tabela de cima: `SPEC.md` com `status: em-implementacao` mais `features.json` com as tasks pendentes |
| `overview.md` · `modules.yaml` · `flows.md` | Fato não óbvio vai para "Não óbvio" do `AGENTS.md`. Restrição de import vira regra de lint se o usuário quiser. O resto sai |
| `.context/PREVEC.md` · `.context/formats/` | Saem. A metodologia fica neste bootstrap, não no projeto |
| `.claude/agents/{PLANNER,BUILDER,REVIEWER}.md` · `.codex/agents/*` | Saem. O revisor substitui o REVIEWER |
| `"agent": "PLANNER"` em `.claude/settings.json` · `developer_instructions` do PLANNER no Codex | Saem. O thread principal é o agente nativo |
| `.claude/skills/{plan,build,ship,gates,arch-*,design}` | Saem. `ship` é substituída pela nova. `arch-*` e `design` viraram `.claude/rules/` |
| `.codex/skills` (symlink) | Sai. O Codex lê `.agents/skills` |
| `opencode.json` com `agent` | Corrija para `agents`, ou remova se só apontava para os agents do V8 |
| `.context/work/` de features já entregues | Arquivo morto: o commit e o PR contam a história |

Antes de apagar qualquer arquivo, mostre a lista completa e espere o usuário confirmar. Arquivo com conteúdo escrito à mão que não cabe em nenhum destino: pergunte o que fazer.

## 3. Gerar

| Origem em `$B/assets` | Destino | Como |
|---|---|---|
| `project/AGENTS.md` | `AGENTS.md` | Preencha. Remova o comentário de molde. Ajuste o que cita item não instalado (lista abaixo da tabela). Cole na seção Postura o bloco de `skills/postura/references/<postura>.md`. De 40 a 60 linhas. Linha sem conteúdo real sai. Se já existe um `AGENTS.md`, aproveite dele só o que passa no filtro das duas perguntas do topo, e mostre ao usuário o que saiu |
| `project/CLAUDE.md` | `CLAUDE.md` | Se não existe, copie. Se existe sem `@AGENTS.md`: mova o conteúdo útil para o `AGENTS.md` (com o mesmo filtro), deixe no `CLAUDE.md` só o que é específico do Claude e ponha `@AGENTS.md` na primeira linha |
| `project/settings.json` | `.claude/settings.json` | Só com Claude Code. Remova do molde os hooks e a `statusLine` que o usuário desmarcou no wizard. Se já existe, mescle chave a chave. Em `permissions.deny` e `ask`, una as listas sem repetir. Em `hooks`, acrescente cada evento só se nenhum hook dele já chama o mesmo script; hook duplicado roda duas vezes. Acrescente ao `deny` o cliente de banco do projeto (`Bash(psql *)`, `Bash(supabase db execute *)`…) quando houver banco. Postura `conservador`: acrescente ao `ask` o comando de instalar dependência do projeto. Saída `curta`: `"outputStyle": "curto"`. A `statusLine` do projeto substitui a do usuário. A do V9 já traz na primeira linha branch, modelo, janela de contexto e linhas da sessão, e na segunda tarefa, gate e cache. Se o usuário tem `statusLine` própria (procure em `~/.claude/settings.json` ou em `$CLAUDE_CONFIG_DIR/settings.json`), mostre as duas e pergunte qual fica |
| `output-styles/curto.md` | `.claude/output-styles/curto.md` | Só com saída `curta`. Se o usuário já usa um plugin de saída curta (ex.: caveman), pergunte se fica o dele ou este |
| `hooks/*` | `.claude/hooks/` | Copie `_lib.sh`, `gates.conf` e o script de cada item ativado no wizard: `gate.sh`, `guard.sh`, `format.sh`, e `statusline.sh` com `statusline.py`, e `notify.sh`. Statusline e notify só com Claude Code. Rode `chmod +x .claude/hooks/*.sh`. Preencha todas as variáveis do `gates.conf`: comandos confirmados e os padrões `PROTECTED`, `MIGRATIONS` e `TESTS` reais. Passo inexistente fica com string vazia (`""`), nunca com o `<ex.: …>` |
| `rules/codigo.md` | `.claude/rules/codigo.md` | Conforme o wizard. Remova o comentário de molde, como em toda regra. `paths:` com as extensões do código-fonte. Em C1, o reforço é o lint se o projeto já tem `no-explicit-any` (ou equivalente) ligado; senão, `revisão` |
| `rules/testes.md` | `.claude/rules/testes.md` | Junto com "Código e testes", se o projeto tem testes. Remova o comentário de molde. `paths:` com os padrões de arquivo de teste. Ajuste os exemplos de fronteira de mock ao projeto |
| `rules/api.md` · `dados.md` · `ui.md` | `.claude/rules/` | Conforme o wizard. Remova o comentário de molde. `paths:` com as pastas reais. Cada `<...>` vira `arquivo:linha` ou "ainda não existe" |
| `skills/spec` · `skills/ship` · `skills/postura` | `.claude/skills/` | Copie |
| `skills/retomar` · `skills/retro` · `skills/code-review-confiavel` | `.claude/skills/` | Conforme o wizard |
| `agents/{explorador,mecanico,executor,revisor}.md` | `.claude/agents/` | Conforme o wizard, com qualquer ferramenta: é a especificação que os agentes do Codex e do OpenCode leem. Sem revisor, o `ship` usa `/code-review`. Ajuste a seção Orquestração do `AGENTS.md` e a tabela da skill `delegar` aos agentes instalados |
| `skills/delegar` | `.claude/skills/delegar` | Sempre que houver ao menos um subagente instalado |
| `context/decision.template.md` | `.context/decisions/_TEMPLATE.md` | Copie. Crie também `.context/specs/` vazio, com `.gitkeep` |
| `codex/config.toml` · `codex/hooks.json` · `agents/codex/*.toml` | `.codex/config.toml` · `.codex/hooks.json` · `.codex/agents/` | Só com Codex, e só os agentes escolhidos. Preencha o `model` de cada agente com o modelo rápido e o de uso geral que a doc atual do Codex recomenda para subagentes; sem certeza, deixe sem a linha, e o agente herda o modelo da sessão. Skills: veja "Skills que o projeto já tem" abaixo da tabela. Saída `normal`: apague `model_verbosity` |
| `agents/opencode/*.md` | `.opencode/agents/` | Só com OpenCode, e só os agentes escolhidos. Confira na doc atual se os IDs `anthropic/claude-*-5-5#effort` ainda valem. O OpenCode V2 já lê `AGENTS.md` e `.claude/skills` sozinho. Não crie `opencode.json` sem necessidade |

Ajustes no `AGENTS.md` conforme o que não foi instalado:
- sem gate, a frase "No Claude Code e no Codex um hook já faz isso" sai;
- sem `revisor`, o modo padrão pede `/code-review`;
- sem `testes.md`, sai a linha que manda lê-lo;
- regra de área ausente sai da lista.

Skills que o projeto já tem:
- **Pasta real em `.agents/skills`** (gerenciada por `npx skills`, com `skills-lock.json`) **e symlinks em `.claude/skills`:** não troque essa estrutura. Copie as skills do V9 como pastas reais em `.claude/skills/<nome>`. Com Codex, crie um symlink por skill em `.agents/skills/<nome>` apontando para `../../.claude/skills/<nome>`, em vez de substituir a pasta.
- **`.agents/skills` não existe e há Codex:** `mkdir -p .agents && ln -sfn ../.claude/skills .agents/skills`.

`.gitignore` que ignora `.claude/` ou `.agents/` inteiros: o V9 só funciona para quem clonar se for versionado. Pergunte (veja a quarta chamada do wizard) e, se a resposta for versionar, acrescente as exceções sem tirar o que já está ignorado:

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
!.claude/skills/<cada skill do V9>/
```

Crie as pastas antes de copiar: `mkdir -p .claude/hooks .claude/rules .claude/skills .claude/agents .claude/output-styles .context/decisions .context/specs`, mais `.codex/agents` e `.opencode/agents` conforme as ferramentas.

Lista de tarefas nativa, para mostrar o andamento de trabalho longo:
- **Claude Code:** já vem pronta, a lista de tarefas nativa mais a statusline do V9.
- **Codex e OpenCode:** a forma de ligar muda entre versões. Antes de configurar, consulte a doc atual da versão instalada, pelo Context7 ou pela doc oficial (learn.chatgpt.com/docs e opencode.ai/docs). Descubra:
  1. qual ferramenta nativa de plano ou tarefas existe: no Codex, o plano da sessão; no OpenCode, o `todowrite`, que pode precisar de flag;
  2. se precisa ser ativada na config;
  3. se há statusline ou equivalente.

  Configure o que existir e registre no relatório o que você achou, com a URL. O `longa-duracao.md` da skill `spec` já manda espelhar o `features.json` nessa lista.

Alcance dos hooks por ferramenta. Diga isso no relatório, sem prometer mais:
- No Claude Code, os hooks valem para Edit e Write, e o `deny` vale para Read e Bash.
- No Codex, os hooks valem só para `apply_patch`. Edição feita por Bash (`sed -i`) passa.
- O OpenCode fica sem hooks. Lá o gate e as proteções dependem do `AGENTS.md`.

Adicione ao `.gitignore`: `.claude/hooks/tests.lock`, `.claude/hooks/gate.pause` e `.claude/settings.local.json`. São estado da sua máquina, não do projeto.

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

Relate em até 15 linhas:
- o que foi detectado;
- o que foi gerado;
- o custo fixo estimado que o doctor mostrou;
- as pendências (dado que ninguém soube responder);
- o que o usuário precisa fazer: no Codex, abrir `/hooks` e confiar nos três hooks; no Claude Code, `/hooks` mostra o que está ligado.

Termine com um exemplo de uso de cada modo.
