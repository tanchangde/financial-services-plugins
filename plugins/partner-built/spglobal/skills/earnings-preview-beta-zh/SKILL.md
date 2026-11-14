---
name: earnings-preview-single-zh
description: 为单家公司生成简洁的 4-5 页股票研究财报预览。分析最新的财报电话会议记录、竞争对手格局、估值和近期新闻，生成专业的 HTML 报告。
---

# 单家公司财报预览 (Single-Company Earnings Preview)

为单家公司生成简洁、专业的股票研究财报预览。输出为独立的 HTML 文件，目标为打印后 4-5 页。报告包含密集的数据和图表，叙述简洁扼要，直切要点。

**数据来源（零例外）：** 唯一允许的数据来源是 **Kensho Grounding MCP** (`search`) 和 **S&P Global MCP** (`kfinance`)。绝对不允许使用其他任何工具、数据源或网络访问。具体而言：
- 禁止使用 `WebSearch`、`WebFetch`、`web_search`、`brave_search`、`google_search` 或任何通用网络/互联网搜索工具——即使 Kensho 响应缓慢、无结果或暂时不可用。
- 禁止使用任何浏览器、URL 获取或网络爬虫工具。
- 如果 Kensho Grounding 对某个查询无结果，尝试重新措辞查询或在报告中标注"数据不可用"。**切勿将网络搜索作为备选方案。**
- 报告中的每条信息必须可追溯至 `kfinance` MCP 函数调用或 Kensho `search` 调用。如果无法追溯到这两个来源之一，则不得出现在报告中。

**关键规则：** 在撰写报告的任何部分之前，必须完成所有研究和数据收集（第 1-5 阶段）。

**中间文件规则：** 来自 MCP 工具调用的所有原始数据必须在**每次工具调用返回后立即**写入 `/tmp/earnings-preview/` 目录中的文件——在进行下一次调用之前。这可以防止数据被上下文窗口压缩。请勿仅将数据保存在内存中。在第 1 阶段开始时，运行 `mkdir -p /tmp/earnings-preview` 创建目录。**在生成 HTML 报告（第 7 阶段）之前，必须使用 `cat` 命令将所有中间文件读回上下文中。文件——而非你对早期对话的记忆——是报告中每个数字、引用和来源 URL 的唯一真实来源。如果跳过读取文件，报告将出现错误。**

**财季规则：** 切勿从日历报告日期推断财季。许多公司的财年并非标准日历年度（例如，沃尔玛的财年于 1 月 31 日结束，因此 2026 年 2 月的报告涵盖 Q4 FY2026，而非 Q4 2025 或 Q1 2026）。务必使用 `get_next_earnings_from_identifiers` 或 `get_earnings_from_identifiers` 返回的财报电话会议名称中所述的财季和财年（例如，"Walmart Q4 FY2026 Earnings Call" 表示季度为 Q4 FY2026）。在报告标题、表头、表格和所有引用中逐字使用该名称。如果会议名称模糊，可交叉参考 `get_financial_line_item_from_identifiers` 的期间标签。

**长度规则：** 报告必须简洁。目标打印后 4-5 页。切勿撰写多段落的长篇叙述。使用紧凑、简练的要点。每句话都必须有其存在的价值。如果可以用更少的词表达，就这么做。

**逐字引用规则：** 当在 `<blockquote>` 标签中引用管理层发言时，文本必须从财报电话会议记录中**逐字**复制——一字不差，包括填充词和不完整的句子。切勿改写、重组、组合来自财报电话会议记录不同部分的句子或"润色"引用。如果在财报电话会议记录中找不到确切的短语，切勿将其作为直接引用呈现。相反，用自己的叙述声音进行转述，不使用块引用格式（例如，"管理层指出数据中心需求仍然强劲"）。每个块引用必须是可针对财报电话会议记录验证的逐字复制摘录。

**计算完整性规则：** 对于任何多步骤计算（从年度指引推导隐含季度数据、LTM 市盈率、同比（YoY）增长率、分部同比变化），明确写出每个步骤并在使用于下一步之前验证中间结果。如果声明 A + B + C = X，在使用 X 进行后续公式计算之前，验证 X 在算术上是正确的。如有疑问，从原始数据重新计算，而非重用先前计算的中间值。

**比率命名规则：** 所有估值比率必须明确标注为 **LTM**（过去 12 个月）或 **NTM**（未来 12 个月）。切勿使用"trailing"或"forward"——始终使用 LTM 或 NTM。LTM 比率使用最近 4 个已报告季度的总和。NTM 比率使用 **`get_consensus_estimates_from_identifiers` 返回的未来 4 个季度共识平均每股收益（EPS）估计值的总和**——而非单个年度数字。必须在竞争对手比较表中计算并显示 LTM 和 NTM 市盈率。

