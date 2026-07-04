"""
Wind 客户端 — 直连 WindPy，自动检测登录状态，返回 pandas DataFrame。

用法:
    from wind_client import wsd, wss, wset, wsq, edb, health
    from wind_client import wsi, wst, wsee, wses, wsed
    from wind_client import tdays, tdaysoffset, tdayscount
    from wind_client import weqs, htocode, wai, wgel

    df = wsd("000300.SH", "close,pct_chg", "-30D")
    df = wss("600519.SH,000858.SZ", "sec_name,close,pe_ttm", "tradeDate=20241231")
    df = wset("sectorconstituent", "date=20241231;windcode=000300.SH")
    df = wsq("600519.SH", "rt_last,rt_pct_chg")
    df = edb("M0001383", "2024-01-01", "2024-12-31")
    dates = tdays("20260101", "20260226")
"""

import os
import re
import sys
import atexit
import pandas as pd

# ---------------------------------------------------------------------------
# WindPy 连接管理
# ---------------------------------------------------------------------------
_w = None


def _check_auto_login() -> bool:
    """检查 Wind 是否配置了自动登录。"""
    config_path = os.path.expanduser("~/.Wind/WFT/users/Auth/user.config")
    if not os.path.exists(config_path):
        return False
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'isAutoLogin="(\d+)"', content)
        return match is not None and match.group(1) == "1"
    except Exception:
        return False


def _ensure_connected():
    """确保 WindPy 已连接，首次调用时自动 w.start()。"""
    global _w
    if _w is not None and _w.isconnected():
        return _w

    from WindPy import w as _wind
    _w = _wind

    if _w.isconnected():
        return _w

    if not _check_auto_login():
        print("[wind_client] 警告: Wind 未开启自动登录，可能弹出登录窗口", file=sys.stderr)
        print("[wind_client] 请在 Wind 终端设置中勾选「自动登录」", file=sys.stderr)

    ret = _w.start(waitTime=30)
    if not _w.isconnected():
        raise RuntimeError(f"Wind 连接失败: {ret}")

    atexit.register(_cleanup)
    return _w


def _cleanup():
    global _w
    if _w is not None and _w.isconnected():
        _w.stop()
        _w = None


# ---------------------------------------------------------------------------
# WindData → DataFrame 转换
# ---------------------------------------------------------------------------

def _is_synthetic_codes(codes: list) -> bool:
    """判断 Codes 是否为 wset 返回的行号 ("1","2","3",...)。"""
    if not codes:
        return False
    return all(isinstance(c, str) and c.isdigit() for c in codes[:10])


def _serialize_times(times) -> list:
    """将 WindData.Times 转为字符串列表。"""
    if not times:
        return []
    return [str(t) for t in times]


def _to_dataframe(result, endpoint: str = "") -> pd.DataFrame:
    """将 WindData 对象转为 DataFrame。"""
    if hasattr(result, 'ErrorCode') and result.ErrorCode != 0:
        raise RuntimeError(f"Wind error {result.ErrorCode}: {result.Data}")

    data = result.Data if hasattr(result, 'Data') and result.Data else []
    fields = result.Fields if hasattr(result, 'Fields') and result.Fields else []
    codes = [str(c) for c in result.Codes] if hasattr(result, 'Codes') and result.Codes else []
    times = result.Times if hasattr(result, 'Times') and result.Times else []

    if not data:
        return pd.DataFrame()

    # wset: Codes 为行号 ("1","2",...), 不是真实代码
    if _is_synthetic_codes(codes) and fields:
        return pd.DataFrame(dict(zip(fields, data)))

    # 截面接口: 按代码索引
    _cross_section = {"wss", "wsq", "wsee", "wsed"}
    if endpoint in _cross_section and codes:
        df = pd.DataFrame(dict(zip(fields, data)), index=codes)
        df.index.name = "code"
        return df

    # 判断是否为时间序列: data[0] 长度匹配 times 长度
    row_len = len(data[0]) if data else 0
    is_time_series = times and row_len == len(times)

    if is_time_series:
        n_codes = len(codes) if codes else 0
        if n_codes > 1 and len(data) == n_codes:
            # 多代码单字段
            df = pd.DataFrame(dict(zip(codes, data)), index=pd.to_datetime(times))
            df.index.name = "date"
            return df
        # 单代码: 按字段分列
        df = pd.DataFrame(dict(zip(fields, data)), index=pd.to_datetime(times))
        df.index.name = "date"
        return df

    # 截面 fallback
    if codes and row_len == len(codes):
        df = pd.DataFrame(dict(zip(fields, data)), index=codes)
        df.index.name = "code"
        return df

    # fallback
    if fields:
        return pd.DataFrame(dict(zip(fields, data)))
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# 公开 API — 对齐 WindPy 原生接口
# ---------------------------------------------------------------------------

