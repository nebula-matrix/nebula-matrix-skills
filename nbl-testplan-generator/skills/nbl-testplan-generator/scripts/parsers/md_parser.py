#!/usr/bin/env python3
"""md_parser.py - Parse Markdown specification into structured JSON.

This parser processes Markdown files converted from docx by nbl-docx-to-markdown.
"""
import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_markdown(filepath: str) -> dict[str, Any]:
    """Parse a Markdown functional specification into a hierarchical dictionary.

    Returns a dict with keys:
        document_title, total_lines, feature_ids, sections, tables
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    feature_pattern = re.compile(r"【(\w+\.\d+)】")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
    table_row_pattern = re.compile(r"^\|(.+)\|$")
    table_separator = re.compile(r"^\|[-:|]+\|$")

    result: dict[str, Any] = {
        "document_title": filepath.stem.replace("_work/markdown_output/", "").replace("_work\\markdown_output\\", ""),
        "total_lines": len(lines),
        "feature_ids": [],
        "sections": [],
        "tables": [],
    }

    # Parse tables first (HTML tables from pandoc)
    content = "".join(lines)

    # Extract HTML tables
    html_table_pattern = re.compile(r"<table[^>]*>.*?</table>", re.DOTALL | re.IGNORECASE)
    html_tables = html_table_pattern.findall(content)
    for idx, table_html in enumerate(html_tables):
        rows = []
        row_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
        for row_match in row_pattern.finditer(table_html):
            cell_pattern = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL | re.IGNORECASE)
            cells = []
            for cell_match in cell_pattern.finditer(row_match.group(1)):
                cell_text = re.sub(r"<[^>]+>", "", cell_match.group(1)).strip()
                cells.append(cell_text)
            if cells:
                rows.append(cells)
        if rows:
            result["tables"].append({"table_index": idx, "rows": rows})

    # Extract Markdown tables
    md_table_pattern = re.compile(r"(\|[^\n]+\|\n)+", re.MULTILINE)
    for match in md_table_pattern.finditer(content):
        table_block = match.group(0)
        rows = []
        for line in table_block.strip().split("\n"):
            if table_separator.match(line):
                continue
            if table_row_pattern.match(line):
                cells = [c.strip() for c in line.strip("|").split("|")]
                rows.append(cells)
        if rows:
            result["tables"].append({"table_index": len(result["tables"]), "rows": rows})

    # Build hierarchical section structure
    current_section: dict[str, Any] | None = None
    current_subsection: dict[str, Any] | None = None
    current_subsubsection: dict[str, Any] | None = None
    current_content: list[dict[str, Any]] = []
    current_sub_content: list[dict[str, Any]] = []
    current_subsub_content: list[dict[str, Any]] = []

    def flush_content() -> None:
        nonlocal current_content, current_sub_content, current_subsub_content
        if current_subsubsection is not None:
            current_subsubsection["content"] = current_subsub_content
            current_subsub_content = []
        elif current_subsection is not None:
            current_subsection["content"] = current_sub_content
            current_sub_content = []
        elif current_section is not None:
            current_section["content"] = current_content
            current_content = []

    for line in lines:
        line = line.rstrip("\n")
        heading_match = heading_pattern.match(line)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            features = feature_pattern.findall(title)

            flush_content()

            if level == 1:
                current_section = {
                    "level": 1,
                    "title": title,
                    "children": [],
                    "content": [],
                }
                result["sections"].append(current_section)
                current_subsection = None
                current_subsubsection = None
            elif level == 2:
                if current_section is None:
                    continue
                if current_subsubsection is not None and current_subsection is not None:
                    current_subsection["children"].append(current_subsubsection)
                    current_subsubsection = None
                if current_subsection is not None:
                    current_subsection["content"] = current_sub_content
                    current_sub_content = []
                    current_section["children"].append(current_subsection)
                current_subsection = {
                    "level": 2,
                    "title": title,
                    "children": [],
                    "content": [],
                }
                current_subsubsection = None
            elif level == 3:
                if current_subsection is None:
                    continue
                if current_subsubsection is not None:
                    current_subsection["children"].append(current_subsubsection)
                current_subsubsection = {"level": 3, "title": title, "content": []}
        else:
            text = line.strip()
            features = feature_pattern.findall(text)
            if not text and not features:
                continue

            entry: dict[str, Any] = {"text": text}
            if features:
                entry["feature_ids"] = features
                result["feature_ids"].extend(features)
            if current_subsubsection is not None:
                current_subsub_content.append(entry)
            elif current_subsection is not None:
                current_sub_content.append(entry)
            elif current_section is not None:
                current_content.append(entry)

    # Flush remaining content
    if current_subsubsection is not None and current_subsection is not None:
        current_subsubsection["content"] = current_subsub_content
        current_subsection["children"].append(current_subsubsection)
    if current_subsection is not None and current_section is not None:
        current_subsection["content"] = current_sub_content
        current_section["children"].append(current_subsection)
    if current_section is not None:
        current_section["content"] = current_content

    # Deduplicate feature_ids
    result["feature_ids"] = list(dict.fromkeys(result["feature_ids"]))

    return result


def get_section_by_title(parsed: dict[str, Any], title_keyword: str) -> dict[str, Any] | None:
    """Find a section whose title contains the keyword."""
    for section in parsed["sections"]:
        if title_keyword in section["title"]:
            return section
        for child in section.get("children", []):
            if title_keyword in child["title"]:
                return child
            for grandchild in child.get("children", []):
                if title_keyword in grandchild["title"]:
                    return grandchild
    return None


def get_features_section(parsed: dict[str, Any]) -> dict[str, Any] | None:
    """Return the '模块特性' section."""
    return get_section_by_title(parsed, "模块特性")


def get_functional_details_section(parsed: dict[str, Any]) -> dict[str, Any] | None:
    """Return the '功能详述' section."""
    return get_section_by_title(parsed, "功能详述")


def get_parameters_section(parsed: dict[str, Any]) -> dict[str, Any] | None:
    """Return the '参数列表' section."""
    return get_section_by_title(parsed, "参数列表")


def extract_feature_map(features_section: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    """Extract a mapping of feature_id -> {description, raw_text}."""
    feature_map: dict[str, dict[str, str]] = {}
    if not features_section:
        return feature_map

    def _extract(content_list: list[dict[str, Any]]) -> None:
        for entry in content_list:
            for fid in entry.get("feature_ids", []):
                desc = re.sub(r"【\w+\.\d+】", "", entry["text"]).strip()
                feature_map[fid] = {
                    "description": desc,
                    "raw_text": entry["text"],
                }

    _extract(features_section.get("content", []))
    for child in features_section.get("children", []):
        _extract(child.get("content", []))
        for grandchild in child.get("children", []):
            _extract(grandchild.get("content", []))
    return feature_map


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_parser.py <input.md> [output.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = parse_markdown(input_path)

    print(f"Document: {result['document_title']}")
    print(f"Lines: {result['total_lines']}")
    print(f"Tables: {len(result['tables'])}")
    print(f"Sections: {[s['title'] for s in result['sections']]}")
    print(f"Feature IDs: {result['feature_ids']}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
