#!/usr/bin/env python3
"""
WindPy Code Generator
WindPy 代码生成器 - 通用模板

使用方法:
    python windpy_code_generator.py --function wsd --codes 600519.SH --fields close
    
或直接在代码中调用:
    from windpy_code_generator import generate_wsd_code
    code = generate_wsd_code(codes="600519.SH", fields="close", days=30)
    print(code)
"""

def generate_wsd_code(codes="600519.SH", fields="close", days=30, options="PriceAdj=F"):
    """生成 WSD 查询代码"""
    return f'''from WindPy import w
import pandas as pd

w.start()

# 获取日级数据
codes = "{codes}"
fields = "{fields}"
err, df = w.wsd(codes, fields, "-{days}D", "", "{options}", usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error: {{err}}")

w.stop()
'''

def generate_wss_code(codes="600519.SH", fields="pe_ttm,pb_lf"):
    """生成 WSS 查询代码"""
    return f'''from WindPy import w
import pandas as pd

w.start()

# 获取截面数据
codes = "{codes}"
fields = "{fields}"
err, df = w.wss(codes, fields, "tradeDate=20241231", usedf=True)

if err == 0:
    print(df)
else:
    print(f"Error: {{err}}")

w.stop()
'''

def generate_wset_code(table="sectorconstituent", sectorid="a39901011i000000"):
    """生成 WSET 查询代码"""
    return f'''from WindPy import w
import pandas as pd

w.start()

# 获取报表数据
tableName = "{table}"
options = "date=20241231;sectorid={sectorid}"

result = w.wset(tableName, options)

if result.ErrorCode == 0:
    df = pd.DataFrame({{
        'date': result.Data[0],
        'wind_code': result.Data[1],
        'sec_name': result.Data[2]
    }})
    print(df)
    print(f"Total: {{len(df)}} items")
else:
    print(f"Error: {{result.Data}}")

w.stop()
'''

def generate_stock_search_code(keyword="茅台"):
    """生成股票搜索代码"""
    return f'''from WindPy import w

w.start()

# 搜索股票: {keyword}
result = w.wset("sectorconstituent", "date=20241231;sectorid=a001010100000000")

if result.ErrorCode == 0:
    matches = []
    for i in range(len(result.Data[2])):
        if "{keyword}" in result.Data[2][i]:
            matches.append({{
                'code': result.Data[1][i],
                'name': result.Data[2][i]
            }})
    
    print(f"Found {{len(matches)}} matches:")
    for m in matches[:10]:
        print(f"  {{m['code']}} - {{m['name']}}")

w.stop()
'''

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WindPy Code Generator')
    parser.add_argument('--function', choices=['wsd', 'wss', 'wset', 'search'], 
                       default='wsd', help='Wind function type')
    parser.add_argument('--codes', default='600519.SH', help='Stock codes')
    parser.add_argument('--fields', default='close', help='Data fields')
    parser.add_argument('--days', type=int, default=30, help='Days for wsd')
    
    args = parser.parse_args()
    
    if args.function == 'wsd':
        code = generate_wsd_code(args.codes, args.fields, args.days)
    elif args.function == 'wss':
        code = generate_wss_code(args.codes, args.fields)
    elif args.function == 'wset':
        code = generate_wset_code()
    elif args.function == 'search':
        code = generate_stock_search_code(args.codes)
    
    print(code)

if __name__ == "__main__":
    main()
