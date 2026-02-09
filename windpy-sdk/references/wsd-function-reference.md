# WSD 函数参考手册

## 概述

**WSD** (Wind Daily Series) 用于获取日级时间序列数据，支持行情、估值、资金流向、技术指标等多类数据。

```python
err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| codes | str | 是 | 证券代码，如 "600519.SH" 或多代码 "600519.SH,000858.SZ" |
| fields | str | 是 | 数据字段，多个用逗号分隔 |
| beginTime | str | 是 | 开始时间，如 "-30D" 或 "20240101" |
| endTime | str | 否 | 结束时间，空字符串表示最新 |
| options | str | 否 | 选项参数，如 "PriceAdj=F" |

## 常用字段

### 行情数据
`open`, `high`, `low`, `close`, `volume`, `amt`, `pct_chg`

### 估值指标
`pe_ttm`, `pb_lf`, `ps_ttm`, `mkt_cap_ard`

### 资金流向
`mfd_inflow_xl`, `mfd_inflow_l`, `mfd_inflow_m`, `mfd_inflow_s`

### 技术指标
`macd`, `kdj_k`, `kdj_d`, `rsi`, `ma5`, `ma10`, `ma20`

### 财务数据
`roe_diluted`, `roa`, `gross_margin`, `eps_ttm`

## Options 参数

| 参数 | 值 | 说明 |
|------|-----|------|
| PriceAdj | F | 前复权 |
| PriceAdj | B | 后复权 |
| Period | D | 日线 |
| Period | W | 周线 |
| Period | M | 月线 |

## 时间格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 相对日期 | "-30D" | 30天前 |
| 相对日期 | "-3M" | 3个月前 |
| 绝对日期 | "20240101" | 具体日期 |

## 使用示例

### 示例1: 获取单股票日级数据
```python
from WindPy import w
w.start()

err, df = w.wsd("600519.SH", "close,open,high,low,volume,pct_chg",
                "-30D", "", "PriceAdj=F", usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error: {err}")

w.stop()
```

### 示例2: 获取多股票估值
```python
codes = "600519.SH,000858.SZ,000568.SZ"
fields = "pe_ttm,pb_lf,mkt_cap_ard"

err, df = w.wsd(codes, fields, "", "", "", usedf=True)
```

### 示例3: 获取资金流向
```python
codes = "600519.SH"
fields = "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s"

err, df = w.wsd(codes, fields, "-30D", "", "", usedf=True)

if err == 0:
    df['total_inflow'] = df.sum(axis=1)
    print(df)
```

### 示例4: 获取技术指标
```python
codes = "600519.SH"
fields = "macd,kdj_k,kdj_d,rsi"

err, df = w.wsd(codes, fields, "-60D", "", "", usedf=True)
```

### 示例5: 获取周线数据
```python
err, df = w.wsd("600519.SH", "close,pct_chg",
                "-1Y", "", "Period=W;PriceAdj=F", usedf=True)
```

## 查询可用字段

```python
# 查询 WSD 可用字段列表
result = w.wset("wsdfield", "")
for i in range(len(result.Data[0])):
    print(f"{result.Data[0][i]}: {result.Data[1][i]}")
```

或通过 Wind 代码生成器的 **IND** 按钮查看字段列表。

## 相关文档

- `field-catalog.md` - 字段速查表
- `sw3-industries-guide.md` - 申万三级行业使用指南
- `error-codes.md` - 错误码对照
