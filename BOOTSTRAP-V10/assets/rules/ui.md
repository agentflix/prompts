---
paths:
  - "<ex.: src/**/*.tsx>"
  - "<ex.: src/**/*.vue>"
  - "<ex.: resources/views/**>"
---
<!--
Molde de .claude/rules/ui.md. Instale só se o projeto tem interface.
Este comentário não vai para o arquivo final.
Se existe design system documentado, aponte para ele em vez de copiar tokens aqui.
-->
# Interface

- **U1** Toda tela ou componente que busca dado cobre quatro estados: vazio, carregando, erro e sucesso. `undefined` nunca chega na renderização.
- **U2** Cor, espaçamento e tipografia vêm dos tokens de <arquivo do tema ou do design system do projeto>. Valor literal é achado de review.
- **U3** Antes de criar componente, procure em <pasta de componentes compartilhados>. Componente compartilhado não guarda estado de domínio.
- **U4** Erro e sucesso aparecem via <componente de notificação>, em <idioma>, nunca por `alert` nem em silêncio.
- **U5** HTML vindo de dado passa pelo sanitizador do projeto (<lib>). Escape manual não conta.
- **U6** Navegação por teclado e foco visível fazem parte do pronto.

Para validar UI, rode o app e olhe a tela (`/verify` ou Playwright). Screenshot ao lado da referência vale mais que descrição.
