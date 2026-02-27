# 风险指标公式参考

## 指标速查表

| 指标 | 含义 | 越大越好？ | 典型范围 |
|------|------|-----------|---------|
| 年化收益率 | 复合年化回报 | 是 | -20% ~ 50% |
| 年化波动率 | 收益率标准差年化 | 否 | 5% ~ 40% |
| 最大回撤 | 峰谷最大跌幅 | 否 | 5% ~ 60% |
| 夏普比率 | 单位风险超额收益 | 是 | -1 ~ 3 |
| 信息比率 | 单位跟踪误差超额收益 | 是 | -1 ~ 2 |
| 卡尔玛比率 | 年化收益 / 最大回撤 | 是 | 0 ~ 5 |
| 索提诺比率 | 单位下行风险超额收益 | 是 | -1 ~ 5 |
| 胜率 | 正收益天数占比 | 是 | 40% ~ 65% |

---

## 1. 年化收益率 (Annualized Return)

**公式：**

$$R_{ann} = \left(\frac{NAV_{end}}{NAV_{start}}\right)^{\frac{252}{n}} - 1$$

其中 $n$ 为交易日天数，252 为 A 股年交易日。

**Python：**
```python
def annualized_return(nav: pd.Series) -> float:
    """nav: 日频净值序列，index 为日期"""
    total_return = nav.iloc[-1] / nav.iloc[0]
    n_days = len(nav) - 1
    if n_days <= 0:
        return 0.0
    return total_return ** (252 / n_days) - 1
```

**Excel 公式：**
```
= (末日净值/首日净值) ^ (252 / (交易日数-1)) - 1
```

---

## 2. 年化波动率 (Annualized Volatility)

**公式：**

$$\sigma_{ann} = \text{std}(r_t) \times \sqrt{252}$$

其中 $r_t = \ln(NAV_t / NAV_{t-1})$ 为日对数收益率。

**Python：**
```python
def annualized_volatility(nav: pd.Series) -> float:
    """nav: 日频净值序列"""
    log_returns = np.log(nav / nav.shift(1)).dropna()
    return log_returns.std() * np.sqrt(252)
```

**Excel 公式：**
```
= STDEV(日收益率区域) * SQRT(252)
```

> **注意：** 使用对数收益率 `LN(B3/B2)` 而非简单收益率，因对数收益率可加性更好。Excel 中若已有简单收益率列，可直接用 `STDEV` 近似。

---

## 3. 最大回撤 (Maximum Drawdown)

**公式：**

$$MDD = \max_{t} \left(\frac{\text{RunningMax}_t - NAV_t}{\text{RunningMax}_t}\right)$$

**Python：**
```python
def max_drawdown(nav: pd.Series) -> float:
    """返回正数（如 0.15 表示回撤 15%）"""
    running_max = nav.cummax()
    drawdown = (running_max - nav) / running_max
    return drawdown.max()
```

**Excel 辅助列方法：**
```
辅助列 RunningMax:  C2 = MAX($B$2:B2)  （向下填充）
辅助列 Drawdown:    D2 = (C2 - B2) / C2
最大回撤:           = MAX(D:D)
```

---

## 4. 夏普比率 (Sharpe Ratio)

**公式：**

$$Sharpe = \frac{R_{ann} - R_f}{\sigma_{ann}}$$

其中 $R_f$ 为无风险利率，A 股通常取一年期定存利率（当前约 1.5%）或 0。

**Python：**
```python
def sharpe_ratio(nav: pd.Series, rf: float = 0.015) -> float:
    ann_ret = annualized_return(nav)
    ann_vol = annualized_volatility(nav)
    if ann_vol == 0:
        return 0.0
    return (ann_ret - rf) / ann_vol
```

**Excel 公式：**
```
= (年化收益率 - 无风险利率) / 年化波动率
```

---

## 5. 信息比率 (Information Ratio)

**公式：**

$$IR = \frac{R_{p,ann} - R_{b,ann}}{TE}$$

其中 $TE = \text{std}(r_p - r_b) \times \sqrt{252}$ 为年化跟踪误差。

**Python：**
```python
def information_ratio(nav_p: pd.Series, nav_b: pd.Series) -> float:
    """nav_p: 组合净值, nav_b: 基准净值（需对齐日期）"""
    ret_p = np.log(nav_p / nav_p.shift(1)).dropna()
    ret_b = np.log(nav_b / nav_b.shift(1)).dropna()
    # 对齐
    common = ret_p.index.intersection(ret_b.index)
    excess = ret_p.loc[common] - ret_b.loc[common]
    te = excess.std() * np.sqrt(252)
    if te == 0:
        return 0.0
    ann_excess = annualized_return(nav_p) - annualized_return(nav_b)
    return ann_excess / te
```

**Excel 公式：**
```
跟踪误差 = STDEV(组合日收益 - 基准日收益) * SQRT(252)
信息比率 = (组合年化 - 基准年化) / 跟踪误差
```

---

## 6. 卡尔玛比率 (Calmar Ratio)

**公式：**

$$Calmar = \frac{R_{ann}}{MDD}$$

**Python：**
```python
def calmar_ratio(nav: pd.Series) -> float:
    mdd = max_drawdown(nav)
    if mdd == 0:
        return 0.0
    return annualized_return(nav) / mdd
```

**Excel 公式：**
```
= 年化收益率 / 最大回撤
```

---

## 7. 索提诺比率 (Sortino Ratio)

**公式：**

