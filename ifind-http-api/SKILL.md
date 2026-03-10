---
name: ifind-http-api
description: |
  iFinD HTTP API 调用参考手册。当用户需要编写使用同花顺 iFinD HTTP API 获取金融数据的代码时使用此技能。
  覆盖全部 18 个 API 端点的 URL、参数、指标和示例。支持股票、基金、债券、期货、期权、宏观数据。
  触发词：ifind、iFinD、同花顺API、同花顺数据、quantapi。
---

# iFinD HTTP API 调用参考手册

本技能提供同花顺 iFinD HTTP API 的完整函数参考，用于编写通过 HTTP 请求获取金融数据的 Python 代码。

**API 基础地址：** `https://quantapi.51ifind.com/api/v1/`

## 触发条件

当用户需要：
- 编写调用 iFinD HTTP API 的 Python 代码
- 查询同花顺 API 某个接口的用法、参数或指标
- 获取 A 股/债券/基金/期货/宏观/期权数据（通过 HTTP 方式）
- 调试 iFinD API 调用错误
- 从 WindPy 迁移到 iFinD HTTP API

## 认证机制

iFinD 使用两层 token 鉴权：`refresh_token`（长期）→ `access_token`（短期，7天有效）。

### 获取 access_token

```python
import requests
import json

REFRESH_TOKEN = "your_refresh_token_here"

# 获取当前有效的 access_token
resp = requests.post(
    "https://quantapi.51ifind.com/api/v1/get_access_token",
    headers={"Content-Type": "application/json", "refresh_token": REFRESH_TOKEN}
)
access_token = json.loads(resp.content)["data"]["access_token"]

# 或获取一个新的 access_token（会使所有旧 token 失效）
resp = requests.post(
    "https://quantapi.51ifind.com/api/v1/update_access_token",
    headers={"Content-Type": "application/json", "refresh_token": REFRESH_TOKEN}
)
access_token = json.loads(resp.content)["data"]["access_token"]
```

**注意：**
- `access_token` 7 天有效，最多绑定 20 个 IP
- `refresh_token` 与账号有效期一致，更新后所有旧 token 全部失效
- 每天 token 请求次数有限制

### 通用请求模板

```python
import requests

BASE_URL = "https://quantapi.51ifind.com/api/v1"
ACCESS_TOKEN = "your_access_token"
HEADERS = {"Content-Type": "application/json", "access_token": ACCESS_TOKEN}

def ifind_request(endpoint, params):
    """通用 iFinD API 请求"""
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.post(url, json=params, headers=HEADERS)
    data = resp.json()
    if data.get("errorcode") != 0:
        raise Exception(f"iFinD Error {data['errorcode']}: {data.get('errmsg', '')}")
    return data
```

### 通用返回结构

所有数据接口返回 JSON，包含以下字段：

| 字段 | 说明 |
|------|------|
| errorcode | 0=成功，其他为错误码 |
| errmsg | 错误信息（errorcode 非 0 时） |
| tables | 数据结构体，含 thscode 和 table |
| datatype | 指标格式 |
| perf | 请求耗时（ms） |
| dataVol | 消耗数据量 |

---

## 核心数据接口

### 1. basic_data_service — 基础数据（截面）

获取多品种多指标的截面数据（对应 WindPy 的 `w.wss()`）。

**URL:** `https://quantapi.51ifind.com/api/v1/basic_data_service`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 半角逗号分隔的代码 | `"300033.SZ,600030.SH"` |
| indipara | 是 | 指标数组，每项含 indicator 和 indiparams | 见下方 |

**indipara 结构：** indicator 为指标英文名，indiparams 为该指标的用户参数。推荐使用超级命令生成。

```python
# 获取 ROE 和平均 ROE
params = {
    "codes": "300033.SZ,600030.SH",
    "indipara": [
        {"indicator": "ths_roe_stock", "indiparams": ["20241231"]},
        {"indicator": "ths_roe_avg_by_ths_stock", "indiparams": ["20241231"]}
    ]
}
data = ifind_request("basic_data_service", params)
```

---

### 2. date_sequence — 日期序列

获取多品种多指标的历史时间序列（对应 WindPy 的 `w.wsd()` + 自定义指标）。

**URL:** `https://quantapi.51ifind.com/api/v1/date_sequence`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 半角逗号分隔的代码 | `"300033.SZ,600030.SH"` |
| startdate | 是 | 开始日期 | `"2023-01-01"` |
| enddate | 是 | 结束日期 | `"2024-12-31"` |
| functionpara | 否 | 功能参数 | 见下方 |
| indipara | 是 | 指标数组 | 同 basic_data_service |

