#!/usr/bin/env python3
"""
章节划分脚本 - 粗框架划分
按指定标题级别切分文档，生成JSON供后续subagent分析
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any


class SectionSplitter:
    """文档章节划分器"""

    def __init__(self):
        pass

    def split_document(self, md_content: str, split_level: int = 1) -> Dict[str, Any]:
        """
        按指定标题级别粗划分文档

        Args:
            md_content: Markdown文档内容
            split_level: 切分层级 (1=#, 2=##, 3=###)

        Returns:
            包含sections列表的字典
        """
        lines = md_content.split('\n')

        # 提取文档标题（第一个一级标题）
        document_title = ""
        for line in lines:
            if line.startswith('# '):
                document_title = line[2:].strip()
                break

        # 找出所有指定层级的标题及其行号
        heading_pattern = '^' + '#' * split_level + ' '
        section_markers = []

        for line_num, line in enumerate(lines, 1):
            if re.match(heading_pattern, line):
                title = line.lstrip('#').strip()
                section_markers.append({
                    "line_number": line_num,
                    "title": title,
                    "level": split_level
                })

        # 构建sections列表，计算每个章节的行号范围
        sections = []
        for i, marker in enumerate(section_markers):
            line_start = marker["line_number"]
            # 下一章节的开始行号（如果是最后一个章节，则为文档末尾）
            line_end = section_markers[i + 1]["line_number"] - 1 if i + 1 < len(section_markers) else len(lines)

            # 提取章节内容预览（前10行，保证完整行）
            section_lines = lines[line_start - 1:line_end]
            preview_lines_count = min(10, len(section_lines))
            content_preview = '\n'.join(section_lines[:preview_lines_count]).strip()

            section = {
                "id": f"S{i + 1:03d}",
                "title": marker["title"],
                "level": split_level,
                "line_start": line_start,
                "line_end": line_end,
                "content_preview": content_preview,
                "line_count": line_end - line_start + 1
            }
            sections.append(section)

        result = {
            "document_title": document_title,
            "split_config": {
                "level": split_level,
                "marker": "#" * split_level,
                "total_sections": len(sections)
            },
            "sections": sections
        }

        return result

    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """保存为JSON文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='文档章节划分 - 粗框架划分，支持后续subagent分析')
    parser.add_argument('input_file', help='输入的markdown文件路径')
    parser.add_argument('-l', '--split-level', type=int, choices=[1, 2, 3], default=1,
                       help='章节切分层级 (1=#, 2=##, 3=###)，默认为1')
    parser.add_argument('-o', '--output', help='输出JSON文件路径（可选）')

    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误：文件不存在 {args.input_file}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 创建划分器并执行划分
    splitter = SectionSplitter()
    result = splitter.split_document(md_content, args.split_level)

    # 输出结果
    if args.output:
        splitter.save_to_json(result, args.output)
        print(f"✅ 章节划分完成")
        print(f"📄 文档标题: {result['document_title']}")
        print(f"🔖 切分层级: {result['split_config']['marker']} (level {result['split_config']['level']})")
        print(f"📊 章节总数: {result['split_config']['total_sections']}")
        print(f"💾 已保存到: {args.output}\n")

        # 打印章节列表
        print("章节列表:")
        for section in result['sections']:
            print(f"  [{section['id']}] {section['title']} (行 {section['line_start']}-{section['line_end']}, {section['line_count']}行)")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
