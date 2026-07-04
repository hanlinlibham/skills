# HLB_ 页面布局

## 导航栏

### 首页导航

```html
<nav>
  <div class="nav-brand">HLB_</div>
  <div class="nav-links">
    <a href="#about">ABOUT</a>
    <a href="#products">PRODUCTS</a>
    <a href="#work">WORK</a>
    <a href="https://github.com/hanlinlibham">GITHUB ↗</a>
  </div>
</nav>
```

### 子页面导航（面包屑）

```html
<nav>
  <div class="nav-breadcrumb">
    <a href="/">HLB_</a>
    <span>/</span>
    <span>ABLEMIND</span>
  </div>
  <div class="nav-links">
    <a href="#positioning">POSITIONING</a>
    <a href="#agents">AGENTS</a>
    <a href="#protocol">PROTOCOL</a>
    <a href="#capabilities">FEATURES</a>
    <a href="#stack">STACK</a>
    <a href="/">HOME ↗</a>
  </div>
</nav>
```

### 导航样式

```css
nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 57px;
  background: var(--bg-nav);
  backdrop-filter: blur(12px);
}

.nav-brand {
  font-weight: 800;
  font-size: 18px;
  color: var(--accent);
  letter-spacing: 0.05em;
}

.nav-breadcrumb span {
  color: var(--text-muted);
  margin: 0 8px;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  font-size: 16.8px;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  text-decoration: none;
  text-transform: uppercase;
}
```

## Hero 区

### 首页 Hero

```
┌──────────────────────────────────────────┐
│ <developer />                            │  ← badge 小标签
│                                          │
│ HANLIN                    ┌─────────────┐│
│ LI        (em=accent)    │ ░░░░░░░░░░░ ││  ← 右侧装饰方块
│ BHAM                     │ ░░░░░░░░░░░ ││
│                          │ ░░░ accent ░ ││
│ Independent developer... ├─────────────┤│
│                          │ 10   2026   ││  ← 统计数字
│ [VIEW WORK] [GITHUB ↗]   │ REPOS ACTIVE ││
│                          └─────────────┘│
│ SCROLL ────────                          │
└──────────────────────────────────────────┘
```

### 子页面 Hero

```
┌──────────────────────────────────────────────────┐
│ [MULTI-AGENT PLATFORM]      ← badge              │
│                                                   │
│ ABLE                        ┌──────────────────┐ │
│ MIND  (em=accent)           │ System Metrics   │ │
│                             │ 21+ MCP Tools    │ │
│ 面向金融分析的多智能体...     │ 14 Agents       │ │
│                             │ 3 Gateways       │ │
│ [tag] [tag] [tag] [tag]     │                  │ │
│                             │ Agent Cluster    │ │
│                             │ • Conductor      │ │
│                             │ • Crunch ...     │ │
│                             └──────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Hero 样式

```css
.hero {
  padding: 120px 57px 80px;
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.hero-content {
  max-width: 60%;
}

.hero-sidebar {
  max-width: 35%;
}
```

## 内容分区

每个分区以编号标识，结构统一：

```
┌──────────────────────────────────────────┐
│ 01                                       │
│ SECTION TITLE                            │
│──────────────────────────────────────────│
│                                          │
│ 描述段落...                               │
│                                          │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│ │ Card 1  │ │ Card 2  │ │ Card 3  │     │
│ └─────────┘ └─────────┘ └─────────┘     │
│                                          │
└──────────────────────────────────────────┘
```

```css
.section {
  padding: 120px 57px;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 24px;
  margin-bottom: 48px;
}

.section-number {
  font-size: 64px;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}

.section-title {
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
}
```

### 分区之间的分隔

分区间不使用显式分隔线，而是通过大量垂直空白（120px padding）和背景微调实现视觉分隔。偶尔使用 `border-top: 1px solid var(--border)` 作为弱分隔。

## 网格系统

```css
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }

/* 响应式：小屏单列 */
@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
}
```

## Footer

```html
<footer>
  <div class="footer-left">
    © 2026 <a href="/">HLB_</a> / PAGENAME
  </div>
  <div class="footer-right">
    <a href="/">HOME</a>
    <a href="/ableflow/">ABLEFLOW</a>
    <a href="https://github.com/hanlinlibham">GITHUB</a>
  </div>
</footer>
```

```css
footer {
  padding: 32px 57px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
}

footer a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.footer-right {
  display: flex;
  gap: 24px;
}
```

## 关键间距汇总

| 位置 | 值 |
|------|-----|
| 页面水平 padding | 57px |
| 分区垂直 padding | 120px |
| 卡片内 padding | 28px |
| 卡片间 gap | 24px |
| 导航链接间 gap | 32px |
| 标签间 gap | 8~12px |
| 段落间 margin | 16~24px |
