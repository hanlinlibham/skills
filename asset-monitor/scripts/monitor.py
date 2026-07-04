#!/usr/bin/env python3
"""
资产异常波动日频监控脚本

使用方法:
    python scripts/monitor.py
    python scripts/monitor.py --notify
"""

from WindPy import w
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# 监控资产配置
ASSET_CONFIG = {
    "sw3_industry": {
        "name": "申万三级行业",
        "type": "sector",
        "sectorid": "a39901011i000000",  # 259个
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


def analyze_asset(code, name, category, threshold_z=2.0, min_days=30):
    """分析单个资产的波动"""
    try:
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        today_str = datetime.now().strftime('%Y%m%d')
        
        hist = w.wsd(code, "pct_chg", one_year_ago, today_str, "", usedf=True)
        
        if hist[0] == 0 and len(hist[1]) > min_days:
            returns = hist[1]['PCT_CHG'].dropna()
            if len(returns) > min_days:
                mean_ret = returns.mean()
                std_ret = returns.std()
                today_ret = returns.iloc[-1] if len(returns) > 0 else None
                
                if today_ret is not None and std_ret > 0:
                    z_score = (today_ret - mean_ret) / std_ret
                    
                    if abs(z_score) > threshold_z:
                        return {
                            'category': category,
                            'code': code,
                            'name': name,
                            'today_return': float(today_ret),
                            'z_score': float(z_score),
                            'direction': '大涨' if z_score > 0 else '大跌'
                        }
    except Exception:
        pass
    return None


def monitor_sector(config, threshold_z=2.0):
    """监控板块类资产"""
    print(f"\n[监控] {config['name']}")
    
    today_str = datetime.now().strftime('%Y%m%d')
    result = w.wset("sectorconstituent", f"date={today_str};sectorid={config['sectorid']}")
    
    if result.ErrorCode != 0 or len(result.Data) < 2:
        print(f"  ⚠️ 未获取到数据")
        return []
    
    codes = result.Data[1]
    names = result.Data[2]
    
    print(f"  共 {len(codes)} 个资产")
    
    anomalies = []
    for code, name in zip(codes, names):
        result = analyze_asset(code, name, config['name'], threshold_z)
        if result:
            anomalies.append(result)
            print(f"  ⚠️ {name}: {result['today_return']:+.2f}% (Z={result['z_score']:+.2f})")
    
    print(f"  发现 {len(anomalies)} 个异常")
    return anomalies


def monitor_direct(config, threshold_z=2.0):
    """监控直接代码类资产"""
    print(f"\n[监控] {config['name']} ({len(config['codes'])}个)")
    
    # 获取名称
    try:
        result = w.wss(','.join(config['codes']), "sec_name", "", usedf=True)
        name_map = dict(zip(result[1].index, result[1]['SEC_NAME'])) if result[0] == 0 else {}
    except:
        name_map = {code: code for code in config['codes']}
    
    anomalies = []
    for code in config['codes']:
        name = name_map.get(code, code)
        result = analyze_asset(code, name, config['name'], threshold_z)
        if result:
            anomalies.append(result)
            print(f"  ⚠️ {name}: {result['today_return']:+.2f}% (Z={result['z_score']:+.2f})")
    
    print(f"  发现 {len(anomalies)} 个异常")
    return anomalies


def run_monitoring(threshold_z=2.0):
    """运行完整监控"""
    today = datetime.now()
    
    print("="*70)
    print(f"📊 资产异常波动监控")
    print(f"时间: {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"Z值阈值: {threshold_z}")
    print("="*70)
    
    all_anomalies = []
    
    for key, config in ASSET_CONFIG.items():
        try:
            if config['type'] == 'sector':
                anomalies = monitor_sector(config, threshold_z)
            else:
                anomalies = monitor_direct(config, threshold_z)
            all_anomalies.extend(anomalies)
        except Exception as e:
            print(f"  ❌ {config['name']} 监控失败: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ 监控完成，共发现 {len(all_anomalies)} 个异常")
    print(f"{'='*70}\n")
    
    return all_anomalies


def generate_excel_report(anomalies, output_dir="output"):
    """生成 Excel 报告"""
    if not anomalies:
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.DataFrame(anomalies)
    df = df.sort_values('z_score', key=abs, ascending=False)
    
    today_str = datetime.now().strftime('%Y%m%d')
    excel_path = os.path.join(output_dir, f"asset_anomaly_report_{today_str}.xlsx")
    df.to_excel(excel_path, index=False, sheet_name='异常波动资产')
    
    print(f"✅ Excel 报告: {excel_path}")
    return excel_path


def generate_text_report(anomalies):
    """生成文本报告"""
    if not anomalies:
        return "📊 资产异常监控\n\n✅ 今日无异常资产。"
    
    lines = [
        "📊 资产异常波动报告",
        f"报告时间: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        f"共发现 {len(anomalies)} 个异常资产:",
        "",
    ]
    
    for i, item in enumerate(anomalies, 1):
        emoji = "🚀" if item['z_score'] > 0 else "📉"
        lines.append(
            f"{i}. {emoji} {item['name']} ({item['category']})\n"
            f"   涨跌幅: {item['today_return']:+.2f}% | Z值: {item['z_score']:+.2f}"
        )
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='资产异常波动监控')
    parser.add_argument('--threshold', type=float, default=2.0, help='Z-Score阈值')
    parser.add_argument('--output', type=str, default='output', help='输出目录')
    parser.add_argument('--notify', action='store_true', help='打印报告')
    
    args = parser.parse_args()
    
    # 连接 Wind
    print("正在连接 Wind...")
    w.start()
    print("✅ Wind 连接成功\n")
    
    try:
        # 运行监控
        anomalies = run_monitoring(threshold_z=args.threshold)
        
        # 生成报告
        if anomalies:
            excel_path = generate_excel_report(anomalies, args.output)
            
            if args.notify:
                print("\n" + generate_text_report(anomalies))
        else:
            print("✅ 今日无异常资产")
            
    finally:
        w.stop()
        print("\nWind 连接已断开")


if __name__ == "__main__":
    main()
