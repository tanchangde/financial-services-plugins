---
name: funding-digest
description: 生成专业的单页 PowerPoint 幻灯片，总结用户关注的行业或公司近期融资轮次和重要资本市场活动的关键要点。当用户请求交易流摘要、每周回顾、融资简报、交易汇总或资本市场简报时使用此技能。触发词包括：'deal flow digest'（交易流简报）、'weekly funding recap'（每周融资回顾）、'deal roundup'（交易汇总）、'transaction summary this week'（本周交易摘要）、'what happened in [sector] this week'（本周 [行业] 发生了什么）、'capital markets update'（资本市场更新）或任何将近期融资活动汇编为简报幻灯片的请求。生成专业的单页 PPTX，包含关键要点、估值数据和 Capital IQ 交易链接。
---

**AI 免责声明（强制）：**
必须在 PowerPoint 页脚中包含以下免责声明文本。这不是可选项——没有它的报告是不完整的：

> **"Analysis is AI-generated — please confirm all outputs"（分析由 AI 生成——请确认所有输出）**

**页脚**——在生成的幻灯片底部，作为醒目的黄色横幅："Analysis is AI-generated — please confirm all outputs"

---

# 每周交易流简报 (Weekly Deal Flow Digest)

生成分析师质量的**单页 PowerPoint**，总结用户关注的行业或公司近期融资轮次的关键要点，使用 S&P Global Capital IQ（标普全球资本市场情报）数据。每笔交易链接回其 Capital IQ 档案，便于快速深入查看。

## 何时使用

在以下任何模式时触发：
- "Give me a deal flow digest for this week"（给我本周的交易流简报）
- "Weekly funding recap for [sector]"（[行业] 的每周融资回顾）
- "What deals closed in [sector/companies] recently?"（最近 [行业/公司] 完成了哪些交易？）
- "Transaction roundup" 或 "deal roundup"（交易汇总）
- "Capital markets update for my coverage universe"（我覆盖范围的资本市场更新）
- "Summarize recent funding activity"（总结近期融资活动）
- 任何关于交易、融资或轮次的定期简报请求

## 嵌套技能

此技能生成单页 PPTX 简报：
- 在生成 PowerPoint 之前**阅读** `/mnt/skills/public/pptx/SKILL.md`（及其子参考 `pptxgenjs.md` 用于从头创建）

## 实体解析与工具鲁棒性

S&P Global（标普全球）的标识符系统可将公司名称解析为法律实体。这对大多数公司都有效，但存在已知的失败模式，会导致空结果。**在整个工作流程中应用这些规则，以避免静默数据丢失。**

### 规则 0：在查询融资前预验证所有标识符

**在**调用任何融资工具之前，通过 `get_info_from_identifiers` 运行每个标识符。这是最早捕获问题的最便宜和最可靠的方法。检查响应中的两件事：

1. **是否解析成功？** 如果标识符返回空/错误，则该名称在 S&P Global 中不存在。尝试 `references/sector-seeds.md` 中的别名、法律实体名称或直接使用 `company_id`。
2. **`status` 字段是什么？**
   - `"Operating"`（运营中）→ 可安全查询融资轮次。
   - `"Operating Subsidiary"`（运营子公司）→ 公司存在但由母公司拥有。将返回**零融资轮次**。在简报中注明此为上下文（例如，"被 [母公司] 收购"），但切勿查询融资。
   - 任何其他状态（例如，已关闭、非活跃）→ 公司不再运营。历史数据可能存在，但无新活动。

**此单一预验证步骤可防止大多数空结果问题。** 将所有候选批量处理到单个 `get_info_from_identifiers` 调用中（它能很好地处理大批量），并在继续之前进行分类。

### 规则 1：切勿信任无回退的空结果

如果 `get_rounds_of_funding_from_identifiers` 对预期有数据的公司返回空：
1. **尝试法律实体名称或 company_id。** 品牌名称通常有效，但有些不行。请参阅 `references/sector-seeds.md` 中的别名表以获取已知的不匹配。常见模式："[Brand] AI" → "[Legal Name], Inc."（例如，Together AI → "Together Computer, Inc."，Character.ai → "Character Technologies, Inc."，Runway ML → "Runway AI, Inc."）。
2. **验证公司是否存在于 S&P 中。** 如果跳过了规则 0，现在调用 `get_info_from_identifiers(identifiers=["Company"])`——如果这也返回空，该公司可能处于太早期阶段或尚未被索引。

