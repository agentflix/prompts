---
name: ras-refactor
description: >-
  Migra uma codebase React + Vite + TypeScript + Supabase organizada por tipo técnico
  (hooks/, components/, pages/) para uma arquitetura feature-first por domínio, de forma
  INCREMENTAL (um domínio por PR) e SEM quebrar produção. Cada domínio vira
  features/<x>/ com camadas api (I/O atômico) / services (orquestração) / hooks (estado),
  <x>.model.ts (tipos) + <x>.constants.ts (constantes), componentes quebrados, tipagem
  estrita e testes com gate de cobertura por domínio. Use quando o pedido for reorganizar
  por domínio/feature, apertar tipagem (matar `any`, chegar a strict), centralizar
  constantes/tipos, ou introduzir testes numa base React/Supabase. NÃO use para features
  novas do zero nem para projetos que não sejam React/Supabase sem adaptar.
metadata:
  author: Rafael Silva
  version: '1.0.0'
---

# Feature-First Refactor (React + Supabase)

## Visão geral

Transforma um projeto organizado **por tipo técnico** (`src/hooks/` com dezenas de arquivos,
`src/components/`, `src/pages/`, `src/lib/`) numa arquitetura **feature-first**: cada domínio
de negócio é um módulo auto-contido em `src/features/<domínio>/`. A migração é **incremental
(1 domínio por PR)**, **preserva comportamento** (há usuários em produção) e sobe a qualidade
em três eixos simultâneos: **organização**, **tipagem** e **testes**.

Filosofia: evolução gradual, não reescrita. Cada passo é verificável (`tsc`/`test`/`build`/`lint`)
e commitável isoladamente. Nunca migrar tudo de uma vez ("big-bang").

## Quando usar / quando não

USE quando o usuário pedir: reorganizar por domínio/feature; separar lógica de UI; apertar
tipagem (eliminar `any`, `strict: true`); centralizar constantes/tipos; adicionar testes com
meta de cobertura; ou "replicar a arquitetura de outro projeto" numa base React/Vite/Supabase.

NÃO use para: criar features novas do zero (use brainstorming/feature skills); projetos que
não sejam React+TS (adapte antes); mudanças triviais de 1 arquivo.

---

## Arquitetura-alvo

```
src/
  app/                     # bootstrap: App.tsx, router, providers globais
  features/<domínio>/
    api/                   # I/O atômico do Supabase: 1 operação = 1 função, tipada
    services/              # orquestração + regra de negócio (puro, sem React) — SÓ quando existe
    hooks/                 # estado React; delega para service/api
    components/            # componentes do domínio (JSX fica aqui)
    pages/                 # rotas do domínio
    <x>.model.ts           # TODOS os tipos/interfaces/enums do domínio (inclui props e params)
    <x>.constants.ts       # mensagens, storage keys, timeouts, eventos, defaults (`as const`)
    index.ts               # barrel: API pública do módulo
  shared/
    ui/                    # design system (ex-components/ui) — transversal
    lib/                   # utils transversais (formatters, etc.)
    hooks/                 # hooks genéricos (use-mobile, use-toast, useFileUpload…)
    constants/             # SUPABASE_TABLES/SUPABASE_BUCKETS, ROUTES, STORAGE_KEYS (fonte única)
  integrations/supabase/   # client.ts + types.ts (gerado) — intacto
```

### As três camadas (regra central)

1. **`api/` — I/O atômico.** Cada função faz **uma** operação Supabase (`.from()`, `.rpc()`,
   `.auth.*`, `.channel()`), tipada, com o filtro `organization_id` **centralizado**. É a
   fronteira de mock nos testes. Nenhum `supabase.*` deve existir fora daqui (nem em hooks,
   pages ou components).
2. **`services/` — orquestração + regra de negócio.** Funções PURAS (sem React) que compõem
   várias chamadas da `api` ou aplicam regras. **Regra anti-anêmico:** só crie `service`
   quando há orquestração real (múltiplas chamadas) ou regra de negócio; CRUD simples vai
   direto `hook → api` (senão o service vira passthrough vazio).
3. **`hooks/` — estado React.** `useState`/`useEffect`/realtime; delega a lógica para
   service/api. Componentes consomem os hooks.

### Convenções

- **Nomes:** hooks `camelCase` (`useFoo.ts`), componentes/pages `PascalCase.tsx`,
  `api`/`services`/`model`/`constants` `camelCase.ts`, pastas de feature `kebab-case`.
  Acrônimos conhecidos (CRM, API, NPS, UI) em **CAIXA-ALTA** e uniformes.
