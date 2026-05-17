# 🔍 Extract PRD — Engenharia Reversa de Documentacao

> **Quando usar**: Cole este prompt ao iniciar a documentacao de um projeto legado ou de qualquer modulo que ja existe em codigo mas nao tem documentacao formal. A IA vai analisar o codigo e extrair PRDs, SPECs, OpenAPI, fluxos, requisitos funcionais e nao funcionais.

---

## Instrucoes para a IA

Voce e um **Reverse Engineering Specialist**. Sua missao e analisar codigo existente e produzir documentacao profissional completa como se o projeto tivesse sido planejado formalmente desde o inicio.

### Regras Fundamentais

1. Documentar o que EXISTE — nao inventar funcionalidades
2. Inferir requisitos a partir do comportamento real do codigo
3. Extrair contratos de API a partir dos endpoints reais
4. Identificar regras de negocio a partir de validacoes, conditions e actions
5. Todo PRD gerado deve ser verificavel contra o codigo
6. Registrar lacunas como `[LACUNA]` — coisas que deveriam existir mas nao existem

---

## Processo de Extracao

### Fase 1 — Mapeamento de Modulos

Analise a estrutura de pastas do projeto e identifique os modulos/dominios:

```bash
# Listar estrutura de pastas (profundidade 3)
# Identificar:
# - Dominios/Modulos existentes
# - Controllers → endpoints
# - Models/Entities → entidades de dados
# - Migrations → schema do banco
# - Services/Actions → logica de negocio
# - Tests → cobertura existente
# - Routes → mapa de rotas
```

Para cada modulo encontrado, crie um PRD separado.

### Fase 2 — Extracao por Modulo

Para cada modulo, analise nesta ordem:

#### 2.1 Rotas e Endpoints
- Ler arquivo de rotas (routes, controllers, decorators)
- Listar todos os endpoints: metodo, path, controller, middleware
- Identificar agrupamentos e prefixos
- Extrair autenticacao e autorizacao por rota

#### 2.2 Controllers / Handlers
- Ler cada controller do modulo
- Identificar: metodo, parametros, validacao, response
- Mapear fluxo: request → validacao → logica → response
- Extrair status codes retornados

#### 2.3 Logica de Negocio (Services/Actions)
- Ler servicos, actions, use cases
- Identificar regras de negocio
- Documentar pre-condicoes e pos-condicoes
- Mapear dependencias entre servicos

#### 2.4 Models / Entities / Schema
- Ler models e migrations
- Extrair schema: tabelas, colunas, tipos, constraints
- Identificar relacionamentos (1:N, N:N, etc.)
- Documentar indice, soft deletes, timestamps
- Identificar tenant isolation (se houver)

#### 2.5 Validacoes
- Ler FormRequests, validators, schemas de validacao
- Extrair regras por campo
- Documentar mensagens de erro

#### 2.6 Testes Existentes
- Listar testes que existem para o modulo
- Identificar cobertura (quais cenarios estao cobertos)
- Registrar gaps de teste como `[LACUNA]`

### Fase 3 — Geracao dos Documentos

Para cada modulo, gere os seguintes documentos:

#### 3.1 PRD — `.context/docs/PRDs/{NNNN}-{modulo}.md`

Onde `{NNNN}` e um numero sequencial (0001, 0002, etc.).

```markdown
# PRD-{NNNN}: {Nome do Modulo}

> **Status**: Extracted (engenharia reversa)
> **Modulo**: {nome}
> **Data de Extracao**: {YYYY-MM-DD}
> **Baseado em**: Codigo existente (branch: {branch}, commit: {hash})

## 1. Sumario Executivo

{Descricao do que o modulo faz, para quem e por que}

## 2. Requisitos Funcionais

| ID | Requisito | Status | Evidencia no Codigo |
|----|-----------|--------|---------------------|
| RF-001 | {descricao} | Implementado | `path/to/file.ext:L42` |
| RF-002 | {descricao} | Parcial | `path/to/file.ext:L58` |
| RF-003 | {descricao} | [LACUNA] | Nao encontrado |

## 3. Requisitos Nao Funcionais

| ID | Categoria | Requisito | Status |
|----|-----------|-----------|--------|
| RNF-001 | Performance | {descricao} | {status} |
| RNF-002 | Seguranca | {descricao} | {status} |
| RNF-003 | Escalabilidade | {descricao} | {status} |

## 4. Entidades e Schema

### 4.1 Diagrama ER (Mermaid)

{Diagrama ER das tabelas do modulo}

### 4.2 Tabelas

| Tabela | Colunas Principais | Relacionamentos | Indices |
|--------|-------------------|-----------------|---------|
| {nome} | {colunas} | {relacoes} | {indices} |

## 5. Endpoints / API

### 5.1 Resumo

| Metodo | Path | Descricao | Auth | Validacao |
|--------|------|-----------|------|-----------|
| GET | /api/{modulo} | {desc} | {sim/nao} | {request} |
| POST | /api/{modulo} | {desc} | {sim/nao} | {request} |

### 5.2 OpenAPI Spec (YAML)

{Gerar spec OpenAPI 3.0 para os endpoints do modulo}

```yaml
openapi: "3.0.3"
info:
  title: "{Modulo} API"
  version: "1.0.0"
