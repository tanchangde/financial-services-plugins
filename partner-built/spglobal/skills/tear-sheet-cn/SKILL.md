---
name: tear-sheet
description: 使用 Kensho LLM-ready API MCP 服务器的 S&P Capital IQ 数据生成专业的公司 tear sheet（公司概览表）。当用户请求 tear sheet、公司单页、公司简介、事实表、公司快照或公司概述文档时——尤其是当他们提到特定公司名称或股票代码时——使用此技能。当用户请求股票研究摘要、并购（M&A）公司简介、企业开发目标档案、销售/业务开发会议准备文档或任何简洁的单一公司财务摘要时，也会触发。此技能支持四种受众类型：股票研究、投资银行/M&A、企业开发和销售/业务开发。如果用户未指定受众，请询问。适用于上市公司和私营公司。
---

# 财务 Tear Sheet 生成器 (Financial Tear Sheet Generator)

通过从 S&P Capital IQ（标普资本市场情报）提取实时数据（通过 S&P Global MCP 工具），并将结果格式化为专业的 Word 文档，生成针对特定受众的公司 tear sheet。

## 样式配置

这些是合理的默认值。要为公司品牌自定义，修改此部分——常见更改包括交换调色板、更改字体（许多银行使用 Calibri 作为标准）和更新免责声明文本。

**颜色：**
- 主色（页眉横幅背景、部分标题文本）：#1F3864
- 强调色（签名部分高亮）：#2E75B6
- 表格表头行填充：#D6E4F0
- 表格交替行填充：#F2F2F2
- 表格边框：#CCCCCC
- 页眉横幅文本：#FFFFFF

**排版（尺寸以半点为单位，用于 docx-js）：**
- 字体系列：Arial
- 公司名称：18pt 粗体（尺寸：36）
- 部分标题：11pt 粗体（尺寸：22），主色
- 正文文本：9pt（尺寸：18）
- 表格文本：8.5pt（尺寸：17）
- 页脚/免责声明：7pt 斜体（尺寸：14）
- 每个模板的覆盖在参考文件中指定。

**公司页眉横幅：**
- 页眉是深蓝色（#1F3864）横幅，跨越整个页面宽度，公司名称为白色。
- **在横幅下方，键值对必须在两列无边框表格中呈现，跨越整个页面宽度。** 左列：公司标识符（股票代码、总部、成立年份、员工人数、行业）。右列：财务标识符（市值、企业价值（EV）、股票价格、流通股数）。每个单元格包含粗体标签和同一直常规权重的值（例如，"**Market Cap** $124.7B"）。切勿将所有字段左对齐在单列中——这会浪费水平空间且看起来不专业。两列分布是区分专业 tear sheet 与默认文档的最重要视觉信号。
  - **实现：** 创建 2 列表格，所有单元格的 `borders: none` 和 `shading: none`。设置列宽各为 50%。将左列字段（股票代码、总部、成立年份、员工人数）作为单独的段落放在左单元格中。将右列字段（市值、企业价值、股票价格、流通股数）放在右单元格中。每个字段是单个段落：标签为粗体 run，值为常规 run。
  - 每列中的具体字段因受众而异——见参考文件的标题规范。原则始终是：跨页面分布，而非聚集在左侧。
- **切勿对标题键值块使用边框表格。** 边框表格仅保留给财务数据。
- 标题中的关键指标（市值、企业价值、股票价格）应显示为内联键值对，而非单独的边框表格中。

**部分标题：**
- 每个部分标题下方有一条水平线（细线，#CCCCCC，0.5pt），以在部分之间创建清晰的视觉分隔。
- **将规则作为底部边框应用于标题段落本身**——切勿为规则插入单独的段落元素。单独的段落会添加其自身的前后间距，导致标题下方过度空白。
- **实现：** 在 docx-js 中，通过 `paragraph.borders.bottom = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }` 将底部边框应用于部分标题段落。切勿使用 `doc.addParagraph()` 与单独的水平规则元素。切勿使用 `thematicBreak`。边框必须在标题段落本身上，间距后为 0pt，因此规则紧贴标题文本。
- 间距：标题段落前 12pt，标题段落后 0pt，下一个内容元素前 4pt。

