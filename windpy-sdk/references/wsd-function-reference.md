# WSD 函数完整参数手册

## 1. WSD 函数概述

**功能**: 获取日级时间序列数据

**WindPy API**:
```python
err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| codes | str | 是 | 证券代码，多个用逗号分隔 |
| fields | str | 是 | 数据字段，多个用逗号分隔 |
| beginTime | str | 是 | 开始时间 |
| endTime | str | 否 | 结束时间（空表示最新） |
| options | str | 否 | 选项参数 |

---

## 2. 参数详解

### 2.1 codes - 证券代码

**格式**: `代码.交易所`

| 代码示例 | 说明 |
|----------|------|
| 600519.SH | 贵州茅台（上海） |
| 000858.SZ | 五粮液（深圳） |
| 000300.SH | 沪深300指数 |
| 000905.SH | 中证500指数 |
| 510050.SH | 上证50ETF |
| 159915.SZ | 创业板ETF |

**申万三级行业代码** (部分示例):
| 代码 | 行业名称 |
|------|----------|
| 850111.SI | 种子(申万) |
| 850113.SI | 其他种植业(申万) |
| 850122.SI | 水产养殖(申万) |
| 850142.SI | 畜禽饲料(申万) |
| 850322.SI | 氯碱(申万) |
| 850323.SI | 无机盐(申万) |
| ... | ... |
| 859951.SI | 电视广播Ⅲ(申万) |

**获取全部申万三级行业**:
```python
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
```

---

### 2.2 fields - 数据字段

#### 2.2.1 行情数据字段

| 字段 | 中文名 | 说明 |
|------|--------|------|
| open | 开盘价 | 当日开盘价 |
| high | 最高价 | 当日最高价 |
| low | 最低价 | 当日最低价 |
| close | 收盘价 | 当日收盘价 |
| volume | 成交量 | 当日成交量（股） |
| amt | 成交额 | 当日成交额（元） |
| pct_chg | 涨跌幅 | (close-pre_close)/pre_close*100 |
| change | 涨跌额 | close-pre_close |
| pre_close | 昨收价 | 昨日收盘价 |
| vwap | 均价 | 成交额/成交量 |

#### 2.2.2 估值指标字段

| 字段 | 中文名 | 说明 |
|------|--------|------|
| pe_ttm | 市盈率(TTM) | 总市值/过去12个月净利润 |
| pb_lf | 市净率(LF) | 总市值/最近报告期净资产 |
| ps_ttm | 市销率(TTM) | 总市值/过去12个月营业收入 |
| pcf_ocf_ttm | 市现率(TTM) | 总市值/过去12个月经营现金流 |
| mkt_cap_ard | 总市值 | 收盘价*总股本 |
| mkt_cap_float | 流通市值 | 收盘价*流通股本 |
| ev | 企业价值 | 市值+负债-现金 |

#### 2.2.3 资金流向字段

| 字段 | 中文名 | 说明 |
|------|--------|------|
| mfd_inflow_xl | 超大单净流入 | 单笔>100万股 |
| mfd_inflow_l | 大单净流入 | 单笔20-100万股 |
| mfd_inflow_m | 中单净流入 | 单笔4-20万股 |
| mfd_inflow_s | 小单净流入 | 单笔<4万股 |
| mfd_inflow | 主力净流入 | 超大单+大单 |
| mfd_inflow_open | 开盘资金净流入 | 开盘30分钟 |
| mfd_inflow_close | 尾盘资金净流入 | 收盘前30分钟 |

#### 2.2.4 技术指标字段

| 字段 | 中文名 | 说明 |
|------|--------|------|
| macd | MACD | 异同移动平均线 |
| macd_signal | MACD信号线 | |
| macd_hist | MACD柱状图 | |
| rsi | RSI | 相对强弱指标 |
| kdj_k | KDJ-K | |
| kdj_d | KDJ-D | |
| kdj_j | KDJ-J | |
| boll_up | 布林上轨 | |
| boll_mid | 布林中轨 | |
| boll_down | 布林下轨 | |
| ma5 | 5日均线 | |
| ma10 | 10日均线 | |
| ma20 | 20日均线 | |
| ma60 | 60日均线 | |

#### 2.2.5 财务数据字段

| 字段 | 中文名 | 说明 |
|------|--------|------|
| roe_diluted | 净资产收益率(摊薄) | 净利润/期末净资产 |
| roe_avg | 净资产收益率(平均) | 净利润/平均净资产 |
| roa | 总资产收益率 | 净利润/总资产 |
| gross_margin | 毛利率 | (收入-成本)/收入 |
| net_profit_margin | 净利率 | 净利润/营业收入 |
| eps_ttm | 每股收益(TTM) | |
| bps | 每股净资产 | |
| revenue_ps | 每股营业收入 | |
| cf_ps | 每股现金流 | |

---

### 2.3 beginTime / endTime - 时间参数

**时间格式支持**:

| 格式 | 示例 | 说明 |
|------|------|------|
| 绝对日期 | "20240101" | 具体日期 |
| 相对日期 | "-30D" | 30天前 |
| 相对日期 | "-3M" | 3个月前 |
| 相对日期 | "-1Y" | 1年前 |
| 自然语言 | "ED-1M" | 上月末 |
| 自然语言 | "SD+1M" | 下月初 |

**常用时间参数**:

| 参数 | 说明 |
|------|------|
| "" | 空字符串表示最新/今天 |
| "-30D" | 近30天 |
| "-90D" | 近90天 |
| "-1M" | 近1个月 |
| "-3M" | 近3个月 |
| "-6M" | 近6个月 |
| "-1Y" | 近1年 |
| "20240101" | 2024年1月1日 |
| "20241231" | 2024年12月31日 |
| "ED-1Y" | 去年末 |
| "SD-1M" | 上月开始 |

---

### 2.4 options - 选项参数

#### 2.4.1 复权方式 (PriceAdj)

| 值 | 说明 |
|-----|------|
| F | 前复权（默认） |
| B | 后复权 |
| CP | 债券全价 |

#### 2.4.2 周期 (Period)

| 值 | 说明 |
|-----|------|
| D | 日线（默认） |
| W | 周线 |
| M | 月线 |
| Q | 季报 |
| S | 半年报 |
| Y | 年报 |

#### 2.4.3 日期类型 (Days)

| 值 | 说明 |
|-----|------|
| Trading | 交易日（默认） |
| Weekdays | 工作日 |
| Alldays | 日历日 |

#### 2.4.4 填充方式 (Fill)

| 值 | 说明 |
|-----|------|
| Previous | 沿用前值 |
| Blank | 返回空值 |

#### 2.4.5 交易日历 (TradingCalendar)

| 值 | 说明 |
|-----|------|
| SSE | 上交所（默认） |
| SZSE | 深交所 |
| HKEX | 港交所 |
| NYSE | 纽交所 |

---

## 3. Options 参数组合示例

### 常用组合

| 场景 | Options | 说明 |
|------|---------|------|
| 股票前复权日线 | "PriceAdj=F;Period=D" | 默认 |
| 股票后复权日线 | "PriceAdj=B;Period=D" | |
| 周线数据 | "Period=W" | |
| 月线数据 | "Period=M" | |
| 债券全价 | "PriceAdj=CP" | |
| 日历日 | "Days=Alldays" | |

---

## 4. 完整示例代码

### 示例 1: 获取单股票日级数据
```python
from WindPy import w
import pandas as pd

