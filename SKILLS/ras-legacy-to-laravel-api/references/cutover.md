# Dinheiro em paralelo e cutover

## Shadow (F4): comparar legado e novo sobre a mesma entrada

Teste unitário e teste de paridade pontual não pegam o que um port real perdeu (a tarifa nunca era cobrada). Para fechamentos, comissões, cobrança e saldo:

1. Rode o legado e o novo sobre a **mesma entrada**. O novo calcula e compara, mas **não escreve** em
   produção durante o shadow.
2. Compare o resultado campo a campo (valor, tarifa, comissão, status, efeitos colaterais como fila e
   webhook).
3. Registre cada diferença. Só vire o tráfego quando a diferença for zero ou explicada linha a linha
   (correção deliberada de bug, já registrada).
4. Mantenha o shadow por pelo menos um ciclo completo do negócio (um fechamento mensal, por exemplo),
   porque a regra de fim de ciclo só aparece no fim do ciclo.

## Ordem de deploy

1. **Migrations de banco antes do código** (regra dura). Forward-only: o novo aponta para o mesmo banco que
   o legado usa. Coluna nova que o port adiciona é aplicada em produção antes do corte.
2. `composer install --no-dev --optimize-autoloader`.
3. `php artisan config:cache && php artisan route:cache`.
4. Workers de fila do novo no ar com **nomes de fila idênticos** aos do legado. Use um `CACHE_PREFIX`
   distinto durante a janela, para não colidir no Redis compartilhado.
5. Roteie por proxy (strangler) ou reaponte o DNS (virada única).
6. Fumaça pós-virada dos fluxos de dinheiro, login e recebimento de webhook.

## Rollback

Reaponte o proxy ou o DNS de volta para o legado, que permanece íntegro e usa o mesmo banco. Como não
houve migration destrutiva, o rollback não perde dado. Reverta o `CACHE_PREFIX`. Teste o rollback antes do
corte, não depois.

## Segredos (P0, antes ou junto do go-live)

- Rotacione todo segredo que esteve no git do legado e assuma-o comprometido.
- Certificados de mTLS entram por volume ou secret manager, não pelo repositório.
- `.env.example` do novo só tem as chaves, sem valores.
- Purgue o histórico do repositório legado (`git filter-repo`).

## Flags de segurança pós-corte

Liga-se uma de cada vez, com aprovação, depois do corte estável: RBAC (após auditar as roles reais),
assinatura de webhook (após coordenar segredo e formato com o parceiro), rate limit, captcha, restrição de
CORS e HSTS (precisa da lista de origens oficiais).

## O que registrar como descope

O que o port não cobre (PDF, exportação, ferramenta operacional com data fixa, integração ainda sem
infraestrutura) entra em lista de descope no runbook, com a decisão de avaliar a necessidade. Descope
silencioso é regressão disfarçada.

## Fumaça de repositório só coberto por mock

Repository que só tem cobertura por mock não provou a query contra o Postgres real. Rode smoke tests HTTP
contra o banco de teste, ou contra um tenant de homologação, antes do corte.
