---
name: annuity-disclosure-crawler
description: 全量爬取中国企业年金基金投资管理人在其官网发布的《企业年金基金投资管理情况》季度管理报告。内置人社部许可的22家投资管理人名录+每家官网披露栏目入口、抓取策略与站点反爬坑位；驱动脚本按季全量下载并做真伪校验与清单记录。当需要采集/批量下载企业年金(或职业年金)季度管理报告/信息披露、定位某投资管理人官网披露页、更新报告库、或做年金管理人季报数据集时使用。触发词：企业年金、投资管理人、季度报告、季报、信息披露、管理情况、年金爬取、全量爬取、年金披露、pension disclosure crawl。
---

# 企业年金投资管理人季报全量爬取

## 这个技能做什么

把人社部许可的 **22 家企业年金基金投资管理人**在各自官网公开发布的
《企业年金基金投资管理情况》**季度报告**，按季**全量**抓取到本地，做真伪校验并生成清单。
名录、每家披露栏目 URL、抓取策略、站点反爬坑位都已固化在 `references/registry.json`，
两个脚本读它干活，无需每次重新摸索。

核心事实（先读懂再动手）：

- **口径**：抓的是投资管理人**自披露**的《企业年金基金投资管理情况》季度信息披露表。它 ≠ 受托人向委托人/人社部报送的完整《企业年金基金管理情况季度报告》全文（后者按规定不公开）。检索时排在前面的“集合型企业年金计划管理情况信息披露表”常是**受托人口径**（如工商银行、各托管行），别混进投资管理人季报。
- **不是每家都公开**：约 19 家官网公开可下；博时、招商的季报仅登录客户门户可见；建信养老金官网只发“养老金产品”层报告且被 WAF+加密挡住。详见 registry 里各家 `access`。
- **报告形态三种**：PDF（多数）、**DOCX**（泰康资产，链接无扩展名）、**HTML 网页正文**（海富通/南方/长江/中信证券/人保，无 PDF 附件，存网页）。
- **数据坑**：人保养老(picc)官网自 2022Q1 起正文区为空，只登记标题+日期，近四年数据未公开。

## 两层抓取工作流

先用纯 HTTP（快、无依赖），搞不定的再上无头浏览器。

### 第 1 步：看名录与策略

```bash
python3 scripts/crawl.py --list
```

列出 22 家的 slug / 简称 / access(public|waf|login) / strategy / 披露入口。

### 第 2 步：HTTP 全量抓取（默认路径）

```bash
# 全量抓所有可 HTTP 抓取的机构（跳过 waf/login，会明确提示哪几家要换 headless）
python3 scripts/crawl.py --out annuity_reports

# 只抓某几家；--latest N 只留最新 N 期(0=全量，默认全量)
python3 scripts/crawl.py --only m04,m09,m17 --latest 4 --out annuity_reports
```

`strategy` 含义（脚本自动按此处理，一般无需关心）：
`pdf_index` 列表页直给 PDF 直链 · `detail_index` 列表→详情页→再取文件 ·
`html_index` 报告本身是 HTML 网页（存网页）· `spa_api` 列表走后端 JSON ·
`headless` 需浏览器（脚本会跳过并提示）· `login_blocked` 非公开（跳过并说明）。

脚本已内置的通用能力：列表翻页（首页 index.html + index_1/2… 自动补全）、
GBK/UTF-8 自适应解码、pdfjs `viewer.html?file=` 包装解包、相对链接补全、
期次识别（`2026Q1`/`2026年1季度`/中文数字季度）、真伪校验（PDF 看 `%PDF` 魔数、
DOCX 看 `PK`、HTML 看大小+关键字）、内容 MD5 去重、同期两类报告防覆盖。

### 第 3 步：无头浏览器兜底（WAF/SPA 机构）

当第 2 步对某家提示“0 命中：请改用 crawl_headless.py”，或该家 `access=waf`/`strategy=headless`：

