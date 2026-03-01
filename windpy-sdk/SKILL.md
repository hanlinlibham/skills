---
name: windpy-sdk
description: >
  Wind 金融终端 Python API 调用技能。当用户需要通过 WindPy 获取 A 股、债券、基金、
  期货、宏观数据，或查询 Wind 字段、板块代码、SectorID 时触发。
  关键词: Wind, WindPy, w.wsd, w.wss, w.wset, w.wsq, w.edb, 万得
allowed-tools: Bash(python*) Bash(curl*) Read Grep Glob
---

# WindPy SDK

## 执行规则（必须遵守）

1. **Bash timeout 必须设为 60000** — 首次调用需 ~10 秒建立 Wind 连接，默认 timeout 会导致超时中断
2. **每个 Python 脚本开头必须包含下方的路径定位代码块** — 否则 `import wind_client` 会失败
3. **不要因为首次调用慢就中断或重试** — 首次慢是正常的，后续查询毫秒级

## 快速开始

每次编写 Python 脚本时，**必须**在最前面放这段路径定位代码：

```python
import sys, os

# 自动定位 windpy-sdk scripts 目录（勿修改）
for _d in [os.getcwd(), os.path.expanduser("~")]:
    _s = os.path.join(_d, ".claude", "skills", "windpy-sdk", "scripts")
    if os.path.isdir(_s):
        sys.path.insert(0, _s)
        break

from wind_client import wsd, wss, wset, wsq, edb, wsi, tdays, tdaysoffset
```

如果上述代码报 `ModuleNotFoundError: No module named 'wind_client'`，说明 skill 安装路径不在预期位置。用 Glob 工具搜索 `**/windpy-sdk/scripts/wind_client.py` 获取实际路径，然后：

```python
import sys
sys.path.insert(0, "<Glob 找到的 scripts 目录绝对路径>")
from wind_client import wsd, wss, wset, wsq, edb, wsi, tdays, tdaysoffset
```

完整示例：

```python
import sys, os

for _d in [os.getcwd(), os.path.expanduser("~")]:
    _s = os.path.join(_d, ".claude", "skills", "windpy-sdk", "scripts")
    if os.path.isdir(_s):
        sys.path.insert(0, _s)
        break

from wind_client import wsd

df = wsd("000300.SH", "close,pct_chg", "-30D")
print(df)
```

用 Bash 工具执行时设置 `timeout=60000`。

## 禁止事项（常见错误）

- **禁止 wsd 同时多代码×多字段** — `wsd("A,B", "close,volume")` 数据会丢失。只能 `wsd("A,B", "close")` 或 `wsd("A", "close,volume")`
- **禁止 wss 查估值字段不带日期** — `wss(..., "pe_ttm")` 返回 None。必须 `wss(..., "pe_ttm", "tradeDate=20260228")`
- **禁止 wsi 用相对日期** — `wsi(..., "-1D 09:30:00")` 报错。必须用绝对时间 `"2026-02-28 09:30:00"`
- **禁止 Bash timeout 使用默认值** — 必须设 `timeout=60000`

## 函数选择指南

| 我想要... | 用这个函数 | 示例 |
|-----------|-----------|------|
| 一只股票的历史价格走势 | `wsd` | `wsd("600519.SH", "close,pct_chg", "-30D")` |
| 多只股票的今日快照对比 | `wss` | `wss("600519.SH,000858.SZ", "close,pe_ttm", "tradeDate=20260228")` |
| 指数/板块的全部成分股 | `wset` | `wset("sectorconstituent", "date=20260228;windcode=000300.SH")` |
| 实时行情（盘中） | `wsq` | `wsq("600519.SH", "rt_last,rt_pct_chg")` |
| GDP/CPI 等宏观数据 | `edb` | `edb("M0000612", "2024-01-01", "2025-12-31")` |
| 分钟K线 | `wsi` | `wsi("600519.SH", "close,volume", "2026-02-28 09:30:00", "2026-02-28 15:00:00", "BarSize=5")` |
| 交易日列表 | `tdays` | `tdays("20260101", "20260228")` |
| 交易日偏移（前N个交易日） | `tdaysoffset` | `tdaysoffset(-5)` → 返回日期字符串 |

