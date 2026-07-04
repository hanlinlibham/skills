# HLB_ 排版规范

## 字体栈

```css
font-family: "JetBrains Mono", "SF Mono", "Fira Code", monospace;
```

全站统一使用 monospace 字体，不使用 sans-serif 或 serif。

## 字号与字重层级

### H1 — 页面主标题

```css
h1 {
  font-size: clamp(72px, 10vw, 157px); /* 响应式缩放 */
  font-weight: 800;
  letter-spacing: -0.04em;             /* 紧缩字距，约 -5.7px at 143px */
  line-height: 0.92;                   /* 紧凑行高 */
  color: var(--text-primary);
  text-transform: uppercase;
}

h1 em {
  font-style: italic;
  color: var(--accent);                /* 主题色强调 */
}
```

- 首页 H1 约 143px，子页面 H1 约 157px
- `<em>` 标签渲染为主题色斜体，用于品牌名称中的一个词

### H2 — 分区标题

```css
h2 {
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 700;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  color: var(--text-primary);
}
```

### H3 — 子区块标题

```css
h3 {
  font-size: clamp(20px, 2.5vw, 28px);
  font-weight: 600;
  color: var(--text-primary);
}
```

### H4 — 卡片/功能标题

```css
h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
```

### 正文

```css
body {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
}

p {
  color: var(--text-secondary);        /* 段落用 secondary 色 */
}
```

### 导航文字

```css
nav a {
  font-size: 16.8px;
  letter-spacing: 0.1em;              /* 1.68px 宽松字距 */
  text-transform: uppercase;
  color: var(--text-muted);
  text-decoration: none;
}
```

### 分区编号

```css
.section-number {
  font-size: clamp(48px, 6vw, 80px);
  font-weight: 800;
  color: var(--accent);               /* 或 var(--text-subtle) 弱化 */
  letter-spacing: -0.02em;
}
```

### 代码/内联代码

```css
code {
  font-family: inherit;               /* 已是 monospace */
  font-size: 0.9em;
  color: var(--text-primary);
  background: var(--surface-1);
  padding: 2px 6px;
}
```

## 文字大写规则

| 元素 | 规则 |
|------|------|
| H1, H2 | `text-transform: uppercase` |
| 导航链接 | `text-transform: uppercase` + 宽松字距 |
| 按钮文字 | `text-transform: uppercase` + 宽松字距 |
| 标签 (tag) | 原始大小写 (技术名称保留原样) |
| 正文 | 正常句式 |
| 分区标签 | `text-transform: uppercase` |