**项目符号格式：**
- 所有 tear sheet 类型的所有项目符号内容使用单个项目符号字符（•）。切勿在 tear sheet 内或之间混合 •、-、▸ 或编号列表。
- **合成/分析项目符号**（财报亮点、战略契合、整合考虑因素、对话开场白）：缩进块式格式，左缩进 360 DXA（0.25"），并为项目符号字符设置悬挂缩进。这些应在视觉上偏离正文文本——它们是解释性内容，应看起来与数据表格和散文段落不同。
- **关系部分内的信息性项目符号**：标准正文缩进（180 DXA），无悬挂缩进。
- **切勿对任何项目符号部分应用左边框强调。** 左边框样式在 docx-js 中渲染不一致并产生视觉伪影。使用缩进和文本大小区分来区分签名部分。

**表格（仅财务数据）：**
- 表头行：表格标题填充（#D6E4F0），粗体深色文本
- 正文行：交替白色 / 表格交替填充（#F2F2F2）
- 边框：表格边框颜色（#CCCCCC），细（BorderStyle.SINGLE，尺寸 1）
- 单元格填充：顶部/底部 40 DXA，左侧/右侧 80 DXA
- 右对齐所有数字列
- 始终使用 ShadingType.CLEAR（切勿使用 SOLID——SOLID 导致黑色背景）

**布局：**
- 美国信纸纵向，0.75" 边距（所有边 1080 DXA）

**数字格式：**
- 货币：美元。使用百万为单位，除非公司收入 > 500 亿美元（然后使用十亿，一位小数）。在列标题中标注单位（例如，"Revenue ($M)"），而非在单个单元格中。
- **表格单元格：纯数字带逗号，无美元符号。** 例如，收入单元格显示"4,916"而非"$4,916"。列标题携带单位。
- 财年：实际年份（FY2022、FY2023、FY2024），切勿使用相对标签（FY-2、FY-1）。
- 负数：括号，例如 (2.3%)
- 百分比：一位小数
- 大数字：逗号作为千位分隔符

**页脚（文档页脚，非内联）：**
将来源归属和免责声明放在实际的文档页脚（每页重复），而非作为内联正文文本在底部。页脚正好两行，居中，每页：
- 第 1 行："Data: S&P Capital IQ via Kensho | Analysis: AI-generated | [Month Day, Year]"
- 第 2 行："For informational purposes only. Not investment advice."
- 样式：7pt 斜体，居中，#666666 文本颜色
- 此页脚文本在所有 tear sheet 类型、所有受众类型、每页必须完全相同。切勿因受众不同而改变措辞。
- **此页脚在每份 tear sheet、每种受众类型、每页都是必需的。** 切勿省略它。

## 组件函数

**必须使用这些确切的函数创建文档元素。切勿编写自定义 docx-js 样式代码。** 将这些函数复制到生成的 Node 脚本中并调用它们。上方的样式配置散文仍作为文档；这些函数是执行机制。

