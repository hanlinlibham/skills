# 各函数 options 参数速查

> **状态：占位文档，待补充**
>
> 补充方法：代码生成器中选择不同函数 → 查看所有可用 options
> 每个函数右侧面板会列出完整的 options 参数

---

## w.wsd() options

| 参数 | 取值 | 默认值 | 说明 |
|------|------|--------|------|
| PriceAdj | F / B / T | 不复权 | 前复权 / 后复权 / 定点复权 |
| Period | D / W / M / Q / S / Y | D | 日 / 周 / 月 / 季 / 半年 / 年 |
| Days | Trading / Weekdays / Alldays | Trading | 交易日 / 工作日 / 日历日 |
| Fill | Previous / Blank | Blank | 沿用前值 / 返回空值 |
| Order | A / D | A | 升序 / 降序 |
| TradingCalendar | SSE / SZSE / HKEX / NYSE / ... | SSE | 交易所日历 |
| Currency | Original / CNY / USD / HKD | Original | 币种 |
| ShowBlank | 数值 | — | 自定义空值填充数字 |

**债券特有：**
| 参数 | 取值 | 说明 |
|------|------|------|
| PriceAdj | CP / DP / MP / YTM | 净价 / 全价 / 市价 / 收益率 |
| returnType | 1 | 到期收益率计算方法 |

---

## w.wss() options

| 参数 | 取值 | 说明 |
|------|------|------|
| tradeDate | YYYYMMDD | 指定交易日 |
| rptDate | YYYYMMDD | 指定报告期（财报数据） |
| rptType | 408001000 / 408004000 / 408005000 | 合并报表 / 合并调整 / 合并更正前 |
| year | YYYY | 年份（业绩预告用） |
| currencyType | CNY / USD / HKD | 币种 |
| startDate | YYYYMMDD | 区间起始日（pct_chg_per 用） |
| endDate | YYYYMMDD | 区间截止日（pct_chg_per 用） |
| annualized | 0 / 1 | 是否年化（基金收益用） |

```
TODO: 从代码生成器补充更多 options：
- 估值类参数
- 分析师预期参数
- 其他财报选项
```

---

## w.wsq() options

| 参数 | 取值 | 说明 |
|------|------|------|
| — | — | wsq 快照模式通常不需要 options |

```
TODO: 确认订阅模式是否有额外 options
```

---

## w.wsi() options

| 参数 | 取值 | 默认值 | 说明 |
|------|------|--------|------|
| BarSize | 1-60 | 1 | 分钟数 |
| PriceAdj | U / F / B | U | 不复权 / 前复权 / 后复权 |
| Fill | Previous / Blank | Blank | 空值填充 |

```
TODO: 从代码生成器确认是否有更多 options
```

---

## w.wst() options

```
TODO: 代码生成器中确认 wst 可用 options
预期较少，可能只有 Fill 参数
```

---

## w.wses() options

| 参数 | 取值 | 默认值 | 说明 |
|------|------|--------|------|
| DynamicTime | 0 / 1 | 1 | 历史成分 / 最新成分 |
| Period | D / W / M / Q / S / Y | D | 取值周期 |
| Days | Trading / Weekdays / Alldays | Trading | 日期类型 |
| Fill | Previous / Blank | Blank | 空值填充 |
| TradingCalendar | SSE / ... | SSE | 交易所日历 |

---

## w.wsee() options

| 参数 | 取值 | 说明 |
|------|------|------|
| tradeDate | YYYYMMDD | 交易日 |
| DynamicTime | 0 / 1 | 历史成分 / 最新成分 |

```
TODO: 从代码生成器补充更多 options
```

---

## w.edb() options

| 参数 | 取值 | 默认值 | 说明 |
|------|------|--------|------|
| Fill | Previous / Blank | Blank | 空值填充 |
| ShowBlank | 数值 | — | 自定义空值填充数字 |

---

## w.tdays() / w.tdaysoffset() / w.tdayscount() options

| 参数 | 取值 | 默认值 | 说明 |
|------|------|--------|------|
| Days | Trading / Weekdays / Alldays | Trading | 日期类型 |
| Period | D / W / M / Q / S / Y | D | 取值周期 |
| TradingCalendar | SSE / SZSE / HKEX / NYSE / ... | SSE | 交易所日历 |

---

## w.wset() options

> wset 的 options 因 tableName 而异，详见 `wset-tables.md`

---

## 验证脚本

```python
from WindPy import w
w.start()

# 测试不同 options 组合
# Period 参数
for period in ['D', 'W', 'M', 'Q', 'Y']:
    err, df = w.wsd("600519.SH", "close", "-1Y", "", f"Period={period}", usedf=True)
    print(f"Period={period}: {len(df)} 条数据" if err == 0 else f"Period={period}: 错误 {err}")

# PriceAdj 参数
for adj in ['', 'PriceAdj=F', 'PriceAdj=B']:
    err, df = w.wsd("600519.SH", "close", "-30D", "", adj, usedf=True)
    if err == 0:
        print(f"{adj or '不复权'}: 首值={df.iloc[0,0]}, 末值={df.iloc[-1,0]}")

# TradingCalendar 参数
for cal in ['SSE', 'SZSE', 'HKEX', 'NYSE']:
    data = w.tdays("2024-06-01", "2024-06-30", f"TradingCalendar={cal}")
    print(f"{cal}: {len(data.Data[0])} 个交易日" if data.ErrorCode == 0 else f"{cal}: 错误")
```
