# SDD/AI Bootstrap V6 — Layered Context Edition

> Bootstrap AI-First para desenvolvimento com Claude Code, Codex CLI e OpenCode.
> Esta versão cria uma arquitetura de contexto em camadas, preserva PREVC e T.A.C.E, mas evita excesso de tokens, comandos rígidos e documentação operacional desnecessária.

---

## SUA MISSÃO

Configurar uma estrutura AI-First para este projeto, otimizada para desenvolvimento com agentes de IA.

A estrutura deve funcionar bem com:

- Claude Code
- Codex CLI
- OpenCode

Cada ferramenta deve receber sua própria área de configuração, instruções e materiais de apoio quando necessário, respeitando suas convenções.

A estrutura deve preservar:

- PREVC como workflow para features médias e grandes
- T.A.C.E como framework para decomposição de tasks
- MEMORY como memória persistente de conhecimento relevante
- ARCHITECTURE como camada de contexto técnico do projeto
- AGENTS.md como kernel mínimo de instruções
- Contexto em camadas para reduzir consumo de tokens

A estrutura não deve obrigar a IA a carregar contexto profundo por padrão.

Regra central da V6:

> Contexto não é carregado. Contexto é roteado.

---

# 1. PRINCÍPIOS DA V6

A estrutura gerada deve seguir estes princípios:

1. Começar sempre com o menor contexto possível.
2. Usar `AGENTS.md` como kernel mínimo, não como documentação completa.
3. Guardar contexto profundo em `.context/`.
4. Usar skills/instruções sob demanda para tarefas específicas.
5. Usar commands/prompts como entradas operacionais, quando a ferramenta suportar.
6. Manter agents/personas opcionais, pequenos e específicos.
7. Usar PREVC apenas para features médias e grandes.
8. Usar Fast Path para bugs pequenos e ajustes simples.
9. Usar T.A.C.E para tasks de implementação.
10. Suportar Claude Code, Codex CLI e OpenCode.
11. Nunca gerar conteúdo genérico quando houver contexto real do projeto.
12. Nunca sobrescrever arquivos especializados existentes sem preservar ou considerar o conteúdo anterior.
13. Não manter changelog operacional.
14. Registrar em MEMORY apenas conhecimento relevante e reutilizável.
15. Evitar comandos rígidos quando instruções forem suficientes.
16. A IA deve decidir como executar tecnicamente o objetivo, desde que entregue a estrutura esperada.

---

# 2. O QUE NÃO FAZER

A V6 não deve:

- Criar um `AGENTS.md` gigante.
- Colocar arquitetura completa dentro do `AGENTS.md`.
- Colocar PRD completo dentro do `AGENTS.md`.
- Criar changelog de ações.
- Registrar qualquer pequena alteração em MEMORY.
- Criar código de hook obrigatório.
- Criar scripts obrigatórios.
- Forçar comandos específicos como única forma de execução.
- Forçar PREVC para bugs pequenos.
- Carregar toda a pasta `.context` no início da conversa.
- Criar agents grandes e repetitivos para tudo.
- Duplicar instruções longas em Claude, Codex e OpenCode.
- Transformar o bootstrap em um executor de shell.
- Tratar MEMORY como log de tarefas.

---

# 3. DETECÇÃO DO PROJETO

Antes de gerar a estrutura, a IA deve entender o projeto real.

A IA deve identificar:

- Nome do projeto
- Descrição do projeto
- Stack principal
- Backend
- Frontend
- Banco de dados
- Cache/fila
- Infraestrutura
- Frameworks
- Gerenciadores de pacotes
- Ferramentas de teste
- Linters e formatadores
- Arquitetura predominante
- Módulos ou bounded contexts
- Convenções de código existentes
- Regras de negócio importantes
- Áreas sensíveis
- Estruturas AI já existentes
- Ferramentas de agente usadas no projeto:
  - Claude Code
  - Codex CLI
  - OpenCode

A IA pode usar inspeção do repositório, leitura de arquivos existentes, manifestos, specs, README, estruturas de pasta e padrões de código para inferir esses dados.

A IA não deve inventar stack, módulos ou regras quando não houver evidência suficiente.

Quando algo não puder ser detectado com segurança, deve marcar como `unknown` ou `to_be_confirmed`.

---

# 4. CENÁRIOS DE PROJETO

A IA deve classificar o projeto em um dos cenários abaixo.

## Cenário A — Projeto novo com spec

Existe um arquivo de especificação, como:

