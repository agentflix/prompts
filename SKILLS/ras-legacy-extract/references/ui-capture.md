# Captura de telas

Objetivo: quem for reconstruir o sistema precisa saber, para cada tela, **quais campos
existem, o que é obrigatório, o que o usuário clica e qual API cada ação chama**. Sem isso,
a versão nova é criada às cegas.

## Fontes, por ordem de confiança

1. **Código do frontend** (primária, determinística) — o extrator do adaptador lista rotas
   de tela, formulários, campos, validações e chamadas de API com `file:line`.
2. **Aplicação rodando via navegador** (complementar) — confirma o que o usuário realmente
   vê e o tráfego real de cada ação.
3. **Usuário** — regra que não aparece em nenhum dos dois vira `UNK-*`.

## O que registrar por tela (`SCR-*`)

- rota/URL, título, objetivo em uma frase, menu de origem;
- perfis que acessam (e o que muda por perfil);
- campos: label, nome técnico, tipo, obrigatório, máscara/formato, valor padrão, opções
  (com origem: fixa ou API), validação no front, campo correspondente na API;
- listas/tabelas: colunas, ordenação, filtros, paginação;
- ações: rótulo do botão/link → pré-condição → `API-*` chamada → resultado/mensagem →
  navegação seguinte;
- validações que existem SÓ no front (sem equivalente na API) → `FND-*`, é risco;
- screenshot (`SCR-*.png`), com dados pessoais mascarados.

## Navegador — regras de segurança

| Ambiente | Permitido | Proibido |
|---|---|---|
| Produção | navegar, abrir telas, ler campos, capturar tráfego de GET | clicar em salvar/excluir/enviar/cancelar/aprovar, qualquer POST/PUT/PATCH/DELETE |
| Homologação / local | tudo, com autorização explícita do usuário para a sessão | usar dados reais de clientes sem mascarar |

- Login: usar a sessão já aberta do usuário; senha, MFA ou escolha de conta → parar e pedir.
- Antes de qualquer ação que grava, confirmar o ambiente pela URL e pedir autorização.
- Capturas de rede: remover cookies, tokens, headers de autorização; mascarar CPF/CNPJ,
  email, telefone, nomes.

## Captura com navegador (roteiro)

1. Abrir a tela; aguardar carregamento.
2. Árvore de acessibilidade → campos (role, nome acessível, required), botões, links.
3. Screenshot.
4. Habilitar captura de rede; executar a ação (só onde permitido); registrar método, URL,
   payload e resposta (mascarados) → mapear para `API-*` do inventário.
5. Comparar com o que o código do front diz; divergência → `FND-*`.
6. Chamada de rede sem `API-*` correspondente no inventário → falha do adaptador ou
   integração externa; investigar antes de seguir.

Casos capturados de ações relevantes podem virar `PAR-*` em `05-parity/cases/`.
