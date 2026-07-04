# 资产类型代码规则与专用字段

> **状态：占位文档，待补充**
>
> 补充方法：在 Wind 终端搜索各类资产，记录代码规律；
> 代码生成器中切换品种类型，查看各类型特有字段

---

## 股票

### 代码规则

| 市场 | 前缀 | 后缀 | 示例 |
|------|------|------|------|
| 沪市主板 | 600xxx, 601xxx, 603xxx, 605xxx | .SH | 600519.SH |
| 深市主板 | 000xxx, 001xxx | .SZ | 000001.SZ |
| 创业板 | 300xxx, 301xxx | .SZ | 300750.SZ |
| 科创板 | 688xxx, 689xxx | .SH | 688981.SH |
| 北交所 | 8xxxxx, 4xxxxx | .BJ | 830799.BJ |

### 专用字段
已在 `field-catalog.md` 中详细记录。

---

## 指数

### 代码规则

| 系列 | 代码 | 后缀 | 示例 |
|------|------|------|------|
| 上证系列 | 000xxx | .SH | 000001.SH (上证综指) |
| 深证系列 | 399xxx | .SZ | 399001.SZ (深证成指) |
| 中证系列 | 000xxx | .SH | 000300.SH (沪深300) |
| 万得系列 | 884xxx, 886xxx | .WI | TODO: 待确认后缀 |
| 申万系列 | 801xxx | .SI | TODO: 待确认 |

### 专用字段
```
TODO: 在代码生成器中选择指数品种，记录可用字段
如：sec_name, launchdate, basedate, basevalue, close, pct_chg, volume, amt
```

---

## 债券

### 代码规则

| 类型 | 前缀/规律 | 后缀 | 示例 |
|------|----------|------|------|
| 国债 | 01xxxx | .SH | 010107.SH |
| 企业债 | TODO | TODO | TODO |
| 公司债 | TODO | TODO | TODO |
| 可转债 | 11xxxx / 12xxxx | .SH / .SZ | 113009.SH |
| 城投债 | TODO | TODO | TODO |

### 专用字段

```
TODO: 代码生成器中选择债券品种后记录

预期字段（待确认）：
- ytm_b: 到期收益率
- duration: 久期
- modified_duration: 修正久期
- convexity: 凸性
- dirty_price: 全价
- clean_price: 净价
- accrued_interest: 应计利息
- couponrate: 票面利率
- maturitydate: 到期日期
- issueamt: 发行量
- creditrating: 信用评级
- spread: 利差
```

### wsd options（债券特有）
```
PriceAdj=CP  净价
PriceAdj=DP  全价
PriceAdj=YTM 收益率
returnType=1 到期收益率计算方法
```

---

## 基金

### 代码规则

| 类型 | 前缀/规律 | 后缀 | 示例 |
|------|----------|------|------|
| 沪市 ETF | 510xxx, 511xxx, 512xxx, 513xxx, 515xxx, 516xxx, 517xxx, 518xxx, 560xxx, 561xxx, 562xxx, 563xxx | .SH | 510300.SH |
| 深市 ETF | 159xxx | .SZ | 159919.SZ |
| LOF | 16xxxx | .SZ | TODO |
| 场外基金 | TODO | .OF | TODO |

### 专用字段

```
TODO: 代码生成器中选择基金品种后记录

预期字段（待确认）：
- nav: 单位净值
- nav_acc: 累计净值
- nav_adj: 复权净值
- fund_fundmanager: 基金经理
- fund_setupdate: 成立日
- fund_type: 基金类型
- return_1w, return_1m, return_3m, return_6m, return_1y: 区间收益
- fund_totalasset: 基金规模
- fund_shares: 基金份额
```

---

## 期货

### 代码规则

| 交易所 | 后缀 | 品种示例 |
|--------|------|----------|
| 中金所 | .CFE | IF(沪深300), IC(中证500), IH(上证50), IM(中证1000), T(10Y国债), TF(5Y国债), TS(2Y国债) |
| 上期所 | .SHF | CU(铜), AL(铝), AU(黄金), AG(白银), RB(螺纹钢), RU(橡胶) |
| 大商所 | .DCE | I(铁矿石), J(焦炭), JM(焦煤), M(豆粕), P(棕榈油), Y(豆油) |
| 郑商所 | .CZC | TA(PTA), MA(甲醇), SR(白糖), CF(棉花), AP(苹果) |

**主力合约：** 品种代码 + `00`（如 `IF00.CFE`）
**当月合约：** 品种代码 + YYMM（如 `IF2406.CFE`）

### 专用字段

```
TODO: 代码生成器中选择期货品种后记录

预期字段（待确认）：
- open, high, low, close: 行情
- settle: 结算价
- volume: 成交量
- oi / open_interest: 持仓量
- basis: 基差
- basisrate: 基差率
- contractmultiplier: 合约乘数
```

---

## 期权

### 代码规则

```
TODO: 需要在终端确认

预期：
- 50ETF期权：10xxxxxx.SH
- 沪深300ETF期权（沪）：10xxxxxx.SH
- 沪深300ETF期权（深）：TODO
- 沪深300指数期权（中金所）：TODO.CFE
```

### 专用字段

```
TODO: 代码生成器中选择期权品种后记录

预期字段（待确认）：
- delta, gamma, theta, vega, rho: 希腊字母
- us_impliedvol: 隐含波动率
- theorprice: 理论价格
- exe_price: 行权价
- exe_type: 行权方式（欧式/美式）
- optiontype: 认购/认沽
- exe_date: 行权日
- expire_date: 到期日
```

---

## 验证脚本

```python
from WindPy import w
w.start()

# 逐类资产测试，记录实际可用字段
test_cases = {
    "股票": ("600519.SH", "sec_name,close,pe_ttm,pb_lf"),
    "指数": ("000300.SH", "sec_name,close,pct_chg,volume"),
    "国债": ("010107.SH", "sec_name,ytm_b,duration,convexity,close"),
    "可转债": ("113009.SH", "sec_name,close,pct_chg"),
    "ETF": ("510300.SH", "sec_name,nav,close,volume"),
    "股指期货": ("IF00.CFE", "close,settle,volume,oi"),
    # 期权: TODO 需要先找到有效代码
}

for asset_type, (code, fields) in test_cases.items():
    print(f"\n{'='*50}")
    print(f"资产类型: {asset_type} ({code})")
    err, df = w.wss(code, fields, "", usedf=True)
    if err == 0:
        print(f"成功! 返回字段: {df.columns.tolist()}")
        print(df)
    else:
        print(f"错误: {err}")
        # 尝试用 wsd 获取
        err2, df2 = w.wsd(code, fields, "-5D", "", "", usedf=True)
        if err2 == 0:
            print(f"wsd 成功! 返回字段: {df2.columns.tolist()}")
```
