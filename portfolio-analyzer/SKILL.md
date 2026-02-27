---
name: portfolio-analyzer
description: >
  投资组合多维分析与 Excel 报告生成。当用户需要进行组合 vs 基准收益对比、
  风险指标计算、行业归因分析（Brinson 三因素）、资产大类归因，
  或从组合 Excel 数据生成分析报告时触发。
  关键词: 组合分析、业绩归因、行业归因、组合对比、净值分析、风险指标、
  Brinson、夏普比率、最大回撤、信息比率
---

# 投资组合分析

## 触发条件

当用户需要：
- 多组合 vs 基准的收益对比分析
- 计算风险指标（夏普、最大回撤、信息比率、索提诺等）
- 行业归因分析（Brinson 三因素：配置 + 选股 + 交互）
- 资产大类业绩归因
- 从组合 Excel 数据生成分析报告
- 分析净值曲线、回撤、滚动波动率

## 依赖

| 依赖 | 用途 | 必需 |
|------|------|------|
| `windpy-sdk` | 获取基准净值 + 申万行业收益 | 是（Wind 数据） |
| `xlsx` | Excel 输出规范 + `recalc.py` 公式验证 | 是（报告输出） |
| `plotly` | 净值曲线 + 归因柱状图的交互式 HTML | 否（可选） |

## 快速开始

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/portfolio-analyzer/scripts"))
from portfolio_analyzer import (
    load_portfolio_data,
    fetch_benchmark,
    fetch_benchmark_industry_weights,
    fetch_shenwan_returns,
    compute_risk_metrics,
    compute_brinson,
)

# 1. 加载用户 Excel
data = load_portfolio_data("/path/to/portfolio.xlsx")
nav = data["nav_timeseries"]          # 宽表: 列=组合, index=日期

# 2. 获取基准
bench = fetch_benchmark("000300.SH", "2025-01-01", "2026-02-27")

# 3. 计算风险指标
metrics = compute_risk_metrics(nav["P001"], bench["close"])

# 4. Brinson 行业归因
ind = data["industry_attribution"]
result = compute_brinson(
    ind["port_weight"], ind["bench_weight"],
    ind["port_return"], ind["bench_return"],
)
```

## 工作流

### 第 1 步：解析用户请求

从用户消息中提取：
- **输入 Excel 路径**（必需）
- **分析区间**：起止日期，默认取 Excel 数据全区间
- **基准选择**：默认沪深 300（000300.SH），用户可指定中证 500/800/1000 等
- **组合筛选**：分析全部组合或指定组合代码

常用基准代码：

| 基准 | Wind 代码 |
|------|----------|
| 沪深 300 | 000300.SH |
| 中证 500 | 000905.SH |
| 中证 800 | 000906.SH |
| 中证 1000 | 000852.SH |
| 上证 50 | 000016.SH |
| 创业板指 | 399006.SZ |
| 万得全 A | 881001.WI |

### 第 2 步：加载数据

```python
data = load_portfolio_data(filepath)
```

自动识别 5 张表（通过特征列匹配，不依赖 sheet 名称）：

| 表类型 | 键名 | 识别特征 |
|--------|------|---------|
| 时序分析 | `nav_timeseries` | 含"单位净值"/"NAV"列 |
| 交易明细 | `trade_detail` | 含"成交金额"/"买卖方向"列 |
| 收益贡献 | `return_contribution` | 含"收益贡献"/"收益率贡献"列 |
| 业绩归因 | `asset_attribution` | 含"资产大类"列 |
| 行业归因 | `industry_attribution` | 含"行业"+"配置效应"列 |

> **参考**：列名映射规则见 `references/data-loading-guide.md`

### 第 3 步：获取基准数据

```python
bench = fetch_benchmark("000300.SH", start, end)
# 返回 DataFrame: columns=["close"], index=DatetimeIndex
```

### 第 4 步：获取行业基准

```python
# 4a. 基准指数的行业权重（bw_i）
bench_weights = fetch_benchmark_industry_weights("000300.SH", "20260227")
# 返回 Series: index=行业名称, values=权重(0~1)

