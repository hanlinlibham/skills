---
name: windpy-sdk
description: WindPy SDK 本地调用参考手册。当用户需要编写使用 Wind 金融终端 Python API (from WindPy import w) 的代码时使用此技能。覆盖全部数据函数的签名、参数、返回值和示例。
---

# WindPy SDK 本地调用参考手册

本技能提供 Wind 金融终端 Python API (`from WindPy import w`) 的完整函数参考，用于编写直接调用 WindPy SDK 的 Python 代码。

## 触发条件

当用户需要：
- 编写使用 `from WindPy import w` 的 Python 代码
- 查询 Wind API 某个函数的用法、参数或字段
- 获取 A 股/债券/基金/期货/宏观数据的 Wind 代码
- 调试 WindPy SDK 调用错误

## 连接管理

```python
from WindPy import w

w.start()              # 启动连接，默认超时120秒
w.start(waitTime=60)   # 自定义超时60秒
w.isconnected()        # 返回 True/False
w.stop()               # 停止连接（程序退出自动调用，一般不需要）
```

**注意事项：**
- `w.start()` 不会重复启动，需改参数时先 `w.stop()` 再 `w.start()`
- Mac 版 SDK 部分财务报表字段不可用（错误码 -40520017、-40522006）

---

## 核心数据函数

### 1. w.wsd() — 日级时间序列

获取单品种多指标 或 多品种单指标 的日级时间序列数据。

```python
w.wsd(codes, fields, beginTime, endTime, options, usedf=True)
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| codes | str/list | 是 | 证券代码。多品种时 fields 只能单个 |
| fields | str/list | 是 | 指标。如 `"close,high,low,open"` |
| beginTime | str/datetime | 否 | 起始日期。支持 `"2024-01-01"`, `"20240101"`, `"-30D"`, `"IPO"` |
| endTime | str/datetime | 否 | 截止日期。默认当前日期 |
| options | str | 否 | 参数字符串，见下方 |

**常用 options：**
- `PriceAdj=F` 前复权 / `B` 后复权 / 不填=不复权
- `Period=D` 日 / `W` 周 / `M` 月 / `Q` 季 / `Y` 年
- `Days=Trading` 交易日(默认) / `Weekdays` 工作日 / `Alldays` 日历日
- `Fill=Previous` 沿用前值 / `Blank` 返回空值
- `TradingCalendar=SSE` 上交所(默认) / `SZSE` / `HKEX` / `NYSE` 等

**返回值：** `(ErrorCode, DataFrame)` 当 `usedf=True`

```python
# 单品种多指标
err, df = w.wsd("600519.SH", "open,high,low,close,volume,amt,pct_chg",
                "2024-01-01", "2024-06-30", "PriceAdj=F", usedf=True)

# 多品种单指标
err, df = w.wsd("600519.SH,000858.SZ,000001.SZ", "close",
                "-30D", "", "PriceAdj=F", usedf=True)

# 月线数据
err, df = w.wsd("600519.SH", "close,volume", "-2Y", "", "Period=M", usedf=True)

# 资金流向
err, df = w.wsd("600519.SH",
    "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s,mfd_inflow",
    "-30D", "", "", usedf=True)

# 债券数据
err, df = w.wsd("010107.SH", "ytm_b,duration,convexity,close",
                "2024-01-01", "2024-06-30", "PriceAdj=CP", usedf=True)
```

**常用 fields（行情）：** `open, high, low, close, pre_close, volume, amt, pct_chg, turn, vwap, mkt_cap_ard, pe_ttm, pb_lf`

**常用 fields（资金流向）：** `mfd_inflow_xl`(超大单), `mfd_inflow_l`(大单), `mfd_inflow_m`(中单), `mfd_inflow_s`(小单), `mfd_inflow`(主力净流入)

---

### 2. w.wss() — 截面快照

获取多品种多指标的**某一时点**截面数据。

```python
w.wss(codes, fields, options, usedf=True)
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| codes | str/list | 是 | 证券代码，支持多品种 |
| fields | str/list | 是 | 指标，支持多指标 |
| options | str | 否 | 如 `tradeDate`, `rptDate`, `rptType` 等 |

