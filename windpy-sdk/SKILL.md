---
name: windpy-sdk
description: WindPy SDK 本地调用参考手册。当用户需要编写使用 Wind 金融终端 Python API (from WindPy import w) 的代码时触发。覆盖全部数据函数的签名、参数、返回值和示例，以及常用板块代码和字段速查。
---

# WindPy SDK 本地调用参考手册

## 触发条件

当用户需要：
- 编写使用 `from WindPy import w` 的 Python 代码
- 查询 Wind API 某个函数的用法、参数或字段
- 获取 A 股/债券/基金/期货/宏观数据的 Wind 代码
- 调试 WindPy SDK 调用错误

## 快速开始

```python
from WindPy import w

# 连接
w.start()

# 获取数据
err, df = w.wsd("000300.SH", "close", "-30D", "", "", usedf=True)

# 断开
w.stop()
```

## 核心数据函数

### w.wsd() — 日级时间序列

```python
w.wsd(codes, fields, beginTime, endTime, options, usedf=True)
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| codes | str/list | 是 | 证券代码。多品种时 fields 只能单个 |
| fields | str/list | 是 | 指标。如 `"close,pct_chg,volume"` |
| beginTime | str/datetime | 否 | 起始日期。支持 `"2024-01-01"`, `"-30D"`, `"IPO"` |
| endTime | str/datetime | 否 | 截止日期。默认当前日期 |
| options | str | 否 | 参数字符串 |

**常用 options**:
- `PriceAdj=F` 前复权 / `B` 后复权
- `Period=D` 日 / `W` 周 / `M` 月
- `Days=Trading` 交易日(默认)

**返回值**: `(ErrorCode, DataFrame)` 当 `usedf=True`

```python
# 获取沪深300近30天收盘价
err, df = w.wsd("000300.SH", "close", "-30D", "", "", usedf=True)

# 获取多个指数的日涨跌幅
err, df = w.wsd(
    "000300.SH,000905.SH", 
    "pct_chg", 
    "20240101", "20241231", 
    "", usedf=True
)
```

### w.wss() — 截面快照

```python
w.wss(codes, fields, options, usedf=True)
```

```python
# 获取多品种多指标快照
err, df = w.wss(
    "600519.SH,000858.SZ",
    "sec_name,close,pct_chg,pe_ttm",
    "tradeDate=20241231", usedf=True
)
```

### w.wset() — 报表数据集

获取板块成分、指数成分等。

```python
# 获取申万三级行业列表（259个）
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
codes = result.Data[1]  # 行业代码
names = result.Data[2]  # 行业名称

# 获取沪深300成分股
result = w.wset("sectorconstituent", "date=20241231;windcode=000300.SH")

# 获取全部A股
result = w.wset("sectorconstituent", "date=20241231;sectorid=a001010100000000")
```

## 常用板块 SectorID

详见 `references/sector-ids.md`

| 板块 | SectorID | 说明 |
|------|----------|------|
| 全部A股 | `a001010100000000` | 沪深两市全部A股 |
| 申万三级行业 | `a39901011i000000` | 259个三级行业 |
| 沪深300 | `1000000098000000` | 沪深300成分 |
| 中证500 | `1000000099000000` | 中证500成分 |
| ETF板块 | `a002010300000000` | 全部ETF |

## 常用字段速查

详见 `references/field-catalog.md`

| 类别 | 常用字段 |
|------|---------|
| 行情 | `open, high, low, close, pre_close, volume, amt, pct_chg` |
| 估值 | `pe_ttm, pb_lf, ps_ttm, mkt_cap_ard` |
| 财务 | `roe_ttm, roa_ttm, grossprofit_margin, eps_ttm` |
| 资金 | `mfd_inflow_xl, mfd_inflow_l, mfd_inflow_m, mfd_inflow_s` |

## 常用指数代码

| 指数 | 代码 |
|------|------|
| 沪深300 | `000300.SH` |
| 中证500 | `000905.SH` |
| 上证50 | `000016.SH` |
| 创业板指 | `399006.SZ` |
| 科创50 | `000688.SH` |
| 标普500 | `SPX.GI` |
| 纳斯达克 | `IXIC.GI` |
| 恒生指数 | `HSI.HI` |

## 常用商品期货代码

| 品种 | 代码 |
|------|------|
| 黄金 | `AU00.SHF` |
| 白银 | `AG00.SHF` |
| 铜 | `CU00.SHF` |
| 原油 | `SC00.INE` |

## 示例脚本

见 `scripts/windpy-examples.py`

## 参考文档

- `references/field-catalog.md` - 字段速查手册
- `references/sector-ids.md` - 板块SectorID完整列表
- `references/error-codes.md` - 错误码对照表
- `references/wset-tables.md` - wset报表数据集