- `spec.md`
- `SPEC.md`
- `spec.yaml`
- documento equivalente

Neste caso:

- A spec deve ser a principal fonte de verdade.
- A estrutura deve ser gerada com base na spec.
- As decisões devem refletir o que está descrito na spec.
- O código existente, se houver, deve ser usado como validação secundária.

## Cenário B — Projeto existente com código

Existe código, mas não há spec clara.

Neste caso:

- A IA deve inferir a arquitetura a partir do código.
- Deve analisar padrões existentes antes de criar instruções.
- Deve priorizar o que o projeto já faz, não o que seria ideal em teoria.
- Deve evitar impor uma arquitetura diferente sem evidência.

## Cenário C — Projeto já possui estrutura AI

Existe alguma estrutura como:

- `.claude/`
- `.codex/`
- `.opencode/`
- `.context/`
- `AGENTS.md`
- `CLAUDE.md`
- arquivos equivalentes

Neste caso:

- A IA deve preservar conteúdo existente.
- Deve complementar lacunas.
- Deve evitar sobrescrever instruções especializadas.
- Deve consolidar duplicações quando fizer sentido.
- Deve manter compatibilidade com a estrutura anterior quando possível.

---

# 5. ESTRUTURA ESPERADA

A IA deve gerar uma estrutura parecida com esta, adaptada ao projeto real e às ferramentas utilizadas:

```text
project-root/
├─ AGENTS.md
├─ CLAUDE.md
├─ .context/
│  ├─ CONTEXT_INDEX.md
│  ├─ ARCHITECTURE/
│  │  ├─ project-brain.yaml
│  │  ├─ project-state.yaml
│  │  ├─ modules.yaml
│  │  ├─ dependencies.yaml
│  │  └─ architecture.mmd
│  ├─ WORKFLOW/
│  │  ├─ PREVC.md
│  │  ├─ TACE.md
│  │  ├─ task-classification.md
│  │  └─ validation-flow.md
│  ├─ DOCS/
│  │  ├─ FEATURES/
│  │  ├─ TASKS/
│  │  ├─ PRDS/
│  │  └─ MEMORY/
│  └─ LAYOUT/
├─ .claude/
│  ├─ commands/
│  ├─ skills/
│  └─ agents/
├─ .codex/
│  ├─ prompts/
│  ├─ skills/
│  └─ context/
└─ .opencode/
   ├─ command/
   ├─ skill/
   ├─ agent/
   └─ context/
```

A estrutura pode variar conforme a ferramenta e o projeto.

A IA deve criar somente o que for útil.

Se uma ferramenta não estiver sendo usada no projeto, a IA pode criar uma estrutura mínima ou marcar como opcional.

---

# 6. AGENTS.md — AI KERNEL

O `AGENTS.md` deve ser o arquivo mínimo sempre carregado.

Ele deve conter apenas:

- Papel geral da IA
- Idioma de resposta
- Resumo curto do projeto
- Regras essenciais
- Política de contexto
- Quando usar Fast Path
- Quando usar PREVC
- Quando usar T.A.C.E
- Onde encontrar contexto adicional
- Compatibilidade com Claude, Codex e OpenCode

O `AGENTS.md` não deve conter:

- PRD completo
- Arquitetura completa
- Histórico do projeto
- Lista longa de comandos
- Exemplos extensos de código
- Documentação de negócio detalhada
- Memórias antigas
- Conteúdo duplicado de outros arquivos

## Conteúdo esperado do AGENTS.md

O `AGENTS.md` deve comunicar:

```text
Você é um agente de desenvolvimento sênior trabalhando neste repositório.

Responda em português brasileiro.

Use contexto mínimo por padrão.

Não leia o projeto inteiro sem necessidade.

Procure antes de abrir arquivos grandes.

Preserve padrões existentes.

Use PREVC para features médias/grandes.

Use Fast Path para bugs pequenos.

Use T.A.C.E para tasks de implementação.

Consulte `.context/CONTEXT_INDEX.md` para decidir qual contexto carregar.

Não registre logs operacionais.

Use MEMORY apenas para conhecimento relevante e reutilizável.
```

---

# 7. CONTEXT_INDEX.md — MAPA DE CAMADAS

A V6 deve criar `.context/CONTEXT_INDEX.md`.

Este arquivo é obrigatório.

Ele deve explicar quando carregar cada camada de contexto.

## Camadas esperadas

### Layer 0 — Kernel

