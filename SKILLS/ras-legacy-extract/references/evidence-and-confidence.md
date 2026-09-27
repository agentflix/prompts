# Evidência e confiança

## Hierarquia de evidência (da mais para a menos confiável)

1. **Código no commit fixado** — fonte de todo fato descritivo.
2. **Metadados e lógica do banco** — triggers, procedures, constraints são código.
3. **Testes que cobrem o caminho** — mostram o esperado e que o código executa.
4. **Evidência de runtime** — captura de rede, tela real, logs, dados. Perecível: datar.
5. **Histórico git** — explica quando e por que mudou; nunca substitui ler o código atual.
6. **Nomes, comentários, docs existentes, memória das pessoas** — testemunho. Verificar no
   código antes de repetir. Nome que contradiz o comportamento: documente o comportamento e
   registre a contradição em `findings.md`.

Em conflito, vale a fonte de nível mais alto. Conflito que não se resolve → `unknowns.md`.

## Níveis de confiança (`confidence`)

| Nível | Significa | Critério mínimo |
|---|---|---|
| `verified` | comportamento confirmado | fonte de código lida + uma segunda evidência independente (teste, tela, captura de rede, banco) **ou** Critic aprovou relendo a fonte |
| `inferred` | dedução razoável, não confirmada | fonte de código lida, mas depende de dado/config não visto ou de caminho não rastreado até o fim |
| `unknown` | não determinado | registrar em `unknowns.md` com o que foi verificado antes de desistir |

A revisão humana deve focar em `inferred` e `unknown`. Não gaste tempo do especialista com o
que já está `verified`.

## Vivo, morto ou dormente

Código que parece importante pode ser inalcançável, e código que parece morto pode ser o
caminho de produção. Nunca presuma.

- **Vivo**: provado por wiring — rota registrada, entrada no container de DI, agendamento,
  chamada a partir de outro ponto vivo.
- **Morto**: provado por ausência, com a busca nomeada: "nenhuma rota, nenhum registro de DI,
  nenhuma referência fora dos próprios testes" + os comandos usados.
- **Dormente**: ligado mas desativado (flag/config) ou alcançável só a partir de código morto.
  Descrever com a qualificação explícita.
- **Chave de config nunca lida** pelo código = chave morta.

Itens mortos/dormentes vão em `exclusions` do `module.json` com `reason` e `evidence`
(comandos). Sem evidência, não é exclusão — é pendência.

## Peculiaridades (quirks) e defeitos

- Quirk é conteúdo: comportamento surpreendente mas real ("update substitui o registro
  inteiro") entra no requisito, dito de forma direta.
- Defeito é anotado, não caçado: a extração documenta, não audita. Uma linha em
  `findings.md` com `file:line` e os IDs afetados. Sem triagem de severidade detalhada.
- Deliberado ou bug frequentemente é indecidível: descreva, marque intenção desconhecida,
  pergunte em `unknowns.md`.

## Pergunta boa em `unknowns.md`

Especialista de negócio tem pouco tempo. Cada `UNK-*` deve permitir resposta em 1 minuto:
contexto curto, o que o código faz (com `file:line`), a dúvida exata, opções de resposta,
IDs afetados.
