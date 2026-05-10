#!/usr/bin/env python3
"""review_writer.py - Write fs_reg_slv_review.md from review items."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def write_review_md(
    review_items: list[dict[str, Any]],
    output_path: str | Path,
    module_name: str = "",
) -> Path:
    """Generate fs_reg_slv_review.md from review items list."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    title = f"# {module_name.upper()} FS/REG 审查记录" if module_name else "# FS/REG 审查记录"
    lines.append(title)
    lines.append("")
    lines.append("> 以下条目为功能规格书或寄存器配置手册中未明确体现的内容，需要用户补充确认。")
    lines.append("")

    if not review_items:
        lines.append("*未发现需要确认的条目。*")
        lines.append("")
    else:
        for item in review_items:
            item_id = item.get("item_id", "")
            feature = item.get("feature", "")
            question = item.get("question", "")
            source = item.get("source", "")
            status = item.get("status", "pending")

            lines.append(f"## {item_id}: {feature}")
            lines.append("")
            lines.append(f"- **问题**: {question}")
            lines.append(f"- **来源**: {source}")
            lines.append(f"- **确定信息**: [待填写]")
            lines.append(f"- **状态**: {status}")
            lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("\n## 使用说明")
    lines.append("")
    lines.append("1. 阅读每个条目的问题和来源")
    lines.append("2. 在'确定信息'处填写你的确认或补充说明")
    lines.append("3. 将更新后的文件重新输入给本 skill 进行二次刷新，即可更新测试点文档")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path.resolve()


def write_review_from_testplan(testplan_data: dict[str, Any], output_path: str | Path) -> Path:
    """Convenience: extract review_items from testplan_raw.json and write review md."""
    review_items = testplan_data.get("review_items", [])
    module_name = testplan_data.get("module_name", "")
    return write_review_md(review_items, output_path, module_name)


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 3:
        print("Usage: python review_writer.py <testplan.json> <output.md>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    result = write_review_from_testplan(data, sys.argv[2])
    print(f"Written: {result}")
