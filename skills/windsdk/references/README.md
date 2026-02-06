# WindPy SDK Skill 参考资料准备指南

本目录存放 windpy-sdk skill 的补充参考资料。以下说明每个文件的用途、当前状态、以及如何补充。

---

## 当前文件清单

| 文件 | 状态 | 内容 |
|------|------|------|
| `field-catalog.md` | 基础版 | 行情/基本面/三大报表/资金流向/业绩预告 字段 |
| `edb-indicators.md` | 基础版 | ~100个 EDB 宏观指标代码 |
| `wset-tables.md` | 占位 | wset 可用报表名 + 参数 |
| `sector-ids.md` | 占位 | 板块/行业 sectorid 完整列表 |
| `asset-type-codes.md` | 占位 | 债券/基金/期货/期权 代码规则和专用字段 |
| `error-codes.md` | 占位 | 完整错误码对照表 |
| `options-cheatsheet.md` | 占位 | 各函数 options 参数速查 |

---

## 如何补充资料

### 通用方法

**方法 1：Wind 终端代码生成器（最推荐）**
```
Wind 终端 → 量化 → API 接口 → 代码生成器
→ 选择函数（如 WSD）→ 选择品种和指标 → 查看可选参数
```
代码生成器会列出所有可用的 fields 和 options，直接复制到对应文件即可。

**方法 2：终端直接运行测试**
```python
from WindPy import w
w.start()

# 测试某个调用，记录返回的 Fields
data = w.wsd("600519.SH", "close", "-1D", "")
print(data.Fields)  # 看实际返回字段名
```

**方法 3：Wind API 帮助文档**
```
Wind 终端 → 帮助 → API 帮助中心 → 选择函数查看字段列表
```

---

## 各文件详细准备说明

### 1. field-catalog.md（需扩充）

**当前已有：** A 股行情、基本面、三大报表、资金流向、业绩预告/快报字段

**需要补充：**

#### 债券字段
在代码生成器中选择品种为债券（如 `010107.SH`），可查到：
```
需要记录的字段：
- 价格类：ytm_b(到期收益率), duration(久期), convexity(凸性), dirty_price(全价), clean_price(净价)
- 基本信息：couponrate(票面利率), maturitydate(到期日), issueamt(发行量), creditrating(信用评级)
- 其他：accrued_interest(应计利息), spread(利差)
```

#### 基金字段
选择品种为基金（如 `510300.SH`），记录：
```
需要记录的字段：
- NAV类：nav(单位净值), nav_acc(累计净值), nav_adj(复权净值)
- 基本信息：fund_fundmanager(基金经理), fund_setupdate(成立日), fund_type(基金类型)
- 业绩类：return_1w, return_1m, return_3m, return_6m, return_1y, return_ytd
- 规模类：fund_totalasset(基金规模), fund_shares(基金份额)
```

#### 期货字段
选择品种为期货（如 `IF00.CFE`），记录：
```
需要记录的字段：
- 行情类：open, high, low, close, settle(结算价), volume, oi(持仓量)
- 基差类：basis(基差), basisrate(基差率)
- 其他：contractmultiplier(合约乘数), margin_ratio(保证金比例)
```

#### 期权字段
选择品种为期权（如 `10004753.SH`），记录：
```
需要记录的字段：
- 希腊字母：delta, gamma, theta, vega, rho
- 定价：us_impliedvol(隐含波动率), theorprice(理论价格)
- 基本信息：exe_price(行权价), exe_type(行权方式), optiontype(认购/认沽)
```

**操作步骤：**
1. 在 Wind 终端打开代码生成器
2. 分别选择 债券/基金/期货/期权 品种
3. 勾选所有可用字段
4. 复制字段名和中文说明
5. 追加到 `field-catalog.md` 对应章节

---

### 2. edb-indicators.md（需扩充）

**当前已有：** GDP、CPI、PPI、PMI、货币供应、利率、国债、社融、固投、消费、进出口、融资融券、美国经济

**需要补充的分类：**

#### 行业经济数据
```
需要记录的指标：
- 钢铁：螺纹钢价格、铁矿石价格、粗钢产量
- 房地产：70城房价指数、土地成交面积
- 汽车：汽车销量、新能源汽车销量
- 电力：全社会用电量、发电量
- 航运：BDI指数、集装箱运价指数
```

