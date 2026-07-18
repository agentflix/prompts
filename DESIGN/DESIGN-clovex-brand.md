# Design System — Clovex

## 1. Visual Theme & Atmosphere

Clovex is a dual-theme product identity built around a single hero asset: a four-stop
diagonal gradient that runs **Green → Mint → Lavender → Purple** (`#4BEA7B → #67E4C3 →
#7D9CFF → #7A3CFF`). The design philosophy is "neutral canvas, gradient signature" — the
surfaces stay quiet and near-monochrome so the brand gradient reads as the one true source
of color. In **Dark Mode** (the principal theme) the product lives in a deep blue-black
(`#0B0B0F`) where the gradient glows; in **Light Mode** the same gradient sits on clean white
(`#FFFFFF`), shifting from luminous to crisp without changing the brand mark.

The gradient is the logo's energy and should be treated as a **brand-only accent**: the
Clovex mark, hero backgrounds, primary CTAs, active states, and key highlights. It is never
spread across body surfaces or used as decorative fill behind text. The mark itself flips
contrast by theme — white Clovex on dark, black Clovex on light — while the gradient stays
identical, giving instant recognition across both modes.

Surfaces follow a tight three-step elevation ladder (`Background → Surface → Border`) in each
theme. Typography and geometry stay modern-SaaS: soft rounded corners, a neutral high-legibility
sans, and a clear bold/regular weight split. The result is a calm, premium interface where a
single multicolor gradient does all the brand-talking.

**Key Characteristics:**
- Dual theme — Dark (`#0B0B0F`) principal, Light (`#FFFFFF`) — same gradient on both
- Four-stop brand gradient (`#4BEA7B → #67E4C3 → #7D9CFF → #7A3CFF`) as the singular signature
- Gradient is brand-only: mark, hero, primary CTA, active states — never decorative fill
- Clovex mark flips contrast by theme (white on dark / black on light), gradient stays fixed
- Near-monochrome neutral surfaces so the gradient owns all color
- Three-step elevation ladder per theme (Background / Surface / Border)
- Soft rounded geometry, modern sans typography, bold/regular weight split
- Premium dark hero gradient variant for marketing-grade landing surfaces

## 2. Color Palette & Roles

### Brand (Gradient Stops)
- **Green** (`#4BEA7B`): Gradient start — freshest, leftmost stop
- **Mint** (`#67E4C3`): Gradient stop 2 — green→blue transition
- **Lavender** (`#7D9CFF`): Gradient stop 3 — blue→violet transition
- **Purple** (`#7A3CFF`): Gradient end — deepest, rightmost stop
- **Official Gradient**: `linear-gradient(135deg, #4BEA7B 0%, #67E4C3 35%, #7D9CFF 65%, #7A3CFF 100%)`
- **Dark Premium Gradient** (hero only): `linear-gradient(135deg, #4BEA7B 0%, #52D4B8 25%, #6B9EFF 60%, #7A3CFF 100%)`

### Dark Theme (Principal)
- **Background** (`#0B0B0F`): Deepest surface, page background
- **Surface** (`#151821`): Cards, panels, elevated containers
- **Border** (`#232734`): Dividers, card borders, input outlines
- **Text** (`#FFFFFF`): Primary text
- **Text Secondary** (`#A0A8B8`): Muted labels, captions, inactive items

### Light Theme
- **Background** (`#FFFFFF`): Page background
- **Surface** (`#F8FAFC`): Cards, panels, elevated containers
- **Border** (`#E5E7EB`): Dividers, card borders, input outlines
- **Text** (`#111827`): Primary text
- **Text Secondary** (`#6B7280`): Muted labels, captions, inactive items

### Semantic *(derived — harmonized to brand, adjust if you have official values)*
- **Success** (`#4BEA7B`): Reuses brand Green — success states, confirmations
- **Error** (`#F2546B`): Destructive actions, error states
- **Warning** (`#F5A623`): Warning states, caution
- **Info** (`#7D9CFF`): Reuses brand Lavender — informational states

### Surface & Shadow tokens
- **Shadow (Dark)** *(derived)*: `rgba(0,0,0,0.45) 0px 8px 24px` — elevated panels on dark
- **Shadow (Light)** *(derived)*: `rgba(17,24,39,0.08) 0px 8px 24px` — elevated panels on light
- **Glow (brand)** *(derived)*: `rgba(122,60,255,0.35) 0px 0px 32px` — gradient CTA hover halo

## 3. Typography Rules

*Font not specified — defaulting to a modern neutral sans. Swap `Inter` for your brand font.*