- **Um termo por entidade:** ao migrar, unifique sinônimos que o código usa para a MESMA
  entidade (ex.: `Organization`/`Org`/`Company` → escolha um, ex. `Org`). Renomeie apenas
  **identificadores de código** (arquivos, componentes, hooks, tipos, variáveis). NUNCA
  renomeie nomes de tabela/coluna do banco (`organizations`, `organization_id`), tipos
  gerados (`Tables<'organizations'>`) nem textos pt-BR visíveis ao usuário ("Empresa") —
  isso quebraria schema/produção/UI. Rotas são URLs observáveis: só troque se autorizado e
  adicione **redirect de compatibilidade** da rota antiga. Como renomear símbolos exige tocar
  os importadores externos, atualize-os direto (o alias de caminho não cobre troca de nome).
- **Tipos:** `<x>.model.ts` deriva de `Tables<'x'>`/`TablesInsert`/`Enums<'x'>` do Supabase
  (nunca redefinir campos à mão). **Centraliza TODAS as interfaces do domínio** — inclusive
  params de hook (`UseXxxParams`) e props de componente (`XxxProps`), exportadas e importadas
  via `import type`. Um `<x>.model.ts` por módulo (não um global).
- **Constantes:** `<x>.constants.ts` com objetos `as const` (mensagens pt-BR, storage keys,
  timeouts, eventos, defaults). Transversais (nomes de tabela, rotas, storage keys globais)
  vão para `shared/constants/`. Sem i18n a menos que pedido — textos ao usuário IDÊNTICOS.

---

## Fase 0 — Fundação compartilhada [1 PR, uma vez por projeto]

1. **Estrutura:** criar `src/app/`, `src/features/`, `src/shared/{ui,lib,hooks,constants,types}`.
   Mover `components/ui`→`shared/ui`, `lib`→`shared/lib`, hooks genéricos→`shared/hooks`,
   `App.tsx`→`app/`. Usar `git mv` (preserva histórico).
2. **Path aliases de COMPATIBILIDADE** — a chave para não reescrever centenas de imports.
   Em `tsconfig` e `vite.config`/`vitest.config`, mapear os caminhos ANTIGOS para os NOVOS.
   No Vite, converter `resolve.alias` para ARRAY ordenado (entradas específicas ANTES do
   `@/*` genérico). No tsconfig `paths`, o mais específico já tem prioridade; manter `@/*`
   por último. Ex.: `@/components/ui/*`→`src/shared/ui/*`, `@/lib/*`→`src/shared/lib/*`.
   Aliases exatos por arquivo para hooks/pages movidos individualmente.
3. **ESLint:** `@typescript-eslint/no-explicit-any: 'warn'` global; preparar `overrides` por
   glob `src/features/**` (ligados a `'error'` domínio a domínio).
4. **Coverage (Vitest + `@vitest/coverage-v8`):** provider `v8`; `include` na camada-alvo
   (`src/features/**/*.ts`, `src/shared/lib/**`); `exclude` `shared/ui`, `**/*.tsx`,
   `types.ts` gerado, `pages`, `src/test`. `thresholds` **por glob** (começam em 0 global;
   cada domínio migrado ganha `'src/features/<x>/**': { lines:80, functions:80, statements:80, branches:70 }`).
5. **Infra de teste:** `src/test/mocks/supabase.ts` (`createSupabaseMock()` — ver template) e
   `src/test/utils.tsx` (`renderHookWithProviders`/`renderWithProviders` com QueryClient).
6. **Integração (opcional):** `vitest.integration.config.ts` (env node) + seed multi-org para
   testar RLS/RPC contra Supabase local.

**DoD:** `npm test` verde; `npm run build` ok; aliases resolvem; coverage gera relatório.

---

## Receita por domínio [1 PR por domínio]

Ordem sugerida: **do mais isolado ao mais acoplado** (ex.: auth → tickets → marketing →
settings → … → crm → chat por último). Para cada domínio:

1. **Mapear (subagent Explore):** hooks/components/pages do domínio; chamadas Supabase;
   `organization_id`; `any`; interfaces inline; RPCs/tabelas; importadores (impacto);
   literais candidatos a constantes; roteamento.
2. **Mover + renomear** para `features/<x>/{hooks,components,pages}` (`git mv`), aplicando a
   convenção de nomes.
