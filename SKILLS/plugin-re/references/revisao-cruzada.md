# Revisão cruzada e memória verificável

Processo para auditar documentação existente de engenharia reversa / medição, corrigir erros na origem e manter confiança ao longo do tempo. Complementa o ledger de confiança (`ledger-confianca.md`) e a matriz de cobertura (`matriz_cobertura.py`).

## Índice
1. Quando usar
2. Princípio: reproduzir, não reler
3. Passo a passo
4. Verificador de tabelas
5. Reprodução independente
6. Coerência entre docs
7. Correção na origem
8. Enriquecimento
9. Higiene (`make check`)
10. Armadilhas da revisão
11. Cruzamento estático × medição

## 1. Quando usar
- Quando um estudo foi escrito por outro agente, modelo ou sessão.
- Quando se retoma trabalho após semanas ou meses.
- Quando o prompt ou o usuário pede auditoria / revisão / "confere isso".
- Quando se descobre um número errado e se quer saber quantos mais há.
- Periodicamente: a cada N itens fechados, rodar o `make check` e conferir o ledger.

## 2. Princípio: reproduzir, não reler
Não confie em resumo — verifique. Documentos escritos por IA contêm dois tipos de erro:
- **Números certos, texto errado**: as tabelas (geradas de CSVs) batem, mas as conclusões em prosa generalizam mal ("nenhum estilo passa de X" quando 4 passam; "14 de 16 idênticos" quando são 8).
- **Números velhos, script atualizado**: o CSV guarda um valor superado que o doc ainda cita.

A regra: cada afirmação que entra no dossiê precisa de evidência reproduzível (comando + arquivo). Reler o doc e concordar não é evidência.

## 3. Passo a passo

### 3.1. Verificar o que já existe
1. Rodar os verificadores existentes (`gap_check.py`, `check_tables.py`, `make check`). Se não existem, criar.
2. `py_compile` em todos os `.py` de medição.
3. Conferir que todo caminho citado nos docs existe em disco.
4. Conferir que o índice (`plugins-kb/README.md`) lista todos os `.md`.
5. Conferir que o README do corpus (`_re-corpus/README.md`) lista todos os diretórios.

### 3.2. Conferidor de tabelas (automático)
Escrever ou atualizar `check_tables.py`:
- Para cada tabela Markdown nos docs, achar o CSV de origem.
- Comparar célula a célula (tolerância 0,06 dB; aceitar vírgula decimal).
- Meta: 0 divergências. Tabela sem CSV = achado a declarar.
- O conferidor deve falhar com código ≠ 0 se houver divergência.
- Gerar tabelas por script a partir do CSV; nunca copiar à mão.

### 3.3. Reprodução independente
Escolher 3 a 5 afirmações de cabeçalho (as mais citadas ou as mais arriscadas) e **reproduzir com código novo** (não copiar o script do autor):
- Cada reprodução = instância nova do plugin, sinal novo, análise nova.
- Comparar com o doc: dentro da tolerância = ✓; fora = ✗; impossível = ?.
- Registrar na tabela de revisão com evidência (script, CSV, número medido vs doc).

### 3.4. Coerência entre docs
- Algum doc contradiz outro? Procurar termos-chave (nomes de estilo, valores, limites) nos outros docs e comparar.
- Referências internas resolvem? (ex.: "ver §2.3 do doc de lacunas" — existe? diz o que o autor diz que diz?)
- Rótulos coerentes? Mesmo número marcado "observado" num doc e "inferido" em outro é erro.

## 4. Correção na origem
Regra absoluta: se corrigir um número, **corrija na origem** (o doc que o publicou) **E** registre antes/depois no doc de revisão. Nunca:
- Corrigir só no doc de revisão (o original fica errado).
- Corrigir em silêncio (ninguém sabe que mudou).
- Reescrever a conclusão sem mostrar o que dizia antes.

Formato do registro:
```markdown
| doc | local | antes | depois | evidência |
|---|---|---|---|---|
| saturn2 §7.2 | "nenhum estilo passa de h5 −15 dB" | nenhum | 4 estilos passam | check_tables.py + CSV |
```