```javascript
const docx = require("docx");
const {
  Document, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType,
  Header, Footer, PageNumber, HeadingLevel, TableLayoutType,
  convertInchesToTwip
} = docx;

// ── 颜色常量 ──
const COLORS = {
  PRIMARY: "1F3864",
  ACCENT: "2E75B6",
  TABLE_HEADER_FILL: "D6E4F0",
  TABLE_ALT_ROW: "F2F2F2",
  TABLE_BORDER: "CCCCCC",
  HEADER_TEXT: "FFFFFF",
  FOOTER_TEXT: "666666",
};

const FONT = "Arial";

// ── 1. createHeaderBanner ──
// 返回 docx 元素数组：[横幅段落，键值表]
function createHeaderBanner(companyName, leftFields, rightFields) {
  // leftFields / rightFields: { label: string, value: string } 数组
  const banner = new Paragraph({
    children: [
      new TextRun({
        text: companyName,
        bold: true,
        size: 36, // 18pt
        color: COLORS.HEADER_TEXT,
        font: FONT,
      }),
    ],
    shading: { type: ShadingType.CLEAR, color: "auto", fill: COLORS.PRIMARY },
    spacing: { after: 0 },
    alignment: AlignmentType.LEFT,
  });

  function buildCellParagraphs(fields) {
    return fields.map(
      (f) =>
        new Paragraph({
          children: [
            new TextRun({ text: f.label + "  ", bold: true, size: 18, font: FONT }),
            new TextRun({ text: f.value, size: 18, font: FONT }),
          ],
          spacing: { after: 40 },
        })
    );
  }

  const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
  const noShading = { type: ShadingType.CLEAR, color: "auto", fill: "FFFFFF" };

  const kvTable = new Table({
    rows: [
      new TableRow({
        children: [
          new TableCell({
            children: buildCellParagraphs(leftFields),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: noBorders,
            shading: noShading,
          }),
          new TableCell({
            children: buildCellParagraphs(rightFields),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: noBorders,
            shading: noShading,
          }),
        ],
      }),
    ],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });

  return [banner, kvTable];
}

// ── 2. createSectionHeader ──
// 返回带有底部边框规则的单个段落
function createSectionHeader(text) {
  return new Paragraph({
    children: [
      new TextRun({
        text: text,
        bold: true,
        size: 22, // 11pt
        color: COLORS.PRIMARY,
        font: FONT,
      }),
    ],
    spacing: { before: 240, after: 0 }, // 前 12pt，后 0pt
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    },
  });
}

// ── 3. createTable ──
// headers: string[], rows: string[][], options: { accentHeader?, fontSize? }
function createTable(headers, rows, options = {}) {
  const fontSize = options.fontSize || 17; // 8.5pt 默认
  const headerFill = options.accentHeader ? COLORS.ACCENT : COLORS.TABLE_HEADER_FILL;
  const headerTextColor = options.accentHeader ? COLORS.HEADER_TEXT : "000000";

  const cellBorders = {
    top: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    left: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    right: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
  };

  const cellMargins = { top: 40, bottom: 40, left: 80, right: 80 };

  function isNumeric(val) {
    if (typeof val !== "string") return false;
    const cleaned = val.replace(/[,$%()]/g, "").trim();
    return cleaned !== "" && !isNaN(cleaned);
  }

  // 表头行
  const headerRow = new TableRow({
    children: headers.map(
      (h) =>
        new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: h,
                  bold: true,
                  size: fontSize,
                  color: headerTextColor,
                  font: FONT,
                }),
              ],
            }),
          ],
          shading: { type: ShadingType.CLEAR, color: "auto", fill: headerFill },
          borders: cellBorders,
          margins: cellMargins,
        })
    ),
  });

  // 数据行，交替着色
  const dataRows = rows.map((row, rowIdx) => {
    const fill = rowIdx % 2 === 1 ? COLORS.TABLE_ALT_ROW : "FFFFFF";
    return new TableRow({
      children: row.map((cell, colIdx) => {
        const align = colIdx > 0 && isNumeric(cell)
          ? AlignmentType.RIGHT
          : AlignmentType.LEFT;
        return new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: cell, size: fontSize, font: FONT }),
              ],
              alignment: align,
            }),
          ],
          shading: { type: ShadingType.CLEAR, color: "auto", fill: fill },
          borders: cellBorders,
          margins: cellMargins,
        });
      }),
    });
  });

  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });
}

// ── 4. createBulletList ──
// items: string[], style: "synthesis" | "informational"
function createBulletList(items, style = "synthesis") {
  const indent =
    style === "synthesis"
      ? { left: 360, hanging: 180 }   // 左 360 DXA，项目符号悬挂缩进
      : { left: 180 };                 // 180 DXA，无悬挂

  return items.map(
    (item) =>
      new Paragraph({
        children: [
          new TextRun({ text: "•  ", font: FONT, size: 18 }),
          new TextRun({ text: item, font: FONT, size: 18 }),
        ],
        indent: indent,
        spacing: { after: 60 },
      })
  );
}

// ── 5. createFooter ──
// date: string（例如，"February 23, 2026"）
function createFooter(date) {
  return new Footer({
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text: `Data: S&P Capital IQ via Kensho | Analysis: AI-generated | ${date}`,
            italics: true,
            size: 14, // 7pt
            color: COLORS.FOOTER_TEXT,
            font: FONT,
          }),
        ],
        alignment: AlignmentType.CENTER,
      }),
      new Paragraph({
        children: [
          new TextRun({
            text: "For informational purposes only. Not investment advice.",
            italics: true,
            size: 14,
            color: COLORS.FOOTER_TEXT,
            font: FONT,
          }),
        ],
        alignment: AlignmentType.CENTER,
      }),
    ],
  });
}
```