**functionpara 说明：**

| 名称 | key | 值 | 默认 |
|------|-----|------|------|
| 时间周期 | Interval | D-日 W-周 M-月 Q-季 S-半年 Y-年 | D |
| 日期类型 | Days | Tradedays-交易日 Alldays-日历日 | Tradedays |
| 非交易间隔处理 | Fill | Previous-沿用前值 Blank-空值 | Previous |

```python
# 获取归母所有者权益合计和定期报告实际披露日期
params = {
    "codes": "300033.SZ,600030.SH",
    "startdate": "20230101",
    "enddate": "20241231",
    "functionpara": {"Days": "Alldays", "Fill": "Blank", "Interval": "Y"},
    "indipara": [
        {"indicator": "ths_total_equity_atoopc_stock", "indiparams": ["", "100"]},
        {"indicator": "ths_regular_report_actual_dd_stock", "indiparams": [""]}
    ]
}
data = ifind_request("date_sequence", params)
```

---

### 3. cmd_history_quotation — 历史行情

获取日/周/月级别的 OHLCV 等历史行情数据（对应 WindPy 的 `w.wsd()` 行情部分）。

**URL:** `https://quantapi.51ifind.com/api/v1/cmd_history_quotation`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 代码 | `"300033.SZ,600030.SH"` |
| indicators | 是 | 半角逗号分隔指标 | `"preClose,open,high,low,close"` |
| startdate | 是 | 开始日期 | `"2024-01-01"` |
| enddate | 是 | 结束日期 | `"2025-01-01"` |
| functionpara | 否 | 功能参数 | 见下方 |

**indicators 常用指标（股票）：**
`preClose`(前收盘价), `open`(开盘), `high`(最高), `low`(最低), `close`(收盘), `avgPrice`(均价), `change`(涨跌), `changeRatio`(涨跌幅), `volume`(成交量), `amount`(成交额), `turnoverRatio`(换手率), `totalShares`(总股本), `totalCapital`(总市值), `floatSharesOfAShares`(A股流通股本), `floatCapitalOfAShares`(A股流通市值), `pe_ttm`(市盈率TTM), `pe`(PE), `pb`(PB), `ps`(PS), `pcf`(PCF)

**indicators 特殊品种：**
- 基金: `netAssetValue`(单位净值), `adjustedNAV`(复权净值), `accumulatedNAV`(累计净值)
- 指数: `floatCapital`(流通市值), `pe_ttm_index`(PE TTM)
- 债券: `yieldMaturity`(到期收益率), `remainingTerm`(剩余期限), `modifiedDuration`(修正久期)
- 期货: `openInterest`(持仓量), `settlement`(结算价)

**functionpara 说明：**

| 名称 | key | 值 | 默认 |
|------|-----|------|------|
| 时间周期 | Interval | D W M Q S Y（返回周期汇总统计值） | D |
| 抽样周期 | SampleInterval | D W M Q S Y（返回周期最后一个交易日数据） | D |
| 复权方式 | CPS | 1-不复权 2-前复权(分红再投) 3-后复权(分红再投) 4-全流通前复权 5-全流通后复权 6-前复权(现金分红) 7-后复权(现金分红) | 1 |
| 报价类型 | PriceType | 1-全价 2-净价（仅债券） | 1 |
| 非交易间隔 | Fill | Previous Blank 具体数值 Omit | Previous |
| 复权基点 | BaseDate | `"YYYY-MM-DD"` | 后复权按上市日，前复权按最新日 |
| 货币 | Currency | MHB-美元 GHB-港元 RMB-人民币 YSHB-原始货币 | YSHB |

```python
# 获取周线数据（后复权）
params = {
    "codes": "300033.SZ,600030.SH",
    "indicators": "open,close,volume",
    "startdate": "2024-08-25",
    "enddate": "2025-08-25",
    "functionpara": {"Interval": "W", "CPS": "3", "Currency": "RMB", "Fill": "Blank"}
}
data = ifind_request("cmd_history_quotation", params)
```

---

### 4. high_frequency — 高频序列（分钟级）

获取 1-60 分钟级别的 K 线数据（对应 WindPy 的 `w.wsi()`）。

**URL:** `https://quantapi.51ifind.com/api/v1/high_frequency`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 代码 | `"300033.SZ,600030.SH"` |
| indicators | 是 | 指标 | `"open,high,low,close"` |
| starttime | 是 | 开始时间 | `"2024-01-01 09:15:00"` |
| endtime | 是 | 结束时间 | `"2024-01-01 15:15:00"` |
| functionpara | 否 | 功能参数 | 见下方 |

