---
name: windpy-sdk
description: WindPy SDK 本地调用参考手册。当用户需要编写使用 Wind 金融终端 Python API (from WindPy import w) 的代码时触发。提供完整的函数参考、字段速查、板块代码和错误处理指南。
---

# WindPy SDK 本地调用参考手册

## 触发条件

当用户需要：
- 编写使用 `from WindPy import w` 的 Python 代码
- 查询 Wind API 某个函数的用法、参数或字段
- 获取 A 股/债券/基金/期货/宏观数据的 Wind 代码
- 调试 WindPy SDK 调用错误
- 查找板块 SectorID、指数代码、字段名称

## 连接管理

```python
from WindPy import w

w.start()              # 启动连接，默认超时120秒
w.start(waitTime=60)   # 自定义超时60秒
w.isconnected()        # 返回 True/False
w.stop()               # 停止连接
```

## 核心数据函数速查

### w.wsd() — 日级时间序列

```python
err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)
```

**常用示例**:
```python
# 获取沪深300近30天收盘价
err, df = w.wsd("000300.SH", "close", "-30D", "", "", usedf=True)

# 获取多个指数的日涨跌幅（前复权）
err, df = w.wsd("000300.SH,000905.SH", "pct_chg", "20240101", "20241231", "PriceAdj=F", usedf=True)

# 获取资金流向
err, df = w.wsd("600519.SH", "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s", "-30D", "", "", usedf=True)
```

### w.wss() — 截面快照

```python
err, df = w.wss(codes, fields, options, usedf=True)
```

**常用示例**:
```python
# 获取多品种多指标快照
err, df = w.wss("600519.SH,000858.SZ", "sec_name,close,pct_chg,pe_ttm", "tradeDate=20241231", usedf=True)
```

### w.wset() — 报表数据集

```python
result = w.wset(tableName, options)
```

**常用示例**:
```python
# 获取申万三级行业列表（259个）
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
codes = result.Data[1]
names = result.Data[2]

# 获取沪深300成分股
result = w.wset("sectorconstituent", "date=20241231;windcode=000300.SH")

# 获取全部A股
result = w.wset("sectorconstituent", "date=20241231;sectorid=a001010100000000")
```

## 参考文档索引

- `references/field-catalog.md` — 常用字段速查（行情/财务/资金流向/估值）
- `references/sectorid-catalog.md` — 板块 SectorID 完整列表（指数/行业/概念）
- `references/error-codes.md` — 错误码完整列表及解决方案
- `references/wset-tables.md` — wset 报表数据集（板块成分/ETF清单/分红/股东户数）
- `references/bond-fields.md` — 债券专用字段（YTM/久期/凸性/评级/中债估值）
- `references/fund-fields.md` — 基金专用字段（NAV/基金类型/基金经理/ETF实时&日频涨跌幅）
- `references/future-fields.md` — 期货专用字段（持仓量/结算价/保证金）
- `references/technical-indicators.md` — 技术指标字段（MACD/RSI/KDJ/BOLL/CCI/WR）
- `references/edb-indicators.md` — EDB 宏观经济指标代码（GDP/CPI/PMI/M2/利率）

## 常用代码速查

### 板块 SectorID

| 板块 | SectorID |
|------|----------|
| 全部A股 | `a001010100000000` |
| 申万三级行业 | `a39901011i000000` |
| 沪深300 | `1000000098000000` |
| 中证500 | `1000000099000000` |

### 常用指数代码

| 指数 | 代码 |
|------|------|
| 沪深300 | `000300.SH` |
| 中证500 | `000905.SH` |
| 创业板指 | `399006.SZ` |
| 标普500 | `SPX.GI` |

### 常用字段

| 类别 | 字段 |
|------|------|
| 行情 | `open, high, low, close, volume, amt, pct_chg` |
| 估值 | `pe_ttm, pb_lf, mkt_cap_ard` |
| 资金 | `mfd_inflow_xl, mfd_inflow_l, mfd_inflow_m, mfd_inflow_s` |

## 完整文档

详见 `references/` 目录下的各专题文档。
