# WindPy 期权专用字段参考

期权数据通过 `wset()`（合约查询）、`wsd()`（时间序列）、`wss()`（截面快照）、`wsq()`（实时行情）获取。

## 合约查询（wset）

使用 `optioncontractbasicinfo` 表查询在交易期权合约：

```python
from wind_client import wset

# 50ETF 期权 — 在交易合约
df = wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=trading")

# 300ETF 期权 — 在交易合约
df = wset("optioncontractbasicinfo", "exchange=sse;windcode=510300.SH;status=trading")
```

### 返回字段

| 字段 | 含义 | 示例值 |
|------|------|--------|
| `wind_code` | Wind代码 | 10010173 |
| `trade_code` | 交易代码 | 510050C2603A03600 |
| `sec_name` | 合约名称 | 50ETF购3月3507A |
| `option_mark_code` | 标的代码 | 510050.SH |
| `option_type` | 期权类型 | ETF期权 |
| `call_or_put` | 认购/认沽 | 认购 / 认沽 |
| `exercise_mode` | 行权方式 | 欧式 |
| `exercise_price` | 行权价 | 3.507 |
| `contract_unit` | 合约单位 | 10265 |
| `limit_month` | 到期月份 | 2026-03 |
| `listed_date` | 上市日期 | 2025-10-10 |
| `expire_date` | 到期日 | 2026-03-25 |
| `exercise_date` | 行权日 | 2026-03-25 |
| `settlement_date` | 交割日 | 2026-03-26 |
| `reference_price` | 参考价 | 0.0487 |
| `settle_mode` | 交割方式 | 实物资产 |
| `contract_state` | 合约状态 | 上市 |

## 期权代码格式

- Wind代码：`10XXXXXX.SH`（注意：wss 中需要 `.SH` 后缀才能获取数据）
- 交易代码：`{标的}{C/P}{年月}{调整标记}{行权价×1000}`
  - C = 认购 (Call), P = 认沽 (Put)
  - 示例：`510050C2603A03600` = 50ETF 认购 2026年3月 A档 行权价3.600

## 期权行情字段（wss/wsd）

**重要：** wss 中期权代码必须带 `.SH` 后缀。

| 字段 | 含义 | 说明 |
|------|------|------|
| `sec_name` | 合约名称 | |
| `close` | 收盘价 | 权利金价格 |
| `open` | 开盘价 | |
| `high` | 最高价 | |
| `low` | 最低价 | |
| `volume` | 成交量 | 张 |
| `amt` | 成交额 | |
| `oi` | 持仓量 | |

## 希腊字母（Greeks）

| 字段 | 含义 | 说明 |
|------|------|------|
| `us_impliedvol` | 隐含波动率 | Implied Volatility |
| `delta` | Delta | 标的价格敏感度 |
| `gamma` | Gamma | Delta变化率 |
| `vega` | Vega | 波动率敏感度 |
| `theta` | Theta | 时间衰减 |
| `rho` | Rho | 利率敏感度 |

```python
from wind_client import wss

# 获取活跃期权的Greeks（注意 .SH 后缀）
df = wss("10010173.SH", "sec_name,close,us_impliedvol,delta,gamma,vega,theta,rho")
```

## 使用示例

```python
from wind_client import wset, wss, wsd

# 1. 查询当前可交易的50ETF期权
contracts = wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=trading")

# 2. 筛选近月认购期权
calls = contracts[contracts['call_or_put'] == '认购']
near_month = calls[calls['limit_month'] == calls['limit_month'].min()]

# 3. 获取Greeks
codes = ','.join([c + '.SH' for c in near_month['wind_code'].tolist()[:5]])
greeks = wss(codes, "sec_name,close,exercise_price,us_impliedvol,delta,gamma,vega,theta")

# 4. 期权价格时间序列
df = wsd("10010173.SH", "close,volume,oi,us_impliedvol", "-10D")
```

## 常见标的

| 标的 | 代码 | 交易所 | 说明 |
|------|------|--------|------|
| 50ETF | 510050.SH | 上交所 | 最活跃ETF期权 |
| 300ETF | 510300.SH | 上交所 | 沪市300ETF期权 |
| 创业板ETF | 159915.SZ | 深交所 | |
| 沪深300指数 | 000300.SH | 中金所 | 股指期权 |

## 注意事项

1. **代码后缀：** wset 返回的 `wind_code` 不带后缀，但 wss/wsd 中必须加 `.SH` 才能获取行情和Greeks
2. **Greeks 有效性：** 仅对在交易且有成交的合约有效，过期合约返回 None
3. **行权方式：** A股 ETF 期权均为欧式期权
4. **合约单位：** 不同标的合约单位不同（50ETF约10000张，300ETF约10000张）
5. **交割方式：** ETF期权为实物交割，股指期权为现金交割
6. **wset 参数：** `exchange=sse`(上交所) `exchange=szse`(深交所) `exchange=cfe`(中金所)
