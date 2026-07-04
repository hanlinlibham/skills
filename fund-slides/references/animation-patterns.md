# Animation Patterns Reference

Use this reference when generating presentations. Match animations to the intended feeling.

## Effect-to-Feeling Guide

| Feeling | Animations | Visual Cues |
|---------|-----------|-------------|
| **Dramatic / Cinematic** | Slow fade-ins (1-1.5s), large scale transitions (0.9 to 1), parallax scrolling | Dark backgrounds, spotlight effects, full-bleed images |
| **Techy / Futuristic** | Neon glow (box-shadow), glitch/scramble text, grid reveals | Particle systems (canvas), grid patterns, monospace accents, cyan/magenta/electric blue |
| **Playful / Friendly** | Bouncy easing (spring physics), floating/bobbing | Rounded corners, pastel/bright colors, hand-drawn elements |
| **Professional / Corporate** | Subtle fast animations (200-300ms), clean slides | Navy/slate/charcoal, precise spacing, data visualization focus |
| **Calm / Minimal** | Very slow subtle motion, gentle fades | High whitespace, muted palette, serif typography, generous padding |
| **Editorial / Magazine** | Staggered text reveals, image-text interplay | Strong type hierarchy, pull quotes, grid-breaking layouts, serif headlines + sans body |

## Entrance Animations

```css
/* Fade + Slide Up (most versatile) */
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s var(--ease-out-expo),
                transform 0.6s var(--ease-out-expo);
}
.visible .reveal {
    opacity: 1;
    transform: translateY(0);
}

/* Scale In */
.reveal-scale {
    opacity: 0;
    transform: scale(0.9);
    transition: opacity 0.6s, transform 0.6s var(--ease-out-expo);
}

/* Slide from Left */
.reveal-left {
    opacity: 0;
    transform: translateX(-50px);
    transition: opacity 0.6s, transform 0.6s var(--ease-out-expo);
}

/* Blur In */
.reveal-blur {
    opacity: 0;
    filter: blur(10px);
    transition: opacity 0.8s, filter 0.8s var(--ease-out-expo);
}
```

## Background Effects

```css
/* Gradient Mesh — layered radial gradients for depth */
.gradient-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
        var(--bg-primary);
}

/* Noise Texture — inline SVG for grain */
.noise-bg {
    background-image: url("data:image/svg+xml,..."); /* Inline SVG noise */
}

/* Grid Pattern — subtle structural lines */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

## Interactive Effects

```javascript
/* 3D Tilt on Hover — adds depth to cards/panels */
class TiltEffect {
    constructor(element) {
        this.element = element;
        this.element.style.transformStyle = 'preserve-3d';
        this.element.style.perspective = '1000px';

        this.element.addEventListener('mousemove', (e) => {
            const rect = this.element.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            this.element.style.transform = `rotateY(${x * 10}deg) rotateX(${-y * 10}deg)`;
        });

        this.element.addEventListener('mouseleave', () => {
            this.element.style.transform = 'rotateY(0) rotateX(0)';
        });
    }
}
```

## Financial Data Animations

金融演示专用动画效果。数据展示优先清晰和准确，动画起辅助作用。

### KPI 数字滚动

```javascript
/* 数字从 0 滚动到目标值，配合 formatCN 格式化 */
class CountUp {
    constructor(el, target, duration = 1200) {
        this.el = el;
        this.target = target;
        this.duration = duration;
    }
    start() {
        const t0 = performance.now();
        const tick = (now) => {
            const p = Math.min((now - t0) / this.duration, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            this.el.textContent = typeof formatCN === 'function'
                ? formatCN(this.target * eased)
                : Math.round(this.target * eased).toLocaleString();
            if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }
}
```

### 表格逐行显现

```css
.data-table tbody tr {
    opacity: 0;
    transform: translateY(10px);
    transition: opacity 0.4s var(--ease-out-expo),
                transform 0.4s var(--ease-out-expo);
}
.slide.visible .data-table tbody tr { opacity: 1; transform: none; }
.slide.visible .data-table tbody tr:nth-child(1) { transition-delay: 0.1s; }
.slide.visible .data-table tbody tr:nth-child(2) { transition-delay: 0.15s; }
.slide.visible .data-table tbody tr:nth-child(3) { transition-delay: 0.2s; }
.slide.visible .data-table tbody tr:nth-child(4) { transition-delay: 0.25s; }
.slide.visible .data-table tbody tr:nth-child(5) { transition-delay: 0.3s; }
.slide.visible .data-table tbody tr:nth-child(6) { transition-delay: 0.35s; }
```

### KPI 卡片依次进入

```css
.kpi-grid .kpi-card {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s var(--ease-out-expo),
                transform 0.5s var(--ease-out-expo);
}
.slide.visible .kpi-grid .kpi-card { opacity: 1; transform: none; }
.slide.visible .kpi-grid .kpi-card:nth-child(1) { transition-delay: 0.1s; }
.slide.visible .kpi-grid .kpi-card:nth-child(2) { transition-delay: 0.2s; }
.slide.visible .kpi-grid .kpi-card:nth-child(3) { transition-delay: 0.3s; }
.slide.visible .kpi-grid .kpi-card:nth-child(4) { transition-delay: 0.4s; }
```

### 图表容器淡入

```css
.chart-container {
    opacity: 0;
    transition: opacity 0.8s ease;
}
.slide.visible .chart-container {
    opacity: 1;
}
```

### 趋势指标闪烁强调

```css
@keyframes highlight-pulse {
    0%, 100% { background-color: transparent; }
    50% { background-color: rgba(var(--accent-rgb, 37, 99, 235), 0.1); }
}
.kpi-trend.positive, .kpi-trend.negative {
    animation: highlight-pulse 2s ease 1;
    animation-delay: 1.5s;
    border-radius: 2px;
    padding: 0 0.2em;
}
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Fonts not loading | Check Fontshare/Google Fonts URL; ensure font names match in CSS |
| Chinese fonts slow | Noto Sans/Serif SC are 2-4MB; use `display=swap` and subset `&subset=chinese-simplified` |
| Animations not triggering | Verify Intersection Observer is running; check `.visible` class is being added |
| Scroll snap not working | Ensure `scroll-snap-type: y mandatory` on html; each slide needs `scroll-snap-align: start` |
| ECharts not rendering | Charts must init after slide is visible (container needs non-zero dimensions) |
| Mobile issues | Disable heavy effects at 768px breakpoint; test touch events; reduce particle count |
| Performance issues | Use `will-change` sparingly; prefer `transform`/`opacity` animations; throttle scroll handlers |
