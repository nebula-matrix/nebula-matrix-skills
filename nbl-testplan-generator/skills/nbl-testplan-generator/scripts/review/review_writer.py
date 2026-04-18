"""Review generation and parsing for fs_reg_slv_review.md.

Generates a markdown review file with categorized issues and summary
statistics. Also parses a filled-in review file to extract resolved
issues for refresh workflows.
"""

from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import Any

# Category key -> (Chinese label, markdown anchor name)
CATEGORY_META: dict[str, tuple[str, str]] = {
    "spec_defect": ("Spec 缺陷", "spec_defect"),
    "reg_missing": ("寄存器缺失", "reg_missing"),
    "logic_conflict": ("逻辑矛盾", "logic_conflict"),
    "param_undefined": ("参数未定义", "param_undefined"),
    "coverage_gap": ("覆盖率缺口", "coverage_gap"),
}

# Ordered category keys for deterministic output
CATEGORY_ORDER: list[str] = [
    "spec_defect",
    "reg_missing",
    "logic_conflict",
    "param_undefined",
    "coverage_gap",
]


def write_review(
    output_path: str,
    spec_name: str,
    reg_name: str,
    issues: list[dict[str, Any]],
) -> str:
    """Generate a markdown review file and return *output_path*.

    Parameters
    ----------
    output_path:
        Destination file path for the review markdown.
    spec_name:
        Name of the specification document being reviewed.
    reg_name:
        Name of the register manual being reviewed.
    issues:
        List of issue dicts. Each dict should contain the keys
        ``category``, ``id``, ``title``, ``feature``, ``description``,
        ``suggestion``, and ``resolution``. If ``resolution`` is empty
        or missing it defaults to ``"待用户填写"``.
    """
    # Group issues by category
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        cat = issue.get("category", "spec_defect")
        grouped[cat].append(issue)

    lines: list[str] = []

    # --- Header ---
    lines.append("# 功能规格书 & 寄存器手册 Review 报告")
    lines.append("")
    lines.append(f"- **规格书**: {spec_name}")
    lines.append(f"- **寄存器手册**: {reg_name}")
    lines.append("")

    # --- Summary table ---
    lines.append("## 汇总统计")
    lines.append("")
    lines.append("| 类别 | 数量 |")
    lines.append("| --- | --- |")
    for cat_key in CATEGORY_ORDER:
        label = CATEGORY_META[cat_key][0]
        count = len(grouped.get(cat_key, []))
        lines.append(f"| {label} | {count} |")
    total = len(issues)
    lines.append(f"| **合计** | **{total}** |")
    lines.append("")

    # --- Issue sections by category ---
    for cat_key in CATEGORY_ORDER:
        cat_issues = grouped.get(cat_key, [])
        if not cat_issues:
            continue
        label = CATEGORY_META[cat_key][0]
        lines.append(f"## [{cat_key}] {label}")
        lines.append("")
        for issue in cat_issues:
            _write_issue_block(lines, issue)
        lines.append("")

    # Ensure parent directory exists
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    return output_path


def _write_issue_block(lines: list[str], issue: dict[str, Any]) -> None:
    """Append a single issue block to *lines*."""
    iid = issue.get("id", "UNKNOWN")
    title = issue.get("title", "")
    feature = issue.get("feature", "")
    description = issue.get("description", "")
    suggestion = issue.get("suggestion", "")
    resolution = issue.get("resolution", "") or "待用户填写"

    lines.append(f"### {iid}: {title}")
    lines.append(f"- **关联特性**: {feature}")
    lines.append(f"- **问题描述**: {description}")
    lines.append(f"- **建议**: {suggestion}")
    lines.append(f"- **确定结果**: {resolution}")
    lines.append("")


def parse_review_for_refresh(review_path: str) -> list[dict[str, str]]:
    """Parse a filled-in review markdown and return resolved issues.

    An issue is considered "resolved" when its ``确定结果`` field has
    been changed from the default ``"待用户填写"`` to any non-empty
    value.

    Returns a list of dicts with keys ``id``, ``category``, ``title``,
    ``feature``, and ``resolution``.
    """
    with open(review_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    resolved: list[dict[str, str]] = []
    current_category = ""

    # Category header pattern: ## [spec_defect] Spec 缺陷
    cat_pattern = re.compile(r"^## \[([^\]]+)\]", re.MULTILINE)
    # Issue header pattern: ### SD-001: Missing boundary
    issue_pattern = re.compile(
        r"^###\s+(?P<id>\S+):\s*(?P<title>.+)$", re.MULTILINE
    )

    # Find all category positions first
    cat_positions: list[tuple[int, str]] = [
        (m.start(), m.group(1)) for m in cat_pattern.finditer(content)
    ]

    # Find all issue headers
    for issue_match in issue_pattern.finditer(content):
        iid = issue_match.group("id")
        title = issue_match.group("title").strip()
        block_start = issue_match.start()

        # Determine category by finding the last category header before this issue
        current_category = ""
        for pos, cat_key in cat_positions:
            if pos < block_start:
                current_category = cat_key
            else:
                break

        # Extract fields from the block after the issue header
        block_text = content[block_start:]
        # Find the end of this issue block (next ### header or EOF)
        next_issue = re.search(r"\n### ", block_text[len(issue_match.group(0)):])
        if next_issue:
            block_text = block_text[: len(issue_match.group(0)) + next_issue.start()]

        feature = _extract_field(block_text, "关联特性")
        description = _extract_field(block_text, "问题描述")
        suggestion = _extract_field(block_text, "建议")
        resolution = _extract_field(block_text, "确定结果")

        # Only include resolved issues (not the default placeholder)
        if resolution and resolution != "待用户填写":
            resolved.append({
                "id": iid,
                "category": current_category,
                "title": title,
                "feature": feature,
                "resolution": resolution,
            })

    return resolved


def _extract_field(block: str, field_name: str) -> str:
    """Extract the value of a markdown field like ``- **field_name**: value``."""
    pattern = re.compile(rf"- \*\*{re.escape(field_name)}\*\*:\s*(.+)")
    m = pattern.search(block)
    if m:
        return m.group(1).strip()
    return ""
