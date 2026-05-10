#!/usr/bin/env python3
"""md_parser.py - Parse Markdown spec into spec_tree.json structure.

Reads a Markdown file (converted from docx by nbl-docx-to-markdown),
extracts chapters, feature tree, and cross-reference index.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def parse_spec_tree(filepath: str | Path) -> dict[str, Any]:
    """Parse a Markdown functional spec into spec_tree.json."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    # Extract document title from first H1
    spec_title = filepath.stem
    for line in lines:
        if line.startswith("# "):
            spec_title = line[2:].strip()
            break

    # Build chapter list with content segments
    chapters: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    chapter_counter = 0

    for line in lines:
        heading_match = heading_pattern.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            chapter_counter += 1
            if current is not None:
                current["content_md"] = "\n".join(current["_lines"])
            new_chapter = {
                "chapter_id": f"ch{chapter_counter}",
                "chapter_title": title,
                "outline_level": level - 1,
                "content_md": "",
                "features": [],
                "_lines": [],
            }
            chapters.append(new_chapter)
            current = new_chapter
        elif current is not None:
            current["_lines"].append(line)

    if current is not None:
        current["content_md"] = "\n".join(current["_lines"])

    # Identify module_features chapter
    module_features_ch = None
    for ch in chapters:
        if "模块特性" in ch["chapter_title"]:
            module_features_ch = ch
            break

    # Extract features from all chapter contents
    all_content = "\n".join(ch["content_md"] for ch in chapters)
    features = _extract_features(all_content)
    if module_features_ch is not None:
        module_features_ch["features"] = features

    # Build feature-specific cross-reference index
    _build_refs(chapters, features)

    # Cleanup
    for ch in chapters:
        del ch["_lines"]

    # Derive module name from spec_title
    module_name = _infer_module_name(spec_title)

    return {
        "module_name": module_name,
        "spec_title": spec_title,
        "chapters": chapters,
    }


def _extract_features(content: str) -> list[dict[str, Any]]:
    """Extract feature items from the '模块特性' chapter content."""
    features: list[dict[str, Any]] = []
    feature_pattern = re.compile(r"【(\w+\.\d+)】\s*(.+?)$", re.MULTILINE)
    for match in feature_pattern.finditer(content):
        fid = match.group(1)
        fname = match.group(2).strip()
        features.append({
            "feature_id": fid,
            "feature_name": fname,
            "content_md": f"【{fid}】{fname}",
            "refs": {
                "detail_chapters": [],
                "data_structure_chapters": [],
                "init_chapters": [],
                "error_chapters": [],
                "ctrl_chapters": [],
                "dft_chapters": [],
                "limit_chapters": [],
            }
        })
    return features


def _build_refs(chapters: list, features: list) -> None:
    """Build cross-reference refs for each feature."""
    for feat in features:
        keywords = _extract_keywords(feat["feature_name"])
        feat_id = feat["feature_id"]
        for ch in chapters:
            ch_title = ch["chapter_title"]
            ch_content = ch["content_md"]

            if "模块特性" in ch_title:
                continue

            matched = False
            if any(kw in ch_title for kw in keywords):
                matched = True

            if not matched and feat_id in ch_content:
                matched = True

            if matched:
                category = _classify_chapter(ch_title)
                feat["refs"][f"{category}_chapters"].append(ch["chapter_id"])


def _extract_keywords(feature_name: str) -> list[str]:
    """Extract meaningful keywords from a feature name."""
    stop_words = {"\"", "实现", "功能", "机制", "特性", "的", "和", "与"}
    words = feature_name.split()
    keywords = [w for w in words if w not in stop_words and len(w) >= 2]
    return keywords if keywords else words


def _classify_chapter(title: str) -> str:
    """Classify a chapter into a reference category."""
    title_norm = title.lower()
    if any(k in title_norm for k in ("详述", "详细", "detail", "功能详述")):
        return "detail"
    elif any(k in title_norm for k in ("数据结构", "data structure", "格式")):
        return "data_structure"
    elif any(k in title_norm for k in ("初始化", "init", "启动")):
        return "init"
    elif any(k in title_norm for k in ("错误", "error", "异常", "故障", "fault")):
        return "error"
    elif any(k in title_norm for k in ("流控", "流控制", "ctrl", "control", "使能")):
        return "ctrl"
    elif any(k in title_norm for k in ("dft", "dfx", "可测试", "debug")):
        return "dft"
    elif any(k in title_norm for k in ("限制", "limit", "约束", "要求")):
        return "limit"
    else:
        return "detail"


def _infer_module_name(spec_title: str) -> str:
    """Infer short module name from spec title."""
    title_lower = spec_title.lower()
    name_map = {
        "upa": ("upa", "pa", "datapath_upa"),
        "dped": ("dped", "ped", "datapath_dped"),
    }
    for name, keywords in name_map.items():
        if any(k in title_lower for k in keywords):
            return name
    import re as _re
    letters = _re.findall(r"[a-z]+", title_lower)
    return letters[0] if letters else "module"


def get_feature_by_id(spec_tree: dict, feature_id: str) -> dict | None:
    """Look up a feature by its ID in spec_tree."""
    for ch in spec_tree.get("chapters", []):
        for feat in ch.get("features", []):
            if feat.get("feature_id") == feature_id:
                return feat
    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python md_parser.py <spec.md>")
        sys.exit(1)
    result = parse_spec_tree(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
