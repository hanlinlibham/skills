# Fund Slides

> Forked from [frontend-slides](https://github.com/zarazhangrui/frontend-slides) by [@zarazhangrui](https://github.com/zarazhangrui) (Zara Zhang).
> Enhanced by [@hanlinlibham](https://github.com/hanlinlibham) with financial chart integration and offline optimizations.

A Claude Code skill for creating animation-rich HTML presentations from any content — with first-class support for financial data visualization.

## What This Does

**Fund Slides** helps non-designers create beautiful web presentations without knowing CSS or JavaScript. It uses a "show, don't tell" approach: instead of asking you to describe your aesthetic preferences in words, it generates visual previews and lets you pick what you like.

Here is a deck about the original skill, made through the skill:

https://github.com/user-attachments/assets/ef57333e-f879-432a-afb9-180388982478

### Key Features

- **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no build tools, no frameworks.
- **Offline-Ready** — ECharts library (~1MB) is inlined directly into the HTML. No CDN, no network required.
- **Visual Style Discovery** — Can't articulate design preferences? No problem. Pick from generated visual previews.
- **PPT Conversion** — Convert existing PowerPoint files to web, preserving all images and content.
- **Anti-AI-Slop** — Curated distinctive styles that avoid generic AI aesthetics.
- **Production Quality** — Accessible, responsive, well-commented code you can customize.

### What's New in This Fork

Compared to the original `frontend-slides`:

- **ECharts Inline Integration** — ECharts v5 library pre-bundled in `references/echarts.min.js`, inlined at generation time for fully offline HTML output. The original used CDN `<script src="...">` which requires network access.
- **Financial Chart Library** — Added specialized chart references for financial use cases:
  - `charts-trend.md` — Line/area/bar charts for time series
  - `charts-composition.md` — Pie/rose/treemap/sunburst for composition analysis
  - `charts-matrix.md` — Heatmap/radar/scatter for multi-dimensional comparison
  - `charts-flow.md` — Waterfall/candlestick/funnel/sankey for flow analysis
- **A-Share Color Convention** — Red-up/green-down (China stock market standard) built into the base template
- **Financial Layouts** — KPI cards, data tables, timelines, comparison cards optimized for investment presentations
- **Content Mapping System** — Intelligent content-to-visual mapping that automatically selects optimal chart types based on data characteristics
- **Safe Base Template** — Defensive HTML template with built-in viewport fitting, CJK typography, responsive breakpoints, and Chinese number formatting (`formatCN`)
- **15 Visual Presets** — Expanded from 12 to 15 curated styles including `Research Formal`, `Data Dashboard`, and `Roadshow Elegance`
- **Self-Check Checklist** — Phase 3.5 automated quality gate ensuring zero external dependencies, proper `clamp()` usage, and A-share color compliance

## Installation

```bash
git clone https://github.com/hanlinlibham/skills.git ~/.claude/skills
```

Then use it by typing `/fund-slides` in Claude Code.

## Usage

### Create a New Presentation

```
/fund-slides

> "Create a fund analysis presentation for XX Fund"
```

The skill will:
1. Ask about your content, length, chart needs, and editing preference
2. Analyze content and map each block to optimal visual form
3. Generate 3 visual style previews for you to compare
4. Create the full presentation with charts inlined
5. Open it in your browser — works offline

### Convert a PowerPoint

```
/fund-slides

> "Convert my presentation.pptx to a web slideshow"
```

## Included Styles

### Dark Themes
- **Bold Signal** — Confident, high-impact, vibrant card on dark
- **Electric Studio** — Clean, professional, split-panel
- **Creative Voltage** — Energetic, retro-modern, electric blue + neon
- **Dark Botanical** — Elegant, sophisticated, warm accents

### Light Themes
- **Notebook Tabs** — Editorial, organized, paper with colorful tabs
- **Pastel Geometry** — Friendly, approachable, vertical pills
- **Split Pastel** — Playful, modern, two-color vertical split
- **Vintage Editorial** — Witty, personality-driven, geometric shapes

### Financial / Specialty
- **Research Formal** — Institutional, trustworthy, data-heavy layouts
- **Data Dashboard** — Clean metrics, KPI cards, chart-forward
- **Roadshow Elegance** — Premium, investor-facing, bold confidence
- **Swiss Modern** — Minimal, Bauhaus-inspired, geometric
- **Paper & Ink** — Literary, drop caps, pull quotes
- **Neon Cyber** — Futuristic, particle backgrounds, neon glow
- **Terminal Green** — Developer-focused, hacker aesthetic

## Architecture

| File | Purpose | Loaded When |
|------|---------|-------------|
| `SKILL.md` | Core workflow and rules | Always (skill invocation) |
| `content-mapping.md` | Content type to visual form mapping | Phase 1 (content analysis) |
| `STYLE_PRESETS.md` | 15 curated visual presets | Phase 2 (style selection) |
| `references/safe-base-template.html` | Defensive base HTML template | Phase 3 (generation) |
| `references/echarts.min.js` | ECharts v5 library (~1MB) | Phase 3 (inline into HTML) |
| `references/charts-*.md` | Chart type configurations | Phase 3 (per chart type) |
| `references/financial-layouts.md` | KPI/table/timeline layouts | Phase 3 (financial slides) |
| `references/animation-patterns.md` | CSS/JS animation reference | Phase 3 (generation) |
| `references/html-template.md` | HTML structure and JS features | Phase 3 (generation) |
| `scripts/extract-pptx.py` | PPT content extraction | Phase 4 (conversion) |

## Credits

- **Original author**: [Zara Zhang](https://github.com/zarazhangrui) — created [frontend-slides](https://github.com/zarazhangrui/frontend-slides) with Claude Code
- **Fork maintainer**: [hanlinlibham](https://github.com/hanlinlibham) — financial chart integration, offline ECharts inlining, A-share conventions, and expanded presets

## License

MIT — See [LICENSE](LICENSE) for details.