### 规则 2：子公司没有融资轮次

作为大公司部门或全资子公司的公司（例如，DeepMind 隶属于 Alphabet、GitHub 隶属于 Microsoft、BeReal 隶属于 Voodoo）将返回**零融资轮次**。其资本事件在母公司层面追踪。

**如何检测：** `get_info_from_identifiers` 返回的 `status` 字段将显示 `"Operating Subsidiary"`。`references/sector-seeds.md` 文件也用 ⚠️ 警告标记已知的子公司。对于融资查询，跳过这些。

### 规则 3：使用 `get_rounds_of_funding_from_identifiers` 作为主要工具，而非 `get_funding_summary_from_identifiers`

摘要工具更快但较不可靠——即使详细轮次存在，它也可能返回错误或不完整数据。始终使用详细轮次工具作为主要数据源。摘要工具仅在快速 aggregate 检查（总融资额、轮次数量）时可接受，如果结果看起来偏低，应使用轮次工具验证。

### 规则 4：仔细批量处理并验证

处理大型公司群体（50+ 家公司）时，以 15-20 家为一组进行批量处理。每批后，检查返回空结果的公司，并在继续之前通过规则 1 中的回退步骤运行它们。

### 规则 5：`role` 参数至关重要

- `company_raising_funds`（筹集资金的公司）→ "X 筹集了哪些轮次？"（公司视角）
- `company_investing_in_round_of_funding`（在融资轮次中投资的公司）→ "投资者 Y 投资了什么？"（投资者视角）

使用错误的角色会静默返回空结果。对于交易流简报，几乎总是需要 `company_raising_funds`。仅在专门分析投资者的投资组合活动时使用投资者角色。

### 规则 6：标识符解析不区分大小写但区分拼写

S&P Global 处理大小写变体（"openai" = "OpenAI"），但对拼写和标点符号严格。"Character AI" 可能在 "Character.ai" 成功时失败。如有疑问，使用 `company_id`（例如，`C_1829047235`），这保证能解析。

## 工作流程

### 第 1 步：确定覆盖范围与期间

确定简报应涵盖的内容。有两种设置：

**回头客（已有观察列表）：**
如果用户之前定义了要追踪的行业或公司，使用该列表。检查对话历史中之前的观察列表。

**新用户：**
询问：

| 参数 | 默认值 | 备注 |
|-----------|---------|-------|
| **行业** | *(至少一个)* | 例如，"AI、金融科技、生物技术" |
| **特定公司** | 可选 | 补充行业级覆盖范围 |
| **时间期间** | 过去 7 天 | "本周"、"过去 2 周"、"本月" |

从时间期间计算确切的 `start_date` 和 `end_date`。

### 第 2 步：构建公司群体

对于每个指定的行业，使用已验证的引导方法构建公司群体：

1. **种子公司** 来自领域知识（见 `references/sector-seeds.md`）
   - 注意种子文件中的 ⚠️ 警告和别名注释——一些知名公司是子公司、已被收购或需要特定法律名称才能解析。
   - 种子文件包括 `company_id` 值，用于已知的别名不匹配。如果品牌名称失败，直接使用这些。

2. **立即预验证所有种子**（规则 0）：
   ```
   get_info_from_identifiers(identifiers=[all_seeds_for_this_sector])
   ```
   将结果分为两类：
   - ✅ **已解析且运营中**（`status` = "Operating"）→ 继续进行竞争对手扩展
   - ❌ **未解析或子公司** → 使用种子文件中的别名/法律名称重试；子公司注明为上下文但排除在融资查询之外

3. **通过竞争对手扩展**（仅使用 ✅ 已解析的种子）：
   ```
   get_competitors_from_identifiers(identifiers=[resolved_seeds], competitor_source="all")
   ```

4. **验证扩展的群体：**
   ```
   get_info_from_identifiers(identifiers=[new_competitors])
   ```
   应用相同的分类。按 `simple_industry` 匹配目标行业进行过滤。删除任何未解析的名称或子公司。

如果用户提供特定公司，直接添加这些，但仍通过预验证分类运行它们。切勿跳过验证——即使是知名品牌名称也可能静默失败。

