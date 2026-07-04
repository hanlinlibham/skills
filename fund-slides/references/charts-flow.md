# Charts -- Flow (流向与特殊类型)

瀑布图、K 线、横向条形、漏斗图、桑基图。基础设施见 [charts-base.md](charts-base.md)。

---

## 瀑布图（加减拆解）

从总量逐步拆解到净值。正/负值不同颜色。

```javascript
const waterfallOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '12%' },
    xAxis: { type: 'category', data: ['营业收入', '营业成本', '毛利', '销售费用', '管理费用', '财务费用', '营业利润'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => formatCN(v) } },
    series: [
        {
            name: '辅助',
            type: 'bar', stack: 'total',
            itemStyle: { borderColor: 'transparent', color: 'transparent' },
            data: [0, 0, 0, 0, 0, 0, 0]  /* 计算后的偏移量 */
        },
        {
            name: '数值',
            type: 'bar', stack: 'total', barWidth: '40%',
            label: { show: true, position: 'top', formatter: p => formatCN(p.value) },
            data: [
                { value: 10000, itemStyle: { color: '#2563eb' } },
                { value: -6000, itemStyle: { color: '#dc2626' } },
                { value: 4000, itemStyle: { color: '#2563eb' } },
                { value: -800, itemStyle: { color: '#dc2626' } },
                { value: -600, itemStyle: { color: '#dc2626' } },
                { value: -200, itemStyle: { color: '#dc2626' } },
                { value: 2400, itemStyle: { color: '#16a34a' } }
            ]
        }
    ]
};
```

**瀑布图辅助层计算逻辑：**

```javascript
// 自动计算 transparent 辅助柱的高度
function buildWaterfall(items) {
    // items: [{ label, value, type: 'start'|'add'|'sub'|'total' }]
    let running = 0;
    const categories = [], assist = [], values = [];
    items.forEach(item => {
        categories.push(item.label);
        if (item.type === 'start' || item.type === 'total') {
            assist.push(0);
            values.push({ value: item.value, itemStyle: { color: item.type === 'total' ? '#16a34a' : '#2563eb' } });
            running = item.value;
        } else {
            const v = item.type === 'sub' ? -Math.abs(item.value) : Math.abs(item.value);
            assist.push(Math.max(0, running + Math.min(0, v)));
            values.push({ value: v, itemStyle: { color: v >= 0 ? '#2563eb' : '#dc2626' } });
            running += v;
        }
    });
    return { categories, assist, values };
}
```

---

## K 线图（股价走势）

A 股惯例：红涨绿跌。

```javascript
const candlestickOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '15%' },
    xAxis: { type: 'category', data: ['03-01', '03-04', '03-05', '03-06', '03-07', '03-08', '03-11', '03-12'] },
    yAxis: { type: 'value', scale: true },
    series: [{
        type: 'candlestick',
        itemStyle: {
            color: '#dc2626',        /* 阳线填充 */
            color0: '#16a34a',       /* 阴线填充 */
            borderColor: '#dc2626',
            borderColor0: '#16a34a'
        },
        data: [
            /* [open, close, low, high] */
            [540, 548, 536, 552],
            [548, 545, 540, 550],
            [545, 555, 543, 558],
            [555, 550, 546, 556],
            [550, 560, 548, 562],
            [560, 558, 554, 563],
            [558, 565, 555, 568],
            [565, 550, 548, 566]
        ]
    }]
};
```

K 线 + 成交量组合：

```javascript
const klineWithVolOption = {
    tooltip: { trigger: 'axis' },
    grid: [
        { left: '10%', right: '5%', top: '8%', height: '55%' },     /* K 线区域 */
        { left: '10%', right: '5%', top: '72%', height: '18%' }     /* 成交量区域 */
    ],
    xAxis: [
        { type: 'category', data: /* dates */, gridIndex: 0 },
        { type: 'category', data: /* dates */, gridIndex: 1 }
    ],
    yAxis: [
        { type: 'value', scale: true, gridIndex: 0 },
        { type: 'value', gridIndex: 1, axisLabel: { formatter: v => formatCN(v) } }
    ],
    series: [
        {
            type: 'candlestick',
            xAxisIndex: 0, yAxisIndex: 0,
            itemStyle: { color: '#dc2626', color0: '#16a34a', borderColor: '#dc2626', borderColor0: '#16a34a' },
            data: /* [[open,close,low,high], ...] */
        },
        {
            type: 'bar',
            xAxisIndex: 1, yAxisIndex: 1,
            barWidth: '60%',
            data: /* volume array, with itemStyle per bar based on up/down */
        }
    ]
};
```

