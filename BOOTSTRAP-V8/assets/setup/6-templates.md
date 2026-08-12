# Passo 6 — Metodologia e templates de trabalho

## `.context/PREVEC.md` — a metodologia viaja com o repositório

Copie **como está**, sem adaptar ao projeto. É a definição canônica do ciclo, dos
papéis, do **T.A.C.E** e dos cinco princípios — e o `AGENTS.md` aponta para ele.

Dois motivos para ele existir como arquivo, e não como link:

1. **Sem dependência externa.** Repositório de terceiro sai do ar ou divergir do que
   você espera; o arquivo no repositório não.
2. **A metodologia precisa ser legível.** Sem ele, o T.A.C.E fica só *mencionado* em
   agents e skills, e nunca *definido* — quem chega no projeto não tem onde aprender
   o mecanismo central. O crédito ao **ia-coders** vive nele.

Ele não repete procedimento: o passo a passo de cada fase mora nas skills.

```bash
B=${B:-BOOTSTRAP-V8}      # se a sessão de shell não veio do Passo 1

cp $B/assets/PREVEC.md          .context/PREVEC.md      # a metodologia, auto-contida
cp $B/assets/formats/plan.md     .context/formats/plan.md
cp $B/assets/formats/response.md .context/formats/response.md
cp $B/assets/context/work/_TEMPLATE.md .context/work/_TEMPLATE.md
cp $B/assets/context/decisions/_TEMPLATE.md .context/arch/decisions/_TEMPLATE.md   # se decisões = sim
```

## O work file

Um arquivo por feature. Substitui, do V7.1: PRD + feature doc + arquivo de tasks +
session file + planning session.

| Seção | Quando existe |
|---|---|
| Cabeçalho | Sempre — tamanho, módulos, deployables, tabela de tasks com estado |
| Spec | Do tamanho M para cima |
| Fases | Do tamanho L para cima |
| Tasks | Sempre — uma seção por task: T.A.C.E + log do BUILDER embaixo |
| Delta de arquitetura | Sempre que a feature invalida algo em `arch/` |
| Review | Escrito pelo REVIEWER no fim |

**Seção que não se aplica não existe** — não fica vazia com "N/A". É a diferença
entre um arquivo de trabalho e um formulário.

## O delta de arquitetura

É o mecanismo que impede `arch/` de apodrecer, e o motivo pelo qual não existe
"item de checklist para atualizar a documentação".

A feature declara o que ela torna obsoleto:

```markdown
## Delta de arquitetura
- MODIFIED `arch/modules.yaml`: módulo `pagamentos` passa a poder importar `notificações`
- ADDED `arch/rules.md` #21: toda operação de estorno é idempotente por `external_id`
- REMOVED `arch/flows.md`: fluxo de confirmação manual sai — virou automático
```

O `/ship` **aplica esse delta** antes de commitar. Sem delta declarado, `arch/`
vira ficção em três features.

## Adapte o template ao projeto

O molde é genérico; ajuste:

- Os nomes dos deployables e, nos exemplos do campo E, o comando **filtrado por task** de `arch/gates.md` — nunca o gate completo. O BUILDER não roda o gate completo, e o comando completo só vive em `arch/gates.md` e na tabela do `AGENTS.md`
- A lista de módulos válidos no cabeçalho
- Os padrões EARS com um exemplo do domínio real, não com `<evento>` abstrato
- Se o setup respondeu TDD do vermelho = `sim`, o campo E pede duas evidências

## Sem README por pasta

Convenção de nome e regra de uso vão como comentário no **topo do próprio
template**, onde quem preenche já está olhando. README de pasta repete o template
e envelhece separado dele.

➡️ Próximo: `bash assets/setup/verify.sh`
