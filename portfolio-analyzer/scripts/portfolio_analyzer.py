"""
投资组合分析引擎 — 数据加载 + 风险指标 + Brinson 归因。

用法:
    import sys, os
    sys.path.insert(0, os.path.expanduser("~/.claude/skills/portfolio-analyzer/scripts"))
    from portfolio_analyzer import (
        load_portfolio_data,
        fetch_benchmark,
        fetch_shenwan_returns,
        compute_risk_metrics,
        compute_brinson,
    )

依赖:
    - pandas, numpy, openpyxl
    - windpy-sdk/scripts/wind_client.py (fetch_benchmark, fetch_shenwan_returns)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Wind 客户端（延迟导入，仅在 fetch 函数中使用）
# ---------------------------------------------------------------------------
_WIND_CLIENT_DIR = str(
    Path(__file__).resolve().parent.parent.parent / "windpy-sdk" / "scripts"
)


def _get_wind_client():
    """延迟导入 wind_client，避免非 Windows 环境报错。"""
    if _WIND_CLIENT_DIR not in sys.path:
        sys.path.insert(0, _WIND_CLIENT_DIR)
    import wind_client
    return wind_client


# ---------------------------------------------------------------------------
# 申万一级行业代码
# ---------------------------------------------------------------------------
SHENWAN_L1_CODES = [
    "801010.SI", "801020.SI", "801030.SI", "801040.SI", "801050.SI",
    "801080.SI", "801880.SI", "801110.SI", "801120.SI", "801130.SI",
    "801140.SI", "801150.SI", "801160.SI", "801170.SI", "801180.SI",
    "801200.SI", "801210.SI", "801780.SI", "801790.SI", "801720.SI",
    "801710.SI", "801730.SI", "801740.SI", "801750.SI", "801760.SI",
    "801770.SI", "801950.SI", "801960.SI", "801970.SI", "801890.SI",
    "801980.SI",
]

SHENWAN_L1_NAMES = {
    "801010.SI": "农林牧渔", "801020.SI": "采掘",     "801030.SI": "化工",
    "801040.SI": "钢铁",     "801050.SI": "有色金属", "801080.SI": "电子",
    "801880.SI": "汽车",     "801110.SI": "家用电器", "801120.SI": "食品饮料",
    "801130.SI": "纺织服饰", "801140.SI": "轻工制造", "801150.SI": "医药生物",
    "801160.SI": "公用事业", "801170.SI": "交通运输", "801180.SI": "房地产",
    "801200.SI": "商贸零售", "801210.SI": "社会服务", "801780.SI": "银行",
    "801790.SI": "非银金融", "801720.SI": "建筑装饰", "801710.SI": "建筑材料",
    "801730.SI": "电力设备", "801740.SI": "国防军工", "801750.SI": "计算机",
    "801760.SI": "传媒",     "801770.SI": "通信",     "801950.SI": "煤炭",
    "801960.SI": "石油石化", "801970.SI": "环保",     "801890.SI": "机械设备",
    "801980.SI": "美容护理",
}

# 行业名称别名 → 标准名
_INDUSTRY_ALIASES = {
    "农业": "农林牧渔", "有色": "有色金属", "家电": "家用电器",
    "食品": "食品饮料", "医药": "医药生物", "生物医药": "医药生物",
    "地产": "房地产",   "商贸": "商贸零售", "零售": "商贸零售",
    "军工": "国防军工", "非银": "非银金融", "电新": "电力设备",
    "新能源": "电力设备", "建材": "建筑材料", "建筑": "建筑装饰",
}

# 反向映射: 标准名 → Wind 代码
_NAME_TO_CODE = {v: k for k, v in SHENWAN_L1_NAMES.items()}


def match_industry(name: str) -> str | None:
    """将行业名称模糊匹配到 Wind 申万一级行业指数代码。"""
    name = name.strip()
    # 精确匹配
    if name in _NAME_TO_CODE:
        return _NAME_TO_CODE[name]
    # 别名匹配
    if name in _INDUSTRY_ALIASES:
        return _NAME_TO_CODE.get(_INDUSTRY_ALIASES[name])
    # 包含匹配
    for standard_name, code in _NAME_TO_CODE.items():
        if standard_name in name or name in standard_name:
            return code
    return None


# ===================================================================
# 1. load_portfolio_data — 解析 Excel 中的 5 张表
# ===================================================================

# 列名模糊匹配模式
_COL_PATTERNS = {
    # 时序分析
    "date": ["日期", "交易日期", "Date", "TradeDate", "trade_date"],
    "portfolio_code": ["组合代码", "组合编码", "PortCode", "产品代码", "port_code"],
    "portfolio_name": ["组合名称", "组合简称", "PortName", "产品名称", "port_name"],
    "nav": ["单位净值", "净值", "NAV", "UnitNAV", "unit_nav"],
    "acc_nav": ["累计净值", "AccNAV", "累计单位净值", "acc_nav"],
    "daily_return": ["日收益率", "DailyReturn", "日回报", "daily_return"],
    "acc_return": ["累计收益率", "AccReturn", "累计回报", "acc_return"],
    # 交易明细
    "sec_code": ["证券代码", "股票代码", "SecCode", "sec_code", "wind_code"],
    "sec_name": ["证券名称", "股票名称", "SecName", "sec_name"],
    "direction": ["买卖方向", "交易方向", "Direction", "direction", "side"],
    "volume": ["成交数量", "交易数量", "Volume", "volume"],
    "price": ["成交价格", "交易价格", "Price", "price"],
    "amount": ["成交金额", "交易金额", "Amount", "amount"],
    "commission": ["手续费", "佣金", "Commission", "commission"],
    # 收益贡献
    "industry": ["行业", "行业名称", "申万行业", "Industry", "industry", "所属行业"],
    "market_value": ["持仓市值", "市值", "MarketValue", "market_value"],
    "weight": ["权重", "持仓权重", "Weight", "weight"],
    "sec_return": ["收益率", "个股收益率", "SecReturn", "sec_return"],
    "return_contrib": ["收益贡献", "收益率贡献", "绝对收益率贡献", "ReturnContrib", "return_contrib"],
    # 业绩归因
    "asset_class": ["资产大类", "大类资产", "AssetClass", "asset_class"],
    "asset_subclass": ["资产类别", "子类", "AssetSubclass", "asset_subclass"],
    "port_weight": ["组合权重", "实际权重", "PortWeight", "port_weight", "行业权重"],
    "bench_weight": ["基准权重", "BenchWeight", "bench_weight"],
    "port_return": ["组合收益", "实际收益", "PortReturn", "port_return", "行业收益"],
    "bench_return": ["基准收益", "BenchReturn", "bench_return"],
    "allocation": ["配置效应", "Allocation", "allocation"],
    "selection": ["选股效应", "Selection", "selection"],
    "interaction": ["交互效应", "Interaction", "interaction"],
    "total_attribution": ["总归因", "超额收益", "TotalAttribution", "total_attribution"],
}


def _match_columns(df: pd.DataFrame) -> dict[str, str]:
    """将 DataFrame 列名映射到标准化列名。返回 {标准名: 原始列名}。"""
    mapping = {}
    cols = list(df.columns)
    for std_name, patterns in _COL_PATTERNS.items():
        for pat in patterns:
            for col in cols:
                if col.strip() == pat:
                    mapping[std_name] = col
                    break
            if std_name in mapping:
                break
    return mapping


def _rename_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """用标准化列名重命名 DataFrame。"""
    reverse = {v: k for k, v in mapping.items()}
    return df.rename(columns=reverse)


def _identify_sheet(df: pd.DataFrame) -> str:
    """根据特征列识别表类型。"""
    cols = {c.strip() for c in df.columns}

    nav_kw = {"单位净值", "累计净值", "NAV", "净值", "UnitNAV", "unit_nav"}
    trade_kw = {"成交金额", "交易金额", "买卖方向", "交易方向", "Amount", "Direction"}
    contrib_kw = {"收益贡献", "收益率贡献", "绝对收益率贡献", "ReturnContrib", "return_contrib"}
    asset_kw = {"资产大类", "大类资产", "AssetClass", "asset_class"}
    industry_kw = {"行业", "行业名称", "申万行业", "Industry", "industry", "所属行业"}
    brinson_kw = {"配置效应", "选股效应", "Allocation", "Selection", "allocation", "selection"}

    if cols & nav_kw:
        return "nav_timeseries"
    if cols & trade_kw:
        return "trade_detail"
    if cols & contrib_kw:
        return "return_contribution"
    if cols & asset_kw:
        return "asset_attribution"
    if (cols & industry_kw) and (cols & brinson_kw):
        return "industry_attribution"
    return "unknown"


def _clean_numeric(s: pd.Series) -> pd.Series:
    """清洗数值列：去除百分号、逗号、空格。"""
    if s.dtype == object:
        s = s.str.replace("%", "", regex=False)
        s = s.str.replace(",", "", regex=False)
        s = s.str.strip()
    return pd.to_numeric(s, errors="coerce")


def _detect_percentage(s: pd.Series) -> bool:
    """检测列值是否为百分比形式（值域 ±100 而非 ±1）。"""
    valid = s.dropna()
    if len(valid) == 0:
        return False
    return valid.abs().max() > 1.0 and valid.abs().max() <= 100.0


_DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"]


def _parse_dates(s: pd.Series) -> pd.Series:
    """尝试多种格式解析日期列。"""
    for fmt in _DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(s, errors="coerce")


def _process_nav_sheet(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """处理时序分析表：标准化列名、日期解析、pivot 为宽表。"""
    df = _rename_columns(df, mapping)
    if "date" in df.columns:
        df["date"] = _parse_dates(df["date"])
    if "nav" in df.columns:
        df["nav"] = _clean_numeric(df["nav"])

    # 如果有组合代码列，pivot 为宽表
    if "portfolio_code" in df.columns and "nav" in df.columns:
        nav_wide = df.pivot_table(index="date", columns="portfolio_code", values="nav")
        nav_wide = nav_wide.sort_index().ffill()
        return nav_wide
    return df


def _process_trade_sheet(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """处理交易明细表：标准化、统一买卖方向。"""
    df = _rename_columns(df, mapping)
    if "date" in df.columns:
        df["date"] = _parse_dates(df["date"])
    for col in ["volume", "price", "amount", "commission"]:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])
    # 统一买卖方向
    if "direction" in df.columns:
        df["direction"] = df["direction"].str.strip().replace(
            {"B": "买入", "S": "卖出", "买": "买入", "卖": "卖出"}
        )
    return df


def _process_contrib_sheet(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """处理收益贡献表：标准化、按贡献绝对值排序。"""
    df = _rename_columns(df, mapping)
    for col in ["market_value", "weight", "sec_return", "return_contrib"]:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])
            if col in ("sec_return", "return_contrib", "weight") and _detect_percentage(df[col]):
                df[col] = df[col] / 100
    if "return_contrib" in df.columns:
        df = df.sort_values("return_contrib", key=abs, ascending=False)
    return df


def _process_attribution_sheet(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """处理归因表（资产大类/行业）：标准化数值列。"""
    df = _rename_columns(df, mapping)
    numeric_cols = [
        "port_weight", "bench_weight", "port_return", "bench_return",
        "allocation", "selection", "interaction", "total_attribution",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])
            if _detect_percentage(df[col]):
                df[col] = df[col] / 100
    return df


def load_portfolio_data(filepath: str) -> dict[str, pd.DataFrame]:
    """
    加载投资组合 Excel 文件，自动识别 5 张表并解析。

    Parameters
    ----------
    filepath : str
        Excel 文件路径

    Returns
    -------
    dict
        键为表类型，值为解析后的 DataFrame:
        - "nav_timeseries": 净值宽表（列=组合，index=日期）
        - "trade_detail": 交易明细
        - "return_contribution": 收益贡献（按绝对值排序）
        - "asset_attribution": 资产大类归因
        - "industry_attribution": 行业归因
    """
    xls = pd.ExcelFile(filepath)
    result = {}

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        if df.empty:
            continue

        sheet_type = _identify_sheet(df)
        if sheet_type == "unknown":
            continue

        mapping = _match_columns(df)

        if sheet_type == "nav_timeseries":
            result[sheet_type] = _process_nav_sheet(df, mapping)
        elif sheet_type == "trade_detail":
            result[sheet_type] = _process_trade_sheet(df, mapping)
        elif sheet_type == "return_contribution":
            result[sheet_type] = _process_contrib_sheet(df, mapping)
        elif sheet_type == "asset_attribution":
            result[sheet_type] = _process_attribution_sheet(df, mapping)
        elif sheet_type == "industry_attribution":
            result[sheet_type] = _process_attribution_sheet(df, mapping)

    return result


# ===================================================================
# 2. fetch_benchmark — 获取基准净值数据
# ===================================================================

def fetch_benchmark(
    code: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    """
    通过 Wind 获取基准指数净值（收盘价）。

    Parameters
    ----------
    code : str
        基准指数代码，如 "000300.SH"（沪深 300）
    start : str
        起始日期，如 "2025-01-01"
    end : str
        结束日期，如 "2026-02-27"

    Returns
    -------
    pd.DataFrame
        columns: ["close"]，index: DatetimeIndex(name="date")
    """
    wc = _get_wind_client()
    df = wc.wsd(code, "close", start, end)
    return df


# ===================================================================
# 3. fetch_shenwan_returns — 获取 31 行业收益率
# ===================================================================

def fetch_shenwan_returns(
    start: str,
    end: str,
) -> pd.DataFrame:
    """
    通过 Wind 获取 31 个申万一级行业指数的区间涨跌幅。

    Parameters
    ----------
    start : str
        起始日期
    end : str
        结束日期

    Returns
    -------
    pd.DataFrame
        index: 行业名称，columns: ["code", "pct_chg"]
    """
    wc = _get_wind_client()
    codes = ",".join(SHENWAN_L1_CODES)
    df = wc.wss(codes, "pct_chg_per", f"startDate={start};endDate={end}")

    # 添加行业名称
    df["industry"] = df.index.map(SHENWAN_L1_NAMES)
    df = df.rename(columns={"PCT_CHG_PER": "pct_chg"})
    if "pct_chg" in df.columns:
        df["pct_chg"] = df["pct_chg"] / 100  # Wind 返回百分比数值
    df["code"] = df.index
    df = df.set_index("industry")
    return df[["code", "pct_chg"]]


# ===================================================================
# 3b. fetch_benchmark_industry_weights — 基准指数的行业权重
# ===================================================================

def fetch_benchmark_industry_weights(
    index_code: str,
    date: str,
) -> pd.Series:
    """
    获取基准指数在指定日期的申万一级行业权重分布。

    步骤:
    1. wset("indexconstituent") 拉取指数成分股及权重
    2. wss() 查每只成分股的申万一级行业
    3. 按行业聚合权重

    Parameters
    ----------
    index_code : str
        指数代码，如 "000300.SH"
    date : str
        日期，如 "20260227" 或 "2026-02-27"

    Returns
    -------
    pd.Series
        index=行业名称, values=权重（0~1 之间），合计为 1
    """
    wc = _get_wind_client()
    date_str = date.replace("-", "")

    # 1. 获取指数成分股及权重
    constituents = wc.wset(
        "indexconstituent",
        f"date={date_str};windcode={index_code}",
    )
    # wset 返回列名通常为: wind_code, sec_name, i_weight 等
    # 列名可能为大写或小写，做容错处理
    cols_lower = {c.lower(): c for c in constituents.columns}

    code_col = cols_lower.get("wind_code", cols_lower.get("windcode"))
    weight_col = cols_lower.get("i_weight", cols_lower.get("weight"))

    if code_col is None or weight_col is None:
        raise ValueError(
            f"无法识别成分股列名，实际列: {list(constituents.columns)}"
        )

    stocks = constituents[code_col].tolist()
    weights = pd.to_numeric(constituents[weight_col], errors="coerce").values

    if not stocks:
        raise ValueError(f"指数 {index_code} 在 {date} 无成分股数据")

    # 2. 查每只成分股的申万一级行业
    #    分批查询（wss 一次最多约 100 只）
    batch_size = 80
    industry_map = {}
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i : i + batch_size]
        codes_str = ",".join(batch)
        ind_df = wc.wss(
            codes_str,
            "industry_sw",
            f"tradeDate={date_str};industryType=1",
        )
        for code in batch:
            if code in ind_df.index:
                val = ind_df.loc[code, "INDUSTRY_SW"]
                industry_map[code] = val if pd.notna(val) else "其他"
            else:
                industry_map[code] = "其他"

    # 3. 按行业聚合权重
    records = []
    for code, w in zip(stocks, weights):
        ind_name = industry_map.get(code, "其他")
        records.append({"industry": ind_name, "weight": w})

    agg = pd.DataFrame(records).groupby("industry")["weight"].sum()
    # 归一化为 0~1
    total = agg.sum()
    if total > 0:
        agg = agg / total

    return agg.sort_values(ascending=False)


# ===================================================================
# 4. compute_risk_metrics — 计算风险指标
# ===================================================================

def annualized_return(nav: pd.Series) -> float:
    """年化收益率。nav: 日频净值序列。"""
    total_return = nav.iloc[-1] / nav.iloc[0]
    n_days = len(nav) - 1
    if n_days <= 0:
        return 0.0
    return float(total_return ** (252 / n_days) - 1)


def annualized_volatility(nav: pd.Series) -> float:
    """年化波动率（基于对数收益率）。"""
    log_returns = np.log(nav / nav.shift(1)).dropna()
    if len(log_returns) == 0:
        return 0.0
    return float(log_returns.std() * np.sqrt(252))


def max_drawdown(nav: pd.Series) -> float:
    """最大回撤（返回正数，如 0.15 表示 15%）。"""
    running_max = nav.cummax()
    drawdown = (running_max - nav) / running_max
    return float(drawdown.max())


def sharpe_ratio(nav: pd.Series, rf: float = 0.015) -> float:
    """夏普比率。rf: 年化无风险利率，默认 1.5%。"""
    ann_ret = annualized_return(nav)
    ann_vol = annualized_volatility(nav)
    if ann_vol == 0:
        return 0.0
    return float((ann_ret - rf) / ann_vol)


def information_ratio(nav_p: pd.Series, nav_b: pd.Series) -> float:
    """信息比率。nav_p: 组合净值, nav_b: 基准净值（需日期对齐）。"""
    ret_p = np.log(nav_p / nav_p.shift(1)).dropna()
    ret_b = np.log(nav_b / nav_b.shift(1)).dropna()
    common = ret_p.index.intersection(ret_b.index)
    if len(common) == 0:
        return 0.0
    excess = ret_p.loc[common] - ret_b.loc[common]
    te = excess.std() * np.sqrt(252)
    if te == 0:
        return 0.0
    ann_excess = annualized_return(nav_p) - annualized_return(nav_b)
    return float(ann_excess / te)


def calmar_ratio(nav: pd.Series) -> float:
    """卡尔玛比率 = 年化收益 / 最大回撤。"""
    mdd = max_drawdown(nav)
    if mdd == 0:
        return 0.0
    return float(annualized_return(nav) / mdd)


def sortino_ratio(nav: pd.Series, rf: float = 0.015) -> float:
    """索提诺比率。"""
    log_returns = np.log(nav / nav.shift(1)).dropna()
    daily_rf = rf / 252
    downside = log_returns[log_returns < daily_rf] - daily_rf
    if len(downside) == 0:
        return 0.0
    downside_vol = downside.std() * np.sqrt(252)
    if downside_vol == 0:
        return 0.0
    return float((annualized_return(nav) - rf) / downside_vol)


def win_rate(nav: pd.Series) -> float:
    """胜率：正收益天数占比。"""
    daily_returns = nav.pct_change().dropna()
    if len(daily_returns) == 0:
        return 0.0
    return float((daily_returns > 0).sum() / len(daily_returns))


def compute_risk_metrics(
    nav: pd.Series,
    benchmark: pd.Series | None = None,
    rf: float = 0.015,
) -> dict[str, float]:
    """
    计算全套风险指标。

    Parameters
    ----------
    nav : pd.Series
        组合日频净值序列（index 为日期）
    benchmark : pd.Series, optional
        基准日频净值序列（用于计算信息比率）
    rf : float
        年化无风险利率，默认 1.5%

    Returns
    -------
    dict
        包含 8 个指标的字典
    """
    metrics = {
        "年化收益率": annualized_return(nav),
        "年化波动率": annualized_volatility(nav),
        "最大回撤": max_drawdown(nav),
        "夏普比率": sharpe_ratio(nav, rf),
        "卡尔玛比率": calmar_ratio(nav),
        "索提诺比率": sortino_ratio(nav, rf),
        "胜率": win_rate(nav),
    }

    if benchmark is not None:
        metrics["信息比率"] = information_ratio(nav, benchmark)
    else:
        metrics["信息比率"] = None

    return metrics


# ===================================================================
# 5. compute_brinson — Brinson 三因素归因
# ===================================================================

def compute_brinson(
    port_weights: pd.Series,
    bench_weights: pd.Series,
    port_returns: pd.Series,
    bench_returns: pd.Series,
) -> pd.DataFrame:
    """
    Brinson 三因素归因（配置 + 选股 + 交互）。

    Parameters
    ----------
    port_weights : pd.Series
        组合行业权重，index=行业名
    bench_weights : pd.Series
        基准行业权重
    port_returns : pd.Series
        组合行业收益率
    bench_returns : pd.Series
        基准行业收益率

    Returns
    -------
    pd.DataFrame
        columns: ["配置效应", "选股效应", "交互效应", "总归因"]
        index: 行业名称
    """
    # 对齐行业（取并集，缺失补 0）
    all_industries = (
        port_weights.index
        .union(bench_weights.index)
        .union(port_returns.index)
        .union(bench_returns.index)
    )
    pw = port_weights.reindex(all_industries, fill_value=0)
    bw = bench_weights.reindex(all_industries, fill_value=0)
    pr = port_returns.reindex(all_industries, fill_value=0)
    br = bench_returns.reindex(all_industries, fill_value=0)

    bench_total = (bw * br).sum()

    allocation = (pw - bw) * (br - bench_total)
    selection_ = bw * (pr - br)
    interaction_ = (pw - bw) * (pr - br)
    total = allocation + selection_ + interaction_

    result = pd.DataFrame({
        "配置效应": allocation,
        "选股效应": selection_,
        "交互效应": interaction_,
        "总归因": total,
    })

    return result.sort_values("总归因", ascending=False)


# ===================================================================
# 辅助分析函数
# ===================================================================

def align_nav(nav1: pd.Series, nav2: pd.Series) -> tuple[pd.Series, pd.Series]:
    """按日期取交集并对齐两个净值序列。"""
    common = nav1.index.intersection(nav2.index)
    return nav1.loc[common], nav2.loc[common]


def rolling_volatility(nav: pd.Series, window: int = 20) -> pd.Series:
    """滚动年化波动率。"""
    log_ret = np.log(nav / nav.shift(1))
    return log_ret.rolling(window).std() * np.sqrt(252)


def drawdown_series(nav: pd.Series) -> pd.Series:
    """每日回撤幅度（正数表示回撤）。"""
    running_max = nav.cummax()
    return (running_max - nav) / running_max


def top_drawdowns(nav: pd.Series, n: int = 5) -> pd.DataFrame:
    """提取前 N 次最大回撤的起止日期和幅度。"""
    dd = drawdown_series(nav)
    results = []
    remaining = dd.copy()

    for _ in range(n):
        if remaining.max() == 0:
            break
        end_idx = remaining.idxmax()
        before = remaining.loc[:end_idx]
        start_candidates = before[before == 0]
        start_idx = start_candidates.index[-1] if len(start_candidates) > 0 else before.index[0]
        results.append({
            "起始日期": start_idx,
            "最低点日期": end_idx,
            "回撤幅度": remaining[end_idx],
        })
        remaining.loc[start_idx:end_idx] = 0

    return pd.DataFrame(results)


def cumulative_return(nav: pd.Series) -> pd.Series:
    """累计收益率序列。"""
    return nav / nav.iloc[0] - 1


def daily_returns(nav: pd.Series) -> pd.Series:
    """日收益率序列。"""
    return nav.pct_change().dropna()
