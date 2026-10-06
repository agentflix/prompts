---
name: ras-legacy-to-laravel-api
description: >-
  Lê um projeto PHP legado (Lumen, CodeIgniter, Tonic, framework próprio ou sem framework) e porta o
  backend para uma API Laravel 12 robusta e segura, sem regressão de comportamento. Dá a ordem das fases
  (ler o legado, decisão e spike, extração com paridade, esqueleto com gates, migração módulo a módulo,
  dinheiro em paralelo, corte), a arquitetura em camadas (Controller fino, Action, Service só com regra
  real, Repository, DTO, FormRequest com envelope de erro), a regra "contrato HTTP intocável", a triagem de
  bug do legado (corrigir ou preservar), auditoria de paridade, autenticação máquina a máquina para
  parceiros, isolamento de tenant, gates de qualidade e runbook de cutover. Use sempre que o pedido for
  migrar, portar, modernizar ou separar a API ou o backend de um legado para Laravel, escolher framework
  para a API nova, planejar strangler ou virada única, escrever o PATTERN.md ou o rules.md da API nova,
  auditar se um port está pronto, ou decidir se um bug do legado deve ser corrigido no port. Use também
  quando a API vai servir de base para outros sistemas via HTTP, mesmo que o usuário não diga "Laravel"
  ou "migração". Não use para feature nova sem legado, nem para extrair requisitos do legado (use
  ras-legacy-extract).
license: CC-BY-4.0
metadata:
  author: Rafael Silva
  version: '1.1.0'
---

# ras-legacy-to-laravel-api: ler um legado e portá-lo para Laravel sem regressão

Esta skill é genérica. Ela não conhece o projeto: a primeira fase é **ler o projeto que está na frente
dela** e só depois decidir. Os exemplos citam situações reais de ports anteriores, sem nomes de projeto.

## Por que esta skill existe

Um port de backend parece mecânico (a lógica já existe, só muda a casca) e por isso engana. Num port real
de cerca de 400 arquivos, o runbook declarava "todos os domínios portados", com 784 testes verdes e 83% de
cobertura. A auditoria arquivo a arquivo, feita depois, achou regressões extensas: o comando que construía o
banco não funcionava, a tarifa nunca era cobrada e o cliente furava o limite mensal. O veredito foi "não está
pronto para cutover". A lição que organiza tudo abaixo: **gate verde e cobertura alta não provam
equivalência**. O risco de um port é declarar pronto sem prova de paridade. Por isso a paridade vem antes do
código novo, e cada fase fecha com um critério que um comando ou uma comparação decide.

Quando a API vira base de outros sistemas, o custo de erro sobe: um consumidor externo não reclama, ele
quebra. Segurança, teste e qualidade entram como critério de aceite de cada fase.

## Princípios (o porquê de cada um)

1. **O contrato HTTP é intocável.** Status, shape JSON e mensagens são os do legado. O consumidor não sabe
   que o servidor trocou, e é assim que a troca fica segura. Mudança de contrato exige decisão registrada.
2. **Preservar é o default; corrigir é exceção justificada.** Bug sem consumidor observável é corrigido e
   documentado. Comportamento de que algo depende hoje nunca é "corrigido" em silêncio. Detalhe em
   `references/triagem-de-bugs.md`.
3. **Exponha exatamente as rotas do legado.** Método de controller não é rota. Rota nova só com decisão e
   com throttle incondicional. Os middlewares do legado muitas vezes são stubs, e rotear um CRUD que o
   legado nunca expôs abre superfície sem proteção.
4. **Nada de hardening ligado como efeito colateral.** RBAC, assinatura de webhook e rate limit nascem
   implementados e desligados por flag, com default igual ao comportamento atual. Ligar a flag é uma tarefa
   própria, com aprovação, porque ligar sem auditar quebra consumidor.
5. **Autor diferente de verificador.** Quem escreve não aprova. Revisão independente por módulo e, para
   dinheiro, comparação em paralelo (shadow).
