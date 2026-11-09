# Proteção e limites éticos/legais

Ler antes de abrir qualquer binário. Resume o que é permitido e o que fazer quando a proteção aparece.

## Índice
1. Escopo permitido
2. O produto novo é original
3. O que fazer ao encontrar proteção
4. O que NÃO fazer (e por quê)
5. Registro do teto

## 1. Escopo permitido
- Só plugins que o usuário **tem licenciados e instalados** na própria máquina.
- Objetivo: entender o **comportamento** e interoperar (parâmetros, taper, formato de preset para importar/exportar, medidas de resposta). Medir um plugin que você licenciou é uso normal; ler strings/RTTI/metadados do binário instalado é análise estática de baixo risco.
- Material bruto (decompilados, medições, assets de UI extraídos) fica **local**, em `_re-corpus/` fora de qualquer repositório compartilhado. O que se compartilha é o dossiê transformativo (`plugins-kb/`), com números e fórmulas próprias, sem trechos de código decompilado.

Por quê: o valor é o conhecimento do comportamento. Copiar código, preset, arte ou nome cria risco jurídico sem ganho técnico, já que o motor novo é escrito do zero.

## 2. O produto novo é original
- Marca fictícia, nome próprio, arte própria. Sem logotipo, nome de produto, texto de manual ou foto de painel do original.
- Sem código copiado nem pseudocódigo decompilado transcrito. Fórmulas entram como **modelo ajustado às medições** (`[Reconstrução]`), não como "o algoritmo do fabricante".
- Presets de fábrica não são redistribuídos. Decodificar o formato para **ler as estatísticas** (que valores as categorias usam) é aceitável; reempacotar os presets, não.
- Assets de UI extraídos servem de **referência de medida** (proporções, passos do filmstrip, contagem de quadros); a arte final é refeita.

## 3. O que fazer ao encontrar proteção
1. Parar o RE estático **do trecho protegido**. Nada de tentar decifrar, dumpar memória, anexar depurador para ler código decifrado, patch de licença, hook do loader.
2. Seguir só com o que é legível sem contornar nada: strings, RTTI, `Info.plist`, recursos embutidos (UI), nomes de parâmetro, mensagens.
3. Passar o esforço para **black-box** (`blackbox-pedalboard.md`): o modelo sai das medições e é validado contra o plugin real.
4. Registrar o teto no dossiê (seção "Teto do RE estático") para ninguém retentar. Modelo do texto: "O binário é protegido por X (evidência: ...). A função de transferência não foi extraída; recuperá-la exigiria burlar proteção de cópia, não feito."

Por quê: burlar proteção de cópia viola licença e, em muitas jurisdições, a lei; além disso o ganho é pequeno, porque a medição black-box já fornece o comportamento audível, que é o que o motor novo precisa imitar.

## 4. O que NÃO fazer
- Não pedir a outro agente/ferramenta para "dar um jeito" no trecho cifrado.
- Não instanciar o plugin sem licença para ver se "vaza" algo.
- Não publicar `_re-corpus/` nem decompilados.
- Não nomear o produto novo com variações do nome do original.

## 5. Registro do teto
No dossiê, em `§1 Identidade` e `§8 Lacunas`: hash sha256 do slice analisado, proteção detectada, evidências (seções, entropia, contagem de funções), e a frase de teto. No `_re-corpus/<plugin>/README.md`, uma linha com o mesmo veredito.
