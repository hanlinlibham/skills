# Style Presets Reference

Curated visual styles for Frontend Slides. Each preset is inspired by real design references — no generic "AI slop" aesthetics. **Abstract shapes only — no illustrations.**

**Viewport CSS:** For mandatory base styles, see [references/viewport-base.css](references/viewport-base.css). Include in every presentation.

---

## Chinese Font Strategy

Every preset must include Chinese font fallback. Load via Google Fonts alongside Latin fonts.

**Standard Chinese Font Stack:**

| Category | Font | Weight | Use Case |
|----------|------|--------|----------|
| Sans | Noto Sans SC | 300-700 | Body text, UI, data labels |
| Serif | Noto Serif SC | 400-700 | Display headings, editorial |
| Literary | LXGW WenKai | 400-700 | Drop caps, quotes, literary feel |

**Loading template:**
```html
<!-- Add Chinese font families to the Google Fonts link -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Noto+Serif+SC:wght@400;600;700&family=LXGW+WenKai:wght@400;700&display=swap" rel="stylesheet">
```

**Font-family pairing rules:**
- Sans-serif preset display/body: append `, 'Noto Sans SC', sans-serif`
- Serif preset display: append `, 'Noto Serif SC', serif`
- Serif preset body: append `, 'Noto Sans SC', sans-serif`
- Mono preset: append `, 'Noto Sans SC', sans-serif` as final fallback
- Literary/editorial preset: can use `'LXGW WenKai'` for display, `'Noto Sans SC'` for body

Example:
```css
:root {
    --font-display: 'Archivo Black', 'Noto Sans SC', sans-serif;
    --font-body: 'Space Grotesk', 'Noto Sans SC', sans-serif;
}
```

---

## Dark Themes

### 1. Bold Signal

**Vibe:** Confident, bold, modern, high-impact

**Layout:** Colored card on dark gradient. Number top-left, navigation top-right, title bottom-left.

**Typography:**
- Display: `Archivo Black`, `Noto Sans SC` (900)
- Body: `Space Grotesk`, `Noto Sans SC` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #1a1a1a;
    --bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card-bg: #FF5722;
    --text-primary: #ffffff;
    --text-on-card: #1a1a1a;
    --font-display: 'Archivo Black', 'Noto Sans SC', sans-serif;
    --font-body: 'Space Grotesk', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Bold colored card as focal point (orange, coral, or vibrant accent)
- Large section numbers (01, 02, etc.)
- Navigation breadcrumbs with active/inactive opacity states
- Grid-based layout for precise alignment

---

### 2. Electric Studio

**Vibe:** Bold, clean, professional, high contrast

**Layout:** Split panel—white top, blue bottom. Brand marks in corners.

**Typography:**
- Display: `Manrope`, `Noto Sans SC` (800)
- Body: `Manrope`, `Noto Sans SC` (400/500)

