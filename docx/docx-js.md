# DOCX Library Tutorial

Generate .docx files with JavaScript/TypeScript.

**Important: Read this entire document before starting.** Critical formatting rules and common pitfalls are covered throughout - skipping sections may result in corrupted files or rendering issues.

## Setup
Assumes docx is already installed globally
If not installed: `npm install -g docx`

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Media, 
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink, 
        InternalHyperlink, TableOfContents, HeadingLevel, BorderStyle, WidthType, TabStopType, 
        TabStopPosition, UnderlineType, ShadingType, VerticalAlign, SymbolRun, PageNumber,
        FootnoteReferenceRun, Footnote, PageBreak } = require('docx');

// Create & Save
const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer)); // Node.js
Packer.toBlob(doc).then(blob => { /* download logic */ }); // Browser
```

## Text & Formatting
```javascript
// IMPORTANT: Never use \n for line breaks - always use separate Paragraph elements
// ❌ WRONG: new TextRun("Line 1\nLine 2")
// ✅ CORRECT: new Paragraph({ children: [new TextRun("Line 1")] }), new Paragraph({ children: [new TextRun("Line 2")] })

// Basic text with all formatting options (公文配置：仿宋 14pt 默认)
new Paragraph({
  alignment: AlignmentType.JUSTIFIED, // 公文两端对齐
  spacing: { before: 200, after: 200 },
  indent: { firstLine: 560 }, // 公文首行缩进 2em
  children: [
    new TextRun({ text: "加粗", bold: true }),
    new TextRun({ text: "斜体", italics: true }),
    new TextRun({ text: "下划线", underline: { type: UnderlineType.SINGLE, color: "000000" } }), // 公文用黑色
    new TextRun({ text: "指定字号", size: 28, font: "STFangsong" }), // 仿宋 14pt
    new TextRun({ text: "高亮", highlight: "yellow" }),
    new TextRun({ text: "删除线", strike: true }),
    new TextRun({ text: "x2", superScript: true }),
    new TextRun({ text: "H2O", subScript: true }),
    new SymbolRun({ char: "2022", font: "Symbol" }), // Bullet •
    new SymbolRun({ char: "00A9", font: "STFangsong" }) // Copyright ©
  ]
})
```

## Styles — AbleMind 公文 UI 设计系统

### 字体体系

| 变量 | 字体栈 | 用途 |
|------|--------|------|
| `--gov-font-body` | STFangsong → FangSong → Fangsong SC → Noto Serif SC → serif | 正文（仿宋体） |
| `--gov-font-heading` | Heiti SC → PingFang SC → SimHei → Noto Sans SC → sans-serif | 标题（黑体） |
| `--gov-font-mono` | IBM Plex Mono → JetBrains Mono → monospace | UI 等宽 |
| `--gov-font-code` | Courier New → monospace | 代码块 |

在 docx-js 中使用时，font 值按优先级取第一个系统可用字体即可（macOS 优先 STFangsong / Heiti SC）。

### 公文排版规范

| 元素 | 字体 | 字号 | 其他 |
|------|------|------|------|
| 正文 | 仿宋 (STFangsong) | 14pt (size: 28) | 行距 1.5，首行缩进 2em，两端对齐 |
| h1 | 黑体 (Heiti SC) | 16pt (size: 32) | 居中，加粗 |
| h2 | 黑体 (Heiti SC) | 15pt (size: 30) | 左对齐，加粗 |
| h3–h6 | 黑体 (Heiti SC) | 14pt (size: 28) | 左对齐，加粗 |
| 表格 | 仿宋 (STFangsong) | 小四 12pt (size: 24) | 全线框，表头灰底 |
| 代码 | Courier New | 12pt (size: 24) | 灰底框线 |
| 链接 | 同正文 | 同正文 | 黑色下划线（公文不用彩色链接） |

### 标准公文样式模板

```javascript
// AbleMind 公文配置 — 默认样式
const GOV_FONT_BODY = "STFangsong";     // 仿宋体（正文）
const GOV_FONT_HEADING = "Heiti SC";     // 黑体（标题）
const GOV_FONT_CODE = "Courier New";     // 代码块

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: GOV_FONT_BODY, size: 28 }, // 仿宋 14pt
        paragraph: {
          spacing: { line: 360 },               // 行距 1.5 (240 * 1.5)
          alignment: AlignmentType.JUSTIFIED     // 两端对齐
        }
      }
    },
    paragraphStyles: [
      // 公文标题 — 黑体 16pt 居中
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 32, bold: true, color: "000000", font: GOV_FONT_HEADING },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      // h1 — 黑体 16pt 居中
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: GOV_FONT_HEADING },
        paragraph: { spacing: { before: 240, after: 240, line: 360 }, alignment: AlignmentType.CENTER, outlineLevel: 0 } },
      // h2 — 黑体 15pt 左对齐
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, color: "000000", font: GOV_FONT_HEADING },
        paragraph: { spacing: { before: 180, after: 180, line: 360 }, outlineLevel: 1 } },
      // h3–h6 — 黑体 14pt 左对齐
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: GOV_FONT_HEADING },
        paragraph: { spacing: { before: 120, after: 120, line: 360 }, outlineLevel: 2 } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: GOV_FONT_HEADING },
        paragraph: { spacing: { before: 120, after: 120, line: 360 }, outlineLevel: 3 } },
      // 自定义样式仍可添加
      { id: "govNote", name: "Gov Note", basedOn: "Normal",
        run: { size: 24, color: "333333", font: GOV_FONT_BODY },
        paragraph: { spacing: { after: 60 } } }
    ],
    characterStyles: [
      // 公文链接：黑色下划线，不用彩色
      { id: "Hyperlink", name: "Hyperlink",
        run: { color: "000000", underline: { type: UnderlineType.SINGLE, color: "000000" } } },
      { id: "govEmphasis", name: "Gov Emphasis",
        run: { bold: true, font: GOV_FONT_HEADING } }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // A4 标准页边距 1 英寸
        size: { width: 11906, height: 16838 } // A4 尺寸 (210mm × 297mm in DXA)
      }
    },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("公文标题")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("一级标题")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("二级标题")] }),
      // 正文段落 — 首行缩进 2em（仿宋14pt ≈ 560 DXA）
      new Paragraph({
        indent: { firstLine: 560 },
        children: [new TextRun("正文内容，仿宋14pt，行距1.5，首行缩进2em，两端对齐。")]
      })
    ]
  }]
});
```

### 公文首行缩进说明
- 首行缩进 2em = 2 × 字号对应的 DXA 值
- 仿宋 14pt → `firstLine: 560` (14pt × 20 DXA/pt × 2)
- 小四 12pt → `firstLine: 480` (12pt × 20 DXA/pt × 2)
- 通过 `indent: { firstLine: 560 }` 设置在每个正文 Paragraph 上

### 跨平台字体回退
- **macOS**: STFangsong / Heiti SC（系统自带）
- **Windows**: FangSong / SimHei（系统自带）
- **Linux/CI**: Noto Serif SC / Noto Sans SC（需安装 Google Noto CJK）
- docx-js 的 `font` 属性只写一个字体名，Word 打开时自动使用系统可用字体

**Key Styling Principles:**
- **Override built-in styles**: Use exact IDs like "Heading1", "Heading2", "Heading3" to override Word's built-in heading styles
- **HeadingLevel constants**: `HeadingLevel.HEADING_1` uses "Heading1" style, `HeadingLevel.HEADING_2` uses "Heading2" style, etc.
- **Include outlineLevel**: Set `outlineLevel: 0` for H1, `outlineLevel: 1` for H2, etc. to ensure TOC works correctly
- **公文字体一致性**: 正文统一仿宋，标题统一黑体，不混用其他字体
- **公文不用彩色**: 链接、标题全部黑色，不使用蓝色超链接或灰色标题
- **A4 纸张**: 使用 `size: { width: 11906, height: 16838 }` 设置 A4 尺寸
- **行距 1.5**: 在 default paragraph spacing 中设置 `line: 360`
- **首行缩进**: 正文段落添加 `indent: { firstLine: 560 }`


## Lists (ALWAYS USE PROPER LISTS - NEVER USE UNICODE BULLETS)
```javascript
// Bullets - ALWAYS use the numbering config, NOT unicode symbols
// CRITICAL: Use LevelFormat.BULLET constant, NOT the string "bullet"
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "first-numbered-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "second-numbered-list", // Different reference = restarts at 1
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    children: [
      // Bullet list items
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("First bullet point")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Second bullet point")] }),
      // Numbered list items
      new Paragraph({ numbering: { reference: "first-numbered-list", level: 0 },
        children: [new TextRun("First numbered item")] }),
      new Paragraph({ numbering: { reference: "first-numbered-list", level: 0 },
        children: [new TextRun("Second numbered item")] }),
      // ⚠️ CRITICAL: Different reference = INDEPENDENT list that restarts at 1
      // Same reference = CONTINUES previous numbering
      new Paragraph({ numbering: { reference: "second-numbered-list", level: 0 },
        children: [new TextRun("Starts at 1 again (because different reference)")] })
    ]
  }]
});

