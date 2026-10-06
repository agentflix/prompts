---
name: ras-legacy-to-laravel-api
description: >-
  Método para portar o backend de um sistema PHP legado (Lumen, Tonic, framework próprio ou sem framework)
  para uma API Laravel 12 robusta e segura, sem regressão de comportamento. Cobre a ordem das fases
  (decisão, extração com paridade, esqueleto com gates, migração módulo a módulo, dinheiro em paralelo,
  corte), a arquitetura em camadas (Controller fino, Action, Service só com regra real, Repository, DTO,
  FormRequest com envelope de erro), a regra "contrato HTTP intocável", a triagem de bug do legado
  (corrigir ou preservar), autenticação máquina a máquina para parceiros, isolamento de tenant, gates de
  qualidade e o runbook de cutover. Use sempre que o pedido for migrar, portar, modernizar ou separar a
  API/backend de um legado para Laravel, escolher framework para a API nova, planejar strangler ou
  virada única, escrever o PATTERN.md ou as regras (rules.md) da API nova, ou decidir se um bug do legado
  deve ser corrigido no port. Use também quando a API vai servir de base para outros sistemas via HTTP,
  mesmo que o usuário não diga "Laravel" ou "migração". Não use para escrever código de uma feature
  nova sem legado, nem para extrair requisitos do legado (use ras-legacy-extract).
license: CC-BY-4.0
metadata:
  author: Rafael Silva
  version: '1.0.0'
  origem: lições do port Lumen 10 para Laravel 12 do projeto DotBank (PATTERN.md, rules.md, CUTOVER.md, AUDIT-FINDINGS.md)
---

# ras-legacy-to-laravel-api: portar o backend sem regressão

## Por que esta skill existe

Um port de backend parece mecânico (a lógica já existe, só muda a casca) e por isso engana. No DotBank,
o port foi declarado concluído, e a auditoria arquivo a arquivo (399 arquivos, 9 agentes) mostrou
regressões extensas: o pipeline de banco não funcionava e a tarifa nunca era cobrada, deixando o
cliente furar o limite mensal. O veredito foi "não está pronto para cutover". A lição que organiza tudo
abaixo é esta: **o risco de um port é declarar pronto sem prova de equivalência**. Por isso a paridade
vem antes do código novo, e cada fase fecha com um gate que um comando decide, não uma opinião.

Quando a API vira o coração de outros sistemas, o custo de erro sobe: um consumidor externo não
reclama, ele quebra. Segurança, teste e qualidade deixam de ser acabamento e entram como critério de
aceite de cada fase.

## Princípios (o porquê de cada um)

1. **O contrato HTTP é intocável.** Status, shape JSON e mensagens são os do legado. O consumidor
   (React, parceiro) não sabe que o servidor trocou, e é assim que a troca fica segura. Mudança de
   contrato é breaking change e exige decisão registrada.
2. **Preservar é o default; corrigir é exceção justificada.** Bug sem consumidor observável em produção
   é corrigido e documentado no docblock. Comportamento de que algum fluxo depende hoje nunca é
   "corrigido" em silêncio, porque isso é mudar comportamento, não portar. Detalhe em
   `references/triagem-de-bugs.md`.
3. **Exponha exatamente as rotas do legado.** Método de controller não é rota. Rota nova só com decisão
   registrada, e já nasce com throttle incondicional. Motivo: os middlewares do legado muitas vezes são
   stubs, e rotear um CRUD que o legado nunca expôs abre superfície sem proteção.
4. **Nada de hardening ligado como efeito colateral.** Controle de segurança novo (RBAC, HMAC de
   webhook, rate limit) nasce implementado e desligado por flag, com default igual ao comportamento
   atual. Ligar a flag é uma tarefa própria, com aprovação, porque ligar sem auditar quebra consumidor.
5. **Autor diferente de verificador.** Quem escreve não aprova. Revisão independente por módulo e, para
   dinheiro, comparação em paralelo (shadow) entre legado e novo.
6. **Gate por comando, não por opinião.** Pronto significa o gate verde (testes, análise estática,
   paridade). Regra que ninguém consegue verificar é opinião: toda regra da constituição tem o campo
   "Reforçado por".

## As fases

Cada fase tem entrada, saída e um gate. Não pule o gate, e não declare a fase pronta sem ele.

### F0: Decisão e spike (portão de decisão)

Antes de planejar o resto, prove o custo real com um corte pequeno e vertical.

1. Registre em `decisions/` o ADR do framework com as alternativas descartadas. Laravel é a escolha
   padrão para quem quer middleware, FormRequest, Actions, jobs, websocket (Reverb) e RBAC prontos;
   Symfony é a alternativa quando se quer só componentes. Registre também o ADR da auth de máquina
   (`references/seguranca-e-auth.md`) e o do isolamento de tenant.
2. Faça o spike numa rota real (a de listagem mais simples que cruza auth, tenant e envelope de erro).
3. Meça o **acoplamento dos Models legados**: eles dependem do framework antigo, do container ou de
   estado global? Se não dependem, o Laravel chama o Model legado por autoload no início e a lógica porta
   depois. Se dependem, a lógica porta junto com a rota e a estimativa sobe. Essa medida decide o tamanho.
4. **Gate F0:** o spike passa no teste de contrato (envelope, auth, isolamento de tenant) e no gate de
   qualidade. Se não passar, o projeto perdeu semanas, não meses. Só então siga.

