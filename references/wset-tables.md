# w.wset() 报表名与参数参考

> **状态：占位文档，待补充**
>
> 补充方法：Wind 终端 → 代码生成器 → WSET → 左侧列出所有可用报表名
> 每个报表选中后，右侧显示可用 options 参数和返回列

---

## 已确认可用的报表

### sectorconstituent — 板块成分股

```python
err, df = w.wset("sectorconstituent",
    "date=2024-06-28;sectorid=a001010100000000", usedf=True)
```

| 参数 | 必选 | 说明 |
|------|------|------|
| date | 是 | 日期 YYYY-MM-DD |
| sectorid | 是 | 板块ID（见 sector-ids.md） |

返回列：`date, wind_code, sec_name`

---

### indexconstituent — 指数成分股

```python
err, df = w.wset("indexconstituent",
    "date=2024-06-28;windcode=000300.SH", usedf=True)
```

| 参数 | 必选 | 说明 |
|------|------|------|
| date | 是 | 日期 |
| windcode | 是 | 指数代码（如 000300.SH） |

返回列：`date, wind_code, sec_name, i_weight`（待确认权重列名）

---

### abnormalactivitiesranking — 龙虎榜

```python
err, df = w.wset("abnormalactivitiesranking",
    "startdate=2024-06-28;enddate=2024-06-28;"
    "field=trade_dt,wind_code,sec_name,close,pct_chg,netbuyamt",
    usedf=True)
```

| 参数 | 必选 | 说明 |
|------|------|------|
| startdate | 是 | 起始日期 |
| enddate | 是 | 截止日期 |
| field | 否 | 需要的字段（逗号分隔） |

返回列：`trade_dt, wind_code, sec_name, close, pct_chg, netbuyamt, ...`（待确认完整列表）

---

## 待补充的报表（从代码生成器获取）

> 以下报表名来自 WindPy.md 文档提及，需逐个在终端验证参数和返回列

### dividendproposal — 分红送转方案

```python
# TODO: 在终端验证
err, df = w.wset("dividendproposal", "year=2024", usedf=True)
```

待记录：options 参数、返回列

---

### tradingsuspend — 停牌股票

```python
# TODO: 在终端验证
err, df = w.wset("tradingsuspend",
    "startdate=2024-06-28;enddate=2024-06-28", usedf=True)
```

待记录：options 参数、返回列

---

### marginassetsandliabilities — 融资融券标的

```python
# TODO: 在终端验证
err, df = w.wset("marginassetsandliabilities",
    "date=2024-06-28;...", usedf=True)
```

待记录：options 参数、返回列

---

### etfconstituent — ETF 申赎清单

```python
# TODO: 在终端验证
err, df = w.wset("etfconstituent",
    "date=2024-06-28;windcode=510300.SH", usedf=True)
```

待记录：options 参数、返回列

---

### sharefloat — 限售解禁

```python
# TODO: 在终端验证
err, df = w.wset("sharefloat", "startdate=2024-06-28;enddate=2024-07-28", usedf=True)
```

待记录：options 参数、返回列

---

### corpaction — 公司行为事件

```python
# TODO: 在终端验证
```

待记录：全部内容

---

## 验证脚本

在 Wind 终端运行以下脚本，逐个验证并记录返回结果：

```python
from WindPy import w
w.start()

tables_to_test = [
    ("sectorconstituent", "date=2024-06-28;sectorid=a001010100000000"),
    ("indexconstituent", "date=2024-06-28;windcode=000300.SH"),
    ("abnormalactivitiesranking", "startdate=2024-06-28;enddate=2024-06-28"),
    ("dividendproposal", "year=2024"),
    ("tradingsuspend", "startdate=2024-06-28;enddate=2024-06-28"),
    ("etfconstituent", "date=2024-06-28;windcode=510300.SH"),
    # 添加更多...
]

for table, opts in tables_to_test:
    print(f"\n{'='*60}")
    print(f"报表: {table}")
    print(f"参数: {opts}")
    try:
        err, df = w.wset(table, opts, usedf=True)
        if err == 0:
            print(f"返回列: {df.columns.tolist()}")
            print(f"行数: {len(df)}")
            print(df.head(3))
        else:
            print(f"错误: {err}")
    except Exception as e:
        print(f"异常: {e}")
```
