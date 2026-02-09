"""
Asset Monitor
资产异常波动监控核心逻辑
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any


class AssetMonitor:
    """
    资产异常波动监控器
    
    依赖 windpy_sdk 获取数据，专注于监控逻辑
    """
    
    # 监控资产配置
    ASSET_CONFIG = {
        "sw3_industry": {
            "name": "申万三级行业",
            "type": "sector",
            "sectorid": "a39901011i000000",
        },
        "ashare_index": {
            "name": "A股主要指数",
            "type": "direct",
            "codes": [
                "000300.SH", "000905.SH", "000016.SH", "000852.SH",
                "000001.SH", "399001.SZ", "399006.SZ", "000688.SH", "883985.WI"
            ],
        },
        "bond_index": {
            "name": "中债指数",
            "type": "direct",
            "codes": [
                "CBA00101.CS", "CBA00301.CS", "CBA00401.CS",
                "CBA00501.CS", "CBA00601.CS"
            ],
        },
        "etf": {
            "name": "主流ETF",
            "type": "direct",
            "codes": [
                "510300.SH", "510500.SH", "510050.SH", "159915.SZ",
                "588000.SH", "512480.SH", "515030.SH", "512760.SH"
            ],
        },
        "commodity": {
            "name": "商品期货",
            "type": "direct",
            "codes": [
                "AU00.SHF", "AG00.SHF", "CU00.SHF", "AL00.SHF",
                "ZN00.SHF", "RB00.SHF", "SC00.INE", "TA00.CZC"
            ],
        },
        "global_index": {
            "name": "全球指数",
            "type": "direct",
            "codes": [
                "SPX.GI", "IXIC.GI", "DJI.GI", "VIX.GI",
                "HSI.HI", "N225.GI", "KS11.GI", "GDAXI.GI", "FTSE.GI"
            ],
        },
    }
    
    def __init__(self, threshold_z: float = 2.0, min_days: int = 30):
        """
        初始化监控器
        
        Parameters:
        -----------
        threshold_z : float
            Z-Score阈值，默认2.0（2倍标准差）
        min_days : int
            最小交易日数量，默认30天
        """
        self.threshold_z = threshold_z
        self.min_days = min_days
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y%m%d')
        self.one_year_ago = (self.today - timedelta(days=365)).strftime('%Y%m%d')
        self.all_anomalies: List[Dict[str, Any]] = []
        
    def run(self, client) -> List[Dict[str, Any]]:
        """
        运行完整监控
        
        Parameters:
        -----------
        client : WindClient
            windpy_sdk 的 WindClient 实例
            
        Returns:
        --------
        List[dict] : 异常资产列表
        """
        print(f"{'='*70}")
        print(f"📊 资产异常波动监控")
        print(f"时间: {self.today.strftime('%Y-%m-%d %H:%M')}")
        print(f"区间: {self.one_year_ago} 至 {self.today_str}")
        print(f"Z值阈值: {self.threshold_z}")
        print(f"{'='*70}\n")
        
        total_anomalies = 0
        
        for key, config in self.ASSET_CONFIG.items():
            try:
                if config['type'] == 'sector':
                    count = self._monitor_sector(client, key, config)
                else:
                    count = self._monitor_direct(client, key, config)
                total_anomalies += count
            except Exception as e:
                print(f"  ❌ {config['name']} 监控失败: {e}")
        
        print(f"\n{'='*70}")
        print(f"✅ 监控完成，共发现 {total_anomalies} 个异常")
        print(f"{'='*70}\n")
        
        return self.all_anomalies
    
    def analyze_single(self, client, code: str, name: str, category: str) -> Optional[Dict[str, Any]]:
        """
        分析单个资产的波动
        
        Parameters:
        -----------
        client : WindClient
        code : str
            资产代码
        name : str
            资产名称
        category : str
            资产类别
            
        Returns:
        --------
        dict or None : 异常信息或None（如果正常）
        """
        try:
            # 使用 windpy_sdk 获取历史数据
            hist = client.get_historical_returns(code, '-252TD')
            
            if len(hist) < self.min_days:
                return None
                
            returns = hist.dropna()
            if len(returns) < self.min_days:
                return None
            
            mean_ret = returns.mean()
            std_ret = returns.std()
            today_ret = returns.iloc[-1] if len(returns) > 0 else None
            
            if today_ret is not None and std_ret > 0:
                z_score = (today_ret - mean_ret) / std_ret
                
                if abs(z_score) > self.threshold_z:
                    return {
                        'category': category,
                        'code': code,
                        'name': name,
                        'today_return': float(today_ret),
                        'z_score': float(z_score),
                        'std_annual': float(std_ret),
                        'direction': '大涨' if z_score > 0 else '大跌'
                    }
        except Exception as e:
            # 静默处理错误，避免中断监控
            pass
        
        return None
    
    def _monitor_sector(self, client, key: str, config: Dict) -> int:
        """监控板块类资产"""
        print(f"\n[监控] {config['name']}")
        
        # 使用 windpy_sdk 获取板块成分
        df = client.get_sector_constituents(config['sectorid'])
        
        if df.empty:
            print(f"  ⚠️ 未获取到数据")
            return 0
        
        codes = df['wind_code'].tolist()
        names = df['sec_name'].tolist()
        
        print(f"  共 {len(codes)} 个资产")
        
        count = 0
        for i, (code, name) in enumerate(zip(codes, names)):
            if i % 50 == 0 and len(codes) > 50:
                print(f"    进度: {i}/{len(codes)}...")
            
            result = self.analyze_single(client, code, name, config['name'])
            if result:
                self.all_anomalies.append(result)
                print(f"    ⚠️ {name}: {result['today_return']:+.2f}% (Z={result['z_score']:+.2f})")
                count += 1
        
        print(f"  发现 {count} 个异常")
        return count
    
    def _monitor_direct(self, client, key: str, config: Dict) -> int:
        """监控直接代码类资产"""
        print(f"\n[监控] {config['name']} ({len(config['codes'])}个)")
        
        # 获取名称
        try:
            snapshot = client.get_snapshot(config['codes'], 'sec_name')
            name_map = dict(zip(snapshot.index, snapshot['SEC_NAME']))
        except:
            name_map = {code: code for code in config['codes']}
        
        count = 0
        for code in config['codes']:
            name = name_map.get(code, code)
            result = self.analyze_single(client, code, name, config['name'])
            if result:
                self.all_anomalies.append(result)
                print(f"  ⚠️ {name}: {result['today_return']:+.2f}% (Z={result['z_score']:+.2f})")
                count += 1
        
        print(f"  发现 {count} 个异常")
        return count
