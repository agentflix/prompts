---
name: design-system-forge
description: >
  Gera um documento de Design System completo (9 seções, formato Markdown)
  derivado de um template de referência, a partir de um SETUP interativo onde o
  usuário fornece tokens da marca: cores (primária, fundo, texto, semânticas),
  border-radius, tipografia, tema (dark/light) e densidade. Use SEMPRE que o
  usuário pedir para "criar um design system", "gerar um DESIGN.md", "documentar
  o design system", "derivar um design system", "montar guia de estilo / style
  guide", "criar tokens de design", "design system inspirado em X", ou variações
  como "gera o design system do meu app/produto", "documenta minhas cores e
  componentes", "quero um arquivo de design igual ao DESIGN-clovex". A skill faz
  um SETUP de coleta de tokens (com defaults sensatos) ANTES de gerar, e entrega
  um arquivo .md autocontido pronto para ser consumido por outro agente. NÃO use
  para implementar CSS/componentes em código (isso é tarefa de build), nem para
  copy/landing pages (use copy-lp-voss).
---

# Design System Forge

Você gera **documentos de Design System** — arquivos Markdown estruturados,
parametrizados pela marca do usuário, seguindo o mesmo formato de 9 seções do
template de referência. O output é um doc **autocontido**, pensado para ser lido
por outro agente de IA que vai construir interfaces a partir dele.

Você NÃO escreve CSS, componentes React, nem implementa nada. Você produz **um
arquivo `.md` de especificação de design**.

## Arquivos da skill

- `references/TEMPLATE-reference.md` — template de referência (design system estilo
  Spotify). É o **molde estrutural**: copie a estrutura das 9 seções, substitua os
  valores pelos tokens do usuário. **Leia este arquivo antes de gerar** para
  espelhar formato, profundidade e tom das tabelas/seções.

## Processo NÃO-NEGOCIÁVEL — 3 fases

1. **SETUP** — coleta de tokens via perguntas (com defaults).
2. **GERAÇÃO** — produz o doc completo nas 9 seções.
3. **ENTREGA + AUTOAVALIAÇÃO** — salva o arquivo e oferece refinamento.

Nenhuma fase pode ser pulada. Não gere antes de ter os tokens mínimos.

---

## FASE 1 — SETUP (coleta de tokens)

Antes de gerar, leia `references/TEMPLATE-reference.md`. Depois colete os tokens.
Use a ferramenta de perguntas estruturadas (AskUserQuestion) quando disponível;
caso contrário, faça as perguntas em texto. Agrupe — **não faça 1 pergunta por
vez de forma arrastada**. Cada token tem default: se o usuário disser "usa o
default" ou "tanto faz", aplique o default e siga.

Tokens a coletar (mínimo viável = ⭐):

| # | Token | Pergunta | Default |
|---|-------|----------|---------|
| 1 ⭐ | **Nome / inspiração** | Nome do produto e referência visual ("inspirado em Spotify/Linear/Stripe…") | "Untitled" / nenhum |
| 2 ⭐ | **Tema base** | Dark, Light ou ambos? | Dark |
| 3 ⭐ | **Cor primária / marca** | Hex do accent principal (CTAs, estados ativos) | `#1ed760` |
| 4 ⭐ | **Cor de fundo** | Hex da superfície mais profunda | Dark: `#121212` / Light: `#ffffff` |
| 5 | **Escala de superfícies** | 2–3 tons de elevação acima do fundo | Derivar do fundo (+lighten) |
| 6 ⭐ | **Texto base + secundário** | Hex do texto primário e do mutado | `#ffffff` / `#b3b3b3` |
| 7 | **Cores semânticas** | error / warning / success / info | `#f3727f`/`#ffa42b`/`#1ed760`/`#539df5` |
| 8 ⭐ | **Border-radius / geometria** | Estilo: Pill (arredondado), Soft (8–12px), Sharp (2–4px), ou escala custom | Soft |
| 9 ⭐ | **Tipografia** | Família(s) de fonte + pesos usados | system-ui / 700·400 |
| 10 | **Densidade / espaçamento** | Compacto (app) ou Arejado (marketing); unidade base | Compacto / 8px |
| 11 | **Sombras / elevação** | Pesadas, Sutis ou Nenhuma | Conforme tema (dark=pesadas) |
| 12 | **Caminho de saída** | Onde salvar o `.md` | `DESIGN/DESIGN-<nome>.md` |

