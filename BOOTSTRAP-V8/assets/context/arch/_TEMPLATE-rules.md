<!--
_TEMPLATE-rules.md → gera .context/arch/rules.md

Este é o arquivo mais importante do .context/ — todo agent decide a partir dele.

REGRAS DE ESCRITA:
1. Cada regra é uma AFIRMAÇÃO VERIFICÁVEL, não conselho.
   ✅ "Toda query mora no repositório."   ❌ "Prefira repositórios."
2. Cada regra diz ONDE é reforçada, quando houver: linter, script, teste, revisão.
3. Regras são NUMERADAS e o número é estável — agents e reviews citam por número.
   Regra que sai deixa o número vago com uma nota. Nunca renumere.
4. O projeto já tem documento canônico de arquitetura? REFERENCIE a seção dele.
   Regra copiada é a origem de toda divergência futura.
5. Regra só muda por decisão registrada em decisions/.
-->

# Regras invioláveis — [PROJECT_NAME]

> Constituição do projeto. Toda decisão técnica passa por aqui.
> Alteração exige decisão registrada em `.context/arch/decisions/`.
> Documento canônico do projeto: [PATH ou "—"].

## Contrato e compatibilidade

**1.** [ex: O contrato público da API é intocável — o consumidor em produção depende do formato atual. Mudança de formato é breaking change e exige decisão registrada.]
*Reforçado por:* [teste de contrato / revisão]

**2.** [regra]
*Reforçado por:* [onde]

## Arquitetura e camadas

**3.** [ex: Nenhuma camada acima do repositório monta query. Toda query mora no repositório, atrás da interface.]
*Reforçado por:* [script de auditoria / revisão]

**4.** [regra]
*Reforçado por:* [onde]

## Dados

**5.** [ex: Dado de cliente vive na conexão resolvida pelo gerenciador de tenant. Nunca cruzar dados entre tenants.]
*Reforçado por:* [teste / revisão]

## Segurança

**6.** [ex: Segredo, token, senha e credencial nunca aparecem em log sem máscara.]
*Reforçado por:* [linter / revisão]

## Testes

**7.** [ex: Teste que precisa de banco usa transação por teste. Recriação de schema é proibida.]
*Reforçado por:* [revisão]

## Convenções obrigatórias

**8.** [ex: Idioma do projeto em código, comentário, mensagem de erro e commit: <idioma>.]
*Reforçado por:* [revisão]

---

## Como usar estas regras

| Quem | Como |
|---|---|
| PLANNER | Cita no handoff **só as 2–4 regras que se aplicam** à task, por número e texto curto |
| BUILDER | Segue as citadas. Em dúvida, lê este arquivo — mas não presume regra não escrita |
| REVIEWER | Achado de violação cita **o número da regra**, nunca copia o texto |

Regra que ninguém consegue verificar não é regra — é opinião. Se você não consegue
escrever o campo *Reforçado por*, reescreva a regra até conseguir, ou remova-a.