## 5. Enriquecimento
Após a auditoria, enriquecer os docs:
- **Referências cruzadas**: cada doc linka para os outros onde relevante.
- **Sumário executivo**: o doc principal deve ter uma visão geral com o que se sabe e o que falta.
- **Tabela de cobertura**: recurso × status (✓ medido / parcial / aberto).
- **Glossário**: termos técnicos definidos uma vez (null test, THD, LUFS, LR4).
- **Rótulos**: todo número tem rótulo (observado/inferido/desconhecido). Passar pelos docs e adicionar onde faltar.

## 6. Higiene (`make check`)
Manter um `Makefile` na raiz que rode todos os verificadores:
```makefile
PY ?= _re-corpus/saturn2/.venv/bin/python
check:
	$(PY) _re-corpus/saturn2/gap_check.py
	$(PY) _re-corpus/saturn2/check_tables.py
	cd _re-corpus/decapitator/measurements && $(PY) gen_tables.py --check
	$(PY) _re-corpus/check_kb.py
	# py_compile de todos os .py
```
- `make check` deve sair com código 0 se tudo passa.
- Rodar ao fim de cada tarefa, antes de declarar "fechado".
- Todo script novo deve ser adicionado ao `make check`.

## 7. Armadilhas da revisão
| Armadilha | Consequência | Regra |
|---|---|---|
| Reler e concordar | drift de confiança: o erro original propaga | reproduzir, não reler |
| Copiar tabela à mão | deriva silenciosa entre CSV e doc | gerar do CSV por script |
| Mover/renomear doc sem grep | links quebrados no índice e em referências cruzadas | grep antes de mover; rodar `check_kb.py` depois |
| Corrigir número só no doc de revisão | doc original fica errado | sempre na origem + registro |
| Aceitar "não verificado" sem declarar | leitor assume que está verificado | rotular explicitamente |
| Medir com o mesmo script do autor | confirma o método, não o resultado | código novo para reproduções |
| Confiar em "TUDO BATE" sem saber o que o verificador cobre | pode não cobrir as tabelas novas | conferir que novos handlers existem para cada tabela |
| Modelo mais barato escreveu o doc | números bons, conclusões ruins (generalizações erradas) | pedir que cada "todos/nenhum/N de M" cite CSV e coluna |

## 8. Cruzamento estático × medição
Quando o binário não é decompilável (proteção), as strings e RTTI são a segunda fonte independente. O cruzamento funciona assim:

1. **Extrair classes RTTI, strings de DSP, nomes de parâmetro** (sempre permitido, `protecao-e-limites.md` §3).
2. **Mapear para a arquitetura**: cada classe RTTI = um bloco do grafo de processamento. Strings de parâmetro confirmam os knobs.
3. **Cruzar com medições**:
   - RTTI diz `wmSplineModShaper` + medição diz curva não-tanh → [Cruzado]: shaper é spline.
   - RTTI diz `wmSlewedBiquad` + medição precisa assentar → hipótese (a suavização explica, mas não está medida isoladamente).
   - RTTI diz `wmDownSample` + medição mostra aliasing → confirma oversampling, mas o fator é só medido.
4. **Rótulos**:
   - [Fato-RE]: veio do binário (nome, classe, string).
   - [Medido]: veio de medição reproduzível.
   - [Cruzado]: EST e BB concordam (promove a "confirmado" no ledger).
   - Hipótese: EST sugere e BB é compatível, mas não há medição isolada.
5. **Cuidado**: a ausência de uma string (ex.: sem `tanh` no binário) é evidência fraca quando o código está cifrado. A string pode existir dentro do bloco cifrado.

## 9. Frequência recomendada
- **A cada plugin fechado**: rodar `make check` + conferir ledger.
- **A cada 3–5 plugins**: revisão cruzada completa (reproduções independentes).
- **Quando retomar após pausa longa**: começar pela revisão cruzada antes de medir coisas novas.
- **Quando mudar de modelo (ex.: trocar de DeepSeek para Sonnet)**: conferir as conclusões em prosa; os números costumam estar certos.
