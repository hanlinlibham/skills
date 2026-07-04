# HLB_ 仪表盘（Air Vault Dashboard）

> Obsidian 主页门户的 HLB_ 实现。**浅色变体**：暖白底 + 橙 accent + 等宽 + 零圆角 + 编号分区，叠在 Brutalist 主题的 masonry(column) 网格上。
> 源文件：`00-Dashboard/Dashboard.md`（Markdown + DataviewJS 逻辑）+ `.obsidian/snippets/dashboard.css`（样式）。本页把它的**设计 / 逻辑 / 排布**沉淀为可复用范式。

---

## 0. 与暗黑基底的关系

主站（lihanlin.com、AbleMind…）是**暗黑**变体；本仪表盘是同一套 HLB_ 语言的**浅色**变体——规则不变（等宽 / 零圆角 / 橙 accent / 编号分区 / 大写标签），只把 surface 反相为暖白。

> ⚠️ **本页色板 = 浅色 v1 遗留**（Air Vault 已部署实例的 as-built 记录）。
> 2026-07-04 起新建浅色页面一律用 colors.md「浅色模式（标准色板 v2）」——
> ablemind gov-review 快照（bg `#F8F6F2` / text `#1D2330` / border `#D3C9BB` /
> 默认 accent 深蓝 `#22456D`，语义色成对）。本页其余部分（布局/DataviewJS/masonry 范式）不受影响，仍然有效。

| token | 暗黑基底 | 仪表盘（浅色） |
|------|----------|----------------|
| `--bg` | `#0A0A0A` | `#F4F2EC`（暖白） |
| `--surface-1` | `#141414` | `#FFFFFF` |
| `--surface-2` | `#1E1E1E` | `#FBFAF5` |
| `--text-primary` | `#F0F0F0` | `#1B1813` |
| `--text-secondary` | `#B0B0B8` | `#57534B` |
| `--text-muted` | `#858088` | `#8E887C` |
| `--border` | `#3A363E` | `#DBD7CB` |
| `--accent` | `#FF5C00` | `#FF5C00`（不变） |
| `--accent-10 / -25` | 橙 10% / 25% | `rgba(255,92,0,.07)` / `.22` |
| 健康徽标 ok / warn | — | `#2DA44E` / `#E5484D` |

挂载选择器：`cssclasses: [dashboard, hlb, hide-all]`，样式作用于 `.markdown-preview-view.dashboard`。

---

## 1. 排布（整体结构）

全宽 Hero 横跨顶部；下方四张「信息流」卡片各占一列（masonry column）；底部全宽 footer。

```
┌───────────────────────────────────────────────────────────────┐
│ HERO（全宽，三段式 flex，底对齐）                                │
│ ┌── main ──────┬─ mid ───────────────┬─ stats ──────────────┐ │
│ │ [KNOWLEDGE…] │ MACRO 本体·当前构成   │  12   45    3        │ │
│ │ AIR VAULT    │ 机构3 工具6 指标9 …   │ 节点  笔记  INBOX     │ │
│ │ (em=橙)      │ [健康·无断链] (badge) │   8    4    33%       │ │
│ │ 早上好·日期   │                      │ 待办  项目  完成      │ │
│ └──────────────┴─────────────────────┴──────────────────────┘ │
│ 知识本体 · 项目 · 领域 · 资源 · 日记 · 收集箱 · MOC   ← 导航行   │
├───────────────────────────────────────────────────────────────┤
│ 01 信息流                                          ← 全宽 H2     │
│ `发散 INBOX` → `研究` → `编译 WIKI` → `看板 GRAPH`  ← 流程横幅   │
│ ┌── ① 发散 ──┐ ┌── ② 行动 ──┐ ┌── ③ 编译 ──┐ ┌── ④ 看板 ──┐  │
│ │ INBOX 表   │ │ 今日待办   │ │ WIKI 节点  │ │ GRAPH 嵌入 │  │ ← 四列并排
│ │ (dataview) │ │ 活跃项目   │ │ (dataview) │ │ 拓扑图     │  │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
├───────────────────────────────────────────────────────────────┤
│ © 2026 HLB_ / AIR VAULT · 知识编译全过程 · MOC      ← 全宽 quote │
└───────────────────────────────────────────────────────────────┘
```

**网格逻辑**：正文默认走 Brutalist 主题的 `column`(masonry) 多列流；HLB_ 用 `column-span: all` 把 Hero(abstract)、每个 H2、流程横幅、footer(quote) **拉成全宽横幅**，把四张卡片用 `break-before: column` 强制**各起一列**横向并排——一屏看全局。