保持群体可控——每个行业目标为 15-40 家**已解析、运营中**的公司。对于多行业简报，这可能总计 50-100+ 家公司。

### 第 3 步：提取融资轮次

对于群体中的所有公司：

```
get_rounds_of_funding_from_identifiers(
    identifiers=[batch],
    role="company_raising_funds",
    start_date="YYYY-MM-DD",
    end_date="YYYY-MM-DD"
)
```

如果群体很大，以 15-20 家为一组进行处理。

**每批后，识别结果为空的公司。** 对于任何预期有活动的公司：
1. 使用法律实体名称或备用标识符重试（见上方的实体解析规则）。
2. 仅在耗尽回退后将公司记录为"无数据"。

收集所有成功结果中的 `transaction_id` 值，然后使用详细信息丰富轮次：

```
get_rounds_of_funding_info_from_transaction_ids(
    transaction_ids=[all_funding_ids]
)
```

在单个调用（或少量调用）中传递所有交易 ID，而非每笔交易一次——该工具可高效处理批量。

**从每轮中提取以下内容（对幻灯片至关重要）：**
- `transaction_id`——Capital IQ 交易链接所需
- **公告日期**——轮次公开宣布的日期
- **结束日期**——轮次正式结束的日期
- 融资金额
- **投前估值**（如披露）
- **投后估值**（如披露）
- 领投方
- 轮次类型（A 轮、B 轮、C 轮等）
- 证券条款
- 顾问
- 定价趋势（向上轮次 / 向下轮次 / 平价）

> **日期是必需的。** 公告日期和结束日期必须始终出现在最终幻灯片的交易表中。如果只有一个日期可用，显示它并将另一个标记为"—"。

### 第 4 步：为重要交易获取公司背景

对于参与重大交易的任何公司（大额轮次、显著的估值变化），获取简要描述：

```
get_company_summary_from_identifiers(identifiers=[notable_companies])
```

这为叙述添加上下文（例如，"该公司是一家成立于 2021 年的 AI 基础设施初创公司，正在扩展到..."）。

### 第 5 步：识别亮点与趋势

在设计幻灯片之前，分析数据以呈现故事：

**标记为"重要"：**
- 轮次 ≥ 1 亿美元
- 向下轮次（定价趋势 = 向下）
- 新独角兽（投后估值突破 10 亿美元）
- 显著的估值跳跃（投后估值 ≥ 上次已知估值的 2 倍）
- 重复融资者（同一公司在 6 个月内再次融资）
- 异常庞大的投资者辛迪加

**识别趋势：**
- 本期部署的总资本与典型情况（如有历史数据可用）
- 哪些子行业最热门（最多轮次、最多资本）
- 轮次阶段分布（早期还是晚期主导？）
- 整个简报中最活跃的投资者
- 地理集中度
- 估值趋势（投前估值是压缩还是扩张？）

**选择关键要点（3-5 个）：**
将最重要的信号提炼为 3-5 个简洁的要点式要点。这些是幻灯片的中心。每个要点应为一句话，简洁且有数据支持。

示例：
- "AI 行业在本期通过 8 轮融资筹集 24 亿美元——是前一周的 3 倍，由 [公司] 的 8 亿美元 mega 轮领投，投后估值 120 亿美元。"
- "[公司] 完成 2 亿美元 D 轮，投前估值 35 亿美元，高于其 C 轮的 18 亿美元——表明对 AI 开发者工具的强劲需求。"
- "向下轮次活动上升：6 笔晚期轮次中有 2 笔定价低于先前估值。"

### 第 6 步：生成公司徽标

对于关键要点或重要交易中展示的每家公司，使用两层本地管道生成徽标。**切勿使用 Clearbit** (`logo.clearbit.com`)——它已弃用且持续失败。外部徽标 CDN（Brandfetch、logo.dev、Google Favicons）需要 API 密钥或被网络限制阻止。相反，使用以下方法：

#### 第 1 层：`simple-icons` npm 包（3,300+ 品牌 SVG，无需网络）

`simple-icons` 包捆绑了数千个知名品牌的高质量 SVG 图标。它完全离线工作——无需 API 密钥、无需网络调用。与 `sharp` 一起安装以进行 SVG → PNG 转换：

```bash
npm install simple-icons sharp
```

**查找策略：**

