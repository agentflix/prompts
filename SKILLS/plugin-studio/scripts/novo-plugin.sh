#!/usr/bin/env bash
# Cria um plugin de efeito novo a partir de assets/template-efeito.
# Uso:
#   novo-plugin.sh <pasta-destino> <NOME> <CODIGO4> "<Empresa>" <MFR4> <bundle-prefix>
# Exemplo:
#   novo-plugin.sh ~/plugins/brilhor BRILHOR Brlh "Minha Empresa" Mnha com.minhaempresa
#
#   NOME           letras, números e espaços, começando com letra. Pode ter espaço ("SATUR ANALOG"):
#                  o nome exibido no host/UI mantém o espaço; o alvo do CMake, o bundle e o .pkg
#                  usam o nome sem espaços ("SATURANALOG'), e o id é esse nome em minúsculas
#   CODIGO4        código do plugin: 4 letras/números, com pelo menos uma maiúscula (ideal: só a 1ª)
#   Empresa        nome exibido no host
#   MFR4           código do fabricante: 4 letras/números, 1º caractere maiúsculo
#   bundle-prefix  ex.: com.minhaempresa (minúsculas, separado por pontos)
set -euo pipefail

erro() { echo "Erro: $*" >&2; exit 1; }

[ $# -eq 6 ] || { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }

DEST="$1"; DISPLAY_NAME="$2"; CODE="$3"; EMPRESA="$4"; MFR="$5"; BUNDLE="$6"

# espaços repetidos/nas pontas viram um só; o alvo/bundle é o nome sem espaços
DISPLAY_NAME=$(printf '%s' "$DISPLAY_NAME" | tr -s ' ' | sed -E 's/^ +//; s/ +$//')
NOME="${DISPLAY_NAME// /}"
[[ "$DISPLAY_NAME" =~ ^[A-Za-z][A-Za-z0-9\ ]*$ && "$NOME" =~ ^[A-Za-z][A-Za-z0-9]{1,31}$ ]] || erro "NOME '$DISPLAY_NAME' deve ter só letras, números e espaços, começar com letra (2 a 32 caracteres sem contar espaços)."
[[ "$CODE" =~ ^[A-Za-z0-9]{4}$ ]]                || erro "CODIGO4 '$CODE' deve ter exatamente 4 letras ou números."
[[ "$CODE" =~ [A-Z] ]]                           || erro "CODIGO4 '$CODE' não pode ser todo minúsculo (o AU exige uma maiúscula)."
[[ "$MFR" =~ ^[A-Za-z0-9]{4}$ ]]                 || erro "MFR4 '$MFR' deve ter exatamente 4 letras ou números."
[[ "$MFR" =~ ^[A-Z] ]]                           || erro "MFR4 '$MFR' deve começar com letra maiúscula."
[[ "$BUNDLE" =~ ^[a-z][a-z0-9-]*(\.[a-z0-9][a-z0-9-]*)+$ ]] || erro "bundle-prefix '$BUNDLE' inválido (ex.: com.minhaempresa)."
[ -n "${EMPRESA// /}" ]                          || erro "Empresa não pode ser vazia."
[[ "$EMPRESA" != *'"'* && "$EMPRESA" != *'<'* && "$EMPRESA" != *'>'* && "$EMPRESA" != *'\'* ]] || erro "Empresa não pode ter aspas, < > ou barra invertida."
[ -e "$DEST" ] && erro "'$DEST' já existe. Não vou sobrescrever: escolha outra pasta."

n_mai=$(printf '%s' "$CODE" | tr -cd 'A-Z' | wc -c | tr -d ' ')
[ "$n_mai" = "1" ] || echo "Aviso: o ideal para o AU é CODIGO4 com exatamente uma maiúscula (ex.: Brlh); '$CODE' tem $n_mai."

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$SKILL_DIR/assets/template-efeito"
[ -d "$TEMPLATE" ] || erro "template não encontrado em $TEMPLATE"

ID=$(printf '%s' "$NOME" | tr 'A-Z' 'a-z')

mkdir -p "$(dirname "$DEST")"
cp -R "$TEMPLATE" "$DEST"
rm -rf "$DEST/build" "$DEST/dist"

# troca os marcadores em todos os arquivos de texto (perl: valores com espaço, & ou / ficam seguros)
export R_PLUGIN="$NOME" R_DISPLAY="$DISPLAY_NAME" R_ID="$ID" R_CODE="$CODE" R_COMPANY="$EMPRESA" R_MFR="$MFR" R_BUNDLE="$BUNDLE"
find "$DEST" -type f \( -name '*.txt' -o -name '*.h' -o -name '*.cpp' -o -name '*.html' -o -name '*.md' -o -name '*.sh' -o -name '.gitignore' \) -print0 |
  xargs -0 perl -pi -e '
    s/__PLUGIN_ID__/$ENV{R_ID}/g;
    s/__PLUGIN_DISPLAY__/$ENV{R_DISPLAY}/g;
    s/__PLUGIN__/$ENV{R_PLUGIN}/g;
    s/__CODE__/$ENV{R_CODE}/g;
    s/__COMPANY__/$ENV{R_COMPANY}/g;
    s/__MFR__/$ENV{R_MFR}/g;
    s/__BUNDLE__/$ENV{R_BUNDLE}/g;'

if grep -rqE '__(PLUGIN|PLUGIN_ID|PLUGIN_DISPLAY|CODE|COMPANY|MFR|BUNDLE)__' "$DEST"; then
  erro "sobrou marcador sem trocar em: $(grep -rlE '__(PLUGIN|PLUGIN_ID|PLUGIN_DISPLAY|CODE|COMPANY|MFR|BUNDLE)__' "$DEST" | tr '\n' ' ')"
fi
chmod +x "$DEST/scripts/"*.sh

cat <<EOF
Plugin "$DISPLAY_NAME" (alvo/bundle: $NOME) criado em $DEST

Próximos passos:
  cd "$DEST"
  cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release          # com JUCE local: -DFETCHCONTENT_SOURCE_DIR_JUCE=/tmp/juce-src
  cmake --build build
  ./build/${NOME}Tests                                        # testes do motor de DSP
  ./build/${NOME}ProcTests_artefacts/Release/${NOME}ProcTests # testes do processador e da ponte com a UI
  auval -v aufx $CODE $MFR                                    # valida o AU
  open ui/index.html                                          # vê a interface no navegador
EOF