Sempre carregado:

- `AGENTS.md`

Uso:

- Regras essenciais
- Política de contexto
- Segurança
- Decisão inicial de fluxo

### Layer 1 — Project Brain

Carregar quando precisar entender o projeto.

Arquivos esperados:

- `.context/ARCHITECTURE/project-brain.yaml`
- `.context/ARCHITECTURE/project-state.yaml`

Uso:

- Stack
- Identidade
- Arquitetura resumida
- Convenções principais
- Áreas sensíveis

### Layer 2 — Architecture

Carregar quando houver risco arquitetural.

Arquivos esperados:

- `.context/ARCHITECTURE/modules.yaml`
- `.context/ARCHITECTURE/dependencies.yaml`
- `.context/ARCHITECTURE/architecture.mmd`

Uso:

- Mudança multi-módulo
- Novo módulo
- Mudança de dependência
- Banco de dados
- Contratos
- Integrações
- Regras estruturais

### Layer 3 — Product / Feature

Carregar quando a tarefa envolver produto ou escopo.

Arquivos esperados:

- `.context/DOCS/FEATURES/`
- `.context/DOCS/PRDS/`

Uso:

- Planejar feature
- Ver critérios de aceite
- Entender escopo
- Validar regra de negócio

### Layer 4 — Tasks

Carregar quando houver execução de task.

Arquivos esperados:

- `.context/DOCS/TASKS/`

Uso:

- Implementar TASK específica
- Ler T.A.C.E
- Ver evidências esperadas

### Layer 5 — Workflow

Carregar quando a tarefa exigir processo formal.

Arquivos esperados:

- `.context/WORKFLOW/PREVC.md`
- `.context/WORKFLOW/TACE.md`
- `.context/WORKFLOW/task-classification.md`
- `.context/WORKFLOW/validation-flow.md`

Uso:

- Planejar
- Revisar
- Executar
- Validar
- Confirmar
- Classificar complexidade

### Layer 6 — Memory

Carregar quando houver decisão técnica, dúvida recorrente ou risco.

Arquivos esperados:

- `.context/DOCS/MEMORY/`

Uso:

- Ver decisões anteriores
- Evitar repetir erros
- Entender padrões não óbvios
- Consultar aprendizados relevantes

### Layer 7 — Source Code

Carregar quando a execução exigir código.

Uso:

- Debug
- Implementação
- Testes
- Refatoração
- Validação real

Regra:

- Buscar primeiro.
- Abrir apenas arquivos diretamente relacionados.
- Preferir padrões existentes.

### Layer 8 — External Knowledge / MCP

Carregar quando o conhecimento local não for suficiente.

Uso:

- Documentação oficial
- APIs recentes
- Frameworks com versões atuais
- Context7
- MCPs relevantes

---

# 8. PREVC

A V6 deve manter PREVC como workflow oficial para features médias e grandes.

PREVC significa:

```text
Planning → Review → Execution → Validation → Confirm
```

## Planning

Objetivo:

- Entender problema
- Definir escopo
- Identificar impacto
- Consultar memória relevante se houver decisão
- Criar ou atualizar feature doc

Saída esperada:

- Feature documentada
- Escopo claro
- Critérios de aceite
- Riscos conhecidos
- Impacto técnico inicial

## Review

Objetivo:

- Validar escopo
- Validar arquitetura
- Validar dependências
- Identificar lacunas
- Decompor em tasks T.A.C.E

Saída esperada:

- Feature aprovada ou ajustada
- Tasks claras
- Riscos documentados
- Dependências explícitas

## Execution

Objetivo:

- Implementar tasks
- Seguir T.A.C.E
- Manter alterações pequenas e seguras
- Respeitar arquitetura e padrões existentes

Saída esperada:

- Código ou alteração realizada
- Testes ou validações aplicáveis
- Evidência técnica da execução

## Validation

Objetivo:

- Validar comportamento
- Rodar testes/lint/build quando aplicável
- Verificar critérios de aceite
- Reprovar se evidência for insuficiente

Saída esperada:

- Evidência de validação
- Critérios confirmados ou pendências claras

## Confirm

Objetivo:

- Fechar a task ou feature
- Registrar evidências finais
- Atualizar estado do projeto se necessário
- Registrar MEMORY apenas se houve conhecimento relevante

Saída esperada:

- Task/feature marcada como concluída
- Evidências preservadas
- MEMORY atualizado somente quando aplicável

---

# 9. FAST PATH

