---
name: Lycaon Security
description: Tactical security operations platform with obsidian surfaces and classic gold accents
colors:
  primary: "#D4AF37"
  primary-light: "#F5D77F"
  primary-dark: "#996515"
  neutral-bg: "#09090B"
  surface: "#121216"
  surface-elevated: "#18181F"
  surface-hover: "#1E1E28"
  text-primary: "#F4F4F5"
  text-secondary: "#A1A1AA"
  text-muted: "#A1A1AA"
  border-hairline: "rgba(255, 255, 255, 0.08)"
  status-success: "#10B981"
  status-warning: "#F59E0B"
  status-danger: "#EF4444"
typography:
  display:
    fontFamily: "Inter, sans-serif"
    fontSize: "clamp(2rem, 4vw, 3rem)"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Inter, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "normal"
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.08em"
rounded:
  xs: "4px"
  sm: "8px"
  md: "10px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral-bg}"
    rounded: "{rounded.lg}"
    padding: "10px 20px"
  button-primary-hover:
    backgroundColor: "{colors.primary-light}"
  card-charcoal:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "20px"
---

# Design System: Lycaon Security

## Overview

**Creative North Star: "Tactical Obsidian & Precision Gold"**

Lycaon Security embodies a high-stakes, defense-grade visual language designed for mission-critical operations. Surfaces are grounded in deep obsidian blacks (`#09090B`) and charcoal layers (`#121216`), structured by clean, subtle 1px micro-borders (`border-neutral-800` or `border-amber-500/20`). High-priority interactive elements feature solid metallic gold (`#D4AF37`) without neon halos, glows, or diffuse light blooms.

The interface prioritizes discipline, authority, and tactical composure. Data density is calibrated for rapid assessment without clutter, presenting crisp matte surfaces, static status indicators, and clean typography.

**Key Characteristics:**
- Deep obsidian foundation with multi-tier matte tonal elevation.
- Clean 1px micro-borders without glow halos.
- Precision engineering corner radius (12px standard).
- Dual typography stack: neutral production sans (Inter) with monospaced telemetry (JetBrains Mono).
- Completely static status dots without pulsing animations.

## Colors

The palette is strictly anchored by deep obsidian voids, warm tactical charcoals, neutral grays, and authoritative metallic gold accents.