**超链接规则（严格执行）：** 报告中的每个声明——数字和非数字——必须包裹在 `<a href="#ref-N" class="data-ref">` 超链接中，指向附录中的相应条目。**这不是可选项。报告中的每个数字都必须是可点击的链接。** 这包括：收入数字、每股收益（EPS）、利润率、增长率、市值、市盈率（P/E）比率、股票回报、目标价、分部收入以及任何其他财务指标。还包括来自财报电话会议记录或 Kensho 搜索的定性声明。如果作为事实陈述，则必须链接到来源。为每个唯一声明分配连续的引用 ID（`ref-1`、`ref-2` 等）。超链接样式微妙——深蓝色，无下划线，悬停时虚线下划线。**切勿在报告正文中书写任何数字而不将其包裹在 `<a>` 标签中。** 示例：写 `<a href="#ref-1" class="data-ref">$152.3B</a>`，切勿写 `$152.3B` 作为纯文本。

---

## 第 1 阶段：公司简介与设置

1. 从 `$ARGUMENTS` 解析单家公司股票代码（去除空格）。
2. 运行 `mkdir -p /tmp/earnings-preview` 创建工作目录。
3. 调用 `get_latest()` 建立当前报告期上下文。
4. 调用 `get_info_from_identifiers`——记录市值、行业。
5. 调用 `get_company_summary_from_identifiers`——记录业务描述。
6. 调用 `get_next_earnings_from_identifiers`——记录即将到来的财报发布日期和财季名称。

**立即写入** `/tmp/earnings-preview/company-info.txt`：
```
TICKER: [ticker]
COMPANY: [full name]
INDUSTRY: [industry]
MARKET_CAP: [value] (as of [date])
NEXT_EARNINGS_DATE: [date]
NEXT_EARNINGS_QUARTER: [Q# FY#### exactly as returned by API]
BUSINESS_DESCRIPTION: [2-3 sentence summary]
```

---

## 第 2 阶段：财报电话会议记录分析（强制——在撰写前完成）

1. 调用 `get_latest_earnings_from_identifiers` 获取最近已完成的财报电话会议的 `key_dev_id`。
2. 调用 `get_transcript_from_key_dev_id` 获取该财报电话会议记录。
3. **立即写入** `/tmp/earnings-preview/transcript-extracts.txt`，包含以下部分。在上下文中仍有财报电话会议记录时写入此文件——切勿等待：

```
TRANSCRIPT_SOURCE: [Call Name, e.g., "Q3 2025 Earnings Call"]
KEY_DEV_ID: [key_dev_id]
CALL_DATE: [date]
FISCAL_QUARTER: [Q# FY####]

=== VERBATIM QUOTES (copy-paste exactly — do NOT paraphrase) ===
QUOTE_1: "[exact text from transcript]"
SPEAKER_1: [Name], [Title]
CONTEXT_1: [1 sentence on where this appeared — prepared remarks or Q&A]

QUOTE_2: "[exact text from transcript]"
SPEAKER_2: [Name], [Title]
CONTEXT_2: [context]

QUOTE_3: "[exact text from transcript]"
SPEAKER_3: [Name], [Title]
CONTEXT_3: [context]

QUOTE_4: "[exact text from transcript]"
SPEAKER_4: [Name], [Title]
CONTEXT_4: [context]

=== GUIDANCE (quantitative only) ===
- [metric]: [range or point estimate as stated by management]
- [metric]: [range or point estimate]

=== KEY DRIVERS ===
- [driver 1 with supporting data point]
- [driver 2 with supporting data point]
- [driver 3 with supporting data point]

=== HEADWINDS & RISKS ===
- [risk 1 with quantification if available]
- [risk 2]

=== ANALYST Q&A THEMES ===
- [theme 1: what analysts pushed on]
- [theme 2]
- [theme 3]

=== SYNTHESIS: THEMES TO WATCH NEXT QUARTER ===
- [theme 1]
- [theme 2]
- [theme 3]
```

---

## 第 3 阶段：竞争对手分析

1. 调用 `get_competitors_from_identifiers`，参数 `competitor_source="all"`。
2. 选择**5-7 家最相关的公开竞争对手**。
3. 对于该公司和所有选定的竞争对手，收集：
   - `get_prices_from_identifiers`，参数 `periodicity="day"`，过去 12 个月
   - `get_financial_line_item_from_identifiers` 获取 `diluted_eps`，`period_type="quarterly"`，`num_periods=8`
   - `get_capitalization_from_identifiers`，参数 `capitalization="market_cap"`（最新）
   - `get_consensus_estimates_from_identifiers`，参数 `period_type="quarterly"`，`num_periods_forward=4`——这返回未来 4 个季度的共识平均每股收益（EPS）估计值，用于计算 NTM 每股收益