6. **Gate por comando, não por opinião.** Toda regra da constituição tem o campo "Reforçado por".
7. **O que o legado faz de forma implícita é comportamento.** Escopos globais, validação dentro do model,
   eventos e listeners, accessors que moldam o JSON, seeders, comandos de console. Quando o model novo fica
   fino, isso some em silêncio. `references/auditoria-de-paridade.md` traz a lista.

## As fases

Cada fase tem entrada, saída e um gate. Não pule o gate e não declare a fase pronta sem ele.

### F0.0: Ler o projeto legado (antes de qualquer decisão)

Não suponha a stack. Leia o projeto e produza um **relatório de descoberta**, somente leitura. O guia está
em `references/descoberta-do-legado.md`. Em resumo, levante:

- framework, versão do PHP, gerenciador de dependências, como o app sobe (entrypoint, DI, rotas);
- a lista de rotas reais e o formato de resposta e de erro;
- banco (engine, schemas, migrations, procedures, triggers, seeders, comandos que constroem o banco);
- autenticação, autorização e o modelo de tenant (como o dado de um cliente é separado do de outro);
- jobs, filas, agendador, eventos, e-mail, webhooks (de entrada e de saída);
- integrações com parceiros e onde ficam as credenciais;
- testes e gates que existem hoje;
- quem consome a API (frontend, parceiros) e como se autenticam.

O relatório é a entrada das decisões da F0 e o denominador da cobertura da F1. Registre o commit do legado.

### F0: Decisão e spike (portão de decisão)

Prove o custo real com um corte pequeno e vertical.

1. Registre em `decisions/` o ADR do framework com as alternativas descartadas. Laravel é o padrão para quem
   quer middleware, FormRequest, Actions, jobs, websocket (Reverb) e RBAC prontos; Symfony é a alternativa
   quando se quer só componentes. Registre também o ADR da auth de máquina (`references/seguranca-e-auth.md`)
   e o do isolamento de tenant.
2. Faça o spike numa rota real e simples, que cruze auth, tenant e envelope de erro.
3. Meça o **acoplamento dos models legados**: dependem do framework antigo, do container ou de estado global?
   Se não dependem, o Laravel pode chamar o model legado por autoload no início e a lógica porta depois. Se
   dependem, a lógica porta junto com a rota e a estimativa sobe. Essa medida decide o tamanho do projeto.
4. **Gate F0:** o spike passa no teste de contrato (envelope, auth, isolamento de tenant) e no gate de
   qualidade. Se não passar, o projeto perdeu semanas, não meses.

### F1: Extração e paridade (antes de portar o módulo)

Para cada módulo, na ordem do strangler (núcleo e dependências primeiro), extraia o comportamento real com a
skill `ras-legacy-extract`: APIs, regras em EARS com `file:line`, banco (procedures e triggers também são
regra de negócio), jobs, integrações e requisitos de segurança. Saídas obrigatórias para o port:

- **`findings.md`**: os bugs, descritos como comportamento e nunca corrigidos na extração.
- **Casos de paridade**: request e response reais (dados mascarados) das rotas e regras críticas. Viram teste
  de caracterização, e o módulo novo precisa passar neles.

Uma divergência em relação ao caso de paridade só é aceita se for correção deliberada de bug (princípio 2),
registrada. **Gate F1:** inventário coberto 100% ou excluído com evidência (código morto prova-se por busca de
chamadores), e paridade escrita para o que o dono do produto marcou como crítico.

### F2: Esqueleto com gates (antes de qualquer módulo)

Monte o esqueleto e os gates **primeiro**, para que nenhum módulo nasça fora do padrão.

- Escreva o `PATTERN.md` da API nova e a constituição `rules.md` (`references/arquitetura-em-camadas.md` e
  `references/regras-modelo.md`).
- Gates mínimos: análise estática com baseline vazio (acrescentar ao baseline é proibido, corrige-se o erro),
  testes com meta de cobertura na camada de lógica, formatação, auditoria de dependências, teste de contrato
  do envelope de erro e **teste de isolamento de tenant contra banco real**. Teste que só usa mock não pega
  erro de conexão ou de schema: foi assim que um port levou uma regressão de multi-tenant sem nenhum teste
  vermelho.