A V6 deve prever um fluxo rápido para tarefas pequenas.

Usar Fast Path quando a tarefa for:

- Bug pequeno
- Ajuste visual simples
- Correção de texto
- Rename
- Pequena validação
- Alteração de baixo risco
- Mudança localizada

Fluxo:

```text
Detect → Fix → Validate → Summary
```

O Fast Path não deve exigir:

- PRD
- Feature doc completa
- PREVC completo
- Decomposição extensa
- Registro em MEMORY
- Registro histórico operacional

Saída esperada:

- Causa identificada
- Correção pequena
- Validação proporcional
- Resumo objetivo

---

# 10. T.A.C.E

A V6 deve preservar T.A.C.E para tasks de implementação.

Toda task técnica relevante deve conter:

## T — Tarefa

O que deve ser feito.

Deve ser:

- Clara
- Pequena
- Verificável
- Sem ambiguidade

## A — Arquivo / Área

Onde a mudança deve ocorrer.

Pode conter:

- Arquivos conhecidos
- Módulos
- Rotas
- Services
- Components
- Tabelas
- Migrations
- Testes
- Áreas prováveis

## C — Comportamento

Como o sistema deve se comportar.

Deve conter:

- Antes
- Depois
- Regras
- Restrições
- Edge cases

## E — Evidência

Como provar que está pronto.

Pode conter:

- Teste automatizado
- Teste manual
- Build
- Lint
- Comando de validação
- Screenshot
- Evidência de banco
- Evidência de API
- Critério observável

---

# 11. MEMORY

A V6 não deve criar CHANGELOG.

A V6 deve usar apenas MEMORY como memória persistente.

Mas MEMORY não é log de ações.

MEMORY deve guardar somente conhecimento relevante e reutilizável.

## O que deve ir para MEMORY

Registrar em MEMORY quando houver:

- Decisão técnica importante
- Decisão de arquitetura
- Escolha entre alternativas
- Regra de negócio não óbvia
- Padrão de implementação reutilizável
- Armadilha descoberta
- Bug difícil com causa relevante
- Integração com comportamento inesperado
- Convenção importante do projeto
- Restrição sensível
- Aprendizado que evitará erro futuro
- Trade-off relevante

## O que NÃO deve ir para MEMORY

Não registrar:

- Toda task concluída
- Toda alteração pequena
- Correção trivial
- Mudança visual simples
- Rodada de teste comum
- Log diário
- “Arquivo X foi alterado”
- Histórico operacional
- Ações sem aprendizado reutilizável
- Coisas óbvias pelo próprio código
- Informações temporárias

## Formato esperado da MEMORY

Cada memória deve conter:

- Título claro
- Tipo:
  - Decisão
  - Aprendizado
  - Armadilha
  - Padrão
  - Regra de negócio
  - Integração
- Data
- Contexto
- Situação
- Conhecimento registrado
- Alternativas consideradas, se houver
- Consequências
- Quando consultar novamente
- Referências relacionadas

## Exemplo de MEMORY boa

```text
Título:
Normalização de telefones deve usar E.164 por organização

Tipo:
Decisão técnica / Regra de negócio

Situação:
Chamados, conversas e contatos estavam criando duplicidades por variação de telefone.

Conhecimento:
Todo telefone deve ser normalizado antes de vincular crm_contacts, conversations e tickets.

Consequência:
Evita duplicidade e garante que o botão editar contato sempre abra o contato real.

Quando consultar:
Sempre que mexer em contatos, conversas, tickets, WhatsApp ou CRM.
```

## Exemplo de MEMORY ruim

```text
Hoje alterei o arquivo ContactController.php.
```

Motivo:

- Isso é log operacional.
- Não contém aprendizado reutilizável.
- Não deve ser salvo.

---

# 12. PROJECT BRAIN

A V6 deve criar `.context/ARCHITECTURE/project-brain.yaml`.

Este arquivo deve ser um resumo estruturado do projeto.

Deve conter:

- Nome
- Descrição
- Tipo de produto
- Domínio de negócio
- Stack
- Arquitetura
- Camadas
- Módulos principais
- Regras de negócio relevantes
- Convenções importantes
- Áreas sensíveis
- Integrações externas
- Decisões principais, se detectadas

O `project-brain.yaml` deve ser curto o suficiente para consulta rápida.

Ele não deve virar documentação completa.

---

# 13. PROJECT STATE

A V6 pode criar `.context/ARCHITECTURE/project-state.yaml`.