**每次工具调用返回后，立即将原始数据附加到相应的中间文件：**

**写入** `/tmp/earnings-preview/prices.csv`——每行一个（股票代码，日期，收盘价）。包含 `source` 列，带有确切的 MCP 函数调用。先写入标的公司的价格，然后在获取时写入每个竞争对手的价格：
```
ticker,date,close,source
D,2025-02-19,55.67,get_prices_from_identifiers(identifier='D',periodicity='day')
D,2025-02-20,55.82,get_prices_from_identifiers(identifier='D',periodicity='day')
...
DUK,2025-02-19,111.79,get_prices_from_identifiers(identifier='DUK',periodicity='day')
...
```
注意：来自单次调用的所有行的 `source` 值相同——在每一行上写入，以便始终可用。

**写入** `/tmp/earnings-preview/peer-eps.csv`——每行一个（股票代码，期间，每股收益）。每次 `diluted_eps` 调用后立即写入：
```
ticker,period,diluted_eps,source
D,Q4 2024,1.09,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
D,Q1 2025,-0.11,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
...
DUK,Q4 2024,1.52,get_financial_line_item_from_identifiers(identifier='DUK',line_item='diluted_eps',period_type='quarterly')
...
```

**写入** `/tmp/earnings-preview/peer-market-caps.csv`——每个股票代码一行。每次 `market_cap` 调用后立即写入：
```
ticker,market_cap,retrieval_date,source
D,55900000000,2026-02-19,get_capitalization_from_identifiers(identifier='D',capitalization='market_cap')
DUK,98300000000,2026-02-19,get_capitalization_from_identifiers(identifier='DUK',capitalization='market_cap')
...
```

**写入** `/tmp/earnings-preview/consensus-eps.csv`——每行一个（股票代码，期间，共识平均每股收益）。每次 `get_consensus_estimates_from_identifiers` 调用后立即写入：
```
ticker,period,consensus_mean_eps,num_estimates,source
D,Q4 2025,0.88,12,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q1 2026,0.72,10,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q2 2026,0.91,9,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q3 2026,1.05,8,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
DUK,Q4 2025,1.48,14,get_consensus_estimates_from_identifiers(identifier='DUK',period_type='quarterly',num_periods_forward=4)
...
```

4. **暂时不要计算市盈率或回报。** 原始数据现在在磁盘上。计算在第 6 阶段（验证）中进行，从这些文件读取。

**日期一致性规则（股票回报）：** 计算比较股票回报（年初至今 YTD %、1 年 %、30 天 %、90 天 %）时，所有股票代码必须使用**完全相同的开始和结束日期**。在将所有价格数据写入 `prices.csv` 后，识别所有股票代码数据中出现的第一个交易日期，并将其用作共同基准日期。切勿对不同股票代码使用不同的基准日期（例如，标的公司使用 2 月 19 日，同行使用 2 月 28 日）。如果某个股票代码的数据开始日期晚于其他股票，则对所有计算使用第一个重叠日期。在附录中为每个回报计算声明共同基准日期。

**市盈率货币规则（LTM 市盈率）：** 计算每家公司的 LTM 市盈率时，使用该公司来自 `peer-eps.csv` 的**最近 4 个已报告季度**——而非对所有公司应用固定的日历窗口。如果某同行已报告 Q4 2025 而标的公司仅报告至 Q3 2025，则同行的 LTM 每股收益应包含 Q4 2025。检查每家公司的最新报告期，并对每家公司使用 4 个最近的期间。在附录中注明每个市盈率计算使用了哪 4 个季度。

**市值日期标记：** 报告市值时，使用 `peer-market-caps.csv` 中的 `retrieval_date`。如果与报告日期不同，在附录中注明。

---

## 第 4 阶段：新闻、预期与行业情报（通过 Kensho Grounding）

为以下**每个**类别运行这些 `search` 查询。切勿跳过任何类别。

**关键——捕获来源 URL：** 每个 Kensho `search` 结果都包含底层文章、报告或数据页面的**来源 URL**。必须将 URL 与每个发现一起记录。

**每次搜索调用后，立即将结果附加到** `/tmp/earnings-preview/kensho-findings.txt`，使用以下格式。切勿等到所有搜索完成——每次调用后写入：

```
=== SEARCH: "[query used]" ===
DATE_RUN: [today's date]
CATEGORY: [estimates|analyst_ratings|risks|news|sector]

FINDING_1: [key finding or excerpt]
URL_1: [source URL from search result]
SOURCE_1: [publication name, date if available]

FINDING_2: [key finding or excerpt]
URL_2: [source URL]
SOURCE_2: [publication name, date]

[...continue for all relevant results from this search...]
```

