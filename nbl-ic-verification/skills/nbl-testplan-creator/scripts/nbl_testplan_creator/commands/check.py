"""Check markdown file for format issues.

Error taxonomy and fix templates are centralized in this module.
All check functions process text line-by-line via paragraphs.
"""

from pathlib import Path
from dataclasses import dataclass, field
from enum import StrEnum


# ---------------------------------------------------------------------------
# Error taxonomy
# ---------------------------------------------------------------------------

class CheckErrorType(StrEnum):
    TABLE_ROW_TRUNCATED   = "TABLE_ROW_TRUNCATED"     # row doesn't end with |
    TABLE_CONTINUATION    = "TABLE_CONTINUATION"      # orphaned continuation line
    TABLE_COLUMN_MISMATCH = "TABLE_COLUMN_MISMATCH"   # col count != header count
    TABLE_MISSING_SEP     = "TABLE_MISSING_SEPARATOR"
    TABLE_EMPTY           = "TABLE_EMPTY"               # no data rows
    ORPHAN_SUBFEATURE     = "ORPHAN_SUBFEATURE"       # ### without ##
    PROPERTY_FORMAT       = "PROPERTY_FORMAT"         # - line without ":"


# Unified hint templates indexed by error type.
FIX_TEMPLATES: dict[CheckErrorType, str] = {
    CheckErrorType.TABLE_ROW_TRUNCATED: (
        '将单元格内的换行符替换为 <br>，确保整行以 "|" 结尾；'
        '表格中的每一行必须在一行内完成，不能出现真正的换行。'
    ),
    CheckErrorType.TABLE_CONTINUATION: (
        '将当前行与上一行合并为一个完整的表格行，单元格内换行用 <br>。'
    ),
    CheckErrorType.TABLE_COLUMN_MISMATCH: (
        "排查该行是否:\n"
        '  1) 遗漏了 "|" 分隔符（最常见）\n'
        "  2) 单元格内有真实换行导致拆行\n"
        '  3) 缺少空单元格（连续两个 "|" 表示空列）'
    ),
    CheckErrorType.TABLE_MISSING_SEP: (
        '在表头行之后添加分隔行，格式: | --- | --- | ...'
    ),
    CheckErrorType.TABLE_EMPTY: (
        '表格没有数据行——通常因为前面的数据行存在格式错误被跳过导致整表为空。'
    ),
    CheckErrorType.ORPHAN_SUBFEATURE: (
        '确保每个 "### SubFeature" 前面都有一个对应的 "## Feature" 标题。'
    ),
    CheckErrorType.PROPERTY_FORMAT: (
        '属性行必须使用 "- key: value" 格式，注意冒号 " :" 不能省略。'
    ),
}


# AI-facing guidance for top-level rejection message.
AI_HINT = (
    "请将跨行的单元格内容合并为一行，并用 <br> 替代换行符；"
    "确保每个表格行末尾以 | 结尾；检查是否遗漏了 | 分隔符。"
)


@dataclass
class CheckIssue:
    line: int
    error_type: CheckErrorType
    message: str
    content: str
    hint: str = field(default="")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_separator_row(text: str) -> bool:
    cells = [c.strip() for c in text.split('|') if c.strip()]
    if not cells:
        return False
    return all(set(c) <= {'-', ':', ' ', '|'} for c in cells)


def _cell_count(text: str) -> int:
    cells = [c.strip() for c in text.strip().split('|')]
    if cells and cells[0] == '':
        cells = cells[1:]
    if cells and cells[-1] == '':
        cells = cells[:-1]
    return len(cells)


def _make_issue(
    line: int,
    error_type: CheckErrorType,
    message: str,
    content: str = "",
) -> CheckIssue:
    return CheckIssue(
        line=line,
        error_type=error_type,
        message=message,
        content=content[:80] + ('...' if len(content) > 80 else ''),
        hint=FIX_TEMPLATES.get(error_type, ""),
    )


# ---------------------------------------------------------------------------
# Core checker
# ---------------------------------------------------------------------------

