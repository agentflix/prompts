# 🔄 Sync Tools — Sincronizar para Ferramentas de IA

> **Fase 6 do INDEX.md**: Distribuir `.context/` para `.github/`, `.claude/`, `.gemini/`.

## Instruções para a IA

Leia `.context/` e distribua o conteúdo para cada pasta de ferramenta IA, respeitando os formatos oficiais de cada uma.

---

## 1. GitHub Copilot (`.github/`)

### Formato Oficial
- **`copilot-instructions.md`**: Instruções globais do repositório
- **`agents/*.agent.md`**: Agents com frontmatter YAML
- **`instructions/*.instructions.md`**: Instruções por path com `applyTo`

### O que gerar

#### `.github/copilot-instructions.md`
Gere a partir do `AGENTS.md`, adaptando para o formato Copilot:
- Resumo do projeto
- Stack e tecnologias
- Regras de codificação (phpDoc, jsDoc, sem any, strict_types)
- Caminhos de arquivos
- Gates de qualidade
- Referências para `.context/`

#### `.github/agents/*.agent.md`
Copie de `.context/agents/` os agents principais, mantendo o frontmatter YAML:

```yaml
---
type: agent
name: AGENT_NAME
description: Descrição
capabilities:
  - cap1
triggers:
  - trigger1
---
```

**Agents a copiar**: `orchestrator`, `dev`, `backend`, `frontend`, `dba`, `architect`, `reviewer`, `qa`, `debug`, `doc`, `pm`, `git-commit`

Nomeie como `UPPERCASE.agent.md`: `DEV.agent.md`, `DBA.agent.md`, etc.

#### `.github/instructions/` (por path)
Se o projeto tem múltiplas camadas (api, app, gateway), crie:

```yaml
# .github/instructions/backend.instructions.md
---
applyTo: "api/**"
---
# Backend Instructions
<!-- Regras específicas do backend extraídas de .context/ -->
```

```yaml
# .github/instructions/frontend.instructions.md
---
applyTo: "app/**"
---
# Frontend Instructions
<!-- Regras específicas do frontend extraídas de .context/ -->
```

---

## 2. Claude Code (`.claude/`)

### Formato Oficial
- **`CLAUDE.md`** na raiz (já feito na Fase 5 — symlink para `AGENTS.md`)
- **`settings.json`**: Configurações
- **`agents/*.md`**: Subagents (sem `.agent.md`, apenas `.md`)
- **`commands/*.md`**: Slash commands com frontmatter
- **`skills/*.md`**: Skills resumidas

### O que gerar

#### `.claude/settings.json`
```json
{
  "permissions": {
    "allow": [
      "Read()",
      "Bash(git *)",
      "Bash(cd * && composer *)",
      "Bash(cd * && npm *)",
      "Bash(cd * && pnpm *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ]
  }
}
```
Adapte os comandos permitidos para a stack real do projeto.

#### `.claude/agents/*.md`
Gere versões resumidas dos agents de `.context/agents/`, nomeadas em lowercase:
`dev.md`, `backend.md`, `frontend.md`, `reviewer.md`, `qa.md`, `debug.md`, `orchestrator.md`

Cada agent deve ter ~30-50 linhas com instruções concisas + referências para `.context/agents/`.

#### `.claude/commands/*.md`
Gere slash commands para operações comuns:

**`feature.md`** — `/project:feature`
```yaml
---
description: Criar nova feature full-stack
---
```

**`review.md`** — `/project:review`
```yaml
---
description: Executar code review com checklist
---
```

**`gates.md`** — `/project:gates`
```yaml
---
description: Executar gates de qualidade
---
```

**`fix-issue.md`** — `/project:fix-issue`
```yaml
---
description: Investigar e corrigir bug
---
```

**`doc.md`** — `/project:doc`
```yaml
---
description: Gerar documentação
---
```

#### `.claude/skills/*.md`
Gere versões resumidas (~50-80 linhas) das skills de `.context/skills/`, uma por framework principal:
Ex: `laravel-ddd.md`, `angular-signals.md`, `code-review.md`

