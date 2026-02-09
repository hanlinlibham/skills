---
name: asset-anomaly-monitor
description: 全量资产异常波动日频监控系统。使用WindPy SDK对多类资产进行日频异常波动监控，包括申万三级行业(259个)、A股主要指数、中债指数、ETF、商品期货、全球指数等。检测偏离历史均值超过2倍标准差的异常波动，生成报告并推送。
---

# 全量资产异常波动日频监控系统

## 功能概述

本技能提供完整的多资产类别日频异常波动监控，使用Z-Score统计方法检测当日涨跌幅偏离历史均值超过2倍标准差的异常波动。

## 监控资产范围（全量）

| 资产类别 | 数量 | 获取方式 | 说明 |
|---------|------|---------|------|
| **申万三级行业** | 259个 | `w.wset("sectorconstituent", "date=YYYYMMDD;sectorid=a39901011i000000")` | 全量三级行业指数 |
| **A股主要指数** | 9个 | 直接代码 | 沪深300、中证500、上证50、中证1000等 |
| **中债指数** | 5个 | 直接代码 | 中债总指数、国债指数、金融债指数等 |
| **主流ETF** | 8个 | 直接代码 | 沪深300ETF、中证500ETF、创业板ETF等 |
| **商品期货** | 8个 | 直接代码 | 黄金、白银、铜、原油等主要品种 |
| **全球指数** | 9个 | 直接代码 | 标普500、纳指、道指、恒指、日经等 |

## 核心计算逻辑

### 1. 数据获取
```python
# 申万三级行业（259个全量）
result = w.wset("sectorconstituent", f"date={today_str};sectorid=a39901011i000000")

# 每个资产获取过去一年日涨跌幅
hist = w.wsd(code, "pct_chg", one_year_ago, today_str, "", usedf=True)
```

### 2. 统计量计算
```python
mean_ret = returns.mean()      # 历史日均涨跌幅
std_ret = returns.std()        # 历史波动率（标准差）
today_ret = returns.iloc[-1]   # 今日涨跌幅
```

### 3. Z-Score计算
```
Z = (今日涨跌幅 - 历史均值) / 历史标准差
Z = (R_today - μ) / σ
```

### 4. 异常判定
```python
if abs(z_score) > 2:
    标记为异常波动
    direction = "大涨" if z_score > 0 else "大跌"
```

### 5. 筛选条件
- 必须有 >30个交易日数据
- 历史标准差必须 >0（有波动）
- 按 |Z| 绝对值降序排列

## 使用方法

### 直接运行监控脚本
```bash
python scripts/full_asset_monitor.py
```

### Python代码调用
```python
from scripts.full_asset_monitor import AssetAnomalyMonitor

monitor = AssetAnomalyMonitor()
results = monitor.run_full_monitoring()
monitor.generate_report(results)
```

### 定时任务（推荐）
```bash
# 每日15:30运行
30 15 * * * cd /path/to/workspace && python scripts/full_asset_monitor.py
```

## 输出结果

### Excel报告字段
| 字段 | 说明 |
|------|------|
| `category` | 资产类别 |
| `code` | 资产代码 |
| `name` | 资产名称 |
| `today_return` | 今日涨跌幅(%) |
| `z_score` | Z值（偏离度） |
| `std_annual` | 年化标准差（历史波动率） |
| `direction` | 大涨/大跌 |

## 资产代码配置

### A股主要指数
```python
ASHARE_INDEX_CODES = [
    "000300.SH",  # 沪深300
    "000905.SH",  # 中证500
    "000016.SH",  # 上证50
    "000852.SH",  # 中证1000
    "000001.SH",  # 上证指数
    "399001.SZ",  # 深证成指
    "399006.SZ",  # 创业板指
    "000688.SH",  # 科创50
    "883985.WI",  # 万得全A
]
```

### 商品期货
```python
COMMODITY_CODES = [
    "AU00.SHF",  # 黄金
    "AG00.SHF",  # 白银
    "CU00.SHF",  # 铜
    "AL00.SHF",  # 铝
    "ZN00.SHF",  # 锌
    "RB00.SHF",  # 螺纹钢
    "SC00.INE",  # 原油
    "TA00.CZC",  # PTA
]
```

### 全球指数
```python
GLOBAL_INDEX_CODES = [
    "SPX.GI",    # 标普500
    "IXIC.GI",   # 纳斯达克
    "DJI.GI",    # 道琼斯
    "VIX.GI",    # VIX波动率
    "HSI.HI",    # 恒生指数
    "N225.GI",   # 日经225
    "KS11.GI",   # 韩国KOSPI
    "GDAXI.GI",  # 德国DAX
    "FTSE.GI",   # 英国富时100
]
```

## 与原有监控的区别

| 对比项 | 原有监控 | 本全量监控 |
|--------|---------|-----------|
| 申万三级行业 | 20个样本 | **259个全量** |
| 中债指数 | 5个指定 | **5个主要指数** |
| ETF | 8个主流 | **8个主流** |
| 商品 | 8个品种 | **8个主要品种** |
| 全球指数 | 9个主要 | **9个主要指数** |

## 依赖

- Python 3.8+
- WindPy (Wind金融终端Python API)
- pandas
- numpy

## 注意事项

1. **Wind终端**: 必须启动Wind金融终端并保持登录状态
2. **数据权限**: 部分数据需要对应的数据权限
3. **运行时间**: 建议在每日收盘后15:30运行
4. **首次运行**: 首次获取一年历史数据可能需要较长时间

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| w.start() 失败 | Wind终端未启动 | 启动Wind终端并保持登录 |
| 获取不到数据 | 无数据权限 | 联系Wind客服开通权限 |
| 运行缓慢 | 资产数量多 | 正常现象，首次运行较慢 |
| Z值异常 | 历史数据不足 | 确保有>30个交易日数据 |

## 参考文档

- `references/sectorid-catalog.md` - 板块SectorID完整列表
- `references/field-catalog.md` - Wind字段速查手册
- `references/error-codes.md` - 错误码对照表
