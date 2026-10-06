# Exemplo: Portal de Franquias Gigatron (Tonic para Laravel)

Carregue quando o legado for o Portal de Franquias Gigatron. Os fatos abaixo vêm do `AGENTS.md` e dos
planos do repositório; confirme no código antes de decidir, porque o acoplamento dos Models ainda não foi medido.

## Ponto de partida

- Stack atual: PHP 8.3, Tonic (framework sem manutenção há cerca de 13 anos), Pimple, Twig, PostgreSQL 18
  (SQL compatível com 17), Redis e um PostgreSQL 14 só para logs.
- O frontend React já consome `/api/v1` com um envelope JSON. A camada `/api/v1` é a **costura**: o React
  só conhece o contrato JSON, então o Laravel assume o contrato e o legado fica atrás.
- O Resource da API hoje chama o Model legado (decisão `2026-10-06-resource-de-api-chama-o-model-legado`).
  Medir se esses Models dependem do Tonic, do Pimple ou de estado global é o que o spike da F0 precisa
  responder.
- O Gigatron já é consumidor de uma API de parceiro (o DotBank), então existe experiência de integração
  máquina a máquina no ecossistema.

## Mapa do port

| Hoje | Laravel |
|---|---|
| Resource | Controller fino |
| Validator | FormRequest |
| Policy | Policy |
| Service | Action |
| Model, Mapper, ORM Table | Model e Repository (Query Builder ou SQL puro onde a query for pesada) |
| `config/di.php` | Container, com ServiceProvider por domínio |
| `config/routes.php` | `routes/api.php` |
| `apps/trabalhos` | Jobs |
| `apps/scripts` | Artisan commands e Scheduler |

## Pontos de atenção específicos

1. **Isolamento por franquia.** É por linha, não por schema. Use global scope ou trait de tenant, mais teste
   de IDOR por rota. Liste no `findings.md` toda query do legado sem filtro de franquia.
2. **Dois bancos.** PG 18 de negócio e PG 14 de logs viram duas connections em `config/database.php`.
3. **Envelope JSON** (regra #15 do projeto) idêntico, com API Resources e um exception handler customizado.
4. **Permissões do userman** precisam de um mapa para o RBAC novo, com desenho antes (e a flag desligada).
5. **Módulos de maior risco:** fechamentos, comissões e licenciamento. Vão pela F4 (shadow), por último.
6. **Versão e gate:** o projeto roda PHP 8.3 e o gate atual pede PHP 8.4 ou superior; confirme a versão do
   Laravel e o PHP exigidos antes de fixar.
7. **Plano em andamento:** os planos `plano-levantamento-*` levantam telas, não o backend. A extração do
   backend (F1) ainda precisa de uma passada com `ras-legacy-extract`.

## Decisões a registrar na F0 (`.context/arch/decisions/`)

- Laravel como framework da API, com as alternativas descartadas.
- Autenticação de máquina para parceiros (token com escopo; `client_credentials` como no DotBank).
- Modelo de isolamento por franquia.
- Estratégia de virada (strangler por prefixo, recomendada) e onde a API mora (`api/` no mesmo repositório
  durante a coexistência, recomendado).