**在生成的脚本中使用：**
1. 将上述所有函数和常量复制到生成的 Node.js 脚本中
2. 调用 `createHeaderBanner(...)` 而非手动构建横幅段落和表格
3. 对每个部分标题调用 `createSectionHeader(...)`——切勿手动设置段落边框
4. 对**所有**表格数据调用 `createTable(...)`——财务摘要、交易可比公司、并购活动、关系表、融资历史等。对并购活动表格传递 `{ accentHeader: true }`（IB/M&A 模板）。对于非数字表格（例如，关系、所有权），函数仍然正常工作——它仅右对齐包含数字值的单元格。
5. 对财报亮点、战略契合、整合考虑因素和对话开场白调用 `createBulletList(items, "synthesis")`
6. 对关系条目调用 `createBulletList(items, "informational")`
7. 将 `createFooter(date)` 传递给 Document 构造函数的 `footers.default` 属性

**这些函数消除的内容：**
- 黑色背景表格（在所有地方强制 `ShadingType.CLEAR`）
- 部分标题下的单独水平规则段落（强制 `border.bottom` 在段落本身上）
- 标题中的边框键值表格（强制 `borders: none`）
- 不一致的项目符号样式（仅强制 `•` 字符）
- 缺失页脚（提供确切的页脚结构）

## 工作流程

### 第 1 步：识别输入

在继续之前收集最多四件事：

1. **公司**——名称或股票代码。如果只有股票代码，通过初始查询解析完整公司名称（例如，使用公司信息工具）。
2. **受众**——四种类型之一：
   - **股票研究**——用于买方/卖方分析师评估投资
   - **IB / M&A**——用于银行家在交易背景下分析公司
   - **Corp Dev**——用于内部战略团队评估收购目标
   - **Sales / BD**——用于商业团队准备客户会议
3. **可比公司**（可选）——如果用户有特定的可比公司在心中，记下它们。否则，技能将从 S&P Global 数据识别同行。这对股票研究、IB/M&A 和 Corp Dev tear sheet 很重要。
4. **页面长度偏好**（可选）——因受众而异（见下文），但用户可以覆盖。

如果用户未指定受众，请询问。

### 第 2 步：阅读特定受众的参考

从此技能目录中阅读相应的参考文件：

- 股票研究 → `references/equity-research.md`
- IB / M&A → `references/ib-ma.md`
- Corp Dev → `references/corp-dev.md`
- Sales / BD → `references/sales-bd.md`

每个参考定义了部分、查询计划、格式指南和页面长度默认值。

### 第 3 步：通过 S&P Global MCP 提取数据

**首先：** 创建中间文件目录：
```bash
mkdir -p /tmp/tear-sheet/
```

使用 **S&P Global** MCP 工具（也称为 Kensho LLM-ready API）。Claude 将有权访问用于财务数据、公司信息、市场数据、共识预期、财报电话会议记录、并购交易和业务关系的结构化工具。每个参考文件中的查询计划描述了为每个部分检索哪些数据——将这些映射到对话中可用的适当 S&P Global 工具。

**每次查询步骤后，立即将检索到的数据写入参考文件查询计划中指定的中间文件。** 切勿推迟写入——写入磁盘的数据在长对话中受到上下文退化的保护。

**查询策略：**
每个参考文件包括 4-6 个数据检索步骤的查询计划。这些是起点，而非刚性约束。优先考虑数据完整性而非最小化调用：