**盈利预期与分析师情绪：**
1. `search` 查询 "[TICKER] earnings estimates consensus EPS revenue upcoming quarter"
   - 记录：共识每股收益（EPS）、共识收入、过去 90 天的预期修正方向。
   - **立即附加到 kensho-findings.txt。**
2. `search` 查询 "[TICKER] analyst ratings price target upgrades downgrades"
   - 记录：最近的升级/降级、目标价范围、多头/空头论点摘要。
   - **立即附加到 kensho-findings.txt。**
3. `search` 查询 "[TICKER] risks bear case concerns investors"
   - 记录：关键辩论、空头论点、即将发布的财报的波动因素。
   - **立即附加到 kensho-findings.txt。**

**近期新闻（强制——切勿跳过）：**
4. `search` 查询 "[TICKER] [company name] recent news developments"
   - 记录：过去 60 天内的重要新闻——并购（M&A）、产品发布、高管变动、监管行动、合作伙伴关系、法律发展、关税或任何可能影响即将发布的财报或前瞻性指引的事件。
   - 对于每个项目，注明日期、标题、潜在的财报影响。
   - **立即附加到 kensho-findings.txt。**

**行业背景：**
5. `search` 查询 "[company industry/sector] sector outlook trends"
   - 记录：行业层面的顺风/逆风、宏观数据、竞争动态。
   - **立即附加到 kensho-findings.txt。**

---

## 第 5 阶段：财务数据收集

**季度财务数据（最近 8 个季度）：**
`get_financial_line_item_from_identifiers`，参数 `period_type="quarterly"`，`num_periods=8`，获取：
`revenue`、`gross_profit`、`operating_income`、`ebitda`、`net_income`、`diluted_eps`

**每次细目调用返回后，立即附加到** `/tmp/earnings-preview/financials.csv`。按照工具返回的原始值写入——切勿四舍五入或转换。包含 `source` 列，带有确切的 MCP 函数调用和参数：
```
ticker,period,line_item,value,source
D,Q4 2024,revenue,3941000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q1 2025,revenue,3400000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q2 2025,revenue,4076000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q3 2025,revenue,3810000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q4 2024,diluted_eps,1.09,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
D,Q1 2025,diluted_eps,-0.11,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
...
```

**暂时不要计算利润率或增长率。** 仅写入原始数据。计算在第 6 阶段进行。

**分部数据：**
- `get_segments_from_identifiers`，参数 `segment_type="business"`，`period_type="quarterly"`，`num_periods=8`
- 你需要 8 个季度（而非 4 个），以便有去年同期的季度进行同比（y/y）比较。要计算 Q3 2025 的同比，需要 Q3 2024——这是第 5 个季度前的数据。**如果 API 响应中不提供上年同期的分部数据，切勿估计或编造。在报告中标注"同比不可用"。**

**立即写入** `/tmp/earnings-preview/segments.csv`：
```
ticker,period,segment_name,revenue,source
D,Q3 2024,Dominion Energy Virginia,2762000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2024,Dominion Energy South Carolina,848000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2024,Contracted Energy,260000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Dominion Energy Virginia,3311000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Dominion Energy South Carolina,945000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Contracted Energy,297000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
...
```

**财报历史（用于股票图表注释）：**
- `get_earnings_from_identifiers`——收集 12 个月价格窗口内的过往财报发布日期。
- **立即写入** `/tmp/earnings-preview/earnings-dates.csv`：
```
ticker,earnings_date,call_name,source
D,2025-05-02,Q1 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
D,2025-08-01,Q2 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
D,2025-10-31,Q3 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
...
```

---

## 第 6 阶段：验证与计算（强制——切勿跳过）

在生成报告之前，读回所有中间文件并从干净的数据执行计算。此阶段通过从文件而非压缩的对话上下文工作来确保数据完整性。

1. **使用 bash `cat` 命令读取所有中间文件**：
   - `cat /tmp/earnings-preview/company-info.txt`
   - `cat /tmp/earnings-preview/transcript-extracts.txt`
   - `cat /tmp/earnings-preview/financials.csv`
   - `cat /tmp/earnings-preview/segments.csv`
   - `cat /tmp/earnings-preview/prices.csv`
   - `cat /tmp/earnings-preview/peer-eps.csv`
   - `cat /tmp/earnings-preview/peer-market-caps.csv`
   - `cat /tmp/earnings-preview/consensus-eps.csv`
   - `cat /tmp/earnings-preview/kensho-findings.txt`
   - `cat /tmp/earnings-preview/earnings-dates.csv`