**indicators 通用指标：**
`open`, `high`, `low`, `close`, `avgPrice`, `volume`, `amount`, `change`, `changeRatio`, `turnoverRatio`, `sellVolume`(内盘), `buyVolume`(外盘)

**indicators 技术指标（需同时在 functionpara.calculate 中设置参数）：**
MACD, KDJ, RSI, BOLL, MA, EXPMA, CCI, ATR, OBV, MFI 等 50+ 种技术指标。

选择技术指标时，需在 functionpara 中添加 `calculate` 字段：

```python
# 分钟数据含技术指标
params = {
    "codes": "300033.SZ,600030.SH",
    "indicators": "open,high,SI,MACD,DPTB,OBV,KDJ",
    "starttime": "2018-01-01 09:15:00",
    "endtime": "2018-01-01 09:50:00",
    "functionpara": {
        "Interval": "1",    # 1分钟
        "Fill": "Original",
        "calculate": {
            "SI": "",
            "MACD": "12,26,9,MACD",     # 短周期,长周期,周期,{DIFF/DEA/MACD}
            "DPTB": "7,000001",          # 周期,大盘代码
            "OBV": "OBV_XZ",            # {OBV/OBV_XZ}
            "KDJ": "9,3,3,K"            # 周期,周期1,周期2,{K/D/J}
        }
    }
}
data = ifind_request("high_frequency", params)
```

**functionpara 说明：**

| 名称 | key | 值 | 默认 |
|------|-----|------|------|
| 时间区间开始 | Limitstart | 限定每个交易日数据的开始时间 | - |
| 时间区间结束 | Limitend | 限定每个交易日数据的截止时间 | - |
| 时间周期 | Interval | 1(1分钟) 3 5 10 15 30 60 | 1 |
| 非交易间隔处理 | Fill | Previous Blank 具体数值 Original(不处理) | Original |
| 复权方式 | CPS | -backward1(后复权分红) -backward(前复权交易所) -forward3(后复权交易所) 等 no(不复权) | no |
| 时间截格式 | Timeformat | BeiJingTime LocalTime | BeiJingTime |
| 复权基点 | BaseDate | `"YYYY-MM-DD"` | - |

**常用技术指标参数格式：** 参见 `references/technical-indicators.md`

---

### 5. real_time_quotation — 实时行情

获取当前实时行情快照（对应 WindPy 的 `w.wsq()`）。

**URL:** `https://quantapi.51ifind.com/api/v1/real_time_quotation`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 代码 | `"300033.SZ,600000.SH"` |
| indicators | 是 | 指标 | `"open,high,low,latest"` |
| functionpara | 否 | 仅含债券报价方式 | - |

**indicators 通用指标：**
`tradeDate`(交易日期), `tradeTime`(交易时间), `preClose`(前收盘价), `open`, `high`, `low`, `latest`(最新价), `latestAmount`(现额), `latestVolume`(现量), `avgPrice`(均价), `change`(涨跌), `changeRatio`(涨跌幅), `upperLimit`(涨停价), `downLimit`(跌停价), `amount`(成交额), `volume`(成交量), `turnoverRatio`(换手率), `sellVolume`(内盘), `buyVolume`(外盘)

**股票扩展指标：**
- 十档买卖: `bid1`~`bid10`, `ask1`~`ask10`, `bidSize1`~`bidSize10`, `askSize1`~`askSize10`
- 资金流向: `mainInflow`(主力流入), `mainOutflow`(主力流出), `mainNetInflow`(主力净流入), `retailNetInflow`(散户净流入), `largeNetInflow`(超大单净流入), `bigNetInflow`(大单净流入), `middleNetInflow`(中单净流入), `smallNetInflow`(小单净流入)
- 主动被动大中小单成交量/金额: `activeBuyLargeAmt`, `activeSellLargeAmt`, `activeBuyLargeVol` 等
- 涨跌幅: `chg_1min`(1分钟), `chg_5d`(5日), `chg_10d`, `chg_20d`, `chg_60d`, `chg_120d`, `chg_250d`, `chg_year`(年初至今)
- 其他: `pe_ttm`, `pbr_lf`(PB LF), `mv`(流通市值), `totalCapital`(总市值), `suspensionFlag`(停牌标志), `riseDayCount`(连涨天数)
- 盘后: `post_lastest`(盘后最新成交价), `post_volume`(盘后成交量)

