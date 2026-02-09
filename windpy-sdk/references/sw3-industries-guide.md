# 申万三级行业使用指南

## 概述

申万三级行业是 Wind 提供的行业分类体系，共 **259 个行业**，覆盖全部 A 股市场。

**特点**:
- 三级分类：一级行业 → 二级行业 → 三级行业
- 每个三级行业对应一个 `.SI` 代码
- 可用于板块分析、行业轮动、量化策略

---

## 获取方法

### 获取全部申万三级行业

```python
from WindPy import w
w.start()

result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")

if result.ErrorCode == 0:
    industries = []
    for i in range(len(result.Data[1])):
        industries.append({
            'code': result.Data[1][i],  # 如: 850111.SI
            'name': result.Data[2][i]   # 如: 种子(申万)
        })
    
    print(f"共 {len(industries)} 个申万三级行业")
    # 打印前10个
    for ind in industries[:10]:
        print(f"{ind['code']} - {ind['name']}")

w.stop()
```

### 获取某个行业的所有成分股

```python
# 获取"白酒"行业的所有股票
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")

# 遍历查找"白酒"行业
for i in range(len(result.Data[2])):
    if "白酒" in result.Data[2][i]:
        industry_code = result.Data[1][i]
        industry_name = result.Data[2][i]
        print(f"找到行业: {industry_name} ({industry_code})")
        break

# 注意：获取成分股需要通过其他方式
# 如查询该行业内的具体股票代码
```

---

## 使用场景

### 场景1: 行业轮动策略

```python
# 获取所有申万三级行业的涨跌幅
industries = [...]  # 259个行业代码

for ind in industries:
    err, df = w.wsd(ind['code'], "pct_chg", "-5D", "", "", usedf=True)
    if err == 0:
        avg_return = df['PCT_CHG'].mean()
        print(f"{ind['name']}: {avg_return:.2f}%")
```

### 场景2: 行业对比分析

```python
# 对比白酒、啤酒、调味品行业的估值
sectors = [
    {"code": "850111.SI", "name": "白酒Ⅲ"},
    {"code": "850112.SI", "name": "啤酒"},
    {"code": "850113.SI", "name": "调味品"}
]

for sec in sectors:
    err, df = w.wsd(sec['code'], "pe_ttm", "", "", "", usedf=True)
    if err == 0:
        pe = df.iloc[-1]['PE_TTM']
        print(f"{sec['name']}: PE={pe}")
```

### 场景3: 行业资金流向监控

```python
# 监控各行业的主力资金流向
industries = [...]  # 行业列表

for ind in industries:
    err, df = w.wsd(ind['code'], "mfd_inflow", "-1D", "", "", usedf=True)
    if err == 0:
        inflow = df.iloc[-1]['MFD_INFLOW']
        if inflow > 100000000:  # 1亿以上
            print(f"{ind['name']}: 净流入 {inflow/1e8:.1f} 亿")
```

---

## 行业代码特点

### 代码结构

申万三级行业代码格式: `XXXXXX.SI`

| 代码范围 | 一级行业 | 说明 |
|----------|----------|------|
| 8501xx | 农林牧渔 | 种子、养殖、饲料等 |
| 8502xx | 基础化工 | 化学原料、化学制品等 |
| 8503xx | 钢铁 | 钢铁冶炼、加工等 |
| 8504xx | 有色金属 | 铜、铝、稀土等 |
| 8505xx | 建筑材料 | 水泥、玻璃等 |
| ... | ... | ... |
| 8599xx | 综合 | 综合类 |

### 行业分类层级

```
一级行业：农林牧渔 (11个)
├── 二级行业：种植业
│   └── 三级行业：种子 (850111.SI)
│   └── 三级行业：其他种植业 (850113.SI)
├── 二级行业：渔业
│   └── 三级行业：水产养殖 (850122.SI)
└── ...
```

---

## 查询技巧

### 模糊搜索行业

```python
# 搜索包含"白酒"的行业
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")

for i in range(len(result.Data[2])):
    if "白酒" in result.Data[2][i]:
        print(f"{result.Data[1][i]} - {result.Data[2][i]}")
        # 输出: 850111.SI - 白酒Ⅲ(申万)
```

### 获取行业数量

```python
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
count = len(result.Data[1])
print(f"申万三级行业总数: {count}")  # 259
```

---

## 注意事项

1. **日期参数**: 行业分类会随时间调整，建议指定具体日期
2. **行业更名**: 部分行业可能更名，以最新名称为准
3. **成分股变化**: 行业内的成分股会定期调整

---

## 相关函数

| 函数 | 用途 | 示例 |
|------|------|------|
| w.wsd() | 获取行业指数行情 | w.wsd("850111.SI", "close", "-30D", "") |
| w.wss() | 获取行业估值 | w.wss("850111.SI", "pe_ttm", "tradeDate=20241231") |
| w.wset() | 获取行业列表 | w.wset("sectorconstituent", "...sectorid=a39901011i000000") |

---

## 参考

- 一级行业数量: 31 个
- 二级行业数量: 约 130 个
- 三级行业数量: **259 个** (本指南)
- 更新频率: 每年调整一次

---

**文档版本**: 1.0  
**基于**: Wind 申万行业分类  
**代码**: a39901011i000000 (申万三级行业板块ID)
