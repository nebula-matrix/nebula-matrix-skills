#!/usr/bin/env python3
"""func_writer.py - Generate Ch1 features from parsed markdown and register data.

This module generates the D-E-F-G hierarchy structure for Chapter 1 features:
- D: Feature (level 0) - Main feature from spec
- E: Subfeature L1 (level 1) - First level subfeature
- F: Subfeature L2 (level 2) - Second level subfeature
- G: Subfeature L3 (level 3) - Third level subfeature (optional)

Cross-references features with related registers and generates stimulus/checking.
"""
from __future__ import annotations

import re
from typing import Any


def generate_ch1_features(
    parsed_md: dict[str, Any],
    parsed_reg: dict[str, Any],
) -> dict[str, Any]:
    """Generate Chapter 1 features from parsed markdown and register data.

    Parameters
    ----------
    parsed_md : dict
        Parsed markdown data from md_parser.parse_markdown().
    parsed_reg : dict
        Parsed register data from reg_to_json.parse_register_xlsx().

    Returns
    -------
    dict
        Features data structure with module_name, spec_name, chapter, features.
    """
    # Extract module and spec info
    document_title = parsed_md.get("document_title", "Unknown")
    spec_name = _extract_spec_name(parsed_md) or document_title
    module_name = _extract_module_name(spec_name)

    # Build the D-E-F-G hierarchy
    features = _build_hierarchy(parsed_md)

    # Cross-reference with registers
    features = _cross_reference_registers(features, parsed_md, parsed_reg)

    # Generate stimulus and checking for each L2/L3
    features = _generate_test_info(features, parsed_md, parsed_reg)

    return {
        "module_name": module_name,
        "spec_name": spec_name,
        "chapter": "chapter 1 功能特性",
        "features": features,
    }


def _extract_spec_name(parsed_md: dict[str, Any]) -> str | None:
    """Extract spec name from parsed markdown sections."""
    sections = parsed_md.get("sections", [])
    for section in sections:
        title = section.get("title", "")
        # Look for level 1 heading as spec name
        if section.get("level") == 1:
            return title
    return None


def _extract_module_name(spec_name: str) -> str:
    """Extract module name from spec name."""
    # Try to extract module prefix like "UPA" from title
    match = re.match(r"^([A-Z]{2,})", spec_name)
    if match:
        return match.group(1)
    # Fallback: use first word
    return spec_name.split()[0] if spec_name else "Unknown"


def _build_hierarchy(parsed_md: dict[str, Any]) -> list[dict[str, Any]]:
    """Build D-E-F-G hierarchy from parsed markdown.

    D (Feature): Extracted from feature IDs like PA.001
    E (L1): Sub-features from section hierarchy
    F (L2): Detailed features
    G (L3): Most detailed test points (optional)
    """
    features: list[dict[str, Any]] = []
    feature_ids = parsed_md.get("feature_ids", [])
    feature_content = parsed_md.get("feature_content", {})
    sections = parsed_md.get("sections", [])

    # Build a mapping of feature_id to section title
    feature_section_map = _map_features_to_sections(parsed_md)

    for feature_id in feature_ids:
        content = feature_content.get(feature_id, {})
        section_title = feature_section_map.get(feature_id, "")

        # Extract feature name from section title or content
        feature_name = _extract_feature_name(feature_id, section_title, content)

        # Build L1 subfeatures from content
        subfeatures_l1 = _build_l1_subfeatures(feature_id, content, parsed_md)

        feature_entry = {
            "feature": feature_name,
            "feature_id": feature_id,
            "chapter": "chapter 1 功能特性",
            "subfeatures_l1": subfeatures_l1,
        }
        features.append(feature_entry)

    return features


def _map_features_to_sections(parsed_md: dict[str, Any]) -> dict[str, str]:
    """Map feature IDs to their containing section titles."""
    mapping: dict[str, str] = {}
    sections = parsed_md.get("sections", [])

    for section in sections:
        title = section.get("title", "")
        for child in section.get("children", []):
            child_title = child.get("title", "")
            # Check if child title contains feature ID pattern
            match = re.search(r"(PA\.\d+|【PA\.\d+】)", child_title)
            if match:
                feature_id = match.group(1).replace("【", "").replace("】", "")
                mapping[feature_id] = child_title

    return mapping


def _extract_feature_name(
    feature_id: str,
    section_title: str,
    content: dict[str, Any],
) -> str:
    """Extract feature name from section title or content."""
    # Try to extract from section title (e.g., "1.1 数据通路特性")
    match = re.match(r"^\d+\.\d+\s+(.+)$", section_title)
    if match:
        return match.group(1)

    # Try to extract from content text
    text = content.get("text", "")
    lines = text.split("\n")
    if lines:
        first_line = lines[0].strip()
        # Remove feature ID prefix if present
        first_line = re.sub(r"【?PA\.\d+】?\s*", "", first_line)
        if first_line:
            return first_line[:50]  # Limit length

    # Fallback: use feature_id
    return f"Feature {feature_id}"


