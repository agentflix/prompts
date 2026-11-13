---
paths:
  - "<ex.: **/*.test.ts>"
  - "<ex.: **/*.spec.ts>"
  - "<ex.: tests/**>"
---
<!--
Molde de .claude/rules/testes.md. Instale sempre que o projeto tiver testes.
Este comentário não vai para o arquivo final. Ajuste os exemplos de mock e de fronteira ao projeto.
Base: Dodds (testing trophy), Vocke (practical test pyramid), Beck (test desiderata),
Khorikov (4 pilares, mock só em dependência não gerenciada), Hora & Robbes (MSR 2026:
agentes adicionam mock em 36% dos commits contra 26% dos humanos), Meta ACH (mutação mede valor, cobertura não).
-->
# Testes: valor antes de volume

Todo teste precisa de um motivo: um critério de aceite, um risco ou um bug. Sem motivo, não escreva.

## O que testar
- **T1** Por risco: dinheiro e cálculo, autenticação e permissão, integridade de dados e migration, contrato público (API, evento, schema), lógica com muitos ramos, e todo bug corrigido (teste de regressão).
- **T2** Um teste por item de **Pronto quando** do plano, no mínimo. Antes de escrever, diga qual mudança no código faria o teste falhar. Se não souber dizer, o teste não protege nada.
- **T3** Prefira teste de integração na fronteira (rota, handler, serviço, com banco real ou fake em memória). Teste unitário só para lógica pura com ramificação. Property-based para função pura com invariante.

## O que não testar
- **T4** Getter e setter triviais, configuração sem lógica, código gerado, função privada, comportamento do framework ou de biblioteca de terceiros, texto exato de interface, snapshot de tela inteira, e teste que repete a implementação.

## Mock
- **T5** Mock só na fronteira que o projeto não controla: rede externa, e-mail, pagamento, fila, relógio. Ordem de preferência: real, fake, spy, stub, mock. Não mocke o código sob teste, o próprio banco, value object nem função pura. Mais de 3 mocks num teste indica unidade grande demais.

## Qualidade
- **T6** Refatorar não pode quebrar teste. Se quebrou sem mudar comportamento, o teste testava implementação: reescreva-o pelo comportamento.
- **T7** Veja o teste falhar antes de passar: rodar antes de implementar basta. A mutação (inverter a condição ou apagar a asserção principal e ver falhar) é obrigatória só quando o E da task pede, em área de risco; fora disso, não faça nem liste como não verificado.
- **T8** Antes de criar arquivo de teste, procure teste existente que já cobre o caso e estenda-o. Com `tests.lock` ativo (testes primeiro), o teste novo vai em arquivo novo.
- **T9** Teste instável vai para quarentena com o motivo registrado. Retry silencioso e `sleep` não corrigem.

## Rodar só o que importa
- **T10** O gate rápido roda só os testes afetados pela mudança (`{changed}` no `GATE_FAST`), com parada na primeira falha. Alvo: menos de 30 segundos. Se estourar, não aumente o gate: mova o teste lento para o `GATE_FULL` ou para o CI.