### Font Families
- **UI / Body**: `Inter`, fallbacks: `system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Display / Headings**: same family, heavier weights (700–800)

### Hierarchy

| Role | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|--------|-------------|----------------|-------|
| Display | 48px (3.00rem) | 800 | 1.05 | -0.02em | Hero headlines, gradient-clip optional |
| Section Title | 32px (2.00rem) | 700 | 1.15 | -0.01em | Page / section heads |
| Feature Heading | 24px (1.50rem) | 700 | 1.25 | normal | Card titles, subsections |
| Subheading | 18px (1.13rem) | 600 | 1.35 | normal | Lead text, secondary heads |
| Body Bold | 16px (1.00rem) | 600 | 1.50 | normal | Emphasized body |
| Body | 16px (1.00rem) | 400 | 1.55 | normal | Standard body |
| Button | 15px (0.94rem) | 600 | 1.00 | normal | CTA labels |
| Caption Bold | 14px (0.88rem) | 600 | 1.45 | normal | Bold metadata |
| Caption | 14px (0.88rem) | 400 | 1.45 | normal | Metadata, helper text |
| Small | 13px (0.81rem) | 400 | 1.40 | normal | Fine print |
| Micro | 12px (0.75rem) | 500 | 1.33 | 0.01em | Tags, badges, counts |

### Principles
- **Bold/regular split**: weight does the hierarchy work — 700+ for heads, 600 for emphasis, 400 for body.
- **Tight display tracking**: large sizes use negative letter-spacing (-0.01 to -0.02em) for a modern, condensed feel.
- **Gradient text reserved**: clip the official gradient onto text only for hero display lines — never body.
- **Generous body line-height**: 1.5–1.55 on body for readability (this is more relaxed than the app-dense reference).

## 4. Component Stylings

Values shown as **Dark / Light** where they differ.

### Buttons

**Primary (Gradient)**
- Background: Official Gradient (`135deg, #4BEA7B → #67E4C3 → #7D9CFF → #7A3CFF`)
- Text: `#FFFFFF` (dark) / `#FFFFFF` (light) — gradient is dark enough at the purple end
- Padding: 12px 24px
- Radius: 10px
- Hover: brand glow `rgba(122,60,255,0.35) 0px 0px 32px`
- Use: Primary CTA, key actions

**Secondary (Solid Neutral)**
- Background: `#151821` (dark) / `#F8FAFC` (light)
- Text: `#FFFFFF` / `#111827`
- Border: `1px solid #232734` / `1px solid #E5E7EB`
- Padding: 12px 24px
- Radius: 10px
- Use: Secondary actions

**Ghost / Outlined**
- Background: transparent
- Text: `#FFFFFF` / `#111827`
- Border: `1px solid #232734` / `1px solid #E5E7EB`
- Hover border: gradient via border-image, or `#7D9CFF`
- Radius: 10px
- Use: Tertiary actions, toolbar buttons

**Icon Button**
- Background: `#151821` / `#F8FAFC`
- Radius: 10px (or 50% for round)
- Padding: 10px
- Use: Compact controls

### Cards & Containers
- Background: `#151821` / `#F8FAFC`
- Border: `1px solid #232734` / `1px solid #E5E7EB`
- Radius: 12px–16px
- Shadow: `rgba(0,0,0,0.45) 0px 8px 24px` / `rgba(17,24,39,0.08) 0px 8px 24px` on elevated
- Hover: border lightens toward `#7D9CFF` for interactive cards

### Inputs
- Background: `#0B0B0F` / `#FFFFFF`
- Surface variant: `#151821` / `#F8FAFC`
- Text: `#FFFFFF` / `#111827`, placeholder `#A0A8B8` / `#6B7280`
- Border: `1px solid #232734` / `1px solid #E5E7EB`
- Radius: 10px
- Focus: border `#7D9CFF`, ring `0 0 0 3px rgba(125,156,255,0.25)`

### Navigation
- Background: `#0B0B0F` / `#FFFFFF`
- Active item: `#FFFFFF` / `#111827`, with gradient indicator (underline/left-bar using Official Gradient)
- Inactive item: `#A0A8B8` / `#6B7280`
- Clovex mark top-left: white on dark, black on light, gradient icon fixed

## 5. Layout Principles

### Spacing System
- Base unit: 8px
- Scale: 2px, 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

### Grid & Container
- Sidebar (optional) + main content, or centered max-width container for marketing
- Card grids: responsive auto-fill, min ~280px columns
- Max content width: 1200px–1280px for marketing pages

### Whitespace Philosophy
- **Calm canvas**: neutral surfaces get breathing room so the gradient pops where used.
- **Marketing vs app**: hero/marketing surfaces lean airy (32–64px gaps); dense app views tighten to 8–16px.

### Border Radius Scale
- Subtle (6px): tags, small chips
- Standard (10px): buttons, inputs, icon buttons
- Comfortable (12px): cards, panels
- Large (16px): hero cards, modals
- Pill (9999px): badges, filter chips
- Circle (50%): avatars, round icon buttons

## 6. Depth & Elevation

