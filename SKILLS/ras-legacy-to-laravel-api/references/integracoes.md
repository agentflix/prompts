# Integrações com parceiros e dependências ainda não portadas

## Camada de integração

Cada parceiro ganha um cliente HTTP próprio, atrás de um contrato, fora das Actions.

- **Cliente HTTP:** use o cliente do framework (`Http` do Laravel), que se testa com `Http::fake()`. Configure
  timeout e connect timeout por parceiro em `config/integrations.php`.
- **mTLS e credenciais:** certificado e chave vêm de caminho em config (volume ou secret manager), nunca do
  repositório. `verify_tls` nunca vira `false`. Se o cliente base do legado desligava a verificação, mas cada
  cliente concreto a religava, o comportamento efetivo já era "verifica": replique o efetivo, e prove lendo o
  código de cada cliente.
- **Token OAuth2:** cacheie com checagem da expiração (`exp` do JWT) antes de reutilizar. Deixe um parâmetro de
  sufixo de tenant para acomodar credencial por tenant no futuro sem mudar a assinatura.
- **Assinatura HMAC:** a chave vem de config, nunca hardcoded, nunca de `env()` fora de `config/`.
- **Payload builder:** classe própria, mockável, que monta o payload do parceiro.

## Resolver de parceiro

No legado, a escolha do serviço por parceiro costuma depender de rota, sessão e usuário dentro do controller,
e cada controller repete o mapa. Troque por uma função pura: a entidade já resolvida entra, o serviço do
parceiro sai. Quem chama (uma Action HTTP ou um Job) resolve a entidade antes. Parceiro sem serviço mapeado
lança exceção explícita, sem ramo "default" implícito. Um parceiro novo adiciona uma entrada no mapa e uma
classe que implementa o mesmo contrato, sem mudar Action nem Controller.

## Logger de integração com máscara

Todo dado de integração passa por **um** logger, e `Log::info()` ou `error_log()` direto com esse dado é
proibido.

- Rótulo estruturado por linha: parceiro, domínio, ação e fase (requisição, resposta, erro).
- `correlation_id` igual nas linhas de uma mesma chamada, e o `request_id` da requisição que a originou, para
  amarrar acesso e chamada ao parceiro.
- Máscara recursiva por **chave** (senha, authorization, tokens, segredos, CPF, CNPJ, cartão, blobs de
  documento) e por **valor** (strings que parecem `Bearer` ou JWT), como defesa em profundidade.
- URLs: mascare só os CPF (11 dígitos) e CNPJ (14 dígitos) embutidos no path, sem apagar a URL inteira,
  tratando CNPJ antes de CPF e com âncoras de dígito para não fatiar ids maiores.
- Um canal de log por parceiro, com fallback genérico.
- **Teste obrigatório:** capture o log e confirme que o rótulo e o `correlation_id` aparecem e que segredos
  passados no contexto saem como `***`.

## Dependência ainda não portada (a costura)

Durante a coexistência, uma camada depende de outra que ainda não foi portada. Não bloqueie o módulo, e não
invente a implementação: crie uma **interface** na fronteira e registre um binding padrão **seguro**
(por exemplo, "usuário atual nunca é admin"). Quando o domínio dono for portado, troque o binding. Nenhuma
Action ou Service muda. O comportamento seguro por padrão fica documentado no docblock.

## Webhooks

- **Entrada:** valide a assinatura quando o parceiro suportar (atrás de flag até coordenar segredo e formato),
  deduplique o evento por chave estável, responda a duplicado de forma segura, e grave o payload bruto para
  reprocessar.
- **Saída:** a falha na **entrega** nunca altera o resultado da transação que a originou. O job registra a
  falha e só propaga a exceção em fila assíncrona. Entrega falha é estado recuperável por reenvio.
