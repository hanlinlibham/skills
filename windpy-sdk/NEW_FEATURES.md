# WindPy SDK - 新增功能说明

## 🎉 新增：A股代码查询工具

### 功能概述

现在 windpy-sdk 可以通过 WindPy 实时查询全部 A 股代码和信息！

### 核心能力

| 功能 | 说明 | 数据来源 |
|------|------|----------|
| **代码查询** | 根据名称查代码 | 实时 Wind 数据 (5,479只A股) |
| **名称查询** | 根据代码查名称 | 实时 Wind 数据 |
| **股票信息** | 价格、估值、市值 | 实时 Wind 数据 |
| **行业查询** | 申万三级行业 | 259个行业分类 |

### 使用方法

#### Python API

```python
from scripts.windpy_stock_query import StockQuery

query = StockQuery()

# 1. 根据名称查代码
results = query.find_by_name("茅台")
# 返回: [{'code': '600519.SH', 'name': '贵州茅台'}]

# 2. 根据代码查名称
name = query.get_name("600519.SH")
# 返回: '贵州茅台'

# 3. 获取详细信息
info = query.get_info("600519.SH")
# 返回: {
#     'name': '贵州茅台',
#     'close': 1515.01,
#     'pct_chg': 0.5,
#     'pe_ttm': 25.3,
#     'pb_lf': 8.2,
#     'mkt_cap': 19000亿
# }

# 4. 获取最新价格
price = query.get_price("600519.SH")
# 返回: 1515.01

# 5. 搜索行业
industries = query.search_industry("白酒")
# 返回: [{'code': '850111.SI', 'name': '白酒Ⅲ(申万)'}]
```

#### 命令行

```bash
# 按名称查询
python scripts/windpy_stock_query.py 茅台
# 输出:
# 搜索: 茅台
# 找到 1 个结果:
#   600519.SH - 贵州茅台

# 按代码查询
python scripts/windpy_stock_query.py 600519.SH
# 输出:
# 查询代码: 600519.SH
# 名称: 贵州茅台
# 最新价: 1515.01
# 涨跌幅: 0.5%
# 市盈率: 25.3
# 市净率: 8.2
```

### 数据覆盖范围

| 数据类型 | 数量 | 查询方法 |
|----------|------|----------|
| 全部 A 股 | 5,479 只 | `query.find_by_name()` |
| 沪深300 | 300 只 | `w.wset("sectorconstituent", "...windcode=000300.SH")` |
| 中证500 | 500 只 | `w.wset("sectorconstituent", "...windcode=000905.SH")` |
| 申万三级行业 | 259 个 | `query.search_industry()` |

### 技术实现

```python
from WindPy import w

# 连接 Wind
w.start()

# 查询全部A股
result = w.wset("sectorconstituent", "date=20260209;sectorid=a001010100000000")

# 查询截面数据
err, df = w.wss(code, "sec_name,close,pe_ttm", "tradeDate=20260209", usedf=True)

# 查询时间序列
err, df = w.wsd(code, "close", "-30D", "", "PriceAdj=F", usedf=True)
```

### 应用场景

1. **快速查找代码**
   ```python
   query.find_by_name("宁德时代")  # → 300750.SZ
   ```

2. **批量获取信息**
   ```python
   codes = ["600519.SH", "000858.SZ", "000568.SZ"]
   for code in codes:
       info = query.get_info(code)
       print(f"{info['name']}: PE={info['pe_ttm']}")
   ```

3. **生成查询代码**
   ```python
   code = query.find_by_name("茅台")[0]['code']
   print(f"err, df = w.wsd('{code}', 'close', '-30D', '', 'PriceAdj=F', usedf=True)")
   ```

### 相关文档

- `SKILL.md` - 使用说明
- `scripts/windpy_stock_query.py` - 查询工具源码
- `references/wsd-function-reference.md` - WSD 函数完整参考

---

**更新日期**: 2026-02-09  
**Commit**: 3cab55f  
**PR**: https://github.com/hanlinlibham/skills/pull/4
