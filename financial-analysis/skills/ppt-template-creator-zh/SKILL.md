---
name: ppt-template-creator-zh
description: 从用户提供的PowerPoint模板创建独立的PPT模板技能（而非演示文稿）。仅当用户希望将其模板转换为可重用技能时使用。如果用户只想创建演示文稿，请使用pptx技能。
---

# PPT模板创建器

**此技能创建技能，而非演示文稿。** 当用户希望将其PowerPoint模板转换为可重用技能以便后续生成演示文稿时使用此技能。如果用户只想创建演示文稿，请使用 `pptx` 技能。

生成的技能包括：
- `assets/template.pptx` - 模板文件
- `SKILL.md` - 完整说明（无需引用此元技能）

**对于通用技能构建最佳实践**，请参考 `skill-creator` 技能。此技能专注于PPT特定模式。

## 工作流程

1. **用户提供模板**（.pptx或.potx）
2. **分析模板** - 提取布局、占位符、尺寸
3. **初始化技能** - 使用 `skill-creator` 技能设置技能结构
4. **添加模板** - 将.pptx复制到 `assets/template.pptx`
5. **编写SKILL.md** - 按照下方模板，包含PPT特定细节
6. **创建示例** - 生成示例演示文稿以验证
7. **打包** - 使用 `skill-creator` 技能打包为.skill文件

## 第二步：分析模板

**关键：提取精确的占位符位置** - 这决定了内容区域边界。

```python
from pptx import Presentation

prs = Presentation(template_path)
print(f"尺寸: {prs.slide_width/914400:.2f}\" x {prs.slide_height/914400:.2f}\"")
print(f"布局数量: {len(prs.slide_layouts)}")

for idx, layout in enumerate(prs.slide_layouts):
    print(f"\n[{idx}] {layout.name}:")
    for ph in layout.placeholders:
        try:
            ph_idx = ph.placeholder_format.idx
            ph_type = ph.placeholder_format.type
            # 重要：提取精确位置（英寸）
            left = ph.left / 914400
            top = ph.top / 914400
            width = ph.width / 914400
            height = ph.height / 914400
            print(f"    idx={ph_idx}, type={ph_type}")
            print(f"        x={left:.2f}\", y={top:.2f}\", w={width:.2f}\", h={height:.2f}\"")
        except:
            pass
```

**需要记录的关键尺寸：**
- **标题位置**：标题占位符在哪里？
- **副标题/描述**：副标题行在哪里？
- **页脚占位符**：页脚/来源出现在哪里？
- **内容区域**：副标题和页脚之间的空间是您的内容区域

### 找到真正的内容起始位置

**关键：** 内容区域并不总是紧跟在副标题占位符之后。许多模板在副标题和内容区域之间有视觉边框、线条或保留空间。

**最佳方法：** 查看布局2或类似的"内容"布局，这些布局有OBJECT占位符 - 此占位符的 `y` 位置指示内容实际应该开始的位置。

```python
# 查找OBJECT占位符以确定真正的内容起始位置
for idx, layout in enumerate(prs.slide_layouts):
    for ph in layout.placeholders:
        try:
            if ph.placeholder_format.type == 7:  # OBJECT类型
                top = ph.top / 914400
                print(f"布局 [{idx}] {layout.name}: OBJECT从 y={top:.2f}\" 开始")
                # 这个y值就是您的内容应该开始的位置！
        except:
            pass
```

**示例：** 一个模板可能有：
- 副标题结束于 y=1.38"
- 但OBJECT占位符从 y=1.90" 开始
- 差距（0.52"）是为边框/线条保留的 - **不要在此处放置内容**

使用OBJECT占位符的 `y` 位置作为内容起始位置，而非副标题的结束位置。

## 第五步：编写SKILL.md

生成的技能应具有以下结构：
```
[company]-ppt-template/
├── SKILL.md
└── assets/
    └── template.pptx
```

### 生成的SKILL.md模板

生成的SKILL.md必须是**自包含的**，所有说明都内嵌其中。使用此模板，填入分析得出的方括号值：

