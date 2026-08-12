---
name: arch-frontend
description: "[ADAPTAR] Use ao implementar ou revisar qualquer coisa de interface em [PROJECT_NAME] — [camadas reais: ex. página, componente, serviço de estado, cliente de API]. Traz a regra de camadas de UI, o design system existente e o que é proibido importar."
---

<!--
TEMPLATE. Adapte ou não instale se o projeto não tem frontend.
Referencie arch/ e o design system real — não copie conteúdo. Corpo curto.
-->

# arch-frontend

Fonte: **`.context/arch/overview.md`** e **`.context/arch/rules.md`**.
Design: **`.context/design/DESIGN.md`** (se existir) e a skill `design`.

## Ordem das camadas

```
[ORDEM_REAL — ex: páginas → componentes → serviços → cliente de API → núcleo]
```

## Quem pode falar com o servidor

[REGRA_DE_CAMADA_HTTP — ex: só o cliente de API da feature e o wrapper do núcleo.
Página e componente consomem serviço, nunca o cliente direto.]

Esta é a regra de camada mais violada em frontend. Se a task pede requisição numa
página, ou a task está errada ou existe uma exceção documentada — não improvise.

## Isolamento entre features

[REGRA — ex: uma feature nunca importa de outra. O que é comum sobe para o
compartilhado.]

## Design system

**Antes de criar componente:** verifique se já existe em [PATH_DO_DESIGN_SYSTEM].
Componente novo ali só se for reutilizável e sem estado de domínio; caso contrário
vive dentro da feature.

[LIBS_PERMITIDAS] · **Proibido introduzir** biblioteca de componentes de terceiros
sem decisão registrada em `.context/arch/decisions/`.

Estilo por tokens de [ONDE_FICAM_OS_TOKENS] — valor hardcoded fora do token é achado.

## Padrões obrigatórios do framework

[PADROES_REAIS — ex: componente standalone, estratégia de detecção de mudança,
sintaxe de controle de fluxo, gerenciamento de subscrição, proibição de tipo
dinâmico]

## Estados que toda tela precisa

Vazio · carregando · erro (com o envelope real da API) · sucesso. Task de UI que só
descreve o caminho felizes está incompleta.

## Testes

Comandos em `.context/arch/gates.md`. Teste de comportamento, não de implementação.
