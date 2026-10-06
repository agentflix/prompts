# Triagem de bugs do legado: corrigir ou preservar

Ao extrair e portar, aparecem bugs. A pergunta nunca é só "isso está errado?", é "alguém depende disso?".

## A árvore de decisão

```
O comportamento é um bug?
├─ Não sei dizer se é deliberado → registre como comportamento + pergunta (unknowns). Não decida.
└─ É bug
   ├─ Algum fluxo em produção depende dele hoje?
   │   ├─ Sim → PRESERVE. Registre em findings. Corrigir é uma decisão do dono do produto, depois do port.
   │   └─ Não (sem consumidor observável) → CORRIJA no port e documente no docblock.
   └─ É falha de segurança (XSS, vazamento entre tenants, entidade inteira no JSON, validação ausente)?
       └─ CORRIJA no port, porque a estrutura nova (FormRequest, Resource, scope) elimina a classe do erro.
          Registre a diferença no teste de paridade como divergência deliberada.
```

## Três classes e o destino de cada uma

| Classe | Exemplos | Destino |
|---|---|---|
| **Segurança** | XSS, vazamento entre tenants, entidade inteira no JSON, upload sem validar bytes | Corrige no port; a estrutura nova já fecha a classe |
| **Regra de negócio errada** | Cálculo de comissão, fechamento, licença | Não corrige sozinho. Vira decisão do dono do produto, registrada, e task própria depois do port |
| **Dívida de código** | Duplicação, nomes, acoplamento | Some naturalmente quando Controller, Action e FormRequest substituem o desenho antigo |

## Por que preservar é o default

Se o port corrige no meio do caminho, você não distingue regressão de correção quando o teste de
paridade falha. Duas mudanças misturadas escondem uma à outra. Separe: primeiro equivalência, depois
melhoria, cada uma com sua evidência.

## Como registrar

- **Corrigido:** docblock do arquivo novo com o que o legado fazia, por que ninguém dependia e o que mudou.
- **Preservado:** entrada em `findings.md` com `file:line`, o comportamento observado e a recomendação.
- **Indecidível:** entrada em `unknowns.md` como pergunta ao dono do produto.

## Código morto não é regressão

Antes de portar, prove que o código está vivo: busque os chamadores em todo o código analisado. Um método
sem nenhum chamador, que dependeria de propriedade nunca inicializada, é código morto e **não** deve ser
portado (portar seria criar infraestrutura sem consumidor). Registre a exclusão com a evidência da busca.
No DotBank, um "motor de cobrança" que a auditoria inicial dava como faltando era código morto no legado;
só a busca de chamadores desfez o falso alarme.

## Falso concluído

Dois erros simétricos: omitir comportamento que existe (regressão) e criar comportamento que o legado
não tinha (infraestrutura sem consumidor). A auditoria compara nas duas direções.