```css
/* 全宽横幅：Hero / H2 / 流程行 / footer */
.dashboard .callout[data-callout="abstract"],
.dashboard h2,
.dashboard h2 + p,
.dashboard .callout[data-callout="quote"] { column-span: all; }

/* 四张信息流卡片：各占一列 */
.dashboard .callout + .callout:not([data-callout="abstract"]):not([data-callout="quote"]) { break-before: column; }
.dashboard .el-callout + .el-callout { break-before: column; }   /* 阅读视图 DOM 兼容 */
.dashboard .callout { break-inside: avoid; }
```

---

## 2. Hero 三段式

`> [!abstract]` callout 渲染成全宽、底对齐的三段 flex：**左标题 main | 中本体构成 mid | 右指标 stats**，用 `border-left` 竖线分隔。隐藏 callout 自带标题/图标。

```
┌─ .hlb-hero-main ─┬─ .hlb-hero-mid ──────────┬─ .hlb-hero-stats ─┐
│ .hlb-badge       │ .hlb-mid-lbl (大写小标)   │ 3列 grid:         │
│ h1 + h1 em(橙)   │ .hlb-types(机构N 工具N…)  │ .hlb-stat(b+span) │
│ .hlb-greet       │ .hlb-badge2.ok/.warn      │ ×6                │
└──────────────────┴──────────────────────────┴───────────────────┘
       flex:0 1 auto        flex:1 1 auto(填空白)     flex:0 0 auto
```

DataviewJS 直接 `innerHTML` 注入这三段（见 §3）。关键样式：

```css
.dashboard .hlb-hero { display:flex; align-items:stretch; flex-wrap:nowrap; }
.dashboard .hlb-hero-main { flex:0 1 auto; display:flex; flex-direction:column; justify-content:flex-end; align-items:flex-start; padding-right:30px; }
.dashboard .hlb-hero-mid  { flex:1 1 auto; justify-content:flex-end; gap:10px; padding:4px 30px; border-left:1px solid var(--border); }
.dashboard .hlb-hero-stats{ flex:0 0 auto; align-self:flex-end; display:grid; grid-template-columns:repeat(3,minmax(58px,auto)); gap:12px 26px; padding-left:30px; border-left:1px solid var(--border); }

.dashboard .hlb-badge { padding:4px 11px; background:var(--accent-10); border:1px solid var(--accent-25); color:var(--accent); font-size:11px; font-weight:600; letter-spacing:3px; }
.dashboard .hlb-hero h1 { font-size:clamp(34px,5.2vw,66px); font-weight:800; line-height:.9; letter-spacing:-.04em; text-transform:uppercase; }
.dashboard .hlb-hero h1 em { font-style:italic; color:var(--accent); }   /* VAULT 一词标橙 */
.dashboard .hlb-stat b   { font-size:25px; font-weight:800; color:var(--text-primary); }
.dashboard .hlb-stat span{ font-size:10px; letter-spacing:1px; text-transform:uppercase; color:var(--text-muted); }
.dashboard .hlb-badge2.ok  { color:#2DA44E; border:1px solid rgba(45,164,78,.4);  background:rgba(45,164,78,.07); }
.dashboard .hlb-badge2.warn{ color:#E5484D; border:1px solid rgba(229,72,77,.4); background:rgba(229,72,77,.07); }
```

---

## 3. 逻辑（DataviewJS）

Hero 是「活」的——每次打开按当前库状态重算问候语、6 个指标、本体构成与健康度。

