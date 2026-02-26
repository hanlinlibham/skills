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

### 常驻服务模式（推荐，macOS/Windows/Linux 通用）

避免每次调用弹出 Wind 登录窗口，适合自动化与批量查询。

```bash
# macOS / Linux
python scripts/wind_server.py &

# Windows (CMD)
start /B python scripts\wind_server.py

# Windows (PowerShell)
Start-Process python -ArgumentList "scripts\wind_server.py" -WindowStyle Hidden

# 健康检查
curl http://localhost:18888/health

# 停止（跨平台，通过 HTTP）
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

### 直连模式（交互式或短任务）

不需要常驻服务，直接调用 WindPy。每次 `w.start()` 可能弹出 Wind 登录窗口。

```python
from WindPy import w
w.start()
err, df = w.wsd("000300.SH", "close", "-30D", "", "", usedf=True)
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

## 脚本

- `scripts/wind_server.py` — Wind 常驻 HTTP 服务 (端口 18888，自动重连，17 个端点)
- `scripts/wind_client.py` — 客户端库，提供全部 17 个函数，返回 DataFrame/list/str
