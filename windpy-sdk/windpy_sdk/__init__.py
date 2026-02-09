"""
WindPy SDK 数据获取工具包
提供标准化的 Wind 金融数据获取接口
"""

from .client import WindClient
from .functions import (
    get_sector_constituents,
    get_historical_returns,
    get_realtime_quote,
    get_index_list,
    get_etf_list,
    get_bond_index_list,
)
from .constants import (
    SECTOR_ALL_A_SHARES,
    SECTOR_SW3_INDUSTRIES,
    SECTOR_HS300,
    SECTOR_CSI500,
    INDEX_HS300,
    INDEX_CSI500,
    INDEX_SSE50,
    COMMODITY_GOLD,
    COMMODITY_SILVER,
    COMMODITY_COPPER,
)

__version__ = '1.0.0'

__all__ = [
    'WindClient',
    'get_sector_constituents',
    'get_historical_returns',
    'get_realtime_quote',
    'get_index_list',
    'get_etf_list',
    'get_bond_index_list',
    'SECTOR_ALL_A_SHARES',
    'SECTOR_SW3_INDUSTRIES',
    'SECTOR_HS300',
    'SECTOR_CSI500',
    'INDEX_HS300',
    'INDEX_CSI500',
    'INDEX_SSE50',
    'COMMODITY_GOLD',
    'COMMODITY_SILVER',
    'COMMODITY_COPPER',
]
