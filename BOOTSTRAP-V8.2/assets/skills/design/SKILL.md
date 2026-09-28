---
name: design
description: Use antes de implementar qualquer componente, página ou fluxo visual. Traz o design system deste projeto — tokens, componentes existentes, tipografia — e os estados que toda tela precisa cobrir. Só instalada se o setup habilitou design.
---

# design

Fonte: **`.context/design/DESIGN.md`**, no formato da spec DESIGN.md.
Origem definida no setup: derivado do projeto, baixado de `getdesign.md/<marca>/design-md`,
ou arquivo customizado do usuário. Para o consumo, tanto faz — o formato é o mesmo.

## Antes de escrever a primeira linha de UI

1. Leia `.context/design/DESIGN.md`.
2. Procure o componente em [PATH_DO_DESIGN_SYSTEM]. Reaproveitar vence criar.
3. Confirme que a task descreve os quatro estados: vazio, carregando, erro, sucesso.

Task de UI que só descreve o caminho felizes está incompleta — devolva ao PLANNER.

## Regras

- **Token, nunca valor literal.** Cor, espaçamento e tipografia saem dos tokens de [ONDE]. Hardcode é achado de review.
- **Componente novo em compartilhado só se reutilizável e sem estado de domínio.** Caso contrário vive dentro da feature.
- **Nenhuma biblioteca de componentes de terceiros** sem decisão registrada em `.context/arch/decisions/`.
- **Acessibilidade é requisito:** navegação por teclado e foco visível. Não é extra.

## Se não existe artefato de design para a feature

Pare e produza um — ou peça. Implementar UI sem referência visual gera retrabalho
caro, porque o problema só aparece quando alguém olha a tela.

Artefato salvo em `.context/design/<feature>-<tipo>.md`, sendo tipo
`wireframe` · `component-spec` · `ux-flow`.