- **始终提取 4 个财年的财务数据**，即使只显示 3 年。第四年（最早）需要计算第一个显示年份的同比（YoY）收入增长。没有它，最早年份的增长率将显示"N/A"——这看起来像缺失数据，而非设计选择。
- 按书面执行查询计划，使用与所需数据匹配的任何 S&P Global 工具。
- 如果工具调用返回不完整结果，尝试替代工具或更窄的查询。例如，如果公司摘要不包括分部详细信息，直接尝试分部工具。
- 如果目标重试后未返回数据点，继续——将其标记为"N/A"或"未披露"。
- 切勿编造数据。如果工具未返回数字，切勿从训练知识估计。

**用户指定的可比公司：** 如果用户提供可比公司，明确查询每个可比公司的财务数据和倍数。如果未提供可比公司，使用工具返回的任何同行数据，或使用竞争对手工具从公司行业识别同行。

**来自用户的可选上下文：** 倾听用户自然提供的其他上下文。如果他们提到收购方是谁（"我们为我们的平台看待这个"）、他们销售什么（"我们向银行销售数据分析"）或可能的买家是谁（"这对 Salesforce 或 Microsoft 很有趣"），将该上下文纳入相关合成部分（战略契合、对话开场白、交易角度）。切勿提示此信息——如果提供，只需使用它。

**私营公司处理：**
CIQ 包括私营公司数据，因此以相同方式查询。但预期结果较稀疏。为私营公司生成时：
- 跳过：股票价格、52 周范围、beta、股票表现、共识预期、交易可比公司
- 强调：业务概述、关系、所有权结构、任何可用的财务数据
- 在标题中显著注明"Private Company"（私营公司）

### 第 3b 步：计算衍生指标

在所有数据收集完成并写入中间文件后，在单个专用传递中计算所有衍生指标。这是纯计算步骤——无新的 MCP 查询。

**将所有中间文件读回上下文中**，然后计算：

- **利润率：** 毛利率 %、息税折旧摊销前利润（EBITDA）利润率 %、自由现金流（FCF）利润率 %、营业利润率 %
- **增长率：** 同比（YoY）收入增长、同比分部收入增长、同比每股收益（EPS）增长
- **效率比率：** FCF 转换率（FCF/EBITDA）、研发占收入 %、资本支出占收入 %
- **资本结构：** 净债务（总债务 − 现金及等价物）、净债务 / EBITDA
- **分部组合：** 每个分部的收入占综合总收入的 %（使用综合收入作为分母，根据数据完整性规则 8）

**验证（从算术验证移动）：** 在此计算传递期间，执行所有算术检查：

- **利润率计算：** 验证 EBITDA 利润率 = EBITDA / 收入，毛利率 = 毛利 / 收入等。如果计算的利润率与原始数字不匹配，使用从原始组件的计算。
- **增长率：** 验证同比增长 = (当前 − 先前) / 先前。如果有基础值，切勿依赖预先计算的增长率。
- **分部总计：** 如果显示分部收入，验证分部总和等于总收入（在舍入容差内）。如果不符合，省略总行而非发布不一致的数学。
- **百分比列：** 验证"% of Total"列总和约 100%。
- **估值交叉检查：** 如果显示企业价值（EV）和 EV/收入，验证 EV / 收入 ≈ 声明的倍数。

如果验证失败：尝试从原始数据重新计算。如果仍然不一致，将该指标标记为"N/A"，而非发布不正确的数字。静默的数学错误在 tear sheet 中会破坏可信度。

**写入结果** 到 `/tmp/tear-sheet/calculations.csv`，列：`metric,value,formula,components`

示例行：
```
metric,value,formula,components
gross_margin_fy2024,72.4%,gross_profit/revenue,"9524/13159"
revenue_growth_fy2024,12.3%,(current-prior)/prior,"13159/11716"
net_debt_fy2024,2150,total_debt-cash,"4200-2050"
```

### 第 3c 步：验证数据文件

在生成文档之前，验证所有中间文件是否存在并填充。

**通过单独的读取操作读取每个中间文件**并打印验证摘要：

