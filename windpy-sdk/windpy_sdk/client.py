"""
WindPy SDK Client
Wind 数据获取客户端
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Union, Optional
from .constants import DEFAULT_CONFIG, SECTOR_SW3_INDUSTRIES


class WindDataError(Exception):
    """Wind 数据获取错误"""
    pass


class WindClient:
    """
    WindPy 连接管理客户端
    
    使用上下文管理器自动管理连接:
    ```
    with WindClient() as client:
        data = client.get_daily_data('000300.SH', 'close', '-30D')
    ```
    """
    
    def __init__(self, timeout: int = None):
        """
        初始化客户端
        
        Parameters:
        -----------
        timeout : int
            连接超时时间（秒），默认120
        """
        self.timeout = timeout or DEFAULT_CONFIG['start_timeout']
        self._w = None
        self._connected = False
        
    def __enter__(self):
        """进入上下文，自动连接"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，自动断开"""
        self.disconnect()
        
    def connect(self):
        """建立 WindPy 连接"""
        if self._connected:
            return
            
        try:
            from WindPy import w
            self._w = w
            result = w.start(waitTime=self.timeout)
            if result.ErrorCode != 0:
                raise ConnectionError(f"Wind连接失败: {result.Data}")
            self._connected = True
        except ImportError:
            raise ImportError("WindPy 未安装，请安装 Wind 金融终端 Python API")
        except Exception as e:
            raise ConnectionError(f"Wind连接失败: {e}")
    
    def disconnect(self):
        """断开 WindPy 连接"""
        if self._connected and self._w:
            self._w.stop()
            self._connected = False
            
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected
    
    # ==================== 板块数据 ====================
    
    def get_sector_constituents(self, sectorid: str, date: str = None) -> pd.DataFrame:
        """
        获取板块成分股
        
        Parameters:
        -----------
        sectorid : str
            板块代码，如 'a39901011i000000' (申万三级行业)
        date : str, optional
            日期，默认当前日期
            
        Returns:
        --------
        DataFrame with columns: [date, wind_code, sec_name]
        """
        if not self._connected:
            raise ConnectionError("Wind未连接")
            
        date = date or datetime.now().strftime('%Y%m%d')
        
        result = self._w.wset("sectorconstituent", f"date={date};sectorid={sectorid}")
        
        if result.ErrorCode != 0:
            raise WindDataError(f"获取板块成分失败: {result.Data}")
            
        if len(result.Data) < 3:
            return pd.DataFrame()
            
        df = pd.DataFrame({
            'date': result.Data[0],
            'wind_code': result.Data[1],
            'sec_name': result.Data[2]
        })
        return df
    
    def get_sector_list(self, sector_type: str = 'sw3') -> pd.DataFrame:
        """
        获取板块列表
        
        Parameters:
        -----------
        sector_type : str
            'sw3' - 申万三级行业 (默认)
            'sw1' - 申万一级行业
            'index' - 主要指数
            
        Returns:
        --------
        DataFrame with columns: [code, name]
        """
        if not self._connected:
            raise ConnectionError("Wind未连接")
            
        sector_map = {
            'sw3': SECTOR_SW3_INDUSTRIES,
            'sw1': 'a39901011g000000',
        }
        
        sectorid = sector_map.get(sector_type, sector_type)
        return self.get_sector_constituents(sectorid)
    
    # ==================== 历史数据 ====================
    
    def get_daily_data(self, 
                       codes: Union[str, List[str]], 
                       fields: str, 
                       start_date: str, 
                       end_date: str = None,
                       **options) -> pd.DataFrame:
        """
        获取日级历史数据 (wsd)
        
        Parameters:
        -----------
        codes : str or list
            证券代码，如 '000300.SH' 或 ['000300.SH', '000905.SH']
        fields : str
            字段，如 'close,pct_chg,volume'
        start_date : str
            开始日期，支持 '20240101', '-30D', '-1M'
        end_date : str, optional
            结束日期，默认今天
        **options : 
            PriceAdj : str - 'F'(前复权), 'B'(后复权)
            Period : str - 'D'(日), 'W'(周), 'M'(月)
            
        Returns:
        --------
        DataFrame with date index and field columns
        """
        if not self._connected:
            raise ConnectionError("Wind未连接")
            
        codes = ','.join(codes) if isinstance(codes, list) else codes
        end_date = end_date or ""
        
        options_str = ';'.join([f"{k}={v}" for k, v in options.items()])
        
        result = self._w.wsd(codes, fields, start_date, end_date, options_str, usedf=True)
        
        if result[0] != 0:
            raise WindDataError(f"获取历史数据失败: {result}")
            
        return result[1]
    
    def get_historical_returns(self, 
                               codes: Union[str, List[str]], 
                               lookback: str = '-252TD') -> pd.DataFrame:
        """
        获取历史收益率
        
        Parameters:
        -----------
        codes : str or list
            证券代码
        lookback : str
            回溯期，如 '-30D', '-252TD'(一年交易日), '-1Y'
            
        Returns:
        --------
        DataFrame with daily returns
        """
        return self.get_daily_data(codes, 'pct_chg', lookback)
    
    # ==================== 截面数据 ====================
    
    def get_snapshot(self, 
                     codes: Union[str, List[str]], 
                     fields: str,
                     trade_date: str = None) -> pd.DataFrame:
        """
        获取截面快照 (wss)
        
        Parameters:
        -----------
        codes : str or list
            证券代码
        fields : str
            字段，如 'sec_name,close,pct_chg,pe_ttm'
        trade_date : str, optional
            交易日，默认最近交易日
            
        Returns:
        --------
        DataFrame indexed by wind_code
        """
        if not self._connected:
            raise ConnectionError("Wind未连接")
            
        codes = ','.join(codes) if isinstance(codes, list) else codes
        options = f"tradeDate={trade_date}" if trade_date else ""
        
        result = self._w.wss(codes, fields, options, usedf=True)
        
        if result[0] != 0:
            raise WindDataError(f"获取截面数据失败: {result}")
            
        return result[1]
    
    def get_realtime_quote(self, 
                           codes: Union[str, List[str]], 
                           fields: str = None) -> pd.DataFrame:
        """
        获取实时行情 (wsq)
        
        Parameters:
        -----------
        codes : str or list
            证券代码
        fields : str, optional
            实时字段，默认 'rt_last,rt_pct_chg,rt_vol'
            
        Returns:
        --------
        DataFrame with real-time quotes
        """
        if not self._connected:
            raise ConnectionError("Wind未连接")
            
        codes = ','.join(codes) if isinstance(codes, list) else codes
        fields = fields or "rt_last,rt_pct_chg,rt_vol"
        
        result = self._w.wsq(codes, fields, usedf=True)
        
        if result[0] != 0:
            raise WindDataError(f"获取实时行情失败: {result}")
            
        return result[1]
