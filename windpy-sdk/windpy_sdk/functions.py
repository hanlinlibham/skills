"""
WindPy SDK 便捷函数
无需管理连接，函数内部自动处理
"""

from typing import List, Union
import pandas as pd
from .client import WindClient
from .constants import (
    SECTOR_SW3_INDUSTRIES,
    INDEX_HS300,
    INDEX_CSI500,
    COMMODITY_GOLD,
    COMMODITY_SILVER,
)


def get_sector_constituents(sectorid: str, date: str = None) -> pd.DataFrame:
    """
    获取板块成分股（便捷函数）
    
    Parameters:
    -----------
    sectorid : str
        板块代码
    date : str, optional
        日期
        
    Returns:
    --------
    DataFrame with columns: [date, wind_code, sec_name]
    
    Example:
    --------
    >>> sw3 = get_sector_constituents('a39901011i000000')  # 申万三级行业
    >>> a_shares = get_sector_constituents('a001010100000000')  # 全部A股
    """
    with WindClient() as client:
        return client.get_sector_constituents(sectorid, date)


def get_historical_returns(codes: Union[str, List[str]], 
                           lookback: str = '-252TD') -> pd.DataFrame:
    """
    获取历史收益率（便捷函数）
    
    Parameters:
    -----------
    codes : str or list
        证券代码
    lookback : str
        回溯期，如 '-30D', '-252TD', '-1Y'
        
    Returns:
    --------
    DataFrame with daily returns
    
    Example:
    --------
    >>> returns = get_historical_returns('000300.SH', '-252TD')
    >>> mean = returns.mean()
    >>> std = returns.std()
    """
    with WindClient() as client:
        return client.get_historical_returns(codes, lookback)


def get_realtime_quote(codes: Union[str, List[str]], 
                       fields: str = None) -> pd.DataFrame:
    """
    获取实时行情（便捷函数）
    
    Parameters:
    -----------
    codes : str or list
        证券代码
    fields : str, optional
        字段列表
        
    Returns:
    --------
    DataFrame with real-time quotes
    """
    with WindClient() as client:
        return client.get_realtime_quote(codes, fields)


def get_index_list() -> List[dict]:
    """
    获取主要指数列表
    
    Returns:
    --------
    List of dict with 'code', 'name', 'type'
    """
    indices = [
        {'code': INDEX_HS300, 'name': '沪深300', 'type': '股票指数'},
        {'code': INDEX_CSI500, 'name': '中证500', 'type': '股票指数'},
        {'code': '000016.SH', 'name': '上证50', 'type': '股票指数'},
        {'code': '000852.SH', 'name': '中证1000', 'type': '股票指数'},
        {'code': '000001.SH', 'name': '上证指数', 'type': '股票指数'},
        {'code': '399001.SZ', 'name': '深证成指', 'type': '股票指数'},
        {'code': '399006.SZ', 'name': '创业板指', 'type': '股票指数'},
        {'code': '000688.SH', 'name': '科创50', 'type': '股票指数'},
    ]
    return indices


def get_etf_list() -> pd.DataFrame:
    """
    获取主流 ETF 列表
    
    Returns:
    --------
    DataFrame with ETF information
    """
    etfs = [
        {'code': '510300.SH', 'name': '沪深300ETF', 'tracking': '沪深300'},
        {'code': '510500.SH', 'name': '中证500ETF', 'tracking': '中证500'},
        {'code': '510050.SH', 'name': '上证50ETF', 'tracking': '上证50'},
        {'code': '159915.SZ', 'name': '创业板ETF', 'tracking': '创业板指'},
        {'code': '588000.SH', 'name': '科创50ETF', 'tracking': '科创50'},
        {'code': '512480.SH', 'name': '半导体ETF', 'tracking': '半导体指数'},
        {'code': '515030.SH', 'name': '新能源车ETF', 'tracking': '新能源车指数'},
        {'code': '512760.SH', 'name': '芯片ETF', 'tracking': '芯片指数'},
    ]
    return pd.DataFrame(etfs)


def get_bond_index_list() -> pd.DataFrame:
    """
    获取中债指数列表
    
    Returns:
    --------
    DataFrame with bond index information
    """
    bonds = [
        {'code': 'CBA00101.CS', 'name': '中债总指数'},
        {'code': 'CBA00301.CS', 'name': '中债国债指数'},
        {'code': 'CBA00401.CS', 'name': '中债金融债指数'},
        {'code': 'CBA00501.CS', 'name': '中债企业债指数'},
        {'code': 'CBA00601.CS', 'name': '中债央票指数'},
    ]
    return pd.DataFrame(bonds)


def get_commodity_list() -> pd.DataFrame:
    """
    获取主要商品期货列表
    
    Returns:
    --------
    DataFrame with commodity information
    """
    commodities = [
        {'code': COMMODITY_GOLD, 'name': '黄金', 'exchange': 'SHFE'},
        {'code': COMMODITY_SILVER, 'name': '白银', 'exchange': 'SHFE'},
        {'code': 'CU00.SHF', 'name': '铜', 'exchange': 'SHFE'},
        {'code': 'AL00.SHF', 'name': '铝', 'exchange': 'SHFE'},
        {'code': 'ZN00.SHF', 'name': '锌', 'exchange': 'SHFE'},
        {'code': 'RB00.SHF', 'name': '螺纹钢', 'exchange': 'SHFE'},
        {'code': 'SC00.INE', 'name': '原油', 'exchange': 'INE'},
        {'code': 'TA00.CZC', 'name': 'PTA', 'exchange': 'CZCE'},
    ]
    return pd.DataFrame(commodities)


def get_global_index_list() -> pd.DataFrame:
    """
    获取全球主要指数列表
    
    Returns:
    --------
    DataFrame with global index information
    """
    indices = [
        {'code': 'SPX.GI', 'name': '标普500', 'region': '美股'},
        {'code': 'IXIC.GI', 'name': '纳斯达克', 'region': '美股'},
        {'code': 'DJI.GI', 'name': '道琼斯', 'region': '美股'},
        {'code': 'VIX.GI', 'name': 'VIX波动率', 'region': '美股'},
        {'code': 'HSI.HI', 'name': '恒生指数', 'region': '港股'},
        {'code': 'N225.GI', 'name': '日经225', 'region': '日股'},
        {'code': 'KS11.GI', 'name': '韩国KOSPI', 'region': '韩股'},
        {'code': 'GDAXI.GI', 'name': '德国DAX', 'region': '欧股'},
        {'code': 'FTSE.GI', 'name': '英国富时100', 'region': '欧股'},
    ]
    return pd.DataFrame(indices)


def get_sw3_industries() -> pd.DataFrame:
    """
    获取申万三级行业列表（259个）
    
    Returns:
    --------
    DataFrame with SW3 industry information
    """
    return get_sector_constituents(SECTOR_SW3_INDUSTRIES)