**指数专用：** `riseCount`(上涨家数), `fallCount`(下跌家数), `upLimitCount`(涨停家数), `downLimitCount`(跌停家数)

**期权专用：** `impliedVolatility`(隐含波动率), `delta`, `gamma`, `vega`, `theta`, `rho`

```python
# 实时行情
params = {"codes": "300033.SZ,600000.SH", "indicators": "open,high,low,latest,changeRatio,volume"}
data = ifind_request("real_time_quotation", params)
```

---

### 6. snap_shot — 日内快照

获取指定时间段内的盘口快照数据（对应 WindPy 的 `w.wst()`）。

**URL:** `https://quantapi.51ifind.com/api/v1/snap_shot`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 代码 | `"300033.SZ,600030.SH"` |
| indicators | 是 | 指标 | `"open,high,latest"` |
| starttime | 是 | 开始时间 | `"2025-08-25 09:30:00"` |
| endtime | 是 | 结束时间 | `"2025-08-25 15:00:00"` |

**注意：** startDate 和 endDate 必须为同一天（-4209 错误）。

**indicators：**
`tradeDate`, `tradeTime`, `preClose`, `open`, `high`, `low`, `latest`(现价), `amt`(成交额), `vol`(成交量), `amount`(累计成交额), `volume`(累计成交量), `tradeNum`(成交次数), 十档买卖盘 `bid1`~`bid10`, `ask1`~`ask10`, `bidSize1`~`bidSize10`, `askSize1`~`askSize10`, `avgBuyPrice`(均买价), `avgSellPrice`(均卖价), `dealDirection`(成交方向,仅当日), `dealtype`(成交性质,期货/期权)

```python
params = {
    "codes": "300033.SZ,600030.SH",
    "indicators": "open,high,latest,volume",
    "starttime": "2025-08-25 09:30:00",
    "endtime": "2025-08-25 15:00:00"
}
data = ifind_request("snap_shot", params)
```

---

### 7. edb_service — 经济数据库 (EDB)

获取宏观经济指标数据（对应 WindPy 的 `w.edb()`）。

**URL:** `https://quantapi.51ifind.com/api/v1/edb_service`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| indicators | 是 | 半角逗号分隔的 EDB 指标代码 | `"M001620326,M002822183"` |
| startdate | 是 | 开始日期 | `"2018-01-01"` |
| enddate | 是 | 结束日期 | `"2024-12-31"` |
| functionpara | 否 | 时间筛选 | 见下方 |

**functionpara 说明：**
- `startrtime` — 更新起始时间（不勾选时省略）
- `end rtime` — 更新结束时间（不勾选时省略）

```python
params = {
    "indicators": "M001620326,M002822183",
    "startdate": "2018-01-01",
    "enddate": "2024-12-31",
    "functionpara": {
        "startrtime": "2018-01-01 09:15:00",
        "end rtime": "2018-01-01 10:15:00"
    }
}
data = ifind_request("edb_service", params)
```

**注意：** 宏观指标代码推荐使用超级命令终端或网页版查询。

---

### 8. data_pool — 专题报表

获取专题报表数据（对应 WindPy 的 `w.wset()`）。

**URL:** `https://quantapi.51ifind.com/api/v1/data_pool`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| reportname | 是 | 报表编码 | `"p03341"` |
| functionpara | 是 | 报表筛选参数 | 见下方 |
| outputpara | 是 | 输出字段控制（Y/N） | `"p03341_f001:Y,p03341_f002:Y"` |

```python
# 查询 REITs 项目一览报表
params = {
    "reportname": "p03341",
    "functionpara": {
        "sdate": "20210421",
        "edate": "20211119",
        "xmzt": "全部",
        "jcsslx": "全部",
        "jys": "全部"
    },
    "outputpara": "p03341_f001:Y,p03341_f002:Y"
}
data = ifind_request("data_pool", params)
```

**注意：** 报表过多，functionpara 和 outputpara 推荐使用超级命令查看生成。

---

### 9. portfolio_manage — 组合管理

统一 URL，通过 `func` 字段区分功能。

**URL:** `https://quantapi.51ifind.com/api/v1/portfolio_manage`

#### (1) 组合新建 — func: "newportf"

```python
params = {
    "func": "newportf",
    "name": "股债联动",
    "group": 11580,
    "performbm": {"code": "000300.SH", "name": "沪深300"},
    "supbm": {"code": "", "name": ""},
    "tday": "国内交易所",
    "curency": "CNY",
    "finacrate": "",
    "secrate": "",
    "info": "股票与债券结合的策略组合"
}
data = ifind_request("portfolio_manage", params)
```

