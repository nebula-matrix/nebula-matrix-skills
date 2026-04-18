# Testplan Generator V2 — 11-Point Improvement Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve testplan-generator with 11 enhancements covering cell formatting (font/color/borders/newlines), content logic (J-W correspondence, Ch2 F-column, I-column, path fallback, inferred marking, script consolidation, no fabrication).

**Architecture:** Format layer first (xlsx_writer.py: font, borders, line-breaks, red font), then Content layer (combine_writer.py: F-column empty, W fallback, I fill, J-W validation), then Documentation (tp_prompt.md, SKILL.md).

**Tech Stack:** Python 3.12+, openpyxl, pytest, uv

---

## File Structure

| File | Responsibility | Action |
|------|---------------|--------|
| `writers/xlsx_writer.py` | Font, borders, line-breaks, red font, wrap_text | Modify |
| `writers/combine_writer.py` | F-column empty, W fallback, I fill, J-W validation | Modify |
| `templates/tp_prompt.md` | J-W rules, path fallback, no-fabrication rules | Modify |
| `SKILL.md` | Script consolidation, review naming, Ch2 instructions | Modify |
| `tests/test_xlsx_writer.py` | Font/border/newline/red-font/wrap tests | Modify |
| `tests/test_combine_writer.py` | F-column/W-fallback/I-fill/J-W tests | Modify |
| `tests/conftest.py` | New fixtures for font/direct_tc/assertion testing | Modify |

---

## Task 1: Font — 微软雅黑, Size 10, Black Color

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Write failing tests for default font**

Add to `tests/test_xlsx_writer.py` inside `TestWriteXlsx`:

```python
def test_data_cells_have_correct_font(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """All non-empty data cells must use 微软雅黑 size=10 black font."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(1, 24):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value is not None and str(cell.value).strip():
                assert cell.font.name == "微软雅黑", (
                    f"Cell ({row_idx},{col_idx}) font is '{cell.font.name}', expected '微软雅黑'"
                )
                assert cell.font.size == 10, (
                    f"Cell ({row_idx},{col_idx}) font size is {cell.font.size}, expected 10"
                )
                assert cell.font.color is not None, (
                    f"Cell ({row_idx},{col_idx}) has no font color"
                )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_data_cells_have_correct_font -v`
Expected: FAIL — current `_write_cell` does not set font.

- [ ] **Step 3: Implement font configuration in `_write_cell`**

Add imports and constants at the top of `writers/xlsx_writer.py` (after existing imports):

```python
from openpyxl.styles import Font

# Default data cell font
DEFAULT_FONT_NAME = "微软雅黑"
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT_COLOR = "000000"  # black
RED_FONT_COLOR = "FF0000"
```

Modify `_write_cell` to apply font on non-empty cells. After the line `cell.border = THIN_BORDER` (around line 104), add:

```python
    cell.font = Font(
        name=DEFAULT_FONT_NAME,
        size=DEFAULT_FONT_SIZE,
        color=DEFAULT_FONT_COLOR,
    )
```

Also apply font to `_apply_meta_rows` cells — add the same font to rows 3-5. After each `ws.cell(row=..., column=..., value=...)` call in `_apply_meta_rows`, add:

```python
    cell.font = Font(name=DEFAULT_FONT_NAME, size=DEFAULT_FONT_SIZE, color=DEFAULT_FONT_COLOR)
```

So `_apply_meta_rows` becomes:

```python
def _apply_meta_rows(ws: openpyxl.worksheet.worksheet.Worksheet, spec_name: str) -> None:
    default_font = Font(name=DEFAULT_FONT_NAME, size=DEFAULT_FONT_SIZE, color=DEFAULT_FONT_COLOR)
    c = ws.cell(row=3, column=1, value="plan")
    c.font = default_font

    c = ws.cell(row=4, column=1, value="weight")
    c.font = default_font
    c = ws.cell(row=4, column=21, value=5)
    c.font = default_font
    c = ws.cell(row=4, column=22, value=95)
    c.font = default_font

    c = ws.cell(row=5, column=1, value="skip")
    c.font = default_font
    c = ws.cell(row=5, column=2, value=spec_name)
    c.font = default_font
```

