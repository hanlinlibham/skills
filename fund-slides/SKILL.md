---
name: fund-slides
description: Create animation-rich HTML presentations from any content. Provides intelligent content-to-visual mapping -- given information of any type, selects the optimal slide layout, chart, and animation. Zero-dependency single HTML files with Chinese font support and ECharts inline integration. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides.
---

# Frontend Slides

将任意内容转化为零依赖、动画丰富的 HTML 演示文稿。

本技能不关心内容从哪来、用什么分析框架 -- 它只做一件事：**给定一块信息，选择最佳的视觉呈现方式。**

## Core Principles

1. **Content-Agnostic** -- 技能不决定"展示什么"，只决定"怎么展示"。研究逻辑由用户或上游技能负责。
2. **Zero Dependencies** -- 单 HTML 文件，CSS/JS 全部内联。需要图表时，ECharts 库直接内嵌在 HTML 的 `<script>` 标签中（通过 WebFetch 下载 echarts.min.js 后内联），确保离线可用。
3. **Show, Don't Tell** -- 生成可视化预览让用户选择风格，而非要求用户用语言描述偏好。
4. **Viewport Fitting (NON-NEGOTIABLE)** -- 每张 slide 精确适配 100vh。禁止滚动。内容超限时拆分。
5. **No Emoji** -- 禁止任何 emoji。用 CSS 形状、SVG 图标或文字替代。
6. **Chinese Font Required** -- 每份演示文稿必须包含中文字体回退链。

## Design Aesthetics

杜绝"AI 味"。每份演示文稿都应有定制感。

- 字体：选择有辨识度的字体，避免 Arial/Inter/Roboto。所有字号用 `clamp()`。
- 配色：主色 + 锐利强调色，避免均匀分布。CSS 变量保持一致。
- 动画：聚焦高影响力时刻 -- 入场交错显现优于零散微交互。
- 背景：渐变/图案/纹理营造层次，而非纯色。

## Viewport Fitting Rules

适用于每张 slide 的不变量：

- `.slide`: `height: 100vh; height: 100dvh; overflow: hidden;`
- 所有字号: `clamp(min, preferred, max)` -- 禁止固定 px/rem
- 所有间距: `clamp()` 或视口单位
- 图片: `max-height: min(50vh, 400px)`
- 断点: 700px, 600px, 500px (height), 600px (width)
- `prefers-reduced-motion` 支持
- CSS 函数取反用 `calc(-1 * clamp(...))` -- 禁止 `-clamp()`

---

## Phase 0: Detect Mode

- **Mode A: 新建** -- 用户提供内容（文本/数据/图片），从零创建。进入 Phase 1。
- **Mode B: PPT 转换** -- 转换 .pptx 文件。进入 Phase 4。
- **Mode C: 增强** -- 改进现有 HTML 演示文稿。遵循 Mode C 规则。

### Mode C: 修改规则

1. 添加内容前统计现有元素，对照密度限制
2. 任何修改后验证: `overflow: hidden`、`clamp()` 字号、图片 max-height
3. 将要溢出时主动拆分并告知用户

---

## Phase 1: Content Discovery

**目标：理解用户有什么内容，而非告诉用户应该有什么内容。**

通过一次 AskUserQuestion 收集信息：

**问题 1 -- 内容来源** (header: "内容"):
你的内容是什么形式？选项：
- "内容已就绪" -- 有完整的文字/数据/图表素材
- "有粗略笔记" -- 有要点但未整理
- "仅有主题" -- 只有主题，需要协助组织结构

**问题 2 -- 长度** (header: "长度"):
大约多少页？选项：简短 5-10 / 中等 10-20 / 较长 20+

**问题 3 -- 图表需求** (header: "图表"):
是否需要数据图表？选项：
- "ECharts (推荐)" -- 折线/柱状/饼图/K线/瀑布图，内嵌到 HTML 中，离线可用
- "简单 SVG" -- 更轻量，适合简单图表
- "不需要"

**问题 4 -- 在线编辑** (header: "编辑"):
是否需要浏览器内编辑文字？选项：是（推荐） / 否

然后请用户提供内容。

### Step 1.2: Content Analysis

**用户提供内容后，读取 [content-mapping.md](content-mapping.md) 进行内容分析：**

1. **识别** -- 将用户内容拆解为独立信息块
2. **分类** -- 对每块内容标注信息类型（数值指标 / 时序趋势 / 结构构成 / 对比关系 / 叙事论点 / 时间序列 / 风险评估）
3. **映射** -- 为每块内容匹配最佳视觉形式（KPI卡片 / 图表 / 表格 / 分栏 / 列表 / 时间线 / 对比卡片）
4. **排序** -- 组织 slide 顺序（概览 -> 核心内容 -> 结论）
5. **呈现给用户确认** -- 展示映射结果表格

示例输出：

