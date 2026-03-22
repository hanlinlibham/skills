# Charts -- Composition (构成类)

饼图、环形图、Treemap、旭日图等。基础设施见 [charts-base.md](charts-base.md)。

---

## 环形饼图（3-6 项占比）

```javascript
const pieOption = {
    color: ['#1a365d', '#2563eb', '#60a5fa', '#93c5fd', '#c5963a'],
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: '5%', top: 'center' },
    series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        padAngle: 2,
        itemStyle: { borderRadius: 4 },
        label: { formatter: '{b}\n{d}%', fontSize: 11 },
        emphasis: {
            label: { fontSize: 14, fontWeight: 'bold' },
            itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.2)' }
        },
        data: [
            { value: 4500, name: '业务A' },
            { value: 3200, name: '业务B' },
            { value: 2100, name: '业务C' },
            { value: 1500, name: '其他' }
        ]
    }]
};
```

---

## 玫瑰图 / 南丁格尔图

各项数值差异大时，用半径缩放强调差异。

```javascript
const roseOption = {
    color: ['#1a365d', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#c5963a'],
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: '3%', left: 'center' },
    series: [{
        type: 'pie',
        radius: ['15%', '70%'],
        center: ['50%', '45%'],
        roseType: 'area',          /* 'radius' = 半径缩放, 'area' = 面积缩放 */
        itemStyle: { borderRadius: 5 },
        label: { formatter: '{b}\n{c}亿', fontSize: 11 },
        data: [
            { value: 1843, name: '游戏' },
            { value: 1200, name: '社交网络' },
            { value: 1240, name: '网络广告' },
            { value: 2100, name: '金融科技' },
            { value: 69, name: '其他' }
        ]
    }]
};
```

---

## 嵌套环形图（两级分类）

内环大类，外环细分。

```javascript
const nestedPieOption = {
    tooltip: { trigger: 'item', formatter: '{a}<br/>{b}: {c} ({d}%)' },
    series: [
        {
            name: '大类',
            type: 'pie',
            radius: ['0%', '35%'],
            label: { position: 'inner', fontSize: 10, color: '#fff' },
            data: [
                { value: 3043, name: '增值服务' },
                { value: 2100, name: '金融科技' },
                { value: 1240, name: '广告' }
            ]
        },
        {
            name: '细分',
            type: 'pie',
            radius: ['45%', '70%'],
            label: { formatter: '{b}: {d}%', fontSize: 10 },
            data: [
                { value: 1843, name: '游戏' },
                { value: 1200, name: '社交网络' },
                { value: 1100, name: '支付' },
                { value: 1000, name: '企业服务' },
                { value: 740, name: '媒体广告' },
                { value: 500, name: '社交广告' }
            ]
        }
    ]
};
```

---

## 半环仪表盘（单指标达标率）

```javascript
const gaugeOption = {
    series: [{
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        radius: '90%',
        center: ['50%', '65%'],
        min: 0, max: 100,
        pointer: { show: false },
        progress: { show: true, overlap: false, roundCap: true, width: 18, itemStyle: { color: '#2563eb' } },
        axisLine: { lineStyle: { width: 18, color: [[1, '#e5e7eb']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: {
            fontSize: 28, fontFamily: 'Noto Sans SC', fontWeight: 700,
            formatter: '{value}%', offsetCenter: [0, '-15%'], color: '#1a1a2e'
        },
        title: { fontSize: 13, offsetCenter: [0, '15%'], color: '#5a5a7a' },
        data: [{ value: 73.5, name: '目标达成率' }]
    }]
};
```

---

## Treemap 矩形树图

面积 = 数值大小。适合两层层级构成。

```javascript
const treemapOption = {
    tooltip: {
        formatter: p => {
            const path = p.treePathInfo.map(n => n.name).filter(n => n).join(' > ');
            return path + '<br/>金额: ' + formatCN(p.value);
        }
    },
    series: [{
        type: 'treemap',
        roam: false,
        width: '92%', height: '85%', top: '8%',
        breadcrumb: { show: true, bottom: 0 },
        label: { show: true, formatter: '{b}\n{c}亿', fontSize: 12, fontFamily: 'Noto Sans SC' },
        upperLabel: { show: true, height: 24, fontSize: 12, fontWeight: 600, color: '#fff' },
        levels: [
            { itemStyle: { borderColor: '#fff', borderWidth: 3, gapWidth: 3 }, upperLabel: { show: true } },
            { itemStyle: { borderColor: 'rgba(255,255,255,0.5)', borderWidth: 1, gapWidth: 1 }, colorSaturation: [0.3, 0.6] }
        ],
        data: [
            {
                name: '增值服务', value: 3043,
                children: [
                    { name: '本土游戏', value: 1200, itemStyle: { color: '#1a365d' } },
                    { name: '海外游戏', value: 643, itemStyle: { color: '#2563eb' } },
                    { name: '社交网络', value: 1200, itemStyle: { color: '#3b82f6' } }
                ]
            },
            {
                name: '金融科技', value: 2100,
                children: [
                    { name: '支付', value: 1100, itemStyle: { color: '#c5963a' } },
                    { name: '云服务', value: 600, itemStyle: { color: '#d4a853' } },
                    { name: '其他', value: 400, itemStyle: { color: '#e8c882' } }
                ]
            },
            {
                name: '网络广告', value: 1240,
                children: [
                    { name: '社交广告', value: 740, itemStyle: { color: '#16a34a' } },
                    { name: '媒体广告', value: 500, itemStyle: { color: '#22c55e' } }
                ]
            }
        ]
    }]
};
```

---

## 旭日图 Sunburst（多层级环形）

从内到外逐层细化。适合 3 层以上层级。

```javascript
const sunburstOption = {
    tooltip: {
        formatter: p => {
            const path = p.treePathInfo.map(n => n.name).filter(n => n).join(' > ');
            return path + '<br/>金额: ' + formatCN(p.value);
        }
    },
    series: [{
        type: 'sunburst',
        radius: ['12%', '85%'],
        sort: 'desc',
        emphasis: { focus: 'ancestor' },
        label: { fontSize: 10, fontFamily: 'Noto Sans SC', rotate: 'radial', minAngle: 10 },
        levels: [
            {},
            { r0: '12%', r: '40%', label: { fontSize: 12, fontWeight: 600 }, itemStyle: { borderWidth: 2, borderColor: '#fff' } },
            { r0: '40%', r: '65%', label: { fontSize: 10 }, itemStyle: { borderWidth: 1.5, borderColor: '#fff' } },
            { r0: '65%', r: '85%', label: { fontSize: 9, align: 'right' }, itemStyle: { borderWidth: 1, borderColor: 'rgba(255,255,255,0.6)' } }
        ],
        data: [
            {
                name: '增值服务', itemStyle: { color: '#1a365d' },
                children: [
                    { name: '游戏', value: 1843, children: [
                        { name: '王者荣耀', value: 500 }, { name: '和平精英', value: 350 },
                        { name: 'LoL/Valorant', value: 400 }, { name: '其他', value: 593 }
                    ]},
                    { name: '社交网络', value: 1200, children: [
                        { name: '会员订阅', value: 650 }, { name: '虚拟道具', value: 550 }
                    ]}
                ]
            },
            {
                name: '金融科技', itemStyle: { color: '#c5963a' },
                children: [ { name: '支付', value: 1100 }, { name: '云服务', value: 600 }, { name: '其他', value: 400 } ]
            },
            {
                name: '广告', itemStyle: { color: '#16a34a' },
                children: [ { name: '社交广告', value: 740 }, { name: '媒体广告', value: 500 } ]
            }
        ]
    }]
};
```