- Contrato versionado: OpenAPI como fonte da verdade, conferido por teste, mais política de depreciação.
- **Gate F2:** o gate completo roda verde num esqueleto vazio e falha de propósito quando uma regra é violada.

### F3: Migração módulo a módulo

Ordem de implementação dentro do módulo, porque a camada de baixo define a assinatura que a de cima consome:
migration, Model, contrato do Repository, Repository, DTO, FormRequest, Service (se houver regra real),
Action, Controller, binding no ServiceProvider do domínio, rota, testes.

Para cada módulo: abra o legado antes de "melhorar" qualquer coisa, imite o arquivo de referência do projeto
novo, preserve o comportamento, trate cada bug pela triagem e feche com a auditoria de paridade do módulo.
**Gate F3 do módulo:** gate completo verde, paridade verde, auditoria de paridade sem achado crítico, e todo
descope documentado com evidência (nunca silencioso).

### F4: Dinheiro em paralelo (fechamentos, comissões, cobrança, saldo)

Módulos que movem ou calculam dinheiro não viram só com gate de teste. Rode o legado e o novo sobre a mesma
entrada e compare o resultado (shadow), sem o novo escrever em produção. Só vire o tráfego quando a diferença
for zero ou explicada linha a linha. Veja `references/cutover.md`.

### F5: Corte e retirada do legado

Use proxy na frente e roteie por prefixo. A recomendação padrão é strangler, porque a virada única só se
sustentou com auditoria completa depois do port. Siga `references/cutover.md`. Remova o framework antigo só
quando ele não receber mais tráfego.

## Strangler contra virada única

| | Strangler (padrão) | Virada única |
|---|---|---|
| Risco | Limitado ao módulo da vez | Tudo de uma vez |
| Rollback | Por prefixo de rota | Reapontar o DNS inteiro |
| Custo | Dois runtimes por um tempo | Um corte, mas exige auditoria total antes |
| Quando vence | Sistema grande, com dinheiro | Sistema pequeno, com paridade total comprovada |

## Papéis e orquestração

- F0.0, F0, F1 (decisão do que é crítico) e F2: trabalho de quem decide, com o dono do produto.
- F3: uma task por vez por módulo, com handoff completo (arquivos, regra aplicável, referência a imitar,
  comando de teste). Quem executa não procura nada e não decide arquitetura.
- Revisão independente do autor, em contexto limpo, com a pergunta "isso preserva o legado?" como critério.

## Referências (carregue só o que a fase pede)

| Arquivo | Quando carregar |
|---|---|
| `references/descoberta-do-legado.md` | F0.0: como ler o projeto e o que levantar |
| `references/arquitetura-em-camadas.md` | F2 e F3: camadas, ordem, DTO, binding, envelope de erro, testes |
| `references/integracoes.md` | F3: clientes de parceiro, logger com máscara, resolver, dependência ainda não portada |
| `references/triagem-de-bugs.md` | Sempre que o legado mostrar comportamento suspeito |
| `references/auditoria-de-paridade.md` | F3 e F4: como auditar o port, classes de regressão, lista do que é implícito |
| `references/seguranca-e-auth.md` | F0 e F2: auth de máquina, tenant, flags, upload, log, segredos, throttle |
| `references/regras-modelo.md` | F2: modelo de constituição com "Reforçado por" |
| `references/cutover.md` | F4 e F5: shadow, runbook, rollback, segredos |

## Antes de dizer que terminou

1. O gate completo da fase rodou verde e você leu a saída.
2. Todo desvio do legado está registrado (decisão, docblock ou `findings.md`) com o motivo.
3. Nada foi omitido em silêncio: o que não foi portado aparece como descope, com a evidência de que é código
   morto ou fatal no legado. Uma alegação de descope sem evidência já se mostrou falsa em port real.
4. Você disse em voz alta o que **não** foi provado e o risco disso.
