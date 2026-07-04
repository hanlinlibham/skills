# WindPy 外汇专用字段参考

外汇数据通过 `w.wsd()`（时间序列）和 `w.wss()`（截面快照）获取，代码后缀为 `.FX`。

## 主要货币对代码

### G10 货币

| 代码 | 名称 | 说明 |
|------|------|------|
| `USDCNY.FX` | 美元兑人民币 | 在岸人民币 |
| `USDCNH.FX` | 美元兑离岸人民币 | 离岸CNH |
| `EURUSD.FX` | 欧元兑美元 | |
| `USDJPY.FX` | 美元兑日元 | |
| `GBPUSD.FX` | 英镑兑美元 | |
| `AUDUSD.FX` | 澳元兑美元 | |
| `NZDUSD.FX` | 新西兰元兑美元 | |
| `USDCHF.FX` | 美元兑瑞郎 | |
| `USDCAD.FX` | 美元兑加元 | |

### 亚太货币

| 代码 | 名称 | 说明 |
|------|------|------|
| `USDHKD.FX` | 美元兑港元 | 联系汇率 |
| `USDSGD.FX` | 美元兑新加坡元 | |
| `USDKRW.FX` | 美元兑韩元 | |
| `USDTWD.FX` | 美元兑新台币 | |

### 交叉汇率

| 代码 | 名称 | 说明 |
|------|------|------|
| `EURGBP.FX` | 欧元兑英镑 | |
| `EURJPY.FX` | 欧元兑日元 | |

### 银行间市场

| 代码 | 名称 | 说明 |
|------|------|------|
| `USDCNY.IB` | 美元兑人民币(CFETS) | 银行间外汇市场 |

## 行情字段

| 字段 | 含义 | 函数 |
|------|------|------|
| `close` | 收盘价 | wsd/wss |
| `open` | 开盘价 | wsd |
| `high` | 最高价 | wsd |
| `low` | 最低价 | wsd |
| `pct_chg` | 涨跌幅(%) | wsd |
| `sec_name` | 品种名称 | wss |

## 使用示例

```python
from wind_client import wsd, wss

# 美元兑人民币走势（近 30 天）
df = wsd("USDCNY.FX", "open,high,low,close", "-30D")

# 多货币对截面数据
df = wss("USDCNY.FX,EURUSD.FX,USDJPY.FX,GBPUSD.FX", "sec_name,close")

# 在岸 vs 离岸价差
df = wsd("USDCNY.FX,USDCNH.FX", "close", "-30D")
```

## 代码命名规则

- 格式：`{CCY1}{CCY2}.FX`，其中 CCY1/CCY2 为 ISO 4217 三位字母代码
- **直接标价法**（以美元为基础）：`USDCNY`、`USDJPY` — 值表示 1 美元兑多少本币
- **间接标价法**（以非美元为基础）：`EURUSD`、`GBPUSD` — 值表示 1 单位非美货币兑多少美元
- 银行间市场用 `.IB` 后缀（如 `USDCNY.IB`）

## 汇率 EDB 指标

| EDB代码 | 指标名称 | 频率 |
|---------|----------|------|
| `M0000271` | 美元指数(DXY) | 日 |
| `M0290205` | 人民币汇率中间价:美元 | 日 |
| `M0290208` | 人民币汇率中间价:欧元 | 日 |
| `M0290211` | 人民币汇率中间价:日元 | 日 |

## 注意事项

1. **在岸 vs 离岸：** USDCNY 为在岸价（央行管理），USDCNH 为离岸价（市场化），价差反映市场情绪
2. **CFETS：** `.IB` 后缀为中国外汇交易中心（CFETS）报价
3. **交易时间：** 外汇市场 24 小时运行，Wind 数据以纽约收盘为截止
4. **`.CF` 后缀不可用：** 测试中 `USDCNY.CF`、`USDCNH.CF` 返回空数据
