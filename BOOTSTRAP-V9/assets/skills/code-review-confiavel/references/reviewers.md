# 8 Revisores do Code Review Confiável

Abra os 8 subagents **em lotes de 2 por vez** (1+2 → 3+4 → 5+6 → 7 → 8) quando a invocação autorizar subagents, nunca os 8 de uma vez. O 8 (Meta-review) roda sozinho, depois de todos. Espere cada lote terminar antes de abrir o próximo. Cada agente deve ler somente o contexto necessário, revisar o diff inteiro dentro do seu escopo e retornar achados com evidência.

Se a política/ferramenta exigir autorização explícita para subagents e o pedido não trouxer essa autorização, peça confirmação curta antes de abrir os revisores.

## 1. Especialização

**Escopo:** arquitetura e regras do workspace alterado.

**Prompt base:**

> Revise o diff como especialista do workspace afetado. Leia a fonte de padrão da camada (tabela abaixo) e aponte apenas violações reais de arquitetura, padrão do repositório, isolamento por tenant, contratos ou segurança. Inclua arquivo/linha, evidência e correção sugerida.

**Fonte de padrão do workspace.** Leia o que o projeto declara como padrão da camada: o `AGENTS.md` e as regras da área em `.claude/rules/`. Skill de outro projeto não vale. Se o projeto não declara fonte, diga isso no relatório em vez de usar conhecimento genérico.

## 2. Grounding

**Escopo:** aderência a documentos, skills, agents e contexto do projeto.

**Prompt base:**

> Revise se a entrega respeita `AGENTS.md`, `.claude/skills/`, `.claude/agents/` e documentação relevante. Não use conhecimento genérico quando houver regra local. Aponte divergências verificáveis entre diff e fonte da verdade.

## 3. Second Pass

**Escopo:** releitura integral do diff e omissões do review.

**Prompt base:**

> Releia o diff inteiro. Liste áreas revisadas que estão limpas e aponte somente problemas com evidência. Procure bugs silenciosos, caminhos não testados, estados de erro, regressões e mudanças incompletas.

## 4. Precision

**Escopo:** reduzir falsos positivos.

**Prompt base:**

> Revise os possíveis achados com limiar alto: reporte apenas se houver confiança >= 80%, impacto real e evidência. Classifique incertezas como perguntas, não como bugs. Remova estilo subjetivo, preferência pessoal e suposição sem prova.

## 5. Human-in-the-Loop

**Escopo:** decisão humana e próximos passos.

**Prompt base:**

> Avalie quais achados exigem decisão humana, contexto de produto ou trade-off. Não aprove nem rejeite a entrega. Indique perguntas objetivas para o autor quando uma decisão depender de requisito não documentado.

## 6. Rastreabilidade

**Escopo:** vínculo entre diff, pedido ou SPEC, critérios de aceite e evidências.

**Prompt base:**

> Verifique se a entrega bate com task/issue/documentação funcional, critérios de aceite e arquivos alterados. Confirme que testes/gates cobrem o comportamento. Aponte lacunas de rastreabilidade, documentação ou evidência.

## 7. Testes, qualidade e segurança

**Escopo:** a qualidade dos testes criados, o reaproveitamento de teste e de fixture, a qualidade do código e a resistência a ataque.

**Prompt base:**

