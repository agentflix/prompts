# PREVEC — AI-First com Workflow PREVC

## SUA MISSÃO

Configurar a estrutura AI-First neste projeto.
Agents gerados com base no contexto REAL — nunca genéricos.
Siga TODOS os passos na ordem. Não pule nenhum.

**PRINCÍPIO CENTRAL:** Não invente conteúdo inline. Leia os arquivos em `prevec-assets/` antes de cada passo relevante e siga o que eles mandam.

> `prevec-assets/` está na mesma pasta deste prompt (`BOOTSTRAP/`). Todos os paths de assets são relativos a este diretório.

---

## PASSO 0 — DETECÇÃO DO PROJETO

### 0.1 — Identificar cenário

```bash
echo "=== DETECÇÃO DO PROJETO ==="

echo "--- Buscando spec.md ---"
find . -maxdepth 3 -name "spec.md" -o -name "SPEC.md" -o -name "spec.yaml" 2>/dev/null

echo "--- Buscando manifesto de dependências ---"
ls package.json composer.json pyproject.toml Cargo.toml go.mod pom.xml build.gradle *.csproj 2>/dev/null

echo "--- Buscando estrutura existente ---"
ls -la .claude/ .codex/ .opencode/ .context/ 2>/dev/null
```

Registre quais dessas pastas já existem — usadas no Passo 1.

### 0.2 — Extrair contexto do projeto

**Cenário A (spec.md encontrado):** leia o spec.md completamente e extraia:
`PROJECT_NAME`, `PROJECT_DESCRIPTION`, `BACKEND_LANG`, `BACKEND_FRAMEWORK`, `FRONTEND_LANG`, `FRONTEND_FRAMEWORK`, `DATABASE`, `ARCHITECTURE`, `ARCHITECTURE_LAYERS`, `ARCHITECTURE_RULES`, `MODULES`, `CONVENTIONS`, `BUSINESS_RULES`, `TESTING_STACK`, `INFRA`

**Cenário B (código sem spec.md):** analise dependências, estrutura de pastas, patterns, testes, linters e infira as mesmas variáveis.

**Cenário C (já tem .claude/, .codex/, .opencode/ ou .context/):**
- NÃO sobrescreva agents com conteúdo especializado existente
- APENAS adicione o que falta
- Renomeie PLANS → FEATURES se existir

### 0.3 — Registrar contexto detectado

```
CONTEXTO DETECTADO:
- Cenário: [A/B/C]
- PROJECT_NAME: [valor]
- BACKEND: [LANG + FRAMEWORK]
- FRONTEND: [LANG + FRAMEWORK]
- DATABASE: [valor]
- ARCHITECTURE: [padrão + camadas]
- ARCHITECTURE_RULES: [regras invioláveis]
- MODULES: [lista]
- TESTING: [stack]
- CONVENTIONS: [padrões]
- BUSINESS: [regras de negócio]
```

### 0.4 — Perguntas obrigatórias

Pergunte ao usuário ANTES de continuar:

1. **CHANGELOG:** Quer usar registro diário de mudanças? (sim/não)
2. **MEMORY:** Quer usar memória persistente de decisões e aprendizados? (sim/não)
3. **Skills externas:** Em qual(is) pasta(s) instalar as skills do projeto?
   - `.claude/skills/`
   - `.opencode/skills/`
   - `.codex/skills/`
   - Todas

Registre as respostas. Elas condicionam os passos seguintes.

---

## PASSO 1 — ESTRUTURA DE PASTAS

Crie as pastas que ainda não existem. Baseie-se nas pastas detectadas no Passo 0.