```bash
pip install playwright --break-system-packages && python3 -m playwright install chromium

# 默认抓所有需浏览器的机构；也可 --only 指定；--headful 显示窗口调试
python3 scripts/crawl_headless.py --only m15,m21 --latest 4 --out annuity_reports
```

真实 Chromium 会自动过瑞数(botgate 412)、加速乐(jsl 521)等 JS 挑战，
渲染出 SPA 列表后用带 Cookie 的浏览器上下文下载（含跨域文件站）。复用 crawl.py 的
识别/校验/命名逻辑，落地到**同一** `--out` 目录，另出 `manifest_headless.*`。

典型需 headless 的：富国/工银瑞信/嘉实/易方达(SPA 列表)、平安养老/华泰资产(动态列表)、
银华/太平养老/中金(反爬 WAF)。

## 输出结构与清单

```
annuity_reports/
├── m04/  m04_2026Q1.pdf  m04_2025Q4.pdf ...  _disclosure_page.html
├── m13/  m13_2026Q1.docx ...
├── m22/  m22_2026Q1.html ...
├── manifest.csv / manifest.json            # crawl.py 清单：机构·期次·状态·字节·本地路径·源URL
└── manifest_headless.csv / .json           # crawl_headless.py 清单
```

`status` 取值：`ok`（校验通过）/ `not-pdf`/`not-docx`/`suspect`（存为 `*.suspect` 待查）/ `download-fail:*`。
交付前用 manifest 核对每家是否抓全、有无 suspect。

## 全量 vs 增量

- **全量**：不加 `--latest`（默认 0），脚本翻完列表所有分页，抓每家全部历史季度。
  首轮建议单跑几家验证：`--only m04,m17,m13`，确认无误再整体跑。
- **增量**：定期只补新季度用 `--latest 2`，MD5 去重会跳过已存在的同内容文件（但会重新下载比对，
  真正省流可结合已存在文件名跳过）。季度披露节奏：一般次季度中下旬发布（如 Q1 报告约 6 月中下旬）。

## 排障速查

- **HTTP 0 命中** → 列表 JS 渲染或被 WAF 挡：改 `crawl_headless.py`。
- **headless 仍 0 命中** → 可能需登录、或报告藏在需点击的折叠/下一页里：加 `--headful` 肉眼看，
  必要时在 registry 该家 `list_url` 填精确分页模板或改 `strategy`。
- **拿到的 PDF 打不开/很小** → 多半是 WAF 降级的 HTML 错误页；脚本已标 `suspect`。换 headless。
- **404 一堆中文名 .pdf** → 详情页里的“显示用文件名”被误当链接；已在 `files_in_page` 收敛，若仍有属噪声可忽略（不影响真链）。
- **工银瑞信**：官网迁 icbccs→icbcubs 成 SPA，直链多 404；可靠源是 Wayback 快照
  `https://web.archive.org/web/{ts}id_/{原PDF直链}`（快照止于 2024Q2）。
- **name 冲突** `rtk gain` 无关；与本技能无关的报错先 `--list` 自检 registry 是否可读。

## 维护 registry（增删改机构或修坑）

`references/registry.json` 是唯一事实源，字段语义见其 `meta.field_notes`。常见维护：

- 名单变动：以**人社部社保基金监管司**最新《企业年金基金管理机构名单》为准，增删 `managers` 条目。
- 某家官网改版：更新其 `disclosure_url` / `list_url`(分页模板，`{n}` 为页码) / `file_url_pattern`(报告文件或报告页 URL 正则) / `strategy`。
- 加新机构：复制一条，填 `slug`(mNN)、`short`、`name`、`category`、`access`、`strategy`、`item_type`、入口与正则，先 `--only 新slug --latest 2` 验证。

registry 里每家的 `notes` 记录了该站的真实坑位（编码、反爬类型、命名规律、口径提醒），改站点前先读。
