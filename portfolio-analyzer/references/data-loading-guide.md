# 数据加载指南

## 概述

投资组合 Excel 文件包含 5 张表（sheet），每张表结构不同。`load_portfolio_data()` 通过**特征列匹配**自动识别表类型，无需依赖 sheet 名称。

---

## 表 1：时序分析（NAV 时序数据）

### 识别特征
- 含有"日期"列 + "单位净值"或"累计净值"列
- 或含有"日期" + "组合代码"/"组合名称" + "净值"列

### 列映射

| 原始列名（可能变体） | 标准化列名 | dtype | 必需 |
|---------------------|-----------|-------|------|
| 日期 / 交易日期 / Date | date | datetime64 | 是 |
| 组合代码 / 组合编码 / PortCode | portfolio_code | str | 是 |
| 组合名称 / 组合简称 / PortName | portfolio_name | str | 否 |
| 单位净值 / 净值 / NAV | nav | float64 | 是 |
| 累计净值 / AccNav | acc_nav | float64 | 否 |
| 日收益率 / DailyReturn | daily_return | float64 | 否 |
| 累计收益率 / AccReturn | acc_return | float64 | 否 |

### 解析规则

```python
# 列名模糊匹配规则
COLUMN_PATTERNS_NAV = {
    "date": ["日期", "交易日期", "Date", "TradeDate"],
    "portfolio_code": ["组合代码", "组合编码", "PortCode", "产品代码"],
    "portfolio_name": ["组合名称", "组合简称", "PortName", "产品名称"],
    "nav": ["单位净值", "净值", "NAV", "UnitNAV"],
    "acc_nav": ["累计净值", "AccNAV", "累计单位净值"],
    "daily_return": ["日收益率", "DailyReturn", "日回报"],
    "acc_return": ["累计收益率", "AccReturn", "累计回报"],
}
```

### Pivot 逻辑
长表（多组合在同一列）→ pivot 为宽表，每列为一个组合的净值序列：

```python
# 输入：长表
#   date | portfolio_code | nav
#   2026-01-02 | P001 | 1.0000
#   2026-01-02 | P002 | 1.0000
#   2026-01-03 | P001 | 1.0050

# 输出：宽表
#            | P001   | P002
# 2026-01-02 | 1.0000 | 1.0000
# 2026-01-03 | 1.0050 | NaN

nav_wide = df.pivot(index="date", columns="portfolio_code", values="nav")
nav_wide = nav_wide.sort_index().ffill()  # 前向填充缺失值
```

---

## 表 2：交易明细

### 识别特征
- 含有"证券代码"/"股票代码" + "成交金额"/"交易金额"列
- 或含有"买卖方向"/"交易方向"列

### 列映射

| 原始列名 | 标准化列名 | dtype | 必需 |
|---------|-----------|-------|------|
| 日期 / 交易日期 | date | datetime64 | 是 |
| 组合代码 | portfolio_code | str | 是 |
| 证券代码 / 股票代码 | sec_code | str | 是 |
| 证券名称 / 股票名称 | sec_name | str | 否 |
| 买卖方向 / 交易方向 | direction | str | 是 |
| 成交数量 / 交易数量 | volume | float64 | 是 |
| 成交价格 / 交易价格 | price | float64 | 是 |
| 成交金额 / 交易金额 | amount | float64 | 是 |
| 手续费 / 佣金 | commission | float64 | 否 |

### 处理规则
- **直接透传**，不做 pivot
- 统一买卖方向标签：买入/B → "买入"，卖出/S → "卖出"
- 确保 amount 为正数（卖出交易不取负）

---

## 表 3：收益贡献

### 识别特征
- 含有"收益贡献"/"收益率贡献"/"绝对收益率贡献"列
- 或含有"持仓市值" + "收益"列

### 列映射

| 原始列名 | 标准化列名 | dtype | 必需 |
|---------|-----------|-------|------|
| 组合代码 | portfolio_code | str | 是 |
| 证券代码 / 股票代码 | sec_code | str | 是 |
| 证券名称 / 股票名称 | sec_name | str | 否 |
| 行业 / 所属行业 / 申万行业 | industry | str | 否 |
| 持仓市值 / 市值 | market_value | float64 | 否 |
| 权重 / 持仓权重 | weight | float64 | 否 |
| 收益率 / 个股收益率 | sec_return | float64 | 否 |
| 收益贡献 / 收益率贡献 / 绝对收益率贡献 | return_contrib | float64 | 是 |

### 处理规则
- 按 `return_contrib` 绝对值降序排序
- 便于输出 Top/Bottom 贡献个股

---

## 表 4：业绩归因（资产大类）

### 识别特征
- 含有"资产大类"/"资产类别"列
- 或含有"配置效应"/"选股效应"列（排除含"行业"相关列的表）

