# Skills

useful-skills，including wind terminal（万德）

## 目录

| 技能 | 说明 |
|------|------|
| [windpy-sdk](windpy-sdk/) | WindPy SDK 本地调用参考手册 — Wind 金融终端 Python API 函数、字段、板块代码速查 |
| [asset-monitor](asset-monitor/) | 资产异常波动日频监控 — 检测偏离历史均值超过2倍标准差的异常资产，生成报告 |
| [openclaw-adj-skill](openclaw-adj-skill/) | OpenClaw 多代理配置 — 配置 4 个专用代理（闪电、工作、研究、编程）的多代理部署 |

## 项目统计

- **语言构成**: Shell (66.1%) + Python (33.9%)
- **技能数量**: 3 个
- **代理支持**: 4 个专用代理的多代理协作

## 使用方式

将技能目录复制到 `~/.claude/skills/` 下，Claude Code 会自动识别并加载。

```bash
# 示例：安装 windpy-sdk 技能
cp -r windpy-sdk ~/.claude/skills/windpy-sdk

# 示例：安装 asset-monitor 技能
cp -r asset-monitor ~/.claude/skills/asset-monitor

# 示例：安装 openclaw-adj-skill 技能
cp -r openclaw-adj-skill ~/.claude/skills/openclaw-adj-skill
```

## 技能说明

### windpy-sdk

WindPy SDK 参考手册，提供：
- WindPy 核心函数用法（wsd/wss/wset/wsq 等）
- 常用字段速查（行情、财务、资金流向、估值）
- 板块 SectorID 列表（申万行业、指数、概念）
- 错误码对照表
- EDB 宏观经济指标代码

### asset-monitor

资产异常波动监控系统，功能包括：
- 监控 298 个资产（申万三级259个 + A股指数9个 + 债券5个 + ETF8个 + 商品8个 + 全球指数9个）
- Z-Score 异常检测（偏离历史均值 > 2倍标准差）
- 自动生成 Excel 报告
- 支持定时任务运行

### openclaw-adj-skill

OpenClaw 多代理配置系统，支持：
- 4 个专用代理协作（Shandian 主代理 + Work/Research/Coding 专用代理）
- 代理间通信和权限管理
- 沙箱配置和工作空间管理
- 远程客户端配置和连接

## 依赖关系

```
asset-monitor (监控业务逻辑)
    ↓ 直接使用 WindPy 获取数据
WindPy SDK (Wind 金融终端 API)
    ↓ 字段/代码查询参考
windpy-sdk skill (参考文档)

openclaw-adj-skill (多代理编排)
    ↓ 独立配置系统
    与其他 skill 无直接依赖
```