// ⚠️ CRITICAL NUMBERING RULE: Each reference creates an INDEPENDENT numbered list
// - Same reference = continues numbering (1, 2, 3... then 4, 5, 6...)
// - Different reference = restarts at 1 (1, 2, 3... then 1, 2, 3...)
// Use unique reference names for each separate numbered section!

// ⚠️ CRITICAL: NEVER use unicode bullets - they create fake lists that don't work properly
// new TextRun("• Item")           // WRONG
// new SymbolRun({ char: "2022" }) // WRONG
// ✅ ALWAYS use numbering config with LevelFormat.BULLET for real Word lists
```

## Tables — 公文表格规范
```javascript
// 公文表格：小四 12pt 仿宋，全线框，表头灰底居中加粗
const GOV_FONT_BODY = "STFangsong";
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" }; // 公文用黑色全线框
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

new Table({
  columnWidths: [4680, 4680], // ⚠️ CRITICAL: Set column widths at table level - values in DXA (twentieths of a point)
  margins: { top: 80, bottom: 80, left: 120, right: 120 }, // Set once for all cells
  rows: [
    // 表头行：灰底居中加粗
    new TableRow({
      tableHeader: true,
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          // ⚠️ CRITICAL: Always use ShadingType.CLEAR to prevent black backgrounds in Word.
          shading: { fill: "D9D9D9", type: ShadingType.CLEAR }, // 浅灰底
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "表头", bold: true, size: 24, font: GOV_FONT_BODY })] // 小四 12pt
          })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: "D9D9D9", type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "列标题", bold: true, size: 24, font: GOV_FONT_BODY })]
          })]
        })
      ]
    }),
    // 数据行：小四仿宋，左对齐
    new TableRow({
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun({ text: "数据内容", size: 24, font: GOV_FONT_BODY })] })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          children: [
            new Paragraph({
              numbering: { reference: "bullet-list", level: 0 },
              children: [new TextRun({ text: "列表项一", size: 24, font: GOV_FONT_BODY })]
            }),
            new Paragraph({
              numbering: { reference: "bullet-list", level: 0 },
              children: [new TextRun({ text: "列表项二", size: 24, font: GOV_FONT_BODY })]
            })
          ]
        })
      ]
    })
  ]
})
```

**IMPORTANT: Table Width & Borders**
- Use BOTH `columnWidths: [width1, width2, ...]` array AND `width: { size: X, type: WidthType.DXA }` on each cell
- Values in DXA (twentieths of a point): 1440 = 1 inch, Letter usable width = 9360 DXA (with 1" margins)
- Apply borders to individual `TableCell` elements, NOT the `Table` itself

**Precomputed Column Widths (Letter size with 1" margins = 9360 DXA total):**
- **2 columns:** `columnWidths: [4680, 4680]` (equal width)
- **3 columns:** `columnWidths: [3120, 3120, 3120]` (equal width)

## Links & Navigation
```javascript
// TOC (requires headings) - CRITICAL: Use HeadingLevel only, NOT custom styles
// ❌ WRONG: new Paragraph({ heading: HeadingLevel.HEADING_1, style: "customHeader", children: [new TextRun("Title")] })
// ✅ CORRECT: new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Title")] })
new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),

