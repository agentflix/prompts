---
name: investigar
description: Diagnostica falha de causa desconhecida antes de editar código. Use para erro intermitente, regressão de performance, comportamento inexplicado ou quando o usuário pede para entender o problema antes de mexer.
---

# Investigar

Junte evidência antes de alterar código de produto.

- Separe o sintoma observado da causa suposta.
- Siga entradas, mudanças de estado, fronteiras entre módulos e a saída do erro.
- Ordene hipóteses pela evidência e pelo custo de derrubá-las. Teste a mais barata primeiro.
- Não edite até um mecanismo explicar toda a evidência.
- Pare de explorar quando a evidência bastar para nomear a causa ou o bloqueio exato.

Relate a causa e a prova. Corrija só se o pedido autorizar implementação; nesse caso, siga a skill `corrigir` ou `surgical-patch`, a que estiver instalada; sem nenhuma, corrija na camada mais estreita com teste de regressão.