```javascript
const si = require('simple-icons');
const sharp = require('sharp');

// 通过精确标题匹配查找图标（不区分大小写）
function findSimpleIcon(companyName) {
    // 首先尝试精确匹配
    for (const [key, val] of Object.entries(si)) {
        if (!key.startsWith('si') || !val || !val.title) continue;
        if (val.title.toLowerCase() === companyName.toLowerCase()) return val;
    }
    // 尝试去除常见后缀（AI、Inc.、Corp.）
    const stripped = companyName.replace(/\s*(AI|Inc\.?|Corp\.?|Ltd\.?)$/i, '').trim();
    if (stripped !== companyName) {
        for (const [key, val] of Object.entries(si)) {
            if (!key.startsWith('si') || !val || !val.title) continue;
            if (val.title.toLowerCase() === stripped.toLowerCase()) return val;
        }
    }
    return null;
}

// 将 SVG 转换为 PNG，使用品牌的官方颜色
async function simpleIconToPng(icon, outputPath) {
    const coloredSvg = icon.svg.replace('<svg', `<svg fill="#${icon.hex}"`);
    await sharp(Buffer.from(coloredSvg))
        .resize(128, 128, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
        .png()
        .toFile(outputPath);
}
```

**覆盖范围：** ~43% 的典型交易流公司（对主要科技品牌如 Stripe、Anthropic、Databricks、Snowflake、Discord、Shopify、SpaceX、Mistral AI、Hugging Face 较强；对小众金融科技、生物技术或早期公司较弱）。

#### 第 2 层：通过 `sharp` 基于首字母的回退徽标（100% 覆盖范围）

对于未在 `simple-icons` 中找到的公司，生成基于首字母的简洁徽标作为 PNG：

```javascript
async function generateInitialLogo(companyName, outputPath) {
    const initial = companyName.charAt(0).toUpperCase();
    const svg = `
    <svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
        <circle cx="64" cy="64" r="64" fill="#BDBDBD"/>
        <text x="64" y="64" font-family="Arial, Helvetica, sans-serif"
              font-size="56" font-weight="bold" fill="#FFFFFF"
              text-anchor="middle" dominant-baseline="central">${initial}</text>
    </svg>`;
    await sharp(Buffer.from(svg)).png().toFile(outputPath);
}
```

#### 完整管道

```javascript
async function fetchLogo(companyName, outputDir) {
    const fileName = companyName.toLowerCase().replace(/[\s.]+/g, '-') + '.png';
    const outPath = path.join(outputDir, fileName);

    // 第 1 层：尝试 simple-icons
    const icon = findSimpleIcon(companyName);
    if (icon) {
        await simpleIconToPng(icon, outPath);
        return { path: outPath, source: 'simple-icons' };
    }

    // 第 2 层：生成基于首字母的回退徽标
    await generateInitialLogo(companyName, outPath);
    return { path: outPath, source: 'initial-fallback' };
}
```

**徽标指南：**
- 将所有徽标保存到 `/home/claude/logos/[company-name].png`
- 所有徽标为 128×128 PNG，透明背景
- 在幻灯片上，徽标显示为 0.35"–0.5" 高——它们是点缀，而非焦点
- 基于首字母的回退圆圈使用灰色（`BDBDBD`）填充，白色文本——与单色调色板一致
- 切勿随机混合徽标样式——如果大多数公司解析为品牌图标，少数回退应自然地融入

### 第 7 步：生成单页 PPTX

在创建幻灯片之前，阅读 `/mnt/skills/public/pptx/SKILL.md` 和 `/mnt/skills/public/pptx/pptxgenjs.md`。

使用 `pptxgenjs` 创建**单页**PowerPoint。幻灯片应信息密集但视觉清晰——想想"高管仪表盘"，而非"文字墙"。

#### 幻灯片布局

