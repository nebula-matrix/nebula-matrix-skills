#!/usr/bin/env python3
"""md_parser.py - Parse Markdown specification into structured JSON.

This parser processes Markdown files converted from docx by nbl-docx-to-markdown.
Extracts Feature IDs (【PA.XXX】), hierarchical sections, and tables.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_markdown(filepath: str | Path) -> dict[str, Any]:
    """Parse a Markdown functional specification into a hierarchical dictionary.

    Parameters
    ----------
    filepath : str | Path
        Path to the markdown file.

    Returns
    -------
    dict
        Contains: document_title, total_lines, feature_ids, sections, tables
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Pattern for 【PA.XXX】 format in body text
    feature_pattern = re.compile(r"【(\w+\.\d+)】")
    # Pattern for PA.XXX format in headings (without brackets)
    heading_feature_pattern = re.compile(r"\b(\w+\.\d+)\b")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    result: dict[str, Any] = {
        "document_title": filepath.stem,
        "total_lines": len(lines),
        "feature_ids": [],
        "sections": [],
        "tables": [],
        "feature_content": {},
    }

    # Parse line by line
    current_section: dict[str, Any] | None = None
    current_subsection: dict[str, Any] | None = None
    current_feature: str | None = None
    current_feature_content: list[str] = []

    def _save_feature_content():
        nonlocal current_feature, current_feature_content
        if current_feature and current_feature_content:
            text = "\n".join(current_feature_content)
            result["feature_content"][current_feature] = {
                "text": text,
                "registers": _extract_registers(text),
            }
        current_feature_content = []

    for line in lines:
        line = line.rstrip("\n")
        heading_match = heading_pattern.match(line)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            # Try both patterns for headings: 【PA.XXX】 and PA.XXX
            features = feature_pattern.findall(title)
            if not features:
                features = heading_feature_pattern.findall(title)

            # Save previous feature content
            _save_feature_content()

            if level == 1:
                current_section = {
                    "level": 1,
                    "title": title,
                    "children": [],
                }
                result["sections"].append(current_section)
                current_subsection = None
            elif level == 2:
                if current_section is None:
                    continue
                current_subsection = {
                    "level": 2,
                    "title": title,
                    "children": [],
                }
                current_section["children"].append(current_subsection)

            if features:
                current_feature = features[0]
                result["feature_ids"].extend(features)
        else:
            text = line.strip()
            features = feature_pattern.findall(text)

            if features:
                _save_feature_content()
                current_feature = features[0]
                result["feature_ids"].extend(features)

            if current_feature and text:
                current_feature_content.append(text)

    # Save last feature content
    _save_feature_content()

    # Deduplicate feature_ids
    result["feature_ids"] = list(dict.fromkeys(result["feature_ids"]))

    return result


def _extract_registers(text: str) -> list[str]:
    """Extract register names from text (pattern: upa_xxx)."""
    pattern = re.compile(r"(upa_\w+)")
    return list(dict.fromkeys(pattern.findall(text)))


def extract_feature_ids(filepath: str | Path) -> list[str]:
    """Extract all feature IDs from a markdown file.

    Parameters
    ----------
    filepath : str | Path
        Path to the markdown file.

    Returns
    -------
    list[str]
        List of feature IDs (e.g., ['PA.001', 'PA.002'])
    """
    result = parse_markdown(filepath)
    return result["feature_ids"]


def get_feature_content(parsed: dict[str, Any], feature_id: str) -> dict[str, Any] | None:
    """Get content for a specific feature ID from parsed data.

    Parameters
    ----------
    parsed : dict
        Parsed markdown data from parse_markdown()
    feature_id : str
        Feature ID to look up (e.g., 'PA.001')

    Returns
    -------
    dict | None
        Dict with 'text' and 'registers' keys, or None if not found
    """
    return parsed.get("feature_content", {}).get(feature_id)


def get_section_by_title(parsed: dict[str, Any], title_keyword: str) -> dict[str, Any] | None:
    """Find a section whose title contains the keyword."""
    for section in parsed.get("sections", []):
        if title_keyword in section.get("title", ""):
            return section
        for child in section.get("children", []):
            if title_keyword in child.get("title", ""):
                return child
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_parser.py <input.md> [output.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = parse_markdown(input_path)

    print(f"Document: {result['document_title']}")
    print(f"Lines: {result['total_lines']}")
    print(f"Feature IDs: {result['feature_ids']}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