**常用 options：**
- `tradeDate=20240101` 指定交易日
- `rptDate=20231231` 指定报告期
- `rptType=408001000` 合并报表(默认) / `408004000` 合并报表(调整) / `408005000` 合并报表(更正前)
- `year=2024` 指定年份（业绩预告用）
- `currencyType=CNY` 币种

```python
# 行情快照（多品种多指标）
err, df = w.wss("600519.SH,000858.SZ",
    "sec_name,close,pct_chg,pe_ttm,pb_lf,mkt_cap_ard",
    f"tradeDate=20240628", usedf=True)

# 基本信息
err, df = w.wss("600519.SH",
    "sec_name,sec_englishname,industry_sw,industry_sw_level2,"
    "listdate,province,chairman,mkt_cap_ard,total_shares,float_a_shares",
    "", usedf=True)

# 核心财务指标
err, df = w.wss("600519.SH",
    "roe_ttm,roa_ttm,grossprofit_margin,netprofit_margin,"
    "eps_ttm,pe_ttm,pb_lf,ps_ttm,current_ratio,debttoassets,"
    "yoynetprofit,yoyrevenue",
    f"tradeDate=20240628", usedf=True)

# 利润表
err, df = w.wss("600519.SH",
    "tot_oper_rev,oper_rev,tot_oper_cost,oper_cost,"
    "oper_profit,tot_profit,net_profit_is,eps_basic,eps_diluted",
    "rptDate=20231231;rptType=408001000", usedf=True)

# 资产负债表
err, df = w.wss("600519.SH",
    "tot_assets,tot_cur_assets,cash_equivalents,inventories,"
    "tot_non_cur_assets,fix_assets,tot_liab,tot_cur_liab,"
    "st_borrow,lt_borrow,tot_equity,undist_profit",
    "rptDate=20231231;rptType=408001000", usedf=True)

# 现金流量表
err, df = w.wss("600519.SH",
    "net_cash_flows_oper_act,net_cash_flows_inv_act,"
    "net_cash_flows_fnc_act,free_cash_flow",
    "rptDate=20231231;rptType=408001000", usedf=True)

# 业绩预告
err, df = w.wss("600519.SH",
    "profitnotice_date,profitnotice_style,"
    "profitnotice_netprofitmin,profitnotice_netprofitmax,"
    "profitnotice_changemin,profitnotice_changemax,profitnotice_reason",
    f"year=2024", usedf=True)

# 业绩快报
err, df = w.wss("600519.SH",
    "expr_discdate,expr_oper_rev,expr_oper_profit,expr_tot_profit,"
    "expr_net_profit_parent_comp,expr_eps_basic,expr_roe_diluted,"
    "expr_yoy_oper_rev,expr_yoy_net_profit",
    "rptDate=20231231", usedf=True)

# 区间涨跌幅
err, df = w.wss("600519.SH,000858.SZ", "sec_name,pct_chg_per",
    "startDate=20240101;endDate=20240628", usedf=True)
```

**常用 fields 速查见** `references/field-catalog.md`

---

### 3. w.wsq() — 实时行情

获取当天实时行情快照，或订阅实时数据推送。

```python
# 快照模式
w.wsq(codes, fields, usedf=True)

# 订阅模式
w.wsq(codes, fields, func=callback_function)
w.cancelRequest(requestID)  # 取消订阅, 0=取消全部
```

```python
# 快照
err, df = w.wsq("600519.SH,000858.SZ",
    "rt_last,rt_open,rt_high,rt_low,rt_pct_chg,rt_vol,rt_amt,rt_chg",
    usedf=True)

# 订阅模式
def on_quote(indata):
    print(f"Code: {indata.Codes}, Fields: {indata.Fields}, Data: {indata.Data}")

data = w.wsq("600519.SH", "rt_last,rt_vol", func=on_quote)
# ... 等待回调 ...
w.cancelRequest(data.RequestID)  # 取消订阅
```