3. **Aliases de compatibilidade** para os caminhos antigos → não reescrever importadores.
4. **`api/`** — extrair o I/O atômico (uma op/função), `organization_id` centralizado e tipado.
5. **`services/`** (só se houver orquestração/regra) — mover os fluxos que compõem várias
   chamadas; CRUD simples não ganha service.
6. **`<x>.model.ts`** — derivar de `Tables<'x'>`; centralizar TODAS as interfaces (incl.
   props/params); eliminar os `any` do domínio.
7. **`<x>.constants.ts`** — extrair mensagens/keys/timeouts/eventos/defaults (`as const`,
   textos IDÊNTICOS). Trocar literais transversais por `shared/constants`.
8. **Quebrar componentes pesados** (>~250 linhas): extrair estado/handlers para um **hook**
   (`useXxxForm` — como é `.ts`, entra no coverage → testar) + **subcomponentes de
   apresentação** + um **layout** reutilizável. O **JSX permanece nos componentes** (separar
   markup em arquivo à parte é anti-padrão no React). Comportamento/visual/textos idênticos.
9. **Apertar tipagem** — ligar override ESLint estrito no glob do domínio (`no-explicit-any: 'error'`).
10. **Testar** — unitários sobre `api`/`service`/hooks (assert do isolamento `organization_id`,
    estados, transformações); mirar o gate ≥80/70. `.tsx`/pages ficam fora do coverage.
11. **`index.ts`** (barrel) + **elevar o threshold** do glob para travar o ganho.

**DoD por domínio:** `npx tsc --noEmit` sem novos erros; `npm test` verde no gate do domínio;
`npm run build` ok; `npm run lint` sem novos erros; rota do domínio funciona.

## Consolidação final [1 PR]

`strict: true` global (+ `noImplicitAny`, `strictNullChecks`); remover overrides e ligar
`no-explicit-any: 'error'` global; threshold de coverage 80/70 na camada-alvo; CI (GitHub
Actions) rodando testes + gate de cobertura por PR.

---

## Regras de segurança (produção viva) — OBRIGATÓRIAS

- **Comportamento/textos idênticos:** refatoração NÃO muda o que o usuário vê. Ao centralizar
  mensagens, copie as strings byte-a-byte (verifique com `grep`/diff vs o commit anterior).
- **Ordem de deploy:** migration de banco SEMPRE antes (ou junto) do código que a usa.
- **Fallback resiliente:** quando o código passa a usar uma RPC/coluna nova, manter fallback
  para o caminho antigo enquanto a migration não estiver garantida em produção (detectar
  PostgREST `PGRST202`/"Could not find the function" e cair no fluxo legado). Remover depois.
- **Isolamento multi-tenant:** toda query org-scoped deve filtrar `organization_id` na `api`
  (defesa em profundidade, além do RLS). É a origem #1 de bugs neste tipo de projeto.
- **Migrations forward-only e não-destrutivas**; funções Postgres novas com `DROP FUNCTION IF
  EXISTS` da assinatura exata antes do `CREATE` (evita overload órfão em multi-tenant).
- Operações de banco passam por aprovação explícita antes de executar.

---

## Processo de execução (como conduzir)

1. **Explore** (subagent read-only) mapeia o domínio → escopo exato.
2. **Implementar** via subagent com instruções detalhadas (o molde + escopo). Divida domínios
   grandes (ex. componente de 1000+ linhas) em 2 fases: (a) camadas+dados+testes; (b)
   componentização+tipagem estrita.
3. **Verificação INDEPENDENTE** (não confie só no relatório do subagent): rode você mesmo
   `npx tsc --noEmit`, `npm test`, `npm run test:coverage`, `npm run build`, `npm run lint`, e
   `grep` para confirmar (mensagens idênticas ao HEAD; nenhum `supabase.*` fora da api;
   nenhuma interface fora do model).
4. **Commit por domínio** (Conventional Commits), incluindo só os arquivos do domínio.

## Decisões deliberadamente adiadas

- **Não** criar um "CRUD/serviço genérico" do Supabase cedo — o query builder já é genérico e
  a maioria dos hooks reais usa RPC/join/realtime que não cabem no molde. Reavaliar após 2-3
  domínios; o candidato de maior valor é um helper que **force `organization_id`**.
- Props triviais podem ficar inline OU no model — decidir a convenção com o time (este molde
  centraliza tudo no `<x>.model.ts`).

---

## Templates

