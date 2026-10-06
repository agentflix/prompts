# Auditoria de paridade: provar que o port equivale ao legado

Teste unitário e cobertura medem o código novo. Eles não medem o que ficou **de fora**. Num port real, a
suíte estava verde com cobertura alta e a auditoria comparativa ainda achou regressões extensas. Esta
auditoria compara legado e novo nas duas direções e roda por módulo, antes do módulo ser dado como pronto.

## Como auditar

1. Por módulo, liste os arquivos do legado (inventário da F1) e o equivalente novo de cada um.
2. Um auditor independente do autor compara arquivo a arquivo. Quando o escopo for grande, use um agente por
   área e dois a mais para os pontos mais densos (por exemplo, submodels de uma entidade central e serviços de
   cobrança).
3. Classifique cada achado: **crítico** (bloqueia ou quebra dinheiro), **alto**, **médio**, **baixo**,
   **fiel** (verificado igual) ou **não é regressão** (código morto no legado).
4. Cada achado cita `arquivo:linha` do legado e do novo, e o efeito observável.
5. Corrija em lotes pequenos, e re-audite o que mudou. Um achado só fecha com teste que o reproduz.
6. Confirme cada alegação de "o legado fatalizaria" ou "é código morto" com evidência. Num port real, um
   docblock dizia que uma operação quebrava no legado, e a investigação mostrou que a coluna existia e a
   operação funcionava. A alegação falsa tinha escondido uma rota viva.

## Classes de regressão que costumam aparecer

| Classe | Exemplo | Como detectar |
|---|---|---|
| Pipeline de banco | O comando que cria o schema e semeia as tabelas de apoio não foi portado; o banco limpo nasce sem dados de referência | Construir o banco do zero com o código novo e conferir as tabelas de apoio |
| Regra de cobrança | A tarifa era calculada dentro do fluxo do parceiro; o novo gravava zero e não validava limite mensal | Comparar valores persistidos com a mesma entrada (shadow) |
| Conexão ou schema errado | O escopo de tenant passou a valer só numa conexão; consultas que juntam tabela comum e de tenant quebram em produção | Teste de isolamento contra banco real, com dois tenants |
| Escopo global perdido | O legado filtrava por dono via escopo global; o repositório novo não filtrou e um usuário comum listou dados de todos | Teste de acesso negado por rota; revisar todo escopo global do legado |
| Efeito colateral omitido | Recusar um cadastro enviava e-mail ao cliente; o novo só mudava o status | Listar efeitos (e-mail, fila, webhook) por fluxo no legado e conferir no novo |
| Contrato alterado | Paginação, ordem, shape de agrupamento, mensagem de sucesso diferentes | Casos de paridade request e response |
| Status HTTP | O legado uniformizava erros de domínio num status; o novo variou por exceção, e o frontend trata aquele status de um jeito (por exemplo, deslogar) | Tabela exceção para status com teste |
| Serialização de dinheiro | O legado enviava o valor como string com duas casas; o novo mandava float | Teste do payload ao parceiro |
| JSON moldado por accessor | `$hidden`, accessors e casts do legado mudavam o que o JSON expunha | Comparar o JSON de resposta campo a campo |
| Webhook de entrada | A confirmação de pagamento perdia valor pago, multa e juros | Reprocessar eventos reais gravados |
| Webhook de saída e reenvio | O evento de um tipo de cobrança e o reenvio manual sumiram | Listar eventos e rotas de reenvio do legado |
| Migração de dado de arquivo | O caminho de certificados ou documentos mudou e os arquivos antigos não foram achados | Conferir o caminho com arquivo real |

## O que o legado faz de forma implícita (checklist)

Marque cada item como portado, descartado com evidência, ou pergunta aberta:

- escopos globais de model (filtro por dono, por tenant)
- validação que morava dentro do model e as mensagens literais
- eventos, listeners e observers, e quais têm dispatch
- accessors, mutators, casts e `$hidden` que moldam o JSON
- helpers globais e funções de formatação
- middlewares (e quais eram stubs que deixavam tudo passar)
- seeders e dados de referência
- comandos de console e tarefas agendadas
- templates de e-mail e textos fixos
- transações e a ordem de efeitos externos
- constantes de status (UUID ou inteiro) e seus significados
- funcionalidades parciais (métodos "TODO" no base, sobrescritos no model realmente usado)

## Código morto não é regressão

Código sem chamador, que depende de propriedade nunca inicializada, ou que fatalizaria se fosse invocado,
não deve ser portado: portar criaria infraestrutura sem consumidor. Registre a exclusão com a busca de
chamadores. A auditoria erra nos dois sentidos, então confira também o que ela acusou de faltar.

## Divergência deliberada

Uma melhoria assumida (por exemplo, manter o registro e dar nova tentativa onde o legado apagava) é
permitida se for **decisão de produto confirmada**, registrada, e se o contrato visível não quebrar. Sem
confirmação, é regressão.

## Saída da auditoria

Um documento por módulo com: veredito (pronto ou não), achados por severidade, o que está fiel, o que não é
regressão, os descopes com evidência, e as perguntas ao dono do produto.
