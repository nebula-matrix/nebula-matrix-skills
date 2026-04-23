"""Shared validation utilities."""

import re

VALID_PRIORITIES = frozenset({'HIGH', 'MID', 'LOW'})


def validate_priority(value: str) -> str:
    """Validate and canonicalize priority value."""
    v = value.strip().upper()
    if v not in VALID_PRIORITIES:
        raise ValueError(f"无效的优先级 '{value}'，可选: HIGH, MID, LOW")
    return v


def validate_checking(value: str) -> str:
    """Validate checking is non-empty."""
    v = value.strip()
    if not v:
        raise ValueError("checking 不能为空")
    return v


def parse_sections(value: str) -> list[str]:
    """Parse comma-separated SXXX section identifiers."""
    result = []
    for part in value.split(','):
        s = part.strip()
        if not s:
            continue
        if not re.match(r'^S\d+$', s):
            raise ValueError(f"无效的章节编号: {s}")
        result.append(s)
    return result


def parse_bool(value: str) -> bool:
    """Parse a string as a boolean."""
    return value.strip().lower() in ('true', 'yes', '1', 'skip')