## 函数签名速查

### 核心函数

| 函数 | 签名 | 返回类型 |
|------|------|----------|
| `wsd` | `wsd(codes, fields, beginTime, endTime="", options="")` | DataFrame |
| `wss` | `wss(codes, fields, options="")` | DataFrame |
| `wset` | `wset(tableName, options="")` | DataFrame |
| `wsq` | `wsq(codes, fields, options="")` | DataFrame |
| `edb` | `edb(codes, beginTime="", endTime="", options="")` | DataFrame |
| `wsi` | `wsi(codes, fields, beginTime, endTime, options="")` | DataFrame |

### 交易日工具

| 函数 | 签名 | 返回类型 |
|------|------|----------|
| `tdays` | `tdays(beginTime, endTime, options="")` | list[str] |
| `tdaysoffset` | `tdaysoffset(offset, beginTime="", options="")` | str |
| `tdayscount` | `tdayscount(beginTime, endTime, options="")` | int |

### 板块与辅助函数

| 函数 | 签名 | 返回类型 |
|------|------|----------|
| `wsee` | `wsee(codes, fields, options="")` | DataFrame |
| `wses` | `wses(codes, fields, beginTime, endTime, options="")` | DataFrame |
| `wsed` | `wsed(codes, fields, options="")` | DataFrame |
| `weqs` | `weqs(filtername, options="")` | DataFrame |
| `htocode` | `htocode(codes, sec_type, options="")` | DataFrame |

## 常用代码与字段速查

| 类别 | 示例 |
|------|------|
| 指数 | `000300.SH`(沪深300) `000905.SH`(中证500) `399006.SZ`(创业板指) |
| 行情字段 | `open, high, low, close, volume, amt, pct_chg` |
| 估值字段 | `pe_ttm, pb_lf, mkt_cap_ard`（wss 必须带 tradeDate） |
| 资金字段 | `mfd_inflow_xl, mfd_inflow_l, mfd_inflow_m, mfd_inflow_s` |
| 板块ID | `a001010100000000`(全A) `a39901011i000000`(申万三级) |
| 中债指数 | `CBA00101.CS`(新综合财富) `CBA00601.CS`(国债总财富) |
| 期货主力 | `IF00.CFE`(沪深300) `AU00.SHF`(黄金) `CU00.SHF`(沪铜) |
| 外汇 | `USDCNY.FX`(在岸) `USDCNH.FX`(离岸) `EURUSD.FX` |
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

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `ModuleNotFoundError: No module named 'wind_client'` | scripts 目录不在 sys.path | 用 Glob 搜索 `**/windpy-sdk/scripts/wind_client.py` 获取实际路径 |
| `ModuleNotFoundError: No module named 'WindPy'` | WindPy 未安装或未链接 | 运行 `python <scripts目录>/setup_windpy.py --fix` |
| `RuntimeError: Wind 连接失败` | Wind 终端未运行 | 启动 Wind API.app (macOS) 或 Wind 金融终端 (Windows) |
| 脚本执行超时 | Bash timeout 太短 | 设置 `timeout=60000` |
| wss 返回 None | 估值字段缺少日期参数 | 添加 `tradeDate=YYYYMMDD` 到 options |
| wsd 数据不完整 | 多代码×多字段同时查询 | 拆分为单字段多代码或多字段单代码 |

## 平台说明

- **macOS**: `wind_client.py` 直连 WindPy，首次调用自动 `w.start()`。前提: Wind API.app 已运行并开启自动登录
- **Windows**: 推荐使用 `wind_server_win.py`（常驻服务）+ `wind_client_win.py`（客户端），避免每次弹出登录窗口。需安装 `pywin32`
- **环境检测**: 运行 `python <scripts目录>/setup_windpy.py --fix --verify` 可自动诊断和修复
