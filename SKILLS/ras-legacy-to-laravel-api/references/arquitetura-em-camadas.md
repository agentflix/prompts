# Arquitetura em camadas

Padrão validado em um port real de Lumen para Laravel 12. Use como base e adapte o nome dos domínios. O
resultado desta fase é o `PATTERN.md` do projeto novo, o documento canônico que as regras citam por seção.

## Fluxo

```
Rota (routes/api.php, FQCN + middleware)
  Controller (fino)
    Action (um caso de uso, um execute())
      Service (só quando há regra de negócio real)
        Repository (toda query, atrás de interface)
          Model (mapeamento, relations, scopes, constantes)
```

## O que cada camada pode e não pode

| Camada | Pode | Proibido |
|---|---|---|
| Controller | Resolver FormRequest ou parâmetro, chamar **uma** Action, serializar | Regra de negócio, query, `try/catch` de exceção de domínio |
| Action | Um caso de uso, um método público `execute()`, dependências tipadas no construtor, sem estado mutável | Query direta, receber array cru de request, mais de um método público |
| Service | Decisão que não é buscar nem gravar; orquestrar qual query é a certa | Existir vazio, montar query, tocar `Model::` |
| Repository | Toda query, paginação e filtros, atrás de interface em `Repositories/Contracts/<Domínio>/` | Regra de negócio, ser injetado pela classe concreta |
| Model | `$table`, `$fillable`, `$hidden`, `$connection`, relations, scopes | Regra de negócio, montar query fora de scope |
| Integrations | Cliente HTTP do parceiro, payload builder | Log sem máscara, `env()`, `verify_tls` desligado |

Por que assim: query só no Repository permite testar a lógica com mock, sem banco, e rápido. Service
vazio é cerimônia sem valor, então CRUD trivial vai direto `Action -> Repository`.

## Entrada e saída

- **Entrada é DTO `readonly`**, construído de `$request->validated()`. Nenhuma Action recebe array cru.
- **FormRequest** estende uma base do projeto cujo `failedValidation()` lança a exceção de validação com o
  envelope do legado. O 422 padrão do Laravel é proibido quando o legado tinha outro formato, porque o
  consumidor já depende do formato antigo.
- **Enums** tipam códigos e status que o legado guardava como strings ou UUIDs soltos.
- **Binding** interface para implementação mora no ServiceProvider do domínio, registrado em
  `bootstrap/providers.php`. Sem o binding a interface não resolve em runtime, mesmo com todos os testes
  unitários verdes. Por isso o teste de integração resolve a Action pelo container.

## Contrato de erro

Preserve o envelope de erro do legado. Num port real o envelope era:

```json
{ "message": "...", "type": "danger", "code": 0, "status": 0, "exception": "NomeDaClasse" }
```

- Exceção de domínio estende a base do projeto, declara suas mensagens e o status HTTP, e não mexe num
  mapa central (isso evita o acoplamento base para todos os domínios que o legado tinha).
- **Todo envelope relevante tem teste de contrato** que compara o JSON exato, inclusive 401, 403, 404 e
  422. É esse teste que impede o contrato de mudar sem ninguém notar.

## Superfície HTTP

Antes de rotear, confirme no arquivo de rotas do legado o que realmente está registrado. Método de
controller sem rota no legado pode ser portado por fidelidade e coberto por teste de Action resolvida
pelo container, mas **não ganha rota**. Para exercitar o pipeline HTTP sem rota de produção, registre uma
rota `/__test__/...` dentro do próprio teste.

Rota de negócio tem **uma** definição. Uma versão nova que só muda a autenticação ganha a rota por
envelope sobre o mesmo grupo, nunca por bloco copiado, e um teste de paridade de rotas entre as versões
impede divergência.

## Banco e migrations

- Migration forward-only em produção. O port não roda migration destrutiva num banco compartilhado com o
  legado durante a coexistência.
- Fidelidade ao schema do legado, com `up()` e `down()`. Não arraste artefato histórico sem consumidor
  (coluna que ninguém lê); documente a simplificação no docblock.
- Todo comando que constrói o banco do legado (instalar, atualizar, semear) é inventário também. Se o
  legado cria o banco por comandos próprios e seeders, o port precisa dos dois, ou o banco limpo nasce
  sem as tabelas de apoio. Isso foi o achado crítico nº 1 da auditoria de um port real.
- Se o legado marca cada coluna com comentário, ou separa migrations por schema em subpastas, mantenha a
  convenção e registre as subpastas no `AppServiceProvider` (`loadMigrationsFrom`), porque o Laravel só
  descobre a raiz por padrão. Comentário de coluna só se aplica na criação: alterou, recrie o schema de teste.

## Validação, mensagens e status

- **Mensagens de validação:** o formato do envelope é o do legado, mas o conteúdo de `errors` pode ser
  amigável e específico. Cada FormRequest declara `messages()` e `attributes()`, e o arquivo de tradução
  global fica só como fallback.
- **Mensagem de sucesso:** guarde como constante na própria Action, copiada **byte a byte** do serviço
  legado, para o contrato não mudar por um espaço ou uma vírgula.
- **Status HTTP:** o legado pode devolver o mesmo status para erros de domínio diferentes, e o frontend pode
  tratar esse status de um jeito (por exemplo, deslogar em 401). Mantenha uma tabela exceção para status,
  com teste, e só mude um status com decisão registrada.
- **Dinheiro:** preserve a serialização que o parceiro recebe hoje (string com duas casas, por exemplo), e
  teste o payload.
- **Dependência ainda não portada:** crie uma interface com binding seguro por padrão (veja
  `integracoes.md`).

## Testes

- A cobertura vem de teste unitário puro com mock sobre as interfaces de Repository, sem banco.
- Teste que precisa de Postgres usa transação por teste (`DatabaseTransactions`) contra um banco de teste
  próprio, nunca o de desenvolvimento. `RefreshDatabase`, `truncate()` e lock pessimista em teste são
  proibidos, porque re-migrar a cada teste fica lento e gera lock em modelo multi-schema.
- Teste de banco fica mínimo (um ou dois por rota ou regra que vale provar com Postgres real).
- Repository com query só coberta por mock precisa de um smoke test HTTP contra banco real antes do corte.