# 4b. 各行业指数的区间收益（br_i）
sw = fetch_shenwan_returns(start, end)
# 返回 DataFrame: index=行业名称, columns=["code", "pct_chg"]
```

`fetch_benchmark_industry_weights` 内部流程：
1. `wset("indexconstituent")` 拉取成分股及权重
2. `wss(codes, "industry_sw")` 查每只股票的申万一级行业（分批，每批 80 只）
3. 按行业聚合权重并归一化

> **参考**：31 个申万一级行业代码见 `references/shenwan-industry-codes.md`

### 第 5 步：收益分析

对每个组合计算：
- 累计收益率：`nav / nav.iloc[0] - 1`
- 日收益率：`nav.pct_change()`
- 超额收益：组合累计 - 基准累计

### 第 6 步：风险分析

```python
metrics = compute_risk_metrics(nav_series, benchmark_series, rf=0.015)
```

返回 8 个指标：

| 指标 | 含义 | Excel 格式 |
|------|------|-----------|
| 年化收益率 | 复合年化回报 | 0.00% |
| 年化波动率 | 收益率标准差年化 | 0.00% |
| 最大回撤 | 峰谷最大跌幅 | 0.00% |
| 夏普比率 | 单位风险超额收益 | 0.00 |
| 信息比率 | 单位跟踪误差超额 | 0.00 |
| 卡尔玛比率 | 年化收益/最大回撤 | 0.00 |
| 索提诺比率 | 单位下行风险超额 | 0.00 |
| 胜率 | 正收益天数占比 | 0.00% |

> **参考**：公式详情见 `references/risk-metrics-formulas.md`

辅助分析：
```python
from portfolio_analyzer import rolling_volatility, drawdown_series, top_drawdowns

vol = rolling_volatility(nav_series, window=20)    # 20日滚动波动率
dd = drawdown_series(nav_series)                    # 每日回撤
top5 = top_drawdowns(nav_series, n=5)               # Top5 回撤
```

### 第 7 步：行业归因（Brinson 三因素）

```python
result = compute_brinson(port_weights, bench_weights, port_returns, bench_returns)
# columns: ["配置效应", "选股效应", "交互效应", "总归因"]
```

**数据来源优先级**：
1. 若用户 Excel 已包含行业归因数据（表 5 有 port_weight/bench_weight/port_return/bench_return），直接使用
2. 否则从 Wind 构建全部 4 个输入：
   - `pw_i` 组合行业权重：从表 3 收益贡献按行业聚合 `weight`
   - `bw_i` 基准行业权重：`fetch_benchmark_industry_weights("000300.SH", date)`
   - `pr_i` 组合行业收益：从表 3 按行业聚合 `sec_return`（加权平均）
   - `br_i` 基准行业收益：`fetch_shenwan_returns(start, end)["pct_chg"]`

### 第 8 步：生成 Excel 报告

使用 openpyxl 生成 6 个 sheet 的 Excel 报告，遵循 xlsx skill 格式规范。

#### Sheet 1: 概览

多组合指标对比仪表盘：

```
       | 组合A    | 组合B    | 基准     |
年化收益 | 12.50%  | 8.30%   | 10.20%  |  ← 最优绿色
年化波动 | 15.20%  | 12.80%  | 14.50%  |  ← 最低绿色
最大回撤 | 18.50%  | 12.30%  | 15.80%  |  ← 最低绿色
夏普比率 | 0.72    | 0.53    | 0.60    |  ← 最高绿色
```

**条件格式**：每行最优值绿色底色，最差值红色底色。

#### Sheet 2: 净值曲线

| 列 | 内容 | 来源 |
|----|------|------|
| A | 日期 | 数据 |
| B+ | 各组合 NAV | 数据 |
| 之后 | 基准 NAV | Wind |
| 之后 | 各组合日收益率 | 公式 `=B3/B2-1` |
| 之后 | 各组合累计收益率 | 公式 `=B3/B$2-1` |

冻结首行首列。

#### Sheet 3: 风险分析

- 滚动波动率列（辅助列计算 20 日标准差）
- 回撤序列（辅助列 RunningMax = `MAX($B$2:B2)`，Drawdown = `(RunMax-NAV)/RunMax`）
- Top 5 最大回撤表（起始日、最低点、幅度）

#### Sheet 4: 收益归因

- 资产大类归因表（从表 4 直接输出）
- 个股贡献 Top 10 / Bottom 10（从表 3 排序）
- 条件格式：正值绿色，负值红色
- SUM 校验行验证归因加总

#### Sheet 5: 行业归因

- Brinson 配置/选股/交互效应
- 按总归因降序排序
- 数据条可视化（配置效应、选股效应列）
- 底部合计行

#### Sheet 6: 交易明细

- 原始交易数据透传
- 自动筛选 + 冻结首行

### 第 9 步：公式验证

```bash
python ~/.claude/skills/xlsx/scripts/recalc.py output.xlsx
# 期望输出: 0 个公式错误
```

## Excel 格式规范

遵循 xlsx skill 标准：

| 元素 | 规范 |
|------|------|
| 输入数据字体 | 蓝色 (0000FF) |
| 公式字体 | 黑色 (000000) |
| 百分比 | `0.00%` 格式 |
| 负数 | 用括号 `(0.00%)` |
| 表头 | 深蓝底白字，加粗 |
| 千分位 | 金额列用 `#,##0` |
| 冻结窗格 | 所有 sheet 冻结首行 |

