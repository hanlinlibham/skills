---
name: windpy-sdk
description: WindPy SDK 本地调用参考手册。当用户需要编写使用 Wind 金融终端 Python API (from WindPy import w) 的代码时触发。提供完整的函数参考、字段速查、板块代码和错误处理指南。
---

# WindPy SDK 本地调用参考手册

## 快速开始

```python
from WindPy import w

# 启动连接
w.start()

# 使用数据函数
err, df = w.wsd("600519.SH", "close", "-30D", "", "PriceAdj=F", usedf=True)

# 关闭连接
w.stop()
```

## 核心数据函数

### 1. wsd() - 日级时间序列
获取日级历史数据，支持行情、估值、资金、技术指标。

```python
err, df = w.wsd(codes, fields, beginTime, endTime, options, usedf=True)
```

**参数说明**:
- `codes`: 证券代码，如 "600519.SH" 或多代码 "600519.SH,000858.SZ"
- `fields`: 字段，如 "close,open,high,low,volume,pct_chg"
- `beginTime`: 开始时间，如 "-30D", "20240101"
- `endTime`: 结束时间，如 "" 表示最新
- `options`: 选项，如 "PriceAdj=F;Period=D"

**Options 参数**:
| 参数 | 值 | 说明 |
|------|-----|------|
| PriceAdj | F/B/CP | 前复权/后复权/债券全价 |
| Period | D/W/M/Q/S/Y | 日/周/月/季/半年/年 |
| Days | Trading/Weekdays/Alldays | 交易日/工作日/日历日 |

**常用字段分类**:
- 行情: open, high, low, close, volume, amt, pct_chg
- 估值: pe_ttm, pb_lf, ps_ttm, mkt_cap_ard
- 资金: mfd_inflow_xl, mfd_inflow_l, mfd_inflow_m, mfd_inflow_s
- 技术指标: macd, kdj_k, kdj_d, rsi, ma5, ma10, ma20
- 财务: roe_diluted, roa, gross_margin, eps_ttm

**示例**:
```python
# 获取茅台近30天日线（前复权）
err, df = w.wsd("600519.SH", "close,open,high,low,volume,pct_chg", 
                "-30D", "", "PriceAdj=F", usedf=True)

# 获取多只股票的估值指标
err, df = w.wsd("600519.SH,000858.SZ", "pe_ttm,pb_lf,mkt_cap_ard", 
                "", "", "", usedf=True)

# 获取资金流向
err, df = w.wsd("600519.SH", "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s",
                "-30D", "", "", usedf=True)
```

详见: `references/wsd-function-reference.md`

---

### 2. wss() - 截面快照
获取某个时间点的截面数据。

```python
err, df = w.wss(codes, fields, options, usedf=True)
```

**示例**:
```python
# 获取多股票当前估值
err, df = w.wss("600519.SH,000858.SZ", "pe_ttm,pb_lf,mkt_cap_ard", 
                "tradeDate=20241231", usedf=True)
```

---

### 3. wset() - 报表数据集
获取板块成分、指数成分等报表数据。

```python
result = w.wset(tableName, options)
```

**常用 TableName**:
| TableName | 功能 | Options 示例 |
|-----------|------|--------------|
| sectorconstituent | 板块成分股 | date=20241231;sectorid=a39901011i000000 |
| indexconstituent | 指数成分股 | date=20241231;windcode=000300.SH |
| etfconstituent | ETF成分 | date=20241231;windcode=510050.SH |

**常用 SectorID**:
| 板块 | SectorID |
|------|----------|
| 全部A股 | a001010100000000 |
| 申万三级行业 | a39901011i000000 |

**示例**:
```python
# 获取申万三级行业列表
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
codes = result.Data[1]   # 行业代码
names = result.Data[2]   # 行业名称

# 获取沪深300成分股
result = w.wset("sectorconstituent", "date=20241231;windcode=000300.SH")

# 获取全部A股
result = w.wset("sectorconstituent", "date=20241231;sectorid=a001010100000000")
```