```markdown
---
name: [company]-ppt-template
description: [公司]PowerPoint模板用于创建演示文稿。在创建[公司]品牌的推介材料、董事会材料或客户演示时使用。
---

# [公司] PPT模板

模板：`assets/template.pptx`（[宽度]" x [高度]"，[N]个布局）

## 创建演示文稿

```python
from pptx import Presentation

prs = Presentation("path/to/skill/assets/template.pptx")

# 首先删除所有现有幻灯片
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

# 从布局添加幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_IDX])
```

## 主要布局

| 索引 | 名称 | 用途 |
|------|------|------|
| [0] | [布局名称] | [封面/标题幻灯片] |
| [N] | [布局名称] | [带项目符号的内容] |
| [N] | [布局名称] | [两栏布局] |

## 占位符映射

**关键：包含每个占位符的精确位置（x, y坐标）。**

### 布局 [N]：[名称]
| idx | 类型 | 位置 | 用途 |
|-----|------|------|------|
| [idx] | TITLE (1) | y=[Y]" | 幻灯片标题 |
| [idx] | BODY (2) | y=[Y]" | 副标题/描述 |
| [idx] | BODY (2) | y=[Y]" | 页脚 |
| [idx] | BODY (2) | y=[Y]" | 来源/注释 |

### 内容区域边界

**记录自定义形状/表格/图表的安全内容区域：**

```
内容区域（布局 [N]）：
- 左边距：[X]"（内容从此开始）
- 顶部：[Y]"（副标题占位符下方）
- 宽度：[W]"
- 高度：[H]"（页脚前结束）

对于四象限布局：
- 左栏：x=[X]"，宽度=[W]"
- 右栏：x=[X]"，宽度=[W]"
- 上行：y=[Y]"，高度=[H]"
- 下行：y=[Y]"，高度=[H]"
```

**为什么这很重要：** 自定义内容（文本框、表格、图表）必须保持在边界内，以避免与标题、页脚和来源行等模板占位符重叠。

## 填充内容

**不要添加手动项目符号字符** - 幻灯片母版处理格式。

```python
# 填充标题
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        if shape.placeholder_format.type == 1:  # TITLE
            shape.text = "幻灯片标题"

# 用层次结构填充内容（级别0=标题，级别1=项目符号）
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        idx = shape.placeholder_format.idx
        if idx == [CONTENT_IDX]:
            tf = shape.text_frame
            for para in tf.paragraphs:
                para.clear()

            content = [
                ("章节标题", 0),
                ("第一个要点", 1),
                ("第二个要点", 1),
            ]

            tf.paragraphs[0].text = content[0][0]
            tf.paragraphs[0].level = content[0][1]
            for text, level in content[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.level = level
```

## 示例：封面幻灯片

```python
slide = prs.slides.add_slide(prs.slide_layouts[[COVER_IDX]])
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        idx = shape.placeholder_format.idx
        if idx == [TITLE_IDX]:
            shape.text = "公司名称"
        elif idx == [SUBTITLE_IDX]:
            shape.text = "演示标题 | 日期"
```

## 示例：内容幻灯片

```python
slide = prs.slides.add_slide(prs.slide_layouts[[CONTENT_IDX]])
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        ph_type = shape.placeholder_format.type
        idx = shape.placeholder_format.idx
        if ph_type == 1:
            shape.text = "执行摘要"
        elif idx == [BODY_IDX]:
            tf = shape.text_frame
            for para in tf.paragraphs:
                para.clear()
            content = [
                ("主要发现", 0),
                ("收入同比增长40%至5000万美元", 1),
                ("扩展到3个新市场", 1),
                ("建议", 0),
                ("推进战略举措", 1),
            ]
            tf.paragraphs[0].text = content[0][0]
            tf.paragraphs[0].level = content[0][1]
            for text, level in content[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.level = level
```
```

## 第六步：创建示例输出

生成示例演示文稿以验证技能正常工作。将其保存在技能旁边以供参考。

## 生成技能的PPT特定规则

1. **模板在assets/** - 始终捆绑.pptx文件
2. **自包含SKILL.md** - 所有说明内嵌，无外部引用
3. **无手动项目符号** - 使用 `paragraph.level` 实现层次结构
4. **先删除幻灯片** - 添加新幻灯片前始终清除现有幻灯片
5. **按idx记录占位符** - 占位符idx值是模板特定的