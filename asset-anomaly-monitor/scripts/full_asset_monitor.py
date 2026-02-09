"""
全量资产异常波动日频监控脚本
监控范围：申万三级行业(259个)、A股指数、中债指数、ETF、商品、全球指数
"""

from WindPy import w
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class AssetAnomalyMonitor:
    """全量资产异常波动监控器"""
    
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
        "china_bond": {
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
    
    def __init__(self, threshold_z=2.0, min_days=30):
        self.threshold_z = threshold_z
        self.min_days = min_days
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y%m%d')
        self.one_year_ago = (self.today - timedelta(days=365)).strftime('%Y%m%d')
        self.all_anomalies = []
        
    def start(self):
        w.start()
        print(f"{'='*80}")
        print(f"全量资产异常波动日频监控")
        print(f"报告时间: {self.today.strftime('%Y-%m-%d %H:%M')}")
        print(f"分析区间: {self.one_year_ago} 至 {self.today_str}")
        print(f"Z-Score阈值: {self.threshold_z}")
        print(f"{'='*80}\n")
        
    def stop(self):
        w.stop()
        
    def get_codes_from_sector(self, sectorid):
        try:
            result = w.wset("sectorconstituent", f"date={self.today_str};sectorid={sectorid}")
            if result.ErrorCode == 0 and len(result.Data) > 1:
                return result.Data[1], result.Data[2]
        except Exception as e:
            print(f"  获取板块失败: {e}")
        return [], []
    
    def analyze_single_asset(self, code, name, category):
        try:
            hist = w.wsd(code, "pct_chg", self.one_year_ago, self.today_str, "", usedf=True)
            if hist[0] == 0 and len(hist[1]) > self.min_days:
                returns = hist[1]['PCT_CHG'].dropna()
                if len(returns) > self.min_days:
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
                                'today_return': today_ret,
                                'z_score': z_score,
                                'std_annual': std_ret,
                                'direction': '大涨' if z_score > 0 else '大跌'
                            }
        except Exception:
            pass
        return None
    
    def run_full_monitoring(self):
        self.start()
        total_anomalies = 0
        
        for key, config in self.ASSET_CONFIG.items():
            try:
                if config['type'] == 'sector':
                    count = self._monitor_sector(key, config)
                else:
                    count = self._monitor_direct(key, config)
                total_anomalies += count
            except Exception as e:
                print(f"  监控 {config['name']} 失败: {e}")
        
        print(f"\n{'='*80}")
        print(f"共发现 {total_anomalies} 个异常波动资产\n")
        return self.all_anomalies
    
    def _monitor_sector(self, key, config):
        print(f"\n[监控] {config['name']}")
        codes, names = self.get_codes_from_sector(config['sectorid'])
        if not codes:
            print(f"  未获取到数据")
            return 0
        
        count = 0
        for code, name in zip(codes, names):
            result = self.analyze_single_asset(code, name, config['name'])
            if result:
                self.all_anomalies.append(result)
                print(f"  ⚠️ {name}: 涨跌幅={result['today_return']:.2f}%, Z值={result['z_score']:.2f}")
                count += 1
        
        print(f"  发现 {count} 个异常")
        return count
    
    def _monitor_direct(self, key, config):
        print(f"\n[监控] {config['name']} ({len(config['codes'])}个)")
        
        try:
            name_result = w.wss(','.join(config['codes']), "sec_name", "", usedf=True)
            name_map = dict(zip(name_result[1].index, name_result[1]['SEC_NAME'])) if name_result[0] == 0 else {}
        except:
            name_map = {code: code for code in config['codes']}
        
        count = 0
        for code in config['codes']:
            name = name_map.get(code, code)
            result = self.analyze_single_asset(code, name, config['name'])
            if result:
                self.all_anomalies.append(result)
                print(f"  ⚠️ {name}: 涨跌幅={result['today_return']:.2f}%, Z值={result['z_score']:.2f}")
                count += 1
        
        print(f"  发现 {count} 个异常")
        return count
    
    def generate_report(self, anomalies=None, output_dir="output"):
        if anomalies is None:
            anomalies = self.all_anomalies
        
        os.makedirs(output_dir, exist_ok=True)
        
        if len(anomalies) > 0:
            df = pd.DataFrame(anomalies)
            df = df.sort_values('z_score', key=abs, ascending=False)
            
            excel_path = os.path.join(output_dir, f"asset_anomaly_report_{self.today_str}.xlsx")
            df.to_excel(excel_path, index=False, sheet_name='异常波动资产')
            print(f"✅ 结果已保存: {excel_path}")
            return excel_path, df
        else:
            print("\n✅ 未发现异常")
            return None, None


def main():
    monitor = AssetAnomalyMonitor(threshold_z=2.0, min_days=30)
    
    try:
        anomalies = monitor.run_full_monitoring()
        monitor.generate_report(anomalies)
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