**Colors:**
```css
:root {
    --bg-dark: #0a0a0a;
    --bg-white: #ffffff;
    --accent-blue: #4361ee;
    --text-dark: #0a0a0a;
    --text-light: #ffffff;
    --font-display: 'Manrope', 'Noto Sans SC', sans-serif;
    --font-body: 'Manrope', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Two-panel vertical split
- Accent bar on panel edge
- Quote typography as hero element
- Minimal, confident spacing

---

### 3. Creative Voltage

**Vibe:** Bold, creative, energetic, retro-modern

**Layout:** Split panels—electric blue left, dark right. Script accents.

**Typography:**
- Display: `Syne`, `Noto Sans SC` (700/800)
- Mono: `Space Mono`, `Noto Sans SC` (400/700)

**Colors:**
```css
:root {
    --bg-primary: #0066ff;
    --bg-dark: #1a1a2e;
    --accent-neon: #d4ff00;
    --text-light: #ffffff;
    --font-display: 'Syne', 'Noto Sans SC', sans-serif;
    --font-body: 'Space Mono', 'Noto Sans SC', monospace;
}
```

**Signature Elements:**
- Electric blue + neon yellow contrast
- Halftone texture patterns
- Neon badges/callouts
- Script typography for creative flair

---

### 4. Dark Botanical

**Vibe:** Elegant, sophisticated, artistic, premium

**Layout:** Centered content on dark. Abstract soft shapes in corner.

**Typography:**
- Display: `Cormorant`, `Noto Serif SC` (400/600) — elegant serif
- Body: `IBM Plex Sans`, `Noto Sans SC` (300/400)

**Colors:**
```css
:root {
    --bg-primary: #0f0f0f;
    --text-primary: #e8e4df;
    --text-secondary: #9a9590;
    --accent-warm: #d4a574;
    --accent-pink: #e8b4b8;
    --accent-gold: #c9b896;
    --font-display: 'Cormorant', 'Noto Serif SC', serif;
    --font-body: 'IBM Plex Sans', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Abstract soft gradient circles (blurred, overlapping)
- Warm color accents (pink, gold, terracotta)
- Thin vertical accent lines
- Italic signature typography
- **No illustrations—only abstract CSS shapes**

---

## Light Themes

### 5. Notebook Tabs

**Vibe:** Editorial, organized, elegant, tactile

**Layout:** Cream paper card on dark background. Colorful tabs on right edge.

**Typography:**
- Display: `Bodoni Moda`, `Noto Serif SC` (400/700) — classic editorial
- Body: `DM Sans`, `Noto Sans SC` (400/500)

**Colors:**
```css
:root {
    --bg-outer: #2d2d2d;
    --bg-page: #f8f6f1;
    --text-primary: #1a1a1a;
    --tab-1: #98d4bb; /* Mint */
    --tab-2: #c7b8ea; /* Lavender */
    --tab-3: #f4b8c5; /* Pink */
    --tab-4: #a8d8ea; /* Sky */
    --tab-5: #ffe6a7; /* Cream */
    --font-display: 'Bodoni Moda', 'Noto Serif SC', serif;
    --font-body: 'DM Sans', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Paper container with subtle shadow
- Colorful section tabs on right edge (vertical text)
- Binder hole decorations on left
- Tab text must scale with viewport: `font-size: clamp(0.5rem, 1vh, 0.7rem)`

---

### 6. Pastel Geometry

**Vibe:** Friendly, organized, modern, approachable

**Layout:** White card on pastel background. Vertical pills on right edge.

**Typography:**
- Display: `Plus Jakarta Sans`, `Noto Sans SC` (700/800)
- Body: `Plus Jakarta Sans`, `Noto Sans SC` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #c8d9e6;
    --card-bg: #faf9f7;
    --pill-pink: #f0b4d4;
    --pill-mint: #a8d4c4;
    --pill-sage: #5a7c6a;
    --pill-lavender: #9b8dc4;
    --pill-violet: #7c6aad;
    --font-display: 'Plus Jakarta Sans', 'Noto Sans SC', sans-serif;
    --font-body: 'Plus Jakarta Sans', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Rounded card with soft shadow
- **Vertical pills on right edge** with varying heights (like tabs)
- Consistent pill width, heights: short → medium → tall → medium → short
- Download/action icon in corner

---

### 7. Split Pastel

**Vibe:** Playful, modern, friendly, creative

**Layout:** Two-color vertical split (peach left, lavender right).

**Typography:**
- Display: `Outfit`, `Noto Sans SC` (700/800)
- Body: `Outfit`, `Noto Sans SC` (400/500)

**Colors:**
```css
:root {
    --bg-peach: #f5e6dc;
    --bg-lavender: #e4dff0;
    --text-dark: #1a1a1a;
    --badge-mint: #c8f0d8;
    --badge-yellow: #f0f0c8;
    --badge-pink: #f0d4e0;
    --font-display: 'Outfit', 'Noto Sans SC', sans-serif;
    --font-body: 'Outfit', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Split background colors
- Playful badge pills with icons
- Grid pattern overlay on right panel
- Rounded CTA buttons

---

### 8. Vintage Editorial

**Vibe:** Witty, confident, editorial, personality-driven

**Layout:** Centered content on cream. Abstract geometric shapes as accent.

**Typography:**
- Display: `Fraunces`, `Noto Serif SC` (700/900) — distinctive serif
- Body: `Work Sans`, `Noto Sans SC` (400/500)

**Colors:**
```css
:root {
    --bg-cream: #f5f3ee;
    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --accent-warm: #e8d4c0;
    --font-display: 'Fraunces', 'Noto Serif SC', serif;
    --font-body: 'Work Sans', 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Abstract geometric shapes (circle outline + line + dot)
- Bold bordered CTA boxes
- Witty, conversational copy style
- **No illustrations—only geometric CSS shapes**

---

## Specialty Themes

### 9. Neon Cyber

**Vibe:** Futuristic, techy, confident

**Typography:** `Clash Display` + `Satoshi` (Fontshare), CN fallback: `Noto Sans SC`

**Colors:** Deep navy (#0a0f1c), cyan accent (#00ffcc), magenta (#ff00aa)

**Font vars:**
```css
:root {
    --font-display: 'Clash Display', 'Noto Sans SC', sans-serif;
    --font-body: 'Satoshi', 'Noto Sans SC', sans-serif;
}
```

**Signature:** Particle backgrounds, neon glow, grid patterns

---

### 10. Terminal Green

**Vibe:** Developer-focused, hacker aesthetic

**Typography:** `JetBrains Mono` (monospace only), CN fallback: `Noto Sans SC`

**Colors:** GitHub dark (#0d1117), terminal green (#39d353)

**Font vars:**
```css
:root {
    --font-display: 'JetBrains Mono', 'Noto Sans SC', monospace;
    --font-body: 'JetBrains Mono', 'Noto Sans SC', monospace;
}
```

**Signature:** Scan lines, blinking cursor, code syntax styling

---

### 11. Swiss Modern

**Vibe:** Clean, precise, Bauhaus-inspired

**Typography:** `Archivo` (800) + `Nunito` (400), CN fallback: `Noto Sans SC`

**Colors:** Pure white, pure black, red accent (#ff3300)

**Font vars:**
```css
:root {
    --font-display: 'Archivo', 'Noto Sans SC', sans-serif;
    --font-body: 'Nunito', 'Noto Sans SC', sans-serif;
}
```

**Signature:** Visible grid, asymmetric layouts, geometric shapes

---

### 12. Paper & Ink

**Vibe:** Editorial, literary, thoughtful

**Typography:** `Cormorant Garamond` + `Source Serif 4`, CN: `LXGW WenKai` (display) + `Noto Serif SC` (body)

**Colors:** Warm cream (#faf9f7), charcoal (#1a1a1a), crimson accent (#c41e3a)

**Font vars:**
```css
:root {
    --font-display: 'Cormorant Garamond', 'LXGW WenKai', serif;
    --font-body: 'Source Serif 4', 'Noto Serif SC', serif;
}
```

**Signature:** Drop caps, pull quotes, elegant horizontal rules

---

## Font Pairing Quick Reference

| Preset | Display Font | Body Font | CN Fallback | Source |
|--------|--------------|-----------|-------------|--------|
| Bold Signal | Archivo Black | Space Grotesk | Noto Sans SC | Google |
| Electric Studio | Manrope | Manrope | Noto Sans SC | Google |
| Creative Voltage | Syne | Space Mono | Noto Sans SC | Google |
| Dark Botanical | Cormorant | IBM Plex Sans | Noto Serif SC / Noto Sans SC | Google |
| Notebook Tabs | Bodoni Moda | DM Sans | Noto Serif SC / Noto Sans SC | Google |
| Pastel Geometry | Plus Jakarta Sans | Plus Jakarta Sans | Noto Sans SC | Google |
| Split Pastel | Outfit | Outfit | Noto Sans SC | Google |
| Vintage Editorial | Fraunces | Work Sans | Noto Serif SC / Noto Sans SC | Google |
| Neon Cyber | Clash Display | Satoshi | Noto Sans SC | Fontshare |
| Terminal Green | JetBrains Mono | JetBrains Mono | Noto Sans SC | JetBrains |
| Swiss Modern | Archivo | Nunito | Noto Sans SC | Google |
| Paper & Ink | Cormorant Garamond | Source Serif 4 | LXGW WenKai / Noto Serif SC | Google |
| **Research Formal** | Noto Serif SC | Noto Sans SC | (native) | Google |
| **Roadshow Elegance** | Playfair Display | Noto Sans SC | Noto Serif SC | Google |
| **Data Dashboard** | Noto Sans SC | Noto Sans SC | (native) | Google |

---

## Financial Themes (金融专用)

### 13. Research Formal (研报正式)

**Vibe:** Institutional, authoritative, data-driven. Suitable for research reports, analyst presentations, internal review meetings.

**Layout:** Clean white background with navy sidebar navigation. Emphasis on tables and structured data. Section numbers in sidebar.

**Typography:**
- Display: `Noto Serif SC` (600/700) — authoritative serif for Chinese headings
- Body: `Noto Sans SC` (400/500) — clean sans for data and body text

**Colors:**
```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #1a1a2e;
    --text-secondary: #5a5a7a;
    --accent: #1a365d;
    --accent-secondary: #2563eb;
    --accent-gold: #c5963a;
    --border-color: rgba(26, 54, 93, 0.12);
    --color-positive: #dc2626;
    --color-negative: #16a34a;
    --font-display: 'Noto Serif SC', serif;
    --font-body: 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Navy blue sidebar with section navigation and page numbers
- Horizontal rule separators between sections (2px solid navy)
- Tables with navy header row and alternating gray rows
- Source citations in small text at slide bottom
- Company/team logo placement: top-right corner
- Section numbering: large navy numerals (01, 02, 03)

**Financial Layouts:** Optimized for KPI Dashboard, Data Table, Chart + Text Split. See [references/financial-layouts.md](references/financial-layouts.md).

---

### 14. Roadshow Elegance (路演风范)

**Vibe:** Premium, confident, investor-grade. For IPO roadshows, investor meetings, board presentations.

**Layout:** Dark gradient background with centered content. Gold accent highlights key metrics. Generous whitespace for gravitas.

**Typography:**
- Display: `Playfair Display`, `Noto Serif SC` (700/800) — premium serif
- Body: `Noto Sans SC` (300/400) — light weight for elegance

**Colors:**
```css
:root {
    --bg-primary: #0c1929;
    --bg-gradient: linear-gradient(145deg, #0c1929 0%, #162d50 40%, #0c1929 100%);
    --text-primary: #f0ece4;
    --text-secondary: #8a9bb5;
    --accent: #d4a853;
    --accent-secondary: #e8c882;
    --border-color: rgba(212, 168, 83, 0.2);
    --color-positive: #ef4444;
    --color-negative: #22c55e;
    --card-bg: rgba(255, 255, 255, 0.04);
    --font-display: 'Playfair Display', 'Noto Serif SC', serif;
    --font-body: 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Subtle radial gradient glow behind key content
- Gold accent lines (1px) as decorative separators
- Large KPI values in gold with light glow effect
- Minimal text, maximum impact
- Abstract geometric shapes: thin gold circles, lines
- Progress indicators and slide numbers in muted gold

**Best for:** Title slides with company valuation, KPI highlights with trend arrows (CSS `::after` triangles, not emoji), full-width chart slides with dark chart themes.

---

### 15. Data Dashboard (数据简报)

**Vibe:** Efficient, analytical, information-dense. For daily/weekly market updates, portfolio reviews, data-driven briefings.

**Layout:** Grid-based with tight spacing. Header bar with date and context. Content area maximizes data display. 2-3 column grids for KPI cards.

**Typography:**
- Display: `Noto Sans SC` (700) — clean, functional
- Body: `Noto Sans SC` (400) — consistent sans throughout

**Colors:**
```css
:root {
    --bg-primary: #f5f5f5;
    --bg-card: #ffffff;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --accent: #2563eb;
    --accent-secondary: #60a5fa;
    --border-color: #e5e7eb;
    --color-positive: #dc2626;
    --color-negative: #16a34a;
    --font-display: 'Noto Sans SC', sans-serif;
    --font-body: 'Noto Sans SC', sans-serif;
}
```

**Signature Elements:**
- Top status bar: date + report title + page count
- Card-based layout with thin borders (1px solid #e5e7eb)
- Compact KPI cards with mini inline sparklines (SVG)
- Data tables with fixed header and zebra striping
- Trend indicators: CSS triangles + percentage (never emoji)
- Minimal decoration, maximum data real estate
- Color coding: blue = neutral/info, red = up (A-share), green = down

**Best for:** Multi-metric overview pages, dense comparison tables, chart grids (2x2), status/alert slides.

---

## DO NOT USE (Generic AI Patterns)

**Fonts:** Inter, Roboto, Arial, system fonts as display

**Colors:** `#6366f1` (generic indigo), purple gradients on white

**Layouts:** Everything centered, generic hero sections, identical card grids

**Decorations:** Realistic illustrations, gratuitous glassmorphism, drop shadows without purpose

---

## CSS Gotchas

### Negating CSS Functions

**WRONG — silently ignored by browsers (no console error):**
```css
right: -clamp(28px, 3.5vw, 44px);   /* Browser ignores this */
margin-left: -min(10vw, 100px);      /* Browser ignores this */
```

**CORRECT — wrap in `calc()`:**
```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));  /* Works */
margin-left: calc(-1 * min(10vw, 100px));     /* Works */
```

CSS does not allow a leading `-` before function names. The browser silently discards the entire declaration — no error, the element just appears in the wrong position. **Always use `calc(-1 * ...)` to negate CSS function values.**

