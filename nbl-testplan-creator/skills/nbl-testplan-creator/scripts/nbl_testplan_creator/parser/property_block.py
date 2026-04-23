"""Property block parsing via regex."""

import re

PROPERTY_RE = re.compile(r'^(?:[-|>]\s*)(\w[\w\s]*)\s*:\s*(.*)$', re.MULTILINE)


def parse_properties(text: str) -> dict[str, str]:
    """Extract '- key: value' or '> key: value' pairs from text."""
    return {m.group(1).strip(): m.group(2).strip() for m in PROPERTY_RE.finditer(text)}