Este arquivo deve guardar estado de alto nível do projeto.

Pode conter:

- Feature atual
- Task atual
- Módulos ativos
- Áreas em risco
- Última validação relevante
- Pendências importantes
- Status geral

Não deve conter log detalhado de ações.

---

# 14. ARCHITECTURE

A V6 deve criar arquivos de arquitetura quando fizer sentido.

Arquivos esperados:

- `modules.yaml`
- `dependencies.yaml`
- `architecture.mmd`

Esses arquivos devem refletir o projeto real.

Não usar DDD se o projeto não usa DDD.

Não inventar microserviços se o projeto é monólito.

Não inventar módulos sem evidência.

Não criar diagramas complexos sem necessidade.

A arquitetura deve ajudar a IA a evitar decisões ruins, não virar documentação pesada.

---

# 15. FEATURES

A V6 deve criar área para features.

Features devem ser usadas para:

- Escopo de produto
- Critérios de aceite
- Regras de negócio
- Impacto técnico
- Riscos
- Relação com tasks

Feature docs não devem ser exigidos para bugs pequenos.

Feature docs devem ser usados em PREVC Lite ou PREVC Full.

---

# 16. TASKS

A V6 deve criar área para tasks.

Tasks devem seguir T.A.C.E.

Cada task deve ser pequena, verificável e implementável.

A task deve ser clara o suficiente para outro agente executar sem reler toda a feature.

Task ruim:

```text
Melhorar contatos.
```

Task boa:

```text
TASK-001 — Garantir contact_id em conversations criadas pelo chat público

T:
Criar ou vincular crm_contact ao iniciar conversa pública.

A:
Área de criação de conversa pública, contato CRM e persistência da conversation.

C:
Antes: conversation pode ser criada sem contact_id.
Depois: toda conversation pública deve possuir contact_id válido.

E:
Teste cria conversa pública e verifica contact_id preenchido.
```

---

# 17. PRDS

A V6 pode criar área para PRDs.

Deve existir:

- PRD Light
- PRD Full

## PRD Light

Usar para a maioria das features.

Deve conter:

- Problema
- Objetivo
- Solução
- Usuários impactados
- Requisitos funcionais
- Requisitos não funcionais importantes
- Critérios de aceite
- Fora de escopo
- Riscos

## PRD Full

Usar apenas para features grandes, estratégicas ou complexas.

Deve conter:

- Visão geral
- Problema
- Solução
- Personas
- Requisitos funcionais
- Requisitos não funcionais
- Wireframes/layout
- Dependências
- Riscos
- Cronograma
- Revisões

A IA não deve usar PRD Full para toda pequena mudança.

---

# 18. CLAUDE CODE

A V6 deve criar estrutura compatível com Claude Code.

A área `.claude/` deve conter, quando útil:

- commands
- skills
- agents
- instruções específicas

A V6 deve criar ou referenciar `CLAUDE.md`.

`CLAUDE.md` deve apontar para `AGENTS.md` ou conter instrução mínima equivalente.

A estrutura Claude não deve duplicar todo o conteúdo do `.context`.

O objetivo da pasta `.claude/` é adaptar o projeto ao Claude Code, não virar outra fonte de verdade completa.

---

# 19. CODEX CLI

A V6 deve criar estrutura compatível com Codex CLI.

A área `.codex/` deve conter, quando útil:

- prompts
- skills
- context
- instruções específicas do Codex

O Codex deve seguir `AGENTS.md` como kernel comum.

A pasta `.codex/` deve conter adaptações específicas para o fluxo do Codex, sem duplicar toda a documentação.

Quando uma skill existir para Claude e também for útil no Codex, a V6 deve criar uma versão equivalente e enxuta para Codex.

---

# 20. OPENCODE

A V6 deve criar estrutura compatível com OpenCode.

A área `.opencode/` deve conter, quando útil:

- command
- skill
- agent
- context
- instruções específicas do OpenCode

O OpenCode deve seguir `AGENTS.md` como kernel comum.

A pasta `.opencode/` deve conter apenas adaptações necessárias ao OpenCode.

Não duplicar todo o contexto do projeto dentro de `.opencode`.

---

# 21. SKILLS

A V6 deve criar skills como instruções sob demanda.

Skills devem ser pequenas, focadas e operacionais.

Skills recomendadas:

