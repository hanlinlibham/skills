"""
Wind 客户端 — 与 wind_server.py 常驻服务通信，返回 pandas DataFrame。

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
    df = wsi("600519.SH", "close,volume", "-0D 09:30:00", "-0D 15:00:00", "BarSize=5")
    dates = tdays("20260101", "20260226")
"""

import json
import os
import urllib.request
import pandas as pd

_BASE_URL = os.environ.get(
    "WIND_SERVER_URL",
    "http://{host}:{port}".format(
        host=os.environ.get("WIND_SERVER_HOST", "127.0.0.1"),
        port=os.environ.get("WIND_SERVER_PORT", "18888"),
    ),
)


def _post(endpoint: str, payload: dict) -> dict:
    """发送 POST 请求到 Wind 服务。"""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{_BASE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Wind 服务未启动或不可达 ({_BASE_URL})。"
            f"请先运行: python wind_server.py &\n原始错误: {e}"
        )


def _is_synthetic_codes(codes: list) -> bool:
    """判断 Codes 是否为 wset 返回的行号 ("1","2","3",...)。"""
    if not codes:
        return False
    return all(isinstance(c, str) and c.isdigit() for c in codes)


def _to_dataframe(result: dict, endpoint: str = "") -> pd.DataFrame:
    """将服务端返回的 dict 转为 DataFrame。"""
    if result.get("error"):
        raise RuntimeError(f"Wind error {result.get('code', '?')}: {result.get('message', '')}")

    data = result.get("Data", [])
    fields = result.get("Fields", [])
    codes = result.get("Codes", [])
    times = result.get("Times", [])

    if not data:
        return pd.DataFrame()

    # wset: Codes 为行号 ("1","2",...), 不是真实代码
    if _is_synthetic_codes(codes) and fields:
        return pd.DataFrame(dict(zip(fields, data)))

    # 截面接口: 即使 times 有值也应按代码索引
    _cross_section = {"/wss", "/wsq", "/wsee", "/wsed"}
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
            # 多代码单字段: 每个 data[i] 对应一个代码
            df = pd.DataFrame(dict(zip(codes, data)), index=pd.to_datetime(times))
            df.index.name = "date"
            return df
        # 单代码 (或无代码信息): 按字段分列
        df = pd.DataFrame(dict(zip(fields, data)), index=pd.to_datetime(times))
        df.index.name = "date"
        return df

    # wss/wsq 截面: data[0] 长度匹配 codes 长度
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
    result = _post("/wsd", {
        "codes": codes, "fields": fields,
        "beginTime": begin, "endTime": end, "options": options,
    })
    return _to_dataframe(result, "/wsd")


def wss(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """截面快照，等价于 w.wss()。"""
    result = _post("/wss", {"codes": codes, "fields": fields, "options": options})
    return _to_dataframe(result, "/wss")


def wset(table_name: str, options: str = "") -> pd.DataFrame:
    """报表数据集，等价于 w.wset()。"""
    result = _post("/wset", {"tableName": table_name, "options": options})
    return _to_dataframe(result, "/wset")


def wsq(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """实时行情快照，等价于 w.wsq()。"""
    result = _post("/wsq", {"codes": codes, "fields": fields, "options": options})
    return _to_dataframe(result, "/wsq")


def edb(codes: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """宏观经济指标，等价于 w.edb()。"""
    result = _post("/edb", {
        "codes": codes, "beginTime": begin, "endTime": end, "options": options,
    })
    return _to_dataframe(result, "/edb")


def wsi(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """分钟K线序列，等价于 w.wsi()。options 常用: BarSize=1/5/15/30/60"""
    result = _post("/wsi", {
        "codes": codes, "fields": fields,
        "beginTime": begin, "endTime": end, "options": options,
    })
    return _to_dataframe(result, "/wsi")


def wst(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """日内Tick跳价，等价于 w.wst()。"""
    result = _post("/wst", {
        "codes": codes, "fields": fields,
        "beginTime": begin, "endTime": end, "options": options,
    })
    return _to_dataframe(result, "/wst")


def wsee(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """板块多维数据，等价于 w.wsee()。codes 为板块/指数代码。"""
    result = _post("/wsee", {"codes": codes, "fields": fields, "options": options})
    return _to_dataframe(result, "/wsee")


def wses(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """板块时间序列，等价于 w.wses()。"""
    result = _post("/wses", {
        "codes": codes, "fields": fields,
        "beginTime": begin, "endTime": end, "options": options,
    })
    return _to_dataframe(result, "/wses")


def wsed(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """板块查询，等价于 w.wsed()。codes 为 SectorID。"""
    result = _post("/wsed", {"codes": codes, "fields": fields, "options": options})
    return _to_dataframe(result, "/wsed")


def tdays(begin: str = "", end: str = "", options: str = "") -> list:
    """交易日列表，等价于 w.tdays()。返回日期字符串列表。"""
    result = _post("/tdays", {"beginTime": begin, "endTime": end, "options": options})
    if result.get("error"):
        raise RuntimeError(f"Wind error {result.get('code')}: {result.get('message')}")
    data = result.get("Data", [])
    return data[0] if data else []


def tdaysoffset(offset: int, begin: str = "", options: str = "") -> str:
    """交易日偏移，等价于 w.tdaysoffset()。返回偏移后的日期字符串。"""
    if not begin:
        from datetime import date
        begin = date.today().strftime("%Y%m%d")
    result = _post("/tdaysoffset", {"offset": offset, "beginTime": begin, "options": options})
    if result.get("error"):
        raise RuntimeError(f"Wind error {result.get('code')}: {result.get('message')}")
    data = result.get("Data", [])
    return data[0][0] if data and data[0] else ""


def tdayscount(begin: str = "", end: str = "", options: str = "") -> int:
    """交易日计数，等价于 w.tdayscount()。返回交易日数量。"""
    result = _post("/tdayscount", {"beginTime": begin, "endTime": end, "options": options})
    if result.get("error"):
        raise RuntimeError(f"Wind error {result.get('code')}: {result.get('message')}")
    data = result.get("Data", [])
    return int(data[0][0]) if data and data[0] else 0


def weqs(filtername: str, options: str = "") -> pd.DataFrame:
    """条件选股，等价于 w.weqs()。"""
    result = _post("/weqs", {"filtername": filtername, "options": options})
    return _to_dataframe(result, "/weqs")


def htocode(codes: str, sec_type: str, options: str = "") -> pd.DataFrame:
    """代码转换（名称/简称→Wind代码），等价于 w.htocode()。"""
    result = _post("/htocode", {"codes": codes, "sec_type": sec_type, "options": options})
    return _to_dataframe(result, "/htocode")


def wai(func: str, input: str, options: str = "") -> pd.DataFrame:
    """智能API，等价于 w.wai()。"""
    result = _post("/wai", {"func": func, "input": input, "options": options})
    return _to_dataframe(result, "/wai")


def wgel(funname: str, windid: str, options: str = "") -> pd.DataFrame:
    """企业库，等价于 w.wgel()。"""
    result = _post("/wgel", {"funname": funname, "windid": windid, "options": options})
    return _to_dataframe(result, "/wgel")


def health() -> dict:
    """检查 Wind 服务是否在线。"""
    req = urllib.request.Request(f"{_BASE_URL}/health")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"status": "unreachable", "message": str(e)}
