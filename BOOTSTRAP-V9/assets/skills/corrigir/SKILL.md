---
name: corrigir
description: Corrige bug ou pequena mudança de comportamento na camada mais estreita responsável, com prova de regressão. Use para bug reportado, erro em produção, comportamento errado conhecido ou ajuste pontual em que preservar o resto importa.
---

# Corrigir

Reproduza a falha primeiro, com teste ou comando, quando for barato. Se não for, junte a evidência mais forte que existir.

- Siga o sintoma até o mecanismo que causa o erro, não até onde ele aparece.
- Mude a camada mais estreita que é dona do comportamento errado.
- Preserve o comportamento vizinho e as mudanças do usuário.
- Sem limpeza, renomeação ou abstração fora da correção.
- Acrescente só o teste de regressão desta falha.

Pare quando a reprodução passar e o gate estiver verde. Relate causa, correção e prova.