#### (2) 组合导入 — func: "importf"

```python
params = {
    "func": "importf",
    "name": "股债策略组合",
    "portfid": 161390,
    "content": [
        ["交易日期", "证券代码", "业务类型", "数量", "价格", "成交金额", "费用", "证券类型"],
        ["2020-03-30", "CNY", "现金存入", "", "", 10000000, "", ""],
        ["2020-04-01", "600000.SH", "买入", 100, 10.09, 1009, 5.225, "A股"]
    ]
}
data = ifind_request("portfolio_manage", params)
```

#### (3) 现金存取 — func: "cashacs"

```python
params = {
    "func": "cashacs",
    "name": "组合名称",
    "portfid": 161390,
    "functionpara": {"acesscls": "101", "amount": "10000"}  # 101=存入, 102=取出
}
```

#### (4) 普通交易 — func: "deal"

```python
params = {
    "func": "deal",
    "name": "股债策略组合",
    "portfid": 161390,
    "functionpara": {
        "thscode": "300033",
        "direct": "buy",       # buy/sell
        "codeName": "同花顺",
        "marketCode": "212100",
        "securityType": "001001",
        "price": 78.7,
        "volume": 100,
        "currency": "CNY",
        "fee": "0",
        "feep": 0,
        "rate": "1.00",
        "bonus": ""
    }
}
```

#### (5) 交易流水 — func: "query_exchange_records"

最大时间区间 7 天。indicators: `date,code,name,dealPrice,dealNumber,realPrice,businessName,serviceCharge,type,currency,exchangeRate,marketName,importType`

#### (6) 组合监控 — func: "query_overview"

indicators: `category,thscode,stockName,newPrice,increase,increseRate,number,marketValue,weight,todayProfit,floatProfit,floatProfitRate,totalProfit,totalProfitRate,interestIncome,realizedProfit,positionPrice,positionCost,breakevenPrice,serviceCharge,moneyType,currentPrice,updateTime`

#### (7) 持仓分析 — func: "query_positions"

indicators: `categoryName,securityName,thsCode,weight,marketPrice,cost,wavepl,cumpl,price,increaseRate,amount,costPrice`
functionpara: `{"penetrate": "false"}` (false=不穿透, true=穿透)

#### (8) 绩效指标 — func: "query_perform"

functionpara: `{"pfclass": "utnv", "cycle": "day"}` (pfclass: perform/nasset/utnv; cycle: rquota/day/week/month/halfYear/year)

#### (9) 风险指标 — func: "query_risk_profits"

indicators: `alpha,yield,annual_yield,sharpe_ratio,information_ratio,sortino_ratio,jensen_alpha,treynor_ratio,win_ratio,positiveMonth,beta,annual_volatility,tracking_error,downside_risk,value_at_risk,max_drawdown,maxdrawdownRepairNum,maxdownNum,max_cont_decline,rSquare`
functionpara: `{"cycle": "day", "benchmark": "000300"}`

---

### 10. smart_stock_picking — 智能选股

**URL:** `https://quantapi.51ifind.com/api/v1/smart_stock_picking`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| searchstring | 是 | 搜索关键词 | `"个股热度"` |
| searchtype | 是 | 搜索类别 | `"stock"` |

```python
params = {"searchstring": "个股热度", "searchtype": "stock"}
data = ifind_request("smart_stock_picking", params)
```

---

### 11. fund_valuation — 基金实时估值（分钟）

**URL:** `https://quantapi.51ifind.com/api/v1/fund_valuation`

| 参数 | 必须 | 说明 |
|------|------|------|
| codes | 是 | 基金代码如 `"000001.OF,000003.OF"` |
| functionpara | 是 | `onlyLastest`(1=仅最新/0=区间), `beginTime`, `endTime` |
| outputpara | 是 | `"changeRatioValuation:Y,realTimeValuation:Y,Deviation30TDays:Y,rank:Y"` |

outputpara 字段: `changeRatioValuation`(估值涨跌幅), `realTimeValuation`(基金实时估值), `Deviation30TDays`(30交易日估算平均偏差%), `rank`(最新估值涨跌幅排名)

```python
params = {
    "codes": "000001.OF,000003.OF",
    "functionpara": {"onlyLastest": "0", "beginTime": "2021-08-24 09:15:00", "endTime": "2021-08-24 15:15:00"},
    "outputpara": "date:Y,th scode:Y,security_name:Y,weight:Y"
}
data = ifind_request("fund_valuation", params)
```

---

### 12. final_fund_valuation — 基金实时估值（日）