> Revise os testes e o código do diff com olho de quem vai mantê-los e de quem vai atacá-los. Aponte só o que tiver evidência.
>
> **Testes criados.**
> - Cada teste prova o que o título diz: tem assert sobre o resultado, não só "não lançou exceção".
> - Não tem assert condicional (`if` em volta do `expect`) nem `skip` fora da convenção do projeto.
> - Não depende de ordem de execução, da data de hoje, nem de dado do banco que o próprio teste não criou.
> - Cobre o caminho de erro e o limite (vazio, nulo, zero, data inválida), não só o caminho feliz.
> - Quando o teste é porte de outro sistema, o nome segue o cenário original.
>
> **Teste e fixture já existentes.**
> - Procure teste semelhante no repositório: `grep -rn` pelo nome da classe, do método ou da tabela em todas as pastas de teste do repositório.
> - Se já existe teste que prova o mesmo comportamento, aponte a duplicata.
> - Se o teste monta dado que uma fixture ou factory já monta (helpers de suporte de teste, factories, seeders), aponte o reaproveitamento.
> - Se o fixture reinsere dado de referência que o banco de teste já tem, aponte o choque de índice único.
> - Diga de onde reaproveitar, com arquivo e linha.
>
> **Qualidade de código.**
> - Código morto, duplicação dentro do diff e método grande demais para o padrão da camada.
> - Tipo frouxo: `mixed`, array sem forma, `@phpstan-ignore` sem motivo.
> - `catch` genérico sem log e sem rethrow, e comentário no lugar de phpDoc.
> - Só reporte quando houver regra do projeto, risco ou regressão, não gosto pessoal.
>
> **Segurança contra ataque** (a ameaça é modelada, não adjetivo). Para cada entrada nova (rota, parâmetro, argumento de comando, campo de formulário, arquivo, fila), trace o dado até o uso e procure:
> - **SQL injection:** valor concatenado em SQL ou filtro montado por string.
> - **Acesso indevido:** rota sem gate de sessão e de permissão. Registro de um tenant visível a outro, com o filtro do dono fora da query (IDOR).
> - **CSRF:** escrita sem `X-CSRF-Token`.
> - **XSS:** dado do banco ou do usuário sem escape na saída, ou markdown cru.
> - **Força bruta e abuso:** login, token ou rota de escrita sem limite de tentativa nem rate limit.
> - **Vazamento:** senha, hash, token ou stack trace em resposta ou em log. Entidade inteira serializada em vez de DTO.
> - **Path traversal:** caminho de arquivo montado com entrada.
> - **Mass assignment:** `$guarded = []` ou `fill($request->all())` alimentado por entrada externa.
>
> Para cada achado de segurança, descreva o vetor: quem ataca, por qual entrada e o que obtém. Sem vetor concreto, é pergunta, não achado.

## 8. Meta-review

**Escopo:** revisar o review.

**Prompt base:**

> Revise os achados dos outros agentes. Procure hallucinations, imports inexistentes, dead code, assinaturas erradas, duplicidade, falso positivo e achados sem prova. Mantenha apenas comentários acionáveis e verificáveis.

## O que cada subagent recebe

Os subagents **não** carregam esta skill: ela é de orquestração e mandaria abrir outros 8. Quem orquestra passa a cada um, no prompt:

1. O range do diff, a lista de arquivos novos (`??`) e o caminho da SPEC ou o texto do pedido.
2. O bloco do seu revisor neste arquivo e a fonte de padrão do workspace (tabela do revisor 1).
3. Os Guardrails da `SKILL.md`, copiados na íntegra.
4. O formato de `references/report-template.md` para a seção de achados.
5. Se o gate completo está rodando em paralelo: "não rode teste que usa o banco". Com banco de teste compartilhado, duas suítes juntas dão deadlock e sujam o gate e o teste do revisor.
6. Os achados dos lotes anteriores, para o revisor confirmar ou derrubar em vez de redescobrir. O revisor 4 (Precision) sempre recebe esses achados.

O revisor 8 (Meta-review) roda **por último**, sozinho, e recebe os achados consolidados dos revisores 1 a 7. Sem essa entrada, ele não está fazendo meta-review.

## Saída de Cada Subagent

Cada subagent deve retornar:

- Achados por severidade: `Crítico`, `Alto`, `Médio`, `Baixo`.
- Evidência: arquivo/linha, trecho do diff, teste/gate, regra ou contrato.
- Correção sugerida.
- Itens verificados sem achados relevantes.
- Confiança: percentual aproximado.
