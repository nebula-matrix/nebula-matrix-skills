"""Extract-sections command: analyze markdown document section structure.

Extract chapter/section metadata (line numbers, previews) from raw spec markdown
for downstream subagent analysis.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class SectionAnalyzer:
    """文档章节分析器 - 从原始规格文档提取章节结构和行号元数据"""

    def analyze(self, md_content: str, split_level: int = 1,
                preview_lines: int = 10,
                include_full_content: bool = False) -> Dict[str, Any]:
        """
        按指定标题级别分析文档章节结构

        Args:
            md_content: Markdown文档内容
            split_level: 切分层级 (1=#, 2=##, 3=###)
            preview_lines: 每个章节的内容预览行数
            include_full_content: 是否包含完整章节内容

        Returns:
            包含sections列表的字典，含行号范围和内容预览
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

            # 提取章节内容
            section_lines = lines[line_start - 1:line_end]

            # 内容预览
            preview_count = min(preview_lines, len(section_lines))
            content_preview = '\n'.join(section_lines[:preview_count]).strip()

            section = {
                "id": f"S{i + 1:03d}",
                "title": marker["title"],
                "level": split_level,
                "line_start": line_start,
                "line_end": line_end,
                "line_count": line_end - line_start + 1,
                "content_preview": content_preview,
            }

            if include_full_content:
                section["full_content"] = '\n'.join(section_lines).strip()

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

    def get_section_content(self, md_content: str, section_id: str,
                           split_level: int = 1) -> Optional[str]:
        """提取指定section_id的完整内容"""
        result = self.analyze(md_content, split_level=split_level,
                             preview_lines=1)

        for section in result["sections"]:
            if section["id"] == section_id:
                lines = md_content.split('\n')
                start = section["line_start"] - 1
                end = section["line_end"]
                return '\n'.join(lines[start:end]).strip()

        return None


class DocumentInspector:
    """文档检查器 - 用于 tree 和 stats 功能"""

    def extract_all_headings(self, md_content: str) -> List[Dict[str, Any]]:
        """提取文档中所有层级的heading"""
        lines = md_content.split('\n')
        headings = []

        for line_num, line in enumerate(lines, 1):
            match = re.match(r'^(#{1,6})\s+(.*?)\s*$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append({
                    "line_number": line_num,
                    "level": level,
                    "title": title,
                    "marker": "#" * level
                })

        return headings

    def build_tree(self, headings: List[Dict[str, Any]],
                   min_level: Optional[int] = None,
                   max_level: Optional[int] = None) -> str:
        """构建目录树字符串"""
        filtered = headings
        if min_level is not None:
            filtered = [h for h in filtered if h["level"] >= min_level]
        if max_level is not None:
            filtered = [h for h in filtered if h["level"] <= max_level]

        lines = []
        for h in filtered:
            indent = "  " * (h["level"] - 1)
            lines.append(f"{indent}{h['marker']} {h['title']}")

        return '\n'.join(lines)

    def get_stats(self, headings: List[Dict[str, Any]],
                  total_lines: int) -> Dict[str, Any]:
        """获取文档统计信息"""
        level_counts = {}
        for h in headings:
            level_counts[h["level"]] = level_counts.get(h["level"], 0) + 1

        return {
            "total_lines": total_lines,
            "total_headings": len(headings),
            "level_distribution": level_counts,
            "max_heading_level": max((h["level"] for h in headings), default=0),
        }


def _print_stats(stats: Dict[str, Any], document_title: str = ""):
    """打印统计信息"""
    print(f"📊 文档统计: {document_title or 'Untitled'}")
    print(f"  总行数: {stats['total_lines']}")
    print(f"  总heading数: {stats['total_headings']}")

    for level in sorted(stats['level_distribution'].keys()):
        marker = "#" * level
        count = stats['level_distribution'][level]
        print(f"  {marker} 级标题: {count}个")


def cmd_extract_sections(_manager, args) -> int:
    """CLI command handler for 'extract-sections' subcommand."""
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误: 文件不存在 {args.input_file}")
        return 1

    encoding = getattr(args, 'encoding', 'utf-8')
    quiet = getattr(args, 'quiet', False)

    # 检测输入类型：.json 或 .md
    sections_data = None
    source_file = None
    md_content = None

    if input_path.suffix.lower() == '.json':
        # 从 sections.json 读取
        try:
            sections_data = json.loads(input_path.read_text(encoding=encoding))
        except json.JSONDecodeError:
            print(f"错误: 无法解析 JSON 文件 {args.input_file}")
            return 1

        source_file = sections_data.get('source_file')
        if not source_file:
            print(f"错误: JSON 文件中缺少 source_file 字段")
            return 1

        source_path = Path(source_file)
        if not source_path.exists():
            print(f"错误: source_file 指向的文件不存在: {source_file}")
            return 1

        try:
            md_content = source_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            print(f"错误: 源文件编码解码失败: {source_file}")
            return 1
    else:
        # 直接读取 markdown 文件
        try:
            md_content = input_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            print(f"错误: 文件编码解码失败，尝试用 {encoding} 读取")
            return 1

    lines = md_content.split('\n')
    total_lines = len(lines)

    # 初始化工具
    analyzer = SectionAnalyzer()
    inspector = DocumentInspector()

    # 提取所有 heading（用于 tree/stats）
    all_headings = inspector.extract_all_headings(md_content)

    # 确定显示用的文档名（用文件名，避免第一个# heading作为标题的误导）
    if sections_data and sections_data.get('source_file'):
        display_name = Path(sections_data['source_file']).name
    else:
        display_name = input_path.name

    # 模式1: 显示目录树
    if getattr(args, 'tree', False):
        min_level = getattr(args, 'min_level', None)
        max_level = getattr(args, 'max_level', None)

        tree_output = inspector.build_tree(all_headings, min_level, max_level)

        if not quiet:
            print(f"📄 {display_name}\n")
        print(tree_output)

        # 如果同时有 --stats，也打印统计
        if getattr(args, 'stats', False):
            stats = inspector.get_stats(all_headings, total_lines)
            print()
            _print_stats(stats, display_name)

        return 0

    # 模式2: 显示统计概览
    if getattr(args, 'stats', False):
        stats = inspector.get_stats(all_headings, total_lines)
        _print_stats(stats, display_name)
        return 0

    # 模式3: 默认 - 提取章节结构（输出JSON）
    split_level = getattr(args, 'level', 1)
    preview_lines = getattr(args, 'preview_lines', 10)
    include_full = getattr(args, 'include_full_content', False)

    result = analyzer.analyze(
        md_content,
        split_level=split_level,
        preview_lines=preview_lines,
        include_full_content=include_full
    )

    # 添加原始文件路径，方便后续直接定位内容
    if sections_data and sections_data.get('source_file'):
        result["source_file"] = sections_data['source_file']
    else:
        result["source_file"] = str(input_path.resolve())

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if not quiet:
            print(f"✅ 章节分析完成")
            print(f"📄 文档标题: {result['document_title'] or 'Untitled'}")
            print(f"🔖 切分层级: {result['split_config']['marker']} (level {result['split_config']['level']})")
            print(f"📊 章节总数: {result['split_config']['total_sections']}")
            print(f"💾 已保存到: {args.output}\n")

            # 打印章节列表
            print("章节列表:")
            for section in result['sections']:
                print(f"  [{section['id']}] {section['title']} (行 {section['line_start']}-{section['line_end']}, {section['line_count']}行)")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0