## 函数参考

### `load_portfolio_data(filepath) -> dict`

解析组合 Excel 文件，自动识别 5 张表。

| 参数 | 类型 | 说明 |
|------|------|------|
| filepath | str | Excel 文件路径 |
| **返回** | dict | 键为表类型，值为 DataFrame |

### `fetch_benchmark(code, start, end) -> DataFrame`

通过 Wind 获取基准指数收盘价。

| 参数 | 类型 | 说明 |
|------|------|------|
| code | str | 指数代码，如 "000300.SH" |
| start | str | 起始日期 |
| end | str | 结束日期 |
| **返回** | DataFrame | columns=["close"], index=日期 |

### `fetch_benchmark_industry_weights(index_code, date) -> Series`

获取基准指数的申万一级行业权重分布。

| 参数 | 类型 | 说明 |
|------|------|------|
| index_code | str | 指数代码，如 "000300.SH" |
| date | str | 日期，如 "20260227" |
| **返回** | Series | index=行业名, values=权重(0~1) |

内部调用 `wset("indexconstituent")` + `wss(codes, "industry_sw")` 分批查询后聚合。

### `fetch_shenwan_returns(start, end) -> DataFrame`

获取 31 个申万一级行业区间涨跌幅。

| 参数 | 类型 | 说明 |
|------|------|------|
| start | str | 起始日期 |
| end | str | 结束日期 |
| **返回** | DataFrame | index=行业名, columns=["code","pct_chg"] |

### `compute_risk_metrics(nav, benchmark, rf) -> dict`

计算 8 个风险指标。

| 参数 | 类型 | 说明 |
|------|------|------|
| nav | Series | 组合净值序列 |
| benchmark | Series | 基准净值序列（可选） |
| rf | float | 无风险利率，默认 0.015 |
| **返回** | dict | 8 个指标名 → 数值 |

### `compute_brinson(pw, bw, pr, br) -> DataFrame`

Brinson 三因素行业归因。

| 参数 | 类型 | 说明 |
|------|------|------|
| pw | Series | 组合行业权重 |
| bw | Series | 基准行业权重 |
| pr | Series | 组合行业收益 |
| br | Series | 基准行业收益 |
| **返回** | DataFrame | 配置/选股/交互/总归因，按总归因排序 |

### 辅助函数

| 函数 | 说明 |
|------|------|
| `align_nav(nav1, nav2)` | 按日期对齐两个净值序列 |
| `rolling_volatility(nav, window=20)` | 滚动年化波动率 |
| `drawdown_series(nav)` | 每日回撤幅度序列 |
| `top_drawdowns(nav, n=5)` | 提取前 N 次最大回撤 |
| `cumulative_return(nav)` | 累计收益率序列 |
| `daily_returns(nav)` | 日收益率序列 |
| `match_industry(name)` | 行业名称模糊匹配到 Wind 代码 |

## 常见场景

### 场景 1：多组合月度绩效报告

```
用户: 帮我分析这个月组合的表现，Excel 在 ~/data/portfolio_202602.xlsx，
     基准用沪深300
```

→ 执行完整 9 步工作流，输出 6-sheet Excel 报告

### 场景 2：单组合深度风险分析

```
用户: 分析组合 P001 的回撤和波动率
```

→ 只执行步骤 1-2-3-6，重点输出风险分析 sheet（滚动波动率 + Top5 回撤）

### 场景 3：行业归因分析

```
用户: 帮我做 Brinson 行业归因，Excel 里有行业权重和收益数据
```

→ 步骤 1-2-4-7，重点输出行业归因 sheet

### 场景 4：组合间横向对比

```
用户: 对比这 5 个组合的夏普比率和最大回撤
```

→ 步骤 1-2-3-5-6，重点输出概览 sheet（仪表盘）