```bash
# .claude/ — sempre criada
mkdir -p .claude/agents
mkdir -p .claude/skills

# .codex/ — criar se pasta .codex/ foi detectada ou se usuário escolheu .codex/skills no Passo 0.4
if [ -d ".codex" ] || [[ "$SKILLS_DEST" == *".codex"* ]]; then
  mkdir -p .codex/agents
  mkdir -p .codex/skills
fi

# .opencode/ — criar se pasta .opencode/ foi detectada ou se usuário escolheu .opencode/skills no Passo 0.4
if [ -d ".opencode" ] || [[ "$SKILLS_DEST" == *".opencode"* ]]; then
  mkdir -p .opencode/agents
  mkdir -p .opencode/skills
fi

# .context/ — sempre criada
mkdir -p .context/ARCHITECTURE
mkdir -p .context/DOCS/FEATURES
mkdir -p .context/DOCS/TASKS
mkdir -p .context/DOCS/PRDS
mkdir -p .context/DESIGN
mkdir -p .context/WORKFLOW
mkdir -p .context/.session/.archive

# Condicional CHANGELOG
if [[ "$USE_CHANGELOG" == "sim" ]]; then
  mkdir -p .context/DOCS/CHANGELOG
fi

# Condicional MEMORY
if [[ "$USE_MEMORY" == "sim" ]]; then
  mkdir -p .context/DOCS/MEMORY
fi

# Migrar PLANS se existir
if [ -d ".context/DOCS/PLANS" ]; then
  cp -rn .context/DOCS/PLANS/* .context/DOCS/FEATURES/ 2>/dev/null || true
  mv .context/DOCS/PLANS ".context/DOCS/PLANS_BACKUP_$(date +%Y%m%d)"
fi
```

---

## PASSO 2 — ARQUIVOS DE ARCHITECTURE

Gere com base no contexto do Passo 0. Substitua TODAS as variáveis por dados reais.

Arquivos a criar em `.context/ARCHITECTURE/`:

| Arquivo | Conteúdo |
|---|---|
| `architecture.md` | Diagrama Mermaid das camadas reais (bloco ```mermaid``` em markdown) |
| `modules.yaml` | Definição dos módulos/bounded contexts reais |
| `modules.md` | Mapa visual das dependências entre módulos (bloco ```mermaid``` em markdown) |
| `dependencies.yaml` | Regras de dependência entre módulos e camadas |
| `project-state.yaml` | Estado atual: stack, métricas, módulos |
| `project-brain.yaml` | Metadados para IA: identidade, decisões, regras de negócio |
| `context-version.yaml` | Versionamento dos arquivos de contexto |
| `user-flow.md` | Fluxos principais do usuário (bloco ```mermaid``` em markdown) |
| `context-snapshot.md` | **Cache lean** — campos mais lidos de todos os arquivos acima em ~40 linhas |

**Gerar `context-snapshot.md` por último**, após todos os outros arquivos, usando este formato exato:

```markdown
# Context Snapshot
> Cache gerado pelo bootstrap. Regenerar quando context-version.yaml mudar.
> Fonte: project-brain.yaml + architecture.md + modules.yaml + dependencies.yaml

## Stack
Backend: [BACKEND_LANG + BACKEND_FRAMEWORK] | Frontend: [FRONTEND_LANG + FRONTEND_FRAMEWORK]
Database: [DATABASE] | Testes: [TESTING_STACK]
Arquitetura: [ARCHITECTURE] | Camadas: [LAYER_A → LAYER_B → LAYER_C → LAYER_D]

## Regras Invioláveis
1. [regra real do projeto]
2. [regra real do projeto]
[N regras — todas do project-brain.yaml]

## Módulos e Dependências
| Módulo | Pode importar | Proibido |
|---|---|---|
| [módulo-a] | [módulo-b, shared] | [módulo-c] |

## Convenções
- [convenção de código real — ex: PSR-12, Angular Style Guide]
- [padrão de nomenclatura]
```

**Formato dos arquivos de diagrama:** sempre `.md` com o diagrama dentro de um bloco de código mermaid:

````markdown
# [Título do Diagrama]

> [Descrição curta]

```mermaid
[conteúdo do diagrama]
```
````

**Importante:** adapte o diagrama de arquitetura para o padrão REAL detectado (DDD, MVC, Clean, Hexagonal). Nunca use placeholders quando tiver dados reais.

---

## PASSO 3 — TEMPLATES CHANGELOG E MEMORY

**Execute apenas se o usuário respondeu sim no Passo 0.4.**

### CHANGELOG (se sim)

Criar em `.context/DOCS/CHANGELOG/`:
- `_TEMPLATE.md` — template de entrada diária
- `README.md` — convenções e instruções
- `[DATA-HOJE].md` — changelog inicial do setup