**URL:** `https://quantapi.51ifind.com/api/v1/final_fund_valuation`

| 参数 | 必须 | 说明 |
|------|------|------|
| codes | 是 | 基金代码（分号分隔）如 `"000001.OF;000003.OF"` |
| functionpara | 是 | `beginDate`, `endDate` |
| outputpara | 是 | `"finalValuation:Y,netAssetValue:Y,deviation:Y"` |

outputpara 字段: `finalValuation`(日最终估值), `netAssetValue`(日实际净值), `deviation`(估值相对净值偏差率%)

```python
params = {
    "codes": "000001.OF;000003.OF",
    "functionpara": {"beginDate": "2021-06-01", "endDate": "2021-09-02"},
    "outputpara": "finalValuation:Y,netAssetValue:Y,deviation:Y"
}
data = ifind_request("final_fund_valuation", params)
```

---

### 13. get_trade_dates — 日期查询

查询区间日期或区间日期数目。

**URL:** `https://quantapi.51ifind.com/api/v1/get_trade_dates`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| marketcode | 是 | 交易所代码 | `"212001"` |
| functionpara | 是 | 查询参数 | 见下方 |
| startdate | 是 | 开始日期 | `"2025-09-10"` |
| enddate | 是 | 结束日期 | `"2025-09-10"` |

**functionpara 必填字段：**
- `mode` — `"1"` 查询区间日期, `"2"` 查询区间日期数目
- `dateType` — `"0"` 交易日, `"1"` 日历日
- `period` — `"D"` 日, `"W"` 周, `"M"` 月, `"Q"` 季, `"S"` 半年, `"Y"` 年
- `dateFormat` — `"0"` YYYY-MM-DD, `"1"` YYYY/MM/DD, `"2"` YYYYMMDD
- `periodnum` — 时间周期偏移（正数第1日 `"1"`, 倒数第1日 `"-1"`）

**常用交易所代码：**

| 代码 | 交易所 | 代码 | 交易所 |
|------|--------|------|--------|
| 212001 | 上交所 | 212100 | 深交所 |
| 212200 | 港交所 | 212010 | 美国纽约证券交易所 |
| 212011 | 美国NASDAQ | 212020001 | 中金所 |
| 212020002 | 上海黄金交易所 | 212020003 | 郑商所 |
| 212020004 | 大商所 | 212004 | 银行间债券市场 |
| 212020008 | 上期所 | 212012 | 英国伦敦证券交易所 |

```python
# 查询上交所 2025-09-10 的交易日
params = {
    "marketcode": "212001",
    "functionpara": {"mode": "1", "dateType": "0", "period": "D", "dateFormat": "0"},
    "startdate": "2025-09-10",
    "enddate": "2025-09-10"
}
data = ifind_request("get_trade_dates", params)
```

---

### 14. get_trade_dates（日期偏移模式）

从基准日期前推/后退 N 个周期。

| 参数 | 必须 | 说明 |
|------|------|------|
| marketcode | 是 | 交易所代码 |
| functionpara | 是 | 含 dateType, period, offset, dateFormat, output |
| startdate | 是 | 基准日期 |

**functionpara 说明：**
- `dateType` — `"0"` 交易日, `"1"` 日历日
- `period` — 周期
- `offset` — `"-5"` 前推5个, `"5"` 后退5个
- `dateFormat` — 日期格式
- `output` — `"sequencedate"` 所有日期, `"singledate"` 单个日期

```python
# 前推1天
params = {
    "marketcode": "212001",
    "functionpara": {
        "dateType": "0", "period": "D", "offset": "-1",
        "dateFormat": "0", "output": "sequencedate"
    },
    "startdate": "2025-09-10"
}
data = ifind_request("get_trade_dates", params)
```

---

### 15. get_data_volume — 数据量查询

无需参数，仅需传入 token 访问。

**URL:** `https://quantapi.51ifind.com/api/v1/get_data_volume`

---

### 16. get_error_message — 错误信息查询

**URL:** `https://quantapi.51ifind.com/api/v1/get_error_message`

```python
params = {"errorcode": -1}
data = ifind_request("get_error_message", params)
```

---

### 17. get_thscode — 证券代码转换

将行情代码或证券简称转为同花顺代码。

**URL:** `https://quantapi.51ifind.com/api/v1/get_thscode`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| seccode/secname | 是 | 行情代码或简称 | `"300033"` |
| mode | 是 | `"seccode"` 或 `"secname"` | `"seccode"` |
| sectype | 是 | 证券类型 | `"001"` |
| market | 是 | 市场 | `"212001"` |
| tradestatus | 是 | 交易状态 0/1/2 | `"0"` |
| isexact | 是 | 精确匹配 0/1 | `"0"` |

