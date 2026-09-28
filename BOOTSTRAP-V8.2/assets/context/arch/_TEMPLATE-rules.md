<!--
_TEMPLATE-rules.md → gera .context/arch/rules.md

Este é o arquivo mais importante do .context/ — todo agent decide a partir dele.

REGRAS DE ESCRITA:
1. Cada regra é uma AFIRMAÇÃO VERIFICÁVEL, não conselho.
   ✅ "Toda query mora no repositório."   ❌ "Prefira repositórios."
2. Cada regra diz ONDE é reforçada, quando houver: linter, script, teste, revisão.
3. Regras são NUMERADAS e o número é estável — agents e reviews citam por número.
   Regra que sai deixa o número vago com uma nota. Nunca renumere.
4. O projeto já tem documento canônico de arquitetura? REFERENCIE a seção dele.
   Regra copiada é a origem de toda divergência futura.
5. Regra só muda por decisão registrada em decisions/.
6. BLOCO "Dados, API, segurança e código" (última seção) — copie-o INTEIRO quando o
   projeto tem API, banco ou consumo de dado externo. São invariantes que valem em
   toda task e que ninguém reescreve por conta própria. Adapte o que está marcado
   [ADAPTAR] e o resto vai literal. Projeto sem API e sem banco (biblioteca, CLI
   offline) pula o bloco inteiro — e diz no arquivo que pulou, para não parecer
   esquecimento.
-->

# Regras invioláveis — [PROJECT_NAME]

> Constituição do projeto. Toda decisão técnica passa por aqui.
> Alteração exige decisão registrada em `.context/arch/decisions/`.
> Documento canônico do projeto: [PATH ou "—"].

## Contrato e compatibilidade

**1.** [ex: O contrato público da API é intocável — o consumidor em produção depende do formato atual. Mudança de formato é breaking change e exige decisão registrada.]
*Reforçado por:* [teste de contrato / revisão]

**2.** [regra]
*Reforçado por:* [onde]

## Arquitetura e camadas

**3.** [ex: Nenhuma camada acima do repositório monta query. Toda query mora no repositório, atrás da interface.]
*Reforçado por:* [script de auditoria / revisão]

**4.** [regra]
*Reforçado por:* [onde]

## Dados

**5.** [ex: Dado de cliente vive na conexão resolvida pelo gerenciador de tenant. Nunca cruzar dados entre tenants.]
*Reforçado por:* [teste / revisão]

## Segurança

**6.** [ex: Segredo, token, senha e credencial nunca aparecem em log sem máscara.]
*Reforçado por:* [linter / revisão]

## Testes

**7.** [ex: Teste que precisa de banco usa transação por teste. Recriação de schema é proibida.]
*Reforçado por:* [revisão]

## Convenções obrigatórias

**8.** [ex: Idioma do projeto em código, comentário, mensagem de erro e commit: <idioma>.]
*Reforçado por:* [revisão]

## Dados, API, segurança e código

> Copie este bloco inteiro em projeto com API, banco ou consumo de dado externo, e
> adapte só o que está marcado [ADAPTAR]. A numeração continua de onde parou.
> **Sobre o reforço:** na primeira geração a maioria destas regras é reforçada só por
> revisão, porque o projeto ainda não tem API, SQL, autenticação nem migration. Isso é
> verdade e vale dizer no arquivo — regra que promete âncora mecânica que não existe
> é pior que regra sem âncora. A âncora chega junto com o código; a regra #23 abaixo
> registra a candidata concreta.

**[N].** Mensagem de erro e de sucesso sempre em **[ADAPTAR: idioma do projeto]**, fácil de compreender, e sempre exibida via [ADAPTAR: componente de notificação do projeto] — nunca `alert`, nunca erro silencioso, nunca stack trace ou texto técnico na tela. Mensagem de erro diz **o que fazer**, não o que quebrou por dentro.
*Reforçado por:* revisão · [ADAPTAR: aponte o arquivo do projeto onde o padrão já está implementado, se existir]

**[N+1].** Toda resposta de API — sucesso e erro — é JSON no **envelope único** do projeto. Erro nunca é HTTP 200 com corpo de sucesso, e nunca vaza erro interno. [ADAPTAR: se o envelope ainda não existe no código, diga isso e marque que a primeira task que criar uma API precisa defini-lo, por decisão registrada.]
*Reforçado por:* revisão

**[N+2].** Todo acesso a dado tem `fallback` explícito: valor padrão, estado de carregando e estado de erro. `undefined` nunca chega na renderização.
*Reforçado por:* revisão · [ADAPTAR: aponte o `??` do design system, se houver]