2. **从原始数据计算衍生指标**，现在上下文中已有：
   - 毛利率 % = gross_profit / revenue（每季度）
   - 营业利润率 % = operating_income / revenue（每季度）
   - 收入同比增长 % = (当前季度收入 - 上年同期季度收入) / 上年同期季度收入
   - 每股收益同比增长 % = 相同逻辑；如果基数为负，使用"n.m."（无意义）
   - 分部同比增长 % = 按名称匹配分部到上年同期季度；如果缺失，注明"同比不可用"
   - 每家公司的 LTM 市盈率 = 最新价格 / 最近 4 个季度每股收益总和（使用 `peer-eps.csv` 检查每个股票代码可用哪 4 个季度）
   - 每家公司的 NTM 市盈率 = 最新价格 / NTM 每股收益，其中 **NTM 每股收益 = `consensus-eps.csv` 中未来 4 个季度共识平均每股收益估计值的总和**。将每个股票代码的 4 个季度的 consensus_mean_eps 值相加。如果某同行的未来季度少于 4 个，将 NTM 市盈率标记为"n/a"。在附录中注明加总了哪 4 个季度。
   - 股票回报（年初至今 YTD、1 年、30 天、90 天）= 在 `prices.csv` 中找到所有股票代码的**共同第一个日期**，然后从该日期计算回报

3. **交叉检查**：
   - 验证每个分部同比在 `segments.csv` 中是否有实际的上年同期行。如果没有，标记"同比不可用"。
   - 验证所有股票回报基准日期在所有股票代码中相同。
   - 通过重新加总组件验证任何多步骤计算（例如，LTM 每股收益总和与 4 个季度值匹配）。
   - 验证 `transcript-extracts.txt` 中的所有逐字引用是精确复制粘贴（而非转述）。

4. **写入** `/tmp/earnings-preview/calculations.csv`，包含所有衍生值：
```
ticker,metric,value,formula,components
D,gross_margin_Q3_2025,32.5%,gross_profit/revenue,"gross_profit=1238100000,revenue=3810000000"
D,revenue_yoy_Q3_2025,+9.3%,(Q3_2025-Q3_2024)/Q3_2024,"Q3_2025=3810000000,Q3_2024=3486000000"
D,ltm_pe,24.2x,price/ltm_eps,"price=65.46,ltm_eps=2.70,quarters=Q4_2024+Q1_2025+Q2_2025+Q3_2025"
D,ntm_pe,18.5x,price/ntm_eps,"price=65.46,ntm_eps=3.56,quarters=Q4_2025(0.88)+Q1_2026(0.72)+Q2_2026(0.91)+Q3_2026(1.05),source=get_consensus_estimates_from_identifiers"
D,yoy_return,+17.6%,(end-start)/start,"end=65.46,start=55.67,base_date=2025-02-19"
DUK,yoy_return,+13.0%,(end-start)/start,"end=126.32,start=111.79,base_date=2025-02-19"
...
```

此文件成为报告中所有数字的唯一真实来源。

---

## 第 7 阶段：生成 HTML 报告

**停止——在撰写任何 HTML 之前，必须读取所有中间文件。这是阻塞性先决条件。**

这不是可选项。必须将以下每个 `cat` 命令作为**单独的 bash 工具调用**运行（不合并）。这确保每个文件的内容单独加载并在对话中可见。切勿将它们合并到单个命令中。切勿跳过任何文件。

**逐个运行这些命令，每个作为其自己的 bash 调用**：

1. `cat /tmp/earnings-preview/company-info.txt`
2. `cat /tmp/earnings-preview/transcript-extracts.txt`
3. `cat /tmp/earnings-preview/financials.csv`
4. `cat /tmp/earnings-preview/segments.csv`
5. `cat /tmp/earnings-preview/prices.csv`
6. `cat /tmp/earnings-preview/peer-eps.csv`
7. `cat /tmp/earnings-preview/peer-market-caps.csv`
8. `cat /tmp/earnings-preview/consensus-eps.csv`
9. `cat /tmp/earnings-preview/kensho-findings.txt`
10. `cat /tmp/earnings-preview/earnings-dates.csv`
11. `cat /tmp/earnings-preview/calculations.csv`

**读取所有文件后，必须向用户打印摘要消息**，列出每个文件及其状态。完全使用以下格式：

```
--- DATA FILE VERIFICATION ---
1. company-info.txt        ✓ loaded ([N] lines)
2. transcript-extracts.txt ✓ loaded ([N] lines)
3. financials.csv          ✓ loaded ([N] rows)
4. segments.csv            ✓ loaded ([N] rows)
5. prices.csv              ✓ loaded ([N] rows)
6. peer-eps.csv            ✓ loaded ([N] rows)
7. peer-market-caps.csv    ✓ loaded ([N] rows)
8. consensus-eps.csv       ✓ loaded ([N] rows)
9. kensho-findings.txt     ✓ loaded ([N] lines)
10. earnings-dates.csv     ✓ loaded ([N] rows)
11. calculations.csv       ✓ loaded ([N] rows)

All intermediate data files loaded successfully.
Generating report using file data as the single source of truth.
---
```