```
Slide 大纲:
| # | 内容 | 信息类型 | 视觉形式 |
|---|------|---------|---------|
| 1 | 标题与主题 | -- | 标题页 |
| 2 | 6 个核心财务指标 | 少量关键指标 | KPI 卡片网格 |
| 3 | 2019-2024 营收趋势 | 时间序列 | 柱线混合图 |
| 4 | 收入构成 + 解读 | 构成 + 论点 | 图文分栏 (饼图+要点) |
| 5 | 三条核心优势 | 论点+支撑 | 标题+要点列表 |
| ... | ... | ... | ... |
```

通过 AskUserQuestion 确认 (header: "大纲"): "这个 slide 大纲是否合适？" 选项：合适 / 调整

### Step 1.4: 状态暂存（防止跨 Phase 遗忘）

确认大纲后，**必须**将分析结果写入 `.slide-plan.md`，格式如下：

```markdown
# Slide Plan
- 预设: [所选预设名称]
- 图表方案: [ECharts / SVG / 无]
- 编辑模式: [是 / 否]
- 需读取的 references: [列出 Phase 3 需要的文件]

| # | 内容摘要 | 类型 | 视觉形式 | 需要的 CSS class |
|---|---------|------|---------|----------------|
| 1 | ... | ... | ... | ... |
```

Phase 3 生成前**必须先读取此文件**，确保不会遗忘 Phase 1 的分析结果。

### Step 1.3: Image Evaluation (如有)

如果用户提供了图片：扫描 -> 查看 -> 评估可用性 -> 融入大纲。

---

## Phase 2: Style Discovery

**"看效果选风格"环节。**

### Step 2.0: 风格路径

询问 (header: "风格"):
- "给我看几个选项"（推荐）-- 基于感受生成 3 个预览
- "我知道我想要什么" -- 直接从预设列表选择

### Step 2.1: 感受选择

询问 (header: "感受", multiSelect: true, max 2):
- 专业/可信 -- 机构感、值得信赖
- 自信/有力 -- 创新、大胆
- 沉稳/专注 -- 清晰、深思熟虑
- 高端/精致 -- 优雅、令人难忘

### Step 2.2: 生成 3 个风格预览

读取 [STYLE_PRESETS.md](STYLE_PRESETS.md) 获取 15 个可用预设。根据感受从中选择 3 个差异化预设生成单页预览。

| 感受 | 建议预设（按适配度排序） |
|------|------------------------|
| 专业/可信 | Research Formal, Swiss Modern, Notebook Tabs, Data Dashboard |
| 自信/有力 | Roadshow Elegance, Bold Signal, Electric Studio |
| 沉稳/专注 | Paper & Ink, Data Dashboard, Swiss Modern |
| 高端/精致 | Roadshow Elegance, Dark Botanical, Vintage Editorial |

保存预览到 `.claude-design/slide-previews/`，自动打开。

### Step 2.3: 用户选择

询问 (header: "风格选择"): 哪个风格？选项：A / B / C / 混合

---

## Phase 3: Generate Presentation

### Step 3.0: 读取状态 + 防护模板

1. **读取 `.slide-plan.md`** -- 恢复 Phase 1 的分析结果（类型、视觉形式、需要的文件）
2. **复制 [references/safe-base-template.html](references/safe-base-template.html) 作为起点** -- 此模板已内置 viewport-base.css、中文字体、A 股配色、formatCN、SlidePresentation 控制器。在此基础上添加内容，**不要删除模板中的任何 CSS 变量或 JS 函数**。

### Step 3.1: 按需读取参考文件

根据 `.slide-plan.md` 中列出的 references 读取：

1. **[STYLE_PRESETS.md](STYLE_PRESETS.md)** -- 获取所选风格的配色、字体、签名元素，覆盖模板中的 SLOT: THEME 变量
2. **(按需)** [references/charts-base.md](references/charts-base.md) + 对应的 charts-trend/composition/matrix/flow -- 按 `.slide-plan.md` 列出的图表类型读取
3. **(按需)** [references/financial-layouts.md](references/financial-layouts.md) -- 如有 KPI/表格/时间线/对比等布局
4. **(按需)** [references/animation-patterns.md](references/animation-patterns.md) -- 高级动画效果
5. **(按需)** [references/html-template.md](references/html-template.md) -- 编辑功能等 JS 参考

### Step 3.1.5: ECharts 内联（如需图表）

如果 `.slide-plan.md` 中图表方案为 ECharts，**必须**将 ECharts 库内嵌到 HTML 中：

1. 读取本地文件 [references/echarts.min.js](references/echarts.min.js)（~1MB，已预存在 skill 目录中）
2. 将完整内容包裹在 `<script>/* ECharts v5 */...内容...</script>` 中
3. 放入模板的 `<!-- SLOT: ECHARTS INLINE -->` 位置
4. **禁止使用 `<script src="...">` 外部引用** -- 最终 HTML 必须离线可用

### Step 3.2: 生成 slide 内容

在 safe-base-template.html 的 `<!-- SLOT: SLIDES -->` 位置添加 slide。每张 slide 的视觉形式严格按 `.slide-plan.md` 执行。

**slide 结构由 Phase 1 的 content-mapping 结果驱动，而非固定模板。每份演示文稿的页面组合都应该不同。**