```
=== Tear Sheet Data Verification ===
company-profile.txt: ✓ (12 fields)
financials.csv:      ✓ (36 rows)
segments.csv:        ✓ (8 rows)
valuation.csv:       ✓ (5 rows)
calculations.csv:    ✓ (18 rows)
earnings.txt:        ✓ (populated)
relationships.txt:   ⚠ MISSING
peer-comps.csv:      ✓ (12 rows)
================================
```

**软门：** 如果当前受众类型预期的任何文件缺失或为空，打印警告但继续。tear sheet 通过"N/A"和部分跳过优雅地处理缺失数据。但是，警告确保对丢失数据的可见性。

**关键规则：文件——而非你对早期对话的记忆——是文档中每个数字的唯一真实来源。** 在第 4 步生成 DOCX 时，从中间文件读取值。切勿依赖对话上下文的财务数据。

### 第 4 步：格式化为 DOCX

阅读 `/mnt/skills/public/docx/SKILL.md` 了解 docx 创建机制（通过 Node 的 docx-js）。应用上方的样式配置以及参考文件中的特定部分格式。

**页面长度默认值（用户可以覆盖）：**
- 股票研究：1 页（密度是惯例）
- IB / M&A：1-2 页
- Corp Dev：1-2 页
- Sales / BD：1-2 页

如果内容超过目标，每个参考文件指定首先削减哪些部分。

**输出文件名：** `[CompanyName]_TearSheet_[Audience]_[YYYYMMDD].docx`
示例：`Nvidia_TearSheet_CorpDev_20260220.docx`

保存到 `/mnt/user-data/outputs/` 并呈现给用户。

## 数据完整性规则

这些覆盖其他一切：
1. **S&P Global 工具是财务数据的唯一来源。** 切勿用训练知识填补空白——它可能过时或错误。
2. **标记你找不到的内容。** 使用"N/A"或"Not disclosed"而非静默省略行。
3. **日期很重要。** 注明财年结束或报告期。切勿假设日历年度 = 财年。市场数据（股票价格、市值）应包括"as of"日期。
4. **切勿混合报告期。** 如果有 FY2023 收入和 LTM EBITDA，明确标记它们。
5. **优先使用 MCP 返回的字段而非手动计算。** 如果 S&P Global 工具返回预先计算的字段（例如，净债务、EBITDA、FCF），直接使用该值，而非从组件计算。仅当工具未返回字段时手动计算衍生指标。这减少了差异。
6. **确保 tear sheet 类型之间的一致性。** 如果为同一家公司生成多个 tear sheet（例如，同一会话中的股票研究和 IB/M&A），相同的基础数据点必须在所有输出中产生相同的值。净债务、收入、EBITDA、利润率和增长率必须完全匹配。切勿每份报告重新查询或独立重新计算——重用相同的检索值。
7. **切勿降级已知交易值。** 如果 M&A... [截断]
8. **使用综合收入作为分部百分比的分母。** 计算分部表格的"% of Total"时，将每个分部的收入除以综合总收入（如损益表所报告），而非分部收入之和。由于分部间抵消，分部总和通常超过综合收入。使用综合收入确保百分比与文档中其他地方显示的总收入数字一致。
9. **如有可用，始终包括前瞻性（NTM）倍数。** 如果工具返回 trailing 和 forward 估值倍数，两者都必须出现在输出中。Forward 倍数是股票研究、IB/M&A 和 corp dev 受众的主要估值参考。当 forward 数据可用时，切勿仅显示 trailing 倍数。
10. **无 S&P Global 工具返回高管或管理层数据。** 切勿从训练数据填充管理层名称、头衔或传记详细信息——这违反规则 1 并产生过时信息。如果模板中出现管理层部分，完全省略它。所有权结构（机构持有人、内部人 %、PE 赞助商）仅在工具返回时可包括——以"数据允许"为门控。

## 中间文件规则

从 MCP 工具检索的所有数据必须在文档生成之前持久化到结构化的中间文件。这些文件——而非对话上下文——是文档中每个数字的唯一真实来源。

**设置：** 在第 3 步开始时，创建工作目录：
```
mkdir -p /tmp/tear-sheet/
```