def _build_l1_subfeatures(
    feature_id: str,
    content: dict[str, Any],
    parsed_md: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build L1 subfeatures for a feature."""
    text = content.get("text", "")
    registers = content.get("registers", [])

    # Extract L1 name from content
    # Typically: "支持单向数据传输" style descriptions
    l1_name = _extract_l1_name(text)

    # Build L2 subfeatures
    subfeatures_l2 = _build_l2_subfeatures(feature_id, text, registers)

    if not l1_name and not subfeatures_l2:
        return []

    return [{
        "subfeature_l1": l1_name,
        "subfeatures_l2": subfeatures_l2,
    }]


def _extract_l1_name(text: str) -> str:
    """Extract L1 subfeature name from text."""
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        # Look for patterns like "支持xxx" or "xxx功能"
        if line and not line.startswith("相关寄存器"):
            # Remove feature ID prefix
            line = re.sub(r"【?PA\.\d+】?\s*", "", line)
            if line and len(line) > 2:
                return line[:50]
    return ""


def _build_l2_subfeatures(
    feature_id: str,
    text: str,
    registers: list[str],
) -> list[dict[str, Any]]:
    """Build L2 subfeatures from feature content."""
    # Parse the text to extract overview and detail
    lines = text.split("\n")

    overview = ""
    detail = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("相关寄存器"):
            continue
        # Remove feature ID prefix
        line = re.sub(r"【?PA\.\d+】?\s*", "", line)
        if line.startswith("-") or line.startswith("•"):
            continue  # Skip register list items

        if not overview:
            overview = line
        elif not detail:
            detail = line
            break

    if not overview:
        overview = f"功能验证 {feature_id}"

    return [{
        "subfeature_l2_overview": overview,
        "subfeature_l2_detail": detail,
        "subfeatures_l3": [],  # No L3 for simple features
    }]


def _cross_reference_registers(
    features: list[dict[str, Any]],
    parsed_md: dict[str, Any],
    parsed_reg: dict[str, Any],
) -> list[dict[str, Any]]:
    """Cross-reference features with related registers.

    For each L2 subfeature, add related register information.
    """
    feature_content = parsed_md.get("feature_content", {})
    registers_dict = parsed_reg.get("name_index", {})

    for feature in features:
        feature_id = feature.get("feature_id", "")
        content = feature_content.get(feature_id, {})
        related_registers = content.get("registers", [])

        for l1 in feature.get("subfeatures_l1", []):
            for l2 in l1.get("subfeatures_l2", []):
                # Add related registers to L2
                l2["related_registers"] = related_registers

                # Find register details
                reg_details = []
                for reg_name in related_registers:
                    if reg_name in registers_dict:
                        reg_idx = registers_dict[reg_name]
                        reg_list = parsed_reg.get("registers", [])
                        if reg_idx < len(reg_list):
                            reg_details.append(reg_list[reg_idx])
                l2["register_details"] = reg_details

    return features


def _generate_test_info(
    features: list[dict[str, Any]],
    parsed_md: dict[str, Any],
    parsed_reg: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate stimulus, checking, and other test info for L2 subfeatures."""
    for feature in features:
        feature_id = feature.get("feature_id", "")

        for l1 in feature.get("subfeatures_l1", []):
            for l2 in l1.get("subfeatures_l2", []):
                # Generate stimulus
                stimulus = _generate_stimulus(feature_id, l2, parsed_reg)
                l2["stimulus"] = stimulus

                # Generate checking
                checking = _generate_checking(feature_id, l2)
                l2["checking"] = checking

                # Generate other fields
                l2["remarks"] = f"来源: {feature_id}"
                l2["coverage"] = _generate_coverage(l2)
                l2["priority"] = "HIGH"
                l2["activity"] = "BT"
                l2["path"] = ""

    return features


def _generate_stimulus(
    feature_id: str,
    l2: dict[str, Any],
    parsed_reg: dict[str, Any],
) -> str:
    """Generate stimulus string for a subfeature."""
    registers = l2.get("related_registers", [])

    if not registers:
        return f"【配置】使能{feature_id}功能"

    # Build stimulus from registers
    config_parts = []
    for reg_name in registers[:2]:  # Limit to first 2 registers
        # Find register details
        reg_idx = parsed_reg.get("name_index", {}).get(reg_name)
        if reg_idx is not None:
            reg_list = parsed_reg.get("registers", [])
            if reg_idx < len(reg_list):
                reg = reg_list[reg_idx]
                # Find enable field
                for field in reg.get("fields", []):
                    if field.get("name", "").lower() in ["en", "enable"]:
                        config_parts.append(f"配置{reg_name}.{field['name']}=1")
                        break

    if config_parts:
        return f"【配置】" + ", ".join(config_parts)
    else:
        return f"【配置】配置{registers[0]}"


def _generate_checking(feature_id: str, l2: dict[str, Any]) -> str:
    """Generate checking string for a subfeature."""
    # Default checking method
    return "by_direct_tc"


def _generate_coverage(l2: dict[str, Any]) -> str:
    """Generate coverage string for a subfeature."""
    registers = l2.get("related_registers", [])
    overview = l2.get("subfeature_l2_overview", "")

    if registers:
        return f"{registers[0]}覆盖率"
    elif overview:
        return f"{overview[:20]}覆盖率"
    else:
        return "功能覆盖率"


# Public helper functions for testing
def get_feature_by_id(features_data: dict[str, Any], feature_id: str) -> dict[str, Any] | None:
    """Get a feature by its ID from features data."""
    for feature in features_data.get("features", []):
        if feature.get("feature_id") == feature_id:
            return feature
    return None


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    from md_parser import parse_markdown
    from reg_to_json import parse_register_xlsx

    if len(sys.argv) < 3:
        print("Usage: python func_writer.py <spec.md> <reg.xlsx> [output.json]")
        sys.exit(1)

    spec_path = sys.argv[1]
    reg_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    parsed_md = parse_markdown(spec_path)
    parsed_reg = parse_register_xlsx(reg_path)

    result = generate_ch1_features(parsed_md, parsed_reg)

    print(f"Module: {result['module_name']}")
    print(f"Spec: {result['spec_name']}")
    print(f"Features: {len(result['features'])}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