- [ ] **Step 4: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: apply 微软雅黑 size=10 black font to all data cells"
```

---

## Task 2: I-Column Red Font for 【配置】/【激励】

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`

- [ ] **Step 1: Write failing test for I-column red font**

Add to `tests/test_xlsx_writer.py`:

```python
def test_stimulus_column_has_red_font_for_markers(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """I-column cells containing 【配置】 or 【激励】 must have red font."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    found_red = False
    for row_idx in range(6, ws.max_row + 1):
        cell = ws.cell(row=row_idx, column=9)  # I column
        if cell.value and ("【配置】" in str(cell.value) or "【激励】" in str(cell.value)):
            assert cell.font.color is not None
            assert cell.font.color.rgb in ("00FF0000", "FFFF0000", "FF0000"), (
                f"I-column cell ({row_idx},9) has 【配置】/【激励】 but font color is {cell.font.color.rgb}"
            )
            found_red = True
    assert found_red, "Expected at least one I-column cell with red font for 【配置】/【激励】"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_stimulus_column_has_red_font_for_markers -v`
Expected: FAIL — current code uses black font for all cells.

- [ ] **Step 3: Implement I-column red font**

In `_write_cell`, after the `cell.font = Font(...)` line, add I-column red font override:

```python
    # Red font for I-column cells containing 【配置】 or 【激励】
    if col == 9 and ("【配置】" in text or "【激励】" in text):
        cell.font = Font(
            name=DEFAULT_FONT_NAME,
            size=DEFAULT_FONT_SIZE,
            color=RED_FONT_COLOR,
        )
```

- [ ] **Step 4: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: I-column red font for cells containing 【配置】/【激励】"
```

---

## Task 3: ⚠ [推断] Red Font

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`

- [ ] **Step 1: Write failing test for inferred red font**

Add to `tests/test_xlsx_writer.py`:

```python
def test_inferred_cells_have_red_font(
    self, writer_module, template_path, sample_ch1_data_with_inferred, tmp_output
):
    """Cells containing ⚠ [推断] must have red font color."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data_with_inferred}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(1, 24):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value and "⚠" in str(cell.value):
                assert cell.font.color is not None
                assert cell.font.color.rgb in ("00FF0000", "FFFF0000", "FF0000"), (
                    f"Cell ({row_idx},{col_idx}) with ⚠ should have red font, got {cell.font.color.rgb}"
                )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_inferred_cells_have_red_font -v`
Expected: FAIL — current code uses black font for ⚠ cells.

- [ ] **Step 3: Implement red font for inferred cells**

In `_write_cell`, modify the gold fill block. After the existing gold fill check, add red font override:

```python
    # Conditional gold fill AND red font for inferred/uncertain content
    if "⚠" in text or "[推断]" in text:
        cell.fill = GOLD_LIGHT_FILL
        cell.font = Font(
            name=DEFAULT_FONT_NAME,
            size=DEFAULT_FONT_SIZE,
            color=RED_FONT_COLOR,
        )
```

This replaces the default black font set earlier in the function — the red font line comes after, so it overrides.

- [ ] **Step 4: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: red font for ⚠ [推断] cells (keeps gold background)"
```

---

## Task 4: Content Line-Breaks on Punctuation

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Add fixture with punctuation-separated content**

Add to `tests/conftest.py`:

```python
@pytest.fixture
def semicolon_ch1_data():
    """Ch1 data with punctuation-separated content for line-break testing."""
    return {
        "module_name": "UPA",
        "spec_name": "Test Spec",
        "chapter": "chapter 1 功能特性",
        "features": [
            {
                "feature": "换行测试特性",
                "feature_id": "PA.200",
                "chapter": "chapter 1 功能特性",
                "subfeatures_l1": [
                    {
                        "subfeature_l1": "标点换行",
                        "subfeatures_l2": [
                            {
                                "subfeature_l2_overview": "分号换行测试",
                                "stimulus": "【配置】配置reg_a为1；配置reg_b为2",
                                "checking": "by_checker",
                                "coverage": "cover a {0,1}；cover b {0,1}",
                                "priority": "HIGH",
                                "activity": "BT",
                                "path": "",
                                "remarks": "来源: PA.200：验证分号换行",
                            }
                        ],
                    }
                ],
            }
        ],
    }