### F1: Extração e paridade (antes de portar o módulo)

Para cada módulo, na ordem do strangler (núcleo e dependências primeiro), extraia o comportamento real
com a skill `ras-legacy-extract`: APIs, regras em EARS com `file:line`, banco (procedures e triggers
também são regra de negócio), jobs, integrações e requisitos de segurança. Duas saídas são obrigatórias
para o port:

- **`findings.md`**: os bugs, descritos como comportamento e nunca corrigidos na extração.
- **Casos de paridade**: request e response reais (dados mascarados) das rotas e regras críticas. Eles
  viram teste Pest de caracterização, e o módulo novo precisa passar neles.

Uma divergência entre o módulo novo e o caso de paridade é aceita só se for correção deliberada de bug
(princípio 2), registrada no docblock. **Gate F1:** inventário coberto 100% ou excluído com evidência
(código morto prova-se por busca de chamadores), e paridade escrita para o que o dono do produto marcou
como crítico.

### F2: Esqueleto com gates (antes de qualquer módulo)

Monte o esqueleto e os gates **primeiro**, para que nenhum módulo nasça fora do padrão.

- Escreva o `PATTERN.md` da API nova e a constituição `rules.md` (`references/arquitetura-em-camadas.md`
  e `references/regras-modelo.md`).
- Gates mínimos: análise estática em nível alto com baseline vazio (acrescentar ao baseline é proibido,
  corrige-se o erro), testes Pest/PHPUnit com meta de cobertura na camada de lógica, formatação,
  auditoria de dependências, teste de contrato do envelope de erro e teste de isolamento de tenant.
- Contrato versionado: OpenAPI como fonte da verdade, conferido por teste, mais política de depreciação.
- **Gate F2:** o gate completo roda verde num esqueleto vazio e falha de propósito quando uma regra é
  violada (teste do gate).

### F3: Migração módulo a módulo

Ordem de implementação dentro do módulo, porque a camada de baixo define a assinatura que a de cima
consome: migration, Model, contrato do Repository, Repository, DTO, FormRequest, Service (se houver regra
real), Action, Controller, binding no ServiceProvider do domínio, rota, testes.

Para cada módulo: abra o legado antes de "melhorar" qualquer coisa, imite o arquivo de referência do
projeto, preserve o comportamento, trate cada bug pela triagem e feche com revisão independente.
**Gate F3 do módulo:** gate completo verde, paridade verde, revisão sem achado bloqueante, e nenhum
`TODO` de comportamento omitido (descope é documentado, nunca silencioso).

### F4: Dinheiro em paralelo (fechamentos, comissões, cobrança, saldo)

Módulos que movem ou calculam dinheiro não viram com um gate de teste só. Rode o legado e o novo sobre
a mesma entrada e compare o resultado (shadow), sem o novo escrever em produção. Só vire o tráfego quando
a diferença for zero ou explicada linha a linha. Este é o ponto exato onde o DotBank falhou: a tarifa
sumiu e nenhum teste unitário percebeu.

### F5: Corte e retirada do legado

Use proxy na frente e roteie por prefixo. A virada por módulo (strangler) é a recomendação padrão,
porque a virada única do DotBank só se sustentou com auditoria completa depois do port. Siga o runbook
em `references/cutover.md`. Remova o framework antigo só quando ele não receber mais tráfego.

## Estratégia de virada: strangler contra virada única

| | Strangler (padrão) | Virada única |
|---|---|---|
| Risco | Limitado ao módulo da vez | Tudo de uma vez |
| Rollback | Por prefixo de rota | Reapontar o DNS inteiro |
| Custo | Dois runtimes por um tempo | Um corte, mas exige auditoria total antes |
| Quando vence | Sistema grande, com dinheiro | Sistema pequeno, com cobertura de paridade total |

Escolha virada única só com paridade completa e janela de rollback comprovada.

## Papéis e orquestração

- Fases 0, 1 (decisão do que é crítico) e 2 são trabalho de quem decide: um agente só, com o dono do
  produto.
- Fase 3: uma task por vez por módulo, com handoff completo (arquivos, regra aplicável, referência a
  imitar, comando de teste). Quem executa não procura nada e não decide arquitetura.
- Revisão: independente do autor, com contexto limpo, e com a pergunta "isso preserva o legado?" como
  critério principal.

## Referências (carregue só o que a fase pede)

| Arquivo | Quando carregar |
|---|---|
| `references/arquitetura-em-camadas.md` | F2 e F3: camadas, o que cada uma pode, ordem, binding, DTO, envelope de erro |
| `references/triagem-de-bugs.md` | Sempre que o legado mostrar um comportamento suspeito |
| `references/seguranca-e-auth.md` | F0 e F2: auth de máquina, tenant, flags, upload, log, segredos, throttle |
| `references/regras-modelo.md` | F2: modelo de constituição com o campo "Reforçado por" |
| `references/cutover.md` | F4 e F5: shadow, runbook, rollback, segredos |
| `references/exemplo-gigatron.md` | Quando o legado for o Portal de Franquias Gigatron (Tonic) |

## Antes de dizer que terminou

1. O gate completo da fase rodou verde, e você leu a saída.
2. Todo desvio do legado está registrado (decisão, docblock ou `findings.md`) com o motivo.
3. Nada foi omitido em silêncio: o que não foi portado aparece como descope documentado.
4. Você disse em voz alta o que **não** foi provado e o risco disso.