```
┌─────────────────────────────────────────────────────────────┐
│  DEAL FLOW DIGEST（交易流简报）                              │
│  [期间] · [行业]                                [日期]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  $X.XB  │  │  N      │  │  $X.XB  │  │  $X.XB  │       │
│  │ Raised  │  │ Rounds  │  │ Avg Pre │  │ Largest │       │
│  │ 融资额  │  │ 轮次数  │  │ 平均投前│  │ 最大轮次│       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│  KEY TAKEAWAYS（关键要点）                                   │
│  ─────────────────────────────────────────────────          │
│  [Logo] Takeaway 1 text goes here...                        │
│  [Logo] Takeaway 2 text goes here...                        │
│  [Logo] Takeaway 3 text goes here...                        │
│  [Logo] Takeaway 4 text goes here...                        │
│                                                             │
│  TOP DEALS（重要交易）                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │Company│Type │Announced│Closed│Amount│Pre-$│Post-$│Lead│🔗││
│  │───────│─────│─────────│──────│──────│─────│──────│────│──││
│  │ ...   │ ... │  ...    │ ...  │ ...  │ ... │ ...  │... │🔗││
│  └──────────────────────────────────────────────────────────┘│
│                                                             │
│  [Footer: Deal Flow Digest · Sources: S&P Global Capital IQ]│
│  [Footer: AI Disclaimer（AI 免责声明）]                       │
└─────────────────────────────────────────────────────────────┘
```

#### 设计规范

**颜色理念：极简、单色优先。** 幻灯片应感觉像高端金融简报——黑色、白色和灰色主导。颜色**仅**在承载意义的地方使用（例如，向下轮次的红色指示器、突出指标的绿色指示器）或读者自然期望的地方（公司徽标）。切勿将颜色用于纯装饰目的，如背景填充、强调条或渐变效果。

**调色板——单色高管：**
- 主背景：`FFFFFF`（白色）——干净、开阔的幻灯片背景
- 页眉条：`1A1A1A`（近黑色）——标题区域的强对比
- 主文本：`1A1A1A`（近黑色）——所有正文文本、统计数字、要点
- 次要文本：`6B6B6B`（中灰色）——标签、说明、页脚、日期戳
- 边框和分隔线：`D0D0D0`（浅灰色）——微妙的结构线、卡片轮廓、表格边框
- 卡片背景：`F5F5F5`（灰白色/非常浅的灰色）——统计卡片填充、交替表格行
- 链接文本：`2B5797`（柔和蓝色）——表格中的 Capital IQ 交易链接（幻灯片上唯一的蓝色）
- **语义颜色（sparingly）：**
  - 向下轮次或负面信号：`C0392B`（柔和红色）——仅用作小点、标签或单个单词高亮，切勿作为填充或背景
  - 突出正面指标（新独角兽、超大额轮次）：`2E7D32`（柔和绿色）——同样最小化使用：一个点、一个小标签或一个突出显示的数字
  - 如果没有数据点需要颜色指示器，**完全不使用颜色**。完全单色的幻灯片是完全正确的。

**排版：**
- 标题：28–32pt，粗体，白色在近黑色页眉条上
- 统计数字：36–44pt，粗体，近黑色（`1A1A1A`）
- 统计标签：10–12pt，中灰色（`6B6B6B`）
- 要点文本：12–14pt，近黑色，左对齐
- 表格文本：9–11pt，近黑色，次要列为灰色（`6B6B6B`）
- 链接文本：9–10pt，柔和蓝色（`2B5797`）
- 页脚：8pt，中灰色

**统计卡片（顶行）：**
- 4 个关键指标作为大数字标注：总融资额、轮次数、平均投前估值、最大轮次
- 每个在带有 `F5F5F5` 填充和细 `D0D0D0` 边框的卡片中——无阴影、无颜色填充
- 如果某个统计数字令人惊讶或极端（例如，正常量的 3 倍、创纪录的交易），可以在该单个数字旁边放置一个小彩色点或下划线——否则保持完全单色
- 如果投前估值大多未披露，用不同的指标替代（例如，中位轮次规模、新独角兽数量）

**关键要点（中间部分）：**
- 3-5 个单行要点，每个以前缀相关公司徽标（小，约 0.35" 高）
- 如果没有徽标可用，使用**灰色圆圈**，白色公司首字母——而非彩色圆圈
- 左对齐，有足够的间距呼吸
- 向下轮次或负面要点可以使用小红点前缀；否则无颜色
- 在可用时包括估值上下文（例如，"投后估值 50 亿美元"）