**实时行情 fields（rt_ 前缀）：** `rt_last`(最新价), `rt_open`, `rt_high`, `rt_low`, `rt_pre_close`, `rt_pct_chg`, `rt_chg`, `rt_vol`(成交量), `rt_amt`(成交额), `rt_last_vol`(最新成交量)

---

### 4. w.wsi() — 分钟级 K 线

获取 1-60 分钟级别的 OHLCV 数据。支持国内六大交易所近三年数据。

```python
w.wsi(codes, fields, beginTime, endTime, options, usedf=True)
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| codes | str/list | 是 | 证券代码（带后缀） |
| fields | str/list | 是 | 如 `"open,high,low,close,volume"` |
| beginTime | str/datetime | 否 | 如 `"2024-06-28 09:30:00"` |
| endTime | str/datetime | 否 | 默认当前时间 |

**options：**
- `BarSize=5` 分钟数（1-60，默认1）
- `PriceAdj=F` 前复权 / `B` 后复权 / `U` 不复权(默认)
- `Fill=Previous` 沿用前值

**限制：** 单品种近三年；多品种时 品种数×天数 ≤ 100

```python
# 5分钟K线
err, df = w.wsi("600519.SH", "open,high,low,close,volume,amt",
    "2024-06-28 09:30:00", "2024-06-28 15:00:00", "BarSize=5", usedf=True)

# 15分钟K线（最近3天）
err, df = w.wsi("600519.SH", "open,high,low,close,volume",
    "-3D 09:30:00", "", "BarSize=15", usedf=True)

# 期货分钟数据
err, df = w.wsi("IF00.CFE", "open,high,low,close",
    "2024-06-28 09:30:00", "2024-06-28 15:00:00", "BarSize=1", usedf=True)
```

---

### 5. w.wst() — Tick 逐笔数据

获取日内盘口买卖五档快照和分时成交数据。仅支持单品种，近七个交易日。

```python
w.wst(codes, fields, beginTime, endTime, options, usedf=True)
```

```python
# 逐笔成交
err, df = w.wst("600519.SH", "last,volume,amt,bid1,bsize1,ask1,asize1",
    "2024-06-28 09:30:00", "2024-06-28 11:30:00", "", usedf=True)
```

**Tick fields：** `last`(最新价), `volume`, `amt`, `bid1~bid5`(买1~5价), `bsize1~bsize5`(买1~5量), `ask1~ask5`(卖1~5价), `asize1~asize5`(卖1~5量)

---

### 6. w.wses() — 板块日级时间序列

获取板块级别的历史日序列数据（如板块平均收盘价、PE等）。

```python
w.wses(codes, fields, beginTime, endTime, options, usedf=True)
```

**注意：** 一次仅支持单指标，可多板块。

```python
# 上证A股和深证A股的平均收盘价
err, df = w.wses("a001010200000000,a001010300000000", "sec_close_avg",
    "2024-01-01", "2024-06-30", "", usedf=True)
```

**options：**
- `DynamicTime=0` 使用板块历史成分 / `1` 使用最新成分(默认)
- `Period=D` 日(默认) / `W` 周 / `M` 月

---

### 7. w.wsee() — 板块截面快照

获取多板块多指标的某一天截面数据。

```python
w.wsee(codes, fields, options, usedf=True)
```

```python
# 多板块截面对比
err, df = w.wsee("a001010200000000,a001010300000000",
    "sec_close_avg,sec_pct_chg_avg,sec_pe_ttm_median",
    "tradeDate=20240628", usedf=True)