w.start()

# 获取贵州茅台近30天日线数据（前复权）
codes = "600519.SH"
fields = "open,high,low,close,volume,amt,pct_chg"
beginTime = "-30D"
endTime = ""
options = "PriceAdj=F"

err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)

if err == 0:
    print(df)
    # 保存到Excel
    # df.to_excel("maotai_30days.xlsx")
else:
    print(f"Error: {err}")

w.stop()
```

### 示例 2: 获取多股票估值指标
```python
from WindPy import w

w.start()

# 获取多只股票当前估值
codes = "600519.SH,000858.SZ,000568.SZ"
fields = "pe_ttm,pb_lf,ps_ttm,mkt_cap_ard"
beginTime = ""
endTime = ""
options = ""

err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error: {err}")

w.stop()
```

### 示例 3: 获取资金流向数据
```python
from WindPy import w

w.start()

# 获取资金流向
codes = "600519.SH"
fields = "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s"
beginTime = "-30D"
endTime = ""
options = ""

err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)

if err == 0:
    # 计算总净流入
    df['total_inflow'] = df.sum(axis=1)
    print(df)
else:
    print(f"Error: {err}")

w.stop()
```

### 示例 4: 获取技术指标
```python
from WindPy import w

w.start()

# 获取技术指标
codes = "600519.SH"
fields = "macd,macd_signal,macd_hist,kdj_k,kdj_d,rsi"
beginTime = "-60D"
endTime = ""
options = ""

err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error: {err}")

w.stop()
```

### 示例 5: 获取财务指标
```python
from WindPy import w

w.start()

# 获取财务指标
codes = "600519.SH"
fields = "roe_diluted,roa,gross_margin,net_profit_margin,eps_ttm"
beginTime = "-1Y"
endTime = ""
options = "Period=Q"  # 季报数据

err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error: {err}")

w.stop()
```

---

## 5. 查询 Wind 字段的方法

### 5.1 通过 IND 按钮（代码生成器）
在 Wind 代码生成器中点击 **IND** 按钮，可以浏览所有可用字段。

### 5.2 通过 wset 查询字段列表
```python
# 查询 WSD 可用字段
result = w.wset("wsdfield", "")
if result.ErrorCode == 0:
    for i, field in enumerate(result.Data[0][:20]):  # 前20个
        print(f"{field}: {result.Data[1][i]}")
```

### 5.3 通过 Wind 终端帮助
在 Wind 终端中：
1. 打开 **函数向导**
2. 选择 **WSD** 函数
3. 查看 **字段列表**

---

## 6. 常见问题

### Q1: 如何获取全部申万三级行业代码？
```python
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
```

### Q2: 如何获取指数成分股？
```python
result = w.wset("sectorconstituent", "date=20241231;windcode=000300.SH")
```

### Q3: 如何处理复权？
- 前复权: `options="PriceAdj=F"`
- 后复权: `options="PriceAdj=B"`
- 不复权: 不加 PriceAdj 参数

### Q4: 时间格式支持哪些？
- 绝对日期: "20240101"
- 相对日期: "-30D", "-3M", "-1Y"
- 自然语言: "ED-1M" (上月末), "SD+1M" (下月初)

---

## 7. 相关文档

- `field-catalog.md` - 字段速查表
- `sectorid-catalog.md` - 板块代码列表
- `error-codes.md` - 错误码对照表
- `wset-tables.md` - WSET 报表数据集

---

**文档版本**: 1.0  
**更新日期**: 2026-02-09  
**基于**: Wind 代码生成器分析 + WindPy API 文档
