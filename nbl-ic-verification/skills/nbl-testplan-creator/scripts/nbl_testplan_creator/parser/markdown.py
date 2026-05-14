"""Unified markdown document parser."""

from dataclasses import dataclass, field

from .heading import split_by_headings
from .property_block import parse_properties
from .table import parse_table
from nbl_testplan_creator.core.name_encoder import strip_heading_number


@dataclass
class SubFeatureBlock:
    heading: str
    properties: dict[str, str] = field(default_factory=dict)
    tables: list[dict] = field(default_factory=list)


@dataclass
class FeatureBlock:
    heading: str
    properties: dict[str, str] = field(default_factory=dict)
    subfeatures: list[SubFeatureBlock] = field(default_factory=list)
    pre_body: list[str] = field(default_factory=list)


def parse_markdown_document(text: str) -> dict:
    """
    Parse a full markdown document into structured blocks.

    Returns:
        {
            'title': str | None,
            'metadata': str | None,
            'features': list[FeatureBlock],
        }
    """
    text = text.lstrip('﻿')

    # Extract title (# Title)
    title = None
    lines = text.split('\n')
    title_end = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('##'):
            title = stripped[2:].strip()
            title_end = i + 1
            break

    # Everything from title_end onward: split by ## headings
    body_text = '\n'.join(lines[title_end:])
    heading_blocks = split_by_headings(body_text, min_level=2, max_level=3)

    # Detect metadata: text between title and first ## Feature
    metadata = None
    if heading_blocks:
        first_feature_pos = heading_blocks[0].start
        if first_feature_pos > 0:
            raw_meta = body_text[:first_feature_pos].strip('\n')
            if raw_meta.strip():
                metadata = raw_meta

    # Group blocks: level 2 = feature, level 3 = subfeature under current feature
    features: list[FeatureBlock] = []
    current_feature: FeatureBlock | None = None

    for block in heading_blocks:
        clean_heading = strip_heading_number(block.text)

        if block.level == 2:
            current_feature = FeatureBlock(
                heading=clean_heading,
                properties=parse_properties(block.body),
            )
            # Find any tables at feature level (orphaned testpoints)
            tbl = parse_table(block.body)
            if tbl:
                current_feature.subfeatures.append(
                    SubFeatureBlock(heading='', properties={}, tables=[tbl])
                )
            features.append(current_feature)

        elif block.level == 3:
            if current_feature is None:
                continue
            sf = SubFeatureBlock(
                heading=clean_heading,
                properties=parse_properties(block.body),
            )
            tbl = parse_table(block.body)
            if tbl:
                sf.tables.append(tbl)
            current_feature.subfeatures.append(sf)

    return {
        'title': title,
        'metadata': metadata,
        'features': features,
    }
