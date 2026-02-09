# WindPy Options 参数速查表

## 常用 Options 参数

### 价格调整

| 参数 | 值 | 说明 |
|------|-----|------|
| PriceAdj | F | 前复权 |
| PriceAdj | B | 后复权 |
| PriceAdj | CP | 债券全价 |

### 周期设置

| 参数 | 值 | 说明 |
|------|-----|------|
| Period | D | 日线（默认） |
| Period | W | 周线 |
| Period | M | 月线 |
| Period | Q | 季报 |
| Period | S | 半年报 |
| Period | Y | 年报 |

### 日期类型

| 参数 | 值 | 说明 |
|------|-----|------|
| Days | Trading | 交易日（默认） |
| Days | Weekdays | 工作日 |
| Days | Alldays | 日历日 |

### 填充方式

| 参数 | 值 | 说明 |
|------|-----|------|
| Fill | Previous | 沿用前值 |
| Fill | Blank | 返回空值 |

### 交易日历

| 参数 | 值 | 说明 |
|------|-----|------|
| TradingCalendar | SSE | 上交所（默认） |
| TradingCalendar | SZSE | 深交所 |
| TradingCalendar | HKEX | 港交所 |
| TradingCalendar | NYSE | 纽交所 |

## 常用组合

### 股票日线（前复权）
```
PriceAdj=F;Period=D;Days=Trading
```

### 债券数据（全价）
```
PriceAdj=CP
```

### 周度数据
```
Period=W;Days=Trading
```

## 财务数据 Options

| 参数 | 说明 |
|------|------|
| rptDate=20231231 | 指定报告期 |
| rptType=408001000 | 合并报表 |
| year=2024 | 指定年份（业绩预告） |

## 截面数据 Options

| 参数 | 说明 |
|------|------|
| tradeDate=20241231 | 指定交易日 |
| currencyType=CNY | 币种 |

## 板块成分 Options

| 参数 | 示例 | 说明 |
|------|------|------|
| date | date=20241231 | 指定日期 |
| sectorid | sectorid=a39901011i000000 | 板块ID |
| windcode | windcode=000300.SH | 指数代码 |
