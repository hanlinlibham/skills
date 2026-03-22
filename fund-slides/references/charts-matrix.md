# Charts -- Matrix (矩阵与分布类)

热力图、相关性矩阵、雷达图、散点图。基础设施见 [charts-base.md](charts-base.md)。

---

## 热力图（NxM 矩阵数据）

两个维度交叉的数值强度，颜色深浅表示大小。

```javascript
const heatmapOption = {
    tooltip: { position: 'top', formatter: p => p.data[1] + ' x ' + p.data[0] + ': ' + p.data[2] },
    grid: { left: '12%', right: '8%', top: '8%', bottom: '15%' },
    xAxis: {
        type: 'category',
        data: ['Q1', 'Q2', 'Q3', 'Q4'],
        splitArea: { show: true },
        axisLabel: { fontSize: 11 }
    },
    yAxis: {
        type: 'category',
        data: ['游戏', '社交', '广告', '金融科技', '云服务'],
        splitArea: { show: true },
        axisLabel: { fontSize: 11 }
    },
    visualMap: {
        min: 0, max: 600,
        calculable: true,
        orient: 'horizontal',
        left: 'center', bottom: '0%',
        inRange: { color: ['#f0f4ff', '#93c5fd', '#2563eb', '#1a365d'] },
        textStyle: { fontSize: 10 }
    },
    series: [{
        type: 'heatmap',
        data: [
            ['Q1', '游戏', 480], ['Q2', '游戏', 520], ['Q3', '游戏', 460], ['Q4', '游戏', 580],
            ['Q1', '社交', 290], ['Q2', '社交', 310], ['Q3', '社交', 300], ['Q4', '社交', 320],
            ['Q1', '广告', 250], ['Q2', '广告', 340], ['Q3', '广告', 310], ['Q4', '广告', 380],
            ['Q1', '金融科技', 490], ['Q2', '金融科技', 530], ['Q3', '金融科技', 510], ['Q4', '金融科技', 560],
            ['Q1', '云服务', 130], ['Q2', '云服务', 150], ['Q3', '云服务', 155], ['Q4', '云服务', 170]
        ],
        label: { show: true, fontSize: 10, color: '#333', formatter: p => p.data[2] },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }
    }]
};
```

---

## 相关性热力图（方阵）

对称矩阵，-1 到 +1 色阶。适用于多资产/多因子相关系数。

```javascript
const labels = ['贵州茅台', '五粮液', '泸州老窖', '山西汾酒', '洋河股份'];
const corrData = [
    [0,0,1.0],[1,0,0.85],[2,0,0.82],[3,0,0.71],[4,0,0.68],
    [0,1,0.85],[1,1,1.0],[2,1,0.91],[3,1,0.78],[4,1,0.74],
    [0,2,0.82],[1,2,0.91],[2,2,1.0],[3,2,0.80],[4,2,0.72],
    [0,3,0.71],[1,3,0.78],[2,3,0.80],[3,3,1.0],[4,3,0.65],
    [0,4,0.68],[1,4,0.74],[2,4,0.72],[3,4,0.65],[4,4,1.0]
];

const corrMatrixOption = {
    tooltip: { formatter: p => labels[p.data[0]] + ' vs ' + labels[p.data[1]] + ': ' + p.data[2].toFixed(2) },
    grid: { left: '15%', right: '12%', top: '15%', bottom: '5%' },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'category', data: labels, axisLabel: { fontSize: 10 } },
    visualMap: {
        min: -1, max: 1,
        inRange: { color: ['#dc2626', '#fef2f2', '#ffffff', '#eff6ff', '#2563eb'] },
        orient: 'horizontal', left: 'center', bottom: '0%',
        text: ['+1.0', '-1.0']
    },
    series: [{
        type: 'heatmap',
        data: corrData,
        label: { show: true, fontSize: 10, formatter: p => p.data[2].toFixed(2) }
    }]
};
```

---

## 雷达图（多维评分对比）

多个维度的综合评分。2 个主体对比最佳。

```javascript
const radarOption = {
    tooltip: {},
    legend: { top: '2%' },
    radar: {
        indicator: [
            { name: '网络效应', max: 10 },
            { name: '转换成本', max: 10 },
            { name: '品牌价值', max: 10 },
            { name: '规模经济', max: 10 },
            { name: '无形资产', max: 10 },
            { name: '成本优势', max: 10 }
        ],
        radius: '65%',
        axisName: { fontSize: 11, fontFamily: 'Noto Sans SC' },
        splitArea: { areaStyle: { color: ['rgba(37,99,235,0.02)', 'rgba(37,99,235,0.05)'] } }
    },
    series: [{
        type: 'radar',
        data: [
            { name: '腾讯', value: [9.5, 9.0, 7.0, 8.0, 8.5, 5.0], areaStyle: { opacity: 0.25 }, lineStyle: { width: 2 } },
            { name: '阿里巴巴', value: [7.0, 7.5, 6.5, 8.5, 6.0, 6.0], areaStyle: { opacity: 0.15 }, lineStyle: { width: 2 } }
        ]
    }]
};
```

---

## 散点图 / 气泡图

两变量相关性，气泡大小编码第三维度。

```javascript
const scatterOption = {
    tooltip: {
        formatter: p => p.data[3] + '<br/>PE: ' + p.data[0] + 'x<br/>ROE: ' + p.data[1] + '%<br/>市值: ' + formatCN(p.data[2])
    },
    grid: { left: '10%', right: '8%', top: '8%', bottom: '12%' },
    xAxis: { name: 'PE (TTM)', nameLocation: 'center', nameGap: 30, scale: true },
    yAxis: { name: 'ROE (%)', nameLocation: 'center', nameGap: 35, scale: true },
    series: [{
        type: 'scatter',
        symbolSize: p => Math.sqrt(p[2]) / 800,
        data: [
            [22.8, 22.5, 53000e8, '腾讯'],
            [16.2, 12.8, 22000e8, '阿里巴巴'],
            [28.5, 35.2, 16000e8, 'Meta'],
            [35.0, 42.0, 33000e8, '微软'],
            [25.0, 30.0, 25000e8, '字节(估)']
        ],
        label: { show: true, formatter: p => p.data[3], position: 'top', fontSize: 10 },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }
    }]
};
```
