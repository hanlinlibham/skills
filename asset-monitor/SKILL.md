---
name: asset-monitor
description: 资产异常波动监控与报告生成。基于 windpy-sdk 获取数据，实现多资产类别的日频异常监控、自动报告生成和邮件推送。专注于监控逻辑，数据获取委托给 windpy-sdk。
---

# 资产异常波动监控与报告生成

## 定位

本 skill **专注于监控逻辑和报告生成**，数据获取完全委托给 **windpy-sdk**。

**架构关系**:
```
asset-monitor (监控逻辑 + 报告生成)
    ↓ 导入
windpy-sdk (数据获取)
    ↓ 调用
WindPy (Wind API)
```

## 依赖

必须预先安装 windpy-sdk:
```bash
# 确保 windpy-sdk 在 Python 路径中
export PYTHONPATH="/path/to/skills/windpy-sdk:$PYTHONPATH"
```

Python 依赖:
```python
# asset-monitor 内部导入
from windpy_sdk import WindClient, get_sector_constituents, get_historical_returns
```

## 功能

### 1. 异常监控
- **监控资产**: 申万三级(259) + A股指数(9) + 债券(5) + ETF(8) + 商品(8) + 全球指数(9)
- **检测方法**: Z-Score > 2 (偏离历史均值超过2倍标准差)
- **运行模式**: 手动运行 / 定时任务

### 2. 报告生成
- **Excel 报告**: 异常资产详细信息
- **飞书推送**: 自动发送异常提醒
- **邮件报告**: 带附件的完整报告

### 3. 原因分析（可选）
- 通过 Gangtise MCP 搜索研报原因
- 自动生成带来源的分析报告

## 使用方式

### 方式1: 直接运行
```bash
cd /path/to/skills/asset-monitor
python scripts/monitor.py
```

### 方式2: Python API
```python
from asset_monitor import AssetMonitor, ReportGenerator
from windpy_sdk import WindClient

# 1. 运行监控
monitor = AssetMonitor(threshold_z=2.0)
with WindClient() as client:
    anomalies = monitor.run(client)

# 2. 生成报告
reporter = ReportGenerator()
excel_path = reporter.to_excel(anomalies)
reporter.send_feishu(excel_path)
reporter.send_email(excel_path)
```

### 方式3: 定时任务
```bash
# crontab -e
30 15 * * * cd /path/to/skills/asset-monitor && python scripts/monitor.py --notify
```

## 配置文件

```json
{
  "monitor": {
    "threshold_z": 2.0,
    "min_trading_days": 30,
    "lookback_period": "-252TD"
  },
  "assets": {
    "sw3_industry": {"enabled": true},
    "ashare_index": {"enabled": true},
    "bond_index": {"enabled": true},
    "etf": {"enabled": true},
    "commodity": {"enabled": true},
    "global_index": {"enabled": true}
  },
  "notification": {
    "feishu": {"enabled": true, "webhook": "..."},
    "email": {"enabled": true, "recipients": ["..."]}
  }
}
```

## 核心类

### AssetMonitor
```python
class AssetMonitor:
    def __init__(self, threshold_z=2.0, min_days=30):
        self.threshold_z = threshold_z
        self.min_days = min_days
        
    def run(self, client: WindClient) -> List[dict]:
        """
        运行完整监控
        
        Returns:
        --------
        List of anomaly dict with keys:
        - category: 资产类别
        - code: 资产代码
        - name: 资产名称
        - today_return: 今日涨跌幅
        - z_score: Z值
        - direction: '大涨' or '大跌'
        """
        
    def analyze_single(self, client: WindClient, code: str, name: str) -> Optional[dict]:
        """分析单个资产"""
```

### ReportGenerator
```python
class ReportGenerator:
    def to_excel(self, anomalies: List[dict], output_dir: str = 'output') -> str:
        """生成 Excel 报告"""
        
    def to_markdown(self, anomalies: List[dict]) -> str:
        """生成 Markdown 报告"""
        
    def send_feishu(self, file_path: str, webhook: str = None):
        """发送飞书通知"""
        
    def send_email(self, file_path: str, recipients: List[str] = None):
        """发送邮件报告"""
```

