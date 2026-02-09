#!/usr/bin/env python3
"""
Wind A-Share Stock Query Tool
A股代码查询工具

使用方法:
    from windpy_stock_query import StockQuery
    
    query = StockQuery()
    
    # 根据名称查代码
    results = query.find_by_name("茅台")
    
    # 根据代码查名称
    name = query.get_name("600519.SH")
    
    # 获取股票信息
    info = query.get_info("600519.SH")
    
    # 获取最新价格
    price = query.get_price("600519.SH")
"""

from WindPy import w
import pandas as pd
from typing import List, Dict, Optional

class StockQuery:
    """A股代码查询器"""
    
    def __init__(self):
        self.w = w
        self.w.start()
        self._cache = {}
        
    def __del__(self):
        if hasattr(self, 'w'):
            self.w.stop()
    
    def find_by_name(self, keyword: str) -> List[Dict[str, str]]:
        """
        根据名称关键字查找股票代码
        
        Args:
            keyword: 股票名称关键字，如"茅台"
            
        Returns:
            匹配的股票列表，每个元素包含 code 和 name
            
        Example:
            >>> query.find_by_name("茅台")
            [{'code': '600519.SH', 'name': '贵州茅台'}]
        """
        result = self.w.wset("sectorconstituent", "date=20260209;sectorid=a001010100000000")
        
        matches = []
        if result.ErrorCode == 0:
            codes = result.Data[1]
            names = result.Data[2]
            
            for i in range(len(names)):
                if keyword in names[i]:
                    matches.append({
                        'code': codes[i],
                        'name': names[i]
                    })
        
        return matches
    
    def get_name(self, code: str) -> Optional[str]:
        """
        根据代码获取股票名称
        
        Args:
            code: 股票代码，如"600519.SH"
            
        Returns:
            股票名称，如"贵州茅台"
            
        Example:
            >>> query.get_name("600519.SH")
            '贵州茅台'
        """
        # 检查缓存
        if code in self._cache:
            return self._cache[code]
        
        result = self.w.wss(code, "sec_name", "tradeDate=20260209", usedf=True)
        
        if result[0] == 0:
            name = result[1].iloc[0]['SEC_NAME']
            self._cache[code] = name
            return name
        
        return None
    
    def get_info(self, code: str) -> Optional[Dict]:
        """
        获取股票详细信息
        
        Args:
            code: 股票代码
            
        Returns:
            包含股票信息的字典
            
        Example:
            >>> query.get_info("600519.SH")
            {
                'name': '贵州茅台',
                'close': 1515.01,
                'pct_chg': 0.5,
                'pe_ttm': 25.3,
                'pb_lf': 8.2,
                'mkt_cap': 19000亿
            }
        """
        fields = "sec_name,close,pct_chg,pe_ttm,pb_lf,mkt_cap_ard"
        err, df = self.w.wss(code, fields, "tradeDate=20260209", usedf=True)
        
        if err == 0:
            row = df.iloc[0]
            return {
                'name': row['SEC_NAME'],
                'close': row['CLOSE'],
                'pct_chg': row['PCT_CHG'],
                'pe_ttm': row['PE_TTM'],
                'pb_lf': row['PB_LF'],
                'mkt_cap': row['MKT_CAP_ARD']
            }
        
        return None
    
    def get_price(self, code: str) -> Optional[float]:
        """
        获取股票最新价格
        
        Args:
            code: 股票代码
            
        Returns:
            最新收盘价
            
        Example:
            >>> query.get_price("600519.SH")
            1515.01
        """
        err, df = self.w.wsd(code, "close", "", "", "", usedf=True)
        
        if err == 0:
            return df.iloc[-1]['CLOSE']
        
        return None
    
    def get_industry_stocks(self, industry_code: str) -> List[Dict[str, str]]:
        """
        获取某个行业的所有股票
        
        Args:
            industry_code: 行业代码，如"850111.SI"(种子)
            
        Returns:
            该行业的股票列表
            
        Example:
            >>> query.get_industry_stocks("850111.SI")
            [{'code': '...', 'name': '...'}, ...]
        """
        # 通过 wset 获取行业成分
        result = self.w.wset("sectorconstituent", f"date=20260209;sectorid=a39901011i000000")
        
        stocks = []
        if result.ErrorCode == 0:
            for i in range(len(result.Data[1])):
                stocks.append({
                    'code': result.Data[1][i],
                    'name': result.Data[2][i]
                })
        
        return stocks
    
    def search_industry(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索行业
        
        Args:
            keyword: 行业名称关键字
            
        Returns:
            匹配的行业列表
            
        Example:
            >>> query.search_industry("白酒")
            [{'code': '850111.SI', 'name': '白酒Ⅲ(申万)'}]
        """
        result = self.w.wset("sectorconstituent", "date=20260209;sectorid=a39901011i000000")
        
        matches = []
        if result.ErrorCode == 0:
            for i in range(len(result.Data[2])):
                if keyword in result.Data[2][i]:
                    matches.append({
                        'code': result.Data[1][i],
                        'name': result.Data[2][i]
                    })
        
        return matches


def main():
    """命令行使用示例"""
    import sys
    
    query = StockQuery()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python windpy_stock_query.py <股票名称或代码>")
        print("")
        print("示例:")
        print("  python windpy_stock_query.py 茅台")
        print("  python windpy_stock_query.py 600519.SH")
        return
    
    keyword = sys.argv[1]
    
    # 判断是代码还是名称
    if '.' in keyword:
        # 是代码，查询名称和信息
        print(f"查询代码: {keyword}")
        name = query.get_name(keyword)
        if name:
            print(f"名称: {name}")
            info = query.get_info(keyword)
            if info:
                print(f"最新价: {info['close']}")
                print(f"涨跌幅: {info['pct_chg']}%")
                print(f"市盈率: {info['pe_ttm']}")
                print(f"市净率: {info['pb_lf']}")
        else:
            print("未找到该代码")
    else:
        # 是名称，查询代码
        print(f"搜索: {keyword}")
        results = query.find_by_name(keyword)
        if results:
            print(f"找到 {len(results)} 个结果:")
            for r in results[:10]:  # 最多显示10个
                print(f"  {r['code']} - {r['name']}")
        else:
            print("未找到匹配的股票")


if __name__ == "__main__":
    main()
