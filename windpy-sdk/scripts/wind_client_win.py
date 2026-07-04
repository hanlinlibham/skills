"""
Wind Windows 客户端 - 通过命名管道连接到常驻服务

用法:
    from wind_client_win import wsd, wss, wset, wsq, edb, wsi, tdays, tdaysoffset

    df = wsd("000300.SH", "close,pct_chg", "-30D")
    df = wss("600519.SH,000858.SZ", "sec_name,close,pe_ttm")
    df = wset("sectorconstituent", "date=20241231;windcode=000300.SH")

前提:
    先运行: python wind_server_win.py
"""

import pickle
import struct

import pandas as pd
import win32file
import pywintypes

PIPE_NAME = r'\\.\pipe\WindPyServer'


def _send_request(func_name, args, kwargs):
    """发送请求到服务端"""
    try:
        # 连接到命名管道
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )

        # 准备请求
        request = {'func': func_name, 'args': args, 'kwargs': kwargs}
        data = pickle.dumps(request)

        # 发送数据长度 + 数据
        size = struct.pack('I', len(data))
        win32file.WriteFile(handle, size)
        win32file.WriteFile(handle, data)

        # 读取响应长度
        size_data = win32file.ReadFile(handle, 4)
        response_size = struct.unpack('I', size_data[1])[0]

        # 读取响应数据
        response_data = b''
        while len(response_data) < response_size:
            chunk = win32file.ReadFile(handle, min(4096, response_size - len(response_data)))
            response_data += chunk[1]

        win32file.CloseHandle(handle)
        return pickle.loads(response_data)

    except Exception as e:
        raise ConnectionError(
            f"无法连接到 Wind 服务。请确保已运行: python wind_server_win.py\n"
            f"原始错误: {e}"
        )


def _to_dataframe(result, func_name):
    """将结果转换为 DataFrame"""
    if not result.get('success'):
        raise RuntimeError(f"Wind 错误: {result.get('error')}")

    error_code = result.get('error_code')
    if error_code != 0:
        raise RuntimeError(f"Wind API 错误码: {error_code}")

    data = result.get('data', [])

    # 根据函数类型构建 DataFrame
    if func_name == 'wsd' and len(data) >= 2:
        # wsd: 时间序列
        times = data[0] if data else []
        values = data[1:] if len(data) > 1 else []
        if times and values:
            df = pd.DataFrame(dict(zip(['CLOSE'], values)), index=pd.to_datetime(times))
            df.index.name = 'date'
            return df

    elif func_name in ['wss', 'wsq'] and len(data) >= 2:
        # wss/wsq: 截面数据
        codes = data[0] if data else []
        values = data[1:] if len(data) > 1 else []
        if codes and values:
            df = pd.DataFrame(dict(zip(['FIELD'], values)), index=codes)
            df.index.name = 'code'
            return df

    elif func_name == 'wset' and data:
        # wset: 数据集
        return pd.DataFrame(data)

    elif func_name in ['tdays', 'tdaysoffset'] and data:
        # 交易日相关
        return data[0] if data else []

    return pd.DataFrame(data)


# API 函数

def wsd(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """日级时间序列"""
    result = _send_request('wsd', [codes, fields, begin, end, options], {})
    return _to_dataframe(result, 'wsd')


def wss(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """截面快照"""
    result = _send_request('wss', [codes, fields, options], {})
    return _to_dataframe(result, 'wss')


def wset(table_name: str, options: str = "") -> pd.DataFrame:
    """报表数据集"""
    result = _send_request('wset', [table_name, options], {})
    return _to_dataframe(result, 'wset')


def wsq(codes: str, fields: str, options: str = "") -> pd.DataFrame:
    """实时行情快照"""
    result = _send_request('wsq', [codes, fields, options], {})
    return _to_dataframe(result, 'wsq')


def edb(codes: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """宏观经济指标"""
    result = _send_request('edb', [codes, begin, end, options], {})
    return _to_dataframe(result, 'edb')


def wsi(codes: str, fields: str, begin: str = "", end: str = "", options: str = "") -> pd.DataFrame:
    """分钟K线序列"""
    result = _send_request('wsi', [codes, fields, begin, end, options], {})
    return _to_dataframe(result, 'wsi')


def tdays(begin: str = "", end: str = "", options: str = "") -> list:
    """交易日列表"""
    result = _send_request('tdays', [begin, end, options], {})
    return _to_dataframe(result, 'tdays')


def tdaysoffset(offset: int, begin: str = "", options: str = "") -> str:
    """交易日偏移"""
    result = _send_request('tdaysoffset', [offset, begin, options], {})
    return _to_dataframe(result, 'tdaysoffset')


if __name__ == "__main__":
    # 测试
    print("测试 Windows 客户端...")
    try:
        df = wsd("000300.SH", "close", "-5D")
        print(df)
    except Exception as e:
        print(f"错误: {e}")