**[N+3].** Nada de `any`, `as any`, `@ts-ignore` ou `@ts-expect-error` sem motivo escrito. Desconhecido é `unknown` e estreita. O `strict` pega `any` implícito, **não** o explícito — este é o ponto cego dele, e é por isso que a regra existe. Candidata a [ADAPTAR: config do linter] quando houver hook de pre-commit.
*Reforçado por:* revisão — hoje sem âncora mecânica; o linter não tem `no-explicit-any` ligado

**[N+4].** O frontend **nunca** executa SQL. Dado muda por **migration versionada** ou por **[ADAPTAR: RPC / function / stored procedure]**, e a lógica vai para o banco sempre que possível, não para o cliente. Rodar migration ou [ADAPTAR: SQL] avulso é proibido, inclusive "só para ver o resultado rápido": histórico de banco se faz por arquivo, não por console.
*Reforçado por:* revisão · o histórico é o `git log` das migrations

**[N+5].** Migration é arquivo **novo**, versionado, com o que faz e por quê. Migration já aplicada não é editada — a correção é uma migration nova.
*Reforçado por:* revisão

**[N+6].** Toda listagem é paginada **no servidor**. A resposta traz o total e a página; o cliente pede por `start`, `end` e `perPage`. Trazer tudo e filtrar no cliente é proibido.
*Reforçado por:* revisão

**[N+7].** A feature busca o que precisa com o menor número de requisições: prefira um `GET` que já devolve o conjunto que a tela usa a N `GET`s encadeados. Waterfall de requisição é defeito, e N+1 também.
*Reforçado por:* revisão

**[N+8].** Consulta sempre escapa entrada: nenhum valor concatenado em filtro, nenhum filtro montado por string. Todo filtro vai por parâmetro, binding ou [ADAPTAR: RPC] com parâmetro. Vale para string de busca, id e data.
*Reforçado por:* revisão

**[N+9].** Segurança é ameaça modelada, não adjetivo. As que este projeto tem que fechar: **XSS** (nada de escape manual de dado vindo do banco; o renderer de markdown do projeto sanitiza) · **SQL injection** (regra anterior) · **força bruta** (login e token com contador de tentativa e bloqueio) · **rate limit** (toda rota de escrita e todo consumer de token é limitado por origem) · **endpoint que expõe dado sem gate** (regra seguinte). O mesmo vetor explorado por **pentest** ou por **I.A.** continua sendo o mesmo vetor, só que automatizado e em escala: fechar aqui é o que fecha lá.
*Reforçado por:* revisão

**[N+10].** Cruzamento de registro é sempre por **[ADAPTAR: RPC] com o id do dono no filtro**, dentro do banco. O filtro de [ADAPTAR: entidade de tenant] vai na query — nunca no filtro do cliente, nunca removido depois do fetch. É a defesa contra o registro de uma empresa aparecer na tela de outra. [ADAPTAR: a coluna de dono é X, até decisão registrada em contrário.]
*Reforçado por:* revisão

**[N+11].** Toda chamada que devolve ou altera dado de usuário exige gate: sessão autenticada e, quando existir, a permissão. [ADAPTAR: diga o estado atual do projeto, com arquivo:linha.] Rota nova entra com o gate **no mesmo diff** que a rota.
*Reforçado por:* revisão

**[N+12].** Antes de criar tabela, coluna ou índice, a análise vem no formato de DBA: normalização até 3FN, chave primária e FK explícita, índice para o filtro que a tela realmente usa, e o que ficou redundante. A análise vai no cabeçalho da migration, não na conversa.
*Reforçado por:* revisão

**[N+13].** Comentário de código é proibido. JSDoc só em função, método ou classe cuja assinatura não explica o que faz — com o que faz e os parâmetros. O código já diz o resto: comentário que repete o código envelhece e mente.
*Reforçado por:* revisão

**[N+14].** "Boa prática" não escrita aqui não é prática deste projeto. Se a task precisa de um padrão que nenhuma regra cobre, ele vira decisão registrada em `.context/arch/decisions/` **antes** de virar código.
*Reforçado por:* revisão

---

## Como usar estas regras

| Quem | Como |
|---|---|
| PLANNER | Cita no handoff **só as 2–4 regras que se aplicam** à task, por número e texto curto |
| BUILDER | Segue as citadas. Em dúvida, lê este arquivo — mas não presume regra não escrita |
| REVIEWER | Achado de violação cita **o número da regra**, nunca copia o texto |

Regra que ninguém consegue verificar não é regra — é opinião. Se você não consegue
escrever o campo *Reforçado por*, reescreva a regra até conseguir, ou remova-a.