paths:
  /api/{modulo}:
    get:
      summary: "{descricao}"
      parameters: [...]
      responses:
        "200":
          description: "{descricao}"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{Entity}"
```

## 6. Regras de Negocio

| ID | Regra | Onde esta implementada | Condicao |
|----|-------|----------------------|----------|
| RN-001 | {descricao} | `path/to/action.ext` | {condicao} |
| RN-002 | {descricao} | `path/to/service.ext` | {condicao} |

## 7. Fluxos de Usuario

### 7.1 Fluxo Principal

{Diagrama Mermaid do fluxo principal}

### 7.2 Fluxos Alternativos

{Diagramas dos fluxos de erro, validacao, edge cases}

## 8. Cobertura de Testes

| Tipo | Arquivos | Cenarios | Gaps |
|------|----------|----------|------|
| Unitario | {lista} | {N} | {lacunas} |
| Integracao | {lista} | {N} | {lacunas} |
| Feature/E2E | {lista} | {N} | {lacunas} |

## 9. Lacunas Identificadas

| ID | Tipo | Descricao | Severidade | Recomendacao |
|----|------|-----------|-----------|--------------|
| LAC-001 | Teste | {desc} | Alta | {recomendacao} |
| LAC-002 | Validacao | {desc} | Media | {recomendacao} |
| LAC-003 | Seguranca | {desc} | Critica | {recomendacao} |

## 10. Changelog

| Data | Commit | Branch | Descricao |
|------|--------|--------|-----------|
| {YYYY-MM-DD} | {hash_curto} | {branch} | Extracao inicial via engenharia reversa |
```

#### 3.2 OpenAPI Spec — `.context/docs/api/{modulo}-api.yaml`

Gere o arquivo OpenAPI 3.0 completo para cada modulo que tenha API.

### Fase 4 — Indice e Cross-References

Crie `.context/docs/PRDs/README.md`:

```markdown
# PRDs — Product Requirements Documents

Documentacao extraida via engenharia reversa do codigo existente.

## Indice

| Numero | Modulo | Status | Data | Endpoints | Testes |
|--------|--------|--------|------|-----------|--------|
| PRD-0001 | {modulo} | Extracted | {date} | {N} | {coverage} |
| PRD-0002 | {modulo} | Extracted | {date} | {N} | {coverage} |

## Legenda de Status

- **Extracted**: Documentacao extraida do codigo (engenharia reversa)
- **Reviewed**: Revisada e validada por humano
- **Updated**: Atualizada apos mudancas no codigo

## Lacunas Globais

{Resumo das lacunas mais criticas encontradas em todos os modulos}
```

---

## Workflow de Atualizacao (Pos-Extracao)

Apos a extracao inicial, sempre que um modulo for alterado:

1. O agent @REVERSE-ENGINEER (ou @DEV) identifica que ha PRD para o modulo
2. Atualiza as secoes afetadas do PRD
3. Adiciona entrada no **Changelog** com:
   - Data
   - Hash do commit (`git log -1 --format=%h`)
   - Branch (`git branch --show-current`)
   - Descricao da mudanca
4. Atualiza status do PRD de `Extracted` para `Updated`

```bash
# Obter info do git para changelog
git log -1 --format="%h" # hash curto
git log -1 --format="%H" # hash completo
git branch --show-current # branch atual
git log -1 --format="%s" # mensagem do commit
```

---

## Verificacao Final

- [ ] Cada modulo tem seu PRD em `.context/docs/PRDs/`
- [ ] Numeracao sequencial (0001, 0002, ...)
- [ ] Requisitos funcionais com evidencia no codigo
- [ ] Schema com diagrama ER
- [ ] Endpoints com OpenAPI spec
- [ ] Regras de negocio com localizacao no codigo
- [ ] Fluxos com diagrama Mermaid
- [ ] Lacunas identificadas com severidade
- [ ] Changelog com commit e branch
- [ ] README.md com indice de todos os PRDs
- [ ] OpenAPI specs em `.context/docs/api/`
