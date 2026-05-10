"""Show-section command: read a specific section from sections.json metadata.

Usage:
    nbl-testplan show-section sections.json S006
    nbl-testplan show-section sections.json S006 -o output.md
"""

import json
from pathlib import Path


def cmd_show_section(_manager, args) -> int:
    """CLI command handler for 'show-section' subcommand."""
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"错误: 文件不存在 {args.json_file}")
        return 1

    section_id = args.section_id.upper()

    # 读取 sections.json
    try:
        sections_data = json.loads(json_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        print(f"错误: 无法解析 JSON 文件 {args.json_file}")
        return 1

    # 验证必要字段
    source_file = sections_data.get('source_file')
    if not source_file:
        print(f"错误: JSON 文件中缺少 source_file 字段")
        return 1

    sections = sections_data.get('sections', [])
    if not sections:
        print(f"错误: JSON 文件中缺少 sections 数据")
        return 1

    # 查找指定章节
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        available = ', '.join(s['id'] for s in sections)
        print(f"错误: 未找到章节 {section_id}")
        print(f"可用章节: {available}")
        return 1

    # 读取源文件
    source_path = Path(source_file)
    if not source_path.exists():
        print(f"错误: source_file 指向的文件不存在: {source_file}")
        return 1

    try:
        lines = source_path.read_text(encoding='utf-8').split('\n')
    except UnicodeDecodeError:
        print(f"错误: 源文件编码解码失败: {source_file}")
        return 1

    # 提取内容
    start = section['line_start'] - 1
    end = section['line_end']
    content = '\n'.join(lines[start:end]).strip()

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + '\n', encoding='utf-8')
        print(f"✅ 章节 {section_id} ({section['title']}) 已保存到: {args.output}")
    else:
        print(content)

    return 0
