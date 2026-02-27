---
name: windpy-sdk
description: >
  Wind 金融终端 Python API 调用技能。当用户需要通过 WindPy 获取 A 股、债券、基金、
  期货、宏观数据，或查询 Wind 字段、板块代码、SectorID 时触发。
  关键词: Wind, WindPy, w.wsd, w.wss, w.wset, w.wsq, w.edb, 万得
allowed-tools: Bash(python*), Bash(curl*), Read, Grep, Glob
---

# WindPy SDK

## 快速开始（直接复制使用）

**重要**: 每次调用都必须包含下面的路径设置代码块，写在脚本最前面：

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".claude/skills/windpy-sdk/scripts") if os.path.exists(".claude") else os.path.expanduser("~/.claude/skills/windpy-sdk/scripts"))
from wind_client import wsd, wss, wset, wsq, edb, wsi, tdays, tdaysoffset
```

如果上面的自动路径找不到，直接用绝对路径：
```python
import sys; sys.path.insert(0, "/Users/jameslee/Space/skill_repo/.claude/skills/windpy-sdk/scripts")
from wind_client import wsd, wss, wset, wsq, edb, wsi, tdays, tdaysoffset
```

**首次调用约 10 秒**（WindPy 建立连接），后续查询毫秒级，不要因为慢就中断。请设置 `timeout=60000`。

## 函数选择指南（先看这里）

| 我想要... | 用这个函数 | 示例 |
|-----------|-----------|------|
| 一只股票的历史价格走势 | `wsd` | `wsd("600519.SH", "close,pct_chg", "-30D")` |
| 多只股票的今日快照对比 | `wss` | `wss("600519.SH,000858.SZ", "close,pe_ttm", "tradeDate=20260226")` |
| 指数/板块的全部成分股 | `wset` | `wset("sectorconstituent", "date=20260226;windcode=000300.SH")` |
| 实时行情（盘中） | `wsq` | `wsq("600519.SH", "rt_last,rt_pct_chg")` |
| GDP/CPI 等宏观数据 | `edb` | `edb("M0000612", "2024-01-01", "2025-12-31")` |
| 分钟K线 | `wsi` | `wsi("600519.SH", "close,volume", "2026-02-26 09:30:00", "2026-02-26 15:00:00", "BarSize=5")` |
| 交易日列表 | `tdays` | `tdays("20260101", "20260227")` |

### 常见陷阱

- **wss 查 PE/PB 必须带日期**：`wss(..., "pe_ttm", "tradeDate=20260226")`，不带日期会返回 None
- **wsd 不支持多代码×多字段**：`wsd("A,B", "close,volume")` 会报错，改为 `wsd("A,B", "close")` 或 `wsd("A", "close,volume")`
- **wsi 不支持相对日期**：`wsi(..., "-1D 09:30:00")` 会报错，必须用绝对时间 `"2026-02-26 09:30:00"`
- **所有函数返回 pandas DataFrame**（tdays 返回 list，tdaysoffset 返回 str）

## 连接方式

### macOS — 直连模式

客户端直接调用 WindPy，首次调用自动连接。自动检测 `isAutoLogin` 配置，确保免弹窗。

**前提**：Wind API.app 已安装并运行，已勾选「自动登录」。
环境配置问题可运行：`python scripts/setup_windpy.py --fix`

### Windows — 命名管道服务（推荐）

使用命名管道实现连接共享，避免每次登录和抢占桌面 Wind。

```bash
# 终端1: 启动服务（保持运行）
python scripts/wind_server_win.py

# 终端2/3/4...: 使用客户端查询
python -c "from scripts.wind_client_win import wsd; print(wsd('000300.SH', 'close', '-5D'))"
```

**注意**: 需要安装 `pywin32`: `pip install pywin32 pandas`

### Windows — 直连模式（简单场景）

直接调用 WindPy，无需启动常驻服务。每次 `w.start()` 可能弹出 Wind 登录窗口。

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

## 故障排除

| 问题 | 平台 | 解决方案 |
|------|------|----------|
| 首次调用慢 (~10s) | macOS | 正常，`w.start()` 仅在首次调用时触发 |
| 登录窗口弹出 | macOS | 在 Wind 终端设置中勾选「自动登录」 |
| `ModuleNotFoundError: No module named 'WindPy'` | macOS | 运行 `python scripts/setup_windpy.py --fix`（自动创建 symlink） |
| `ModuleNotFoundError: No module named 'WindPy'` | Windows | 运行 `python scripts/setup_windpy.py --fix`（自动创建 .pth 文件） |
| 中文乱码 | Windows | 正常现象，数据获取正常，仅显示问题 |

## 脚本

- `scripts/wind_client.py` — 客户端库（macOS 直连 WindPy），提供全部 17 个函数，返回 DataFrame/list/str
- `scripts/wind_client_win.py` — Windows 客户端（通过命名管道连接 wind_server_win.py）
- `scripts/wind_server_win.py` — Windows 命名管道常驻服务
- `scripts/setup_windpy.py` — WindPy 环境自动检测与配置（macOS: symlink / Windows: .pth + 注册表检测）
