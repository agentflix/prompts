# Segurança e autenticação

Fonte: regras e decisões de um port real de API financeira. Cada item cita o motivo, porque a regra sem o
porquê vira cargo cult.

## Autenticação de máquina (parceiros)

Quando outros sistemas chamam a API, a credencial deles não é a sessão do navegador. Decisão aplicada num port
real (`client_credentials`):

1. O consumidor troca `client_id:client_secret` (header Basic) por um **token JWT de curta duração**
   (cinco minutos) com escopo de um tenant ou conta. Só o token acompanha a chamada de negócio.
2. A credencial é por **pessoa ou integrador**; o token é por tenant. O tenant pedido precisa pertencer à
   credencial, ou a emissão é negada.
3. O segredo é guardado como **hash** e exibido **uma única vez**, na geração.
4. A integração **nasce desabilitada**. Só passa a existir por ato explícito de um administrador, nunca
   por default de cadastro. (Num port real havia 92 contas com credencial ativa, e só 8 delas pertenciam
   aos 3 consumidores reais; as outras 84 foram revogadas.)
5. A falha **não distingue** credencial inexistente, inativa, revogada ou segredo errado: mesma resposta.
   Isso evita enumeração.
6. O rate limit da rota de token é **incondicional**, chaveado pelo `client_id` mais o IP.

Se o legado usa um token longo guardado em texto claro, trate isso como finding de segurança e planeje a
migração para o esquema acima como decisão própria, sem trocar tudo de uma vez. No port real, a versão
antiga e a nova da API coexistiram, cada uma com seu middleware de auth, sobre **as mesmas rotas de negócio**
(uma definição só, com a versão nova ganha por envelope de autenticação, nunca por bloco copiado).

Para um frontend SPA do próprio produto, a sessão por cookie (Sanctum) é uma opção separada: são dois modos
de auth para dois tipos de cliente, e cada um tem ADR.

## Throttle e autenticação

`throttle:` roda antes do middleware de auth customizado, então dentro do closure de `RateLimiter::for()`
`Auth::id()` é sempre `null`. A chave sai só da requisição crua (header, bearer decodificado, corpo, IP),
com fallback para o IP. Herdar um limiter que chaveia por campo de corpo que o Basic não popula gera um
limiter cego.

## Isolamento de tenant

Erro de isolamento não aparece em teste e aparece em produção, então vira teste obrigatório. Num port real,
o `search_path` do tenant foi aplicado na conexão errada: consultas que juntavam tabela comum e de tenant
quebravam em produção, e nenhum teste ficou vermelho porque todos mockavam o repositório. O teste que pegou
o erro usa **dois tenants num Postgres real** e confere o isolamento entre eles e o acesso à tabela comum.

- Escolha o modelo no ADR: schema por tenant com `search_path` posicionado por middleware, ou coluna de
  tenant com **global scope** em todo model tenant-aware.
- Nunca cruze dados de tenants diferentes na mesma query.
- Toda rota tem teste de acesso negado de outro tenant (IDOR). Liste no `findings.md` toda query do legado
  sem filtro de tenant, porque cada uma é um vazamento potencial.
- Não aceite `tenant_id`, `user_id` privilegiado ou role vindo do payload sem contexto administrativo.

## Flags de hardening (default igual ao hoje)

Controle novo nasce implementado e desligado, com o comportamento atual como default: RBAC
(`rbac_enabled`), assinatura de webhook (`webhook_hmac_enabled`), rate limit, captcha. Motivos:

- Ligar RBAC sem auditar as roles em produção tira o acesso de usuários que dependiam do legado frouxo.
- Ligar HMAC de webhook sem coordenar segredo e formato com o parceiro derruba o recebimento.
- A flag não é ligada como efeito colateral de outra tarefa. Ligar a flag **é** a tarefa, com aprovação.

O Action que chamava a checagem de permissão no legado continua chamando, via um trait que respeita a
flag. O que o legado **não** checava, a Action nova também não checa até a flag ligar.

## Dados sensíveis, log e segredos

- Segredo, token, senha, CPF e CNPJ nunca vão a log sem máscara. Todo dado de integração passa por um
  logger único com máscara recursiva, rótulo estruturado e `correlation_id`. `Log::info()` direto com
  dado de integração é proibido.
- Credencial de parceiro vem de `config/`; `env()` fora de `config/**` é proibido (quebra sob
  `config:cache`), e credencial hardcoded também.
- `verify_tls` de qualquer parceiro nunca vira `false`.
- **Rotacione todo segredo que esteve no git do legado**: assuma comprometido. Purgue o histórico.
  Certificados de mTLS ficam em secret manager ou volume, nunca no repositório.

## Upload

Valide o arquivo pelos **bytes** dentro do FormRequest, antes de qualquer escrita. `filename`, `filesize`
e `fileformat` são declarações do cliente e não valem como critério. Origem: um teste de invasão
autorizado gravou um PHP executável no disco de produção enviando-o como certificado. Corolário:
`storage/` nunca é servido pelo servidor web; documentos saem por rota autenticada. Limites de tamanho
vêm de config e são medidos contra o maior arquivo real.

## Exportação

Sanitize CSV contra injeção de fórmula, verifique a autorização antes de gerar o arquivo e prefira job
com expiração para exportação grande.

## Webhooks de saída

A falha na **entrega** de um webhook nunca altera o resultado da transação que o originou. O job registra
a falha e só propaga a exceção em fila assíncrona. Entrega falha é estado recuperável por reenvio.

## Credenciais que dão acesso à API

Rota que expõe o token de máquina exige segundo fator vigente. Rota que **altera** o estado do 2FA exige
fator vigente (código atual para quem já tem 2FA, senha atual para quem ainda não tem), senão uma sessão
roubada troca o segredo da vítima em silêncio.