// External link
new Paragraph({
  children: [new ExternalHyperlink({
    children: [new TextRun({ text: "Google", style: "Hyperlink" })],
    link: "https://www.google.com"
  })]
}),

// Internal link & bookmark
new Paragraph({
  children: [new InternalHyperlink({
    children: [new TextRun({ text: "Go to Section", style: "Hyperlink" })],
    anchor: "section1"
  })]
}),
new Paragraph({
  children: [new TextRun("Section Content")],
  bookmark: { id: "section1", name: "section1" }
}),
```

## Images & Media
```javascript
// Basic image with sizing & positioning
// CRITICAL: Always specify 'type' parameter - it's REQUIRED for ImageRun
new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png", // NEW REQUIREMENT: Must specify image type (png, jpg, jpeg, gif, bmp, svg)
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150, rotation: 0 }, // rotation in degrees
    altText: { title: "Logo", description: "Company logo", name: "Name" } // IMPORTANT: All three fields are required
  })]
})
```

## Page Breaks
```javascript
// Manual page break
new Paragraph({ children: [new PageBreak()] }),

// Page break before paragraph
new Paragraph({
  pageBreakBefore: true,
  children: [new TextRun("This starts on a new page")]
})

// ⚠️ CRITICAL: NEVER use PageBreak standalone - it will create invalid XML that Word cannot open
// ❌ WRONG: new PageBreak() 
// ✅ CORRECT: new Paragraph({ children: [new PageBreak()] })
```

## Headers/Footers & Page Setup
```javascript
const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1440 = 1 inch
        size: { orientation: PageOrientation.LANDSCAPE },
        pageNumbers: { start: 1, formatType: "decimal" } // "upperRoman", "lowerRoman", "upperLetter", "lowerLetter"
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT,
        children: [new TextRun("Header Text")]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] }), new TextRun(" of "), new TextRun({ children: [PageNumber.TOTAL_PAGES] })]
      })] })
    },
    children: [/* content */]
  }]
});
```

## Tabs
```javascript
new Paragraph({
  tabStops: [
    { type: TabStopType.LEFT, position: TabStopPosition.MAX / 4 },
    { type: TabStopType.CENTER, position: TabStopPosition.MAX / 2 },
    { type: TabStopType.RIGHT, position: TabStopPosition.MAX * 3 / 4 }
  ],
  children: [new TextRun("Left\tCenter\tRight")]
})
```

## Constants & Quick Reference
- **Underlines:** `SINGLE`, `DOUBLE`, `WAVY`, `DASH`
- **Borders:** `SINGLE`, `DOUBLE`, `DASHED`, `DOTTED`  
- **Numbering:** `DECIMAL` (1,2,3), `UPPER_ROMAN` (I,II,III), `LOWER_LETTER` (a,b,c)
- **Tabs:** `LEFT`, `CENTER`, `RIGHT`, `DECIMAL`
- **Symbols:** `"2022"` (•), `"00A9"` (©), `"00AE"` (®), `"2122"` (™), `"00B0"` (°), `"F070"` (✓), `"F0FC"` (✗)

## Cross-Platform 路径处理（Windows / macOS / Linux）

**根本原因**: Windows 用 `\` 作路径分隔符，macOS/Linux 用 `/`。在 JS 字符串中 `\` 是转义符，直接写 `"C:\Users\file"` 会被解析为 `"C:Usersile"`。

### 必须遵守的规则

```javascript
const path = require('path');
const fs = require('fs');

