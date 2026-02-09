---
name: asset-monitor
description: 资产异常波动日频监控。当用户需要对股票、指数、商品等资产进行日频异常波动监控，检测偏离历史均值超过2倍标准差的异常，并生成报告时使用此技能。依赖 windpy-sdk 获取数据。
---

# 资产异常波动日频监控

## 触发条件

当用户需要：
- 监控多资产类别的日频异常波动
- 检测偏离历史均值超过2倍标准差的资产
- 生成异常波动报告（Excel/Markdown）
- 发送飞书/邮件通知

## 依赖

本 skill **依赖 windpy-sdk** 获取数据，请先确保：
1. windpy-sdk skill 可用
2. Wind 金融终端已启动

## 使用方法

### 直接运行监控脚本

```bash
python scripts/monitor.py
```

### 带通知推送

```bash
python scripts/monitor.py --notify
```

### Python API

```python
from WindPy import w
import pandas as pd

# 1. 连接 Wind
w.start()

# 2. 获取资产列表并监控
# 详见 scripts/monitor.py 实现

# 3. 生成报告
# 详见 scripts/reporter.py 实现

w.stop()
```

## 监控资产范围

| 资产类别 | 数量 | 说明 |
|---------|------|------|
| 申万三级行业 | 259个 | 全部三级行业指数 |
| A股主要指数 | 9个 | 沪深300、中证500等 |
| 中债指数 | 5个 | 中债总指数、国债指数等 |
| 主流ETF | 8个 | 沪深300ETF、创业板ETF等 |
| 商品期货 | 8个 | 黄金、白银、铜、原油等 |
| 全球指数 | 9个 | 标普500、纳指、道指等 |

**总计**: 298个资产

## 核心逻辑

### Z-Score 计算

```
Z = (今日涨跌幅 - 历史均值) / 历史标准差
```

### 异常判定

```python
if abs(z_score) > 2.0:
    标记为异常
    direction = "大涨" if z_score > 0 else "大跌"
```

### 筛选条件

- 历史数据 > 30个交易日
- 历史标准差 > 0
- 按 |Z| 绝对值降序排列

## 监控脚本

见 `scripts/monitor.py`

**功能**:
- 遍历所有配置的资产
- 计算每个资产的 Z-Score
- 识别异常波动资产
- 生成 Excel 报告

## 报告生成

见 `scripts/reporter.py`

**功能**:
- 生成 Excel 报告
- 生成 Markdown 报告
- 发送飞书通知
- 发送邮件报告

## 输出示例

### Excel 报告字段

| 字段 | 说明 |
|------|------|
| category | 资产类别 |
| code | 资产代码 |
| name | 资产名称 |
| today_return | 今日涨跌幅(%) |
| z_score | Z值 |
| direction | 大涨/大跌 |

### Markdown 报告示例

```markdown
# 📊 资产异常波动报告

## 异常汇总

| 资产 | 类别 | 涨跌幅 | Z值 | 方向 |
|-----|-----|-------:|----:|:----:|
| 白银 | 商品期货 | -14.02% | -4.39 | 📉 大跌 |
| 印染 | 申万三级 | +5.30% | +3.33 | 🚀 大涨 |
```

## 配置文件

见 `references/monitor-config-example.json`

```json
{
  "threshold_z": 2.0,
  "min_trading_days": 30,
  "lookback_period": "-252TD",
  "notification": {
    "feishu": {"enabled": true},
    "email": {"enabled": true}
  }
}
```

## 定时任务设置

```bash
# crontab -e
# 每日15:30运行
30 15 * * * cd /path/to/skill && python scripts/monitor.py --notify
```

## 参考文档

- `references/monitor-config-example.json` - 配置示例
- `references/usage-guide.md` - 详细使用指南

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Wind连接失败 | Wind终端未启动 | 启动Wind终端 |
| 无数据返回 | 无数据权限 | 联系Wind开通权限 |
| 报告为空 | 今日无异常 | 正常现象 |