def check_markdown(md_path: Path) -> tuple[list[CheckIssue], list[CheckIssue]]:
    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')
    errors: list[CheckIssue] = []
    warnings: list[CheckIssue] = []

    # --- Split into blank-line separated paragraphs ---
    paragraphs: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if line.strip() == '':
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append((i + 1, line))
    if current:
        paragraphs.append(current)

    # --- Per-paragraph table checks ---
    for para in paragraphs:
        table_rows: list[tuple[int, str]] = []
        for ln, text in para:
            stripped = text.strip()
            if stripped.startswith('|') and '|' in stripped[1:]:
                table_rows.append((ln, text))

        if not table_rows:
            continue

        # Truncated row + continuation detection
        for j, (ln, text) in enumerate(para):
            stripped = text.strip()
            if stripped.startswith('|') and not stripped.rstrip().endswith('|'):
                errors.append(_make_issue(
                    ln, CheckErrorType.TABLE_ROW_TRUNCATED,
                    '表格行缺少末尾的 "|"，单元格内容可能被截断或包含未转义的换行',
                    stripped,
                ))
                if j + 1 < len(para):
                    next_ln, next_text = para[j + 1]
                    next_stripped = next_text.strip()
                    if not next_stripped.startswith('|') and '|' in next_stripped:
                        errors.append(_make_issue(
                            next_ln, CheckErrorType.TABLE_CONTINUATION,
                            f'疑似表格续行（上一行 {ln} 缺少末尾的 "|"）',
                            next_stripped,
                        ))

        # Structural table checks
        _check_table_structure(table_rows, errors, warnings)

    # --- Heading structure check ---
    last_feature_line = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            last_feature_line = i + 1
        elif stripped.startswith('### '):
            if last_feature_line == 0:
                warnings.append(_make_issue(
                    i + 1, CheckErrorType.ORPHAN_SUBFEATURE,
                    '缺少前置 Feature (## heading) 的 SubFeature',
                    stripped,
                ))

    # --- Property block format check ---
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('> '):
            body = stripped[2:]
            if ':' not in body:
                if not body.strip().startswith(('*', '-', '+', '1.', '2.', '3.')):
                    warnings.append(_make_issue(
                        i + 1, CheckErrorType.PROPERTY_FORMAT,
                        '属性行缺少 ":" 分隔符，可能不是有效的 key: value 格式',
                        stripped,
                    ))

    return errors, warnings


def _check_table_structure(
    table_rows: list[tuple[int, str]],
    errors: list[CheckIssue],
    warnings: list[CheckIssue],
) -> None:
    if not table_rows:
        return

    # Locate separator row
    sep_idx: int | None = None
    for idx, (ln, text) in enumerate(table_rows):
        if _is_separator_row(text):
            sep_idx = idx
            break

    if sep_idx is None:
        errors.append(_make_issue(
            table_rows[0][0], CheckErrorType.TABLE_MISSING_SEP,
            '表格缺少分隔行 (|---|---|)',
            table_rows[0][1].strip(),
        ))

    # Header column count
    header_col_count: int | None = None
    if sep_idx is not None and sep_idx > 0:
        header_col_count = _cell_count(table_rows[0][1])
    elif sep_idx is None and len(table_rows) > 0:
        header_col_count = _cell_count(table_rows[0][1])

    # Count data rows
    if sep_idx is not None:
        data_rows = sum(
            1 for j in range(sep_idx + 1, len(table_rows))
            if not _is_separator_row(table_rows[j][1])
        )
    else:
        data_rows = sum(
            1 for j in range(1, len(table_rows))
            if not _is_separator_row(table_rows[j][1])
        )

    for idx, (ln, text) in enumerate(table_rows):
        if _is_separator_row(text):
            # 新增：分隔行也需验证列数与表头匹配
            sep_count = _cell_count(text)
            if header_col_count is not None and sep_count != header_col_count:
                errors.append(_make_issue(
                    ln, CheckErrorType.TABLE_COLUMN_MISMATCH,
                    f'分隔行列数不匹配: 表头 {header_col_count} 列, 分隔行 {sep_count} 列',
                    text.strip(),
                ))
            continue
        if sep_idx is not None and idx < sep_idx:
            continue

        if header_col_count is not None:
            count = _cell_count(text)
            if count != header_col_count:
                errors.append(_make_issue(
                    ln, CheckErrorType.TABLE_COLUMN_MISMATCH,
                    f'表格列数不匹配: 表头 {header_col_count} 列, 当前行 {count} 列',
                    text.strip(),
                ))

    if data_rows == 0:
        warnings.append(_make_issue(
            table_rows[0][0], CheckErrorType.TABLE_EMPTY,
            '表格没有数据行',
            table_rows[0][1].strip(),
        ))


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

def _print_issues(issues: list[CheckIssue], label: str, icon: str) -> None:
    print(f"{icon} 发现 {len(issues)} 个{label}:")
    for e in issues:
        print(f"  [{label.upper()}] 第 {e.line} 行 | {e.error_type}")
        if e.content:
            print(f"    内容: {e.content}")
        print(f"    问题: {e.message}")
        if e.hint:
            print(f"    修复: {e.hint}")
        print()


def _print_fail_banner() -> None:
    print("请先修复上述格式问题后再执行 build/merge 命令。")
    print(f"AI 提示: {AI_HINT}")


def cmd_check(_manager, args) -> int:
    md_file = Path(args.md_file)
    if not md_file.exists():
        print(f"错误: 文件不存在: {md_file}")
        return 1

    errors, warnings = check_markdown(md_file)

    if not errors and not warnings:
        print(f"✅ {md_file.name} 格式检查通过，无问题")
        return 0

    if errors:
        _print_issues(errors, "错误", "❌")
    if warnings:
        _print_issues(warnings, "警告", "⚠️")

    if errors:
        _print_fail_banner()
        return 1
    return 0
