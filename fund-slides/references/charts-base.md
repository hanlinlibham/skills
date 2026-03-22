# Charts Base -- 基础设施与工具

ECharts 集成基础：内联引入、容器规范、初始化模式、格式化工具、配色适配。

按需加载具体图表配置：
- [charts-trend.md](charts-trend.md) -- 折线/面积/柱状等趋势图
- [charts-composition.md](charts-composition.md) -- 饼图/玫瑰/Treemap/旭日图等构成图
- [charts-matrix.md](charts-matrix.md) -- 热力图/雷达/散点等矩阵图
- [charts-flow.md](charts-flow.md) -- 瀑布/K线/漏斗/桑基等流向图

---

## ECharts 内联引入（零外部依赖）

**禁止使用 CDN `<script src="...">`。** ECharts 必须内嵌到 HTML 中确保离线可用。

生成流程：
1. 读取本地文件 [echarts.min.js](echarts.min.js)（~1MB，已预存在 references 目录）
2. 将完整内容包裹在 `<script>/* ECharts v5 */...内容...</script>` 中
3. 放置位置：模板的 `<!-- SLOT: ECHARTS INLINE -->` 处（在 SLOT: SLIDES 之后、base JS 之前）

```html
<!-- 正确：内联（读取 references/echarts.min.js 内容） -->
<script>/* ECharts v5 - inline */
...（references/echarts.min.js 的完整内容）...
</script>

<!-- 错误：CDN 引用（禁止） -->
<!-- <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script> -->
```

## 容器规范

```html
<div class="chart-container" id="chart1"></div>
```

```css
.chart-container {
    width: min(90vw, 800px);
    height: min(50vh, 400px);
    margin: 0 auto;
}
@media (max-height: 700px) { .chart-container { height: min(40vh, 300px); } }
@media (max-height: 500px) { .chart-container { height: min(35vh, 250px); } }
```

## 初始化模式

图表必须在 slide 可见时初始化，否则容器尺寸为 0：

```javascript
const chartObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const charts = entry.target.querySelectorAll('.chart-container[data-chart]');
            charts.forEach(el => {
                if (!el._echartInstance) {
                    const chart = echarts.init(el);
                    chart.setOption(JSON.parse(el.dataset.chart));
                    el._echartInstance = chart;
                }
            });
        }
    });
}, { threshold: 0.3 });
```

## 窗口 resize

```javascript
window.addEventListener('resize', () => {
    document.querySelectorAll('.chart-container').forEach(el => {
        if (el._echartInstance) el._echartInstance.resize();
    });
});
```

---

## 中文数字格式化工具

每个包含数据的演示必须内嵌：

```javascript
function formatCN(num, decimals = 1) {
    if (num === null || num === undefined) return '--';
    const abs = Math.abs(num);
    const sign = num < 0 ? '-' : '';
    if (abs >= 1e8) return sign + (abs / 1e8).toFixed(decimals).replace(/\.0$/, '') + '\u4ebf';
    if (abs >= 1e4) return sign + (abs / 1e4).toFixed(decimals).replace(/\.0$/, '') + '\u4e07';
    return sign + abs.toLocaleString('zh-CN');
}

function formatPct(num, decimals = 2) {
    if (num === null || num === undefined) return '--';
    return (num * 100).toFixed(decimals) + '%';
}

function formatDateCN(dateStr) {
    const d = new Date(dateStr);
    return d.getFullYear() + '\u5e74' + (d.getMonth() + 1) + '\u6708' + d.getDate() + '\u65e5';
}
```

---

## 配色适配

```javascript
function getThemeColors() {
    const s = getComputedStyle(document.documentElement);
    return {
        primary:   s.getPropertyValue('--accent').trim() || '#2563eb',
        secondary: s.getPropertyValue('--accent-secondary').trim() || '#60a5fa',
        negative:  s.getPropertyValue('--color-negative').trim() || '#dc2626',
        positive:  s.getPropertyValue('--color-positive').trim() || '#16a34a',
        text:      s.getPropertyValue('--text-primary').trim() || '#333',
        textSec:   s.getPropertyValue('--text-secondary').trim() || '#666',
        bg:        s.getPropertyValue('--bg-primary').trim() || '#fff'
    };
}

function initThemedChart(el, option) {
    const colors = getThemeColors();
    const chart = echarts.init(el, null, { renderer: 'canvas' });
    option.textStyle = option.textStyle || {};
    option.textStyle.fontFamily = getComputedStyle(document.documentElement)
        .getPropertyValue('--font-body').trim() || 'Noto Sans SC, sans-serif';
    option.textStyle.color = colors.text;
    chart.setOption(option);
    return chart;
}
```

---

## 图表类型速查