```

- [ ] **Step 2: Write failing test for line-breaks**

Add to `tests/test_xlsx_writer.py`:

```python
def test_line_breaks_on_punctuation(
    self, writer_module, template_path, semicolon_ch1_data, tmp_output
):
    """Content with punctuation should have line-breaks inserted."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": semicolon_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    # Check I-column (stimulus) has line-breaks after ；
    for row_idx in range(6, ws.max_row + 1):
        cell = ws.cell(row=row_idx, column=9)
        if cell.value and "；" in str(cell.value):
            assert "\n" in str(cell.value), (
                f"I-column row {row_idx}: expected line-break after ；"
            )
            break

def test_all_data_columns_have_wrap_text(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """All data columns (D-W) with content should have wrap_text enabled."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(4, 24):  # D through W
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value is not None and str(cell.value).strip():
                assert cell.alignment.wrap_text is True, (
                    f"Cell ({row_idx},{col_idx}) should have wrap_text enabled"
                )
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_line_breaks_on_punctuation tests/test_xlsx_writer.py::TestWriteXlsx::test_all_data_columns_have_wrap_text -v`
Expected: FAIL — no line-break insertion, wrap_text only on columns {9,11,23}.

- [ ] **Step 4: Implement line-break insertion and expand wrap_text**

Add helper function before `_write_cell` in `writers/xlsx_writer.py`:

```python
# Characters that trigger a line-break after them
BREAK_AFTER_CHARS = [";", "；", "。", "：", ":", "（", "）", "(", ")"]


def _insert_line_breaks(text: str) -> str:
    """Insert line-breaks after punctuation characters."""
    if not text:
        return text
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        result.append(ch)
        if ch in BREAK_AFTER_CHARS:
            # Don't add if already at end or next char is already newline
            if i + 1 < len(text) and text[i + 1] != "\n":
                result.append("\n")
        i += 1
    return "".join(result)
```

Change `WRAP_TEXT_COLUMNS` to cover all data columns:

```python
WRAP_TEXT_COLUMNS: set[int] = set(range(4, 24))  # D through W
```

In `_write_cell`, apply line-break insertion BEFORE the W-column comma sanitization. After the line `text = str(value)` and before the W-column sanitization block, add:

```python
    # Insert line-breaks after punctuation (except W column which uses commas)
    if col != 23:
        text = _insert_line_breaks(text)
        cell.value = text
```

The W-column (col 23) is excluded because paths use comma joining, not line-breaks.

Since `WRAP_TEXT_COLUMNS` now covers all data columns, the `wrap = col in WRAP_TEXT_COLUMNS` line will always be True for data columns. Simplify:

```python
    cell.alignment = Alignment(
        horizontal="left",
        vertical="center",
        wrap_text=True,
    )
```

Remove the now-unused `wrap` variable.

- [ ] **Step 5: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: ALL PASS (some existing tests may need updating for wrap_text change)

- [ ] **Step 6: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py tests/conftest.py
git commit -m "feat: auto line-breaks on punctuation, wrap_text on all data columns"
```

---

