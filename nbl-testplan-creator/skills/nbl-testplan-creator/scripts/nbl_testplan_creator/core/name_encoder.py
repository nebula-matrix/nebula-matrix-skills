"""Shared name encoding utilities."""

import re

ENCODE_RE = re.compile(r'[\s.]+')
STRIP_HEADING_RE = re.compile(r'^\d+(?:\.\d+)*\.?\s*')


def encode_name(name: str) -> str:
    """Encode a name for use as an ID: strip whitespace and dots, lowercase."""
    return ENCODE_RE.sub('', name.strip()).lower()


def strip_heading_number(text: str) -> str:
    """Strip leading numeric section numbers like '1.', '1.1.', '3.1' from heading text."""
    return STRIP_HEADING_RE.sub('', text).strip()