| 要表达什么 | 推荐图表 | 次选 | 配置文件 |
|-----------|---------|------|---------|
| 单指标趋势 | 面积图 | 折线图 | charts-trend |
| 多指标趋势 | 柱线混合图 | 堆叠面积图 | charts-trend |
| 增长率趋势 | 双Y轴折线 | 面积图 | charts-trend |
| 构成占比 (3-6项) | 环形饼图 | 玫瑰图 | charts-composition |
| 差异大的占比 | 玫瑰图 | Treemap | charts-composition |
| 两级分类构成 | 嵌套环形图 | Treemap | charts-composition |
| 三级以上层级 | 旭日图 | Treemap | charts-composition |
| 面积=数值的层级 | Treemap | 旭日图 | charts-composition |
| 单一达标率 | 半环仪表盘 | KPI卡片 | charts-composition |
| 排名 / Top N | 横向条形图 | 柱状图 | charts-flow |
| 多主体多指标对比 | 分组柱状图 | 雷达图 | charts-trend |
| 构成+时间趋势 | 堆叠柱状图 | 堆叠面积图 | charts-trend |
| 多维综合评分 | 雷达图 | CSS评分条 | charts-matrix |
| 两变量相关性 | 散点图 | 热力图 | charts-matrix |
| NxM 矩阵数据 | 热力图 | 表格 | charts-matrix |
| 相关系数矩阵 | 相关性热力图 | 表格 | charts-matrix |
| 逐步递减/转化 | 漏斗图 | 瀑布图 | charts-flow |
| 加减拆解 | 瀑布图 | 堆叠柱 | charts-flow |
| 流向/流转 | 桑基图 | 嵌套环形 | charts-flow |
| 股价走势 | K线图 | 面积折线 | charts-flow |

---

## Inline SVG (零依赖)

不引入 ECharts 时，用 SVG 实现简单图表。

### 简单柱状图

```html
<svg class="chart-svg" viewBox="0 0 400 200" preserveAspectRatio="xMidYMid meet">
    <style>
        .bar { transition: height 0.6s var(--ease-out-expo), y 0.6s var(--ease-out-expo); }
        .bar-label { font-family: var(--font-body); font-size: 11px; fill: var(--text-secondary); text-anchor: middle; }
        .bar-value { font-family: var(--font-body); font-size: 10px; fill: var(--text-primary); text-anchor: middle; }
    </style>
    <line x1="50" y1="10" x2="50" y2="170" stroke="var(--text-secondary)" stroke-width="0.5"/>
    <rect class="bar" x="70" y="50" width="40" height="120" fill="var(--accent)" rx="2"/>
    <rect class="bar" x="130" y="80" width="40" height="90" fill="var(--accent)" rx="2" opacity="0.7"/>
    <rect class="bar" x="190" y="30" width="40" height="140" fill="var(--accent)" rx="2"/>
    <rect class="bar" x="250" y="60" width="40" height="110" fill="var(--accent)" rx="2" opacity="0.7"/>
    <text class="bar-label" x="90" y="190">Q1</text>
    <text class="bar-label" x="150" y="190">Q2</text>
    <text class="bar-label" x="210" y="190">Q3</text>
    <text class="bar-label" x="270" y="190">Q4</text>
    <text class="bar-value" x="90" y="45">1.2亿</text>
    <text class="bar-value" x="150" y="75">0.9亿</text>
    <text class="bar-value" x="210" y="25">1.4亿</text>
    <text class="bar-value" x="270" y="55">1.1亿</text>
</svg>
```

### 简单折线图

```html
<svg class="chart-svg" viewBox="0 0 400 200" preserveAspectRatio="xMidYMid meet">
    <defs>
        <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="var(--accent)" stop-opacity="0"/>
        </linearGradient>
    </defs>
    <path d="M50,140 L120,100 L190,110 L260,60 L330,40 L330,170 L50,170 Z" fill="url(#lineGrad)"/>
    <polyline points="50,140 120,100 190,110 260,60 330,40"
              fill="none" stroke="var(--accent)" stroke-width="2"
              stroke-dasharray="500" stroke-dashoffset="500">
        <animate attributeName="stroke-dashoffset" to="0" dur="1.5s" fill="freeze"
                 begin="0.3s" calcMode="spline" keySplines="0.16 1 0.3 1"/>
    </polyline>
    <circle cx="50" cy="140" r="3" fill="var(--accent)"/>
    <circle cx="120" cy="100" r="3" fill="var(--accent)"/>
    <circle cx="190" cy="110" r="3" fill="var(--accent)"/>
    <circle cx="260" cy="60" r="3" fill="var(--accent)"/>
    <circle cx="330" cy="40" r="3" fill="var(--accent)"/>
</svg>
```

```css
.chart-svg {
    width: min(90vw, 600px);
    height: min(40vh, 300px);
    display: block;
    margin: 0 auto;
}
```