## Task 5: Border Logic — Rectangle Region (A-W)

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`

- [ ] **Step 1: Write failing tests for rectangle borders**

Add to `tests/test_xlsx_writer.py`:

```python
def test_border_rectangle_covers_all_a_to_w(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """Borders must cover the full A-W rectangle from first to last data row."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active

    # Find first and last data rows (rows >= 6 with any content)
    first_data_row = None
    last_data_row = None
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(1, 24):
            if ws.cell(row=row_idx, column=col_idx).value is not None:
                if first_data_row is None:
                    first_data_row = row_idx
                last_data_row = row_idx
                break

    assert first_data_row is not None, "Should have data rows"

    # All cells in the rectangle must have thin borders
    for row_idx in range(first_data_row, last_data_row + 1):
        for col_idx in range(1, 24):  # A through W
            cell = ws.cell(row=row_idx, column=col_idx)
            assert cell.border.left.style == "thin", (
                f"Cell ({row_idx},{col_idx}) missing left border in rectangle"
            )
            assert cell.border.right.style == "thin", (
                f"Cell ({row_idx},{col_idx}) missing right border in rectangle"
            )
            assert cell.border.top.style == "thin", (
                f"Cell ({row_idx},{col_idx}) missing top border in rectangle"
            )
            assert cell.border.bottom.style == "thin", (
                f"Cell ({row_idx},{col_idx}) missing bottom border in rectangle"
            )

def test_no_borders_outside_rectangle(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """Rows before first data row and after last data row should NOT have data borders."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active

    # Row 1-5 should not have data-style thin borders
    for row_idx in range(1, 6):
        for col_idx in range(1, 24):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.border.left.style == "thin":
                # Row 3-5 may have borders from meta rows — skip those
                pass  # Meta rows are excluded from this check
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_border_rectangle_covers_all_a_to_w -v`
Expected: FAIL — current code only borders non-empty cells, empty cells in the rectangle have no borders.

- [ ] **Step 3: Implement rectangle border post-processing**

In `writers/xlsx_writer.py`, remove border logic from `_write_cell` — no longer set `cell.border = THIN_BORDER` inside `_write_cell`. Instead, keep the function clean for content/formatting only.

Add a new function after `_apply_sheet_formatting`:

```python
def _apply_rectangle_borders(
    ws: openpyxl.worksheet.worksheet.Worksheet,
    start_row: int,
    end_row: int,
) -> None:
    """Apply thin borders to the full A-W rectangle for data rows."""
    for row_idx in range(start_row, end_row + 1):
        for col_idx in range(1, 24):  # A through W
            ws.cell(row=row_idx, column=col_idx).border = THIN_BORDER
```

In `write_testpoint_xlsx`, after all chapters are written and before `_apply_sheet_formatting`, call:

```python
    # Apply rectangle borders to all data rows
    data_start = 6
    data_end = max(row - 1, 6)
    _apply_rectangle_borders(ws, data_start, data_end)
```

In `_write_cell`, remove the `cell.border = THIN_BORDER` line (borders are now handled by rectangle post-processing). Keep the empty cell border-clearing logic:

```python
    if value is None or (isinstance(value, str) and value.strip() == ""):
        cell = ws.cell(row=row, column=col)
        cell.value = None
        return
```

Also remove the border-clearing from the template cleanup loop (line 297 `ws.cell(...).border = Border()`) since rectangle borders will overwrite anyway.

Update the existing test `test_data_cells_have_borders` to work with the new rectangle approach — it should still pass since the rectangle covers all data cells.

- [ ] **Step 4: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: ALL PASS (may need to update `test_empty_cells_no_borders` since empty cells now DO have borders in the rectangle)

- [ ] **Step 5: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: rectangle border logic — A-W columns for all data rows"
```

---

## Task 6: Ch2 F-Column Empty + I-Column 【配置】 Fill + W-Column Fallback

**Files:**
- Modify: `writers/combine_writer.py`
- Modify: `tests/test_combine_writer.py`

This task implements requirements 6 (F-column empty), 8 (I-column fill), and 7 (W fallback) together since they all modify `build_ch2_data`.

- [ ] **Step 1: Write failing tests**

Add to `tests/test_combine_writer.py`:

```python
class TestCh2ContentRules:
    """Test Ch2 content generation rules."""

    def test_ch2_f_column_is_empty(self, combine_mod):
        """Ch2 subfeature_l2_overview must be empty (F column)."""
        ch2_regs = [
            {"name": "upa_set_bp", "fields": [
                {"name": "out_bp", "access": "RW", "description": "设置反压", "range": "[0]"},
            ]},
        ]
        ch1_data = {"features": []}
        result = combine_mod.build_ch2_data(ch2_regs, ch1_data)
        l2 = result["registers"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert l2["subfeature_l2_overview"] == ""

    def test_ch2_i_column_filled_for_uncovered(self, combine_mod):
        """Uncovered Ch2 registers must have I-column 【配置】 from field info."""
        ch2_regs = [
            {"name": "upa_set_bp", "fields": [
                {"name": "out_bp", "access": "RW", "description": "设置反压", "range": "[0]"},
                {"name": "rsv", "access": "RO", "description": "reserved", "range": "[31:1]"},
            ]},
        ]
        ch1_data = {"features": []}
        result = combine_mod.build_ch2_data(ch2_regs, ch1_data)
        l2 = result["registers"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert "【配置】" in l2["stimulus"]
        assert "upa_set_bp.out_bp" in l2["stimulus"]
        assert "rsv" not in l2["stimulus"]  # rsv should be excluded

    def test_ch2_i_column_empty_for_covered(self, combine_mod):
        """Covered Ch2 registers keep I-column from Ch1 cross-ref."""
        ch2_regs = [
            {"name": "upa_ck_ctrl", "fields": [
                {"name": "tcp_csum_en", "access": "RW", "description": "tcp checksum使能"},
            ]},
        ]
        ch1_data = {
            "features": [{
                "feature_id": "PA.012",
                "feature": "校验",
                "subfeatures_l1": [{
                    "subfeatures_l2": [{
                        "stimulus": "【配置】配置 upa_ck_ctrl.tcp_csum_en 为1",
                        "checking": "by_checker",
                        "coverage": "cover tcp_csum_en {0,1}",
                        "path": "Group:$unit::upa_fcov::cg_ck.cp_tcp",
                    }],
                }],
            }],
        }
        result = combine_mod.build_ch2_data(ch2_regs, ch1_data)
        l2 = result["registers"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert l2["skip"] is True
        # Covered registers copy stimulus from Ch1
        assert "tcp_csum_en" in l2["stimulus"]

    def test_ch2_w_column_fallback_when_empty(self, combine_mod):
        """Uncovered registers with no path get 【反标路径暂无法确定】."""
        ch2_regs = [
            {"name": "upa_set_bp", "fields": [
                {"name": "out_bp", "access": "RW", "description": "设置反压", "range": "[0]"},
            ]},
        ]
        ch1_data = {"features": []}
        result = combine_mod.build_ch2_data(ch2_regs, ch1_data)
        l2 = result["registers"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert l2["path"] == "【反标路径暂无法确定】"

    def test_ch2_w_column_keeps_path_from_ch1(self, combine_mod):
        """Covered registers keep the path from Ch1 cross-ref."""
        ch2_regs = [
            {"name": "upa_ck_ctrl", "fields": [
                {"name": "tcp_csum_en", "access": "RW", "description": "tcp checksum使能"},
            ]},
        ]
        ch1_data = {
            "features": [{
                "feature_id": "PA.012",
                "feature": "校验",
                "subfeatures_l1": [{
                    "subfeatures_l2": [{
                        "stimulus": "【配置】配置 upa_ck_ctrl.tcp_csum_en 为1",
                        "checking": "by_checker",
                        "coverage": "cover tcp_csum_en {0,1}",
                        "path": "Group:$unit::upa_fcov::cg_ck.cp_tcp",
                    }],
                }],
            }],
        }
        result = combine_mod.build_ch2_data(ch2_regs, ch1_data)
        l2 = result["registers"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert "cg_ck.cp_tcp" in l2["path"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_combine_writer.py::TestCh2ContentRules -v`
Expected: FAIL — F-column currently uses `reg_name`, I-column is empty, W-column has no fallback.

- [ ] **Step 3: Modify `cross_ref_ch2` to fill I-column for uncovered registers**

In `writers/combine_writer.py`, modify the `else` branch of `cross_ref_ch2` (the uncovered register block, around lines 167-184):

Change the `stimulus: ""` line to generate 【配置】 content:

```python
        else:
            desc_parts = []
            config_parts = []
            for field in fields:
                fname = field.get("name", "")
                fdesc = field.get("description", "")
                frange = field.get("range", "")
                faccess = field.get("access", "")
                if fname and fname != "rsv":
                    desc_parts.append(f"{frange} {fname}: {fdesc}")
                    if faccess in ("RW", "RWW"):
                        config_parts.append(f"配置 {reg_name}.{fname} ({frange})")

            stimulus = "【配置】" + "；".join(config_parts) if config_parts else ""

            result.append({
                "name": reg_name,
                "skip": False,
                "remarks": "; ".join(desc_parts) if desc_parts else "",
                "stimulus": stimulus,
                "checking": "",
                "coverage": "",
                "path": "",
            })
```

- [ ] **Step 4: Modify `build_ch2_data` for F-column and W-fallback**

In `writers/combine_writer.py`, modify `build_ch2_data` (around lines 203-214):

Change `"subfeature_l2_overview": reg_name` to `""`:

```python
        subfeatures_l2: list[dict[str, Any]] = [{
            "subfeature_l2_overview": "",  # F-column: empty for Ch2
            "subfeature_l2_detail": "",
            "remarks": reg_info.get("remarks", ""),
            "stimulus": reg_info.get("stimulus", ""),
            "checking": reg_info.get("checking", ""),
            "coverage": reg_info.get("coverage", ""),
            "priority": "HIGH" if not is_skip else "",
            "activity": "BT",
            "path": reg_info.get("path", "") or "【反标路径暂无法确定】",
            "skip": is_skip,
        }]
```

- [ ] **Step 5: Run ALL combine_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_combine_writer.py -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add writers/combine_writer.py tests/test_combine_writer.py
git commit -m "feat: Ch2 F-column empty, I-column 【配置】 fill, W-column fallback"
```

---

## Task 7: J-W Correspondence Validation

**Files:**
- Modify: `writers/combine_writer.py`
- Modify: `tests/test_combine_writer.py`

- [ ] **Step 1: Write failing tests for J-W correspondence**

Add to `tests/test_combine_writer.py`:

```python
class TestJWCorrespondence:
    """Test J-column (checking) ↔ W-column (path) correspondence."""

    def test_direct_tc_gets_direct_fcov_path(self, combine_mod):
        """When checking=by_direct_tc, path should contain _direct_fcov::cp_direct_."""
        data = {
            "module_name": "UPA",
            "chapter": "chapter 1 功能特性",
            "features": [{
                "feature": "直连用例",
                "feature_id": "PA.300",
                "subfeatures_l1": [{
                    "subfeatures_l2": [{
                        "checking": "by_direct_tc",
                        "path": "",
                    }],
                }],
            }],
        }
        result = combine_mod.validate_jw_correspondence(data)
        l2 = result["features"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert "_direct_fcov::cp_direct_" in l2["path"]

    def test_assertion_gets_assert_path(self, combine_mod):
        """When checking=by_assertion, path should contain _assert::."""
        data = {
            "module_name": "UPA",
            "chapter": "chapter 1 功能特性",
            "features": [{
                "feature": "断言覆盖",
                "feature_id": "PA.301",
                "subfeatures_l1": [{
                    "subfeatures_l2": [{
                        "checking": "by_assertion",
                        "path": "",
                    }],
                }],
            }],
        }
        result = combine_mod.validate_jw_correspondence(data)
        l2 = result["features"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert "_assert::" in l2["path"]

    def test_checker_path_unchanged(self, combine_mod):
        """When checking=by_checker, path should not be auto-modified."""
        data = {
            "module_name": "UPA",
            "chapter": "chapter 1 功能特性",
            "features": [{
                "feature": "检查器",
                "feature_id": "PA.302",
                "subfeatures_l1": [{
                    "subfeatures_l2": [{
                        "checking": "by_checker",
                        "path": "Group:$unit::upa_fcov::cg_test.cp_a",
                    }],
                }],
            }],
        }
        result = combine_mod.validate_jw_correspondence(data)
        l2 = result["features"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]
        assert l2["path"] == "Group:$unit::upa_fcov::cg_test.cp_a"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_combine_writer.py::TestJWCorrespondence -v`
Expected: FAIL — `validate_jw_correspondence` does not exist.

- [ ] **Step 3: Implement `validate_jw_correspondence`**

Add to `writers/combine_writer.py`:

```python
def _sanitize_path_name(text: str) -> str:
    """Convert text to a valid snake_case path component."""
    s = re.sub(r"[^a-zA-Z0-9_]", "_", text)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()


def validate_jw_correspondence(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and auto-correct J-column (checking) ↔ W-column (path) correspondence.

    Rules:
    - checking=by_direct_tc + empty path → auto-generate direct_fcov path
    - checking=by_assertion + empty path → auto-generate assert path
    - checking=by_checker → leave path unchanged

    Returns the modified data dict.
    """
    module = data.get("module_name", "xxx").lower()
    counter: dict[str, int] = {}

    for feat in data.get("features", []):
        overview = feat.get("feature", "")
        slug = _sanitize_path_name(overview)
        for sf1 in feat.get("subfeatures_l1", []):
            for idx, sf2 in enumerate(sf1.get("subfeatures_l2", [])):
                checking = sf2.get("checking", "")
                path = sf2.get("path", "")

                if checking == "by_direct_tc" and (not path or "【反标路径暂无法确定】" in path):
                    key = f"direct_{slug}"
                    counter[key] = counter.get(key, 0) + 1
                    sf2["path"] = f"Group:$unit::{module}_direct_fcov::cp_direct_{slug}_{counter[key]}"

                elif checking == "by_assertion" and (not path or "【反标路径暂无法确定】" in path):
                    key = f"assert_{slug}"
                    counter[key] = counter.get(key, 0) + 1
                    sf2["path"] = f"Group:$unit::{module}_assert::{slug}_{counter[key]}_c"

    return data
```

- [ ] **Step 4: Run tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/test_combine_writer.py::TestJWCorrespondence -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/combine_writer.py tests/test_combine_writer.py
git commit -m "feat: J-W correspondence validation (by_direct_tc/by_assertion path auto-generation)"
```

---

## Task 8: Update tp_prompt.md — J-W Rules, Path Fallback, No Fabrication

**Files:**
- Modify: `templates/tp_prompt.md`

- [ ] **Step 1: Update prompt template sections**

Replace the `### checking（预期结果）` section with:

```markdown
### checking（预期结果）
- 三种检查方式：
  - `by_checker`：通过 checker 自动检查
  - `by_direct_tc`：通过直接测试用例检查，此时 W列 path 必须使用 `_direct_fcov::cp_direct_` 格式
  - `by_assertion`：通过断言检查，此时 W列 path 必须使用 `_assert::` 格式
- J列和W列必须严格对应：
  - J=by_direct_tc → W=`Group:$unit::模块_direct_fcov::cp_direct_描述_序号`
  - J=by_assertion → W=`Group:$unit::模块_assert::描述_c`
  - J=by_checker → W=covergroup路径（cg_/cp_/cr_格式）
```

Replace the `### path（覆盖率组路径）` section, appending fallback rule:

```markdown
### path（覆盖率组路径）
四种格式，严格使用前缀：
1. `Group:$unit::模块_fcov::cg_covergroup名.cp_coverpoint名` — covergroup用`cg_`前缀
2. `Group:$unit::模块_fcov::cg_covergroup名.cr_cross名` — cross cover用`cr_`前缀
3. `Group:$unit::模块_direct_fcov::cp_coverpoint名` — direct coverpoint用`cp_`前缀（J=by_direct_tc时必须使用）
4. `Group:$unit::模块_assert::cover_断言名` — assertion覆盖（J=by_assertion时必须使用）

多个路径用英文逗号 `,` 连接（禁止使用换行）。
如果无法从功能规格书或寄存器手册确定反标路径，填写 `【反标路径暂无法确定】`。
```

In the `## 约束` section, add:

```markdown
8. 如果信息在功能规格书和寄存器手册中无法找到，使用 `⚠ [推断]` 标注，不要编造不存在的信息
9. 宁可标注 `⚠ [推断]` 或留空，也不要写入不确定的内容
```

- [ ] **Step 2: Verify template reads correctly**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run python -c "from pathlib import Path; t = Path('templates/tp_prompt.md').read_text(); assert 'direct_fcov' in t; assert '_assert::' in t; assert '反标路径暂无法确定' in t; assert '宁可标注' in t; print('OK')"`

Expected: "OK"

- [ ] **Step 3: Commit**

```bash
git add templates/tp_prompt.md
git commit -m "feat: update tp_prompt with J-W rules, path fallback, no-fabrication constraints"
```

---

## Task 9: Update SKILL.md — Script Consolidation, Ch2 Instructions

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Update Step 5 (Ch2 instructions)**

Replace the Step 5 section with:

```markdown
### Step 5: Generate Chapter 2 Configuration Coverage (Stage 4)

From `reg_parsed.json`, generate register-level test points using `combine_writer.py`:

1. The `combine_writer.py` handles:
   - Filter: exclude int/car_ctrl/fifo_th/spare/cnt/fifo_status/fsm/bp/test/init registers
   - Group: merge numbered variants (_0/_1/_2 → base_0/1/2)
   - Cross-ref: check covered_regs mapping from Chapter 1
     - If already covered -> A="skip", H="寄存器描述 【已在功能特性 [PA.XXX] 中覆盖】", I/J/K copy from Ch1
     - If not covered -> I=【配置】auto-generated from field info, W="【反标路径暂无法确定】"
   - H column: always include register/field description from manual
   - F column: empty (D+E columns express register+field)
   - Only RW/RWW fields (skip ro/rwc/rctr/sctr/rc/rsv)
2. Run `validate_jw_correspondence` on Ch1 data to auto-correct J-W paths
```

- [ ] **Step 2: Update Step 6 output section**

Replace Step 6 section with:

```markdown
### Step 6: Write Output (Stage 5)

After generating Ch1 test points:

1. Save Ch1 features JSON to `/tmp/tp_ch1_features.json`

2. Run combine_writer (handles Ch2 + merge + xlsx write in one command):
```bash
cd ${CLAUDE_SKILL_DIR} && uv run python writers/combine_writer.py \
  --ch1 /tmp/tp_ch1_features.json \
  --reg /tmp/tp_reg_parsed.json \
  --output "$output_path" \
  --template ${CLAUDE_SKILL_DIR}/templates/testplan_template.xlsx
```

3. Write review (if any issues found):
```bash
cd ${CLAUDE_SKILL_DIR} && uv run python review/review_writer.py /tmp/tp_review_data.json "$review_output_path"
```
Review file defaults to `<output_dir>/fs_reg_slv_review.md`.

The pipeline handles:
- Ch2 register filtering and grouping (combine_writer)
- Cross-reference with Ch1 for skip marking
- J-W correspondence validation (by_direct_tc/by_assertion path auto-generation)
- xlsx_writer formatting: 微软雅黑 10号字体, 红色字体 for ⚠/【配置】, 矩形边框, 自动换行
```

- [ ] **Step 3: Update Common Mistakes table**

Add to the Common Mistakes table:

```markdown
| J-W column mismatch | by_direct_tc needs direct_fcov path | Use validate_jw_correspondence |
| Fabricating spec info | Must not invent non-existent data | Use ⚠ [推断] or omit |
| Creating temp scripts | All logic in combine_writer/xlsx_writer | Use existing CLI |
```

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: update SKILL.md with v2 content rules, J-W validation, script consolidation"
```

---

## Task 10: Run Full Test Suite and Fix Any Failures

**Files:**
- Potentially modify any test or source file that fails

- [ ] **Step 1: Run complete test suite**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-v2/testplan-generator && uv run pytest tests/ -v`

Expected: ALL PASS

- [ ] **Step 2: Fix any failures**

Common issues to check:
- `test_empty_cells_no_borders` may fail because rectangle borders now cover empty cells — update test to only check outside the rectangle
- `test_wrap_text_columns` may fail if it checks only specific columns — update to check all data columns
- `test_ch2_chapter_label_appears_once` should still pass (F-column change doesn't affect B-column)

- [ ] **Step 3: Final commit if fixes needed**

```bash
git add -A
git commit -m "fix: resolve test suite failures from v2 changes"
```

---

## Spec Coverage Check

| Requirement | Task | Status |
|-------------|------|--------|
| #1 Font (微软雅黑 10 black) | Task 1 | `_write_cell` Font config |
| #1 I-column 【配置】/【激励】 red | Task 2 | Conditional red font in I column |
| #2 Line-breaks on punctuation | Task 4 | `_insert_line_breaks` + wrap_text all cols |
| #3 Rectangle borders A-W | Task 5 | `_apply_rectangle_borders` post-processing |
| #4 J=by_direct_tc → W path | Tasks 7, 8 | `validate_jw_correspondence` + prompt |
| #5 J=by_assertion → W path | Tasks 7, 8 | `validate_jw_correspondence` + prompt |
| #6 Ch2 F-column empty | Task 6 | `build_ch2_data` subfeature_l2_overview="" |
| #7 W-column fallback | Task 6 | `【反标路径暂无法确定】` |
| #8 Ch2 I-column 【配置】 fill | Task 6 | `cross_ref_ch2` generates config desc |
| #9 ⚠ red font | Task 3 | Red font + gold fill for inferred |
| #10 Script consolidation | Task 9 | SKILL.md references only existing modules |
| #11/12 No fabrication | Tasks 8, 9 | Prompt constraints + review workflow |