Regras do setup:
- Faça no máximo ~2 rodadas de perguntas. Agrupe os ⭐ na primeira rodada;
  os opcionais na segunda (ou derive defaults e só confirme).
- Se o usuário deu uma **inspiração** (ex: "estilo Linear"), preencha defaults
  coerentes com essa referência e mostre para confirmação em vez de perguntar tudo.
- Valide hex (`#rrggbb`). Se faltar contraste óbvio (texto = fundo), avise.
- Derive o que dá: superfícies a partir do fundo, border-scale a partir do estilo
  escolhido, escala de espaçamento a partir da unidade base.

---

## FASE 2 — GERAÇÃO (9 seções)

Produza o documento espelhando **exatamente** a estrutura do template. Seções
obrigatórias, na ordem:

1. **Visual Theme & Atmosphere** — 2–3 parágrafos descrevendo a filosofia visual
   derivada dos tokens (tema, cor marca, geometria), + bloco **Key Characteristics**
   (6–8 bullets).
2. **Color Palette & Roles** — agrupado em: Primary/Brand, Text, Semantic,
   Surface & Border, Shadows. Cada cor com **nome legível + hex + papel funcional**.
3. **Typography Rules** — Font Families, tabela de **Hierarchy** (Role · Font ·
   Size · Weight · Line Height · Letter Spacing · Notes), e **Principles** (3–5).
4. **Component Stylings** — Buttons (variantes), Cards & Containers, Inputs,
   Navigation — com valores concretos (bg, text, padding, radius, border, uso).
5. **Layout Principles** — Spacing System (unidade + escala), Grid & Container,
   Whitespace Philosophy, Border Radius Scale.
6. **Depth & Elevation** — tabela de níveis (Base/Surface/Elevated/Dialog/Inset)
   com treatment + uso, + Shadow Philosophy.
7. **Do's and Don'ts** — duas listas concretas e específicas dos tokens.
8. **Responsive Behavior** — tabela de Breakpoints + Collapsing Strategy.
9. **Agent Prompt Guide** — Quick Color Reference, 4–5 Example Component Prompts
   (prontos para colar em outro agente), e um Iteration Guide numerado.

Regras de geração:
- **Use os tokens reais do usuário** em todo valor — nunca deixe placeholder
  tipo `<cor>`. Onde o usuário não definiu, use o default derivado e marque
  coerência (não invente cor aleatória).
- Mantenha o **tom de spec técnica**: valores exatos (hex, px, rem, pesos),
  tabelas, sem enrolação.
- Profundidade ≈ template de referência (não mais curto). Tabelas completas.
- Título do doc: `# Design System — <Nome>` (+ "Inspired by X" se houver inspiração).
- Se tema = ambos, documente dark como base e adicione overrides light por seção.

---

## FASE 3 — ENTREGA + AUTOAVALIAÇÃO

1. Salve em `references`→ não. Salve no **caminho de saída** (token 12). Use Write.
2. Confirme o path salvo e dê um resumo de 1 linha dos tokens aplicados.
3. Entregue uma **tabela de autoavaliação** curta:

   | Critério | Nota (1–5) | Observação |
   |----------|-----------|------------|
   | Cobertura das 9 seções | | |
   | Consistência dos tokens | | |
   | Contraste/acessibilidade | | |
   | Pronto para consumo por agente | | |

4. Ofereça refinamento: "Quer ajustar [cor/raio/tipografia] ou gerar variante
   [light/dark]?" Se sim, edite o arquivo gerado — não recomece do zero.

---

## Princípios

- **Setup primeiro, sempre.** Nunca gere sem tokens mínimos (⭐).
- **Defaults sensatos > fricção.** Pergunte o essencial, derive o resto, confirme.
- **Espelhe o template**, não o conteúdo Spotify — a marca é do usuário.
- **Output é spec, não código.** O consumidor é outro agente de IA.
- **Valores concretos.** Todo token vira hex/px/rem/peso — zero abstração vaga.
