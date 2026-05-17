# 📂 Prompts Auxiliares

Prompts para usar **fora** do fluxo principal do `INDEX.md`.

## Quando usar

Estes prompts são úteis quando você já está conversando com uma IA sobre o projeto e quer capturar informações ou transformar ideias em prompts profissionais.

## Prompts disponíveis

| Prompt | Uso |
|---|---|
| [return-stack.md](./return-stack.md) | Pedir para a IA devolver a stack no formato `stack.yaml` |
| [prompt-generator.md](./prompt-generator.md) | Transformar texto/ideia/contexto em prompt profissional enterprise |
| [extract-prd.md](./extract-prd.md) | Extrair PRDs, SPECs, OpenAPI, fluxos e requisitos de código existente |

## Fluxo típico — return-stack

```
1. Conversa com IA sobre o projeto (stack, padrões, domínios)
2. Cola o prompt `return-stack.md`
   → A IA retorna a stack no formato stack.yaml
3. Salva como .context/stack.yaml
4. INDEX.md detecta que stack.yaml existe → pula para Fase 2
```

## Fluxo típico — prompt-generator

```
1. Cola `prompt-generator.md` no início de uma conversa
2. Envia qualquer texto: ideia, requisito, contexto de chat
   → A IA transforma em prompt profissional com:
     - Contexto, Objetivo, Requisitos detalhados
     - Mockup textual (wireframe ASCII)
     - Fluxograma (Mermaid)
     - Critérios de aceitação
     - Phases e Tasks
     - TODO List executável
3. Use o prompt gerado com qualquer IA para implementar
```

## Fluxo típico — extract-prd

```
1. Cola `extract-prd.md` numa conversa com acesso ao código
2. Indica o módulo/domínio que quer documentar
   → A IA analisa código e gera:
     - PRD completo em .context/docs/PRDs/NNNN-modulo.md
     - OpenAPI spec em .context/docs/api/modulo-api.yaml
     - Requisitos funcionais com evidência no código
     - Requisitos não-funcionais
     - Diagrama ER e fluxos (Mermaid)
     - Lacunas identificadas com severidade
     - Changelog com commit hash e branch
3. A documentação fica viva — @DEV e @REVERSE-ENGINEER
   atualizam automaticamente ao alterar o módulo
```