$$Sortino = \frac{R_{ann} - R_f}{\sigma_{down}}$$

其中 $\sigma_{down} = \text{std}(\min(r_t - r_f/252, 0)) \times \sqrt{252}$ 为下行波动率。

**Python：**
```python
def sortino_ratio(nav: pd.Series, rf: float = 0.015) -> float:
    log_returns = np.log(nav / nav.shift(1)).dropna()
    daily_rf = rf / 252
    downside = log_returns[log_returns < daily_rf] - daily_rf
    if len(downside) == 0:
        return 0.0
    downside_vol = downside.std() * np.sqrt(252)
    if downside_vol == 0:
        return 0.0
    return (annualized_return(nav) - rf) / downside_vol
```

**Excel 公式：**
```
下行波动率辅助列: = IF(日收益<无风险日利率, 日收益-无风险日利率, 0)
下行标准差:       = STDEV(IF(辅助列<>0, 辅助列))  （Ctrl+Shift+Enter 数组公式）
索提诺比率:       = (年化收益 - 无风险利率) / (下行标准差 * SQRT(252))
```

---

## 8. 胜率 (Win Rate)

**公式：**

$$WinRate = \frac{\text{count}(r_t > 0)}{n}$$

**Python：**
```python
def win_rate(nav: pd.Series) -> float:
    daily_returns = nav.pct_change().dropna()
    if len(daily_returns) == 0:
        return 0.0
    return (daily_returns > 0).sum() / len(daily_returns)
```

**Excel 公式：**
```
= COUNTIF(日收益率区域, ">0") / COUNT(日收益率区域)
```

---

## Brinson 三因素归因

**公式：**

| 因子 | 公式 | 含义 |
|------|------|------|
| 配置效应 | $(w_p^i - w_b^i) \times (r_b^i - r_b)$ | 超配高收益行业的贡献 |
| 选股效应 | $w_b^i \times (r_p^i - r_b^i)$ | 行业内个股选择的贡献 |
| 交互效应 | $(w_p^i - w_b^i) \times (r_p^i - r_b^i)$ | 配置与选股的交叉项 |
| 总归因 | 配置 + 选股 + 交互 | 各因子之和 |

其中：
- $w_p^i$: 组合中行业 $i$ 的权重
- $w_b^i$: 基准中行业 $i$ 的权重
- $r_p^i$: 组合中行业 $i$ 的收益率
- $r_b^i$: 基准中行业 $i$ 的收益率
- $r_b$: 基准整体收益率

**Python：**
```python
def compute_brinson(
    port_weights: pd.Series,
    bench_weights: pd.Series,
    port_returns: pd.Series,
    bench_returns: pd.Series,
) -> pd.DataFrame:
    """
    port_weights:  组合行业权重 (index=行业名)
    bench_weights: 基准行业权重
    port_returns:  组合行业收益率
    bench_returns: 基准行业收益率
    """
    bench_total = (bench_weights * bench_returns).sum()

    allocation = (port_weights - bench_weights) * (bench_returns - bench_total)
    selection = bench_weights * (port_returns - bench_returns)
    interaction = (port_weights - bench_weights) * (port_returns - bench_returns)
    total = allocation + selection + interaction

    return pd.DataFrame({
        "配置效应": allocation,
        "选股效应": selection,
        "交互效应": interaction,
        "总归因": total,
    })
```

**Excel 公式（假设 A=行业, B=组合权重, C=基准权重, D=组合收益, E=基准收益）：**
```
基准整体收益 G1: = SUMPRODUCT(C:C, E:E)
配置效应 F2:     = (B2-C2) * (E2-$G$1)
选股效应 G2:     = C2 * (D2-E2)
交互效应 H2:     = (B2-C2) * (D2-E2)
总归因   I2:     = F2 + G2 + H2
```

---

## 辅助函数

### 对齐两个净值序列

```python
def align_nav(nav1: pd.Series, nav2: pd.Series) -> tuple[pd.Series, pd.Series]:
    """按日期取交集并对齐"""
    common = nav1.index.intersection(nav2.index)
    return nav1.loc[common], nav2.loc[common]
```

### 滚动波动率

```python
def rolling_volatility(nav: pd.Series, window: int = 20) -> pd.Series:
    """window 日滚动年化波动率"""
    log_ret = np.log(nav / nav.shift(1))
    return log_ret.rolling(window).std() * np.sqrt(252)
```

### 回撤序列

```python
def drawdown_series(nav: pd.Series) -> pd.Series:
    """返回每日回撤幅度（正数表示回撤）"""
    running_max = nav.cummax()
    return (running_max - nav) / running_max
```

### Top-N 回撤

```python
def top_drawdowns(nav: pd.Series, n: int = 5) -> pd.DataFrame:
    """提取前 N 次最大回撤的起止日期和幅度"""
    dd = drawdown_series(nav)
    results = []
    remaining = dd.copy()
    for _ in range(n):
        if remaining.max() == 0:
            break
        end_idx = remaining.idxmax()
        # 向前找到回撤起点（上一个0回撤点）
        before = remaining.loc[:end_idx]
        start_candidates = before[before == 0]
        start_idx = start_candidates.index[-1] if len(start_candidates) > 0 else before.index[0]
        results.append({
            "起始日期": start_idx,
            "最低点日期": end_idx,
            "回撤幅度": remaining[end_idx],
        })
        # 清除这段区间
        remaining.loc[start_idx:end_idx] = 0
    return pd.DataFrame(results)
```
