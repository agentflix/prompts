# 🚀 .ai-bootstrap — AI Documentation Generator

> **Versão**: 1.0.0  
> **Autor**: Rafael Silva  
> **Data**: 2026-02-11

## O que é?

Uma pasta portátil que, ao ser importada em qualquer IA coding assistant (Claude, Copilot, Gemini, Codex), gera automaticamente toda a estrutura de documentação necessária para que IAs trabalhem de forma autônoma no projeto.

## Como usar

```bash
# 1. Copie esta pasta para a raiz do seu projeto
cp -r .ai-bootstrap/ /caminho/do/seu/projeto/

# 2. Abra sua IA de preferência e envie o INDEX.md como contexto
#    - Claude: cole o conteúdo ou use /file
#    - Copilot: abra o arquivo e peça para seguir
#    - Gemini: cole ou referencie o arquivo
#    - Codex: inclua no contexto

# 3. A IA executará automaticamente todas as 7 fases

# 4. Após concluir, remova esta pasta
rm -rf .ai-bootstrap/
```

## Estrutura

| Arquivo | Fase | Descrição |
|---|---|---|
| **INDEX.md** | — | 🎯 Prompt mestre (começar aqui) |
| `extract-stack.md` | 1 | Extrair stack de projeto existente |
| `generate-stack.md` | 1 | Gerar stack.yaml para projeto novo |
| `stack-template.yaml` | Ref | Template comentado de stack.yaml |
| `generate-agents.md` | 2 | Criar agents multi-agent + DBA |
| `generate-skills.md` | 3 | Criar skills por framework |
| `generate-docs.md` | 4 | Gerar documentação técnica |
| `generate-agents-md.md` | 5 | Consolidar AGENTS.md + CLAUDE.md |
| `sync-tools.md` | 6 | Sincronizar para ferramentas |

## Fases

1. **Detecção e Stack** — Projeto novo ou existente? Gera `stack.yaml`
2. **Agents** — Multi-agent com ORCHESTRATOR + sub-agents + DBA
3. **Skills** — Por framework (Laravel, Angular, NestJS, etc.)
4. **Docs** — Architecture, testing, security, workflow
5. **AGENTS.md** — Contrato consolidado + CLAUDE.md symlink
6. **Sync** — Distribuir para .github/, .claude/, .gemini/
7. **Revisão** — Auto-verificação de completude

## O que é gerado

```
projeto/
├── AGENTS.md              ← Contrato principal
├── CLAUDE.md              ← Symlink → AGENTS.md
├── .context/              ← Single Source of Truth
│   ├── stack.yaml
│   ├── agents/
│   ├── skills/
│   ├── docs/
│   └── workflow/
├── .github/agents/        ← Copilot
├── .claude/agents/        ← Claude Code
└── .gemini/GEMINI.md      ← Gemini/Antigravity
```

## Ferramentas suportadas

| Ferramenta | Arquivo | Pasta |
|---|---|---|
| **Codex** | `AGENTS.md` | — |
| **Copilot** | `copilot-instructions.md` | `.github/` |
| **Claude** | `CLAUDE.md` + agents | `.claude/` |
| **Gemini** | `GEMINI.md` | `.gemini/` |
