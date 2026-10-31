# Baixar os PDFs do Centro de Mídias SP (gov.br)

Site: https://repositorio.educacao.sp.gov.br/midia  (aba **Materiais digitais**)
Alternativas: a professora pode mandar os PDFs prontos (basta apontar a pasta) ou colar o link do site.

## Passo a passo com o browser-harness (Chrome)
1. Peça para a professora abrir o site no Chrome e **entrar pelo gov.br** (login é manual; o captcha e a senha são dela).
   Depois ela confirma "logada".
2. **Não use `goto_url` nem recarregue a aba logada.** A sessão fica na memória da aba (sessionStorage); recarregar ou
   navegar derruba o login (foi o erro que aconteceu na 1ª tentativa). Só leia o DOM e mexa nos filtros.
3. Liste as opções dos filtros (para mapear nomes → valores):
   `MODE=list browser-harness < scripts/gov_extract.py`
   (valores usados: etapa 2 = Fund. Anos Finais; componente 8 = Geografia, 9 = História; série 6..9; bimestre 1..4)
4. Para cada combinação ano/etapa/série/bimestre/componente:
   `MODE=extract F_ANO=2026 F_ETAPA=2 F_SERIE=6 F_BIM=4 F_COMP=9 browser-harness < scripts/gov_extract.py`
   Saída: linha `STATE{...}` (confira que os filtros ficaram como pediu — trocar a série zera o componente, por isso o
   script define o componente por último) e linha `LINKS[...]`.
5. `... | grep '^LINKS' | sed 's/^LINKS//' > links.json` e
   `python3 scripts/download_pdfs.py links.json <pasta>/<ano>/<etapa>/<serie>ano/<bim>bim/<componente>`
6. Os links diretos em `acervocmsp.educacao.sp.gov.br` abrem sem login, então o download é só `curl`.
7. Se `browser-harness` pedir "Allow remote debugging?", rode `browser-harness mac-approve` ou clique em Allow no Chrome.
8. Se um comando do browser-harness ficar preso (ex.: página com captcha), rode-o em segundo plano com limite de tempo e
   cancele; não reinicie a aba logada.

## Pasta de PDFs (padrão)
`~/Downloads/cmsp/<ano>/EF-anos-finais/<serie>ano/<bim>bim/<componente>/`  (ex.: `.../6ano/4bim/historia`)
Cada pasta deve ter: PDFs das aulas (`Aula N`), o Livro do Estudante (162+ páginas), o caderno de resolução.
Aulas só em PPTX (sem PDF) são baixadas como PPTX; `pdf_meta.py` lê os dois formatos.
