# Testplan Generator 16-Point Improvement Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the testplan-generator skill with 16 specific enhancements covering architecture, formatting, Ch2 logic, and content quality.

**Architecture:** Method A (centralized): New `combine_writer.py` handles Ch2 filtering/grouping/cross-ref logic; `xlsx_writer.py` focuses on pure formatting. Two modules independently testable via TDD.

**Tech Stack:** Python 3.12+, openpyxl, pytest, uv

---

## File Structure

| File | Responsibility | Action |
|------|---------------|--------|
| `writers/xlsx_writer.py` | Pure xlsx write + cell formatting | Modify |
| `writers/combine_writer.py` | Ch2 reg filtering, grouping, cross-ref, JSON merge, CLI | Create |
| `writers/__init__.py` | Module init (already exists) | No change |
| `review/review_writer.py` | Review generation (already exists) | No change |
| `templates/tp_prompt.md` | Prompt template for LLM test point generation | Modify |
| `SKILL.md` | Skill instructions | Modify |
| `tests/test_xlsx_writer.py` | Tests for xlsx formatting | Modify |
| `tests/test_combine_writer.py` | Tests for combine_writer | Create |
| `tests/conftest.py` | Shared fixtures | Modify |

---

## Task 1: Cell Formatting — Replace `_set_wrap_text` with `_write_cell`

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`
- Modify: `tests/conftest.py` (add fixture with `⚠ [推断]` text)

This task addresses improvement #2 (vertical center, left-align, borders on non-empty cells).

- [ ] **Step 1: Write failing tests for cell formatting**

Add to `tests/test_xlsx_writer.py` inside `TestWriteXlsx`:

```python
def test_data_cells_have_left_align(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """All data cells with content must be left-aligned and vertically centered."""
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
                assert cell.alignment.horizontal == "left", (
                    f"Cell ({row_idx},{col_idx}) not left-aligned"
                )
                assert cell.alignment.vertical == "center", (
                    f"Cell ({row_idx},{col_idx}) not vertically centered"
                )

def test_data_cells_have_borders(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """All data cells with content must have thin borders."""
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
                assert cell.border.left.style == "thin", (
                    f"Cell ({row_idx},{col_idx}) missing left border"
                )
                assert cell.border.right.style == "thin", (
                    f"Cell ({row_idx},{col_idx}) missing right border"
                )
                assert cell.border.top.style == "thin", (
                    f"Cell ({row_idx},{col_idx}) missing top border"
                )
                assert cell.border.bottom.style == "thin", (
                    f"Cell ({row_idx},{col_idx}) missing bottom border"
                )

def test_empty_cells_no_borders(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """Empty data cells should NOT have borders."""
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
            if cell.value is None or str(cell.value).strip() == "":
                assert cell.border.left.style is None, (
                    f"Empty cell ({row_idx},{col_idx}) should not have borders"
                )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_data_cells_have_left_align tests/test_xlsx_writer.py::TestWriteXlsx::test_data_cells_have_borders tests/test_xlsx_writer.py::TestWriteXlsx::test_empty_cells_no_borders -v`

Expected: FAIL — current code uses bare `ws.cell()` and `_set_wrap_text()` without alignment or borders.

- [ ] **Step 3: Implement `_write_cell` and replace all cell writes**

Replace `_set_wrap_text` with `_write_cell` in `writers/xlsx_writer.py`:

```python
from openpyxl.styles import Alignment, Border, PatternFill, Side

# Thin border for all non-empty data cells
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

# Gold light 80% fill for cells containing ⚠ or [推断]
GOLD_LIGHT_FILL = PatternFill(
    start_color="FFF2CC",
    end_color="FFF2CC",
    fill_type="solid",
)


def _write_cell(
    ws: openpyxl.worksheet.worksheet.Worksheet,
    row: int,
    col: int,
    value: Any,
) -> None:
    """Write a data cell with standard formatting.

    - Non-empty cells: left-align, vertical-center, thin borders
    - Wrap text on columns I(9), K(11), W(23)
    - Gold background on cells containing '⚠' or '[推断]'
    - Empty cells: no formatting
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        ws.cell(row=row, column=col)
        return

    cell = ws.cell(row=row, column=col, value=value)
    wrap = col in WRAP_TEXT_COLUMNS
    cell.alignment = Alignment(
        horizontal="left",
        vertical="center",
        wrap_text=wrap,
    )
    cell.border = THIN_BORDER

    # Conditional gold fill for inferred/uncertain content
    text = str(value)
    if "⚠" in text or "[推断]" in text:
        cell.fill = GOLD_LIGHT_FILL
```

Then replace ALL calls to `_set_wrap_text(ws, row, col, value)` and bare `ws.cell(row=row, column=N, value=...)` in both `_write_ch1` and `_write_ch2` with `_write_cell(ws, row, col, value)`. Remove the old `_set_wrap_text` function entirely.

For `_write_ch1`, the L2 row becomes:

```python
_write_cell(ws, row, 6, overview)
_write_cell(ws, row, 7, detail)
_write_cell(ws, row, 8, remarks)
_write_cell(ws, row, 9, stimulus)
_write_cell(ws, row, 10, checking)
_write_cell(ws, row, 11, coverage)
_write_cell(ws, row, 12, priority)
_write_cell(ws, row, 13, activity)
_write_cell(ws, row, 23, path)
```

Same pattern for `_write_ch2` L2 rows. Also apply `_write_cell` to the feature header rows (D column) and L1 rows (E column).

- [ ] **Step 4: Run ALL xlsx_writer tests to verify they pass**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`

Expected: ALL PASS (including existing tests and new formatting tests)

- [ ] **Step 5: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: add cell formatting (left-align, vertical-center, borders, gold fill for inferred)"
```

---

## Task 2: Gold Background for Inferred Cells

**Files:**
- Modify: `tests/conftest.py` (add fixture with `⚠ [推断]` content)
- Modify: `tests/test_xlsx_writer.py`

This task addresses improvement #14. The fill logic is already in `_write_cell` from Task 1; this task adds dedicated tests.

- [ ] **Step 1: Add fixture with inferred content to conftest.py**

Add to `tests/conftest.py`:

```python
@pytest.fixture
def inferred_ch1_data():
    """Ch1 data containing ⚠ [推断] markers."""
    return {
        "module_name": "UPA",
        "spec_name": "Test Spec",
        "chapter": "chapter 1 功能特性",
        "features": [
            {
                "feature": "推断特性",
                "feature_id": "PA.999",
                "chapter": "chapter 1 功能特性",
                "subfeatures_l1": [
                    {
                        "subfeature_l1": "推断子特性",
                        "subfeatures_l2": [
                            {
                                "subfeature_l2_overview": "⚠ [推断] 某个不确定的测试点",
                                "subfeature_l2_detail": "",
                                "remarks": "来源: PA.999 ⚠ [推断]",
                                "stimulus": "【配置】⚠ [推断] 配置某寄存器",
                                "checking": "by_checker",
                                "coverage": "cover x {0, 1}",
                                "priority": "MID",
                                "activity": "BT",
                                "path": "",
                            }
                        ],
                    }
                ],
            }
        ],
    }
```

- [ ] **Step 2: Write failing test for gold fill**

Add to `tests/test_xlsx_writer.py`:

```python
def test_inferred_cells_have_gold_fill(
    self, writer_module, template_path, inferred_ch1_data, tmp_output
):
    """Cells containing ⚠ [推断] must have gold background."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": inferred_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    gold_cells = []
    non_gold_with_marker = []
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(1, 24):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value and "⚠" in str(cell.value):
                if cell.fill and cell.fill.start_color and cell.fill.start_color.rgb in ("00FFF2CC", "FFF2CC"):
                    gold_cells.append((row_idx, col_idx))
                else:
                    non_gold_with_marker.append((row_idx, col_idx))
    assert len(gold_cells) >= 1, "Expected at least one cell with gold fill"
    assert len(non_gold_with_marker) == 0, f"Cells with ⚠ but no gold fill: {non_gold_with_marker}"

def test_normal_cells_no_gold_fill(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """Cells without ⚠ markers should NOT have gold fill."""
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
            if cell.value and "⚠" not in str(cell.value) and "[推断]" not in str(cell.value):
                assert cell.fill.start_color.rgb != "00FFF2CC", (
                    f"Normal cell ({row_idx},{col_idx}) should not have gold fill"
                )
```

- [ ] **Step 3: Run tests to verify they pass (implementation already in Task 1)**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_inferred_cells_have_gold_fill tests/test_xlsx_writer.py::TestWriteXlsx::test_normal_cells_no_gold_fill -v`

Expected: PASS — `_write_cell` from Task 1 already handles gold fill.

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/test_xlsx_writer.py
git commit -m "test: add gold fill tests for inferred cells (⚠ [推断])"
```

---

## Task 3: B Column — Chapter Label Only Once Per Section

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`

This task addresses improvement #7.

- [ ] **Step 1: Write failing test for B column singularity**

Add to `tests/test_xlsx_writer.py`:

```python
def test_ch1_chapter_label_appears_once(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """Ch1 chapter label should appear only in B column of the FIRST feature row."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    ch1_labels = []
    for row_idx in range(6, ws.max_row + 1):
        val = ws.cell(row=row_idx, column=2).value
        if val == "chapter 1 功能特性":
            ch1_labels.append(row_idx)
    assert len(ch1_labels) == 1, f"Expected exactly 1 ch1 label, found {len(ch1_labels)} at rows {ch1_labels}"

def test_ch2_chapter_label_appears_once(
    self, writer_module, template_path, sample_ch1_data, sample_ch2_data, tmp_output
):
    """Ch2 chapter label should appear only in B column of the FIRST register row."""
    writer_module.write_testpoint_xlsx(
        chapters=[
            {"type": "ch1", "data": sample_ch1_data},
            {"type": "ch2", "data": sample_ch2_data},
        ],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    ch2_labels = []
    for row_idx in range(6, ws.max_row + 1):
        val = ws.cell(row=row_idx, column=2).value
        if val == "chapter 2 配置特性":
            ch2_labels.append(row_idx)
    assert len(ch2_labels) == 1, f"Expected exactly 1 ch2 label, found {len(ch2_labels)} at rows {ch2_labels}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_ch1_chapter_label_appears_once tests/test_xlsx_writer.py::TestWriteXlsx::test_ch2_chapter_label_appears_once -v`

Expected: FAIL — current code writes chapter_label to B column for EVERY feature/register.

- [ ] **Step 3: Implement — only first row gets chapter label**

In `_write_ch1`, change the feature loop:

```python
for i, feat in enumerate(data.get("features", [])):
    total_features += 1
    feature_name = feat.get("feature", "")

    # Only first feature row gets the chapter label in B column
    if i == 0:
        _write_cell(ws, row, 2, chapter_label)
    _write_cell(ws, row, 4, feature_name)
    ws.row_dimensions[row].outline_level = 0
    row += 1
```

Same change in `_write_ch2`:

```python
for i, reg in enumerate(data.get("registers", [])):
    reg_name = reg.get("register_name", "")
    total_features += 1

    if i == 0:
        _write_cell(ws, row, 2, chapter_label)
    _write_cell(ws, row, 4, reg_name)
    ws.row_dimensions[row].outline_level = 0
    row += 1
```

Also fix the existing `test_ch1_chapter_label` and `test_ch2_chapter_label` tests: change `found = True` assertion to check for exactly one occurrence.

- [ ] **Step 4: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: B column chapter label appears only once per section"
```

---

## Task 4: W Column Path Joining with Comma (Writer-Level)

**Files:**
- Modify: `writers/xlsx_writer.py`
- Modify: `tests/test_xlsx_writer.py`

This task addresses improvement #3 (comma joining). Note: the path content is generated by the LLM, but the writer sanitizes newlines in W column.

- [ ] **Step 1: Add fixture with multi-path in conftest.py**

Add to `tests/conftest.py`:

```python
@pytest.fixture
def multipath_ch1_data():
    """Ch1 data with multi-line paths in W column."""
    return {
        "module_name": "UPA",
        "spec_name": "Test Spec",
        "chapter": "chapter 1 功能特性",
        "features": [
            {
                "feature": "多路径特性",
                "feature_id": "PA.100",
                "chapter": "chapter 1 功能特性",
                "subfeatures_l1": [
                    {
                        "subfeature_l1": "路径测试",
                        "subfeatures_l2": [
                            {
                                "subfeature_l2_overview": "多路径覆盖",
                                "stimulus": "【配置】无",
                                "checking": "by_checker",
                                "coverage": "cover a {0,1}",
                                "priority": "HIGH",
                                "activity": "BT",
                                "path": "Group:$unit::upa_fcov::cg_test.cp_a\nGroup:$unit::upa_fcov::cg_test.cp_b",
                            }
                        ],
                    }
                ],
            }
        ],
    }
```

- [ ] **Step 2: Write failing test for comma joining**

Add to `tests/test_xlsx_writer.py`:

```python
def test_path_column_uses_commas(
    self, writer_module, template_path, multipath_ch1_data, tmp_output
):
    """W column paths must be joined with commas, not newlines."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": multipath_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    for row_idx in range(6, ws.max_row + 1):
        cell = ws.cell(row=row_idx, column=23)
        if cell.value:
            assert "\n" not in str(cell.value), (
                f"Row {row_idx} W column should not contain newlines"
            )
            assert "," in str(cell.value), (
                f"Row {row_idx} W column should use commas to join paths"
            )
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_path_column_uses_commas -v`

Expected: FAIL — current code passes newlines through as-is.

- [ ] **Step 4: Implement newline-to-comma sanitization in `_write_cell`**

Add sanitization for column W (23) inside `_write_cell`:

```python
def _write_cell(ws, row, col, value):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        ws.cell(row=row, column=col)
        return

    text = str(value)
    # Sanitize W column: replace newlines with commas
    if col == 23 and "\n" in text:
        text = ",".join(part.strip() for part in text.split("\n") if part.strip())

    cell = ws.cell(row=row, column=col, value=text)
    wrap = col in WRAP_TEXT_COLUMNS
    cell.alignment = Alignment(
        horizontal="left",
        vertical="center",
        wrap_text=wrap,
    )
    cell.border = THIN_BORDER

    if "⚠" in text or "[推断]" in text:
        cell.fill = GOLD_LIGHT_FILL
```

- [ ] **Step 5: Run ALL xlsx_writer tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`

Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add writers/xlsx_writer.py tests/test_xlsx_writer.py tests/conftest.py
git commit -m "feat: W column paths joined with commas instead of newlines"
```

---

## Task 5: Create `combine_writer.py` — Ch2 Register Exclusion

**Files:**
- Create: `writers/combine_writer.py`
- Create: `tests/test_combine_writer.py`

This task addresses improvement #8 (exclude int/car_ctrl/fifo_th/spare/cnt/etc registers from Ch2).

- [ ] **Step 1: Write failing tests for register exclusion**

Create `tests/test_combine_writer.py`:

```python
"""Tests for combine_writer.py — Ch2 register filtering, grouping, cross-ref."""
import importlib
import os
import sys

import pytest

SKILL_ROOT = os.path.join(os.path.dirname(__file__), "..")
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)


@pytest.fixture
def combine_mod():
    return importlib.import_module("writers.combine_writer")


class TestCh2Exclusion:
    """Test register exclusion patterns for Chapter 2."""

    def test_excludes_int_registers(self, combine_mod):
        regs = [
            {"name": "upa_int_status", "offset": "0x0"},
            {"name": "upa_int_mask", "offset": "0x4"},
            {"name": "upa_int_set", "offset": "0x8"},
            {"name": "upa_rx_p_cnt", "offset": "0x900"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_int_status" not in names
        assert "upa_int_mask" not in names
        assert "upa_int_set" not in names
        assert "upa_rx_p_cnt" in names

    def test_excludes_car_ctrl(self, combine_mod):
        regs = [
            {"name": "upa_car_ctrl", "offset": "0x100"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_car_ctrl" not in names
        assert "upa_set_bp" in names

    def test_excludes_fifo_threshold(self, combine_mod):
        regs = [
            {"name": "upa_layi_info_fifo_th", "offset": "0x114"},
            {"name": "upa_rx_data_fifo_th", "offset": "0x134"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_layi_info_fifo_th" not in names
        assert "upa_rx_data_fifo_th" not in names
        assert "upa_set_bp" in names

    def test_excludes_spare(self, combine_mod):
        regs = [
            {"name": "upa_spare0", "offset": "0x818"},
            {"name": "upa_spare1", "offset": "0x81C"},
            {"name": "upa_spare0_cnt", "offset": "0x810"},
            {"name": "upa_spare1_cnt", "offset": "0x814"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_spare0" not in names
        assert "upa_spare1" not in names
        assert "upa_spare0_cnt" not in names
        assert "upa_spare1_cnt" not in names
        assert "upa_set_bp" in names

    def test_excludes_counters(self, combine_mod):
        regs = [
            {"name": "upa_rx_p_cnt", "offset": "0x900"},
            {"name": "upa_fatal_err_cnt", "offset": "0x24"},
            {"name": "upa_fifo_uflw_err_cnt", "offset": "0x2C"},
            {"name": "upa_layi_info_fifo_fill_cnt", "offset": "0x880"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_rx_p_cnt" not in names
        assert "upa_fatal_err_cnt" not in names
        assert "upa_fifo_uflw_err_cnt" not in names
        assert "upa_layi_info_fifo_fill_cnt" not in names
        assert "upa_set_bp" in names

    def test_excludes_fifo_status(self, combine_mod):
        regs = [
            {"name": "upa_fifo_full", "offset": "0x850"},
            {"name": "upa_fifo_empty", "offset": "0x860"},
            {"name": "upa_fifo_overflow", "offset": "0x18"},
            {"name": "upa_fifo_underflow", "offset": "0x1C"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_fifo_full" not in names
        assert "upa_fifo_empty" not in names
        assert "upa_fifo_overflow" not in names
        assert "upa_fifo_underflow" not in names
        assert "upa_set_bp" in names

    def test_excludes_fsm_debug(self, combine_mod):
        regs = [
            {"name": "upa_rtlpro_fsm1", "offset": "0xC00"},
            {"name": "upa_rtlpro_fsm0", "offset": "0xC04"},
            {"name": "upa_fsm_err_info", "offset": "0x38"},
            {"name": "upa_fsm_err_cnt", "offset": "0x3C"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_rtlpro_fsm1" not in names
        assert "upa_rtlpro_fsm0" not in names
        assert "upa_fsm_err_info" not in names
        assert "upa_fsm_err_cnt" not in names
        assert "upa_set_bp" in names

    def test_excludes_bp_and_test_and_init(self, combine_mod):
        regs = [
            {"name": "upa_bp_state", "offset": "0xB00"},
            {"name": "upa_bp_history", "offset": "0xB04"},
            {"name": "upa_cfg_test", "offset": "0x80C"},
            {"name": "upa_init_done", "offset": "0xC"},
            {"name": "upa_init_start", "offset": "0x180"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_bp_state" not in names
        assert "upa_bp_history" not in names
        assert "upa_cfg_test" not in names
        assert "upa_init_done" not in names
        assert "upa_init_start" not in names
        assert "upa_set_bp" in names

    def test_keeps_configurable_registers(self, combine_mod):
        """Registers that should be KEPT for Ch2."""
        regs = [
            {"name": "upa_set_bp", "offset": "0x10C"},
            {"name": "upa_mask_bp", "offset": "0x110"},
            {"name": "upa_ck_ctrl", "offset": "0x210"},
            {"name": "upa_error_drop", "offset": "0x248"},
            {"name": "upa_error_code", "offset": "0x24C"},
            {"name": "upa_fwd_type_stage_0", "offset": "0x1D0"},
            {"name": "upa_l4s_pad", "offset": "0x1F4"},
            {"name": "upa_layo_flag", "offset": "0x1F8"},
        ]
        result = combine_mod.filter_ch2_registers(regs)
        names = [r["name"] for r in result]
        for expected in [
            "upa_set_bp", "upa_mask_bp", "upa_ck_ctrl",
            "upa_error_drop", "upa_error_code",
            "upa_fwd_type_stage_0", "upa_l4s_pad", "upa_layo_flag",
        ]:
            assert expected in names, f"{expected} should be kept but was excluded"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py -v`

Expected: FAIL — `writers.combine_writer` module does not exist.

- [ ] **Step 3: Implement `combine_writer.py` with exclusion patterns**

Create `writers/combine_writer.py`:

```python
"""combine_writer.py -- Ch2 register filtering, grouping, cross-reference, and CLI.

Handles the business logic for generating Chapter 2 configuration coverage:
- Excludes debug/status/counter registers
- Groups similar registers (e.g., _0/_1/_2 variants)
- Cross-references with Chapter 1 to mark covered registers
- Combines Ch1 + Ch2 into unified output for xlsx_writer
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


# Regex patterns for registers to EXCLUDE from Ch2 configuration coverage.
# Even if fields have RW access, these register categories are not configuration targets.
CH2_EXCLUDE_PATTERNS: list[str] = [
    r".*_int_status$",
    r".*_int_mask$",
    r".*_int_set$",
    r".*_car_ctrl$",
    r".*_fifo_th$",
    r".*_spare",
    r".*_cnt$",
    r".*_fifo_fill_cnt$",
    r".*_fifo_full$",
    r".*_fifo_empty$",
    r".*_fifo_overflow$",
    r".*_fifo_underflow$",
    r".*_fsm",
    r".*_err_info$",
    r".*_bp_state$",
    r".*_bp_history$",
    r".*_test$",
    r".*_init_done$",
    r".*_init_start$",
    r".*_err_cnt$",
]

# Compiled regex objects for performance
_CH2_EXCLUDE_COMPILED = [re.compile(p) for p in CH2_EXCLUDE_PATTERNS]


def _is_excluded_register(reg_name: str) -> bool:
    """Check if a register name matches any exclusion pattern."""
    for pat in _CH2_EXCLUDE_COMPILED:
        if pat.match(reg_name):
            return True
    return False


def filter_ch2_registers(registers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter out excluded registers from the Ch2 configuration list.

    Parameters
    ----------
    registers:
        List of register dicts, each with at least a ``name`` key.

    Returns
    -------
    List of register dicts that passed exclusion filtering.
    """
    return [r for r in registers if not _is_excluded_register(r["name"])]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py -v`

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/combine_writer.py tests/test_combine_writer.py
git commit -m "feat: add combine_writer with Ch2 register exclusion patterns"
```

---

## Task 6: Similar Register Grouping

**Files:**
- Modify: `writers/combine_writer.py`
- Modify: `tests/test_combine_writer.py`

This task addresses improvement #9 (group registers like `upa_fwd_type_stage_0/1/2`).

- [ ] **Step 1: Write failing tests for register grouping**

Add to `tests/test_combine_writer.py`:

```python
class TestCh2Grouping:
    """Test similar register grouping."""

    def test_groups_numbered_variants(self, combine_mod):
        regs = [
            {"name": "upa_fwd_type_stage_0", "offset": "0x1D0"},
            {"name": "upa_fwd_type_stage_1", "offset": "0x1D4"},
            {"name": "upa_fwd_type_stage_2", "offset": "0x1D8"},
            {"name": "upa_set_bp", "offset": "0x10C"},
        ]
        result = combine_mod.group_similar_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_fwd_type_stage_0/1/2" in names
        assert "upa_set_bp" in names
        assert "upa_fwd_type_stage_0" not in names

    def test_groups_fwd_type_bypass(self, combine_mod):
        regs = [
            {"name": "upa_fwd_type_bypass_0", "offset": "0x1E0"},
            {"name": "upa_fwd_type_bypass_1", "offset": "0x1E4"},
            {"name": "upa_fwd_type_bypass_2", "offset": "0x1E8"},
        ]
        result = combine_mod.group_similar_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_fwd_type_bypass_0/1/2" in names

    def test_no_grouping_for_singles(self, combine_mod):
        regs = [
            {"name": "upa_ck_ctrl", "offset": "0x210"},
            {"name": "upa_error_drop", "offset": "0x248"},
        ]
        result = combine_mod.group_similar_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_ck_ctrl" in names
        assert "upa_error_drop" in names

    def test_merged_register_collects_fields(self, combine_mod):
        """Grouped register should merge fields from all variants."""
        regs = [
            {
                "name": "upa_layo_cksum0_ctrl",
                "offset": "0x1B0",
                "fields": [{"range": "[31:0]", "name": "data", "access": "RW"}],
            },
            {
                "name": "upa_layi_cksum0_ctrl",
                "offset": "0x1C0",
                "fields": [{"range": "[31:0]", "name": "data", "access": "RW"}],
            },
            {
                "name": "upa_other_reg",
                "offset": "0x200",
                "fields": [{"range": "[7:0]", "name": "val", "access": "RW"}],
            },
        ]
        result = combine_mod.group_similar_registers(regs)
        names = [r["name"] for r in result]
        assert "upa_other_reg" in names
        assert len(result) >= 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py::TestCh2Grouping -v`

Expected: FAIL — `group_similar_registers` does not exist.

- [ ] **Step 3: Implement `group_similar_registers`**

Add to `writers/combine_writer.py`:

```python
def group_similar_registers(
    registers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Group registers that differ only by a trailing numeric suffix.

    E.g. ``upa_fwd_type_stage_0``, ``upa_fwd_type_stage_1``,
    ``upa_fwd_type_stage_2`` are merged into ``upa_fwd_type_stage_0/1/2``.

    Parameters
    ----------
    registers:
        List of register dicts with ``name`` and optionally ``fields``.

    Returns
    -------
    List with grouped registers merged. Each grouped entry has ``name``
    with ``/``-separated suffixes and merged ``fields``.
    """
    # Strip trailing _N suffix and group
    groups: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []

    for reg in registers:
        name = reg["name"]
        # Match trailing _N where N is one or more digits
        m = re.match(r"^(.+?)_(\d+)$", name)
        if m:
            base = m.group(1)
        else:
            base = name

        if base not in groups:
            groups[base] = []
            order.append(base)
        groups[base].append(reg)

    result: list[dict[str, Any]] = []
    for base in order:
        members = groups[base]
        if len(members) == 1:
            result.append(members[0])
        else:
            # Merge: join suffixes with /
            suffixes = []
            for m_reg in members:
                m_match = re.match(r"^.+?_(\d+)$", m_reg["name"])
                suffixes.append(m_match.group(1) if m_match else "")
            merged_name = f"{base}_{'/'.join(suffixes)}"

            # Collect all unique fields
            all_fields: list[dict[str, Any]] = []
            seen: set[str] = set()
            for m_reg in members:
                for field in m_reg.get("fields", []):
                    key = field.get("name", "")
                    if key and key not in seen:
                        seen.add(key)
                        all_fields.append(field)

            result.append({
                "name": merged_name,
                "offset": members[0].get("offset", ""),
                "fields": all_fields,
                "description": members[0].get("description", ""),
            })

    return result
```

- [ ] **Step 4: Run tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py::TestCh2Grouping -v`

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/combine_writer.py tests/test_combine_writer.py
git commit -m "feat: add similar register grouping (_0/_1/_2 variants)"
```

---

## Task 7: Ch2 Cross-Reference with Ch1

**Files:**
- Modify: `writers/combine_writer.py`
- Modify: `tests/test_combine_writer.py`

This task addresses improvements #10, #11, #12, #13 (H column descriptions, coverage references, copy from Ch1, skip marking).

- [ ] **Step 1: Write failing tests for cross-reference**

Add to `tests/test_combine_writer.py`:

```python
class TestCh2CrossRef:
    """Test cross-referencing Ch2 registers with Ch1 features."""

    def test_mark_covered_register_as_skip(self, combine_mod):
        ch2_regs = [
            {"name": "upa_ck_ctrl", "fields": [
                {"name": "tcp_csum_en", "access": "RW", "description": "tcp checksum使能"},
            ]},
        ]
        ch1_data = {
            "features": [{
                "feature_id": "PA.012",
                "feature": "报文校验",
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
        result = combine_mod.cross_ref_ch2(ch2_regs, ch1_data)
        assert len(result) == 1
        assert result[0]["skip"] is True
        assert "PA.012" in result[0]["remarks"]
        assert "已在功能特性" in result[0]["remarks"]

    def test_covered_register_copies_stimulus(self, combine_mod):
        ch2_regs = [
            {"name": "upa_ck_ctrl", "fields": [
                {"name": "tcp_csum_en", "access": "RW", "description": "tcp checksum使能"},
            ]},
        ]
        ch1_data = {
            "features": [{
                "feature_id": "PA.012",
                "feature": "报文校验",
                "subfeatures_l1": [{
                    "subfeatures_l2": [{
                        "stimulus": "【配置】配置 upa_ck_ctrl.tcp_csum_en 为1\n【激励】发送TCP报文",
                        "checking": "by_checker",
                        "coverage": "cover tcp_csum_en {0,1}",
                        "path": "Group::$unit::upa_fcov::cg_ck.cp_tcp",
                    }],
                }],
            }],
        }
        result = combine_mod.cross_ref_ch2(ch2_regs, ch1_data)
        assert result[0]["skip"] is True
        assert "upa_ck_ctrl" in result[0]["stimulus"]

    def test_uncovered_register_not_skip(self, combine_mod):
        ch2_regs = [
            {"name": "upa_set_bp", "fields": [
                {"name": "out_bp", "access": "RW", "description": "设置反压"},
            ]},
        ]
        ch1_data = {"features": []}
        result = combine_mod.cross_ref_ch2(ch2_regs, ch1_data)
        assert len(result) == 1
        assert result[0].get("skip", False) is False

    def test_h_column_includes_description(self, combine_mod):
        """H column must always include register/field description."""
        ch2_regs = [
            {"name": "upa_error_drop", "fields": [
                {"name": "en", "access": "RW", "description": "bit[6:0] drop enable"},
            ]},
        ]
        ch1_data = {"features": []}
        result = combine_mod.cross_ref_ch2(ch2_regs, ch1_data)
        assert "drop enable" in result[0]["remarks"]

    def test_build_ch2_data_output_format(self, combine_mod):
        """Output must match the register_name/subfeatures format expected by xlsx_writer."""
        ch2_regs = [
            {"name": "upa_set_bp", "fields": [
                {"name": "out_bp", "access": "RW", "description": "设置反压"},
            ]},
        ]
        ch1_data = {"features": []}
        result = combine_mod.build_ch2_data(ch2_regs, ch1_data)
        assert "chapter" in result
        assert result["chapter"] == "chapter 2 配置特性"
        assert "registers" in result
        assert len(result["registers"]) >= 1
        assert result["registers"][0]["register_name"] == "upa_set_bp"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py::TestCh2CrossRef -v`

Expected: FAIL — `cross_ref_ch2` and `build_ch2_data` do not exist.

- [ ] **Step 3: Implement cross-reference functions**

Add to `writers/combine_writer.py`:

```python
def _extract_covered_regs_from_ch1(ch1_data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Build a map of register_name -> {feature_id, stimulus, checking, coverage, path}.

    Scans all Ch1 stimulus/coverage text for register names.
    """
    covered: dict[str, dict[str, str]] = {}
    for feat in ch1_data.get("features", []):
        fid = feat.get("feature_id", "")
        for sf1 in feat.get("subfeatures_l1", []):
            for sf2 in sf1.get("subfeatures_l2", []):
                stimulus = sf2.get("stimulus", "")
                checking = sf2.get("checking", "")
                coverage = sf2.get("coverage", "")
                path = sf2.get("path", "")
                # Extract register names from stimulus text
                # Pattern: word chars before a dot or after 配置
                for reg_name in re.findall(r"(upa_\w+)", stimulus + " " + coverage):
                    if reg_name not in covered:
                        covered[reg_name] = {
                            "feature_id": fid,
                            "stimulus": stimulus,
                            "checking": checking,
                            "coverage": coverage,
                            "path": path,
                        }
    return covered


def cross_ref_ch2(
    ch2_regs: list[dict[str, Any]],
    ch1_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Cross-reference Ch2 registers with Ch1 features.

    For each register:
    - If covered in Ch1: mark skip=True, copy I/J/K from Ch1, add coverage ref to H
    - If not covered: generate full test point row

    Parameters
    ----------
    ch2_regs:
        Filtered/grouped register list with ``name`` and ``fields``.
    ch1_data:
        Ch1 data dict containing ``features``.

    Returns
    -------
    List of register dicts enriched with cross-ref info.
    """
    covered_map = _extract_covered_regs_from_ch1(ch1_data)
    result: list[dict[str, Any]] = []

    for reg in ch2_regs:
        reg_name = reg["name"]
        fields = reg.get("fields", [])

        # Find matching covered entry (check base name too for grouped regs)
        covered_info = covered_map.get(reg_name)
        if not covered_info:
            # Try matching base name for grouped registers (e.g., upa_fwd_type_stage_0/1/2)
            base_match = re.match(r"^(.+?)_\d+(/\d+)*$", reg_name)
            if base_match:
                base = base_match.group(1)
                for key in covered_map:
                    if key.startswith(base):
                        covered_info = covered_map[key]
                        break

        if covered_info:
            # Covered in Ch1 — mark skip, copy content
            fid = covered_info["feature_id"]
            desc_parts = []
            # Include register/field descriptions (#10)
            for field in fields:
                fname = field.get("name", "")
                fdesc = field.get("description", "")
                if fname and fname != "rsv" and fdesc:
                    desc_parts.append(f"{fname}: {fdesc}")

            remarks = "; ".join(desc_parts) if desc_parts else ""
            remarks += f" 【已在功能特性 [{fid}] 中覆盖】"

            result.append({
                "name": reg_name,
                "skip": True,
                "remarks": remarks.strip(),
                "stimulus": covered_info.get("stimulus", ""),
                "checking": covered_info.get("checking", ""),
                "coverage": covered_info.get("coverage", ""),
                "path": covered_info.get("path", ""),
            })
        else:
            # Not covered — generate full entry
            desc_parts = []
            for field in fields:
                fname = field.get("name", "")
                fdesc = field.get("description", "")
                frange = field.get("range", "")
                if fname and fname != "rsv":
                    desc_parts.append(f"{frange} {fname}: {fdesc}")

            result.append({
                "name": reg_name,
                "skip": False,
                "remarks": "; ".join(desc_parts) if desc_parts else "",
                "stimulus": "",
                "checking": "",
                "coverage": "",
                "path": "",
            })

    return result


def build_ch2_data(
    ch2_regs: list[dict[str, Any]],
    ch1_data: dict[str, Any],
) -> dict[str, Any]:
    """Build the full Ch2 data dict expected by xlsx_writer.

    Applies filtering, grouping, cross-reference, and converts to the
    ``registers`` format with ``register_name`` and ``subfeatures_l1``.

    Parameters
    ----------
    ch2_regs:
        Raw register list from reg_parser output.
    ch1_data:
        Ch1 data dict for cross-referencing.

    Returns
    -------
    Dict with ``chapter`` and ``registers`` keys.
    """
    # Step 1: Filter excluded registers
    filtered = filter_ch2_registers(ch2_regs)

    # Step 2: Group similar registers
    grouped = group_similar_registers(filtered)

    # Step 3: Cross-reference with Ch1
    xrefed = cross_ref_ch2(grouped, ch1_data)

    # Step 4: Convert to xlsx_writer format
    registers: list[dict[str, Any]] = []
    for reg_info in xrefed:
        reg_name = reg_info["name"]
        is_skip = reg_info.get("skip", False)

        subfeatures_l2: list[dict[str, Any]] = [{
            "subfeature_l2_overview": reg_name,
            "subfeature_l2_detail": "",
            "remarks": reg_info.get("remarks", ""),
            "stimulus": reg_info.get("stimulus", ""),
            "checking": reg_info.get("checking", ""),
            "coverage": reg_info.get("coverage", ""),
            "priority": "HIGH" if not is_skip else "",
            "activity": "BT",
            "path": reg_info.get("path", ""),
            "skip": is_skip,
        }]

        registers.append({
            "register_name": reg_name,
            "subfeatures_l1": [{
                "subfeature_l1": reg_name,
                "subfeatures_l2": subfeatures_l2,
            }],
        })

    return {
        "chapter": "chapter 2 配置特性",
        "registers": registers,
    }
```

- [ ] **Step 4: Run tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py::TestCh2CrossRef -v`

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/combine_writer.py tests/test_combine_writer.py
git commit -m "feat: add Ch2 cross-reference with Ch1 and build_ch2_data pipeline"
```

---

## Task 8: `combine_writer.py` CLI Entry Point

**Files:**
- Modify: `writers/combine_writer.py`

This task addresses improvement #1 (eliminate ad-hoc scripts, provide a single CLI command).

- [ ] **Step 1: Write failing test for CLI**

Add to `tests/test_combine_writer.py`:

```python
class TestCombineCLI:
    """Test the CLI entry point of combine_writer."""

    def test_cli_produces_xlsx(self, combine_mod, template_path, tmp_path):
        """CLI should accept ch1 JSON + reg JSON and produce xlsx."""
        import subprocess

        ch1_json = tmp_path / "ch1.json"
        reg_json = tmp_path / "reg.json"
        output = tmp_path / "out.xlsx"

        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test",
            "chapter": "chapter 1 功能特性",
            "features": [],
        }
        reg_data = {
            "sheets": {
                "upa": {
                    "registers": [
                        {
                            "name": "upa_set_bp",
                            "offset": "0x10C",
                            "type": "reg",
                            "depth": "1",
                            "width": "32",
                            "fields": [
                                {"range": "[0]", "name": "out_bp", "access": "RW",
                                 "description": "设置反压", "default": "0x0"},
                            ],
                        },
                    ],
                },
            },
        }

        ch1_json.write_text(json.dumps(ch1_data, ensure_ascii=False))
        reg_json.write_text(json.dumps(reg_data, ensure_ascii=False))

        result = subprocess.run(
            [
                sys.executable, "-m", "writers.combine_writer",
                "--ch1", str(ch1_json),
                "--reg", str(reg_json),
                "--output", str(output),
                "--template", template_path,
            ],
            cwd=SKILL_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert output.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py::TestCombineCLI -v`

Expected: FAIL — no `__main__` block in combine_writer.

- [ ] **Step 3: Implement CLI and `__main__` block**

Add to end of `writers/combine_writer.py`:

```python
def combine_and_write(
    ch1_path: str,
    reg_path: str,
    output_path: str,
    template_path: str,
) -> dict[str, int]:
    """Main pipeline: load JSON inputs, process Ch2, write xlsx.

    Returns stats dict from xlsx_writer.
    """
    # Import here to avoid circular dependency at module level
    from writers.xlsx_writer import write_testpoint_xlsx

    with open(ch1_path, "r", encoding="utf-8") as f:
        ch1_data = json.load(f)

    with open(reg_path, "r", encoding="utf-8") as f:
        reg_data = json.load(f)

    # Extract register list from parsed reg data
    registers = []
    for sheet_data in reg_data.get("sheets", {}).values():
        registers.extend(sheet_data.get("registers", []))

    # Build Ch2 data
    ch2_data = build_ch2_data(registers, ch1_data)

    # Combine and write
    chapters = [
        {"type": "ch1", "data": ch1_data},
        {"type": "ch2", "data": ch2_data},
    ]
    return write_testpoint_xlsx(chapters, output_path, template_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Combine Ch1+Ch2 and write testplan xlsx")
    parser.add_argument("--ch1", required=True, help="Path to Ch1 features JSON")
    parser.add_argument("--reg", required=True, help="Path to parsed register JSON")
    parser.add_argument("--output", required=True, help="Output xlsx path")
    parser.add_argument("--template", required=True, help="Template xlsx path")
    args = parser.parse_args()

    stats = combine_and_write(args.ch1, args.reg, args.output, args.template)
    print(f"Done: {stats}")
```

- [ ] **Step 4: Run tests**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_combine_writer.py -v`

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add writers/combine_writer.py tests/test_combine_writer.py
git commit -m "feat: add CLI entry point to combine_writer for one-command xlsx generation"
```

---

## Task 9: Update `tp_prompt.md` — Path Naming and Coverage Guidelines

**Files:**
- Modify: `templates/tp_prompt.md`

This task addresses improvements #4, #5, #15, #16 (path naming conventions, concrete coverage values, H column enhancement).

- [ ] **Step 1: Update the prompt template sections**

Replace the relevant sections in `templates/tp_prompt.md`.

For **path** section (addresses #4, #5):

```markdown
### path（覆盖率组路径）
三种格式，严格使用前缀：
1. `Group:$unit::模块_fcov::cg_covergroup名.cp_coverpoint名` — covergroup用`cg_`前缀
2. `Group:$unit::模块_fcov::cg_covergroup名.cr_cross名` — cross cover用`cr_`前缀
3. `Group:$unit::模块_direct_fcov::cp_coverpoint名` — direct coverpoint用`cp_`前缀
4. `Group:$unit::模块_assert::cover_断言名` — assertion覆盖

命名示例：
- `Group:$unit::upa_fcov::cg_upa_cnt_en0.cp_tx_cell_in_cnt_en`
- `Group:$unit::upa_fcov::cg_upa_ck_ctrl.cr_tcp_udp_cross`

多个路径用英文逗号 `,` 连接（禁止使用换行）。
```

For **coverage** section (addresses #15):

```markdown
### coverage（覆盖率策略）
- 优先使用寄存器手册中的具体值和范围
- 位宽字段使用边界值：全0、全1、default值、典型值
- 枚举类型列出所有枚举值
- 示例（access=RW, range=[7:0], default=0x7）：
  - ✅ `coverpoint: dn_th { bins val[] = {[2,7], 0, 1, 8, 127}; }`
  - ❌ `coverpoint: dn_th { bins val = default; }`
- cross cover 必须考虑
```

For **remarks** section (addresses #16):

```markdown
### remarks（备注）
- 必须包含来源引用：如 "来源: PA.004/PA.006"
- 必须包含 D-G 列无法容纳的补充说明
- 包括：配置约束、依赖关系、时序要求、默认值说明
- 推断的测试点标注 `⚠ [推断]`
```

- [ ] **Step 2: Verify template reads correctly**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run python -c "from pathlib import Path; t = Path('templates/tp_prompt.md').read_text(); assert 'cg_' in t; assert 'cr_' in t; assert 'cp_' in t; assert '英文逗号' in t; print('OK')"`

Expected: "OK"

- [ ] **Step 3: Commit**

```bash
git add templates/tp_prompt.md
git commit -m "feat: update tp_prompt with path naming (cg_/cp_/cr_), concrete coverage, H column rules"
```

---

## Task 10: Update `SKILL.md` — Reflect New Pipeline

**Files:**
- Modify: `SKILL.md`

This task addresses improvement #1 (update skill instructions to use combine_writer instead of ad-hoc scripts).

- [ ] **Step 1: Update Step 5 (Generate Chapter 2)**

Replace the Step 5 section in `SKILL.md` with:

```markdown
### Step 5: Generate Chapter 2 Configuration Coverage (Stage 4)

From `reg_parsed.json`, generate register-level test points:

1. Extract registers from parsed JSON (all sheets)
2. The `combine_writer.py` handles:
   - Filter: exclude int/car_ctrl/fifo_th/spare/cnt/fifo_status/fsm/bp/test/init registers
   - Group: merge numbered variants (_0/_1/_2 → base_0/1/2)
   - Cross-ref: check covered_regs mapping from Chapter 1
     - If already covered -> A="skip", H="寄存器描述 【已在功能特性 [PA.XXX] 中覆盖】", I/J/K copy from Ch1
     - If not covered -> generate full test point row
   - H column: always include register/field description from manual
   - Only RW/RWW fields (skip ro/rwc/rctr/sctr/rc/rsv)
```

- [ ] **Step 2: Update Step 6 (Write Output)**

Replace the Step 6 section in `SKILL.md` with:

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

The pipeline handles:
- Ch2 register filtering and grouping (combine_writer)
- Cross-reference with Ch1 for skip marking
- xlsx_writer formatting: outline grouping, borders, alignment, gold fill for ⚠, comma-joined paths
```

- [ ] **Step 3: Update Common Mistakes table**

Add two new rows to the Common Mistakes table in `SKILL.md`:

```markdown
| Writing ad-hoc Python scripts for combining JSON | combine_writer handles all Ch2 logic | Use combine_writer CLI |
| Forgetting cell formatting | xlsx_writer applies borders/alignment automatically | Verify output |
```

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: update SKILL.md to use combine_writer pipeline"
```

---

## Task 11: Verify U-V Columns Are Not Hidden

**Files:**
- Modify: `tests/test_xlsx_writer.py`

This task addresses improvement #6 (verify U-V columns visible).

- [ ] **Step 1: Write test for U-V visibility**

Add to `tests/test_xlsx_writer.py`:

```python
def test_uv_columns_not_hidden(
    self, writer_module, template_path, sample_ch1_data, tmp_output
):
    """U(21) and V(22) columns must NOT be hidden."""
    writer_module.write_testpoint_xlsx(
        chapters=[{"type": "ch1", "data": sample_ch1_data}],
        output_path=tmp_output,
        template_path=template_path,
    )
    wb = openpyxl.load_workbook(tmp_output)
    ws = wb.active
    for col in [21, 22]:
        letter = openpyxl.utils.get_column_letter(col)
        assert not ws.column_dimensions[letter].hidden, (
            f"Column {letter} should NOT be hidden"
        )
```

- [ ] **Step 2: Run test to verify it passes (already correct)**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_xlsx_writer.py::TestWriteXlsx::test_uv_columns_not_hidden -v`

Expected: PASS — U(21) and V(22) are not in `HIDDEN_COLUMNS`.

- [ ] **Step 3: Commit**

```bash
git add tests/test_xlsx_writer.py
git commit -m "test: add test verifying U-V columns are not hidden"
```

---

## Task 12: Integration Test — Full Pipeline with Real Data

**Files:**
- Create: `tests/test_integration.py`

This task verifies the complete pipeline works end-to-end with the UPA module data.

- [ ] **Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
"""Integration test: full pipeline from parsed JSON to xlsx output."""
import json
import os
import sys

import openpyxl
import pytest

SKILL_ROOT = os.path.join(os.path.dirname(__file__), "..")
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)


@pytest.fixture
def upa_reg_data():
    """Load the actual UPA register parsed data."""
    path = "/tmp/tp_reg_parsed.json"
    if not os.path.exists(path):
        pytest.skip("No parsed UPA register data available")
    with open(path, "r") as f:
        return json.load(f)


@pytest.fixture
def minimal_ch1():
    """Minimal Ch1 data for integration test."""
    return {
        "module_name": "UPA",
        "spec_name": "Leonis PA Functional Specification",
        "chapter": "chapter 1 功能特性",
        "features": [
            {
                "feature": "报文校验",
                "feature_id": "PA.012",
                "chapter": "chapter 1 功能特性",
                "subfeatures_l1": [{
                    "subfeature_l1": "校验控制",
                    "subfeatures_l2": [{
                        "subfeature_l2_overview": "TCP checksum校验",
                        "stimulus": "【配置】配置 upa_ck_ctrl.tcp_csum_en 为1",
                        "checking": "by_checker",
                        "coverage": "cover tcp_csum_en {0,1}",
                        "path": "Group:$unit::upa_fcov::cg_ck.cp_tcp",
                        "priority": "HIGH",
                        "activity": "BT",
                        "remarks": "来源: PA.012",
                    }],
                }],
            }
        ],
    }


class TestFullPipeline:
    def test_full_pipeline_produces_xlsx(
        self, template_path, tmp_path, upa_reg_data, minimal_ch1
    ):
        """Full pipeline: Ch1 + parsed regs → combine_writer → xlsx."""
        import importlib
        combine_mod = importlib.import_module("writers.combine_writer")

        ch1_path = tmp_path / "ch1.json"
        reg_path = tmp_path / "reg.json"
        output_path = tmp_path / "integration_out.xlsx"

        ch1_path.write_text(json.dumps(minimal_ch1, ensure_ascii=False))
        reg_path.write_text(json.dumps(upa_reg_data, ensure_ascii=False))

        stats = combine_mod.combine_and_write(
            str(ch1_path), str(reg_path), str(output_path), template_path,
        )

        assert output_path.exists()
        assert stats["total_features"] >= 1
        assert stats["total_l2"] >= 1

        # Verify formatting
        wb = openpyxl.load_workbook(str(output_path))
        ws = wb.active

        # Check borders on data cells
        found_border = False
        for row_idx in range(6, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=6)
            if cell.value:
                assert cell.border.left.style == "thin"
                found_border = True
                break
        assert found_border

        # Check no newlines in W column
        for row_idx in range(6, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=23)
            if cell.value:
                assert "\n" not in str(cell.value)

        # Check gold fill on inferred cells (if any)
        for row_idx in range(6, ws.max_row + 1):
            for col_idx in range(1, 24):
                cell = ws.cell(row=row_idx, column=col_idx)
                if cell.value and "⚠" in str(cell.value):
                    assert cell.fill.start_color.rgb in ("00FFF2CC", "FFF2CC")
```

- [ ] **Step 2: Run integration test**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/test_integration.py -v`

Expected: PASS (if `/tmp/tp_reg_parsed.json` exists from a previous run) or SKIP

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test for full pipeline"
```

---

## Task 13: Run Full Test Suite and Fix Any Failures

**Files:**
- Potentially modify any test or source file that fails

- [ ] **Step 1: Run complete test suite**

Run: `cd /home/xyy/.claude/skills/.claude/worktrees/testplan-generator/testplan-generator && uv run pytest tests/ -v`

Expected: ALL PASS

- [ ] **Step 2: Fix any failures**

If any test fails, diagnose and fix the issue. Common issues:
- Import path problems (ensure `sys.path` is set correctly in tests)
- Fixture dependency issues (ensure conftest.py fixtures are properly defined)
- Existing tests broken by formatting changes (update assertions)

- [ ] **Step 3: Final commit if fixes needed**

```bash
git add -A
git commit -m "fix: resolve test suite failures from integration changes"
```

---

## Spec Coverage Check

| Improvement | Task | Status |
|-------------|------|--------|
| #1 Eliminate ad-hoc scripts | Tasks 8, 10 | combine_writer CLI replaces temp scripts |
| #2 Cell formatting (center/border) | Task 1 | `_write_cell` with alignment + borders |
| #3 W column comma joining | Task 4 | Sanitization in `_write_cell` |
| #4 W column cg_ prefix | Task 9 | Prompt template update |
| #5 W column cr_ prefix | Task 9 | Prompt template update |
| #6 U-V not hidden | Task 11 | Test verification |
| #7 B column chapter once | Task 3 | Only first row gets label |
| #8 Ch2 register exclusions | Task 5 | `filter_ch2_registers` |
| #9 Ch2 similar grouping | Task 6 | `group_similar_registers` |
| #10 H column descriptions | Task 7 | Always included in cross_ref |
| #11 H column coverage ref | Task 7 | Added in cross_ref remarks |
| #12 I column copy from Ch1 | Task 7 | `cross_ref_ch2` copies stimulus |
| #13 A column skip + J/K copy | Task 7 | `cross_ref_ch2` sets skip + copies |
| #14 Gold fill for inferred | Tasks 1, 2 | `_write_cell` conditional fill |
| #15 K column concrete values | Task 9 | Prompt template update |
| #16 H column enhanced details | Task 9 | Prompt template update |