```js
// 问候语随时间
const h = new Date().getHours();
const period = h < 6 ? "深夜好" : h < 12 ? "早上好" : h < 18 ? "下午好" : "晚上好";
const date = dv.date("today").toFormat("yyyy.MM.dd EEEE");

// 范围：排除 Dashboard/Templates/Attachments/dot 目录
const skip = p => !p.file.path.startsWith("00-Dashboard") && !p.file.path.startsWith("06-Templates")
             && !p.file.path.startsWith("09-Attachments") && !p.file.path.startsWith(".");
const all  = dv.pages().where(skip);
const para = all.where(p => !p.file.path.startsWith("wiki/"));   // PARA 层
const ib = dv.pages('"Inbox"').where(p => p.file.name !== "README").length;
const pj = dv.pages('"01-Projects"').where(p => p.status === "active").length;
const op = para.file.tasks.where(t => !t.completed).length;       // 待办
const dn = para.file.tasks.where(t => t.completed).length;
const pct = (op+dn) > 0 ? Math.round(dn/(op+dn)*100) : 0;         // 完成%

// 本体构成：按 wiki/macro 节点的目录(机构/工具/指标…)计数，固定顺序
const ORDER = ["机构","工具","指标","机制","事件","分析","来源"];
const nodes = dv.pages('"wiki/macro"').where(p => p.type && p.type != "ontology"
              && !p.file.name.startsWith("_") && p.file.name != "宏观" && p.file.name != "log");
const cnt = {}; for (const p of nodes) { const s = p.file.folder.split("/").pop(); cnt[s]=(cnt[s]||0)+1; }

// 健康度：争议 / 缺来源 / 孤儿 / 断链 四项求和，0 = 健康
const LABELS = new Set(["价格型","数量型","结构性"]);            // 分类标签是边不建页，断链豁免
const contested = nodes.where(p => p.confidence=="contested" || p.confidence=="low").length;
const noSrc = nodes.where(p => p.type!="source" && (!p.sources || p.sources.length==0)).length;
const orphan = nodes.where(p => p.type!="source" && p.type!="analysis" && p.file.inlinks.length==0).length;
let broken = 0; for (const p of nodes) for (const l of (p.file.outlinks||[])) {
  if (!l.path) continue; const nm = l.path.split("/").pop().replace(/\.md$/,"");
  if (LABELS.has(nm)) continue; if (!dv.page(l.path)) broken++;
}
const ok = (contested+noSrc+orphan+broken) == 0;

// 注入三段式 innerHTML
const stat  = (v,l) => `<div class="hlb-stat"><b>${v}</b><span>${l}</span></div>`;
const types = ORDER.filter(k=>cnt[k]).map(k=>`<span class="ht">${k}<b>${cnt[k]}</b></span>`).join("");
const health= ok ? "健康 · 无断链 / 孤儿 / 争议" : "待治理 "+(contested+noSrc+orphan+broken);
const root  = dv.el("div",""); root.className = "hlb-hero";
root.innerHTML =
  `<div class="hlb-hero-main"><span class="hlb-badge">KNOWLEDGE BASE</span><h1>AIR <em>VAULT</em></h1><div class="hlb-greet">${period} · ${date}</div></div>`
+ `<div class="hlb-hero-mid"><div class="hlb-mid-lbl">MACRO 本体 · 当前构成</div><div class="hlb-types">${types}</div><span class="hlb-badge2 ${ok?"ok":"warn"}">${health}</span></div>`
+ `<div class="hlb-hero-stats">${stat(nodes.length,"本体节点")}${stat(para.length,"笔记")}${stat(ib,"INBOX")}${stat(op,"待办")}${stat(pj,"项目")}${stat(pct+"%","完成")}</div>`;
```

> 设计意图：Hero 一眼给出「我是谁(AIR VAULT) + 现在几点 + 知识库长多大 + 健康不健康 + 还有多少待办」。**中段专门填补标题与指标之间的空白**（本体构成 + 健康徽标），避免三段式留白。

---

## 4. 信息流（四阶段编号分区）

正文用「知识编译生命周期」串成 4 张卡片，对应库的工作流：

```
01 信息流 :  发散 INBOX → 研究 → 编译 WIKI → 看板 GRAPH
① 发散·INBOX   [!note]     dataview：Inbox 研究专题 + 状态
② 行动·待办    [!todo]     dataviewjs：今日日记未完成任务 + dataview 活跃项目
③ 编译·进WIKI  [!info]     dataview：wiki/macro 最近 7 个节点 + 类型
④ 看板·GRAPH   [!success]  Graph 指引 + 嵌入 ![[wiki/macro/宏观#知识结构]] 拓扑
```

Markdown 骨架（callout 类型决定卡片，相邻 callout 被 CSS 拆成列）：

```markdown
## 信息流
`发散 INBOX` → `研究` → `编译 WIKI` → `看板 GRAPH`

> [!note] ① 发散 · INBOX
> ```dataview …Inbox 专题… ```

> [!todo] ② 行动 · 待办
> **今日** ```dataviewjs …今日未完成任务… ```
> **活跃项目** ```dataview …01-Projects active… ```

> [!info] ③ 编译 · 进 WIKI
> ```dataview …wiki/macro 最近节点… ```

> [!success] ④ 看板 · GRAPH
> 中心实体 **[[中国人民银行]]** · ![[wiki/macro/宏观#知识结构]]
```

「今日待办」逻辑（按当天日记取未完成任务）：