### 列映射

| 原始列名 | 标准化列名 | dtype | 必需 |
|---------|-----------|-------|------|
| 组合代码 | portfolio_code | str | 是 |
| 资产大类 / 大类资产 | asset_class | str | 是 |
| 资产类别 / 子类 | asset_subclass | str | 否 |
| 组合权重 / 实际权重 | port_weight | float64 | 是 |
| 基准权重 | bench_weight | float64 | 是 |
| 组合收益 / 实际收益 | port_return | float64 | 是 |
| 基准收益 | bench_return | float64 | 是 |
| 配置效应 | allocation | float64 | 否 |
| 选股效应 | selection | float64 | 否 |
| 交互效应 | interaction | float64 | 否 |
| 总归因 / 超额收益 | total_attribution | float64 | 否 |

### 层级结构
资产大类 → 资产类别为两级层级，Excel 输出时应体现父子关系：

```
股票
  ├── 主板
  ├── 创业板
  └── 科创板
债券
  ├── 利率债
  └── 信用债
现金
```

---

## 表 5：行业归因

### 识别特征
- 含有"行业"列 + "配置效应"/"选股效应"列
- 且不含"资产大类"/"资产类别"列（与表 4 区分）

### 列映射

| 原始列名 | 标准化列名 | dtype | 必需 |
|---------|-----------|-------|------|
| 组合代码 | portfolio_code | str | 是 |
| 行业 / 行业名称 / 申万行业 | industry | str | 是 |
| 组合权重 / 行业权重 | port_weight | float64 | 是 |
| 基准权重 | bench_weight | float64 | 是 |
| 组合收益 / 行业收益 | port_return | float64 | 是 |
| 基准收益 | bench_return | float64 | 是 |
| 配置效应 | allocation | float64 | 否 |
| 选股效应 | selection | float64 | 否 |
| 交互效应 | interaction | float64 | 否 |
| 总归因 / 超额收益 | total_attribution | float64 | 否 |

### 行业代码匹配
使用 `shenwan-industry-codes.md` 中的模糊匹配表，将用户 Excel 中的行业名称映射到标准申万一级行业代码：

```python
# 模糊匹配逻辑
def match_industry(name: str) -> str | None:
    """将行业名称匹配到 Wind 指数代码"""
    for code, standard_name in SHENWAN_L1_NAMES.items():
        if standard_name in name or name in standard_name:
            return code
    # 简称匹配
    ALIASES = {"家电": "家用电器", "非银": "非银金融", "电新": "电力设备", ...}
    if name in ALIASES:
        return match_industry(ALIASES[name])
    return None
```

---

## 表识别算法

```python
def identify_sheet(df: pd.DataFrame) -> str:
    """根据特征列识别表类型"""
    cols = set(c.strip() for c in df.columns)

    # 关键词集合
    nav_keywords = {"单位净值", "累计净值", "NAV", "净值"}
    trade_keywords = {"成交金额", "交易金额", "买卖方向", "交易方向"}
    contrib_keywords = {"收益贡献", "收益率贡献", "绝对收益率贡献"}
    asset_keywords = {"资产大类", "大类资产", "资产类别"}
    industry_keywords = {"行业", "行业名称", "申万行业"}
    brinson_keywords = {"配置效应", "选股效应"}

    if cols & nav_keywords:
        return "nav_timeseries"
    if cols & trade_keywords:
        return "trade_detail"
    if cols & contrib_keywords:
        return "return_contribution"
    if cols & asset_keywords:
        return "asset_attribution"
    if (cols & industry_keywords) and (cols & brinson_keywords):
        return "industry_attribution"

    return "unknown"
```

---

## 通用解析配置

### 日期解析
```python
# 支持多种日期格式
DATE_FORMATS = [
    "%Y-%m-%d",      # 2026-01-02
    "%Y/%m/%d",      # 2026/01/02
    "%Y%m%d",        # 20260102
    "%Y-%m-%d %H:%M:%S",  # 带时间
]
```

### 数值清洗
```python
def clean_numeric(s: pd.Series) -> pd.Series:
    """清洗数值列：去除百分号、逗号、空格"""
    if s.dtype == object:
        s = s.str.replace("%", "", regex=False)
        s = s.str.replace(",", "", regex=False)
        s = s.str.strip()
    return pd.to_numeric(s, errors="coerce")
```

### 百分比检测
```python
def detect_percentage(s: pd.Series) -> bool:
    """检测列值是否为百分比形式（值域 -100 ~ 100 而非 -1 ~ 1）"""
    valid = s.dropna()
    if len(valid) == 0:
        return False
    return valid.abs().max() > 1.0 and valid.abs().max() <= 100.0
```