**重要交易表（底部部分）：**
- 紧凑表格显示 4-6 笔最重要的交易
- 列：公司、类型（X 轮）、公告（日期）、结束（日期）、金额（百万美元）、投前（百万美元）、投后（百万美元）、领投方、交易链接
- **公告**和**结束**列以 `MMM DD` 格式显示日期（例如，"Jan 15"）。这些列是必需的，必须始终存在。如果日期不可用，显示"—"。
- **交易链接**列包含可点击的"View →"文本，链接到 Capital IQ：
  ```
  https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=<transaction_id>
  ```
  其中 `<transaction_id>` 来自 `get_rounds_of_funding_from_identifiers` 的 `transaction_id`。
- 如果投前或投后估值未披露，在该单元格中显示"—"
- 表头行填充近黑色（`1A1A1A`），白色文本；交替行填充 `F5F5F5` 和 `FFFFFF`
- **在幻灯片上水平居中表格。** 计算表格的总宽度，然后设置 `x` 使其在幻灯片宽度内居中：`x = (slideWidth - tableWidth) / 2`。对于 16:9 布局（13.33" 宽），如果表格为 12" 宽，使用 `x = 0.67`。切勿将表格左对齐到幻灯片边缘。
- 保持紧凑——这是参考，而非焦点
- 表格单元格中无彩色填充。如果交易是向下轮次，可以在金额旁边显示小红文本标签"(↓ down)"——这是表格中唯一允许的颜色。

**交易链接实现（pptxgenjs）：**
在 pptxgenjs 中，超链接使用单元格对象上的 `options.hyperlink` 属性添加到表格单元格：
```javascript
// 带有 Capital IQ 交易链接的表格单元格
{
  text: "View →",
  options: {
    hyperlink: {
      url: `https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=${transactionId}`
    },
    color: "2B5797",
    fontSize: 9,
    fontFace: "Arial"
  }
}
```

**表格居中（pptxgenjs）：**
始终将交易表格在幻灯片上居中。动态计算 x 位置：
```javascript
const SLIDE_W = 13.33; // 16:9 幻灯片宽度（英寸）
const TABLE_W = 12.5;  // 表格总宽度（所有列宽之和）
const TABLE_X = (SLIDE_W - TABLE_W) / 2; // ≈ 0.42"

slide.addTable(tableRows, {
  x: TABLE_X,
  y: tableY,
  w: TABLE_W,
  colW: [1.8, 0.9, 0.9, 0.9, 1.0, 1.1, 1.2, 1.6, 0.7], // 公司、类型、公告、结束、金额、投前、投后、领投、链接
  // ... other options
});
```
根据需要调整 `colW` 值，但始终从 `(SLIDE_W - sum(colW)) / 2` 重新计算 `TABLE_X` 以保持表格居中。

**页脚：**
- 中灰色小文本："Deal Flow Digest · [Period] · Sources: S&P Global Capital IQ · Generated [Date]"

**一般颜色规则（严格执行）：**
- 公司徽标是幻灯片上唯一的"全彩"元素——它们按原样显示。
- 交易链接使用柔和蓝色（`2B5797`）——这是除语义红/绿之外唯一的非单色文本颜色。
- 除徽标和链接外，幻灯片在黑白打印机上打印时应看起来正确。
- 切勿将颜色应用于背景、强调条、装饰形状或部分分隔线。
- 如有疑问，保留灰色。

#### 代码结构

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Deal Flow Digest";

const slide = pres.addSlide();
const SLIDE_W = 13.33; // 16:9 幻灯片宽度（英寸）

// 1. 带有标题和期间的深色页眉条
// 2. 统计卡片行（4 张卡片：总融资额、轮次数、平均投前估值、最大轮次）
// 3. 带有徽标的关键要点部分（包括估值上下文）
// 4. 重要交易表，带有公告、结束、投前、投后列和 Capital IQ 交易链接
//    - 居中表格：x = (SLIDE_W - tableWidth) / 2
// 5. 页脚