**查询后写入要求：** 每个 MCP 查询步骤完成后，立即将检索到的数据写入适当的中间文件。切勿等到所有查询完成。每个参考文件的查询计划指定每个步骤后写入哪些文件。

**文件架构：**

| 文件 | 格式 | 列 / 结构 | 使用者 |
|---|---|---|---|
| `/tmp/tear-sheet/company-profile.txt` | 键值文本 | name, ticker, exchange, HQ, sector, industry, founded, employees, market_cap, enterprise_value, stock_price, 52wk_high, 52wk_low, shares_outstanding, beta, ownership | 所有 |
| `/tmp/tear-sheet/financials.csv` | CSV | `period,line_item,value,source` | 所有 |
| `/tmp/tear-sheet/segments.csv` | CSV | `period,segment_name,revenue,source` | ER, IB, CD |
| `/tmp/tear-sheet/valuation.csv` | CSV | `metric,trailing,forward,source` | ER, IB, CD |
| `/tmp/tear-sheet/consensus.csv` | CSV | `metric,fy_year,value,source` | ER |
| `/tmp/tear-sheet/earnings.txt` | 结构化文本 | Quarter, date, key quotes, guidance, key drivers | ER, IB, Sales |
| `/tmp/tear-sheet/relationships.txt` | 结构化文本 | Customers, suppliers, partners, competitors — each with descriptors | IB, CD, Sales |
| `/tmp/tear-sheet/peer-comps.csv` | CSV | `ticker,metric,value,source` | ER, IB, CD |
| `/tmp/tear-sheet/ma-activity.csv` | CSV | `date,target,deal_value,type,rationale,source` | IB, CD |
| `/tmp/tear-sheet/calculations.csv` | CSV | `metric,value,formula,components` | 所有（在第 3b 步写入） |

**缩写：** ER = 股票研究，IB = IB/M&A，CD = Corp Dev，Sales = Sales/BD。

并非每个受众类型都使用每个文件——参考文件定义哪些查询步骤适用。当前受众类型不相关的文件无需创建。

**仅原始值。** 中间文件存储工具返回的原始值。切勿在这些文件中预先计算利润率、增长率或其他衍生指标——这发生在第 3b 步。

**页面预算执行：** 每个参考文件指定默认页面长度和编号的削减顺序。如果渲染的文档超过目标，按指定顺序应用削减——切勿尝试将字体大小或边距缩小到模板最小值以下。削减顺序是严格的优先级堆栈：在触及第 2 部分之前完全削减第 1 部分。

## 内容质量规则

11. **为受众重写每个叙述部分。** CIQ 公司摘要是输入，而非输出。每个受众类型需要不同的描述：对股票研究简洁且以论点为导向，对 IB 使用 pitchbook 散文，对 Corp Dev 以产品为中心，对 Sales/BD 使用 plain language。切勿在任何 tear sheet 中逐字粘贴 CIQ 摘要。
12. **因受众区分财报亮点。** 相同的财报电话会议为不同读者产生不同的要点。股票研究需要分部级表现和共识超越/落后。IB 需要利润率轨迹和战略评论。Sales/BD 需要创造对话角度的战略主题。切勿在 tear sheet 类型之间重用相同的要点。
13. **合成部分是差异化因素。** 战略契合分析、整合考虑因素、对话开场白和业务概述段落是 tear sheet 赚取其价值的地方。这些部分需要分析推理，将数据点连接成叙述——列出公司名称而无上下文不是合成。
14. **在分部表格中标记待决 divestitures。** 如果公司已宣布待决 divestiture 分部或业务单位，在分部表格中添加脚注或括号注明待决交易（例如，"Mobility* — *Pending divestiture, expected mid-2026"）。对于 Corp Dev 和 IB/M&A tear sheet，在分部表格下方包括一行注释，显示 pro-forma 收入和收入组合，不包括 divested 分部。这帮助读者评估"go-forward"业务，无需自己做数学。

### 算术验证

**→ 算术验证现在在第 3b 步（计算衍生指标）中执行。** 所有利润率计算、增长率、分部总计、百分比列和估值交叉检查在文档生成开始之前在专用计算传递中验证。见第 3b 步的完整验证检查列表。