### Primary
- **Classic Gold** (#D4AF37): Primary interactive brand color, used on primary action buttons, active navigation markers, and key status badges.
- **Light Gold** (#F5D77F): Hover states and high-emphasis telemetry callouts.
- **Dark Gold** (#996515): Subtle border accents and inactive badge markers.

### Neutral
- **Obsidian Black** (#09090B): Base background across all viewports.
- **Charcoal Surface** (#121216): Primary container, card, and table background.
- **Elevated Charcoal** (#18181F): Dropdowns, modals, and flyout navigation.
- **Surface Hover** (#1E1E28): Hover feedback for interactive rows and list cards.
- **Text Primary** (#F4F4F5): High-contrast crisp white for titles, values, and essential copy.
- **Text Secondary** (#A1A1AA): Muted technical copy, table headers, and contextual labels.
- **Text Muted** (#A1A1AA): High-contrast secondary labels and telemetry metadata.

### Named Rules
**The Rarity Rule.** Primary gold accents are reserved strictly for the primary action on any viewport or critical telemetry states; surfaces never get drenched in solid gold.
**The Matte Surface Rule.** All component surfaces and status indicators are static and matte. Diffuse glow effects, colored neon halos, and infinite pulsing animations are forbidden.
**The Solid Text Rule.** Headings and titles render in solid, high-contrast text. Gradient text, drop-shadow glows, and clip-path text fills are forbidden.

## Typography

**Display Font:** Inter
**Body Font:** Inter (fallback: -apple-system, BlinkMacSystemFont, sans-serif)
**Label/Mono Font:** JetBrains Mono, monospace

**Character:** Modern, clean, neutral production sans-serif for instantaneous legibility, paired with crisp monospaced glyphs for telemetry, IDs, currency, and timestamps.

### Hierarchy
- **Display** (800, clamp(2rem, 4vw, 3rem), 1.1): Hero banners and section flagships in solid crisp white.
- **Headline** (700, 1.75rem, 1.2): Modal titles and main view headers.
- **Title** (600, 1.25rem, 1.3): Card headings and panel section labels.
- **Body** (400, 0.9375rem, 1.5): Standard paragraphs, descriptions, and table data.
- **Label** (600, 0.75rem, uppercase, 0.08em tracking): Telemetry chips, column headers, and system tags.

### Named Rules
**The Telemetry Rule.** Every serial number, SKU, price, timestamp, and status token must render in `JetBrains Mono`.

## Layout

A modular CSS Grid and Flexbox system with structured gutters (`16px` to `24px`) anchored by responsive sidebar navigation. Maximum container widths adapt between `1400px` for dense data tables and `1200px` for standard operational forms.

## Elevation & Depth

Depth is established primarily through tonal layering (Obsidian `#09090B` → Charcoal `#121216` → Elevated `#18181F`) reinforced by crisp 1px neutral borders (`border-neutral-800` or `border-amber-500/20`) on matte surfaces.

### Shadow Vocabulary
- **Card Shadow** (`0 4px 16px rgba(0, 0, 0, 0.4)`): Standard resting card elevation.
- **Elevated Shadow** (`0 12px 32px rgba(0, 0, 0, 0.6)`): Modals and flyout menus.
- **No Glow Shadows.** Colored glow halos, box-shadow type glow, and colored drop-shadows are strictly forbidden.

## Shapes

- **Engineering Radius** (12px / `var(--radius-lg)`): The standard corner radius for all cards, containers, and buttons.
- **Sub-elements** (8px / `var(--radius-sm)`): Chips, nested icon containers, and badges.
- **Full Radius** (9999px): Static circular status dots and pill badges.

## Components

### Buttons
- **Shape:** 12px engineering radius (`var(--radius-lg)`).
- **Primary:** Solid Gold background (`#D4AF37`), black bold text (`#09090B`), padding `10px 20px`, matte surface without colored glow.
- **Hover / Focus:** Lifts slightly (`translateY(-2px)`) with light gold shift (`#F5D77F`) and clean 1px border.
- **Outline:** Subtle 1px neutral border (`border-neutral-800`), light gray text (`#D1D5DB`), transitions to gold text and subtle border hover.

### Status Indicators
- **Style:** Static solid circle (`w-2 h-2 rounded-full bg-gold/90` or `bg-emerald-400`).
- **Rule:** Never use `animate-pulse` or neon glow shadows.

### Cards / Containers
- **Corner Style:** 12px radius.
- **Background:** Charcoal `#121216`.
- **Border:** 1px clean neutral border (`border-neutral-800` or `border-amber-500/20`).
- **Padding:** 20px to 24px.

### Forms & Inputs
- **Background & Border:** Input fields use dark neutral surfaces (`bg-neutral-900 border border-neutral-800`) with smooth focus transition to `border-gold`.
- **Text & Placeholders:** Input text uses `#FFFFFF` / `#F4F4F5`. All placeholders must use accessible `#A1A1AA` (`placeholder:text-zinc-400`), guaranteeing a contrast ratio > 7:1 against dark surfaces (well above WCAG AA 4.5:1).
- **Icons:** Input leading icons use `#A1A1AA` (`text-zinc-400`) for crisp visual affordance without low-contrast degradation.

### Card Headers & Icon Flow
- **Side-by-side / Inline Integration:** Never place isolated rounded-square icon tiles stacked directly above headings (`icon-tile-stack`). Integrate icons horizontally within the heading (`flex items-center justify-center gap-2.5`) or embed them inside an integrated header bar.

## Do's and Don'ts

### Do:
- **Do** use `card-charcoal` and `btn-gold` as the primary structural building blocks.
- **Do** format technical metrics, product IDs, and currency in `JetBrains Mono`.
- **Do** maintain clean 1px borders (`border-neutral-800`, `border-amber-500/20`) on matte surfaces.
- **Do** render all status dots as static, solid indicators.
- **Do** place icons side-by-side with headings or inside unified header rows.
- **Do** maintain placeholder contrast >= 4.5:1 with `#A1A1AA` (`text-zinc-400`).

### Don't:
- **Don't** use `animate-pulse` or infinite looping animations on status indicators.
- **Don't** use gradient text (`bg-clip-text text-transparent`) on headings; use solid crisp white (`#F4F4F5` / `text-white`).
- **Don't** use glowing shadows (`shadow-[0_0_...]` or diffuse color halos); keep all shadows neutral or matte.
- **Don't** use Plus Jakarta Sans or overused AI fonts; use Inter as the primary production font.
- **Don't** stack isolated rounded-square icon tiles floating directly above card headings.
- **Don't** use low-contrast placeholders (`text-gray-500` / `#71717A`) on dark backgrounds.
- **Don't** introduce superfluous accent colors (like cyan) when not functionally required.
