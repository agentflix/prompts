<!--
Contrato de resposta do PREVEC V8. Instalado em .context/formats/response.md
Referenciado por AGENTS.md e pelos 3 agents. NÃO copiar o conteúdo para eles.

Regra: toda ação concluída termina num destes blocos. Sempre os mesmos campos,
sempre na mesma ordem — é o que permite bater o olho e saber onde está.
Campo sem conteúdo real fica com "—", nunca é omitido nem preenchido com enfeite.
-->

# Contrato de resposta

Cinco blocos, um por tipo de entrega. O último campo é **sempre** o próximo comando
com argumentos reais — nunca "prossiga" ou "me avise".

---

## 1. CLARIFY — antes de existir plano

```
## Clarify — <assunto>

**Entendi assim:** <1-2 linhas do problema, com suas palavras>

**Lacunas** (preciso da sua resposta)
1. <pergunta objetiva> — assumo <default> se você não responder
2. <pergunta objetiva>

**Decisões que tomei** (não precisam de você, mas você pode discordar)
- <decisão> — porque <motivo em meia linha>

**Riscos**
- <o que quebra, e quem consome o que vai mudar>

**Fora de escopo:** <o que alguém assumiria que entra e não entra>

➡️ Responda as lacunas, ou diga "assume os defaults" para eu seguir
```

---

## 2. PLAN — plano pronto, aguardando duas decisões

```
## Plano — <feature>  ·  tamanho <XS|S|M|L>

<o plano completo, no formato de .context/formats/plan.md>

---
**1. Executar direto?**
- `executar` → começo o /build agora; o plano fica só nesta conversa
- `salvar` → gravo em .context/work/<feature>.md e paro, para retomar depois

**2. Revisar o plano antes de executar?**
- `revisar` → REVIEWER audita as tasks antes do primeiro /build
- `pular` → sigo sem review do plano

Recomendo <executar|salvar> e <revisar|pular> porque <motivo em uma linha>.
```

> Recomendação: **executar** em XS/S/M, **salvar** em L ou quando o trabalho não cabe
> numa sessão; **revisar** em M/L, **pular** em XS/S. Sempre pergunte as duas — a
> decisão é do usuário. Se ele já respondeu na mensagem ("executa direto", "sem
> review"), não pergunte de novo.

---

## 3. BUILD — task concluída

```
## TASK-X.Y.Z — <título>  ·  🟡 aguarda review da feature

**Feito:** <o que mudou de comportamento, 1-2 linhas — não a lista de arquivos>

**Arquivos**
- `path/arquivo.ext` — <o que mudou nele em meia linha>

**Evidência**
```
$ <comando exato>
<resultado real, colado>
```

**Decisões que fui obrigado a tomar:** <ou "—">
**Não coberto:** <escopo que apareceu e ficou de fora, ou "—">
**Para o review:** <edge case, risco, dívida criada, ou "—">

➡️ Próxima: /build <feature>
➡️ Se era a última: /ship <feature>
```

---

## 4. SHIP — feature fechada

```
## <feature> — fechada  ·  <N> tasks ✅

**Entregue:** <o que passou a ser verdade no sistema, 2-3 linhas>

**Review**
- 7 revisores: <N> bloqueantes, <N> médios, <N> baixos | ⏭️ pulados pelo usuário
- Escopo: diff dentro da união das seções A ✅ | remoções não pedidas: <N>
- Contrato entre tasks: <verificado, sem quebra | o que foi encontrado>

**Gates**
- <deployable>: `<comando>` → <resultado>

**Delta de arquitetura aplicado**
- <ADDED|MODIFIED|REMOVED> `arch/<arquivo>`: <o que mudou>
- <ou "— nenhum: a feature não alterou a arquitetura">

**Commit:** <hash> · **PR:** <url>
**Decisão registrada:** <arquivo em decisions/, ou "—">

➡️ /plan <próximo problema>
```

---

## 5. REPROVADO — review encontrou bloqueante

```
## <feature> — reprovado  ·  <N> bloqueantes

1. **[TASK-X.Y.Z]** `arquivo:linha` — <problema>
   Evidência: <o que prova>
   Correção: <o que fazer>
   Origem: <defeito de execução | **defeito de planejamento: a task estava incompleta**>

**Limpo:** <o que foi verificado e não gerou achado — dá confiança no que passou>

➡️ Corrigir: /build <feature> TASK-X.Y.Z
⚠️  Depois da correção o review roda de novo sobre a feature inteira
```

> Marcar a **origem** de cada achado não é burocracia: achado de planejamento
> significa corrigir a *task*, não só o código. Sem isso o mesmo erro volta na
> próxima feature.

---

## Regras do contrato

1. **Evidência é output colado, não descrição.** "Testes passaram" não é evidência; o bloco com o comando e o resultado é.
2. **"Feito" descreve comportamento, não arquivos.** A lista de arquivos vem depois, e é diferente.
3. **Campo vazio vira `—`.** Omitir campo esconde que a pergunta foi feita; encher de texto genérico é pior.
4. **O último campo é sempre um comando executável** com os argumentos reais preenchidos.
5. **Nunca declarar sucesso sem o gate correspondente.** Se o gate não rodou, o campo diz por que e qual o risco residual.