---

## 3. Gemini / Antigravity (`.gemini/`)

### Formato Oficial
- **`GEMINI.md`** no diretório `.gemini/` ou na raiz
- Suporta cascata: global → projeto → subdiretório
- **Skills** no formato `SKILL.md` em subpastas

### O que gerar

#### `.gemini/GEMINI.md`
Gere a partir do `AGENTS.md` e `.context/`, adaptando:

```markdown
# {NomeProjeto} — Gemini Instructions

## Project Overview
<!-- Breve descrição do projeto -->

## Stack
<!-- Tabela de tecnologias -->

## Coding Rules
<!-- Todas as regras de código -->

## Architecture
<!-- Padrão, domínios, camadas -->

## Workflow
<!-- Fluxo PREVC resumido -->

## Quality Gates
<!-- Comandos de gate -->

## References
<!-- Links para .context/ -->
```

Manter conciso (~150-200 linhas). Gemini funciona melhor com instruções diretas e sem excesso de contexto.

#### `.gemini/settings.json`
```json
{
  "tools": {
    "autoApprove": ["read_file", "list_dir", "grep_search"]
  }
}
```

---

## 4. Codex (AGENTS.md na raiz)

### Formato Oficial
- **`AGENTS.md`** na raiz (já gerado na Fase 5)
- Suporta cascata por subdiretório
- `AGENTS.override.md` para prioridade máxima

### O que gerar
O `AGENTS.md` já está na raiz. Opcionalmente, crie `AGENTS.md` em subdiretórios para instruções específicas:

```
api/AGENTS.md        → Regras de backend
app/AGENTS.md        → Regras de frontend  
gateway/AGENTS.md    → Regras de gateway
```

Cada um com ~50 linhas referenciando o `AGENTS.md` da raiz + regras específicas da camada.

---

## 5. Script de Sincronização (`scripts/sync-context.sh`)

Gere um script bash que automatiza a sincronização:

```bash
#!/bin/bash
# sync-context.sh — Sincroniza .context/ para ferramentas de IA
# Uso: ./scripts/sync-context.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTEXT_DIR="$PROJECT_ROOT/.context"

echo "🔄 Sincronizando .context/ para ferramentas de IA..."

# 1. Copiar agents para .github/agents/
echo "  📋 GitHub Copilot agents..."
mkdir -p "$PROJECT_ROOT/.github/agents"
for agent in "$CONTEXT_DIR/agents/"*.agent.md; do
  [ -f "$agent" ] || continue
  name=$(basename "$agent" .agent.md)
  upper_name=$(echo "$name" | tr '[:lower:]' '[:upper:]')
  cp "$agent" "$PROJECT_ROOT/.github/agents/${upper_name}.agent.md"
done

# 2. Gerar resumos para .claude/agents/
echo "  🟣 Claude Code agents..."
mkdir -p "$PROJECT_ROOT/.claude/agents"
# (Resumos devem ser gerados manualmente ou por IA)

# 3. Atualizar symlink CLAUDE.md
echo "  🔗 CLAUDE.md symlink..."
cd "$PROJECT_ROOT"
ln -sf AGENTS.md CLAUDE.md

echo "✅ Sincronização concluída!"
```

### Verificação Final

- [ ] `.github/copilot-instructions.md` gerado com regras do projeto
- [ ] `.github/agents/*.agent.md` sincronizados (UPPERCASE naming)
- [ ] `.claude/settings.json` com permissões corretas
- [ ] `.claude/agents/*.md` resumidos
- [ ] `.claude/commands/*.md` com slash commands
- [ ] `.gemini/GEMINI.md` conciso (~150-200 linhas)
- [ ] `scripts/sync-context.sh` criado e funcionando
- [ ] CLAUDE.md é symlink para AGENTS.md
- [ ] Formatos respeitados para cada ferramenta

**Retorne para o INDEX.md após concluir.**
