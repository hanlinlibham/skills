# WindPy SDK 本地调用参考手册

Wind 金融终端 Python API (`from WindPy import w`) 的 Claude Code 技能，覆盖全部数据函数的签名、参数、返回值和示例。

## 覆盖函数

| 函数 | 用途 |
|------|------|
| `w.wsd()` | 日级时间序列（K线、资金流向等） |
| `w.wss()` | 截面快照（财务指标、估值等） |
| `w.wsq()` | 实时行情（快照 / 订阅模式） |
| `w.wsi()` | 分钟级 K 线（1-60分钟） |
| `w.wst()` | Tick 逐笔数据 |
| `w.wses()` | 板块日级时间序列 |
| `w.wsee()` | 板块截面快照 |
| `w.wset()` | 报表数据集（成分股、龙虎榜等） |
| `w.edb()` | 宏观经济数据库（GDP、CPI、PMI等） |
| `w.tdays()` / `w.tdaysoffset()` / `w.tdayscount()` | 交易日历 |

## 文件结构

```
windsdk/
├── SKILL.md                         # 主技能文件（函数用法 + 示例）
├── README.md                        # 本文件
└── references/
    ├── README.md                    # 参考文档总览与补充指南
    ├── field-catalog.md             # 字段名速查
    ├── edb-indicators.md            # EDB 宏观指标代码
    ├── wset-tables.md               # wset 报表参数参考
    ├── sector-ids.md                # 板块 sectorid 对照表
    ├── asset-type-codes.md          # 资产类型代码规则
    ├── error-codes.md               # 错误码对照表
    └── options-cheatsheet.md        # options 参数速查
```

## 安装

```bash
cp -r windsdk ~/.claude/skills/windsdk
```

## 前置条件

- Wind 金融终端已安装并启动
- WindPy SDK 已安装（`pip install WindPy` 或终端自带）
- 有效的 Wind 数据账户
