"""Markdown table parse and render."""


def parse_table(text: str) -> dict | None:
    """
    Parse first markdown table found in text.
    Returns {'headers': [...], 'rows': [...]} or None.
    """
    lines = text.split('\n')
    table_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('|') and '|' in stripped[1:]:
            if table_start is None:
                table_start = i
        elif table_start is not None:
            break
    if table_start is None:
        return None

    table_end = len(lines)
    for i in range(table_start + 1, len(lines)):
        if not lines[i].strip().startswith('|'):
            table_end = i
            break

    table_lines = [l.strip() for l in lines[table_start:table_end] if l.strip()]
    if not table_lines:
        return None

    # Parse header
    headers = [cell.strip() for cell in table_lines[0].split('|')]
    headers = [h for h in headers if h]

    rows = []
    for line in table_lines[1:]:
        cells_raw = [c.strip() for c in line.split('|')]
        # Drop empty cells caused by leading/trailing pipes, keep empty middle cells
        if cells_raw and cells_raw[0] == '':
            cells_raw = cells_raw[1:]
        if cells_raw and cells_raw[-1] == '':
            cells_raw = cells_raw[:-1]
        if not cells_raw:
            continue
        if all(set(c) <= {'-', ':', ' ', '|'} for c in cells_raw):
            continue
        if len(cells_raw) == len(headers):
            rows.append(dict(zip(headers, cells_raw)))

    return {'headers': headers, 'rows': rows}


def render_table(headers: list[str], rows: list[dict], **field_overrides) -> list[str]:
    """Generate markdown table lines from headers and row dicts."""
    lines = []
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(" --- " for _ in headers) + "|"
    lines.append(header_line)
    lines.append(sep_line)

    for row in rows:
        cells = []
        for h in headers:
            v = str(row.get(h, field_overrides.get(h, '')))
            v = v.replace('\n', '<br>')
            v = v.replace('|', '\\|')
            cells.append(v)
        lines.append("| " + " | ".join(cells) + " |")

    return lines
