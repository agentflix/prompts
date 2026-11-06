---
name: refatorar
description: Reestrutura código preservando o comportamento. Use para extrair, consolidar, mover responsabilidade entre módulos ou limpar código, quando a verificação precisa cercar a mudança estrutural.
---

# Refatorar

Defina a fronteira de comportamento que não pode mudar e rode a prova antes de mexer.

- Mudança de feature fica fora do refactor.
- Mova uma fronteira de responsabilidade por vez.
- Preserve interface pública, comportamento de erro, ordem e compatibilidade, salvo pedido explícito.
- Cada estado intermediário compila e passa nos testes.
- Sem dependência ou configuração nova sem necessidade de correção.

Rode a mesma prova depois. Pare quando o comportamento bater e a estrutura pedida existir.
