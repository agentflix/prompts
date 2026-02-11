# 📄 Generate AGENTS.md — Contrato Principal

> **Fase 5 do INDEX.md**: Consolidar tudo em `AGENTS.md` na raiz + criar `CLAUDE.md`.

## Instruções para a IA

Gere o `AGENTS.md` na raiz do projeto. Este é o **contrato principal** que toda IA deve ler ao começar a trabalhar no projeto. Deve ser **conciso** (máximo ~300 linhas) e referenciar `.context/` para detalhes.

### Estrutura Obrigatória do AGENTS.md

```markdown
# AGENTS.md — {NomeProjeto} Development Contract

> ⚠️ Leia `.context/docs/README.md` antes de começar

**Idioma**: Respostas {idioma_respostas} | Código/docs EN

## 📍 Index

| # | Seção | Quando usar |
|---|---|---|
| 1 | [Stack](#stack) | Dúvida sobre tecnologias |
| 2 | [Rules](#rules) | Antes de codar |
| 3 | [Domains](#domains) | Entender módulos |
| 4 | [Paths](#paths) | Criar arquivos |
| 5 | [Gates](#gates) | Validar código |
| 6 | [Workflow](#workflow) | Fluxo de desenvolvimento |
| 7 | [Agents](#agents) | Escolher agent |
| 8 | [Refs](#refs) | Documentação detalhada |

---

## Stack
<!-- Tabela de tecnologias do stack.yaml -->

## Rules
<!-- Regras organizadas por camada: Backend, Frontend, Security, Anti-patterns -->
<!-- OBRIGATÓRIO incluir: phpDoc/jsDoc, sem any/unknown, strict_types, testes -->

## Domains
<!-- Lista de domínios do architecture.domains -->

## Shared Components (se frontend com template)
<!-- Componentes reutilizáveis, se aplicável -->

## Paths
<!-- Onde criar cada tipo de arquivo -->

## Gates
<!-- Comandos de gate por camada -->

## Workflow
<!-- Fluxo resumido: avaliar → ler skill → implementar + testes → gates → review → commit -->

## Agents
<!-- Tabela de agents com uso -->

## Refs
<!-- Tabela com links para .context/docs/, skills, etc -->
```

### Conteúdo de cada Seção

#### Stack
- Ler `stack.yaml` e criar tabela: Layer | Tech
- Incluir versões

#### Rules
Organizar por camada, extraindo de `stack.yaml.code_rules`:

**Backend** (se aplicável):
- phpDoc obrigatório em classes e métodos públicos
- `declare(strict_types=1)` em todo arquivo
- Padrão Controller → DTO → Action → Response
- Tenant isolation (`tenant_id` em queries)

**Frontend** (se aplicável):
- jsDoc em interfaces e funções exportadas
- NUNCA usar `any` ou `unknown`
- SEMPRE ler referência antes de criar componente (se template_base)
- Padrão de componente da stack (OnPush, Signals, etc.)

**Security**:
- NUNCA logar tokens/senhas
- NUNCA `$guarded = []` (se Laravel)
- SEMPRE tenant isolation (se multi-tenant)

**Anti-patterns (nunca fazer)**:
- Lista de anti-patterns por framework

#### Domains
- Lista de domínios separados por `|`

#### Paths
- Tabela: Tipo de arquivo | Caminho

#### Gates
- Comandos por camada extraídos de `stack.yaml.quality.gates`
- Auto-fix commands (se disponíveis)

#### Workflow
1. Avaliar tamanho → Quick Fix / Small / Feature
2. Ler skill apropriada → `.context/skills/`
3. Implementar + Testes (obrigatório)
4. Rodar gates → Todos devem passar
5. Gates inegociáveis, sem perguntar
6. Code Review → `.context/skills/code-review/SKILL.md`
7. Commit → Conventional Commits

Exit Criteria:
- Código implementado
- Testes criados
- Gates verdes
- Review sem crítico

#### Agents
- Tabela extraída de `.context/agents/`

#### Refs
- Tabela com links para cada doc e skill em `.context/`

### Criar CLAUDE.md

Após gerar `AGENTS.md`, crie um symlink:

```bash
ln -sf AGENTS.md CLAUDE.md
```

Se symlinks não forem suportados, copie o conteúdo do `AGENTS.md` para `CLAUDE.md`.

### Verificação Final

- [ ] `AGENTS.md` tem no máximo ~300 linhas
- [ ] Todas as 8 seções presentes
- [ ] Regras de código (phpDoc, jsDoc, any, strict_types) documentadas
- [ ] Gates com comandos reais do stack.yaml
- [ ] Multi-agent com tabela de agents
- [ ] `CLAUDE.md` existe (symlink ou cópia)
- [ ] Links para `.context/` corretos

**Retorne para o INDEX.md após concluir.**