def wsd(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """日级时间序列，等价于 w.wsd()。"""
    w = _ensure_connected()
    result = w.wsd(codes, fields, begin, end, options)
    return _to_dataframe(result, "wsd")


def wss(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """截面快照，等价于 w.wss()。"""
    w = _ensure_connected()
    result = w.wss(codes, fields, options)
    return _to_dataframe(result, "wss")


def wset(table_name: str, options: str = "") -> pd.DataFrame:
    """报表数据集，等价于 w.wset()。"""
    w = _ensure_connected()
    result = w.wset(table_name, options)
    return _to_dataframe(result, "wset")


def wsq(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """实时行情快照，等价于 w.wsq()。"""
    w = _ensure_connected()
    result = w.wsq(codes, fields, options)
    return _to_dataframe(result, "wsq")


def edb(codes: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """宏观经济指标，等价于 w.edb()。"""
    w = _ensure_connected()
    result = w.edb(codes, begin, end, options)
    return _to_dataframe(result, "edb")


def wsi(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """分钟K线序列，等价于 w.wsi()。options 常用: BarSize=1/5/15/30/60"""
    w = _ensure_connected()
    result = w.wsi(codes, fields, begin, end, options)
    return _to_dataframe(result, "wsi")


def wst(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """日内Tick跳价，等价于 w.wst()。"""
    w = _ensure_connected()
    result = w.wst(codes, fields, begin, end, options)
    return _to_dataframe(result, "wst")


def wsee(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """板块多维数据，等价于 w.wsee()。codes 为板块/指数代码。"""
    w = _ensure_connected()
    result = w.wsee(codes, fields, options)
    return _to_dataframe(result, "wsee")


def wses(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """板块时间序列，等价于 w.wses()。"""
    w = _ensure_connected()
    result = w.wses(codes, fields, begin, end, options)
    return _to_dataframe(result, "wses")


def wsed(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """板块查询，等价于 w.wsed()。codes 为 SectorID。"""
    w = _ensure_connected()
    result = w.wsed(codes, fields, options)
    return _to_dataframe(result, "wsed")


def tdays(begin: str = "", end: str = "", options: str = "") -> list:
    """交易日列表，等价于 w.tdays()。返回日期字符串列表。"""
    w = _ensure_connected()
    result = w.tdays(begin, end, options)
    if hasattr(result, 'ErrorCode') and result.ErrorCode != 0:
        raise RuntimeError(f"Wind error {result.ErrorCode}: {result.Data}")
    data = result.Data if hasattr(result, 'Data') and result.Data else []
    return _serialize_times(data[0]) if data else []


def tdaysoffset(offset: int, begin: str = "", options: str = "") -> str:
    """交易日偏移，等价于 w.tdaysoffset()。返回偏移后的日期字符串。"""
    if not begin:
        from datetime import date
        begin = date.today().strftime("%Y%m%d")
    w = _ensure_connected()
    result = w.tdaysoffset(offset, begin, options)
    if hasattr(result, 'ErrorCode') and result.ErrorCode != 0:
        raise RuntimeError(f"Wind error {result.ErrorCode}: {result.Data}")
    data = result.Data if hasattr(result, 'Data') and result.Data else []
    return str(data[0][0]) if data and data[0] else ""


def tdayscount(begin: str = "", end: str = "", options: str = "") -> int:
    """交易日计数，等价于 w.tdayscount()。返回交易日数量。"""
    w = _ensure_connected()
    result = w.tdayscount(begin, end, options)
    if hasattr(result, 'ErrorCode') and result.ErrorCode != 0:
        raise RuntimeError(f"Wind error {result.ErrorCode}: {result.Data}")
    data = result.Data if hasattr(result, 'Data') and result.Data else []
    return int(data[0][0]) if data and data[0] else 0


def weqs(filtername: str, options: str = "") -> pd.DataFrame:
    """条件选股，等价于 w.weqs()。"""
    w = _ensure_connected()
    result = w.weqs(filtername, options)
    return _to_dataframe(result, "weqs")


def htocode(codes: str, sec_type: str, options: str = "") -> pd.DataFrame:
    """代码转换（名称/简称→Wind代码），等价于 w.htocode()。"""
    w = _ensure_connected()
    result = w.htocode(codes, sec_type, options)
    return _to_dataframe(result, "htocode")


def wai(func: str, input: str, options: str = "") -> pd.DataFrame:
    """智能API，等价于 w.wai()。"""
    w = _ensure_connected()
    result = w.wai(func, input, options)
    return _to_dataframe(result, "wai")


def wgel(funname: str, windid: str, options: str = "") -> pd.DataFrame:
    """企业库，等价于 w.wgel()。"""
    w = _ensure_connected()
    result = w.wgel(funname, windid, options)
    return _to_dataframe(result, "wgel")


def health() -> dict:
    """检查 Wind 连接状态。"""
    try:
        w = _ensure_connected()
        return {"status": "ok", "connected": w.isconnected()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
