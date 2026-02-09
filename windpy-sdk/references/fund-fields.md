# WindPy 基金专用字段参考

基金数据通过 `w.wsd()`（时间序列）和 `w.wss()`（截面快照）获取。

## 基金基础字段（wss 截面数据）

| 字段 | 含义 | 说明 |
|------|------|------|
| `nav` | 单位净值 | 最新净值 |
| `nav_acc` | 累计净值 | 含分红的累计净值 |
| `nav_adj` | 复权净值 | 考虑分红再投资的净值 |
| `nav_date` | 净值日期 | 最新净值对应日期 |

## 基金信息字段（wss 截面数据）

| 字段 | 含义 | 说明 |
|------|------|------|
| `fund_type` | 基金类型 | 股票型/债券型/混合型等 |
| `sec_name` | 基金简称 |  |
| `fund_manager` | 基金经理 |  |
| `fund_corp` | 基金公司 |  |

## ETF 涨跌幅字段

### 实时涨跌幅（日内）

| 字段 | 含义 | 函数 | 说明 |
|------|------|------|------|
| `rt_last` | 最新价 | wsq | 实时成交价 |
| `rt_pct_chg` | 实时涨跌幅(%) | wsq | 相对于昨收的实时涨跌 |
| `rt_chg` | 实时涨跌额 | wsq | 实时涨跌金额 |
| `rt_nav` | 实时净值 | wsq | ETF实时IOPV净值 |

### 日频涨跌幅（日K）

| 字段 | 含义 | 函数 | 说明 |
|------|------|------|------|
| `close` | 日收盘价 | wsd/wss | 当日收盘价 |
| `pct_chg` | 日涨跌幅(%) | wsd/wss | 当日涨跌幅 |
| `change` | 日涨跌额 | wsd/wss | 当日涨跌金额 |
| `nav` | 单位净值 | wsd/wss | 日终单位净值 |
| `pct_chg_nav` | 净值日涨跌幅(%) | wsd/wss | 净值日涨跌幅 |

**使用场景对比：**
- **实时行情（wsq）**：适合盘中监控、日内交易决策
- **日频行情（wsd/wss）**：适合日终复盘、历史数据分析、策略回测

---

## 使用示例

```python
from WindPy import w
w.start()

# 基金净值时间序列
err, df = w.wsd("510300.SH", "nav,nav_acc,nav_adj", "-30D", "", "", usedf=True)
# 列名: ['NAV', 'NAV_ACC', 'NAV_ADJ']

# 多只基金截面信息
err, df = w.wss("510300.SH,159915.SZ,512800.SH",
    "sec_name,nav,nav_acc,fund_type,fund_manager",
    "", usedf=True)

# ETF 实时行情（日内）
err, df = w.wsq("510300.SH", "rt_last,rt_pct_chg,rt_nav", usedf=True)

# ETF 日频涨跌幅获取方式

## 方式1：使用 wsd 获取历史日频涨跌幅（推荐）
err, df = w.wsd("510300.SH", "close,pct_chg", "-30D", "", "", usedf=True)
# close: 日收盘价
# pct_chg: 日涨跌幅(%)

## 方式2：使用 wss 获取截面日频涨跌幅
err, df = w.wss("510300.SH,159915.SZ", "close,pct_chg", "tradeDate=20260209", usedf=True)
# 获取指定交易日的收盘价和涨跌幅

## 方式3：获取ETF的历史净值涨跌幅
err, df = w.wsd("510300.SH", "nav,pct_chg_nav", "-30D", "", "", usedf=True)
# nav: 单位净值
# pct_chg_nav: 净值日涨跌幅

w.stop()
```

---

## 常见基金代码示例

| 代码 | 名称 | 类型 |
|------|------|------|
| `510300.SH` | 华泰柏瑞沪深300ETF | 股票ETF |
| `159915.SZ` | 易方达创业板ETF | 股票ETF |
| `512800.SH` | 华宝中证银行ETF | 行业ETF |
| `511880.SH` | 银华日利 | 货币ETF |
| `518880.SH` | 华安黄金ETF | 商品ETF |

---

## 注意事项

1. **净值更新时间：** 一般 T 日 21:00 后更新 T 日净值
2. **QDII 基金：** 净值更新可能延迟 1-2 个交易日
3. **货币 ETF：** 使用 `rt_nav` 获取实时净值/每万份收益
4. **LOF 基金：** 代码后缀 .SZ/.SH，同时有场内交易和场外净值

---

## ETF 涨跌幅获取详解

### 实时涨跌幅（盘中）

适合**日内交易监控**和**实时盯盘**：

```python
# 获取多只ETF实时涨跌幅
etf_list = "510300.SH,159915.SZ,518880.SH"
err, df = w.wsq(etf_list, "rt_last,rt_pct_chg,rt_chg,rt_nav", usedf=True)

# 返回示例：
# rt_last: 最新成交价
# rt_pct_chg: 相对于昨收的涨跌幅(%)
# rt_chg: 涨跌金额
# rt_nav: 实时IOPV净值
```

### 日频涨跌幅（日K）

适合**盘后分析**、**历史回测**、**日线策略**：

```python
# 获取ETF历史日频涨跌幅（过去30天）
err, df = w.wsd("510300.SH", "close,pct_chg", "-30D", "", "", usedf=True)
# DataFrame 包含每日收盘价和涨跌幅

# 获取特定日期的截面涨跌幅
err, df = w.wss("510300.SH,159915.SZ,518880.SH", 
                "close,pct_chg", 
                "tradeDate=20260209", usedf=True)
# 返回指定交易日的收盘价和涨跌幅

# 获取净值涨跌幅（反映基金实际收益）
err, df = w.wsd("510300.SH", "nav,pct_chg_nav", "-30D", "", "", usedf=True)
# nav: 日终单位净值
# pct_chg_nav: 净值日涨跌幅
```

### 实时 vs 日频的区别

| 维度 | 实时行情 (wsq) | 日频行情 (wsd/wss) |
|------|----------------|-------------------|
| **更新频率** | 秒级/分钟级 | 日终更新 |
| **适用场景** | 盘中交易、实时监控 | 盘后分析、策略回测 |
| **字段前缀** | `rt_` (real-time) | 无前缀 |
| **涨跌幅基准** | 相对于昨收价 | 相对于前一日收盘价 |
| **数据存储** | 通常只保留当日 | 长期历史数据 |

### 常用ETF涨跌幅监控代码

```python
def get_etf_daily_performance(etf_list, date=None):
    """
    获取ETF日频涨跌幅表现
    
    Parameters:
    -----------
    etf_list : list
        ETF代码列表，如 ['510300.SH', '159915.SZ']
    date : str, optional
        日期，格式 'YYYYMMDD'，默认最新交易日
    
    Returns:
    --------
    DataFrame : 包含ETF名称、收盘价、涨跌幅
    """
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y%m%d')
    
    codes = ','.join(etf_list)
    err, df = w.wss(codes, "sec_name,close,pct_chg", 
                    f"tradeDate={date}", usedf=True)
    
    if err == 0:
        df.columns = ['ETF名称', '收盘价', '涨跌幅(%)']
        df = df.sort_values('涨跌幅(%)', ascending=False)
        return df
    return None

# 使用示例
etf_codes = ['510300.SH', '159915.SZ', '518880.SH', '512800.SH']
df = get_etf_daily_performance(etf_codes)
print(df)
```
