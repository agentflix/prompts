---
name: migrar
description: Executa transição reversível e compatível de schema, dados, API, protocolo, configuração ou dependência. Use quando a mudança precisa de caminho de volta, janela de compatibilidade e prova de que nada se perdeu.
---

# Migrar

Antes de editar, mapeie quem lê, quem escreve, o formato atual dos dados, a janela de compatibilidade e o dono.

- Defina o caminho de ida e o de volta.
- Preserve os dados existentes. Passo destrutivo é explícito e precisa de autorização separada.
- Mantenha seguro o período em que versão velha e nova rodam juntas.
- Ordem: expandir, migrar, verificar e só então contrair.
- Retentativa é idempotente e falha parcial fica visível.
- Verifique o caminho velho e o novo em cada etapa.

Pare quando a etapa pedida passar. Não faça a contração destrutiva por conta própria.
