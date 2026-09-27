# Requisitos em EARS

EARS (Easy Approach to Requirements Syntax) força cada requisito a ter gatilho, condição e
resposta explícitos. É a mesma notação da `tlc-spec-driven`, então os requisitos extraídos
entram direto na spec da versão nova.

| Tipo | `<T>` | Padrão | Quando |
|---|---|---|---|
| Ubíquo | `U` | O sistema DEVE <ação>. | sempre vale, sem condição |
| Evento | `E` | QUANDO <gatilho>, o sistema DEVE <ação>. | requisição, comando, mensagem |
| Indesejado | `W` | SE <condição de erro>, ENTÃO o sistema DEVE <ação>. | validação, erro, exceção |
| Estado | `S` | ENQUANTO <estado>, o sistema DEVE <ação>. | status da entidade, job em execução |
| Opcional | `O` | ONDE <config/feature>, o sistema DEVE <ação>. | flag, config por tenant |

Combinações são válidas: "ENQUANTO a licença estiver suspensa, QUANDO o usuário tentar
renovar, o sistema DEVE ...". Use o tipo do gatilho principal.

Se a documentação do projeto for em inglês, use `WHEN / IF ... THEN / WHILE / WHERE / SHALL`.

## Regras de escrita

1. **Comportamento observável**: entrada → saída, efeito colateral. Não descreva a
   implementação (nome de método, classe) no enunciado — ela fica na fonte.
2. **Valores concretos**: "tenta 3 vezes com intervalo de 30 s", nunca "tenta algumas vezes".
3. **Limites exatos**: `>=` vs `>` importa. "valor maior ou igual a 100,00".
4. **Mensagens literais**: erro retornado ao usuário entre aspas, exatamente como no código.
5. **Um comportamento por requisito**. Se tem "e" ligando duas ações independentes, divida.
6. **Proibido**: "adequado", "corretamente", "tratar", "gerenciar", "etc.", "vários",
   "quando necessário". O validador não pega isso — o Critic pega.
7. **Bug é requisito também**: descreva o comportamento real e crie `FND-*` apontando para ele.

## Exemplos

Ruim: "O sistema valida a licença corretamente."

Bom:
- `REQ-LIC-W003` — SE a data de vencimento informada for anterior à data atual, ENTÃO o
  sistema DEVE rejeitar a requisição com HTTP 422 e a mensagem "Data de vencimento inválida".
- `REQ-LIC-E010` — QUANDO uma licença for criada, o sistema DEVE enfileirar o envio de email
  de boas-vindas para o contato principal da franquia.
- `REQ-LIC-S002` — ENQUANTO a licença estiver com status `SUSPENSA`, o sistema DEVE recusar
  a emissão de novos tokens de acesso para essa licença.
- `REQ-LIC-O001` — ONDE a franquia tiver `cobranca_pre_paga = 1`, o sistema DEVE exigir
  saldo maior ou igual ao valor da mensalidade antes de renovar.

## Campos de cada requisito (`module.json`)

`id`, `ears_type`, `statement`, `sources[]`, `values` (valores concretos),
`confidence` (`verified|inferred|unknown`), `critic` (`pending|approved|corrected|rejected`),
`findings[]`, `tags[]`. Ver `schemas/module.schema.json`.
