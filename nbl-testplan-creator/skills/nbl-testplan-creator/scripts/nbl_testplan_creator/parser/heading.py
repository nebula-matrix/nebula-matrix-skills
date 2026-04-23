"""Markdown heading parsing via regex."""

from dataclasses import dataclass
import re

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*$', re.MULTILINE)


@dataclass
class HeadingBlock:
    level: int
    text: str
    start: int       # start index in original text
    end: int         # end index (exclusive, up to next heading or EOF)
    body: str        # text between this heading and next


def split_by_headings(text: str, min_level: int = 1, max_level: int = 6) -> list[HeadingBlock]:
    """Split text into sections by markdown headings."""
    text = text.lstrip('﻿')
    matches = list(HEADING_RE.finditer(text))
    blocks = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        if not (min_level <= level <= max_level):
            continue
        start = m.end() + 1
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip('\n')
        blocks.append(HeadingBlock(
            level=level,
            text=m.group(2),
            start=m.start(),
            end=end,
            body=body,
        ))
    return blocks