```python
params = {
    "seccode": "300033",
    "functionpara": {
        "mode": "seccode", "sectype": "", "market": "",
        "tradestatus": "0", "isexact": "0"
    }
}
data = ifind_request("get_thscode", params)
```

---

### 18. report_query — 公告查询

**URL:** `https://quantapi.51ifind.com/api/v1/report_query`

| 参数 | 必须 | 说明 | 示例 |
|------|------|------|------|
| codes | 是 | 证券代码（或空+mode参数） | `"300033.SZ,600000.SH"` |
| functionpara | 否 | 筛选参数 | 见下方 |
| outputpara | 是 | 输出字段 | `"reportDate:Y,thscode:Y,reportTitle:Y,pdfURL:Y"` |

**functionpara 说明：**
- `mode` — `"allAStock"` 全部A股, `"allBond"` 全部债券（codes 为空时必填）
- `reportType` — `"903"` 全部, `"901"` 等按类型筛选
- `beginrDate` / `endrDate` — 公告日期范围
- `begincTime` / `endcTime` — 发布时间范围
- `keyWord` — 标题关键词

**outputpara 字段：**
`reportDate`(公告日期), `thscode`(证券代码), `secName`(证券简称), `ctime`(发布时间), `reportTitle`(公告标题), `pdfURL`(公告链接), `seq`(唯一标号)

```python
params = {
    "codes": "300033.SZ,600000.SH",
    "functionpara": {"reportType": "901"},
    "beginrDate": "2024-09-10",
    "endrDate": "2025-09-10",
    "outputpara": "reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y"
}
data = ifind_request("report_query", params)
```

---

## 完整示例：A 股日线数据获取

```python
import requests
import json
import pandas as pd

# === 配置 ===
REFRESH_TOKEN = "your_refresh_token"
BASE_URL = "https://quantapi.51ifind.com/api/v1"

# === 获取 token ===
resp = requests.post(
    f"{BASE_URL}/get_access_token",
    headers={"Content-Type": "application/json", "refresh_token": REFRESH_TOKEN}
)
ACCESS_TOKEN = json.loads(resp.content)["data"]["access_token"]
HEADERS = {"Content-Type": "application/json", "access_token": ACCESS_TOKEN}

def ifind_request(endpoint, params):
    resp = requests.post(f"{BASE_URL}/{endpoint}", json=params, headers=HEADERS)
    return resp.json()

# === 获取历史行情 ===
result = ifind_request("cmd_history_quotation", {
    "codes": "600519.SH,000858.SZ",
    "indicators": "open,high,low,close,volume,amount,changeRatio",
    "startdate": "2024-01-01",
    "enddate": "2024-12-31",
    "functionpara": {"Interval": "D", "CPS": "3", "Fill": "Previous"}
})

# === 解析为 DataFrame ===
if result["errorcode"] == 0:
    for table in result["tables"]:
        code = table["thscode"]
        df = pd.DataFrame(table["table"])
        print(f"\n{code}:")
        print(df.head())
```

---

## 与 WindPy SDK 的对应关系

| WindPy 函数 | iFinD HTTP API 端点 | 说明 |
|-------------|---------------------|------|
| `w.wss()` | `basic_data_service` | 截面快照 |
| `w.wsd()` | `date_sequence` / `cmd_history_quotation` | 时间序列/历史行情 |
| `w.wsi()` | `high_frequency` | 分钟 K 线 |
| `w.wst()` | `snap_shot` | 日内快照 |
| `w.wsq()` | `real_time_quotation` | 实时行情 |
| `w.edb()` | `edb_service` | 宏观经济数据 |
| `w.wset()` | `data_pool` | 专题报表 |
| `w.tdays()` / `w.tdaysoffset()` | `get_trade_dates` | 日期查询/偏移 |

---

## 错误码速查

| 错误码 | 含义 |
|--------|------|
| 0 | 成功 |
| -1010 | token 已失效 |
| -1301 | refresh_token 无效 |
| -1302 | access_token 无效 |
| -1303 | access_token 绑定超过 20 个 IP |
| -4001 | 数据为空 |
| -4203 | 请求格式错误 |
| -4204 | 错误的时间格式 |
| -4205 | 开始时间不能大于结束时间 |
| -4206 | 含有错误的同花顺代码 |
| -4209 | snap_shot 起始结束日期要求同一天 |
| -4301 | 本周基础数据提取超过 500 万条 |
| -4302 | 本周报价数据提取超过 1.5 亿条 |
| -4303 | 本周 EDB 数据提取超过 500 万条 |
| -4400 | 每分钟最多 600 条请求 |
| -4308 | 请求区间不能超过一个月 |