pres.writeFile({ fileName: "/home/claude/deal-flow-digest.pptx" });
```

根据 pptxgenjs 陷阱指南，使用工厂函数（而非共享对象）进行阴影和重复样式。

### 第 8 步：QA 幻灯片

遵循 PPTX 技能的 QA 流程：

1. **内容 QA：** `python -m markitdown deal-flow-digest.pptx`——验证所有文本、数字、公司名称、估值数字和交易链接是否正确
2. **视觉 QA：** 转换为图像并检查：
   ```bash
   python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf deal-flow-digest.pptx
   pdftoppm -jpeg -r 200 deal-flow-digest.pdf deal-flow-digest
   ```
   检查重叠元素、文本溢出、对齐问题、低对比度文本、徽标大小问题和交易链接文本是否可见。
3. **链接 QA：** 验证表格中的 Capital IQ URL 是否格式正确，带有正确的交易 ID。
4. **修复并重新验证**——在宣布完成之前至少进行一次修复和验证循环。

### 第 9 步：呈现结果

1. 将最终的 `.pptx` 复制到 `/mnt/user-data/outputs/`
2. 使用 `present_files` 分享幻灯片
3. 提供 2-3 句话的口头摘要：
   - "您的简报涵盖 X 轮融资，总计融资 Y 美元，跨 [行业]。"
   - 强调单笔最重要的交易及其估值
   - 标记任何令人担忧的趋势（向下轮次、估值压缩等）

## 错误处理

### 实体解析失败
- **已知公司的空结果：** 首先检查 `get_info_from_identifiers`——如果失败，尝试 `references/sector-seeds.md` 中的别名或 `company_id`。常见的品牌→法律不匹配：Together AI → "Together Computer, Inc."，Character.ai → "Character Technologies, Inc."，Runway ML → "Runway AI, Inc."。
- **子公司：** DeepMind、GitHub、Instagram、WhatsApp、YouTube、BeReal 等是子公司——它们没有独立的融资轮次。在上下文中将这些注明为"已收购/子公司"，但切勿报告为"无活动"。
- **已倒闭的公司：** Convoy（2023 年 10 月关闭）等公司在 S&P Global 中仍可解析，但永远不会有新活动。`references/sector-seeds.md` 文件标记这些——在纳入公司之前检查它。
- **`get_funding_summary_from_identifiers` 错误或返回零：** 回退到 `get_rounds_of_funding_from_identifiers`——摘要工具较不可靠。切勿依赖摘要工具作为唯一数据源。
- **错误的 `role` 参数：** 如果投资者视角查询返回空，验证使用的是 `company_investing_in_round_of_funding`，而非 `company_raising_funds`（反之亦然）。

### 数据质量问题
- **期间无活动：** 如果某行业本期零融资轮次，在幻灯片上明确注明（"[行业] 本期无交易记录"）——活动缺失本身是信息。
- **稀疏的估值数据：** 如果大多数交易的投前和投后估值未披露，在页脚注释中注明数据限制，并在表格中使用"—"。调整统计卡片以显示不同的指标（例如，中位轮次规模），而非平均投前估值。
- **徽标检索失败：** `simple-icons` npm 包为典型交易流公司提供约 43% 的覆盖范围。对于其余公司，使用 `sharp` 生成的基于首字母的回退徽标。保持一致的图标样式——切勿混合随机方法。如果 `simple-icons` 或 `sharp` 安装失败，回退到基于 pptxgenjs 形状的首字母（灰色椭圆 + 白色文本叠加），无需外部依赖。
- **一张幻灯片上的交易过多：** 如果有超过 6 笔重要交易，在表格中显示前 6 笔，并添加脚注："+N 笔额外交易未显示"。按交易规模优先排序。
- **大型群体：** 对于 100+ 家公司的多行业简报，以 15-20 家为一组批量处理所有 API 调用。优先深度关注重要交易，而非次要交易的完整性。
- **过时的种子：** 如果竞争对手扩展对某行业返回很少的结果，种子公司可能太小众。通过添加 2-3 个更知名的名称并重新扩展来扩大。
- **无效的交易 ID 链接：** 如果来自融资工具的 `transaction_id` 未生成有效的 Capital IQ URL，省略该行的链接单元格，而非包含损坏的链接。

## 示例提示

- "Give me a weekly deal flow digest for AI and fintech"（给我 AI 和金融科技的每周交易流简报）
- "Summarize this week's funding in biotech"（总结本周生物技术的融资）
- "Deal roundup for my coverage — cybersecurity, cloud infrastructure, and dev tools — last 2 weeks"（我覆盖范围的交易汇总——网络安全、云基础设施和开发者工具——过去 2 周）
- "What happened in venture this week across all sectors I follow?"（本周我关注的所有行业中风险投资发生了什么？）
- "Quick deal flow slide for climate tech this month"（本月气候科技的快速交易流幻灯片）