- detect-project
- write-feature
- decompose-tace
- implement-task
- debug-fix
- backend-task
- frontend-task
- db-migration
- qa-validation
- confirm-task
- memory-record
- architecture-review

Cada skill deve conter:

- Propósito
- Quando usar
- Contexto que pode carregar
- Contexto que não deve carregar
- Workflow esperado
- Saída esperada
- Critérios de qualidade

Skills não devem conter:

- Código desnecessário
- Scripts obrigatórios
- Exemplos enormes
- Conteúdo duplicado do workflow
- Regras genéricas demais

---

# 22. COMMANDS / PROMPTS

A V6 pode criar commands ou prompts quando a ferramenta suportar.

Eles devem ser entradas operacionais para tarefas comuns.

Commands/prompts recomendados:

- feature
- task
- fix
- review
- validate
- confirm
- context
- status
- memory

Cada command/prompt deve informar:

- Objetivo
- Quando usar
- Qual contexto carregar
- Qual contexto evitar
- Saída esperada

Eles não devem obrigar uma sequência de shell commands.

Eles devem orientar a IA sobre o resultado esperado.

A IA decide como chegar ao objetivo usando as capacidades da ferramenta.

---

# 23. AGENTS / PERSONAS

Agents/personas são opcionais.

Se criados, devem ser pequenos.

Agents recomendados:

- ORCHESTRATOR
- ARCHITECT
- IMPLEMENTER
- REVIEWER
- QA
- DOC

Não criar agents longos para cada tecnologia se uma skill resolver melhor.

Agents devem conter:

- Missão
- Quando usar
- Limites
- Saída esperada
- Contexto permitido

Agents não devem conter:

- Documentação completa
- Regras duplicadas do AGENTS.md
- Longos exemplos
- Histórico do projeto

---

# 24. VALIDATION FLOW

A V6 deve criar um validation-flow.

O validation-flow deve orientar como validar alterações.

Ele deve ser adaptado à stack real.

Deve conter:

- Validações backend
- Validações frontend
- Validações banco
- Validações integração
- Validações manuais
- Critério para escolher validação pequena ou completa

Ele não deve obrigar sempre rodar tudo.

Regra:

> Validar proporcionalmente ao risco da mudança.

---

# 25. OUTPUT ESPERADO DO BOOTSTRAP

Ao concluir, a IA deve entregar um resumo do que foi criado.

O resumo deve conter:

- Estrutura criada
- Ferramentas configuradas:
  - Claude Code
  - Codex CLI
  - OpenCode
- Arquivos principais
- Como usar o fluxo no dia a dia
- Quando usar Fast Path
- Quando usar PREVC
- Quando registrar MEMORY
- O que ficou pendente ou desconhecido
- Pontos que precisam de confirmação humana

Não deve entregar:

- Log linha a linha
- Changelog
- Lista enorme de ações internas
- Comandos executados sem necessidade
- Texto inflado

---

# 26. CRITÉRIOS DE QUALIDADE DA V6

A estrutura gerada será considerada boa se:

1. O AGENTS.md for curto e útil.
2. O CONTEXT_INDEX.md orientar bem o carregamento de contexto.
3. O PREVC continuar disponível sem ser obrigatório para tudo.
4. O T.A.C.E estiver claro para tasks.
5. Claude Code tiver sua estrutura.
6. Codex CLI tiver sua estrutura.
7. OpenCode tiver sua estrutura.
8. MEMORY existir, mas não virar log operacional.
9. Não existir CHANGELOG.
10. Skills forem pequenas e sob demanda.
11. Commands/prompts orientarem resultado, não execução rígida.
12. Arquivos refletirem o projeto real.
13. O projeto não carregar contexto profundo por padrão.
14. O setup ajudar a economizar tokens.
15. A IA souber onde buscar contexto quando necessário.

---

# 27. REGRA FINAL

A V6 deve gerar uma estrutura que ensina a IA a trabalhar bem no projeto.

Ela não deve tentar executar tudo com comandos fixos.

Ela deve definir:

- o que precisa existir
- por que precisa existir
- quando usar cada camada
- qual saída é esperada
- quais limites respeitar

A IA responsável pela execução decide o melhor caminho técnico para criar os arquivos, adaptar formatos e preservar o projeto existente.

Resultado esperado:

> Um projeto preparado para desenvolvimento agentic com Claude Code, Codex CLI e OpenCode, usando contexto em camadas, PREVC, T.A.C.E e MEMORY relevante, com baixo consumo de tokens e sem burocracia operacional desnecessária.