// ❌ 硬编码斜杠 — Windows 上可能失败
const img = fs.readFileSync("images/logo.png");
const out = "output/report.docx";

// ✅ 始终用 path.join() 拼接路径
const img = fs.readFileSync(path.join("images", "logo.png"));
const out = path.join("output", "report.docx");

// ❌ 模板字符串拼路径
const file = `${dir}/report.docx`;

// ✅ path.join 拼接
const file = path.join(dir, "report.docx");

// ❌ __dirname + 硬编码斜杠
const tpl = __dirname + "/templates/header.xml";

// ✅ path.join(__dirname, ...)
const tpl = path.join(__dirname, "templates", "header.xml");
```

### 输出文件名注意事项

```javascript
// ✅ 写文件前确保目录存在
const outDir = path.join("output");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
Packer.toBuffer(doc).then(buf => fs.writeFileSync(path.join(outDir, "report.docx"), buf));
```

### Python 脚本同样适用

```python
import os

# ❌ 硬编码斜杠
doc_path = "word/document.xml"

# ✅ os.path.join
doc_path = os.path.join("word", "document.xml")

# ✅ pathlib (Python 3.4+) 更优雅
from pathlib import Path
doc_path = Path("word") / "document.xml"
```

### Shell 命令中的路径

```bash
# ✅ 正斜杠在所有平台的 shell 中都能工作（包括 Windows PowerShell/cmd）
python ooxml/scripts/unpack.py input.docx output_dir

