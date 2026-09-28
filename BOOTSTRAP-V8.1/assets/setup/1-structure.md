# Passo 1 — Estrutura e colas nativas

Sem hub proprietário. Cada ferramenta lê do lugar que ela já entende.

> **Trabalhe na raiz do projeto.** Defina o prefixo dos assets uma vez e use daqui
> para frente: `B=BOOTSTRAP-V8` (ou o nome real desta pasta).

## Criar

```bash
# Prefixo dos assets — DEFINA AQUI. Os passos 4 e 6 usam a mesma variável.
B=BOOTSTRAP-V8            # ou o nome real desta pasta, se você a renomeou

mkdir -p .context/arch .context/work .context/formats
# condicionais, conforme as respostas do Passo 0
mkdir -p .context/arch/decisions   # se decisões = sim
mkdir -p .context/design           # se design != não
```

## Claude Code

```bash
mkdir -p .claude/agents .claude/skills
cp $B/assets/tools/CLAUDE.md CLAUDE.md          # uma linha: @AGENTS.md
```

`settings.json` — **mescle, não sobrescreva**:

```bash
if [ ! -f .claude/settings.json ]; then
  cp $B/assets/tools/settings.json .claude/settings.json
else
  echo "existe: mesclar a chave \"agent\": \"PLANNER\" preservando o resto"
fi
```

## Codex — condicional

Lê `AGENTS.md` da raiz nativamente, carrega configuração de projeto em
`.codex/config.toml` e descobre agents TOML em `.codex/agents/`. Skills continuam
compartilhadas por symlink:

```bash
mkdir -p .codex/agents
ln -sfn ../.claude/skills .codex/skills

if [ ! -f .codex/config.toml ]; then
  cp $B/assets/tools/codex-config.toml .codex/config.toml
else
  echo "existe: mesclar model, model_reasoning_effort, developer_instructions e [agents] preservando o resto"
fi
```

O `developer_instructions` do template torna PLANNER o comportamento padrão da
thread principal. Isso é intencional: Codex não possui uma chave `default_agent`
equivalente à chave `agent` do Claude. Não substitua por configuração inventada.

## opencode — condicional

Lê `AGENTS.md` **e** `.claude/skills/` nativamente. Só precisa do config, para
mapear os agents (o corpo fica no arquivo do Claude, sem cópia):

```bash
cp $B/assets/tools/opencode.json opencode.json   # mesclar se já existir
```

## Por que não há hub próprio

| Artefato | Claude Code | Codex | opencode |
|---|---|---|---|
| Contrato | `CLAUDE.md` → `@AGENTS.md` | `AGENTS.md` nativo | `AGENTS.md` nativo |
| Skills | `.claude/skills/` nativo | `.codex/skills` → symlink | `.claude/skills/` **nativo** |
| Agents | `.claude/agents/*.md` | `.codex/agents/*.toml` | `opencode.json` → `{file:...}` |

Uma fonte de skills atende duas das três ferramentas sem cola nenhuma. Sobra um
symlink só, o do Codex.

> **Limitação a documentar no `AGENTS.md`:** em checkout Windows sem
> `core.symlinks=true`, `.codex/skills` não resolve. A alternativa é copiar — ao
> custo de voltar a ter duas fontes, o que este bootstrap existe para evitar.

## .gitignore

O work file **é versionado** — é o registro da feature em andamento, e o `/ship`
o remove no fecho. Se quiser rascunho fora do git, acrescente a linha abaixo ao
`.gitignore` — criando o arquivo se ele não existir:

```
.context/work/*.local.md
```

Não ignore `.claude/` — é ali que suas skills e agents ficam versionados.

➡️ Próximo: `assets/setup/2-arch.md`
