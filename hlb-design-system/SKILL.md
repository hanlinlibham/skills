---
name: hlb-design-system
description: >
  HLB_ 品牌前端设计系统 — 暗黑开发者美学风格。用于构建 lihanlin.com 及其衍生页面
  (AbleMind, AbleFlow, AbleClaw 等) 的前端 UI。当需要为 HLB_ 品牌创建新页面、
  组件、产品展示页，或需要遵循 lihanlin.com 设计语言时使用此 skill。
  触发词：HLB 设计、lihanlin 风格、暗黑开发者风格、产品页设计、HLB 品牌页面、
  AbleMind 风格、AbleFlow 风格、开发者主页风格。
---

# HLB_ Design System

暗黑 + Monospace + 锐角矩形 + 每产品独立主题色。

## 核心规则

1. **全站 monospace** — `"JetBrains Mono", "SF Mono", "Fira Code", monospace`
2. **零圆角** — 所有元素 `border-radius: 0`，包括按钮、标签、卡片、输入框
3. **近纯黑背景** — `#0A0A0A` 基底，不使用纯黑 `#000`
4. **每个产品/页面一个主题色** — 通过 CSS 变量 `--accent` 切换

## 参考文件

- **色彩体系**: 见 [references/colors.md](references/colors.md) — 完整调色板、产品主题色、surface 色
- **排版规范**: 见 [references/typography.md](references/typography.md) — 字号、字重、字间距
- **组件样式**: 见 [references/components.md](references/components.md) — 按钮、标签、表格、卡片、流程图
- **页面布局**: 见 [references/layout.md](references/layout.md) — 导航、分区、Hero、Footer 结构
- **仪表盘**: 见 [references/dashboard.md](references/dashboard.md) — Air Vault 主页门户（**浅色变体**）：Hero 三段式 + 信息流编号分区 + DataviewJS 活指标/健康度逻辑 + masonry 列排布

## 新页面 Checklist

1. 确定产品主题色 → 设置 `--accent` 和 `--accent-10` (10% 透明度)
2. 根据主题色微调 surface 色相（偏暖/偏紫/偏蓝）
3. 使用编号分区 (01, 02, 03...) 组织内容
4. Hero 区：超大标题 + `<em>` 主题色强调 + 标签行 + CTA 按钮
5. 导航：面包屑 `HLB_ / PAGENAME` + 锚点链接
6. Footer: `© 2026 HLB_ / PAGENAME` + 外链

## CSS 变量模板

```css
:root {
  --bg: #0A0A0A;
  --bg-nav: rgba(10, 10, 10, 0.88);
  --text-primary: #F0F0F0;
  --text-secondary: #B0B0B8;
  --text-muted: #858088;
  --text-subtle: #3A363E;
  --border: #3A363E;
  --accent: #FF5C00;
  --accent-10: rgba(255, 92, 0, 0.1);
  --accent-25: rgba(255, 92, 0, 0.25);
  --surface-1: #141414;
  --surface-2: #1E1E1E;
  --font-mono: "JetBrains Mono", "SF Mono", "Fira Code", monospace;
}
```

### 已知产品主题色

| 产品 | --accent | --surface-1 | --surface-2 | 色相倾向 |
|------|----------|-------------|-------------|----------|
| Homepage | `#FF5C00` (橙) | `#141414` | `#1E1E1E` | 中性 |
| AbleMind | `#FF4757` (红粉) | `#131114` | `#1E1C20` | 偏紫 |
| AbleFlow | `#00C8FF` (青蓝) | `#111318` | `#1C1E24` | 偏蓝 |
| Air Vault Dashboard | `#FF5C00` (橙) | `#FFFFFF` | `#FBFAF5` | 浅色 v1 遗留（已部署实例），新页面不再采用，见 dashboard.md |

> **浅色变体（标准 v2 · 2026-07-04）**：HLB_ 语言（等宽 / 零圆角 / 编号分区 / 大写标签）不变，
> 色板统一换用 ablemind gov-review 快照：bg `#F8F6F2`（`hsl(40 27% 96%)` 暖米白）、
> surface-1 `#FFFFFF`、text `#1D2330`、border `#D3C9BB`，默认 accent 政务深蓝 `#22456D`，
> 语义色成对（fg + 浅底）。完整 token 表见 [references/colors.md](references/colors.md) 「浅色模式」节；
> 权威源链：ablework `globals.css` → `yangnan/ablethree/UI_SPEC.md` → colors.md 快照。