```

---

### 8. w.wset() — 报表数据集

获取板块成分、指数成分、龙虎榜、分红送转、停复牌等报表数据。

```python
w.wset(tableName, options, usedf=True)
```

| tableName | 用途 | options 示例 |
|-----------|------|-------------|
| `sectorconstituent` | 板块成分股 | `date=2024-06-28;sectorid=a001010100000000` |
| `indexconstituent` | 指数成分股 | `date=2024-06-28;windcode=000300.SH` |
| `abnormalactivitiesranking` | 龙虎榜 | `startdate=2024-06-28;enddate=2024-06-28;field=...` |
| `dividendproposal` | 分红方案 | `year=2024` |
| `tradingsuspend` | 停牌股票 | `startdate=2024-06-28;enddate=2024-06-28` |
| `marginassetsandliabilities` | 融资融券标的 | `date=2024-06-28;sectorid=...` |
| `etfconstituent` | ETF 申赎清单 | `date=2024-06-28;windcode=510300.SH` |

```python
# 全部A股成分股
err, df = w.wset("sectorconstituent",
    "date=2024-06-28;sectorid=a001010100000000", usedf=True)
# 返回列: date, wind_code, sec_name

# 沪深300成分股
err, df = w.wset("indexconstituent",
    "date=2024-06-28;windcode=000300.SH", usedf=True)

# 申万一级行业成分股
err, df = w.wset("sectorconstituent",
    "date=2024-06-28;sectorid=a39901011g000000", usedf=True)

# 龙虎榜
err, df = w.wset("abnormalactivitiesranking",
    "startdate=2024-06-28;enddate=2024-06-28;"
    "field=trade_dt,wind_code,sec_name,close,pct_chg,netbuyamt",
    usedf=True)
```

**常用板块 sectorid：**
| 板块 | sectorid |
|------|----------|
| 全部A股 | `a001010100000000` |
| 上证A股 | `a001010200000000` |
| 深证A股 | `a001010300000000` |
| 创业板 | `1000006528000000` |
| 科创板 | `a001010l00000000` |

---

### 9. w.edb() — 宏观经济数据库

获取 Wind EDB 宏观经济数据库中的指标数据。

```python
w.edb(codes, beginTime, endTime, options, usedf=True)
```

```python
# GDP
err, df = w.edb("M5567876,M5567889", "2022-01-01", "2024-06-30",
    "Fill=Previous", usedf=True)

# CPI
err, df = w.edb("M0000612,M0000705,M0085932,M0085934", "2023-01-01", "",
    "Fill=Previous", usedf=True)

# PMI
err, df = w.edb("M0017126,M0017127,M5206730", "2023-01-01", "",
    "Fill=Previous", usedf=True)

# M2
err, df = w.edb("M0001384,M0001385,M0001391", "2023-01-01", "",
    "Fill=Previous", usedf=True)

# 利率
err, df = w.edb("M0329537,M0329538,M0017139", "2023-01-01", "",
    "Fill=Previous", usedf=True)
```

**完整 EDB 指标代码见** `references/edb-indicators.md`

---

### 10. 交易日历函数

```python
# w.tdays() — 获取日期区间内的交易日序列
data = w.tdays("2024-01-01", "2024-06-30", "")
dates = data.Data[0]  # [datetime, datetime, ...]

# w.tdaysoffset() — 获取偏移后的交易日
data = w.tdaysoffset(0)           # 最近交易日
data = w.tdaysoffset(-10)         # 前推10个交易日
data = w.tdaysoffset(-3, "2024-06-28", "Period=M")  # 前推3个月
date = data.Data[0][0]            # datetime 对象

# w.tdayscount() — 统计区间内交易日数量
data = w.tdayscount("2024-01-01", "2024-12-31", "")
count = data.Data[0][0]           # int
```

**options：**
- `Days=Trading` 交易日(默认) / `Weekdays` 工作日 / `Alldays` 日历日
- `Period=D` 天(默认) / `W` 周 / `M` 月 / `Q` 季 / `Y` 年
- `TradingCalendar=SSE` 上交所(默认) / 其他交易所代码

---

## 日期宏

WindPy 支持相对日期表达式：

| 格式 | 含义 | 示例 |
|------|------|------|
| `-5D` | 前推5个日历日 | beginTime="-5D" |
| `-10TD` | 前推10个交易日 | beginTime="-10TD" |
| `-1M` | 前推1个月 | beginTime="-1M" |
| `-2Y` | 前推2年 | beginTime="-2Y" |
| `IPO` | 上市首日 | beginTime="IPO" |
| `LYR` | 去年年报 | rptDate 参数 |
| `MRQ` | 最新一期 | rptDate 参数 |
| `RYF` | 本年初 | beginTime="RYF" |
| `LME` | 上月末 | endTime="LME" |
| `ED` | 截止日期 | 用于计算 `ED-10D` |

---

## 返回值处理

### 使用 usedf=True（推荐）

```python
err, df = w.wsd("600519.SH", "close", "-10D", "", "", usedf=True)
if err == 0:
    print(df)           # pandas DataFrame
    print(df.columns)   # ['CLOSE']
