# Passo 0 — Detectar e perguntar

## 0.1 Detectar

```bash
echo "--- spec ---"
find . -maxdepth 3 \( -name "spec.md" -o -name "SPEC.md" -o -name "spec.yaml" \) -not -path "*/node_modules/*" 2>/dev/null
echo "--- manifestos ---"
ls package.json composer.json pyproject.toml Cargo.toml go.mod pom.xml build.gradle 2>/dev/null
echo "--- estrutura AI existente ---"
ls -d .claude .codex .opencode .context AGENTS.md CLAUDE.md 2>/dev/null
echo "--- docs de padrão do projeto ---"
ls *.md 2>/dev/null | head -20
echo "--- git ---"
git rev-parse --abbrev-ref HEAD 2>/dev/null; git rev-parse --short HEAD 2>/dev/null
```

Depois: liste a árvore de pastas de cada deployable até 2 níveis, e leia os configs
de teste e lint. É de onde saem as camadas reais e os comandos de gate.

## 0.2 Cenário

| Cenário | Entrada | Comportamento |
|---|---|---|
| **A** | `spec.md` existe | A spec é a fonte da verdade. Extraia dela stack, módulos, camadas, regras, convenções. O código só confirma |
| **B** | Código sem spec | Infira de manifestos, estrutura de pastas, configs de teste/lint e dos documentos de padrão que o projeto já tiver |
| **C** | Estrutura AI-First já existe | NÃO sobrescreva conteúdo especializado. Acrescente o que falta, migre nomenclatura antiga, preserve regras escritas à mão |

## 0.3 Extrair

Colete, sempre com evidência de onde veio:

- `PROJECT_NAME`, `PROJECT_DESCRIPTION`
- **Deployables**: para cada um — path, linguagem, framework, comando de gate, stack de teste
- `DATABASE` e infraestrutura de apoio (cache, fila)
- **Camadas** de cada deployable, em ordem
- **Módulos** e o que cada um pode e não pode importar
- **Regras invioláveis** — e onde cada uma é reforçada (linter, script, teste)
- **Convenções** de código e de commit; idioma do projeto
- **Documentos canônicos** que o projeto já tem

> **Leia os documentos de padrão que encontrar.** Se o projeto já tem um documento
> canônico de arquitetura, ele é a sua fonte — **referencie**, não resuma. Resumo
> vira segunda fonte de verdade e envelhece sozinho.

## 0.4 Mostrar antes de perguntar

Apresente ao usuário o que entendeu: cenário, deployables com gate de cada um,
arquitetura, módulos, regras. Erro de detecção descoberto agora custa uma linha;
descoberto no Passo 5 custa reescrever tudo.

## 0.5 Perguntar

### 1. Design system?

| Resposta | Quando | Ação |
|---|---|---|
| `não` | Projeto sem UI | Não cria `.context/design/` nem a skill `design` |
| `derivar do projeto` | Já existe design system em código | Gere o `DESIGN.md` do repositório: tokens, componentes reutilizáveis, tipografia, libs em uso |
| `baixar do getdesign.md` | Projeto novo, sem identidade visual | Pergunte a referência do catálogo e busque `https://getdesign.md/<marca>/design-md` → `.context/design/DESIGN.md`. Marca fora do catálogo: registre a pendência, não invente |
| `arquivo customizado` | Já tem spec e modelos próprios | Aponte para o arquivo dele. Não gere nada por cima |

### 2. Ferramentas de AI?

`.claude` · `.codex` · `.opencode` — múltipla escolha. O `AGENTS.md` sai sempre.

### 3. Registro de decisões?

`sim` (recomendado) · `não`. Cria `.context/arch/decisions/` — o único artefato que
guarda o que o git não guarda: a alternativa descartada e o porquê.

### 4. TDD com evidência do vermelho?

`não` (padrão) · `sim`. Com `sim`, o campo E de toda task exige duas evidências:
o teste falhando antes e passando depois. Vale onde teste tautológico custa caro.

### 5. Idioma dos documentos gerados?

Detecte primeiro e **proponha**: o idioma dos comentários do código, dos commits e
dos documentos que o projeto já tem. Projeto costuma ser bilíngue (código em inglês,
prosa no idioma do time) — e nesse caso a resposta certa é a da prosa.

Confirme com o usuário, porque a escolha vale para tudo o que você vai gerar:
`arch/`, agents, skills e o `AGENTS.md`. **Exceção**: as cláusulas EARS do campo C
acompanham o idioma dos identificadores do código, para casarem com o que vai ser
implementado.

Sem essa pergunta, você escolhe por conta e ninguém autorizou.

> **Não pergunte sobre PRD nem changelog.** O PRD virou seção do work file ou uma
> decisão registrada. A visão diária é `git log --since=1.day`.

## Saída deste passo

Um bloco de contexto registrado na conversa, com todas as variáveis preenchidas e
as cinco respostas. Os passos seguintes consomem isso — não re-detecte.

> **Se o usuário forneceu as respostas de antemão** (execução automatizada), o item
> 0.4 "mostrar antes de perguntar" não tem para quem perguntar: registre o bloco de
> contexto na conversa de todo modo. Ele é o que os passos 1 a 6 consomem, e é onde
> um erro de detecção fica visível para quem ler depois.

➡️ Próximo: `assets/setup/1-structure.md`
