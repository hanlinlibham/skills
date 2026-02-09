#!/usr/bin/env python3
"""
Asset Monitor - 监控主程序

依赖 windpy-sdk 获取数据，专注于监控逻辑
"""

import sys
import os
import argparse

# 添加 windpy-sdk 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'windpy-sdk'))

from windpy_sdk import WindClient
from asset_monitor import AssetMonitor, ReportGenerator


def main():
    parser = argparse.ArgumentParser(description='资产异常波动监控')
    parser.add_argument('--threshold', type=float, default=2.0, help='Z-Score阈值，默认2.0')
    parser.add_argument('--min-days', type=int, default=30, help='最小交易日，默认30')
    parser.add_argument('--output', type=str, default='output', help='输出目录')
    parser.add_argument('--notify', action='store_true', help='发送通知')
    parser.add_argument('--email', action='store_true', help='发送邮件')
    parser.add_argument('--feishu', action='store_true', help='发送飞书')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📊 Asset Monitor - 资产异常波动监控")
    print("="*70)
    print()
    
    # 1. 运行监控
    monitor = AssetMonitor(threshold_z=args.threshold, min_days=args.min_days)
    
    with WindClient() as client:
        anomalies = monitor.run(client)
    
    # 2. 生成报告
    if anomalies:
        reporter = ReportGenerator()
        
        # Excel 报告
        excel_path = reporter.to_excel(anomalies, args.output)
        
        # Markdown 报告
        md_report = reporter.to_markdown(anomalies)
        print("\n" + md_report)
        
        # 3. 发送通知
        if args.notify or args.feishu:
            text_report = reporter.to_text(anomalies)
            reporter.send_feishu(text_report)
        
        if args.notify or args.email:
            if excel_path:
                reporter.send_email(excel_path)
    else:
        print("\n✅ 今日无异常资产")
    
    print("\n" + "="*70)
    print("监控完成")
    print("="*70)


if __name__ == "__main__":
    main()