else:
    print(f"错误: {err}")
```

### 不使用 usedf（返回 WindData 对象）

```python
data = w.wsd("600519.SH", "close", "-10D", "")
if data.ErrorCode == 0:
    print(data.Codes)   # ['600519.SH']
    print(data.Fields)  # ['CLOSE']
    print(data.Times)   # [datetime, ...]
    print(data.Data)    # [[1800.0, 1810.5, ...]]
```

### 错误码说明

| 错误码 | 含义 |
|--------|------|
| 0 | 成功 |
| -40520007 | 无数据权限 |
| -40520017 | 字段不支持（Mac常见） |
| -40522006 | 参数错误 |
| -40521001 | 网络连接失败 |

---

## 常用代码模板

### 获取最近交易日

```python
from datetime import datetime

def get_latest_trade_date():
    data = w.tdaysoffset(0, datetime.now().strftime('%Y-%m-%d'), "")
    if data.ErrorCode == 0:
        return data.Data[0][0].strftime('%Y-%m-%d')
    return datetime.now().strftime('%Y-%m-%d')

def get_trade_date_offset(n):
    """前推 n 个交易日"""
    data = w.tdaysoffset(-n, datetime.now().strftime('%Y-%m-%d'), "")
    if data.ErrorCode == 0:
        return data.Data[0][0].strftime('%Y-%m-%d')
    return datetime.now().strftime('%Y-%m-%d')
```

### 批量获取板块所有股票数据

```python
trade_date = get_latest_trade_date()

# 获取成分股
data = w.wset("sectorconstituent", f"date={trade_date};sectorid=a001010100000000")
stocks = data.Data[1]  # wind_code 列表

# 获取数据
err, df = w.wss(stocks,
    "sec_name,industry_sw,close,pct_chg,pe_ttm,pb_lf,mkt_cap_ard",
    f"tradeDate={trade_date.replace('-','')}", usedf=True)
```

### 多期财务数据对比

```python
results = {}
for year in range(2019, 2024):
    err, df = w.wss("600519.SH",
        "tot_oper_rev,net_profit_is,roe_diluted,eps_basic",
        f"rptDate={year}1231;rptType=408001000", usedf=True)
    if err == 0:
        results[year] = df.iloc[0].to_dict()

import pandas as pd
summary = pd.DataFrame(results).T
```

### 相关性分析

```python
import numpy as np

err, df = w.wsd("600519.SH,000858.SZ,000001.SZ", "close",
    "-250TD", "", "PriceAdj=F", usedf=True)

if err == 0:
    returns = df.pct_change().dropna()
    corr = returns.corr()
    print(corr)
```

---

## 注意事项

1. **usedf=True** 返回 `(ErrorCode, DataFrame)`；不加返回 `WindData` 对象
2. **日期格式** 均可用 `"2024-01-01"`, `"20240101"`, `"-5D"`, datetime 对象
3. **wsd 多品种** 时 fields 只能选一个
4. **wss 一次** 只能取一个交易日/报告期，但可多品种多指标
5. **wsi** 多品种时：品种数 × 天数 ≤ 100
6. **wst** 仅支持单品种，近 7 个交易日
7. **DataFrame 列名** 自动大写：`close` → `CLOSE`, `pe_ttm` → `PE_TTM`
8. **股票代码格式**：`600519.SH`(沪), `000001.SZ`(深), `300750.SZ`(创), `688xxx.SH`(科创), `8xxxxx.BJ`(北交所)
