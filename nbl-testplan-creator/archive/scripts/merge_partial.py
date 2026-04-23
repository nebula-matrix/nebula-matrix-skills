#!/usr/bin/env python3
"""
合并多个 partial markdown 文件到统一的 testplan_raw.md
按 Feature 归类，确保同一 Feature 的所有 SubFeature 合并到一起
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class SubFeature:
    """SubFeature 块"""
    heading: str           # ### SubFeatureName
    name: str              # 解析出的 SubFeature 名称
    body: List[str] = field(default_factory=list)  # 属性块+表格等所有内容


@dataclass
class FeatureBlock:
    """Feature 块"""
    heading: str                        # ## FeatureName
    name: str                           # 解析出的 Feature 名称
    body: List[str] = field(default_factory=list)     # 属性块内容（在第一个 SubFeature 之前）
    subfeatures: List[SubFeature] = field(default_factory=list)

    def to_lines(self) -> List[str]:
        """输出为文本行，自动规范化空行"""
        lines = []

        # Feature heading
        lines.append(self.heading)
        lines.append('')  # heading 后空行

        # Feature body（属性块）
        if self.body:
            for line in self.body:
                if line.strip():
                    lines.append(line)
        lines.append('')  # body 后空行

        # SubFeatures
        for i, sf in enumerate(self.subfeatures):
            if i > 0:
                lines.append('')  # SubFeature 之间空行

            lines.append(sf.heading)
            lines.append('')  # heading 后空行

            # 处理 sf.body：规范化空行——跳过原始空行，仅在属性和表格之间插入空行
            sf_lines = []
            table_started = False
            has_attrs = False
            for line in sf.body:
                stripped = line.strip()
                if not stripped:
                    continue  # 忽略 body 内部原始空行
                if stripped.startswith('|'):
                    if not table_started:
                        table_started = True
                        if has_attrs and (not sf_lines or sf_lines[-1]):
                            sf_lines.append('')
                elif stripped.startswith('-') or ':' in stripped:
                    has_attrs = True
                sf_lines.append(line)
            lines.extend(sf_lines)

        # 清理末尾多余空行
        while lines and lines[-1] == '':
            lines.pop()

        return lines


def _encode_name(name: str) -> str:
    """与 feature_manager.py 一致的 name 编码：去掉空白和点号，全小写"""
    return re.sub(r'[\s\.]+', '', name.strip()).lower()


def parse_md_blocks(text: str, source: str = "") -> Tuple[Optional[str], Optional[str], List[FeatureBlock]]:
    """
    用正则解析 markdown，提取文档标题、元数据（# Title 和第一个 ## Feature 之间）和 FeatureBlock

    返回 (doc_title, metadata, blocks)
    """
    blocks: List[FeatureBlock] = []

    # 跳过 BOM
    text = text.lstrip('﻿')

    # 提取文档标题：# Title（不是 ##）
    doc_title = None
    metadata = None
    m_title = re.search(r'^# ([^#\n].*)$', text, re.MULTILINE)
    if m_title:
        doc_title = m_title.group(1).strip()
        after_title = text[m_title.end():]

        # 查找第一个 ## Feature 的位置，保留中间的元数据
        feature_match = re.search(r'^(?=## (?!#))', after_title, flags=re.MULTILINE)
        if feature_match:
            metadata = after_title[:feature_match.start()].strip('\n')
            text = after_title[feature_match.start():]
        else:
            text = after_title.lstrip('\n')

    # 按 ## Feature heading 分割全文
    parts = re.split(r'^(?=## (?!#))', text, flags=re.MULTILINE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # 提取 Feature heading: ## FeatureName
        m = re.match(r'^## (.+)$', part, re.MULTILINE)
        if not m:
            continue

        feature_name = re.sub(r'^\d+(\.\d+)*\.?\s*', '', m.group(1)).strip()
        # 找到 heading 之后的所有内容
        rest = part[m.end():]

        # 按 ### SubFeature heading 分割
        sf_parts = re.split(r'^(?=### (?!#))', rest, flags=re.MULTILINE)

        feature = FeatureBlock(
            heading=f'## {feature_name}',
            name=feature_name,
        )

        for sf_part in sf_parts:
            if not sf_part.strip():
                continue

            if sf_part.strip().startswith('### '):
                # 这是 SubFeature
                m2 = re.match(r'^### (.+)$', sf_part.strip(), re.MULTILINE)
                if m2:
                    sf_name = re.sub(r'^\d+(\.\d+)*\.?\s*', '', m2.group(1)).strip()
                    sf_body = sf_part[m2.end():].strip('\n').split('\n')
                    # 不过滤空行，保留原始格式中的空白行
                    feature.subfeatures.append(SubFeature(
                        heading=f'### {sf_name}',
                        name=sf_name,
                        body=sf_body,
                    ))
            else:
                # 位于 Feature heading 之后、第一个 SubFeature 之前的内容（属性块）
                # 不过滤空行
                feature.body = sf_part.strip('\n').split('\n')

        blocks.append(feature)

    return doc_title, metadata, blocks


def _deduplicate_subfeatures(subfeatures: List[SubFeature]) -> List[SubFeature]:
    """
    合并重复的 SubFeature：相同的 SubFeature 只保留一个
    如果同名但属性不同，保留第一个出现的
    """
    seen: Dict[str, SubFeature] = {}
    result: List[SubFeature] = []

    for sf in subfeatures:
        encoded = _encode_name(sf.name)
        if encoded not in seen:
            seen[encoded] = sf
            result.append(sf)
        else:
            # 同名 SubFeature：追加其 body 内容（保留标题行之后的所有行）
            # 跳过属性块中的重复 sub_feature_name 行，保留其他行和表格行
            existing = seen[encoded]
            for line in sf.body:
                stripped = line.strip()
                # 跳过 SubFeature 属性块中的重复 sub_feature_name 行
                if stripped.startswith('- sub_feature_name:') or stripped.startswith('> sub_feature_name:'):
                    continue
                # 跳过与现有内容完全相同的行
                if line.strip() and line.strip() not in [
                    l.strip() for l in existing.body
                ]:
                    existing.body.append(line)
                elif not line.strip():
                    # 空行也保留，以分隔不同 partial 的内容
                    existing.body.append(line)

    return result


def merge_features(all_blocks: List[FeatureBlock]) -> List[FeatureBlock]:
    """
    按 Feature 名称合并所有块
    不同 partial 中的相同 Feature 合并到一个块中
    """
    merged: Dict[str, FeatureBlock] = {}
    feature_order: List[str] = []

    for block in all_blocks:
        encoded = _encode_name(block.name)

        if encoded not in merged:
            merged[encoded] = FeatureBlock(
                heading=block.heading,
                name=block.name,
                body=block.body.copy(),
                subfeatures=block.subfeatures.copy(),
            )
            feature_order.append(encoded)
        else:
            existing = merged[encoded]
            # 合并 body（属性块）- 保留现有 body，追加新属性块中不同的行
            existing_lines = {l.strip() for l in existing.body if l.strip()}
            for line in block.body:
                if line.strip() and line.strip() not in existing_lines:
                    existing.body.append(line)

            # 合并 SubFeature - 保留现有 subfeatures，追加新的（去重）
            existing.subfeatures.extend(block.subfeatures)
            existing.subfeatures = _deduplicate_subfeatures(existing.subfeatures)

    return [merged[k] for k in feature_order]


def merge_partials(output_path: str, partial_paths: List[str]):
    """
    主合并函数
    """
    # 收集所有 partial 文件内的所有 FeatureBlock
    all_blocks: List[FeatureBlock] = []
    doc_title = None
    metadata = None
    for ppath in partial_paths:
        path = Path(ppath)
        if not path.exists():
            print(f"⚠️  跳过不存在的文件: {path}")
            continue

        text = path.read_text(encoding='utf-8')
        title, meta, blocks = parse_md_blocks(text, source=str(path))
        if doc_title is None and title:
            doc_title = title
        if metadata is None and meta:
            metadata = meta
        all_blocks.extend(blocks)

    if not all_blocks:
        print("❌ 错误：没有解析到任何 Feature 块")
        sys.exit(1)

    # 按 Feature 合并
    merged = merge_features(all_blocks)

    # 输出
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open('w', encoding='utf-8') as f:
        # 写入文档标题（第一个 partial 中定义的）
        if doc_title:
            f.write(f'# {doc_title}\n\n')
        # 写入元数据（# Title 和第一个 ## Feature 之间的内容）
        if metadata:
            f.write(f'{metadata}\n\n')
        for i, block in enumerate(merged):
            for line in block.to_lines():
                f.write(line + '\n')
            # Feature 之间空一行
            if i < len(merged) - 1:
                f.write('\n')

    # 统计
    total_sf = sum(len(b.subfeatures) for b in merged)
    total_tp = 0
    for b in merged:
        for sf in b.subfeatures:
            total_tp += sum(1 for l in sf.body if l.strip().startswith('|') and 'tp_name' not in l)

    print(f"✅ 合并完成: {output_path}")
    print(f"   Features: {len(merged)}")
    print(f"   SubFeatures: {total_sf}")
    print(f"   Testpoint rows: {total_tp}")


def main():
    parser = argparse.ArgumentParser(
        description='合并多个 partial markdown 文件到统一的 testplan_raw.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/merge_partial.py .tp_cache/testplan_raw.md .tp_cache/partial_a.md .tp_cache/partial_b.md
  python3 scripts/merge_partial.py .tp_cache/testplan_raw.md .tp_cache/partial_*.md
""")
    parser.add_argument('output', help='输出文件路径（通常是 .tp_cache/testplan_raw.md）')
    parser.add_argument('partials', nargs='+', help='一个或多个 partial markdown 文件')

    args = parser.parse_args()
    merge_partials(args.output, args.partials)


if __name__ == '__main__':
    main()
