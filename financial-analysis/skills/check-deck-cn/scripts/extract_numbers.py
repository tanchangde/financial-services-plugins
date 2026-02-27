#!/usr/bin/env python3
"""
从演示文稿内容中提取数值用于一致性检查。

用法：
    python extract_numbers.py presentation-content.md
    python extract_numbers.py presentation-content.md --output numbers.json

此脚本解析markdown格式的演示文稿内容（来自markitdown）
并提取所有数值及其上下文和幻灯片引用。
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class NumberInstance:
    """演示文稿中发现的数值。"""
    value: str           # 原始字符串表示
    normalized: float    # 标准化数值
    unit: str           # 检测到的单位（M, B, K, %, bps, x等）
    slide: int          # 幻灯片编号（未知时为0）
    context: str        # 周围文本作为上下文
    line_number: int    # 源文件中的行号
    category: str       # 检测到的类别（收入、利润率、倍数等）


def normalize_number(value_str: str, unit: str) -> float:
    """将带单位的数字字符串转换为标准化浮点值。"""
    # 移除逗号和空格
    clean = re.sub(r'[,\s]', '', value_str)

    try:
        base_value = float(clean)
    except ValueError:
        return 0.0

    # 应用单位乘数
    multipliers = {
        'T': 1e12,
        'B': 1e9,
        'bn': 1e9,
        'billion': 1e9,
        'M': 1e6,
        'mm': 1e6,
        'mn': 1e6,
        'million': 1e6,
        'K': 1e3,
        'k': 1e3,
        'thousand': 1e3,
    }

    for unit_key, multiplier in multipliers.items():
        if unit_key.lower() in unit.lower():
            return base_value * multiplier

    return base_value


def detect_category(context: str, unit: str) -> str:
    """根据上下文和单位检测数字类别。"""
    context_lower = context.lower()

    # 收入相关
    if any(term in context_lower for term in ['revenue', 'sales', 'top line', 'topline', '收入', '销售额']):
        return 'revenue'

    # EBITDA相关
    if 'ebitda' in context_lower:
        if any(term in context_lower for term in ['margin', '%', 'percent', '利润率']):
            return 'ebitda_margin'
        return 'ebitda'

    # 利润率相关
    if any(term in context_lower for term in ['margin', 'profit', '利润率', '利润']):
        return 'margin'

    # 增长相关
    if any(term in context_lower for term in ['growth', 'cagr', 'yoy', 'y/y', '增长']):
        return 'growth'

    # 估值倍数
    if any(term in context_lower for term in ['multiple', 'ev/', 'p/e', 'ev/ebitda', 'ev/revenue', '倍数']):
        return 'multiple'

    # 企业价值/市值
    if any(term in context_lower for term in ['enterprise value', 'ev ', 'market cap', '企业价值', '市值']):
        return 'valuation'

    # 百分比（通用）
    if unit in ['%', 'bps', 'percent']:
        return 'percentage'

    # 倍数指标
    if unit == 'x':
        return 'multiple'

    return 'other'


def extract_numbers(content: str) -> list[NumberInstance]:
    """从演示文稿内容中提取所有数字。"""
    numbers = []
    current_slide = 0

    # 幻灯片标记模式（来自markitdown格式）
    slide_pattern = re.compile(r'^#+\s*Slide\s*(\d+)|^<!-- Slide (\d+)')

    # 各种格式的数字模式
    # 匹配：$500M, 500M, $500 million, 25%, 25.5%, 2.5x, 150bps, $1,234.56等
    number_pattern = re.compile(
        r'(?P<currency>[$€£¥])?'  # 可选货币符号
        r'(?P<number>[\d,]+(?:\.\d+)?)'  # 数字本身
        r'\s*'
        r'(?P<unit>%|bps|x|'  # 常见单位
        r'[Tt]rillion|[Bb]illion|[Mm]illion|[Tt]housand|'  # 完整单词
        r'[TBMKtbmk]n?|mm|MM)?'  # 缩写
        r'(?!\d)'  # 负向先行断言以避免部分匹配
    )

    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # 检查幻灯片标记
        slide_match = slide_pattern.match(line)
        if slide_match:
            current_slide = int(slide_match.group(1) or slide_match.group(2))
            continue

        # 查找行中的所有数字
        for match in number_pattern.finditer(line):
            value_str = match.group('number')
            currency = match.group('currency') or ''
            unit = match.group('unit') or ''

            # 跳过没有上下文的很短数字（可能不是财务数据）
            if len(value_str.replace(',', '').replace('.', '')) < 2 and not unit:
                continue

            # 跳过年份数字（1900-2099），除非有单位
            try:
                num_val = float(value_str.replace(',', ''))
                if 1900 <= num_val <= 2099 and not unit and not currency:
                    continue
            except ValueError:
                pass

            # 构建完整值字符串
            full_value = f"{currency}{value_str}{unit}"

            # 获取上下文（周围单词）
            start = max(0, match.start() - 50)
            end = min(len(line), match.end() + 50)
            context = line[start:end].strip()

            # 标准化单位
            if currency:
                if not unit:
                    unit = 'USD'  # 假设$没有单位时为美元
                else:
                    unit = f"USD_{unit}"

            normalized = normalize_number(value_str, unit)
            category = detect_category(context, unit)

            numbers.append(NumberInstance(
                value=full_value,
                normalized=normalized,
                unit=unit or 'none',
                slide=current_slide,
                context=context,
                line_number=line_num,
                category=category
            ))

    return numbers


def find_inconsistencies(numbers: list[NumberInstance]) -> list[dict]:
    """查找提取数字中潜在的不一致。"""
    inconsistencies = []

    # 按类别分组数字
    by_category = defaultdict(list)
    for num in numbers:
        if num.category != 'other':
            by_category[num.category].append(num)

    # 检查每个类别的不匹配
    for category, instances in by_category.items():
        if len(instances) < 2:
            continue

        # 按近似值分组（5%容差内）
        value_groups = []
        for inst in instances:
            placed = False
            for group in value_groups:
                ref_value = group[0].normalized
                if ref_value > 0:
                    diff_pct = abs(inst.normalized - ref_value) / ref_value
                    if diff_pct < 0.05:  # 5%容差
                        group.append(inst)
                        placed = True
                        break
            if not placed:
                value_groups.append([inst])

        # 如果有多个组，可能存在不一致
        if len(value_groups) > 1:
            # 按大小排序（最大的在前）
            value_groups.sort(key=len, reverse=True)

            # 最大的组可能是"正确的"，其他是潜在问题
            main_group = value_groups[0]
            for other_group in value_groups[1:]:
                inconsistencies.append({
                    'category': category,
                    'expected': {
                        'value': main_group[0].value,
                        'slides': sorted(set(n.slide for n in main_group)),
                        'count': len(main_group)
                    },
                    'found': {
                        'value': other_group[0].value,
                        'slides': sorted(set(n.slide for n in other_group)),
                        'count': len(other_group)
                    },
                    'severity': 'high' if category in ['revenue', 'ebitda', 'valuation'] else 'medium'
                })

    return inconsistencies


def main():
    parser = argparse.ArgumentParser(
        description='从演示文稿内容中提取数字用于一致性检查'
    )
    parser.add_argument('input_file', help='包含演示文稿内容的Markdown文件')
    parser.add_argument('--output', '-o', help='输出JSON文件（默认：stdout）')
    parser.add_argument('--check', '-c', action='store_true',
                       help='检查不一致并报告')

    args = parser.parse_args()

    # 读取输入
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误：文件未找到：{args.input_file}", file=sys.stderr)
        sys.exit(1)

    content = input_path.read_text()

    # 提取数字
    numbers = extract_numbers(content)

    # 准备输出
    output = {
        'total_numbers': len(numbers),
        'by_category': defaultdict(list),
        'numbers': [asdict(n) for n in numbers]
    }

    for num in numbers:
        output['by_category'][num.category].append({
            'value': num.value,
            'slide': num.slide,
            'context': num.context[:100]
        })

    output['by_category'] = dict(output['by_category'])

    # 如果请求则检查不一致
    if args.check:
        inconsistencies = find_inconsistencies(numbers)
        output['inconsistencies'] = inconsistencies

        if inconsistencies:
            print("\n=== 检测到潜在不一致性 ===\n", file=sys.stderr)
            for inc in inconsistencies:
                print(f"类别：{inc['category'].upper()}", file=sys.stderr)
                print(f"  预期：{inc['expected']['value']}（幻灯片：{inc['expected']['slides']}，数量：{inc['expected']['count']}）", file=sys.stderr)
                print(f"  发现：{inc['found']['value']}（幻灯片：{inc['found']['slides']}，数量：{inc['found']['count']}）", file=sys.stderr)
                print(f"  严重程度：{inc['severity']}", file=sys.stderr)
                print(file=sys.stderr)

    # 输出结果
    json_output = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).write_text(json_output)
        print(f"输出已写入 {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == '__main__':
    main()