详见: `references/wset-tables.md`

---

### 4. 其他函数

| 函数 | 功能 | 说明 |
|------|------|------|
| wsi() | 分钟数据 | 1/5/15/30/60分钟K线 |
| wst() | Tick逐笔 | 逐笔成交数据 |
| wsq() | 实时行情 | 实时快照 |
| wsee() | 板块截面 | 板块截面数据 |
| tdays() | 交易日历 | 获取交易日序列 |
| edb() | 宏观经济 | EDB指标数据 |

详见各函数的参考文档。

---

## A股代码查询

### 查询方法

```python
from WindPy import w
w.start()

# 1. 根据名称模糊查询
result = w.wset("sectorconstituent", "date=20241231;sectorid=a001010100000000")
for i in range(len(result.Data[2])):
    if "茅台" in result.Data[2][i]:
        print(f"{result.Data[1][i]} - {result.Data[2][i]}")

# 2. 根据代码查询名称
err, df = w.wss("600519.SH", "sec_name", "tradeDate=20241231", usedf=True)
print(df.iloc[0]['SEC_NAME'])  # 贵州茅台

# 3. 获取最新价格
err, df = w.wsd("600519.SH", "close", "", "", "", usedf=True)
print(df.iloc[-1]['CLOSE'])

w.stop()
```

### 常用查询场景

**场景1: 查找股票代码**
```python
# 在全部A股中搜索
result = w.wset("sectorconstituent", "date=20241231;sectorid=a001010100000000")
# 遍历 result.Data[2] (名称) 匹配关键字
```

**场景2: 获取指数成分股**
```python
# 沪深300
result = w.wset("sectorconstituent", "date=20241231;windcode=000300.SH")

# 中证500
result = w.wset("sectorconstituent", "date=20241231;windcode=000905.SH")
```

**场景3: 获取行业分类**
```python
# 申万三级行业（259个）
result = w.wset("sectorconstituent", "date=20241231;sectorid=a39901011i000000")
```

详见专门文档: `references/sw3-industries-guide.md`

---

## 参考文档索引

| 文档 | 内容 |
|------|------|
| `references/wsd-function-reference.md` | WSD 函数完整参数手册 |
| `references/sw3-industries-guide.md` | 申万三级行业使用指南 |
| `references/wset-tables.md` | WSET 报表数据集 |
| `references/field-catalog.md` | 常用字段速查 |
| `references/sectorid-catalog.md` | 板块 SectorID 列表 |
| `references/error-codes.md` | 错误码对照表 |
| `references/bond-fields.md` | 债券专用字段 |
| `references/fund-fields.md` | 基金专用字段 |
| `references/future-fields.md` | 期货专用字段 |
| `references/technical-indicators.md` | 技术指标字段 |
| `references/edb-indicators.md` | EDB 宏观经济指标 |

---

## 常用代码速查

### 常用指数代码

| 指数 | 代码 |
|------|------|
| 沪深300 | 000300.SH |
| 中证500 | 000905.SH |
| 上证50 | 000016.SH |
| 创业板指 | 399006.SZ |
| 科创50 | 000688.SH |

### 代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 上海主板 | XXXXXX.SH | 600519.SH |
| 深圳主板 | XXXXXX.SZ | 000001.SZ |
| 创业板 | XXXXXX.SZ | 300750.SZ |
| 科创板 | XXXXXX.SH | 688001.SH |
| 北交所 | XXXXXX.BJ | 430047.BJ |
| 指数 | XXXXXX.SH/SZ | 000300.SH |
| 申万行业 | XXXXXX.SI | 850111.SI |

---

## 错误处理

```python
err, df = w.wsd("600519.SH", "close", "-30D", "", "", usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error code: {err}")
    # 常见错误:
    # -40522005: 代码错误
    # -40522006: 字段错误
    # -40522007: 时间错误
```

详见: `references/error-codes.md`
