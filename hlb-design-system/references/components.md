# HLB_ 组件样式

## 按钮

### 主按钮 (Primary CTA)

```css
.btn-primary {
  background: var(--accent);
  color: var(--bg);
  padding: 14px 32px;
  border: none;
  border-radius: 0;
  font-family: var(--font-mono);
  font-size: 16.8px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}
```

### 次按钮 (Secondary / Ghost)

```css
.btn-secondary {
  background: transparent;
  color: var(--text-secondary);
  padding: 14px 32px;
  border: 1px solid var(--border);
  border-radius: 0;
  font-family: var(--font-mono);
  font-size: 16.8px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}
```

### 按钮组合规则

- 主 + 次并排，主在左
- 外链按钮文字后加 `↗` 符号
- 按钮间距 12~16px

## 标签 (Tags)

### 技术标签

用于展示技术栈、特性关键词。

```css
.tag {
  display: inline-block;
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 0;
  color: var(--text-muted);
  font-size: 14px;
  font-family: var(--font-mono);
}
```

### 页面类型标签 (Badge)

用于 Hero 区顶部标识产品类型（如 "MULTI-AGENT PLATFORM"）。

```css
.badge {
  display: inline-block;
  padding: 6px 14px;
  background: var(--accent-10);
  border: 1px solid var(--accent-25);
  border-radius: 0;
  color: var(--accent);
  font-size: 14px;
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
}
```

### 产品卡片内的状态标签

```css
.tag-status {
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--accent);
  text-transform: uppercase;
}
```

## 表格

```css
table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-mono);
}

th {
  text-align: left;
  padding: 12px 18px;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 12px 18px;
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(58, 54, 62, 0.3);
}

td strong {
  color: var(--text-primary);
}

td code {
  color: var(--text-primary);
  background: var(--surface-1);
  padding: 2px 6px;
}
```

## 统计数字卡片

大号数字 + 小号标签的组合，用于展示关键指标。

```html
<div class="stat">
  <span class="stat-value">21+</span>
  <span class="stat-label">MCP Tools</span>
</div>
```

```css
.stat-value {
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

## 流程图 (Pipeline Flow)

用文字方块 + 箭头的线性水平排列。

```html
<div class="flow">
  <span class="flow-node">USER</span>
  <span class="flow-arrow">→</span>
  <span class="flow-node">CONDUCTOR</span>
  <span class="flow-arrow">→</span>
  <span class="flow-node">PIPELINE</span>
  <span class="flow-arrow">→</span>
  <span class="flow-node">SSE</span>
</div>
```

```css
.flow {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 20px 0;
}

.flow-node {
  padding: 8px 16px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.flow-arrow {
  color: var(--text-muted);
  font-size: 18px;
}
```

## 编号功能卡片

三列或四列网格，每张卡片带编号。

```html
<div class="feature-card">
  <span class="feature-num">01</span>
  <h4 class="feature-title">深度推理</h4>
  <p class="feature-desc">本地 LangGraph Agent 编排多步骤推理链。</p>
</div>
```

```css
.feature-card {
  padding: 28px;
  background: var(--surface-1);
  border: 1px solid var(--border);
}

.feature-num {
  font-size: 14px;
  color: var(--accent);
  font-weight: 700;
  letter-spacing: 0.1em;
}

.feature-title {
  margin-top: 16px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-desc {
  margin-top: 8px;
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.6;
}
```

## 产品链接卡片

首页 PRODUCTS 区的链接卡片样式。

```css
.product-card {
  display: block;
  padding: 28px;
  background: var(--surface-1);
  border: 1px solid var(--border);
  text-decoration: none;
  transition: border-color 0.2s;
}

.product-card:hover {
  border-color: var(--accent);
}
```

## 三列架构卡片

用于展示分层架构（如 CONTROL / RUNTIME / DATA）。

```css
.arch-card {
  padding: 28px;
  background: var(--surface-1);
  border: 1px solid var(--border);
}

.arch-card-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--accent);
  text-transform: uppercase;
}

.arch-card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 4px;
}

.arch-card ul {
  list-style: none;
  padding: 0;
  margin-top: 16px;
}

.arch-card li {
  padding: 6px 0;
  color: var(--text-secondary);
  font-size: 14px;
  border-bottom: 1px solid rgba(58, 54, 62, 0.2);
}
```

## 返回顶部按钮

子页面底部固定按钮。

```css
.back-to-top {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 0;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

## Roadmap 时间线卡片

三阶段并列展示。

```css
.roadmap-card {
  padding: 28px;
  background: var(--surface-1);
  border: 1px solid var(--border);
}

.roadmap-phase {
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--accent);
  text-transform: uppercase;
}

.roadmap-card h3 {
  margin-top: 8px;
  font-size: 20px;
}

.roadmap-card ul {
  margin-top: 16px;
  padding-left: 0;
  list-style: none;
}

.roadmap-card li {
  padding: 4px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.roadmap-card li::before {
  content: "□ ";
  color: var(--text-muted);
}
```
