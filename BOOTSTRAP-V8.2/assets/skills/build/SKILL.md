---
name: build
description: Executa uma task T.A.C.E despachando um subagent BUILDER com o handoff completo — arquivos, regras aplicáveis, skill de contexto e comando de teste. Sem argumento de task, pega a próxima pendente. Triggers "implementar", "executar task", "/build", "TASK-X.Y.Z". Do NOT use sem plano (use plan) nem para revisar (use ship).
---

# /build — **E**xecution

## Iron Law

**O HANDOFF CARREGA TUDO.** O subagent não deve procurar nada: arquivos, padrão a
imitar, regras aplicáveis e comando de teste vão no prompt. Handoff genérico é o que
força o executor a explorar o repositório — e explorar é onde ele alucina.

## Input

```
/build <feature>              # próxima task pendente
/build <feature> TASK-X.Y.Z   # task específica
```

Plano não salvo em arquivo: a task vem do plano da conversa. Funciona igual.

## Fluxo

### 1. Escolher a task

Próxima ⬜ na ordem de dependência. Se a anterior não está 🟡, pare e diga qual falta.

### 2. Montar o handoff

```
Task: TASK-X.Y.Z de <feature>
Deployable: <qual> · Módulo: <qual> · Camada: <qual>

T.A.C.E completo:
<colar T, A com Referência e Imports autorizados, C em EARS, E com comando>

Regras que valem aqui:
<as 2-4 de .context/arch/rules.md que se aplicam — citadas por número e texto curto>

Carregue a skill: <arch-backend | arch-frontend | arch-data | ...>
Padrão a imitar: <arquivo da Referência>
Rode só: <comando de teste desta task, de .context/arch/gates.md>

Proibido: tocar arquivo fora da seção A · marcar ✅ · commitar · rodar a suíte completa
Formato da resposta: bloco BUILD de .context/formats/response.md
```

**Nomeie a skill de contexto.** Não deixe o subagent escolher — skill não nomeada é
skill que pode não ser carregada, e aí ele perde o conhecimento da camada.

**Cite só as regras que se aplicam.** Despejar `rules.md` inteiro no handoff desfaz
o ganho: o executor lê 30 regras para usar 3.

### 3. Despachar

Um subagent BUILDER. Uma task por vez. **Sem review entre tasks** — o review é do
`/ship`, sobre o diff acumulado.

### 4. Receber

| Retorno | Ação |
|---|---|
| 🟡 com log preenchido e teste verde | Marcar 🟡 e seguir |
| Reportou arquivo faltando na seção A | **Corrija a task** e redespache. É lacuna de planejamento |
| Reportou decisão pendente | **Corrija a task** com a decisão tomada. Nunca mande "decida você" |
| Teste vermelho | Não avance. Task seguinte herda o defeito |

O teste isolado é o **único gate dentro do loop** — é o que impede um erro nesta
task de contaminar as próximas. Não relaxe nele.

### 5. Registrar

Plano salvo: o log do BUILDER vai na seção da task no work file.
Plano na conversa: o log fica na conversa — e é o que o `/ship` vai ler.

## Output

Bloco `BUILD` de `.context/formats/response.md`, terminando em:

```
➡️ /build <feature>           # próxima task
➡️ /ship <feature>            # se era a última
```

## Error handling

- Task depende de outra ⬜ → pare e diga qual
- Seção A cita arquivo que não existe e a task não diz "criar" → lacuna de planejamento, corrija a task
- BUILDER tocou arquivo fora de A → não aceite; reverta o extra ou promova o arquivo para a seção A explicitamente
- Skill de contexto nomeada não existe → crie-a ou aponte direto o arquivo de `arch/`