如果任何文件缺失或为空，停止并告知用户哪个文件失败。切勿使用缺失数据生成报告。

**HTML 报告中的每个数字、引用、来源 URL 和 MCP 函数调用引用必须来自这些文件——而非来自你对早期对话回合的记忆。** 文件是唯一真实来源。早期的对话上下文可能已被压缩或总结，如果依赖将出现错误。如果数据点不在文件中，则不应出现在报告中。

请参阅 [report-template.md](report-template.md) 获取完整的 HTML 模板、CSS 和 Chart.js 配置。

**强制——使用模板辅助函数进行图表：**
report-template.md 提供预构建、已调试的 Chart.js 辅助函数。必须使用这些确切的函数创建图表。切勿编写自定义内联 Chart.js 代码。辅助函数是：
- `createRevEpsChart(canvasId, labels, revenueData, epsData, revLabel)` —— 用于图 1
- `createMarginChart(canvasId, labels, grossMargins, opMargins)` —— 用于图 2
- `createRevGrowthChart(canvasId, labels, growthData)` —— 用于图 3
- `createAnnotatedPriceChart(canvasId, labels, prices, earningsDates, ticker)` —— 用于图 5
- `createCompPerfChart(canvasId, labels, datasets)` —— 用于图 6
- `createPEChart(canvasId, companies)` —— 用于图 7

每次图表调用必须在其自己的 `<script>` 标签中，包装在 try...catch 块中：
```html
<script>
try {
  createRevEpsChart('chart-rev-eps', [...], [...], [...], 'Revenue ($B)');
} catch(e) { console.error('Figure 1 error:', e); }
</script>
<script>
try {
  createMarginChart('chart-margins', [...], [...], [...]);
} catch(e) { console.error('Figure 2 error:', e); }
</script>
```

### 报告结构（共 4-5 页）

报告分为两半：**叙述**（第 1-2 页）和**图表**（第 3-5 页）。保持这些紧密集成。

---

**AI 免责声明（强制——必须出现在 3 个位置）：**
必须在报告 HTML 中包含以下免责声明文本。这不是可选项——没有它的报告是不完整的：

> **"Analysis is AI-generated — please confirm all outputs"（分析由 AI 生成——请确认所有输出）**

它必须准确出现在以下 3 个位置：
1. **页眉横幅**——在封面页眉之前立即，作为居中的黄色横幅：`<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
2. **页脚**——在 page-footer div 内，作为醒目的黄色横幅：`<div class="footer-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
3. **附录**——作为附录部分的第一行，在表格之前：`<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`

---

**第 1 页：封面与论点**

- **AI 免责声明横幅**（黄色，居中——见上方 AI 免责声明规则）
- **页眉**：公司名称（股票代码）| 行业 | 报告日期
- **标题**：主题性，特定于该季度（例如，"Walmart Inc. (WMT) Q4 FY2026 Earnings Preview: Holiday Harvest — Can Furner's First Print Confirm the $1T Thesis?"）
- **执行论点**（2-3 个短段落，含要点）：
  - 我们期望从本次财报发布中获得的内容，1-2 句话
  - 4-6 个要点涵盖：我们的每股收益（EPS）估计与共识预期、指引预期、关键观察指标、什么会推动股价、关键辩论
  - 保持直接和有观点——采取立场，不要对所有事情都模棱两可
- **来自最近财报电话会议的关键管理层引用**在叙述中相关位置交织。切勿将这些放在单独的标题下。将它们自然地整合为论点的支撑证据。格式为缩进块引用。

---

**第 2 页：预期、主题与新闻**

- **共识预期表**（单个表格，标记为图表）：
  - 列：指标 | 共识 | 我们的估计 | 同比变化
  - 行：收入、每股收益（EPS）、毛利率、营业利润和 2-3 个重要的公司特定关键绩效指标（KPI）（例如，可比销售额、电子商务增长、会员收入——无论华尔街对这家公司关心什么）
  - **颜色编码是机械性的：** 如果同比变化值为负，使用 `class="neg"`（红色）。如果为正，使用 `class="pos"`（绿色）。如果为零或 N/A，使用 `class="neutral"`。数字的符号决定类别——切勿根据解释覆盖。-1.1% 总是红色，即使降幅很小。
  - 这是唯一的指引/预期部分。切勿在其他地方重复预期数据。