#### 商品数据
```
需要记录的指标：
- 能源：原油(WTI/Brent)、天然气、煤炭价格
- 金属：黄金、白银、铜、铝、锂
- 农产品：大豆、玉米、猪肉价格
```

#### 全球利率
```
需要记录的指标：
- 美国国债各期限收益率(3M/2Y/5Y/10Y/30Y)
- 欧洲央行基准利率
- 日本国债利率
```

**操作步骤：**
1. Wind 终端 → EDB（宏观经济数据库）
2. 左侧目录树逐级展开，找到需要的指标
3. 右键复制指标代码（如 `M0001227`）
4. 记录格式：`| 代码 | 指标名称 | 频率 |`
5. 追加到 `edb-indicators.md` 对应章节

---

### 3. wset-tables.md（需新建）

**目的：** 记录 `w.wset()` 所有可用的报表名和参数。

**如何获取：**
1. 代码生成器 → 选择 WSET 函数
2. 左侧列表会显示所有可用报表名
3. 选择每个报表名，查看其 options 参数

**需要记录的格式：**
```markdown
### sectorconstituent — 板块成分股
- date: 日期（YYYY-MM-DD）
- sectorid: 板块ID
- 返回列: date, wind_code, sec_name

### indexconstituent — 指数成分股
- date: 日期
- windcode: 指数代码（如 000300.SH）
- 返回列: date, wind_code, sec_name, i_weight

### abnormalactivitiesranking — 龙虎榜
- startdate/enddate: 起止日期
- field: 需要的字段列表
- 返回列: trade_dt, wind_code, sec_name, close, pct_chg, netbuyamt, ...
```

**重点关注的报表名：**
- `sectorconstituent` — 板块成分股
- `indexconstituent` — 指数成分股
- `abnormalactivitiesranking` — 龙虎榜
- `dividendproposal` — 分红方案
- `tradingsuspend` — 停牌股票
- `marginassetsandliabilities` — 融资融券标的
- `etfconstituent` — ETF 申赎清单
- `sectorconstituent` + 基金板块 — 基金列表
- `corpaction` — 公司行为事件
- `sharefloat` — 限售解禁

**验证方法：**
```python
# 运行并记录实际返回
err, df = w.wset("sectorconstituent",
    "date=2024-06-28;sectorid=a001010100000000", usedf=True)
print(df.columns.tolist())  # 记录实际返回列名
print(df.head())
```

---

### 4. sector-ids.md（需新建）

**目的：** 完整的板块/行业 sectorid 对照表。

**如何获取：**
1. Wind 终端 → 板块 → 左侧树形目录
2. 或使用代码生成器 WSET → sectorconstituent → sectorid 下拉框

**需要记录的分类：**

```markdown
## A 股市场板块
| 板块 | sectorid | 说明 |
|------|----------|------|
| 全部A股 | a001010100000000 | |
| 上证A股 | a001010200000000 | |
| ...    | ...              | |

## 申万一级行业
| 行业 | sectorid | 说明 |
|------|----------|------|
| 银行 | a39901011g000000 | |
| 食品饮料 | ??? | 需要查 |
| ...  | ...              | |

## 申万二级/三级行业
（同上格式）

## 概念板块
（同上格式）

## 指数
| 指数 | windcode | 说明 |
|------|----------|------|
| 沪深300 | 000300.SH | indexconstituent 用 windcode |
| 中证500 | 000905.SH | |
```

**快捷获取方法：**
```python
# 获取申万一级行业列表
err, df = w.wset("sectorconstituent", "date=2024-06-28;sectorid=a001010100000000", usedf=True)
stocks = df['wind_code'].tolist()
err, industry = w.wss(stocks, "industry_sw", "tradeDate=20240628", usedf=True)
print(industry['INDUSTRY_SW'].unique())  # 列出所有一级行业名
# 但这不会给出 sectorid，sectorid 需要从终端目录树查
```

---

### 5. asset-type-codes.md（需新建）

**目的：** 不同资产类型的代码规则和专用函数用法。

**需要记录的内容：**

