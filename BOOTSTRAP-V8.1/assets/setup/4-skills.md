# Passo 4 — Skills

Tudo em `.claude/skills/` — fonte única, lida nativamente por Claude Code e opencode,
e pelo Codex via o symlink do Passo 1.

## 4.1 Fluxo — 3 skills

```bash
B=${B:-BOOTSTRAP-V8}      # se a sessão de shell não veio do Passo 1
cp -r $B/assets/skills/plan  .claude/skills/plan
cp -r $B/assets/skills/build .claude/skills/build
cp -r $B/assets/skills/ship  .claude/skills/ship
```

Cada skill é o atalho para um grupo de letras do PREVEC — o comando é curto, as
fases continuam nomeadas:

| Skill | Letras que executa | Quem |
|---|---|---|
| `/plan <feature>` | **P** Pré-Planning · **P** Planning · **R** review do plano | PLANNER decompõe, REVIEWER revisa o plano |
| `/build <feature> [TASK]` | **E** Execution | PLANNER despacha ao BUILDER |
| `/ship <feature>` | **V** Validation · **C** Confirm | PLANNER despacha ao REVIEWER |

Ao adaptar as skills ao projeto, **mantenha a menção às letras**. Ela é o que amarra o
comando à metodologia: sem isso, `/build` vira um verbo solto e o `E` de Execution
desaparece — junto com a razão de o BUILDER não poder marcar ✅ nem commitar.

> **Nomes sem prefixo — decisão consciente.** O V7 usava `prevec-execute-task`; o V8
> usa `/build`. Ganho: menos digitação em comandos usados várias vezes por feature,
> e o mapeamento para as letras fica óbvio: `/plan`=**P·P·R**, `/build`=**E**,
> `/ship`=**V·C**. Custo aceito: `build` e `ship` são
> palavras genéricas, então um pacote de skills de terceiros pode colidir, e as
> skills do workflow não se distinguem visualmente das pessoais na mesma pasta.
>
> Se a colisão acontecer, renomear é barato: o campo `name:` do frontmatter e o nome
> da pasta. A identidade do workflow não depende do prefixo — ela vive no `AGENTS.md`.

Adapte dentro de cada uma apenas o que é específico do projeto: nomes de deployable
e os paths de gate. O fluxo em si é igual em qualquer projeto.

## 4.2 Contexto — o mecanismo central do V8

Estas são a razão de o `AGENTS.md` ficar curto. Cada uma lê de `arch/` e **só entra
no contexto quando o assunto aparece**.

> ⚠️ **As `arch-*` são TEMPLATES, não arquivos prontos.** Elas contêm `[ADAPTAR]`,
> `[PROJECT_NAME]`, `[ORDEM_REAL...]`. Copiar e seguir adiante instala placeholder
> no projeto — e o agent vai ler "[ORDEM_REAL_DAS_CAMADAS]" como se fosse instrução.
>
> A `gates` é a única que se copia como está — ela só referencia `arch/gates.md`.
> A `design` TAMBÉM tem placeholder (o path do design system e o dos tokens): copie
> e preencha, como as `arch-*`.

```bash
cp -r $B/assets/skills/gates  .claude/skills/gates    # pronta, sem placeholder
```

Para cada camada real do projeto: copie o template correspondente **e preencha**.

```bash
cp -r $B/assets/skills/arch-backend  .claude/skills/arch-backend    # depois PREENCHER
cp -r $B/assets/skills/arch-data     .claude/skills/arch-data       # depois PREENCHER
cp -r $B/assets/skills/arch-frontend .claude/skills/arch-frontend   # só se houver UI
cp -r $B/assets/skills/design        .claude/skills/design          # se design != não
```

Ao preencher, cada uma precisa de: `description` que diga **quando** disparar, a
ordem real das camadas, a tabela do que cada camada pode e não pode, e as 3–4 regras
de `arch/rules.md` que mais pegam ali — **citadas por número, com texto curto**.

Conferência obrigatória antes de seguir:

```bash
grep -rlE '\[[A-Z_]{3,}\]|\[ADAPTAR\]' .claude/skills/ && echo "^^ ainda há placeholder" || echo "ok"
```

**Adapte à arquitetura real — não copie a lista acima cegamente:**

| Projeto | Skills de contexto |
|---|---|
| API + SPA | `arch-backend`, `arch-frontend`, `arch-data`, `gates` |
| Só API | `arch-backend`, `arch-data`, `gates` |
| Monolito com camada de integrações relevante | + `arch-integrations` |
| Biblioteca sem banco | `arch-core`, `gates` |

A regra: **uma skill por área onde o executor precisaria de conhecimento
reutilizável**. Renomeie os arquivos e ajuste as descrições para as camadas que
existem de verdade.

### A `description` é o gatilho

É a única parte da skill que fica no contexto sempre. Escreva **quando ela vale**,
não o que ela contém:

```
✅ description: Use ao implementar ou revisar qualquer coisa na camada de servidor —
   Action, Service, Repository, Controller, migration de domínio.
❌ description: Documentação da arquitetura de backend.
```

E lembre: **o handoff do PLANNER nomeia qual skill carregar.** A descrição é a
rede de segurança, não o mecanismo primário. Skill não nomeada no handoff é skill
que pode não ser carregada.

## 4.3 Externas

```bash
cp -r $B/assets/skills/code-review-confiavel .claude/skills/code-review-confiavel
```

Ajuste `references/gates.md` dela para **apontar** para `.context/arch/gates.md`
em vez de repetir os comandos. Se a skill original vier com gates de outro projeto,
substitua — gate errado é pior que gate ausente.

## 4.4 O que este bootstrap NÃO instala

Skills pessoais do usuário — autoria de skills, brainstorming, utilitários — **não
fazem parte do workflow**. Elas convivem em `.claude/skills/` e são versionadas
junto, mas instalar por conta própria mistura duas coisas com ciclos de vida
diferentes e distorce qualquer medição do workflow.

Se o usuário quer alguma, ele copia — ou pede.

➡️ Próximo: `assets/setup/5-contract.md`
