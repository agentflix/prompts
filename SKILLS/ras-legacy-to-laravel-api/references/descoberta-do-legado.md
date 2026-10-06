# F0.0: ler o projeto legado

Objetivo: produzir um relatório de descoberta, somente leitura, que sustenta as decisões da F0 e dá o
denominador da cobertura da F1. Não edite nada no legado. Registre o commit (`git rev-parse HEAD`).

Todo fato do relatório cita `arquivo:linha`. O que o código não responde vira pergunta ao dono do produto.

## Como ler

1. Comece pelo entrypoint e pelo arquivo de rotas. Daí sai o resto: controllers, middlewares, container.
2. Use busca de texto para inventariar, não a memória. Cada contagem tem o comando que a gerou.
3. Para saber se um trecho está vivo, procure os chamadores em todo o código. Sem chamador, é candidato a
   código morto, e a evidência da busca entra no relatório.
4. Se houver servidor de homologação ou local no ar, confirme o formato real das respostas com chamadas só de
   leitura. Nunca grave em produção.

## O que levantar

| Área | Perguntas |
|---|---|
| Stack | Framework e versão, PHP, composer, como sobe, como faz deploy |
| Rotas | Lista real de rotas (método, path, middleware, controller), e rotas que o código sugere mas ninguém registra |
| Contrato | Formato de sucesso, formato de erro (envelope), status usados, paginação, mensagens literais |
| Auth | Como autentica humano e máquina, onde ficam as permissões, o que cada middleware realmente faz (stub ou real) |
| Tenant | Como separa dado de um cliente do de outro: schema, coluna, escopo global, nada. Liste toda query sem filtro de tenant |
| Banco | Engine, schemas, tabelas, procedures, triggers, views, seeders, comandos que constroem ou atualizam o banco |
| Assíncrono | Jobs, filas (nomes), agendador, eventos e listeners, e quais eventos têm dispatch sem listener |
| Saídas | E-mail, webhooks de saída, arquivos, notificações |
| Entradas | Webhooks de entrada, uploads, importações |
| Integrações | Parceiros, cliente HTTP usado, onde ficam credenciais e certificados, se há segredo no git |
| Qualidade | Testes que existem, gates, cobertura real, análise estática |
| Consumidores | Quem chama a API, como se autentica, quais rotas usa de fato |
| Implícito | Escopos globais, validação no model, accessors e `$hidden` que moldam o JSON, helpers globais |

## Saída

Um arquivo de descoberta com: as tabelas acima preenchidas, a lista de riscos de segurança vistos, a lista
de perguntas abertas e a estimativa preliminar de tamanho por módulo. Com ele, decida o ADR do framework, o da
auth de máquina e o do isolamento de tenant (F0).
