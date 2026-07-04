# Charts -- Trend (趋势类)

折线图、面积图、柱状图及其变体。基础设施见 [charts-base.md](charts-base.md)。

---

## 折线图（多指标趋势）

```javascript
const lineOption = {
    color: ['#2563eb', '#dc2626'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['营业收入', '净利润'] },
    grid: { left: '8%', right: '5%', top: '15%', bottom: '12%' },
    xAxis: { type: 'category', data: ['2021', '2022', '2023', '2024', '2025E'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => formatCN(v) } },
    series: [
        { name: '营业收入', type: 'line', smooth: true, data: [1200e6, 1500e6, 1800e6, 2100e6, 2400e6] },
        { name: '净利润', type: 'line', smooth: true, data: [300e6, 380e6, 450e6, 520e6, 600e6] }
    ]
};
```

---

## 面积图（单指标 + 渐变填充）

强调规模感和趋势方向。

```javascript
const areaOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '10%' },
    xAxis: { type: 'category', boundaryGap: false, data: ['2019', '2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => formatCN(v) } },
    series: [{
        name: '用户规模',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2.5 },
        areaStyle: {
            color: {
                type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                    { offset: 0, color: 'rgba(37, 99, 235, 0.35)' },
                    { offset: 1, color: 'rgba(37, 99, 235, 0.02)' }
                ]
            }
        },
        data: [89000, 112000, 135000, 148000, 162000, 178000]
    }]
};
```

---

## 堆叠面积图（多组分构成趋势）

同时展示各部分和总量随时间的变化。

```javascript
const stackedAreaOption = {
    tooltip: {
        trigger: 'axis',
        formatter: params => {
            let s = params[0].name + '<br/>', total = 0;
            params.forEach(p => { s += p.marker + p.seriesName + ': ' + formatCN(p.value) + '<br/>'; total += p.value; });
            return s + '<b>合计: ' + formatCN(total) + '</b>';
        }
    },
    legend: { top: '2%' },
    grid: { left: '8%', right: '5%', top: '15%', bottom: '10%' },
    xAxis: { type: 'category', boundaryGap: false, data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => formatCN(v) } },
    series: [
        { name: '游戏', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.6 }, data: [1561, 1743, 1707, 1799, 1843] },
        { name: '社交网络', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.6 }, data: [1082, 1173, 1118, 1181, 1200] },
        { name: '广告', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.6 }, data: [823, 886, 827, 1015, 1240] },
        { name: '金融科技', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.6 }, data: [1281, 1722, 1771, 2038, 2100] }
    ]
};
```

---

## 双 Y 轴（绝对值 + 增速）

左轴柱状/面积展示绝对值，右轴折线展示增长率。

```javascript
const dualAxisOption = {
    tooltip: { trigger: 'axis' },
    legend: { top: '2%' },
    grid: { left: '8%', right: '8%', top: '15%', bottom: '10%' },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: [
        { type: 'value', name: '营收 (亿)', axisLabel: { formatter: v => v } },
        { type: 'value', name: 'YoY (%)', axisLabel: { formatter: v => v + '%' }, splitLine: { show: false } }
    ],
    series: [
        { name: '营业收入', type: 'bar', barWidth: '35%', data: [4821, 5601, 5546, 6090, 6609], itemStyle: { borderRadius: [3, 3, 0, 0] } },
        { name: 'YoY 增速', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2.5, type: 'dashed' }, data: [27.8, 16.2, -1.0, 9.8, 8.5] }
    ]
};
```

---

## 柱状图（季度对比）

```javascript
const barOption = {
    color: ['#2563eb', '#60a5fa'],
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '12%' },
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => formatCN(v) } },
    series: [
        { name: '2024', type: 'bar', barWidth: '30%', data: [820, 932, 901, 1034] },
        { name: '2025', type: 'bar', barWidth: '30%', data: [920, 1032, 1001, 1134] }
    ]
};
```

---

## 分组柱状图（多主体对比）

2-4 个主体在多个维度上直接对比。

```javascript
const groupedBarOption = {
    color: ['#1a365d', '#2563eb', '#60a5fa', '#c5963a'],
    tooltip: { trigger: 'axis' },
    legend: { top: '2%' },
    grid: { left: '8%', right: '5%', top: '15%', bottom: '10%' },
    xAxis: { type: 'category', data: ['营收增速', '净利率', 'ROE', 'PE'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => v + '%' } },
    series: [
        { name: '腾讯', type: 'bar', barWidth: '18%', data: [8.5, 30.6, 22.5, 22.8] },
        { name: '阿里', type: 'bar', barWidth: '18%', data: [5.2, 13.1, 12.8, 16.2] },
        { name: '字节', type: 'bar', barWidth: '18%', data: [30, 20, 30, 25] },
        { name: 'Meta', type: 'bar', barWidth: '18%', data: [22, 35.6, 35.2, 28.5] }
    ]
};
```

---

## 堆叠柱状图（构成 + 趋势）

同时展示各组成部分和总量的变化。

```javascript
const stackedBarOption = {
    color: ['#1a365d', '#2563eb', '#60a5fa', '#c5963a'],
    tooltip: {
        trigger: 'axis',
        formatter: params => {
            let s = params[0].name + '<br/>', total = 0;
            params.forEach(p => { s += p.marker + p.seriesName + ': ' + p.value + '亿<br/>'; total += p.value; });
            return s + '<b>合计: ' + total + '亿</b>';
        }
    },
    legend: { top: '2%' },
    grid: { left: '8%', right: '5%', top: '15%', bottom: '10%' },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', axisLabel: { formatter: v => v + '亿' } },
    series: [
        { name: '游戏', type: 'bar', stack: 'total', barWidth: '40%', data: [1561, 1743, 1707, 1799, 1843] },
        { name: '社交', type: 'bar', stack: 'total', data: [1082, 1173, 1118, 1181, 1200] },
        { name: '广告', type: 'bar', stack: 'total', data: [823, 886, 827, 1015, 1240] },
        { name: '金融科技', type: 'bar', stack: 'total', data: [1281, 1722, 1771, 2038, 2100] }
    ]
};
```