```markdown
## 股票
- 沪市：600xxx.SH, 601xxx.SH, 603xxx.SH, 605xxx.SH
- 深市主板：000xxx.SZ, 001xxx.SZ
- 创业板：300xxx.SZ, 301xxx.SZ
- 科创板：688xxx.SH, 689xxx.SH
- 北交所：8xxxxx.BJ, 4xxxxx.BJ

## 指数
- 上证系列：000001.SH(上证综指), 000016.SH(上证50)
- 深证系列：399001.SZ(深证成指), 399006.SZ(创业板指)
- 中证系列：000300.SH(沪深300), 000905.SH(中证500)

## 债券
- 国债：01xxxx.SH
- 企业债/公司债：代码规则...
- 可转债：11xxxx.SH, 12xxxx.SZ

## 基金
- 场内ETF：510xxx.SH, 159xxx.SZ
- 场内LOF：16xxxx.SZ
- 场外基金：代码规则...

## 期货
- 股指期货：IF(沪深300), IC(中证500), IH(上证50) + .CFE
- 商品期货：代码规则 + .SHF/.DCE/.CZC
- 主力合约：合约代码 + 00（如 IF00.CFE）

## 期权
- 50ETF期权：代码规则 + .SH
- 沪深300期权：代码规则
```

**操作步骤：**
1. 在 Wind 终端分别搜索不同资产类型
2. 记录代码前缀规律和后缀规则
3. 记录每种资产类型特有的 wsd/wss 字段（如期货的 settle、oi）

---

### 6. error-codes.md（需新建）

**目的：** 完整的 Wind API 错误码对照表。

**如何获取：**
1. Wind API 帮助中心 → 错误码查询
2. 或在终端运行 `w.menu()` → 帮助 → 错误码

**需要记录的格式：**
```markdown
| 错误码 | 含义 | 常见原因 | 解决方法 |
|--------|------|----------|----------|
| 0 | 成功 | — | — |
| -40520007 | 无数据权限 | 未购买对应数据权限 | 联系Wind客服开通 |
| -40520017 | 字段不支持 | Mac版SDK不支持该字段 | 换用其他字段或Windows |
| -40522006 | 参数错误 | options格式不对 | 检查参数拼写和分号 |
| -40521001 | 网络连接失败 | Wind未启动或网络断开 | 检查Wind终端状态 |
| ... | ... | ... | ... |
```

**快捷获取方法：** 故意传错误参数触发各种错误码，逐个记录：
```python
# 测试各类错误
w.wsd("INVALID", "close", "-1D", "")           # 代码错误
w.wsd("600519.SH", "invalid_field", "-1D", "")  # 字段错误
w.wsd("600519.SH", "close", "invalid", "")      # 日期错误
```

---

### 7. options-cheatsheet.md（需新建）

**目的：** 各函数 options 参数的完整速查表。

**如何获取：**
代码生成器中选择不同函数，查看所有可用 options。

**需要记录的格式：**
```markdown
## w.wsd() options
| 参数 | 值 | 说明 |
|------|-----|------|
| PriceAdj | F/B/T | 前复权/后复权/定点复权 |
| Period | D/W/M/Q/S/Y | 日/周/月/季/半年/年 |
| Days | Trading/Weekdays/Alldays | 交易日/工作日/日历日 |
| Fill | Previous/Blank | 沿用前值/留空 |
| TradingCalendar | SSE/SZSE/HKEX/NYSE/... | 交易所日历 |
| Currency | Original/CNY/USD/HKD | 币种 |
| Order | A/D | 升序/降序 |

## w.wss() options
| 参数 | 值 | 说明 |
|------|-----|------|
| tradeDate | YYYYMMDD | 交易日期 |
| rptDate | YYYYMMDD | 报告期 |
| rptType | 408001000/408004000/... | 报表类型 |
| year | YYYY | 年份（业绩预告用） |
| currencyType | CNY/USD/HKD | 币种 |

## w.wsi() options
（同上格式）

## w.wset() options
（按每个 tableName 分别记录）
```

---

## 补充优先级建议

| 优先级 | 文件 | 原因 |
|--------|------|------|
| P0 | `wset-tables.md` | wset 是最常用但文档最少的函数 |
| P0 | `sector-ids.md` | 申万行业 sectorid 是分析必备 |
| P1 | `field-catalog.md` 扩充 | 债券/基金/期货字段扩展使用场景 |
| P1 | `edb-indicators.md` 扩充 | 行业数据/商品数据 |
| P2 | `asset-type-codes.md` | 多资产类型代码规则 |
| P2 | `error-codes.md` | 调试排错用 |
| P3 | `options-cheatsheet.md` | SKILL.md 已覆盖主要参数 |