| Level | Dark Treatment | Light Treatment | Use |
|-------|----------------|-----------------|-----|
| Base (0) | `#0B0B0F` background | `#FFFFFF` background | Page background |
| Surface (1) | `#151821` + `1px #232734` | `#F8FAFC` + `1px #E5E7EB` | Cards, panels, sidebar |
| Elevated (2) | `rgba(0,0,0,0.45) 0px 8px 24px` | `rgba(17,24,39,0.08) 0px 8px 24px` | Dropdowns, hover cards |
| Dialog (3) | `rgba(0,0,0,0.6) 0px 16px 48px` | `rgba(17,24,39,0.12) 0px 16px 48px` | Modals, overlays |
| Brand Glow | `rgba(122,60,255,0.35) 0px 0px 32px` | `rgba(122,60,255,0.25) 0px 0px 32px` | Gradient CTA hover halo |

**Shadow Philosophy**: Dark mode uses heavier, near-black shadows to register depth against the
blue-black canvas; light mode uses soft slate-tinted shadows (`#111827` @ low opacity) to avoid
harsh gray. The brand glow is the only colored shadow — reserved for gradient CTAs.

## 7. Do's and Don'ts

### Do
- Keep surfaces neutral (`#0B0B0F`/`#151821` dark, `#FFFFFF`/`#F8FAFC` light) so the gradient owns color
- Use the **Official Gradient** for the mark, primary CTA, active indicators, and hero
- Use the **Dark Premium Gradient** only for marketing hero backgrounds
- Flip the Clovex mark contrast by theme (white on dark, black on light) — keep the gradient fixed
- Pair gradient CTAs with the brand glow on hover for a premium tactile feel
- Hold the 135deg angle and the 0/35/65/100% stop positions for gradient consistency

### Don't
- Don't spread the gradient across large body surfaces or behind running text
- Don't recolor or reorder the gradient stops — the Green→Purple direction is the identity
- Don't introduce extra brand hues — the four-stop gradient + neutrals is the full palette
- Don't use pure gray shadows in light mode — tint toward `#111827`
- Don't mix dark and light tokens within one theme — keep each theme's ladder intact
- Don't apply gradient text to body copy — display headlines only

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile | <480px | 1-column, bottom nav, condensed hero |
| Mobile Large | 480–640px | 1-column, larger type |
| Tablet | 640–768px | 2-column grid |
| Tablet Large | 768–1024px | sidebar appears, 3-column grid |
| Desktop | 1024–1280px | full layout |
| Large Desktop | >1280px | max-width container, expanded grid |

### Collapsing Strategy
- Sidebar: full → icon-only → bottom bar on mobile
- Card grid: 4 → 3 → 2 → 1 columns
- Hero gradient: full-bleed maintained at all sizes, text scales down
- Clovex mark: maintained at all sizes (icon-only below mobile)

## 9. Agent Prompt Guide

### Quick Color Reference
- **Dark** — Background `#0B0B0F` · Surface `#151821` · Border `#232734` · Text `#FFFFFF` · Secondary `#A0A8B8`
- **Light** — Background `#FFFFFF` · Surface `#F8FAFC` · Border `#E5E7EB` · Text `#111827` · Secondary `#6B7280`
- **Brand gradient**: `#4BEA7B → #67E4C3 → #7D9CFF → #7A3CFF` (135deg)
- **Stops**: Green `#4BEA7B` · Mint `#67E4C3` · Lavender `#7D9CFF` · Purple `#7A3CFF`

### Example Component Prompts
- "Create a primary CTA: background `linear-gradient(135deg, #4BEA7B 0%, #67E4C3 35%, #7D9CFF 65%, #7A3CFF 100%)`, white text, 10px radius, 12px 24px padding, weight 600. On hover add glow `rgba(122,60,255,0.35) 0px 0px 32px`."
- "Design a dark card: `#151821` background, `1px solid #232734` border, 12px radius, white title (24px/700), `#A0A8B8` subtitle (14px/400). Shadow `rgba(0,0,0,0.45) 0px 8px 24px` on hover."
- "Build a light input: `#FFFFFF` background, `1px solid #E5E7EB` border, `#111827` text, `#6B7280` placeholder, 10px radius. Focus: border `#7D9CFF`, ring `0 0 0 3px rgba(125,156,255,0.25)`."
- "Create a hero section: full-bleed `linear-gradient(135deg, #4BEA7B 0%, #52D4B8 25%, #6B9EFF 60%, #7A3CFF 100%)` background, white Clovex mark, display headline 48px/800 with -0.02em tracking."
- "Design nav: `#0B0B0F` background, active item white with a gradient left-bar indicator, inactive `#A0A8B8`. Clovex mark top-left in white."

### Iteration Guide
1. Pick the theme (Dark principal / Light) — set the neutral ladder first
2. Place the Clovex mark with the fixed gradient + theme-correct contrast
3. Apply the Official Gradient only to mark, primary CTA, and active states
4. Use Dark Premium Gradient for marketing hero backgrounds only
5. Keep all other surfaces neutral — let the gradient be the single color voice
6. Add brand glow on gradient CTA hover for the premium finish
