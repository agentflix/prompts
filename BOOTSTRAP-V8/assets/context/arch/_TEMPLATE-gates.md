<!--
_TEMPLATE-gates.md → gera .context/arch/gates.md

Assunto EXCLUSIVO: comandos reais de verificação e critérios de falha.
NÃO pode conter: regras de arquitetura (rules.md), camadas (overview.md).

Este é a FONTE do comando de gate. Ele aparece em exatamente dois lugares: aqui
(completo, com etapas e filtros) e na tabela de deployables do AGENTS.md (uma célula,
como índice). Comando de gate dentro de um agent ou de uma skill é duplicação —
remova de lá e aponte para cá.

COMANDOS REAIS, extraídos dos scripts do projeto. Nunca inventar nem supor.
-->

# Gates — [PROJECT_NAME]

> Fonte única dos comandos de verificação. Agents e skills apontam para cá.
> Escopo por papel: BUILDER roda o filtrado da task; REVIEWER roda o completo, no fim.

## [deployable] — [stack]

**Completo** (o que precisa estar verde para a feature fechar):

```bash
cd [path] && [comando de gate completo]
```

**Etapas isoladas** (para diagnosticar falha):

```bash
cd [path] && [comando de análise estática]
cd [path] && [comando de teste]
cd [path] && [comando de lint]
cd [path] && [comando de formatação]
```

**Filtrado por task** (o que o BUILDER roda):

```bash
cd [path] && [comando com filtro por classe/arquivo]
cd [path] && [comando com filtro por diretório]
```

**Build** — [obrigatório antes de merge? deve terminar sem warning?]:

```bash
cd [path] && [comando de build]
```

**Pré-requisitos de ambiente:** [ex: banco de teste acessível, variável X definida]

## [outro deployable]

[mesma estrutura]

## Contexto — `.context/`

Sem comando automatizado. Conferência manual, quando o diff toca `.context/`:

- Alterou `arch/`? O delta foi declarado no plano e aplicado pelo `/ship`?
- `AGENTS.md` continua dentro do limite? `wc -l AGENTS.md` e `wc -c AGENTS.md`
- Algum derivado reapareceu? `bash BOOTSTRAP-V8/assets/setup/verify.sh`

## Critérios de falha

Qualquer um destes reprova a feature e devolve as tasks afetadas:

- Teste falhou · build falhou · lint, type-check ou formatação falhou
- [Cobertura abaixo de [alvo], se o projeto tem gate de cobertura]
- [Análise estática com erro novo, se o projeto tem nível fixado]
- Teste pulado sem justificativa explícita
- Gate obrigatório não executado sem justificativa
- Arquivo alterado fora da união das seções **A** das tasks
- Remoção de código que nenhuma task pediu

## Regras

- **Evidência é output colado**, não descrição. "Passou" não é evidência.
- **Gate que não rodou** entra no relatório com motivo e risco residual — nunca omitido.
- **Nunca ajustar teste para passar.** Teste errado é decisão, e decisão é do PLANNER.
- **Nunca `--no-verify`.**