### GangtiseResearcher（可选）
```python
class GangtiseResearcher:
    """使用 Gangtise MCP 搜索异常原因"""
    
    def research(self, asset_name: str, keywords: str) -> dict:
        """搜索资产异常原因"""
        
    def batch_research(self, anomalies: List[dict]) -> List[dict]:
        """批量研究多个异常"""
```

## 完整示例

```python
#!/usr/bin/env python3
"""完整的监控流程示例"""

import sys
sys.path.insert(0, '/path/to/skills/windpy-sdk')

from windpy_sdk import WindClient
from asset_monitor import AssetMonitor, ReportGenerator, GangtiseResearcher

def main():
    # 1. 监控阶段
    print("="*60)
    print("📊 开始资产异常监控")
    print("="*60)
    
    monitor = AssetMonitor(threshold_z=2.0)
    
    with WindClient() as client:
        anomalies = monitor.run(client)
    
    if not anomalies:
        print("✅ 今日无异常资产")
        return
    
    print(f"\n发现 {len(anomalies)} 个异常资产")
    
    # 2. 报告阶段
    print("\n" + "="*60)
    print("📝 生成报告")
    print("="*60)
    
    reporter = ReportGenerator()
    
    # Excel 报告
    excel_path = reporter.to_excel(anomalies)
    print(f"✅ Excel报告: {excel_path}")
    
    # Markdown 报告
    md_report = reporter.to_markdown(anomalies)
    print(f"✅ Markdown报告生成完成")
    
    # 3. 推送阶段
    print("\n" + "="*60)
    print("📤 发送通知")
    print("="*60)
    
    reporter.send_feishu(excel_path)
    print("✅ 飞书推送完成")
    
    reporter.send_email(excel_path)
    print("✅ 邮件发送完成")
    
    # 4. 原因分析（可选）
    print("\n" + "="*60)
    print("🔍 深度原因分析")
    print("="*60)
    
    researcher = GangtiseResearcher()
    for anomaly in anomalies[:3]:  # 分析前3个
        result = researcher.research(
            anomaly['name'],
            f"{anomaly['name']} {'上涨' if anomaly['z_score'] > 0 else '下跌'} 原因"
        )
        print(f"\n{anomaly['name']}: 找到 {result['total']} 条相关研报")

if __name__ == "__main__":
    main()
```

## 目录结构

```
asset-monitor/
├── SKILL.md                      # 本文档
├── config/
│   └── monitor_config.json       # 监控配置
├── scripts/
│   ├── monitor.py               # 监控主程序
│   └── daily_run.py             # 定时任务入口
├── asset_monitor/
│   ├── __init__.py
│   ├── monitor.py               # AssetMonitor 类
│   ├── reporter.py              # ReportGenerator 类
│   ├── researcher.py            # GangtiseResearcher 类 (可选)
│   └── utils.py                 # 工具函数
└── output/                       # 报告输出目录
```

## 与 windpy-sdk 的关系

| 职责 | windpy-sdk | asset-monitor |
|-----|-----------|---------------|
| WindPy 连接 | ✅ 管理 | ❌ 不管理 |
| 数据获取 | ✅ 提供 | ❌ 使用 SDK |
| 异常检测 | ❌ 不做 | ✅ 实现 |
| 报告生成 | ❌ 不做 | ✅ 实现 |
| 通知推送 | ❌ 不做 | ✅ 实现 |

## 注意事项

1. **必须安装 windpy-sdk** 并确保在 Python 路径中
2. **Wind 终端必须启动**（由 windpy-sdk 管理连接）
3. **Gangtise 研究是可选功能**，需要额外配置 MCP

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| ImportError: windpy_sdk | windpy-sdk 不在路径 | 添加 PYTHONPATH |
| Wind 连接失败 | Wind 终端未启动 | 启动 Wind 终端 |
| 无异常数据 | 市场正常波动 | 正常现象 |
| 飞书推送失败 | Webhook 错误 | 检查配置 |
