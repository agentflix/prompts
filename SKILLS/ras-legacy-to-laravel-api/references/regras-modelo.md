# Modelo de constituição (`rules.md`) para a API nova

Copie e adapte. O formato é o que mantém a regra honesta: cada uma tem um campo **Reforçado por**, o
teste, comando ou verificação que a prova. Se você não consegue escrever esse campo, reescreva a regra
até conseguir, ou remova-a. Regra que ninguém verifica é opinião.

## Formato de cada regra

```
**N.** Enunciado curto, imperativo, com o porquê quando não for óbvio.
*Reforçado por:* teste ou comando exato · revisão
```

## Conjunto base (derivado de um port real)

**Contrato**
1. O contrato HTTP em produção é intocável: status, shape JSON e mensagens são os do legado. Mudança é
   breaking change e exige decisão registrada. *Reforçado por:* teste de contrato do envelope de erro.
2. Toda resposta de erro usa o envelope do legado; o 422 padrão do Laravel é proibido. Todo FormRequest
   estende a base do projeto. *Reforçado por:* teste de contrato do envelope.
3. As rotas expostas são exatamente as do legado. Rota nova exige decisão e nasce com throttle
   incondicional. *Reforçado por:* conferência contra o arquivo de rotas do legado · `php artisan route:list`.
4. Bug sem consumidor observável é corrigido e documentado; comportamento de que algo depende é
   preservado. *Reforçado por:* revisão contra `findings.md`.

**Camadas**
5. Toda query mora no Repository atrás da interface. *Reforçado por:* `grep -rnE "::query\(\)|::where\(" app/Actions app/Services` deve voltar só docblock.
6. Controller é fino: uma Action, zero regra, zero query. *Reforçado por:* revisão.
7. Um caso de uso é uma Action com um único `execute()`. *Reforçado por:* revisão.
8. Service só existe com regra real; Service vazio é proibido. *Reforçado por:* revisão.
9. A entrada é DTO `readonly`, nunca array de request. *Reforçado por:* revisão.
10. O binding interface para implementação mora no ServiceProvider do domínio. *Reforçado por:* teste que resolve a Action pelo container.

**Segurança**
11. Segredo, token, senha e documento nunca aparecem em log sem máscara. *Reforçado por:* teste do logger.
12. `env()` fora de `config/**` é proibido. *Reforçado por:* `grep -rn "env(" app` deve voltar só docblock.
13. `verify_tls` nunca é `false`. *Reforçado por:* revisão.
14. Flag de hardening não é ligada como efeito colateral. *Reforçado por:* revisão.
15. Credencial de integração nasce desabilitada; segredo em hash e mostrado uma vez; a falha não distingue o motivo. *Reforçado por:* teste que compara o corpo da resposta de credencial inativa e de segredo errado.
16. Closure de `RateLimiter::for()` nunca depende de estado de autenticação. *Reforçado por:* teste de rate limit.
17. Upload é validado pelos bytes dentro do FormRequest. *Reforçado por:* teste com arquivo disfarçado.
18. Todo model tenant-aware é isolado, e toda rota tem teste de acesso negado de outro tenant. *Reforçado por:* teste de isolamento.

**Testes e qualidade**
19. A cobertura vem de teste unitário puro com mock sobre as interfaces de Repository. *Reforçado por:* gate de cobertura (meta de 80% na camada de lógica).
20. Teste com banco usa transação por teste num banco próprio; `RefreshDatabase` é proibido. *Reforçado por:* `grep -rn "RefreshDatabase" tests` deve voltar vazio.
21. Análise estática em nível alto com baseline **vazio**; acrescentar ao baseline é proibido. *Reforçado por:* o comando de análise estática do gate.
21b. O alvo de linguagem é a versão de PHP do `composer.json` e do runtime de deploy, mesmo que a máquina local rode mais nova: sintaxe acima do alvo é proibida. *Reforçado por:* o comando de análise estática · revisão.
21c. O nível da análise estática é o mais alto que o código atual comporta, sobe com o tempo e nunca desce. *Reforçado por:* o comando de análise estática.
22. Todo módulo tem teste de paridade contra o legado antes de ser dado como pronto. *Reforçado por:* suíte de paridade.

**Convenções**
23. Prosa em pt-BR (comentário, docblock, mensagem de erro, commit); identificadores em inglês. *Reforçado por:* revisão.
24. Commit segue Conventional Commits com escopo: `tipo(escopo): descrição`. *Reforçado por:* `git log --oneline`.

## Como usar

| Quem | Como |
|---|---|
| Planejador | Cita no handoff só as duas a quatro regras que se aplicam à task, por número |
| Executor | Segue as citadas; em dúvida lê o arquivo, mas não presume regra que não está escrita |
| Revisor | Achado de violação cita o número da regra, não copia o texto |

Mudar uma regra exige decisão registrada em `decisions/`. A constituição só muda por decisão explícita.
