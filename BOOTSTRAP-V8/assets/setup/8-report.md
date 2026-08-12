# Passo 8 — Relatório

Só depois de `verify.sh` sair sem falhas.

## Formato

```
## PREVEC V8 — setup concluído

### Detectado
Cenário [A/B/C]
[deployable]: [stack] · gate `[comando]`
[deployable]: [stack] · gate `[comando]`
Dados: [database] · Arquitetura: [padrão] · Módulos: [N] · Testes: [stack]

### Escolhas
Design: [não / derivar do projeto / getdesign.md:<marca> / customizado]
Ferramentas: [.claude, .codex, .opencode]
Decisões: [sim/não] · TDD do vermelho: [sim/não]

### Gerado
AGENTS.md ([N] linhas, [N]B) · CLAUDE.md · 3 agents por ferramenta selecionada · [N] skills
arch/ com 5 arquivos · work/_TEMPLATE.md

### Verificação
[saída resumida do verify.sh]

### Próximo passo
/plan [descreva o problema — ou aceite o plano do modo plano da CLI e passe para cá]
```

## Avise o usuário sobre estas cinco coisas

Não são detalhes: são as consequências que ele vai encontrar na primeira sessão.

**1. `agent: PLANNER` muda a sessão inteira.** A chave aplica o system prompt, as
restrições de ferramenta **e o modelo** do PLANNER ao thread principal. A sessão
passa a rodar em `opus` e a delegar implementação em vez de editar direto. Saídas:
`/agent` para trocar na sessão, ou mover a chave para `.claude/settings.local.json`
(fora do git, sobrepõe o projeto).

**2. `.codex/skills` é symlink.** Em checkout Windows sem `core.symlinks=true` não
resolve. Claude Code e opencode leem `.claude/skills/` direto e não têm esse problema.

**3. PLANNER no Codex é o comportamento padrão, não um `default_agent`.** O Codex
não expõe essa chave. `.codex/config.toml` usa `gpt-5.6/high` na thread principal e
`developer_instructions` para assumir o papel; os TOML em `.codex/agents/` são
agents customizados para delegação. Alterar o modelo no composer ou na CLI pode
sobrescrever o modelo da thread, mas não remove as instruções do projeto.

**4. `arch/rules.md` é a constituição — revise.** É o arquivo onde um erro de
detecção causa mais dano, porque todo agent decide a partir dele. Ler as regras
geradas leva dois minutos e evita semanas de decisão errada.

**5. Onde a documentação pode apodrecer.** O único mecanismo que mantém `arch/` vivo
é o **delta de arquitetura** declarado no work file e aplicado pelo `/ship`. Se
alguém fechar feature sem declarar delta, `arch/` começa a mentir — e mentira em
`arch/` é pior que ausência, porque o agent confia.

## Se o projeto já rodava V7.1

Avise que features abertas devem **terminar no V7.1**. O V8 vale para features
novas. Não existe script de migração de artefato em andamento — é onde esse tipo
de upgrade costuma travar, e o custo de converter um work-in-progress é maior que
o de terminá-lo no formato antigo.

Para migrar o que já está fechado, use o `verify.sh`: ele lista os resíduos do V7
(pastas absorvidas, derivados materializados, `ORCHESTRATOR.md`) que devem sair.
