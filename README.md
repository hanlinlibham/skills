# Skills

Claude Code 技能集 — 金融数据、资产监控、多代理协作。

## 目录

| 技能 | 说明 |
|------|------|
| [windpy-sdk](windpy-sdk/) | Wind 金融终端 Python API — 17 个函数、常驻服务模式、13 份参考文档，覆盖 A 股/债券/基金/期货/期权/外汇/宏观 |
| [asset-monitor](asset-monitor/) | 资产异常波动日频监控 — Z-Score 检测偏离 > 2σ 的异常资产，自动生成 Excel 报告 |
| [openclaw-adj-skill](openclaw-adj-skill/) | OpenClaw 多代理配置 — 4 个专用代理（闪电/工作/研究/编程）协作部署 |

## 使用方式

将技能目录放入项目的 `.claude/skills/` 下，Claude Code 自动识别加载。

```bash
# 克隆整个仓库
git clone https://github.com/hanlinlibham/skills .claude/skills

# 或只安装单个技能
cp -r windpy-sdk <your-project>/.claude/skills/windpy-sdk
```

## 技能详情

### windpy-sdk

Wind 金融终端 Python API 完整调用技能。

**架构：** HTTP 常驻服务 (`wind_server.py`) + 客户端库 (`wind_client.py`)，避免每次调用弹出 Wind 登录窗口。macOS / Windows / Linux 通用。

**17 个 API 函数：**
- 核心数据：`wsd` `wss` `wset` `wsq` `edb` `wsi` `wst`
- 板块：`wsee` `wses` `wsed`
- 交易日：`tdays` `tdaysoffset` `tdayscount`
- 辅助：`weqs` `htocode` `wai` `wgel`

**13 份参考文档（3,300+ 行）：**

| 文档 | 内容 |
|------|------|
| field-catalog | 行情/财务/资金/估值字段 |
| sectorid-catalog | 板块 SectorID 完整目录 |
| wset-tables | wset 报表数据集 |
| error-codes | 错误码及解决方案 |
| bond-fields | 债券字段 + 中债指数 CBA*.CS |
| fund-fields | 基金字段 + 区间收益率 |
| future-fields | 期货字段 + 30+ 品种速查 |
| options-fields | ETF 期权合约 + Greeks |
| fx-fields | 15 个外汇货币对 |
| edb-indicators | 宏观指标 + 大宗商品 EDB |
| technical-indicators | MACD/RSI/KDJ/BOLL |
| options-cheatsheet | 函数 options 参数速查 |
| asset-type-codes | 资产类型代码 |

### asset-monitor

资产异常波动监控系统：
- 监控 298 个资产（申万三级 259 + A 股指数 9 + 债券 5 + ETF 8 + 商品 8 + 全球指数 9）
- Z-Score 异常检测（偏离历史均值 > 2σ）
- 自动生成 Excel 报告，支持定时任务

### openclaw-adj-skill

OpenClaw 多代理配置系统：
- 4 代理协作（Shandian 主代理 + Work/Research/Coding）
- 代理间通信和权限管理
- 沙箱配置和工作空间管理

## 依赖关系

```
asset-monitor ──uses──→ WindPy SDK ──ref──→ windpy-sdk skill
openclaw-adj-skill                          (独立，无依赖)
```