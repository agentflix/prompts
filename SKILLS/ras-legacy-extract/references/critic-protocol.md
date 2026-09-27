# Protocolo do Critic (Fase 4)

O Critic é um agente **diferente do autor**, com contexto limpo. Ele recebe apenas: o
`module.json` e os `.md` do módulo, os itens do inventário daquele módulo, e acesso de
leitura ao código no commit fixado. Não recebe o raciocínio do autor.

Postura: o autor pode ter inventado, simplificado ou esquecido. Prove o contrário.

## Passo 1 — Cobertura

1. Liste os itens do inventário com `module = <mod>`.
2. Para cada um: está coberto (algum objeto do `module.json` com esse `inventory_key`) ou
   excluído com evidência? Falta algum → **bloqueia**; devolve ao autor.
3. Percorra `surfaces-checklist.md`: o módulo tem alguma superfície que o inventário não
   pegou (ex.: job que altera tabelas do módulo, trigger na tabela principal)? Encontrou →
   registrar como falha do adaptador e devolver para a Fase 1.

## Passo 2 — Cada requisito

Para CADA requisito, releia a fonte citada e verifique:

- a linha existe e o código ali faz o que o enunciado diz;
- condições e limites corretos (`>=` vs `>`, `==` vs `!=`, `AND` vs `OR`);
- valores concretos e mensagens batem literalmente;
- não há comportamento presumido que não está no código;
- não há ramo relevante omitido (outro `if`, `catch`, retorno antecipado);
- o texto segue as regras de `ears.md` (sem termos vagos, um comportamento só).

Veredito por requisito:

| Veredito | Ação |
|---|---|
| `approved` | mantém; pode subir para `verified` |
| `corrected` | corrige texto/linha/valor; registra o que mudou |
| `rejected` | não existe no código; remove e registra como alucinação |

## Passo 3 — APIs, telas e dados

- APIs: método, path, autenticação, parâmetros e erros conferidos na fonte.
- Telas: campos obrigatórios e validações conferidos no código do front; ações apontam para
  a API certa.
- Dados: toda query que toca dado multi-tenant tem o filtro de tenant conferido; ausência
  vira `NFR-SEC-*` + `FND-*`.

## Passo 4 — Registro

`verification-log.md` do módulo:

| ID | Veredito | Problema | Ação | Evidência |
|---|---|---|---|---|

Mais um resumo: totais por veredito, taxa de rejeição, itens devolvidos.

## Regras de parada

- Taxa de rejeição acima de 10% → módulo volta inteiro para o autor, não só os rejeitados.
- Segunda devolução do mesmo módulo → dividir o módulo ou escalar ao usuário.
- Status `verified` no `manifest.json` só com: cobertura 100%, zero `critic: pending`,
  `run_all.py --module <mod>` verde.
