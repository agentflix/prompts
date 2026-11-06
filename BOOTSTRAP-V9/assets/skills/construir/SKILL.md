---
name: construir
description: Implementa feature ou integração nova sem construir além do pedido. Use para comportamento novo, fatia de produto ou integração em que reaproveitar o que existe, escopo estrito e critério de parada claro importam.
---

# Construir

Entregue o menor caminho completo que resolve o pedido e se encaixa no sistema.

- Tire do pedido e do repositório o critério de aceite observável e o que fica de fora.
- Siga o fluxo do ponto de entrada pelas camadas que guardam as regras.
- Entregue o caminho de ponta a ponta nas camadas responsáveis, sem espremer tudo num arquivo só.
- Reaproveite a estrutura existente que encaixa. Refatore só quando remendar duplicaria comportamento ou esconderia a causa.
- Sem modos, provedores, configuração ou extensibilidade que o critério não exige.
- Dependência, serviço, config ou migration nova só com motivo. Diga o trade-off em uma linha.

Exercite o caminho e rode a prova. Pare quando o critério passar. Relate só omissões relevantes.