Formato de entrada:
```
- [HH:MM] [TIPO] [[escopo]]: Descrição concisa
  - Detalhes relevantes
  - Arquivos: path/to/file
  - Ref: FEAT-NNN / TASK-NNN
```

Tipos: `FEAT`, `FIX`, `REFACTOR`, `DOCS`, `TEST`, `CHORE`, `BREAKING`

### MEMORY (se sim)

Criar em `.context/DOCS/MEMORY/`:
- `_TEMPLATE.md` — template de decisão/aprendizado
- `README.md` — tipos e convenções
- `[DATA-HOJE]-setup-ai-first.md` — memory inicial do setup

Campos obrigatórios: Tipo, Data, Autor, Contexto, Tags, Situação, Decisão, Alternativas Consideradas, Consequências.
Tipos: Decisão, Aprendizado, Armadilha, Insight.

---

## PASSO 4 — GERAR AGENTS ESPECIALIZADOS

**Antes de criar cada agent:**
1. Leia o template correspondente em `prevec-assets/agents/{NOME}.md`
2. Substitua TODAS as variáveis por dados REAIS do Passo 0
3. Formato de saída: `.claude/agents/{NOME}.md`

**Cenário C:** não sobrescreva agents existentes com conteúdo especializado.

### Agents a gerar (4 agents)

| Agent | Template | Fase PREVC | Absorve |
|---|---|---|---|
| `ORCHESTRATOR.md` | `prevec-assets/agents/ORCHESTRATOR.md` | Todas | Coordenação pura |
| `PLANNER.md` | `prevec-assets/agents/PLANNER.md` | Pré-Planning + Planning + Review | BRANDING + PM + ARCHITECT + DESIGNER |
| `BUILDER.md` | `prevec-assets/agents/BUILDER.md` | Execution | BACKEND + FRONTEND + DEV + DBA + DEBUG |
| `REVIEWER.md` | `prevec-assets/agents/REVIEWER.md` | Review + Validation + Confirm | REVIEWER + DOC + GIT_COMMIT |

### Processo de geração

Para cada agent:
1. Ler o template em `prevec-assets/agents/{NOME}.md`
2. Ler as "Instruções de preenchimento" no final do template
3. Substituir todas as variáveis `[VARIAVEL]` por dados reais do Passo 0
4. Substituir paths de assets por paths instalados (templates usam paths de bootstrap — agents gerados precisam dos paths reais do projeto):
   - `prevec-assets/brainstorming/SKILL.md` → `[SKILLS_DEST]/brainstorming/SKILL.md`
   - `prevec-assets/code-review-confiavel/SKILL.md` → `[SKILLS_DEST]/code-review-confiavel/SKILL.md`
   - `prevec-assets/orchestrator-context-model.md` → `.claude/orchestrator-context-model.md`
5. Gerar `.claude/agents/{NOME}.md` com o conteúdo final
6. Verificar: nenhuma variável `[...]` nem path `prevec-assets/` deve permanecer no arquivo gerado

---

## PASSO 5 — CRIAR AGENTS.md

**AGENTS.md é carregado em TODA conversa — deve ter no máximo 100 linhas.**
Regra: links e referências, nunca conteúdo inline duplicado dos agent files.
Se ultrapassar 100 linhas: cortar até caber. Detalhes ficam nos arquivos de agent.

Crie `AGENTS.md` na raiz com dados REAIS. Inclua:

- Identidade do projeto (nome, stack, arquitetura)
- Regras absolutas (incluindo: "REVIEWER executa `code-review-confiavel` ao final de toda task")
- Mapa de contexto (`.claude/agents/`, `.claude/skills/`, `.context/ARCHITECTURE/`, `.context/DESIGN/`, `.context/DOCS/`, `.context/WORKFLOW/`)
- Tabela PREVC atualizada (REVIEWER cobre Review + Validation)
- Seções CHANGELOG e MEMORY (condicionais ao Passo 0.4)
- Tabela de agents (4 agents consolidados):
- Framework T.A.C.E
- **Índice de Architecture** — tabela com link e descrição de cada arquivo:

```markdown
## 🏗️ Architecture

| Arquivo | Descrição |
|---|---|
| `.context/ARCHITECTURE/architecture.md` | Diagrama de camadas da arquitetura |
| `.context/ARCHITECTURE/modules.md` | Mapa de módulos e dependências |
| `.context/ARCHITECTURE/user-flow.md` | Fluxos principais do usuário |
| `.context/ARCHITECTURE/modules.yaml` | Definição dos módulos/bounded contexts |
| `.context/ARCHITECTURE/dependencies.yaml` | Regras de dependência entre módulos |
| `.context/ARCHITECTURE/project-state.yaml` | Estado atual: stack, métricas, módulos |
| `.context/ARCHITECTURE/project-brain.yaml` | Metadados para IA: identidade, decisões, regras |
| `.context/ARCHITECTURE/context-version.yaml` | Versionamento dos arquivos de contexto |

> Antes de qualquer decisão técnica: consulte `project-brain.yaml` e `architecture.md`.

## 🎨 Design

| Pasta | Descrição |
|---|---|
| `.context/DESIGN/` | Wireframes, mockups, specs de UI e design system |

> **OBRIGATÓRIO para tasks de Frontend:** consultar `.context/DESIGN/` antes de implementar qualquer componente, página ou fluxo visual.
```

```markdown
## 🤖 Agents

| Agent | Fase PREVC | Absorve |
|---|---|---|
| ORCHESTRATOR | Todas | Coordenação — nunca implementa |
| PLANNER | Pré-Planning + Planning + Review | BRANDING + PM + ARCHITECT + DESIGNER |
| BUILDER | Execution | BACKEND + FRONTEND + DEV + DBA + DEBUG |
| REVIEWER | Review + Validation + Confirm | REVIEWER + DOC + GIT_COMMIT |
```

Remova qualquer referência a: `symlink CLAUDE.md`, `.claude/hooks/`, `settings.json`, agentes antigos (QA, PM, ARCHITECT, BACKEND, FRONTEND, DEV, DBA, DEBUG, DOC, GIT_COMMIT, DESIGNER, BRANDING).

---

## PASSO 6 — WORKFLOW PREVC

Crie `.context/WORKFLOW/PREVC.md` com as fases completas.

### Regra inviolável: REVIEWER obrigatório em toda task

O REVIEWER deve ser executado ao final de **toda** task implementada — sem exceção, sem atalho.

**Por quê:**
- Detecta alucinações do BUILDER (imports inexistentes, assinaturas erradas, dead code)
- Verifica quebra de contrato entre camadas (API ↔ frontend, Domain ↔ Infrastructure)
- Garante que o código implementado bate com a task T.A.C.E (grounding)
- Reduz falsos positivos via meta-review dos 7 revisores
- Captura regressões antes do CONFIRM

> Task sem aprovação explícita do REVIEWER não avança para CONFIRM — nunca.

O REVIEWER executa em **subagent distinto** para não contaminar o contexto do BUILDER com o review.

### Checklist de CONFIRM (obrigatório)

- [ ] Task marcada como ✅ no arquivo de tasks
- [ ] **REVIEWER executou `code-review-confiavel` em subagent distinto e aprovou**
- [ ] Evidências adicionadas (output dos testes, gates, review com 7 revisores)
- [ ] Entrada no CHANGELOG do dia *(se CHANGELOG ativo)*
- [ ] MEMORY atualizado se houve decisão/aprendizado *(se MEMORY ativo)*
- [ ] `project-state.yaml` atualizado (métricas)
- [ ] Se última task da feature → feature marcada como ✅

---

## PASSO 7 — VALIDATION FLOW

Crie `.context/WORKFLOW/validation-flow.md` com gates REAIS da stack detectada.

- Use comandos reais do projeto — não placeholders
- Substitua qualquer referência a `@QA` por `@REVIEWER`
- Include: como executar `code-review-confiavel` neste projeto

---

## PASSO 8 — INSTALAR SKILLS EXTERNAS

Copie de `prevec-assets/skills/` para a(s) pasta(s) escolhida(s) no Passo 0.4:

```bash
# Para cada pasta escolhida (ex: .claude/skills/):
cp -r prevec-assets/skills/code-review-confiavel/ [PASTA_ESCOLHIDA]/
cp -r prevec-assets/skills/brainstorming/ [PASTA_ESCOLHIDA]/
```

Copiar também o modelo de contexto do ORCHESTRATOR e o session model:

```bash
cp prevec-assets/orchestrator-context-model.md .claude/orchestrator-context-model.md
cp prevec-assets/session-model.md .context/.session/_TEMPLATE.md
cp prevec-assets/planning-session-model.md .context/.session/_PLANNING_TEMPLATE.md
```

Confirme ao usuário: "Skills instaladas em [pastas]. orchestrator-context-model.md copiado para .claude/."

---

## PASSO 9 — TEMPLATES

### Features e Tasks

Criar em `.context/DOCS/FEATURES/` e `.context/DOCS/TASKS/`:
- `_TEMPLATE.md` — template com campos obrigatórios
- `README.md` — convenções e fluxo

### PRDs

Criar em `.context/DOCS/PRDS/`:
- `_TEMPLATE.md` — PRD completo com seções: Visão Geral, Problema, Solução, Usuários, Requisitos Funcionais, Requisitos Não-Funcionais, Critérios de Aceite, Wireframes, Dependências, Riscos, Cronograma, Revisões
- `README.md` — convenções e fluxo

**Convenção de nome de PRD:** `0001-PRD-<topic-kebab>.md` (numeração sequencial)

### Design

Copiar template de `prevec-assets/design/_TEMPLATE.md` para `.context/DESIGN/`:

```bash
cp prevec-assets/design/_TEMPLATE.md .context/DESIGN/_TEMPLATE.md
```

Criar `.context/DESIGN/README.md` com:
- Como usar o template (1 arquivo por tipo: wireframe, component-spec, ux-flow)
- Convenção de nome: `[feature]-[tipo].md` (ex: `importacao-csv-wireframe.md`)
- Regra: todo arquivo aqui deve ser aprovado antes de BUILDER iniciar tasks Frontend
- Link para o `_TEMPLATE.md`

---

## PASSO 10 — SKILLS PREVEC

Instalar as 6 skills do workflow PREVEC copiando de `prevec-assets/skills/` para a(s) pasta(s) escolhida(s) no Passo 0.

Para cada pasta de destino selecionada (`.claude/skills/`, `.codex/skills/`, `.opencode/skills/`):

```bash
cp -r prevec-assets/skills/prevec-new-plan          [destino]/prevec-new-plan
cp -r prevec-assets/skills/prevec-decompose-plan     [destino]/prevec-decompose-plan
cp -r prevec-assets/skills/prevec-decompose-task     [destino]/prevec-decompose-task
cp -r prevec-assets/skills/prevec-execute-task       [destino]/prevec-execute-task
cp -r prevec-assets/skills/prevec-review-execution   [destino]/prevec-review-execution
cp -r prevec-assets/skills/prevec-finalize-execution [destino]/prevec-finalize-execution
```

| Skill | Fase PREVC | Descrição |
|---|---|---|
| `prevec-new-plan` | Planning | Ideia → PRD aprovado via brainstorming |
| `prevec-decompose-plan` | Planning | PRD → feature doc estruturada |
| `prevec-decompose-task` | Planning | Feature doc → tasks T.A.C.E hierárquicas |
| `prevec-execute-task` | Execution | Implementa uma task T.A.C.E específica |
| `prevec-review-execution` | Validation | 7 revisores em subagent — detecta alucinações e erros |
| `prevec-finalize-execution` | Confirm | Marca ✅, documenta, commita, PR se feature completa |

**Fluxo completo:**
```
/prevec-new-plan [ideia]
  → /prevec-decompose-plan [prd]
    → /prevec-decompose-task [feature]
      → /prevec-execute-task [feature] TASK-X.Y.Z
        → /prevec-review-execution [feature] TASK-X.Y.Z
          → /prevec-finalize-execution [feature] TASK-X.Y.Z
```

---

## PASSO 11 — .gitignore

```bash
if ! grep -q "prevec-assets" .gitignore 2>/dev/null; then
  echo "" >> .gitignore
  echo "# Assets do bootstrap AI-First (podem ser commitados se desejado)" >> .gitignore
  echo "# prevec-assets/" >> .gitignore
fi
```