**完整错误码见** `references/error-codes.md`

---

## 养老金产品数据

养老金产品使用 `.YLJ` 后缀，通过 `date_sequence` 接口获取数据。

**代码格式：** `{管理人前缀}{产品类型}{编号}.YLJ`

| 类型字母 | 类型 | 数量 |
|---------|------|------|
| A | 权益型 | ~183 只 |
| B | 混合型 | ~134 只 |
| C | 债券型（含 Ca/Cb/Cc/Cf/Cg/Ch 子类） | ~345 只 |
| D | 货币/现金管理型 | ~29 只 |

**管理人前缀：** 00(社保), 02(博时), 05(大成), 07(工银瑞信), 10(海富通), 11(华夏), 15(嘉实), 18(南方), 20(鹏华), 48(易方达), 51(银华), CJ(长江养老), CL(长城人寿), HT(华泰), JX(建信养老金), PA(平安养老), RB(人保), TP(太平养老), TZ(泰康资产), XH(新华养老), ZJ(中金), ZX(中信)

**常用指标：** `ths_unit_nv_fund`(单位净值), `ths_fund_short_name_fund`(基金简称), `ths_fund_establishment_date_fund`(成立日), `ths_rsbfl_pension`(人社部分类, indiparams=["100"]), `ths_invest_manager_current_obcm`(投资经理)

```python
# 获取权益型养老金产品净值
params = {
    "codes": "00A001.YLJ,02A001.YLJ,05A001.YLJ,07A003.YLJ,10A001.YLJ",
    "startdate": "2026-02-10",
    "enddate": "2026-03-10",
    "indipara": [
        {"indicator": "ths_unit_nv_fund", "indiparams": [""]},
        {"indicator": "ths_fund_short_name_fund", "indiparams": [""]},
        {"indicator": "ths_rsbfl_pension", "indiparams": ["100"]}
    ]
}
data = ifind_request("date_sequence", params)
```

**完整代码清单、管理人对照表、THS_DS 命令转换规则见** `references/pension-fund-products.md`

### 养老金产品名称检索

产品代码与名称的对应关系存储在 SQLite 数据库 `data/pension_products.db` 中，提供全文搜索能力。

**使用查询脚本：**
```bash
# 按名称搜索
python scripts/query_pension.py search "平安稳健"

# 按代码查找
python scripts/query_pension.py code PAA001.YLJ

# 按管理人筛选
python scripts/query_pension.py manager PA

# 按产品类型筛选（A=权益/B=混合/C=债券/D=货币，或子类 Ca/Cb/Cf/Cg）
python scripts/query_pension.py type A

# 组合筛选
python scripts/query_pension.py filter --manager PA --type A

# 统计概览
python scripts/query_pension.py stats

# 导出 CSV
python scripts/query_pension.py export output.csv
```

**在代码中使用查询模块：**
```python
from scripts.query_pension import search, get_by_code, get_by_manager, filter_products

# 全文搜索
results = search("data/pension_products.db", "增值")

# 精确查找
product = get_by_code("data/pension_products.db", "PAA001.YLJ")
print(product["name"])  # 产品名称

# 组合筛选
products = filter_products("data/pension_products.db", manager="PA", ptype="A")
codes = ",".join(p["code"] for p in products)  # 拼接代码串用于 API 调用
```

**构建/更新数据库：**
```bash
export IFIND_REFRESH_TOKEN="your_token"
python scripts/build_pension_db.py --source ifind/基础信息数据.md
```

数据库 Schema 见 `references/pension-db-schema.md`

---

## 注意事项

1. **请求方法** 全部为 POST，Content-Type 为 `application/json`
2. **Headers** 必须包含 `access_token`（数据请求）或 `refresh_token`（token 操作）
3. **日期格式** 支持 `YYYYMMDD`、`YYYY-MM-DD`、`YYYY/MM/DD` 三种
4. **返回编码** 统一 unicode
5. **请求参数** 需统一处理为 urlencode，支持 gzip/deflate 压缩
6. **数据限制** 每分钟 600 请求，各类数据有周/月配额
7. **snap_shot** 的起止日期必须为同一天
8. **指标名称** 推荐使用 Windows 超级命令终端或网页版生成
9. **代码格式** 与 Wind 一致：`600519.SH`(沪), `000001.SZ`(深), `000001.OF`(基金)