---

## 横向条形图（排名 / Top N）

横向更易阅读长标签。inverse 从上到下递减。

```javascript
const horizontalBarOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '22%', right: '10%', top: '5%', bottom: '5%' },
    xAxis: { type: 'value', axisLabel: { formatter: v => formatCN(v) } },
    yAxis: {
        type: 'category',
        inverse: true,
        data: ['腾讯', 'Sony', '微软', '任天堂', 'EA', '动视暴雪'],
        axisLabel: { fontSize: 12 }
    },
    series: [{
        type: 'bar',
        barWidth: '55%',
        data: [
            { value: 1843, itemStyle: { color: '#1a365d' } },
            { value: 1250, itemStyle: { color: '#93c5fd' } },
            { value: 1180, itemStyle: { color: '#93c5fd' } },
            { value: 920, itemStyle: { color: '#93c5fd' } },
            { value: 580, itemStyle: { color: '#93c5fd' } },
            { value: 520, itemStyle: { color: '#93c5fd' } }
        ],
        label: { show: true, position: 'right', formatter: p => formatCN(p.value), fontSize: 11 },
        itemStyle: { borderRadius: [0, 3, 3, 0] }
    }]
};
```

---

## 漏斗图（转化/筛选流程）

逐步递减的转化过程。

```javascript
const funnelOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
        type: 'funnel',
        left: '15%', right: '15%', top: '8%', bottom: '8%',
        width: '70%',
        minSize: '15%', maxSize: '100%',
        sort: 'descending',
        gap: 4,
        label: { show: true, position: 'inside', formatter: '{b}\n{c}', fontSize: 12, fontFamily: 'Noto Sans SC' },
        itemStyle: { borderWidth: 0 },
        data: [
            { value: 5000, name: '初筛股票池', itemStyle: { color: '#93c5fd' } },
            { value: 2800, name: '基本面过滤', itemStyle: { color: '#60a5fa' } },
            { value: 1200, name: '估值合理', itemStyle: { color: '#3b82f6' } },
            { value: 450, name: '技术面确认', itemStyle: { color: '#2563eb' } },
            { value: 120, name: '最终标的', itemStyle: { color: '#1a365d' } }
        ]
    }]
};
```

---

## 桑基图 Sankey（价值流向）

从来源到去向的流转关系。

```javascript
const sankeyOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c}亿' },
    series: [{
        type: 'sankey',
        layout: 'none',
        top: '5%', bottom: '5%', left: '5%', right: '15%',
        nodeWidth: 20,
        nodeGap: 12,
        label: { fontSize: 11, fontFamily: 'Noto Sans SC' },
        lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.4 },
        emphasis: { lineStyle: { opacity: 0.7 } },
        data: [
            { name: '游戏' }, { name: '社交' }, { name: '广告' }, { name: '金融科技' },
            { name: '营业收入' }, { name: '营业成本' }, { name: '毛利' }, { name: '费用' }, { name: '净利润' }
        ],
        links: [
            { source: '游戏', target: '营业收入', value: 1843 },
            { source: '社交', target: '营业收入', value: 1200 },
            { source: '广告', target: '营业收入', value: 1240 },
            { source: '金融科技', target: '营业收入', value: 2100 },
            { source: '营业收入', target: '营业成本', value: 3073 },
            { source: '营业收入', target: '毛利', value: 3536 },
            { source: '毛利', target: '费用', value: 1515 },
            { source: '毛利', target: '净利润', value: 2021 }
        ]
    }]
};
```