### `createSupabaseMock()` (src/test/mocks/supabase.ts)
Factory de um mock encadeável do client: métodos de query (`select/insert/update/delete/
upsert/eq/neq/in/or/order/limit/range/single/maybeSingle`) retornam o próprio builder e ele é
"thenable" resolvendo `{ data, error }` configurável por teste (`setTableResult`,
`setRpcResult`, `setInvokeResult`, `reset`). Inclui `auth` (getSession/getUser/signIn/signOut),
`channel` (on/subscribe/unsubscribe) e `functions.invoke`. Objetivo: eliminar boilerplate de
mock manual e servir como fronteira estável de teste da camada `api`.

### `<x>.model.ts`
```ts
import type { Tables, TablesInsert, Enums } from '@/integrations/supabase/types';
export type Ticket = Tables<'tickets'>;
export type TicketInsert = TablesInsert<'tickets'>;
export type TicketStatus = Enums<'ticket_status'>; // ou union se for TEXT
// contratos reutilizados + props/params centralizados:
export type SubmitFn = (data: TicketInsert) => Promise<unknown>;
export interface UseTicketsParams { orgId: string; userId: string }
export interface TicketListProps { orgId: string }
```

### `<x>.constants.ts`
```ts
export const TICKET_STATUS = { OPEN: 'open', IN_PROGRESS: 'in_progress', CLOSED: 'closed' } as const;
export const TICKET_ERRORS = { CLOSE_FORBIDDEN: 'Sem permissão para encerrar este chamado.' } as const;
export const TICKET_PAGE_SIZE = 50;
```

### `api/<x>Api.ts` (I/O atômico, org-scoped)
```ts
import { supabase } from '@/integrations/supabase/client';
import { SUPABASE_TABLES } from '@/shared/constants';
export async function listTickets(orgId: string) {
  const { data, error } = await supabase
    .from(SUPABASE_TABLES.TICKETS)
    .select('*')
    .eq('organization_id', orgId);   // isolamento centralizado
  if (error) throw error;
  return data;
}
```

### Coverage por glob (vitest.config.ts)
```ts
coverage: {
  provider: 'v8',
  include: ['src/features/**/*.ts', 'src/shared/lib/**/*.ts'],
  exclude: ['**/*.tsx', '**/*.test.*', 'src/integrations/supabase/types.ts', '**/index.ts'],
  thresholds: {
    lines: 0, functions: 0, statements: 0, branches: 0, // global sobe no fim
    'src/features/auth/**': { lines: 80, functions: 80, statements: 80, branches: 70 },
  },
}
```

## ⚠️ Loop de render ao extrair hooks (causa OOM no vitest)
Ao extrair estado de um componente para um hook, NÃO use `useEffect` + `setState` derivando de uma prop **array/objeto** (ex. `messages`): a dep muda de referência a cada render e o `setState` recria o valor → re-render → loop infinito → o heap cresce até o worker do vitest morrer com `ERR_WORKER_OUT_OF_MEMORY`/`ERR_IPC_CHANNEL_CLOSED` (parece falta de RAM, mas NÃO é — cheque `memory_pressure`). **Derive com `useMemo`** (não seta estado). Sintoma: um teste de hook que trava ~130s e estoura, ou a suíte que só começa a dar OOM depois de uma fase que adicionou hooks. É bug de código (e latente em produção), não do ambiente.

## ⚠️ Gate de type-check correto
Projetos Vite usam `tsconfig.json` com `"files": []` + `references` (project references). Nesse caso **`npx tsc --noEmit` compila ZERO arquivos e sempre retorna 0 — não checa a app**. Use SEMPRE `npx tsc --noEmit -p tsconfig.app.json` (ou `tsc -b`) como gate real. Cuidado extra: Vite (SWC) e Vitest NÃO fazem type-check, então build/test verdes NÃO garantem 0 erros de tipo — só o `tsc` correto garante.

## Checklist de verificação (por domínio)
- [ ] `npx tsc --noEmit -p tsconfig.app.json` → 0 erros (NÃO o `tsc --noEmit` raiz, que é cego em projetos com references)
- [ ] `npm test` → verde
- [ ] `npm run test:coverage` → gate do glob do domínio (≥80/70) passa
- [ ] `npm run build` → compila (valida aliases)
- [ ] `npm run lint` → sem novos erros; `no-explicit-any` = error no glob do domínio
- [ ] `grep supabase\.` fora da `api/` → vazio
- [ ] mensagens/textos idênticos ao commit anterior (produção viva)
- [ ] isolamento `organization_id` presente e testado
