# Skills

Claude Code 技能集 — 金融数据、文档处理、数据可视化、多代理协作。

## 目录

### 金融与研究

| 技能 | 说明 |
|------|------|
| [windpy-sdk](windpy-sdk/) | Wind 金融终端 Python API — 17 个函数、常驻服务、13 份参考文档，覆盖 A 股/债券/基金/期货/期权/外汇/宏观 |
| [asset-monitor](asset-monitor/) | 资产异常波动日频监控 — Z-Score 检测偏离 > 2σ 的异常资产，自动生成 Excel 报告 |
| [technical-analyst](technical-analyst/) | K 线图技术分析 — 趋势识别、支撑阻力位、形态分析、概率场景推演 |
| [portfolio-analyzer](portfolio-analyzer/) | 投资组合多维分析 — 多组合 vs 基准对比、8 项风险指标、Brinson 三因素行业归因、6-sheet Excel 报告 |

### 文档与可视化

| 技能 | 说明 |
|------|------|
| [pptx](pptx/) | PowerPoint 创建/编辑/分析 — 布局、母版、图表、演讲备注，含 OOXML schema |
| [docx](docx/) | Word 文档创建/编辑 — 修订追踪、批注、格式保留、文本提取 |
| [xlsx](xlsx/) | Excel 电子表格 — 公式、格式、数据分析、可视化、公式重算 |
| [pdf](pdf/) | PDF 处理工具包 — 文本/表格提取、创建、合并/拆分、表单填写 |
| [plotly](plotly/) | Plotly 交互式可视化 — 散点图/折线图/热力图/3D/地图/金融图表，输出 HTML 或静态图片 |

### 写作与工具

| 技能 | 说明 |
|------|------|
| [humanizer](humanizer/) | AI 文本去机器痕迹 — 基于 Wikipedia 标准，修复夸张修辞、破折号滥用、AI 典型词汇等 30+ 种模式 |
| [skill-creator](skill-creator/) | 技能创建指南 — 帮助创建和优化 Claude Code skill |
| [find-skills](find-skills/) | 技能发现与安装 — 从开源技能生态中搜索和安装 skill |

### 基础设施

| 技能 | 说明 |
|------|------|
| [openclaw-adj-skill](openclaw-adj-skill/) | OpenClaw 多代理配置 — 4 个专用代理（闪电/工作/研究/编程）协作部署 |
| [claude-driver](claude-driver/) | Claude CLI 驱动器 — 通过 `claude -p` 驱动内层 Claude Code 执行编码任务，含宪法约束、3 套 Playbook、工件规范 |

## 使用方式

将技能目录放入项目的 `.claude/skills/` 下，Claude Code 自动识别加载。

```bash
# 克隆整个仓库
git clone https://github.com/hanlinlibham/skills .claude/skills

# 或只安装单个技能
cp -r windpy-sdk <your-project>/.claude/skills/windpy-sdk
```

## 依赖关系

```
asset-monitor ─────uses──→ WindPy SDK ──ref──→ windpy-sdk skill
portfolio-analyzer ─uses──→ WindPy SDK ──ref──→ windpy-sdk skill
                   └─uses──→ xlsx skill (recalc.py 公式验证)
其余 skill 均独立，无交叉依赖
```