- **除标题每股收益外的关键指标**（项目符号列表，3-5 项）：
  - 决定本季度好坏的具体指标，超出每股收益数字
  - 对于每个指标：指标是什么、共识/管理层预期、为何重要
  - 具体说明："Walmart Connect 广告收入增长（共识约 30% 同比，3 季度为 33%）"

- **观察主题**（3-5 个要点）：
  - 即将发布的财报的前瞻性项目
  - 管理层需要交付的内容、可能超预期的内容、空头关注的重点
  - 每个主题：最多 1-2 句话

- **近期新闻与发展**（3-5 个要点）：
  - 过去 60 天内的重要新闻，每行一个
  - 日期 + 标题 + 简要影响评估
  - 仅包括可能影响即将发布的财报或指引的项目

---

**第 3-5 页：图表（所有图表和表格）**

所有图表按顺序编号。每个图表都有标题和来源行。

- **图 1：季度收入与稀释每股收益**——柱状/折线组合图，8 个季度
- **图 2：利润率趋势（毛利率和营业利润率 %）**——双折线图，8 个季度
- **图 3：收入同比增长 %**——带有绿色/红色条件着色的柱状图。**仅包括当前和上年同期数据都存在的季度**（通常是从获取的 8 个季度中最近的 4 个）。切勿包括无法计算同比的季度——图表应有 4 个柱，而非 8 个。
- **图 4：业务分部收入**——表格：分部 | 最新季度收入（百万美元）| 占总收入 % | 同比变化
- **图 5：1 年股票价格与财报日期**——价格线，在财报日期处有垂直注释线，标注季度和 1 日后财报走势
- **图 6：股票表现与竞争对手比较（指数化为 100）**——多线图，标的公司为粗实线，竞争对手为较细的虚线
- **图 7：LTM 市盈率与竞争对手比较**——水平条形图，标的公司以深蓝色突出显示
- **图 8：竞争对手比较表**——股票代码 | 公司 | 市值 | LTM 市盈率 | NTM 市盈率 | 年初至今 % | 1 年 %

---

**附录：数据来源与计算（强制——切勿跳过或缩写）**

附录必须以 AI 免责声明横幅开始：`<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`

报告的最后一页必须包括一个附录表，记录报告中引用的**每个声明**——数字和非数字。**报告中出现的每个数字必须在附录中有对应的行，报告正文中的每个这样的数字必须是可点击的 `<a href="#ref-N">` 超链接，滚动到其附录行。** 如果报告中的数字没有超链接到附录，报告是不完整的。

- **表格列**：引用编号 | 事实 | 值 | 来源与推导
- **引用编号**：与报告正文中的超链接锚点匹配的连续 ID（`ref-1`、`ref-2` 等）。每行有一个 `id="ref-N"` 属性，以便超链接滚动到它。
- **事实**：人类可读的标签（例如，"Q3 FY2026 收入"、"LTM 市盈率 — WMT"、"管理层 flagged 关税逆风"、"Barclays 升级为增持"）
- **值**：报告中显示的精确数字（例如，"$152.3B"、"24.5%"、"28.1x"）。对于非数字事实，留空或写"N/A"。
- **来源与推导**：这是关键列。**每行必须有具体、详细的来源——而非只是标签。** 严格遵守以下规则：

  **对于来自 S&P Capital IQ（标普全球）的原始财务数据（收入、每股收益、毛利、营业利润、净利润、息税折旧摊销前利润（EBITDA）、价格、市值等）：**
  - 声明使用的 MCP 函数及其关键参数。格式：`S&P Capital IQ — [function_name](identifier='[TICKER]', line_item='[item]', period_type='[type]', period='[Q# FY####]')`
  - 示例：
    - `S&P Capital IQ — get_financial_line_item_from_identifiers(identifier='WMT', line_item='revenue', period_type='quarterly', period='Q3 FY2026')`
    - `S&P Capital IQ — get_financial_line_item_from_identifiers(identifier='WMT', line_item='diluted_eps', period_type='quarterly', period='Q3 FY2026')`
    - `S&P Capital IQ — get_prices_from_identifiers(identifier='WMT', periodicity='day')`
    - `S&P Capital IQ — get_capitalization_from_identifiers(identifier='WMT', capitalization='market_cap')`
  - **切勿只写"S&P Capital IQ"而无详细信息。** 读者必须知道哪个工具调用的哪个数据点产生了这个数字。

  **对于计算值（利润率、增长率、市盈率、回报、同比变化）：**
  - 显示完整公式，带有**超链接组件**——每个组件必须是 `<a href="#ref-N">` 链接回该原始数据点的附录行。这至关重要：读者必须能够从计算值点击到其每个输入。
  - 示例：`毛利率 = <a href='#ref-5'>毛利 $37.2B</a> / <a href='#ref-1'>收入 $152.3B</a> = 24.4%。来源：S&P Capital IQ（计算）`
  - 示例：`LTM 市盈率 = <a href='#ref-20'>价格 $172.35</a> / (<a href='#ref-8'>Q1 每股收益 $1.47</a> + <a href='#ref-9'>Q2 每股收益 $1.84</a> + <a href='#ref-10'>Q3 每股收益 $1.53</a> + <a href='#ref-11'>Q4 每股收益 $1.80</a>) = $172.35 / $6.64 = 25.9x`
  - 示例：`收入同比增长 = (<a href='#ref-12'>Q3 FY26 收入 $165.8B</a> - <a href='#ref-3'>Q3 FY25 收入 $160.8B</a>) / <a href='#ref-3'>Q3 FY25 收入 $160.8B</a> = +3.1%`
  - **公式的每个组件必须是可点击的超链接。** 切勿用纯文本数字书写公式。

  **对于财报电话会议记录来源的声明（引用、管理层评论、指引）：**
  - 从财报电话会议记录中写入**逐字摘录句子**。
  - 通过其完整名称和用于获取它的 `key_dev_id` 引用财报电话会议记录。
  - 格式：`"[verbatim quote]" — [Speaker], [Title]. Source: [Q# FY#### Earnings Call Transcript] (key_dev_id: [ID])`
  - 示例：`"We expect comp sales growth of 3-4% in Q4" — CEO John Furner. Source: Q3 FY2026 Earnings Call Transcript (key_dev_id: 12345678)`

  **对于 Kensho Grounding 搜索结果（新闻、分析师评级、共识预期）：**
  - 写入搜索结果中的关键发现或摘录。
  - **强制：包括 Kensho `search` 工具返回的来源 URL**，作为可点击的 `<a href="[URL]" target="_blank">` 超链接。这是最重要的部分——读者必须能够点击到原始来源。
  - 格式：`"[finding/excerpt]" — <a href="[URL]" target="_blank">[Source Title or Publication]</a>. Query: search("[query used]")`
  - 示例：`"Barclays upgraded WMT to Overweight with $210 price target on Jan 15, 2026." — <a href="https://www.investing.com/news/barclays-upgrades-wmt" target="_blank">Investing.com, Jan 15 2026</a>. Query: search("WMT analyst ratings price target upgrades downgrades")`
  - 如果某个结果未返回 URL，写"Source URL not available"，并仍包括搜索查询。