# ⚠️ 但如果路径来自变量且含空格，务必加引号
python "ooxml/scripts/unpack.py" "$INPUT_FILE" "$OUTPUT_DIR"
```

### 快速检查清单

| 检查项 | 说明 |
|--------|------|
| 不出现 `"/"`  拼路径 | 用 `path.join()` / `os.path.join()` |
| 不出现 `"\\"` 拼路径 | 同上 |
| 不出现 `` `${x}/y` `` 拼路径 | 用 `path.join(x, "y")` |
| `fs.mkdirSync` 带 `recursive` | 确保输出目录存在 |
| 文件名不含 `: * ? " < > \|` | Windows 保留字符，会导致写入失败 |
| 路径含空格时加引号 | shell 命令中 `"$PATH"` |

## Critical Issues & Common Mistakes
- **CRITICAL: PageBreak must ALWAYS be inside a Paragraph** - standalone PageBreak creates invalid XML that Word cannot open
- **ALWAYS use ShadingType.CLEAR for table cell shading** - Never use ShadingType.SOLID (causes black background).
- Measurements in DXA (1440 = 1 inch) | Each table cell needs ≥1 Paragraph | TOC requires HeadingLevel styles only
- **公文字体**: 正文用仿宋 (STFangsong)，标题用黑体 (Heiti SC)，表格用小四仿宋，代码用 Courier New
- **公文默认字号**: 正文 14pt (size: 28)，h1 16pt (size: 32)，h2 15pt (size: 30)，h3+ 14pt (size: 28)，表格 12pt (size: 24)
- **公文行距**: 在 default paragraph 中设置 `spacing: { line: 360 }` (1.5 倍行距)
- **公文首行缩进**: 正文段落添加 `indent: { firstLine: 560 }`（14pt × 20 × 2）
- **公文纸张**: A4 尺寸 `size: { width: 11906, height: 16838 }`
- **公文链接**: 黑色下划线，覆盖 Hyperlink 字符样式为 `color: "000000"`
- **公文表格**: 黑色全线框 `color: "000000"`，表头灰底 `fill: "D9D9D9"`
- **ALWAYS use columnWidths array for tables** + individual cell widths for compatibility
- **NEVER use unicode symbols for bullets** - always use proper numbering configuration with `LevelFormat.BULLET` constant (NOT the string "bullet")
- **NEVER use \n for line breaks anywhere** - always use separate Paragraph elements for each line
- **ALWAYS use TextRun objects within Paragraph children** - never use text property directly on Paragraph
- **CRITICAL for images**: ImageRun REQUIRES `type` parameter - always specify "png", "jpg", "jpeg", "gif", "bmp", or "svg"
- **CRITICAL for bullets**: Must use `LevelFormat.BULLET` constant, not string "bullet", and include `text: "•"` for the bullet character
- **CRITICAL for numbering**: Each numbering reference creates an INDEPENDENT list. Same reference = continues numbering (1,2,3 then 4,5,6). Different reference = restarts at 1 (1,2,3 then 1,2,3). Use unique reference names for each separate numbered section!
- **CRITICAL for TOC**: When using TableOfContents, headings must use HeadingLevel ONLY - do NOT add custom styles to heading paragraphs or TOC will break
- **Tables**: Set `columnWidths` array + individual cell widths, apply borders to cells not table
- **Set table margins at TABLE level** for consistent cell padding (avoids repetition per cell)
- **跨平台路径**: 始终用 `path.join()` 拼接路径，不硬编码 `/` 或 `\\`。写文件前用 `fs.mkdirSync(dir, { recursive: true })` 确保目录存在