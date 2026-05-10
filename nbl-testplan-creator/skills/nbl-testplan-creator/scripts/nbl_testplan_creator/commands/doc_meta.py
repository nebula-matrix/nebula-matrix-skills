"""Doc-meta command: document metadata processing.

Subcommands:
    generate  - 从 markdown 生成 sections.json
    tree      - 基于 sections.json 显示目录树
    stats     - 基于 sections.json 显示统计概览
    show      - 基于 sections.json 读取指定章节内容

Usage:
    nbl-testplan doc-meta generate spec.md -o sections.json
    nbl-testplan doc-meta tree sections.json
    nbl-testplan doc-meta stats sections.json
    nbl-testplan doc-meta show sections.json S006
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class SectionAnalyzer:
    """文档章节分析器"""

    def analyze(self, md_content: str, max_depth: int = 3,
                include_full_content: bool = False) -> Dict[str, Any]:
        lines = md_content.split('\n')

        document_title = ""
        for line in lines:
            if line.startswith('# '):
                document_title = line[2:].strip()
                break

        # 固定按一级标题 (# ) 切分顶层 sections
        heading_pattern = '^# '
        section_markers = []

        for line_num, line in enumerate(lines, 1):
            if re.match(heading_pattern, line):
                title = line.lstrip('#').strip()
                section_markers.append({
                    "line_number": line_num,
                    "title": title
                })

        sections = []
        for i, marker in enumerate(section_markers):
            line_start = marker["line_number"]
            line_end = section_markers[i + 1]["line_number"] - 1 if i + 1 < len(section_markers) else len(lines)
            section_id = f"S{i + 1:03d}"

            # 递归提取子章节，传递 max_depth 和父 section_id
            subsections = self._extract_subsections(lines, line_start, line_end, 2, max_depth, parent_id=section_id)

            section = {
                "id": section_id,
                "title": marker["title"],
                "level": 1,
                "line_start": line_start,
                "line_end": line_end,
                "line_count": line_end - line_start + 1,
                "subsections": subsections
            }

            if include_full_content:
                section_lines = lines[line_start - 1:line_end]
                section["full_content"] = '\n'.join(section_lines).strip()

            sections.append(section)

        return {
            "document_title": document_title,
            "split_config": {
                "level": 1,
                "marker": "#",
                "max_depth": max_depth,
                "total_sections": len(sections)
            },
            "sections": sections
        }

    def _extract_subsections(self, lines: List[str], start: int, end: int,
                             level: int, max_depth: int = 3,
                             parent_id: str = "") -> List[Dict[str, Any]]:
        """递归提取子章节（嵌套结构），分配层级 id"""
        if level > max_depth:
            return []

        heading_pattern = '^' + '#' * level + ' '
        sub_markers = []

        for line_num in range(start, end + 1):
            line = lines[line_num - 1]
            if re.match(heading_pattern, line):
                title = line.lstrip('#').strip()
                sub_markers.append({
                    "line_number": line_num,
                    "title": title
                })

        subsections = []
        for i, marker in enumerate(sub_markers):
            sub_start = marker["line_number"]
            sub_end = sub_markers[i + 1]["line_number"] - 1 if i + 1 < len(sub_markers) else end

            # 分配层级 id：parent_id.001, parent_id.002
            if parent_id:
                subsection_id = f"{parent_id}.{i + 1:03d}"
            else:
                subsection_id = f"{i + 1:03d}"

            subsection = {
                "id": subsection_id,
                "title": marker["title"],
                "level": level,
                "line_start": sub_start,
                "line_end": sub_end,
                "line_count": sub_end - sub_start + 1,
                "subsections": self._extract_subsections(lines, sub_start, sub_end, level + 1, max_depth, subsection_id)
            }
            subsections.append(subsection)

        return subsections


class DocumentInspector:
    """文档检查器"""

    def extract_all_headings(self, md_content: str) -> List[Dict[str, Any]]:
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

    def get_stats(self, headings: List[Dict[str, Any]], total_lines: int) -> Dict[str, Any]:
        level_counts = {}
        for h in headings:
            level_counts[h["level"]] = level_counts.get(h["level"], 0) + 1

        return {
            "total_lines": total_lines,
            "total_headings": len(headings),
            "level_distribution": level_counts,
            "max_heading_level": max((h["level"] for h in headings), default=0),
        }


def _print_stats(stats: Dict[str, Any], display_name: str = ""):
    print(f"📊 文档统计: {display_name or 'Untitled'}")
    print(f"  总行数: {stats['total_lines']}")
    print(f"  总heading数: {stats['total_headings']}")

    for level in sorted(stats['level_distribution'].keys()):
        marker = "#" * level
        count = stats['level_distribution'][level]
        print(f"  {marker} 级标题: {count}个")


def _load_sections_data(json_path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(json_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _get_source_content(source_file: str, encoding: str = 'utf-8') -> Optional[str]:
    source_path = Path(source_file)
    if not source_path.exists():
        return None
    try:
        return source_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return None


def _get_display_name(json_path: Path, sections_data: Dict[str, Any]) -> str:
    if sections_data and sections_data.get('source_file'):
        return Path(sections_data['source_file']).name
    return json_path.name


# ============================================================================
# Subcommand handlers
# ============================================================================

def _cmd_generate(args) -> int:
    """生成 sections.json"""
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误: 文件不存在 {args.input_file}")
        return 1

    encoding = getattr(args, 'encoding', 'utf-8')
    quiet = getattr(args, 'quiet', False)

    try:
        md_content = input_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        print(f"错误: 文件编码解码失败")
        return 1

    analyzer = SectionAnalyzer()
    result = analyzer.analyze(
        md_content,
        max_depth=getattr(args, 'max_depth', 3),
        include_full_content=getattr(args, 'include_full_content', False)
    )
    result["source_file"] = str(input_path.resolve())

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if not quiet:
            print(f"✅ 章节分析完成")
            print(f"📄 文档标题: {result['document_title'] or 'Untitled'}")
            print(f"🔖 解析深度: {result['split_config']['marker']} → {'#' * result['split_config']['max_depth']} (max_depth={result['split_config']['max_depth']})")
            print(f"📊 章节总数: {result['split_config']['total_sections']}")
            print(f"💾 已保存到: {args.output}\n")

            print("章节列表:")
            for section in result['sections']:
                print(f"  [{section['id']}] {section['title']} (行 {section['line_start']}-{section['line_end']}, {section['line_count']}行)")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 检查目标深度节点行数，超过阈值则警告
    check_depth = result['split_config']['max_depth']
    sections_to_check = _get_sections_to_check(result['sections'], check_depth)
    oversized = [s for s in sections_to_check if s.get('line_count', 0) > 1000]
    if oversized:
        print()
        print(f"⚠️ 警告: 以下 {check_depth} 级章节内容过多（超过1000行），建议增加 --max-depth 重新分析:")
        for section in oversized:
            print(f"  [{section['id']}] {section['title']} ({section['line_count']}行)")
        print(f"  建议命令: nbl-testplan doc-meta generate {args.input_file} --max-depth {min(check_depth + 1, 3)} -o {args.output}\n")

    return 0


def _render_nested_tree(sections: List[Dict[str, Any]], indent_level: int = 0) -> List[str]:
    """递归渲染嵌套 sections 为树形文本，id 在前"""
    lines = []
    for section in sections:
        level = section['level']
        marker = "#" * level
        title = section['title']
        section_id = section.get('id', '')

        indent = "  " * indent_level
        lines.append(f"{indent}[{section_id}] {marker} {title}")

        # 递归渲染 subsections
        subsections = section.get('subsections', [])
        if subsections:
            lines.extend(_render_nested_tree(subsections, indent_level + 1))

    return lines


def _cmd_tree(args) -> int:
    """显示目录树（基于嵌套 sections，带 section_id 标记）"""
    json_path = Path(args.json_file)
    sections_data = _load_sections_data(json_path)
    if not sections_data:
        print(f"错误: 无法读取 JSON 文件 {args.json_file}")
        return 1

    sections = sections_data.get('sections', [])
    if not sections:
        print(f"错误: JSON 文件中缺少 sections 数据")
        return 1

    # 过滤层级
    min_level = getattr(args, 'min_level', None)
    max_level = getattr(args, 'max_level', None)

    if min_level is not None or max_level is not None:
        # 需要过滤，只显示指定层级范围的节点
        def filter_sections(sections_list, parent_id=""):
            result = []
            for section in sections_list:
                level = section['level']
                section_id = section.get('id', parent_id)

                if min_level is not None and level < min_level:
                    # 跳过当前节点，但保留子节点（如果子节点在范围内）
                    subsections = section.get('subsections', [])
                    if subsections:
                        result.extend(filter_sections(subsections, section_id))
                    continue

                if max_level is not None and level > max_level:
                    continue

                # 复制节点，递归过滤子节点
                filtered_subsections = filter_sections(section.get('subsections', []), section_id)
                node = {
                    "title": section['title'],
                    "level": level,
                    "subsections": filtered_subsections
                }
                if 'id' in section:
                    node['id'] = section['id']
                result.append(node)
            return result

        filtered_sections = filter_sections(sections)
    else:
        filtered_sections = sections

    tree_lines = _render_nested_tree(filtered_sections)
    tree_output = '\n'.join(tree_lines)

    display_name = _get_display_name(json_path, sections_data)
    quiet = getattr(args, 'quiet', False)

    if not quiet:
        print(f"📄 {display_name}\n")
    print(tree_output)
    return 0


def _cmd_stats(args) -> int:
    """显示统计概览"""
    json_path = Path(args.json_file)
    sections_data = _load_sections_data(json_path)
    if not sections_data:
        print(f"错误: 无法读取 JSON 文件 {args.json_file}")
        return 1

    source_file = sections_data.get('source_file')
    if not source_file:
        print(f"错误: JSON 文件中缺少 source_file 字段")
        return 1

    md_content = _get_source_content(source_file, getattr(args, 'encoding', 'utf-8'))
    if md_content is None:
        print(f"错误: 无法读取源文件 {source_file}")
        return 1

    inspector = DocumentInspector()
    headings = inspector.extract_all_headings(md_content)
    stats = inspector.get_stats(headings, len(md_content.split('\n')))

    display_name = _get_display_name(json_path, sections_data)
    _print_stats(stats, display_name)
    return 0


def _find_section_by_id(sections: List[Dict[str, Any]], section_id: str) -> Optional[Dict[str, Any]]:
    """递归查找指定 id 的 section"""
    for section in sections:
        if section.get('id') == section_id:
            return section
        subsections = section.get('subsections', [])
        if subsections:
            result = _find_section_by_id(subsections, section_id)
            if result:
                return result
    return None


def _collect_all_ids(sections: List[Dict[str, Any]]) -> List[str]:
    """收集所有 section id（递归）"""
    ids = []
    for section in sections:
        if 'id' in section:
            ids.append(section['id'])
        subsections = section.get('subsections', [])
        if subsections:
            ids.extend(_collect_all_ids(subsections))
    return ids


def _collect_sections_at_depth(sections: List[Dict[str, Any]], target_depth: int) -> List[Dict[str, Any]]:
    """收集指定深度的所有 section（递归）。若该深度无节点，逐层向上回退直到有节点。"""
    result = []
    for section in sections:
        if section.get('level') == target_depth:
            result.append(section)
        subsections = section.get('subsections', [])
        if subsections:
            result.extend(_collect_sections_at_depth(subsections, target_depth))
    return result


def _get_sections_to_check(sections: List[Dict[str, Any]], max_depth: int) -> List[Dict[str, Any]]:
    """获取需要检查行数的 section 列表。优先按 max_depth 层级，无节点则逐层回退。"""
    for depth in range(max_depth, 0, -1):
        found = _collect_sections_at_depth(sections, depth)
        if found:
            return found
    return []


def _cmd_read(args) -> int:
    """读取指定章节内容（支持任意层级 id，可多选）"""
    json_path = Path(args.json_file)
    sections_data = _load_sections_data(json_path)
    if not sections_data:
        print(f"错误: 无法读取 JSON 文件 {args.json_file}")
        return 1

    section_ids = [sid.strip().upper() for sid in args.section_ids.split(',') if sid.strip()]
    sections = sections_data.get('sections', [])

    # 校验所有 id 存在
    all_ids = _collect_all_ids(sections)
    missing = [sid for sid in section_ids if sid not in all_ids]
    if missing:
        print(f"错误: 未找到章节 {', '.join(missing)}")
        print(f"可用章节: {', '.join(all_ids)}")
        return 1

    source_file = sections_data.get('source_file')
    if not source_file:
        print(f"错误: JSON 文件中缺少 source_file 字段")
        return 1

    md_content = _get_source_content(source_file, getattr(args, 'encoding', 'utf-8'))
    if md_content is None:
        print(f"错误: 无法读取源文件 {source_file}")
        return 1

    lines = md_content.split('\n')

    # 收集所有内容
    contents = []
    titles = []
    for section_id in section_ids:
        section = _find_section_by_id(sections, section_id)
        start = section['line_start'] - 1
        end = section['line_end']
        content = '\n'.join(lines[start:end]).strip()
        contents.append(content)
        titles.append(section['title'])

    # 多章节用显式分隔线拼接，包含章节ID和标题
    if len(contents) > 1:
        parts = []
        for i, (content, title) in enumerate(zip(contents, titles)):
            parts.append(f"<!-- === SECTION [{section_ids[i]}] {title} === -->\n\n{content}")
        combined = "\n\n<!-- ==================== SECTION BREAK ==================== -->\n\n".join(parts)
    else:
        combined = contents[0]

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(combined + '\n', encoding='utf-8')
        id_title_list = [f"{sid} ({title})" for sid, title in zip(section_ids, titles)]
        print(f"✅ 章节 {', '.join(id_title_list)} 已保存到: {args.output}")
    else:
        print(combined)

    return 0


def _cmd_info(args) -> int:
    """查看指定章节的元数据"""
    json_path = Path(args.json_file)
    sections_data = _load_sections_data(json_path)
    if not sections_data:
        print(f"错误: 无法读取 JSON 文件 {args.json_file}")
        return 1

    section_id = args.section_id.upper()
    sections = sections_data.get('sections', [])

    # 递归查找
    section = _find_section_by_id(sections, section_id)

    if not section:
        all_ids = _collect_all_ids(sections)
        print(f"错误: 未找到章节 {section_id}")
        print(f"可用章节: {', '.join(all_ids)}")
        return 1

    source_file = sections_data.get('source_file', 'N/A')

    print(f"📋 Section 元数据")
    print(f"  ID:          {section.get('id', 'N/A')}")
    print(f"  标题:        {section.get('title', 'N/A')}")
    print(f"  层级:        {section.get('level', 'N/A')}")
    print(f"  行号范围:    {section.get('line_start', 'N/A')} - {section.get('line_end', 'N/A')}")
    print(f"  行数:        {section.get('line_count', 'N/A')}")
    print(f"  源文件:      {source_file}")

    subsections = section.get('subsections', [])
    if subsections:
        print(f"\n  子章节 ({len(subsections)}个):")
        for sub in subsections:
            sub_id = sub.get('id', 'N/A')
            sub_title = sub.get('title', 'N/A')
            sub_line = sub.get('line_start', 'N/A')
            print(f"    [{sub_id}] {sub_title} (行 {sub_line})")

    return 0


# ============================================================================
# Main dispatcher
# ============================================================================

def cmd_doc_meta(_manager, args) -> int:
    """CLI command handler for 'doc-meta' subcommand dispatcher."""
    subcommand = getattr(args, 'docmeta_command', None)

    if subcommand == 'generate':
        return _cmd_generate(args)
    elif subcommand == 'tree':
        return _cmd_tree(args)
    elif subcommand == 'stats':
        return _cmd_stats(args)
    elif subcommand == 'read':
        return _cmd_read(args)
    elif subcommand == 'info':
        return _cmd_info(args)
    else:
        print("错误: 未指定子命令")
        print("可用子命令: generate, tree, stats, read, info")
        return 1
