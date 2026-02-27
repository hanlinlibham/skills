---
name: windpy-sdk
description: >
  Wind 金融终端 Python API 调用技能。当用户需要通过 WindPy 获取 A 股、债券、基金、
  期货、宏观数据，或查询 Wind 字段、板块代码、SectorID 时触发。
  关键词: Wind, WindPy, w.wsd, w.wss, w.wset, w.wsq, w.edb, 万得
allowed-tools: Bash(python*), Bash(curl*), Read, Grep, Glob
---

# WindPy SDK

## 连接方式

根据操作系统选择合适的连接方式：

| 平台 | 推荐模式 | 适用场景 |
|------|----------|----------|
| **macOS / Linux** | 常驻服务 | 自动化、批量查询、长任务 |
| **Windows** | 直连模式 | 交互式、短任务、快速查询 |

> **注意**：Windows 下常驻服务模式可能因 WindPy 线程兼容性问题导致连接不稳定，建议优先使用直连模式。

### 常驻服务模式（macOS / Linux 推荐）

避免每次调用弹出 Wind 登录窗口，适合自动化与批量查询。

```bash
# macOS / Linux
python scripts/wind_server.py &

# 健康检查
curl http://localhost:18888/health

# 停止（通过 HTTP）
curl http://localhost:18888/shutdown
```

通过客户端调用，返回 pandas DataFrame：

```python
import sys; sys.path.insert(0, "<this_skill_dir>/scripts")
from wind_client import wsd, wss, wset, wsq, edb, wsi, tdays, tdaysoffset

df = wsd("000300.SH", "close,pct_chg", "-30D")
df = wss("600519.SH,000858.SZ", "sec_name,close,pe_ttm")
df = wset("sectorconstituent", "date=20241231;windcode=000300.SH")
df = edb("M0001383", "2024-01-01", "2024-12-31")
df = wsi("600519.SH", "close,volume", "-0D 09:30:00", "", "BarSize=5")
dates = tdays("20260101", "20260226")
```

### Windows 常驻服务（推荐）

使用命名管道实现连接共享，避免每次登录和抢占桌面 Wind。

**优点：**
- 只登录一次，多个客户端复用连接
- 不抢占桌面 Wind 终端
- 支持多进程/多脚本同时查询

```bash
# 终端1: 启动服务（保持运行）
python scripts/wind_server_win.py

# 终端2/3/4...: 使用客户端查询
python -c "from scripts.wind_client_win import wsd; print(wsd('000300.SH', 'close', '-5D'))"
```

**注意**: 需要安装 `pywin32`: `pip install pywin32 pandas`

### 直连模式（Windows，简单场景）

直接调用 WindPy，无需启动常驻服务。每次 `w.start()` 可能弹出 Wind 登录窗口，且会抢占桌面 Wind 终端。

```python
from WindPy import w
w.start()
err, df = w.wsd("000300.SH", "close", "-30D", "", "", usedf=True)
w.stop()
```

**Windows 完整示例**：

```python
import pandas as pd
import numpy as np
from WindPy import w

# 连接 Wind
w.start()

# 获取数据
err, df = w.wsd("000300.SH", "close,pct_chg", "-30D", "", "", usedf=True)

# 处理数据
if err == 0:
    print(df)

# 断开连接
w.stop()
```

## 全函数列表

### 核心数据函数

| 函数 | 用途 | 签名 |
|------|------|------|
| `wsd` | 日级时间序列 | `wsd(codes, fields, beginTime, endTime, options)` |
| `wss` | 截面快照 | `wss(codes, fields, options)` |
| `wset` | 报表数据集 | `wset(tableName, options)` |
| `wsq` | 实时行情快照 | `wsq(codes, fields, options)` |
| `edb` | 宏观经济指标 | `edb(codes, beginTime, endTime, options)` |
| `wsi` | 分钟K线序列 | `wsi(codes, fields, beginTime, endTime, options)` BarSize=1/5/15/30/60 |
| `wst` | 日内Tick跳价 | `wst(codes, fields, beginTime, endTime, options)` |

### 板块函数

| 函数 | 用途 | 签名 |
|------|------|------|
| `wsee` | 板块多维（成分截面） | `wsee(codes, fields, options)` codes=指数/板块代码 |
| `wses` | 板块时间序列 | `wses(codes, fields, beginTime, endTime, options)` |
| `wsed` | 板块查询 | `wsed(codes, fields, options)` codes=SectorID |

### 交易日工具

| 函数 | 用途 | 签名 |
|------|------|------|
| `tdays` | 交易日列表 | `tdays(beginTime, endTime, options)` → list |
| `tdaysoffset` | 交易日偏移 | `tdaysoffset(offset, beginTime, options)` → str |
| `tdayscount` | 交易日计数 | `tdayscount(beginTime, endTime, options)` → int |