**完整性检查：** 在最终确定报告之前，扫描报告正文中的每个数字。如果任何数字未包裹在 `<a href="#ref-N" class="data-ref">` 中，修复它。如果任何附录行的来源与推导只是裸标签如"S&P Capital IQ"而无函数调用详细信息，修复它。如果任何计算值的公式缺乏超链接组件，修复它。如果任何 Kensho 来源的声明缺乏来源 URL，修复它。

按部分对附录行进行分组（财务数据、估值、预期与共识、财报电话会议记录声明、新闻与分析师评论、股票表现），带有子标题。使用较小的字体大小（10-11px）。

---

## 第 8 阶段：输出

1. 将完整的 HTML 文件写入当前工作目录中的 `earnings-preview-[TICKER]-YYYY-MM-DD.html`。
2. 在浏览器中打开它：`open earnings-preview-[TICKER]-YYYY-MM-DD.html`
3. 告知用户文件已创建并总结关键发现。

---

## 撰写指南

- **无表情符号**：切勿在报告中的任何地方使用表情符号。这是专业研究文件。
- **简洁**：目标打印后 4-5 页。每句话都必须有分量。尽可能使用要点，而非段落。如果某个部分感觉过长，删减它。
- **数字具体**："$52.4B 收入，同比增长 5.2%"，而非"强劲的收入增长"。
- **采取观点**：这是财报预览，而非总结。陈述你的期望、重要内容和原因。有观点，但用数据支持。
- **无标题的管理层引用**：将 3-4 个来自最近财报电话会议的关键管理层引用直接作为块引用编织到叙述中。切勿创建"关键管理层引用"部分标题——让它们自然地作为支撑证据流动。
- **专业语气**：卖方股票研究风格——分析性、直接、数据驱动。
- **图表必须使用真实数据**：每个图表用实际 MCP 数据填充。切勿编造。
- **竞争对手背景**：相对于同行框架估值。25 倍市盈率（P/E）在没有知道同行交易于 20 倍或 35 倍的情况下毫无意义。
- **超链接声明**：每个事实声明——数字或定性——必须是 `<a class="data-ref">` 标签，链接到其附录条目。数字：`<a href="#ref-1" class="data-ref">$152.3B</a>`。定性：`<a href="#ref-25" class="data-ref">管理层 flagged 关税逆风为主要利润率风险</a>`。任何事实的出现都应有附录中可追溯的来源。