```js
const todayStr = dv.date("today").toFormat("yyyy-MM-dd");
const page = dv.page("05-Daily/"+todayStr) || dv.page(todayStr);
const open = page ? (page.file.tasks||[]).filter(t=>!t.completed) : [];
if (page && open.length) dv.taskList(open, false);
else if (page) dv.paragraph("今日已清空");
else dv.paragraph("还没有今天的日记");
```

---

## 5. 卡片 / 标题 / 表格 / Footer

```css
/* H2 全宽横幅 + 自增编号(01,02…) */
.dashboard { counter-reset: hlbsec; }
.dashboard h2 { column-span:all; display:flex; align-items:baseline; gap:14px;
  text-transform:uppercase; border-bottom:1.5px solid var(--text-primary); }
.dashboard h2::before { counter-increment:hlbsec; content:counter(hlbsec,decimal-leading-zero);
  color:var(--accent); font-weight:800; }

/* 流程横幅：h2 后第一段，code 标签反色实心 */
.dashboard h2 + p { column-span:all; color:var(--text-muted); letter-spacing:1.5px; }
.dashboard h2 + p code { background:var(--text-primary); color:var(--bg); border-radius:0; padding:6px 16px; font-weight:700; }

/* 锐角白卡：橙色大写标题 + hover 描边变橙 */
.dashboard .callout { padding:12px 16px; background:var(--surface-1); border:1px solid var(--border); border-radius:0; box-shadow:none; }
.dashboard .callout:hover { border-color:var(--accent); }
.dashboard .callout .callout-title { color:var(--accent); font-size:.72em; font-weight:700; letter-spacing:2px; text-transform:uppercase; border-bottom:1px solid var(--border); }
.dashboard .callout .callout-icon { display:none; }

/* Dataview 表：大写 muted 表头 + 细线 + hover 橙底 */
.dashboard .callout table.dataview th { color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; border-bottom:1px solid var(--border); }
.dashboard .callout table.dataview td { color:var(--text-secondary); border-bottom:1px solid var(--surface-2); }
.dashboard .callout table.dataview tbody tr:hover td { background:var(--accent-10); }

/* Footer：quote 全宽，© 2026 HLB_，顶边线 */
.dashboard .callout[data-callout="quote"] { column-span:all; background:none; border:none; border-top:1px solid var(--border); text-transform:uppercase; letter-spacing:1.5px; color:var(--text-muted); }
```

隐藏 Obsidian 默认的笔记标题与属性栏（主页门户不显示 "Dashboard"/Properties）：

```css
.dashboard .inline-title, .dashboard .metadata-container, .dashboard .frontmatter { display:none; }
```

---

## 6. 关键规则汇总

| 项 | 值 / 做法 |
|---|---|
| 画布 padding | `8px 18px 40px` |
| 字体 | 全等宽 `--font-mono`（含 `*` 强制） |
| 圆角 | 一律 `0`（锐角） |
| 全宽横幅 | `column-span: all`（Hero / H2 / 流程行 / footer） |
| 卡片成列 | 相邻 callout `break-before: column` + `break-inside: avoid` |
| Hero 分隔 | 段间 `border-left: 1px solid var(--border)`，底对齐 `justify-content:flex-end` |
| 标题强调 | h1 内 `<em>` 标 `--accent`（如 AIR <em>VAULT</em>） |
| 编号 | H2 `::before` 用 `counter(hlbsec, decimal-leading-zero)` 自增 01/02… |
| accent code | 流程横幅 code 用 `background:var(--text-primary); color:var(--bg)` 反色实心 |
| 健康徽标 | ok=`#2DA44E` / warn=`#E5484D`，三件套（争议/缺源/孤儿/断链=0 即健康） |
| hover | 卡片描边 → `--accent`；表格行 → `--accent-10` 底 |

## 7. 复用清单（做一个新 HLB_ 仪表盘）

1. `cssclasses: [dashboard, hlb, hide-all]`，启用 `dashboard.css` snippet（或暗黑变体改 surface token）。
2. Hero 用 `[!abstract]` + DataviewJS 注入 `.hlb-hero`（main/mid/stats 三段，中段填空白）。
3. 指标取「身份(谁) + 时间 + 规模 + 健康 + 待办」五类，6 格 stats 网格。
4. 正文按**工作流生命周期**切 4 张 callout 卡片（类型各异 → 颜色语义），相邻即成列。
5. H2 全宽 + 自增编号；流程横幅用反色 code 串起阶段。
6. Footer 用 `[!quote]`：`© 2026 HLB_ / PAGENAME` + 关键外链。