---

## PASSO 12 — VERIFICAÇÃO FINAL

```bash
echo "=== VERIFICAÇÃO FINAL ==="

echo "Raiz:"
test -f AGENTS.md && echo "  OK AGENTS.md" || echo "  FALTA AGENTS.md"

echo "Agents:"
for f in ORCHESTRATOR PLANNER BUILDER REVIEWER; do
  test -f ".claude/agents/$f.md" && echo "  OK $f.md" || echo "  FALTA $f.md"
done

echo "Skills externas (em pasta escolhida):"
for f in code-review-confiavel brainstorming; do
  test -d ".claude/skills/$f" && echo "  OK $f" || echo "  VERIFICAR $f"
done

echo "Workflow:"
test -f ".context/WORKFLOW/PREVC.md" && echo "  OK PREVC.md" || echo "  FALTA PREVC.md"
test -f ".context/WORKFLOW/validation-flow.md" && echo "  OK validation-flow.md" || echo "  FALTA validation-flow.md"

echo "Architecture:"
for f in architecture.md modules.yaml modules.md dependencies.yaml project-state.yaml project-brain.yaml context-version.yaml user-flow.md context-snapshot.md; do
  test -f ".context/ARCHITECTURE/$f" && echo "  OK $f" || echo "  FALTA $f"
done

echo "Skills PREVEC (em pasta escolhida):"
for f in prevec-new-plan prevec-decompose-plan prevec-decompose-task prevec-execute-task prevec-review-execution prevec-finalize-execution; do
  test -f ".claude/skills/$f/SKILL.md" && echo "  OK $f/SKILL.md" || echo "  VERIFICAR $f"
done

echo "Assets:"
test -d "prevec-assets" && echo "  OK prevec-assets/" || echo "  FALTA prevec-assets/"
test -f "prevec-assets/orchestrator-context-model.md" && echo "  OK orchestrator-context-model.md" || echo "  FALTA orchestrator-context-model.md"
test -f "prevec-assets/session-model.md" && echo "  OK session-model.md" || echo "  FALTA session-model.md"

echo "Design:"
test -f ".context/DESIGN/_TEMPLATE.md" && echo "  OK _TEMPLATE.md" || echo "  FALTA _TEMPLATE.md"

echo "Session:"
test -d ".context/.session" && echo "  OK .context/.session/" || echo "  FALTA .context/.session/"
test -f ".context/.session/_TEMPLATE.md" && echo "  OK _TEMPLATE.md" || echo "  FALTA _TEMPLATE.md"
test -f ".context/.session/_PLANNING_TEMPLATE.md" && echo "  OK _PLANNING_TEMPLATE.md" || echo "  FALTA _PLANNING_TEMPLATE.md"

echo "=== FIM ==="
```

---

## PASSO 13 — RELATÓRIO FINAL

Apresente:

```
## Relatório de Setup AI-First + PREVC V7

### Cenário Detectado
[A/B/C] — [descrição]

### Stack
- Backend: [real]
- Frontend: [real]
- Database: [real]
- Arquitetura: [real]

### Opções Escolhidas
- CHANGELOG: [sim/não]
- MEMORY: [sim/não]
- Skills instaladas em: [pastas]

### Agents Criados
[lista com check]

### Skills Criadas
[lista com check]

### Skills Externas Instaladas
[lista com paths]

### Próximos Passos
1. Revisar AGENTS.md — ajustar dados não detectados automaticamente
2. Revisar agents em .claude/agents/ — refinar Inviolable Rules
3. Para uma nova ideia: `/prevec-new-plan [ideia]`
4. Para uma feature já documentada: `/prevec-decompose-plan [prd]`
5. Fluxo completo: new-plan → decompose-plan → decompose-task → execute-task → review-execution → finalize-execution
```

---

## EXECUTE AGORA

Comece pelo Passo 0.
Leia `prevec-assets/` antes de cada passo que referencia arquivos externos.
Substitua TODAS as variáveis por valores reais.
Se não conseguir detectar um valor, pergunte ao usuário.
