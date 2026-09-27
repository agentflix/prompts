# Fase 0 — Gerar o adaptador da stack

A skill não conhece nenhuma stack. O conhecimento da stack fica no **adaptador**, gerado
dentro do projeto analisado em `reverse/adapter/`. Assim a skill serve para qualquer sistema
e o adaptador fica versionado junto com a extração.

## Passos

1. **Detectar a stack**, com evidência:
   - linguagens e versões (manifestos de dependência: `composer.json`, `package.json`,
     `pom.xml`, `*.csproj`, `requirements.txt`, `go.mod`...);
   - framework HTTP e onde as rotas são registradas;
   - como a injeção de dependência / wiring funciona (registro = prova de "vivo");
   - ORM ou acesso a dados; engine do banco e como consultar seus metadados;
   - frontend: framework, roteador, onde ficam formulários, como chama a API;
   - fila, agendador, integrações.
   Registre cada conclusão com a fonte (`file:line`).

2. **Percorrer `surfaces-checklist.md` item por item.** Para cada `kind`:
   - existe → escrever um extrator determinístico (script) e a contagem de controle;
   - não existe → registrar "não existe" + o comando de busca que prova.

3. **Escrever os extratores** em `reverse/adapter/`:
   - `extract_inventory.<ext>` → gera `00-inventory/inventory.json` no schema
     `schemas/inventory.schema.json`;
   - `extract_frontend.<ext>` (se houver front) → itens `screen` com campos e chamadas;
   - `db_metadata.sql` + `db_volumetry.sql` (ou script equivalente) → `01-database/db-metadata.json`
     no schema `schemas/db-metadata.schema.json`.
   Regras dos extratores:
   - determinísticos (mesma entrada → mesma saída, ordenada);
   - sem IA dentro do extrator;
   - somente leitura (banco: usuário/conexão read-only sempre que possível);
   - toda linha extraída com `source: {repo, file, line}`;
   - chave natural estável em `key` (ex.: `GET /licencas/{id}`); objetos de banco sempre
     como `table:`, `view:`, `procedure:`, `trigger:`, `sequence:` + nome (ver
     `id-conventions.md`).
   Preferir parsing estrutural (AST, parser da linguagem) a regex quando disponível.

4. **Escrever `ADAPTER.md`** (template: `templates/adapter.md`): stack detectada, tabela de
   superfícies (kind → extrator → contagem de controle → status), limitações conhecidas,
   como rodar.

5. **Rodar e conferir**: inventário gerado, `control_counts` batendo, schema válido.

6. **Gate humano**: apresentar `ADAPTER.md` ao usuário. É o ponto mais barato para descobrir
   uma superfície esquecida. Só seguir para a Fase 1 com aprovação.

## Reuso entre projetos

Um adaptador validado pode ser copiado manualmente como ponto de partida para outro sistema
da mesma stack. Nunca mova adaptadores para dentro da skill.

## Anti-padrões

- Extrator que usa a IA para "listar os endpoints" — perde itens sem ninguém perceber.
- Inventário só a partir das classes ORM — perde tabelas sem classe, views, triggers.
- Considerar "arquivo existe" como "está vivo" — só o wiring (rota/DI/scheduler) prova.
- Contagem de controle feita pelo mesmo código do extrator — não controla nada.
