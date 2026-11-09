# <Fabricante> <Plugin> <versão>: modelagem, UI, fluxo e reconstrução

> Dossiê no padrão `ssl-xsaturator-modelagem.md`. Salvar em `plugins-kb/<fabricante>-<plugin>-modelagem.md`.

Estudo de engenharia reversa do **<Fabricante> <Plugin>** para servir de fonte de reconstrução de um <tipo> original (marca fictícia). Escrito em <data>. Fontes: (1) RE estático <com/sem teto> (2) medição black-box com `pedalboard` em regime estável.

> **Teto do RE estático.** *(só se protegido)* O binário é protegido por <X> (evidência: <seções, entropia, 0 funções>). A função de transferência não foi extraída; recuperá-la exigiria burlar proteção, não feito, não repetir. O modelo vem só das medições.

## Convenção de confiança
- **[Fato-RE]** extraído do binário (strings, RTTI, frameworks, símbolos).
- **[Medido]** medição black-box reproduzível pelos scripts em `_re-corpus/<plugin>/measurements/`.
- **[Fato]** matemática ou documentação pública.
- **[Inferência]** coerente com os achados, não confirmada.
- **[Reconstrução]** fórmula proposta para o nosso clone; não é o algoritmo do fabricante.
- **[Escolha de projeto]** valor a calibrar de ouvido e por medição.
- **[Não verificado]** lacuna.

## 1. Identidade do binário `[Fato-RE]`
| Item | Valor |
|---|---|
| Produto / versão | |
| Formatos | VST3 / AU (tipo, subtipo, fabricante) / CLAP |
| Arch / tamanho | |
| sha256 do slice analisado | |
| Tecnologia de UI | |
Comando: `inventario_estatico.py <plugin> --out _re-corpus/<p>/inspect/`.

## 2. Classes e estrutura `[Fato-RE]`
Classes RTTI úteis, módulos, nomes de parâmetro nas strings, mensagens. O que sugerem sobre a arquitetura.

## 3. UI `[Fato-RE] + [Inferência]`
Tecnologia, assets (nº de PNG, filmstrips: quadros, tamanho), proporções do painel, controles. Comando do carving.

## 4. Parâmetros reais `[Medido]`
Tabela: id | rótulo | unidade | faixa | taper (linear/exp/curvo) | passo (texto/DSP) | padrão | observações. Comando: `sonda_parametros.py`.

## 4b. Classe do sistema `[Medido]`
Saída de `classificar_sistema.py` (`classificacao.md`): veredito por classe (a linear invariante, b não linear sem memória, c não linear com memória, d variante no tempo, e realimentação, f estocástico) com a evidência numérica e os protocolos recomendados. `inconclusivo` vai para a Lacunas. A classe decide a régua: amostra a amostra (a, b, c, delay sem modulação) ou estatística (d aleatório, f).

## 5. Modelo medido (resumo) `[Medido]`
Diagrama do fluxo de sinal e fórmulas em uma página.

## 6. Resultados de medição (regime estável) `[Medido]`
Uma subseção por fenômeno; cada número cita comando e arquivo de saída.
- 6.1 Neutro e coloração (ganho unitário, null vs bypass)
- 6.2 Núcleo (curva de transferência; domínio do tempo)
- 6.3 Harmônicos/THD vs nível e vs ajuste; pares vs ímpares
- 6.4 Dependência de frequência; DC e HP
- 6.5 Aliasing, oversampling, latência
- 6.6 Suavização e rampas; quantização
- 6.7 Mix, bypass, estéreo, ordem dos blocos
- 6.8 Dependência de SR
- 6.9 Erro do modelo contra a verdade: régua explícita, % dentro, hold-out com semente, p50/p90/máx
- 6.10 Música: trechos, ajustes, % de janelas ≤ −40 dB

## 7. Reconstrução `[Reconstrução]`
Fórmulas do motor, coeficientes, parâmetros e passos, estrutura de `dsp-core/<Nome>Engine.h`, testes. Fórmula entra como **modelo ajustado às medições**, nunca como transcrição de código do binário.

## 8. Matriz de cobertura `[Medido]`
Saída de `matriz_cobertura.py` (`cobertura.md`): dimensão → medido? → fase(s) → erro/limite → status (CONVERGENTE / UMA FASE / FORA DO LIMITE / LACUNA). Colar a tabela e os totais (cobertura %, convergente %, lacunas). Manifesto da classe/tipo: `matriz_cobertura.py --gera-modelo <tipo>`.

## 9. Teste de fechamento `[Medido]`
Saída de `teste_fechamento.py` (`fechamento.md`): plugin real vs recriação, % por componente, com a régua explícita.
| Componente | Régua | % dentro | Pior caso | Comando |
|---|---|---|---|---|
| regua (tons: ganho/harmônicas) | `|ganho| ≤ 0,1 dB`, `|H2..H6| ≤ 0,005` | | | |
| resposta (magnitude por banda) | `|erro| ≤ 0,1 dB` | | | |
| musica (resíduo nulo, 100 ms) | ≥ 95 % ≤ −40 dB | | | |
| estatistico (EDC, RT60, NED, espectro, IACC, modulação, ruído) | tolerâncias de `classes-de-sistema.md` §3 | | | |
Declarar hold-out (semente), música usada, ajustes, e quais componentes **não** se aplicam (ex.: música em parte estocástica). Alvo de qualidade: ≥ 95 % por componente.

## 10. Ledger de confiança
Uma linha por afirmação que alimenta o motor (regras em `ledger-confianca.md`):
| id | afirmação | EST | BB | MUS | FEC | confiança (validado / confirmado / medido / inferência / lacuna) | ação |
|---|---|---|---|---|---|---|---|
Cada célula traz comando e arquivo, `-` se a fase não mediu, `diverge: ...` se discorda (rebaixa e abre investigação).

## 11. Lacunas `[Não verificado]`
O que não foi medido (sidechain externo, instrumentos MIDI, SR extremos, modos, BPM sync), cantos fora da régua (com %), dimensões LACUNA da matriz, linhas `lacuna a investigar` do ledger, pendências.

## Fontes
Scripts, CSVs, hashes, docs relacionados, versões de ferramentas (pedalboard x.y, Ghidra, REA).