---

## Phase 3.5: 代码完整性自检（生成后必须执行）

输出最终 HTML 前，逐项检查以下清单。任何一项失败，修复后再继续。

- [ ] `<html lang="zh-CN">` 已设置
- [ ] safe-base-template 的核心 CSS 完整保留（搜索 `scroll-snap-type` 确认存在）
- [ ] 所有 `font-size:` 使用 `clamp()`（搜索 `font-size:`，确认无固定 px/rem 值）
- [ ] `formatCN` 函数已内嵌（如有数字数据）
- [ ] 无 emoji 字符（涨跌用 `.trend-up` / `.trend-down` CSS 类）
- [ ] 每个 `.slide` 继承了 `overflow: hidden`（来自 safe-base-template）
- [ ] 中文字体已加载（Google Fonts link 包含 `Noto+Sans+SC` 或 `Noto+Serif+SC`）
- [ ] `--color-positive: #dc2626` 和 `--color-negative: #16a34a` 存在（A 股默认）
- [ ] **零外部依赖**：无 `<script src="...">` 外部引用（如有 ECharts，确认是内联 `<script>` 而非 CDN）

**如有任何项失败，修复后再继续。不要跳过自检。**

---

## Phase 4: PPT Conversion

1. 运行 `python scripts/extract-pptx.py <input.pptx> <output_dir>`
2. 展示提取结果，与用户确认
3. 进入 Phase 2 选择风格
4. 生成 HTML，保留原始内容和图片

---

## Phase 5: Delivery

1. 删除 `.claude-design/slide-previews/`
2. `open [filename].html`
3. 告知：文件位置、风格、页数、导航方式、自定义方法
4. **如需通过飞书发送给用户**，使用 message 工具：

```javascript
message({
  action: "send",
  channel: "feishu",
  path: "/home/core/.openclaw/workspace/output/presentation.html",
  filename: "presentation.html",
  caption: "基金分析演示文稿"
})
```

---

## Fallback: 降级模式

当内容超过 15 页、或包含 3 种以上图表类型、或模型多次生成失败时，切换到简化路径：

**布局限制为 3 种：**
- KPI 卡片网格（指标页）
- 图文分栏（解读页）
- 标题 + 要点列表（论述页）

**风格固定为 Data Dashboard：** 最简洁的预设，最低出错概率。

**功能限制：**
- 不使用 inline editing
- 动画只用 fade-in（`.reveal` 类）
- 图表只用柱状图和折线图（不用旭日图/桑基图等复杂类型）
- 不使用自定义导航（sidebar/nav-dots）

**分步生成：** 先生成前 3 页预览，确认正确后再生成剩余页面。避免一次生成全部后发现基础层有错。

---

## File Map

```
fund-slides/
  SKILL.md                         ← 入口（始终加载）
  content-mapping.md               ← 信息类型→视觉形式映射 + 强制检查清单
  STYLE_PRESETS.md                  ← 15 个视觉预设
  references/
    safe-base-template.html         ← 防护性基础模板（Phase 3 起点，内置全部安全层）
    echarts.min.js                  ← ECharts v5 库（~1MB，生成时内联到 HTML）
    viewport-base.css               ← 响应式 CSS + CJK + 全局 A 股配色 + 趋势箭头
    animation-patterns.md           ← 动画模式
    charts-base.md                  ← ECharts 基础设施 + 速查表 + SVG
    charts-trend.md                 ← 折线/面积/柱状图
    charts-composition.md           ← 饼图/玫瑰/Treemap/旭日图
    charts-matrix.md                ← 热力图/雷达/散点图
    charts-flow.md                  ← 瀑布/K线/漏斗/桑基图
    financial-layouts.md            ← KPI/表格/时间线/对比布局
    html-template.md                ← HTML 结构 + JS 功能
  scripts/
    extract-pptx.py                 ← PPT 内容提取（Phase 4）
```

| File | When to Read |
|------|-------------|
| content-mapping.md | **MANDATORY** Phase 1.2（强制检查清单） |
| STYLE_PRESETS.md | **MANDATORY** Phase 2 + Phase 3.1 |
| references/safe-base-template.html | **MANDATORY** Phase 3.0（复制为起点） |
| references/charts-base.md | Phase 3.1 -- 含图表时（基础设施 + 速查表） |
| references/charts-trend.md | Phase 3.1 -- 含折线/面积/柱状图时 |
| references/charts-composition.md | Phase 3.1 -- 含饼图/玫瑰/Treemap/旭日图时 |
| references/charts-matrix.md | Phase 3.1 -- 含热力图/雷达/散点图时 |
| references/charts-flow.md | Phase 3.1 -- 含瀑布/K线/漏斗/桑基图时 |
| references/financial-layouts.md | Phase 3.1 -- 含 KPI/表格/时间线/对比时 |
| references/animation-patterns.md | Phase 3.1 -- 高级动画时 |
| references/html-template.md | Phase 3.1 -- 编辑功能等 JS 参考 |
