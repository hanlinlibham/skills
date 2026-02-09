#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WindPy 代码生成器
根据用户需求自动生成 WindPy 代码

使用方法:
    python code_generator.py "获取贵州茅台近30天收盘价"
    python code_generator.py --template daily_price --codes 600519.SH --fields close --days 30
"""

import re
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AssetType(Enum):
    STOCK = "stock"
    INDEX = "index"
    BOND = "bond"
    FUND = "fund"
    FUTURE = "future"
    OPTION = "option"
    ETF = "etf"

class WindCodeGenerator:
    """WindPy 代码生成器"""
    
    def __init__(self):
        self.field_mappings = self._init_field_mappings()
        self.asset_patterns = self._init_asset_patterns()
    
    def _init_field_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """初始化字段映射"""
        return {
            AssetType.STOCK.value: {
                "price": ["open", "high", "low", "close", "volume", "amt"],
                "change": ["pct_chg", "change"],
                "valuation": ["pe_ttm", "pb_lf", "ps_ttm", "mkt_cap_ard"],
                "money_flow": ["mfd_inflow_xl", "mfd_inflow_l", "mfd_inflow_m", "mfd_inflow_s"],
                "technical": ["macd", "rsi", "kdj_k", "kdj_d", "boll_up", "boll_down"],
                "financial": ["roe_diluted", "roa", "gross_margin", "net_profit_margin"],
            },
            AssetType.BOND.value: {
                "price": ["close", "clean_price", "dirty_price"],
                "valuation": ["ytm_b", "duration", "convexity", "modified_duration"],
                "credit": ["creditrating", "issuerrating"],
            },
            AssetType.FUND.value: {
                "nav": ["nav", "nav_adj", "accum_nav"],
                "return": ["return_1m", "return_3m", "return_6m", "return_ytd"],
                "info": ["fund_manager", "fund_type", "establish_date"],
            },
            AssetType.INDEX.value: {
                "price": ["close", "open", "high", "low"],
                "change": ["pct_chg"],
            },
        }
    
    def _init_asset_patterns(self) -> Dict[str, str]:
        """初始化资产识别模式"""
        return {
            r"(\d{6}\.SH|\d{6}\.SZ|\d{5}\.HK)": AssetType.STOCK.value,
            r"(\d{6}\.OF)": AssetType.FUND.value,
            r"(T|TF|TS|IF|IC|IM|IH)\d{4}\.": AssetType.FUTURE.value,
            r"(\d{6}\.IB|\d{6}\.SH|\d{6}\.SZ)": AssetType.BOND.value,
        }
    
    def detect_asset_type(self, code: str) -> str:
        """检测资产类型"""
        for pattern, asset_type in self.asset_patterns.items():
            if re.search(pattern, code):
                return asset_type
        return AssetType.STOCK.value
    
    def suggest_fields(self, asset_type: str, data_category: str) -> List[str]:
        """推荐字段"""
        mappings = self.field_mappings.get(asset_type, {})
        return mappings.get(data_category, [])
    
    def generate_daily_price(self, codes: str, fields: str, start_date: str, end_date: str, options: str = "") -> str:
        """生成日线价格代码"""
        return f'''from WindPy import w
import pandas as pd

w.start()

# 获取日线数据
codes = "{codes}"
fields = "{fields}"
start_date = "{start_date}"
end_date = "{end_date}"

err, df = w.wsd(codes, fields, start_date, end_date, "{options}", usedf=True)

if err == 0:
    print(df.head())
    # df.to_excel("output.xlsx")
else:
    print("错误码:", err)

w.stop()
'''
    
    def generate_snapshot(self, codes: str, fields: str, trade_date: str) -> str:
        """生成截面快照代码"""
        return f'''from WindPy import w
import pandas as pd

w.start()

# 获取截面数据
codes = "{codes}"
fields = "{fields}"
trade_date = "{trade_date}"

err, df = w.wss(codes, fields, f"tradeDate={trade_date}", usedf=True)

if err == 0:
    print(df)
else:
    print("错误码:", err)

w.stop()
'''
    
    def generate_sector_constituents(self, date: str, sector_id: str) -> str:
        """生成板块成分代码"""
        return f'''from WindPy import w
import pandas as pd

w.start()

# 获取板块成分
date = "{date}"
sector_id = "{sector_id}"

result = w.wset("sectorconstituent", f"date={date};sectorid={sector_id}")

if result.ErrorCode == 0:
    df = pd.DataFrame({{
        'date': result.Data[0],
        'wind_code': result.Data[1],
        'sec_name': result.Data[2]
    }})
    print(df)
    print("\\n共", len(df), "只成分股")
else:
    print("错误:", result.Data)

w.stop()
'''
    
    def generate_minute_data(self, code: str, fields: str, start_time: str, end_time: str, options: str = "BarSize=1") -> str:
        """生成分钟数据代码"""
        return f'''from WindPy import w
import pandas as pd

w.start()

# 获取分钟数据
code = "{code}"
fields = "{fields}"
start_time = "{start_time}"
end_time = "{end_time}"

err, df = w.wsi(code, fields, start_time, end_time, "{options}", usedf=True)

if err == 0:
    print(df.head())
else:
    print("错误码:", err)

w.stop()
'''
    
    def generate_realtime_quote(self, codes: str, fields: str) -> str:
        """生成实时行情代码"""
        return f'''from WindPy import w

w.start()

# 获取实时行情
codes = "{codes}"
fields = "{fields}"

err, df = w.wsq(codes, fields, usedf=True)

if err == 0:
    print(df)
else:
    print("错误码:", err)

w.stop()
'''
    
    def generate_trading_calendar(self, start_date: str, end_date: str) -> str:
        """生成交易日历代码"""
        return f'''from WindPy import w

w.start()

# 获取交易日序列
start_date = "{start_date}"
end_date = "{end_date}"

result = w.tdays(start_date, end_date, "")

if result.ErrorCode == 0:
    print("交易日数量:", len(result.Data[0]))
    print("首个交易日:", result.Data[0][0])
    print("最后交易日:", result.Data[0][-1])
else:
    print("错误:", result.Data)

w.stop()
'''
    
    def generate_money_flow(self, code: str, start_date: str, end_date: str) -> str:
        """生成资金流向代码"""
        return f'''from WindPy import w
import pandas as pd

w.start()

# 获取资金流向
code = "{code}"
fields = "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s"  # 超大单/大单/中单/小单
start_date = "{start_date}"
end_date = "{end_date}"

err, df = w.wsd(code, fields, start_date, end_date, "", usedf=True)

if err == 0:
    # 计算净流入
    df['total_inflow'] = df.sum(axis=1)
    print(df)
else:
    print("错误码:", err)

w.stop()
'''
    
    def parse_natural_language(self, description: str) -> Tuple[str, Dict[str, str]]:
        """解析自然语言描述"""
        description = description.lower()
        
        # 检测资产代码
        code_pattern = r'(\d{6}\.\w{2}|\d{5}\.\w{2})'
        codes = re.findall(code_pattern, description)
        code = codes[0] if codes else "600519.SH"  # 默认茅台
        
        # 检测时间范围
        time_patterns = {
            r'近(\d+)天|最近(\d+)天': lambda m: (f"-{m.group(1) or m.group(2)}D", ""),
            r'近(\d+)个月': lambda m: (f"-{m.group(1)}M", ""),
            r'近(\d+)年': lambda m: (f"-{m.group(1)}Y", ""),
            r'(\d{4}-\d{2}-\d{2})到(\d{4}-\d{2}-\d{2})': lambda m: (m.group(1), m.group(2)),
        }
        
        start_date = "-30D"
        end_date = ""
        for pattern, handler in time_patterns.items():
            match = re.search(pattern, description)
            if match:
                start_date, end_date = handler(match)
                break
        
        # 检测数据类型并生成对应代码
        if '分钟' in description or '分钟线' in description:
            return "minute", {
                "code": code,
                "fields": "open,high,low,close,volume",
                "start_time": "2024-01-01 09:30:00",
                "end_time": "2024-01-01 15:00:00",
                "options": "BarSize=1"
            }
        elif '实时' in description or '行情' in description:
            return "realtime", {
                "codes": code,
                "fields": "rt_last,rt_pct_chg,rt_vol"
            }
        elif '成分' in description or '成分股' in description:
            return "sector", {
                "date": "20241231",
                "sector_id": "a39901011i000000"  # 申万三级行业
            }
        elif '资金' in description or '流向' in description:
            return "money_flow", {
                "code": code,
                "start_date": start_date,
                "end_date": end_date
            }
        elif '日历' in description or '交易日' in description:
            return "calendar", {
                "start_date": start_date if not start_date.startswith("-") else "20240101",
                "end_date": end_date if end_date else "20241231"
            }
        else:
            # 默认日线价格
            return "daily", {
                "codes": code,
                "fields": "close,open,high,low,volume,pct_chg",
                "start_date": start_date,
                "end_date": end_date,
                "options": "PriceAdj=F"
            }
    
    def generate(self, description: str) -> str:
        """主生成函数 - 自然语言"""
        template_type, params = self.parse_natural_language(description)
        
        generators = {
            "daily": self.generate_daily_price,
            "snapshot": self.generate_snapshot,
            "sector": self.generate_sector_constituents,
            "minute": self.generate_minute_data,
            "realtime": self.generate_realtime_quote,
            "calendar": self.generate_trading_calendar,
            "money_flow": self.generate_money_flow,
        }
        
        generator = generators.get(template_type)
        if generator:
            return generator(**params)
        else:
            return f"错误: 未找到模板 '{template_type}'"


def main():
    parser = argparse.ArgumentParser(description='WindPy 代码生成器')
    parser.add_argument('description', nargs='?', help='自然语言描述，如"获取贵州茅台近30天收盘价"')
    parser.add_argument('--template', choices=['daily', 'snapshot', 'sector', 'minute', 'realtime', 'calendar', 'money_flow'],
                       help='使用指定模板')
    parser.add_argument('--codes', help='资产代码')
    parser.add_argument('--fields', help='数据字段')
    parser.add_argument('--days', type=int, default=30, help='天数')
    
    args = parser.parse_args()
    
    generator = WindCodeGenerator()
    
    if args.description:
        # 自然语言模式
        print(f"输入: {args.description}")
        print("="*60)
        code = generator.generate(args.description)
        print(code)
    else:
        # 示例模式
        test_cases = [
            "获取贵州茅台近30天收盘价",
            "查询600519.SH的分钟线数据",
            "获取沪深300成分股列表",
            "查询某股票的资金流向",
            "获取实时行情",
            "获取2024年交易日历",
        ]
        
        for test in test_cases:
            print(f"\n{'='*60}")
            print(f"输入: {test}")
            print(f"{'='*60}")
            code = generator.generate(test)
            print(code)


if __name__ == "__main__":
    main()