### 辅助函数

| 函数 | 用途 | 签名 |
|------|------|------|
| `weqs` | 条件选股 | `weqs(filtername, options)` |
| `htocode` | 名称→Wind代码 | `htocode(codes, sec_type, options)` |
| `wai` | 智能API | `wai(func, input, options)` |
| `wgel` | 企业库 | `wgel(funname, windid, options)` |

## 常用速查

| 类别 | 示例 |
|------|------|
| 指数 | `000300.SH`(沪深300) `000905.SH`(中证500) `399006.SZ`(创业板指) |
| 行情字段 | `open, high, low, close, volume, amt, pct_chg` |
| 估值字段 | `pe_ttm, pb_lf, mkt_cap_ard` |
| 资金字段 | `mfd_inflow_xl, mfd_inflow_l, mfd_inflow_m, mfd_inflow_s` |
| 板块ID | `a001010100000000`(全A) `a39901011i000000`(申万三级) |
| 中债指数 | `CBA00101.CS`(新综合财富) `CBA00601.CS`(国债总财富) |
| 期货主力 | `IF00.CFE`(沪深300) `AU00.SHF`(黄金) `CU00.SHF`(沪铜) |
| 外汇 | `USDCNY.FX`(在岸) `USDCNH.FX`(离岸) `EURUSD.FX` |
| 期权 | `10XXXXXX.SH`(ETF期权，wss需.SH后缀) |
| 商品EDB | `S0031525`(WTI) `S0031526`(Brent) `G0010030`(黄金) |

## 参考文档

按需查阅，不要一次性全部加载：

- [references/field-catalog.md](references/field-catalog.md) — 行情/财务/资金/估值字段完整列表
- [references/sectorid-catalog.md](references/sectorid-catalog.md) — 板块 SectorID 完整目录
- [references/wset-tables.md](references/wset-tables.md) — wset 报表数据集用法
- [references/error-codes.md](references/error-codes.md) — 错误码及解决方案
- [references/bond-fields.md](references/bond-fields.md) — 债券专用字段 + 中债指数(CBA*.CS)
- [references/fund-fields.md](references/fund-fields.md) — 基金专用字段 + 区间收益率
- [references/future-fields.md](references/future-fields.md) — 期货专用字段 + 完整品种速查
- [references/options-fields.md](references/options-fields.md) — ETF期权合约查询 + Greeks
- [references/fx-fields.md](references/fx-fields.md) — 外汇货币对代码 + 汇率 EDB
- [references/technical-indicators.md](references/technical-indicators.md) — 技术指标 (MACD/RSI/KDJ/BOLL)
- [references/edb-indicators.md](references/edb-indicators.md) — EDB 宏观指标 + 大宗商品价格
- [references/options-cheatsheet.md](references/options-cheatsheet.md) — 函数 options 参数速查
- [references/asset-type-codes.md](references/asset-type-codes.md) — 资产类型代码

## 跨平台路径说明

Python 中路径分隔符跨平台兼容，以下写法均可：

```python
# 正斜杠（推荐，全平台通用）
sys.path.insert(0, ".claude/skills/windpy-sdk/scripts")

# 反斜杠（Windows 也支持，但需注意转义）
sys.path.insert(0, ".claude\\skills\\windpy-sdk\\scripts")

# os.path.join（最保险）
sys.path.insert(0, os.path.join(".claude", "skills", "windpy-sdk", "scripts"))
```

## Windows 中文乱码解决方案

Windows 控制台默认使用 GBK 编码，可能导致 Wind 返回的中文数据显示为乱码。在脚本开头添加以下代码：

```python
import sys
import io

# 修复 Windows 控制台中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from WindPy import w
w.start()

# 现在中文显示正常
err, df = w.wss('600519.SH', 'sec_name,close', '', usedf=True)
print(df)  # 显示: 贵州茅台 而不是 ����ę́

w.stop()
```

## 故障排除

| 问题 | 平台 | 解决方案 |
|------|------|----------|
| 常驻服务返回 502 | Windows | 改用直连模式 |
| 连接被重置 | Windows | 改用直连模式 |
| 中文乱码 | Windows | 正常现象，数据获取正常，仅显示问题 |
| `ModuleNotFoundError: No module named 'WindPy'` | 全平台 | 确保已安装 Wind 金融终端并配置 Python API |
| 登录窗口频繁弹出 | macOS/Linux | 使用常驻服务模式 |

## 脚本

- `scripts/wind_server.py` — Wind 常驻 HTTP 服务 (端口 18888，自动重连，17 个端点)
- `scripts/wind_client.py` — 客户端库，提供全部 17 个函数，返回 DataFrame/list/str
