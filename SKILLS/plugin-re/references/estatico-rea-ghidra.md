# RE estático com REA + Ghidra (macOS)

Para ler o invólucro legível (strings/RTTI) de um binário cifrado. Antes: `protecao-e-limites.md`.

## Índice
1. Ambiente
2. Passo a passo
3. Achar as funções de DSP
4. Ler o decompilado
5. Quando o Ghidra define 0 funções
6. Snapshots e organização
7. Strings, RTTI e metadados (vale para qualquer binário)

## 1. Ambiente
O REA (`~/.local/bin/rea`, alias `rea-agents`) usa o Ghidra por baixo e precisa de Java 21. Sem as variáveis ele responde `provider_unavailable`; o bloqueio histórico era o Java fora do PATH (openjdk@21 do Homebrew é keg-only).

```bash
export GHIDRA_INSTALL_DIR="$HOME/ghidra/ghidra_12.1.4_PUBLIC"      # confira com ls; já houve cópia em ~/tools/
export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
```
O decompiler nativo do Ghidra no mac arm64 foi compilado do fonte com `CXX="clang++ -arch arm64"`, **um make target por vez** (`ghidra_opt`, depois `sleigh_opt`); se precisar refazer, não paralelizar targets. Em outra máquina, instalar JDK 21 e Ghidra e compilar o decompiler do mesmo jeito.

## 2. Passo a passo
1. **Inventário**: `scripts/inventario_estatico.py <plugin>.vst3 --out _re-corpus/<p>/static/`.
2. **Fatia thin**: o REA recusa Mach-O universal e x86_64. `lipo -thin arm64 "<bundle>/Contents/MacOS/<exe>" -output _re-corpus/<p>/<exe>.arm64`.
3. **Visão geral**: `rea inspect <exe>.arm64 --format md --snapshot _re-corpus/<p>/<p>.snapshot > _re-corpus/<p>/<p>.inspect.md`. Mostra segmentos, funções, strings. A 1ª análise demora (minutos); o snapshot evita refazer.
4. **Decompilar uma função**: `rea decompile <exe>.arm64 0x<endereço> --snapshot <p>.snapshot --format md`. Também aceita nome de procedimento e `--file-offset`.
5. **Varredura em lote**: decompilar as funções candidatas (item 3) e gravar em `_re-corpus/<p>/decompiled/functions/0x<addr>.c`. Depois `grep -rE` no diretório.
6. `rea --help` lista os demais comandos (renomear/anotar função, comparar versões). Use `--filter-output` e `--token-limit` para não inundar o contexto.

## 3. Achar as funções de DSP
Funções de DSP são poucas entre milhares (wrapper JUCE, UI, licença). Ache por **assinatura numérica**, não por nome (o binário costuma estar stripado):
- **Importações matemáticas**: quem chama `sinf/cosf/tanf/tanhf/expf/powf/logf/exp2f/fabsf/sqrtf`. Em `inspect`, procurar as referências cruzadas desses símbolos. `tanhf` ou `tanh` perto de um laço = saturador; `tanf` com `pi*fc/fs` = coeficiente de filtro (bilinear); `expf(-1/(tau*fs))` = coeficiente de envelope/rampa; `powf(10, x/20)` = dB para linear.
- **Constantes**: `grep -E "0\.7071|1\.4142|6\.28318|3\.14159|0\.693147|2\.30258|0\.1151|8\.685"`. Frequências de EQ de console (ex.: 60/220/600/1500/4500 ...) revelam tabelas de bandas. Tabelas grandes em `__const`/`__DATA` com floats = LUTs (curvas de EQ, wavetables).
- **Estrutura**: laço sobre o buffer com `n` amostras e estado persistente (z1/z2) = filtro; dois estados com `max(abs(x), env)` = detector.
- **Strings de parâmetro** apontam para a classe que os registra; seguir referências cruzadas leva ao `processBlock`/`process`.
- **RTTI/vtables**: `processBlock`, `prepareToPlay`, `getStateInformation` ficam em vtables de classes com nomes legíveis (`inventario_estatico.py` lista as classes). Para JUCE: `juce::AudioProcessor` subclasse = o plugin; slot do `processBlock` na vtable.
- **Pistas indiretas**: strings como "oversampling", "latency", "Harrison", "MicPre", nomes de modos, revelam topologia mesmo sem ler código.

## 4. Ler o decompilado
- Pseudocódigo C do Ghidra com SIMD fica denso (`vmulq_f32`, laços desenrolados ×4 ou ×8). Procure primeiro o **esqueleto**: laços, chamadas matemáticas, constantes. Depois reduza a uma fórmula de uma linha e **teste a fórmula contra medições** (`modelar-e-validar.md`); decompilação sem medição é hipótese.
- libm inlined pode esconder `tanh` como polinômio racional. Se a curva medida é tanh e o decompilado mostra uma razão de polinômios, é a mesma coisa.
- Nomes `FUN_...`/`param_1` são do Ghidra; renomear (anotar) à medida que entende evita reler.
- Registrar cada achado com o endereço: `[Fato-RE] função 0x... (sha256 do slice ...)`. Endereço sem o hash do slice não é rastreável.

## 5. Quando o Ghidra define 0 funções
Código cifrado/compactado: o analisador não acha prólogos. Tratar como protegido (`protecao-e-limites.md`): parar, registrar, black-box. Antes de concluir, confirmar que o slice é o arm64 certo e que `rea inspect` rodou até o fim (erro de Java parece "0 funções").

## 6. Snapshots e organização
```
_re-corpus/<plugin>/
  inspect/            saída de inventario_estatico (inspect.md, inspect.json)
  static/             strings, RTTI, listas de funções candidatas
  decompiled/functions/0x<addr>.c
  <exe>.arm64, <p>.snapshot, <p>.inspect.md
  measurements/       scripts e dados do black-box
  ui_assets/          filmstrips etc.
  README.md           comandos, hash
```
`.snapshot` permite reabrir sem reanalisar (`--snapshot`). Guardar o hash do slice no README.

## 7. Strings, RTTI e metadados (sempre permitido)
- `strings -a <exe> | grep -iE "tanh|coef|biquad|oversampl|latency|preset|param"`: se não aparece nada de DSP em binário gigante, é sinal de cifra.
- RTTI Itanium (`_ZTS`, `N3foo3BarE`): `inventario_estatico.py` valida o encadeamento `<len><nome>` para filtrar lixo. Nomes aleatórios (ex.: `AdFVjHGR`) indicam ofuscação do fabricante: registrar como tal.
- `otool -L` (frameworks), `otool -l` (comandos de carga), `codesign -dv` (identidade de assinatura), `Info.plist` (versão, `AudioComponents`: tipo/subtipo/fabricante do AU).
- `auval -a` e `auval -v aufx <sub> <manu>` instanciam o AU de verdade e confirmam que a licença está ativa e quantos buses/presets existem.
