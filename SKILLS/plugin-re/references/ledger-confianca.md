# Ledger de confiança: cada afirmação com suas fontes

Garantia não é promessa: é processo verificável. O ledger registra, **por afirmação** do dossiê, quais fases independentes a sustentam, e aplica regras fixas de promoção e rebaixamento de confiança. Ele convive com os rótulos de `esqueleto_doc.md` (`[Fato-RE]`, `[Medido]`, ...) e com `matriz_cobertura.py` (que olha dimensões, enquanto o ledger olha afirmações).

## Índice
1. Fases (fontes independentes)
2. Formato do ledger
3. Regras de promoção e rebaixamento
4. Níveis de confiança
5. Exemplos
6. Como manter

## 1. Fases (fontes independentes)
| Fase | Sigla | O que é | Independente de |
|---|---|---|---|
| Estático | EST | RTTI, strings, símbolos, decompile compreendido (só binário não protegido), formato de preset | medições |
| Black-box | BB | medição no plugin real em regime estável (tom, ruído, ESS, clique) | código |
| Música | MUS | resíduo nulo ou estatística em material real | tons de teste |
| Fechamento | FEC | recriação vs plugin com régua determinística/estatística | o ajuste (hold-out, semente nova) |
Duas medições da **mesma fase** com métodos diferentes (tempo e FFT, por exemplo) contam como replicação, **não** como fases independentes. Fase independente exige **canal de informação diferente**: código vs sinal; tons vs música; ajuste vs hold-out.

## 2. Formato do ledger
Tabela no dossiê (§ "Ledger de confiança"), uma linha por afirmação que alimenta o motor:
| id | afirmação | EST | BB | MUS | FEC | confiança | ação |
|---|---|---|---|---|---|---|---|
| L1 | "RT60 1 kHz = 2,1 s para decay 2,1 s" | strings: `decay` em segundos | `ir.json` capturas.1 (2,113 s) | n/a | EDC RMS 0,08 dB | alta | usar |
Cada célula traz **o comando e o arquivo** (ou `-` se não há; `diverge: ...` se discorda). Afirmação sem comando não entra.

## 3. Regras de promoção e rebaixamento
1. **Promoção**: duas fases independentes **concordam** (dentro da tolerância da dimensão) → sobe um nível. Três ou mais → "alta".
2. **Rebaixamento**: uma fase **diverge** (fora da tolerância, ou contradiz) → rebaixa para "lacuna a investigar" e **abre investigação**; não vale média. A divergência é informação: aponta um erro de harness, um modo não medido ou um erro de leitura estática.
3. **Estático sozinho nunca passa de "inferência"**: o binário diz o que *existe*, não o que *faz* ao áudio; só a medição confirma. Exceção: formato de preset decodificado e validado contra o plugin.
4. **Estático + black-box concordam** (ex.: string `FDN` + ecos densos com RT60 por banda compatível) → promove a "confirmado".
5. **Medição sem fechamento**: máximo "medido" (sem garantia de recriar). **Fechamento passando** (≥ 95 % no hold-out) promove a "validado".
6. **Hold-out** ≠ ajuste: fechamento com os mesmos pontos do ajuste não conta como fase independente.
7. **Fase única repetida** (mesmo script duas vezes) continua uma fase.
8. Divergência entre BB e MUS (tons bons, música ruim) é a mais valiosa: costuma achar um bloco não medido (mix, DC, detector).

## 4. Níveis de confiança
| Nível | Critério |
|---|---|
| **validado** | ≥ 2 fases independentes concordam E fechamento ≥ 95 % em hold-out |
| **confirmado** | 2 fases independentes concordam (ex.: EST + BB) |
| **medido** | 1 fase BB/MUS reproduzível, com comando |
| **inferência** | só EST, ou coerência indireta |
| **lacuna a investigar** | alguma fase diverge, ou nada mediu |
Correspondência com os rótulos do dossiê: `[Medido]` = medido; `[Fato-RE]` sozinho = inferência (sobre o comportamento); validado/confirmado são colunas do ledger.

## 5. Exemplos
- **Concordância (promove)**: RTTI mostra `FeedbackDelayNetwork` e o BB mostra NED chegando a 1 em 200 ms e cauda com RT60 por banda: confirma FDN. O fechamento estatístico a 100 % → validado.
- **Divergência (rebaixa)**: o tom a 1 kHz diz "memoryless" (THD igual em 3 níveis) mas a música deixa resíduo −20 dB: provavelmente há memória só visível em transientes (detector). Rebaixa "memoryless" a lacuna e mede degrau/dois tons.
- **Artefato de harness**: `reset()` fez parecer suavização de 1 s no X-Saturator (BB sozinho enganou); a leitura estática não via suavização: a divergência abriu investigação e achou o artefato.

## 6. Como manter
- Atualize o ledger junto com o dossiê; cada nova medição ou fechamento reavalia as linhas afetadas.
- `matriz_cobertura.py` mostra o que tem 0, 1 ou 2+ fases por dimensão; o ledger detalha cada afirmação.
- No relatório ao usuário, resuma: quantas afirmações validadas/confirmadas/medidas/inferência/lacuna.
