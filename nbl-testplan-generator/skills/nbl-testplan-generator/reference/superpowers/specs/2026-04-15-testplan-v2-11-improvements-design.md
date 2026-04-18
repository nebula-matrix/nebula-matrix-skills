# Testplan Generator V2 — 11-Point Improvement Design

**Goal:** Improve testplan-generator with 11 enhancements covering cell formatting (font/color/borders/newlines), content logic (J-W correspondence, Ch2 F-column, I-column, path fallback, inferred marking, script consolidation), and content quality (no fabrication).

**Architecture:** Layered approach — Format layer (xlsx_writer.py) first, then Content layer (combine_writer.py, SKILL.md, tp_prompt.md). Format changes are independently testable via TDD.

**Tech Stack:** Python 3.12+, openpyxl, pytest, uv

---

## Requirements Summary

| # | Category | Description | Layer |
|---|----------|-------------|-------|
| 1 | Formatting | Font: 微软雅黑(size=10, color=black); I列 `【配置】`/`【激励】` red | Format |
| 2 | Formatting | Cell content line-breaks on `;` `。` `：` `:` `（` brackets; wrap_text on ALL data columns | Format |
| 3 | Formatting | Border logic: find first/last content rows, border full rectangle A-W | Format |
| 4 | Content | J=by_direct_tc → W=`Group:$unit::xxx_direct_fcov::cp_direct_xxx_0` | Content |
| 5 | Content | J=by_assertion → W=`Group:$unit::xxx_assert::xxx_c` | Content |
| 6 | Content | Ch2 F-column: completely empty (D+E sufficient) | Content |
| 7 | Content | W-column empty → fill `【反标路径暂无法确定】` | Content |
| 8 | Content | Ch2 I-column: fill 【配置】 from register manual | Content |
| 9 | Formatting | `⚠ [推断]` markers: red font color (replace current gold fill) | Format |
| 10 | Content | No ad-hoc scripts; consolidate into skill's existing modules | Content |
| 11 | Content | No fabricated info; use `⚠ [推断]` or omit; review.md tracks issues | Content |

---

## Requirement 11 Clarification

Requirement 11 (spec/register issues → fs_reg_slv_review.md) is **covered by existing review_writer.py** which already supports:
- 5-category issue classification (spec_defect, reg_missing, logic_conflict, param_undefined, coverage_gap)
- Markdown review generation with structured issue blocks
- Refresh workflow: parse user resolutions → regenerate test points

The review file naming convention will be updated: `review_output_path` defaults to `<output_dir>/fs_reg_slv_review.md` instead of a separate path.

---

## Design Details

### Format Layer (xlsx_writer.py)

#### 1. Font Configuration

**Constants:**

```python
# Default data cell font
DEFAULT_FONT_NAME = "微软雅黑"
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT_COLOR = "000000"  # black

# Red font for specific markers
RED_FONT_COLOR = "FF0000"
```

**`_write_cell` changes:**

- All non-empty data cells get `Font(name=DEFAULT_FONT_NAME, size=DEFAULT_FONT_SIZE, color=DEFAULT_FONT_COLOR)`
- Font fallback: if `DEFAULT_FONT_NAME` is not found, openpyxl still writes the name string into xlsx; the actual rendering happens on the user's machine where 微软雅黑 is installed. No runtime fallback needed.
- I-column (col 9): when value contains `【配置】` or `【激励】`, the cell gets red font instead of black. This is a cell-level font, not inline rich text (openpyxl supports RichText but it's complex; cell-level red font is simpler and sufficient since the entire I-column stimulus text relates to these markers).
- `⚠ [推断]` cells (any column): red font color replaces current gold fill (keep gold fill as background too for visual distinction).

**Why cell-level font, not RichText:**
openpyxl's `InlineFont` / `RichText` requires manual text segmentation for each marker occurrence, adding significant complexity. Cell-level font change (entire cell red when it contains `【配置】` or `⚠`) is much simpler and achieves the visual goal. If future needs require inline coloring, it can be added as a separate enhancement.

#### 2. Content Line-Breaks

**Logic:** Before writing a cell value, scan for break-inducing characters and insert `\n`:

```python
BREAK_CHARS = [";", "；", "。", "：", ":", "（", "）", "(", ")"]
```

**Rules:**
- After each break character, insert `\n` (if not already at line end)
- Apply to ALL data columns (D through W) — `WRAP_TEXT_COLUMNS` expands to `set(range(4, 24))`
- Exception: W column (paths) does NOT get line-break insertion (paths use comma joining, already handled)
- The line-break insertion happens in `_write_cell` before font/border application

**Implementation location:** New helper `_insert_line_breaks(text: str) -> str` called by `_write_cell`.

#### 3. Border Logic — Rectangle Region

**Current:** borders on individual non-empty cells.

**New logic:**

1. After all data is written (in `write_testpoint_xlsx`, after all chapters are written), find `first_data_row` (first row >= 6 with any content) and `last_data_row` (last row with any content)
2. Apply thin borders to the entire rectangle: columns A(1) through W(23), rows `first_data_row` through `last_data_row`
3. This replaces the current per-cell border logic in `_write_cell` — borders are applied as a post-processing step

**Why post-processing:**
Per-cell borders during writing require knowing the full row extent. A post-processing pass is cleaner and avoids tracking state during writes.

### Content Layer

#### 4 & 5. J-W Correspondence (checking ↔ path)

**Two-phase approach:**

**Phase 1 — Generation (tp_prompt.md + SKILL.md):**
- Update tp_prompt.md to document the J-W correspondence rules
- When J=`by_direct_tc`, W must follow: `Group:$unit::模块_direct_fcov::cp_direct_描述_序号`
- When J=`by_assertion`, W must follow: `Group:$unit::模块_assert::描述_c`

**Phase 2 — Validation (combine_writer.py):**
- New function `validate_jw_correspondence(data: dict) -> dict`:
  - Scans all L2 entries
  - If J=`by_direct_tc` and W doesn't contain `_direct_fcov::cp_direct_`, auto-correct W
  - If J=`by_assertion` and W doesn't contain `_assert::`, auto-correct W
  - If W is empty and J is `by_checker`, leave empty (coverage path is optional for checker-based tests)
- Called as part of `build_ch2_data` and also available for Ch1 post-processing

**Path generation formula:**
- Module name extracted from `module_name` field (lowercase)
- Description derived from subfeature_l2_overview (sanitized to snake_case)
- Sequence number auto-incremented if duplicates detected

#### 6. Ch2 F-Column Empty

**combine_writer.py change:**
In `build_ch2_data`, the L2 `subfeature_l2_overview` field (which maps to F column) is set to `""` instead of `reg_name`:

```python
"subfeature_l2_overview": "",  # was: reg_name
```

#### 7. W-Column Fallback Text

**combine_writer.py change:**
When path is empty and the entry is not skipped:

```python
"path": reg_info.get("path", "") or "【反标路径暂无法确定】",
```

For Ch1 generation (SKILL.md / tp_prompt.md):
- Add rule: if coverage path cannot be determined from spec, fill `【反标路径暂无法确定】`

#### 8. Ch2 I-Column 【配置】 Fill

**combine_writer.py change:**
For uncovered registers (skip=False), generate I-column content from register field info:

```python
# Build config description from RW fields
config_parts = []
for field in fields:
    if field.get("access", "") in ("RW", "RWW") and field.get("name", "") != "rsv":
        frange = field.get("range", "")
        fname = field.get("name", "")
        fdesc = field.get("description", "")
        config_parts.append(f"配置 {reg_name}.{fname} ({frange})")
stimulus = "【配置】" + "；".join(config_parts) if config_parts else ""
```

#### 9. ⚠ [推断] Red Font (replaces gold fill emphasis)

**xlsx_writer.py change:**
- Keep gold fill (`GOLD_LIGHT_FILL`) for `⚠ [推断]` cells (background)
- Add red font (`Font(color=RED_FONT_COLOR)`) for `⚠ [推断]` cells (foreground)
- Both background and foreground emphasis together provide maximum visual distinction

#### 10. Script Consolidation

**SKILL.md changes:**
- Ensure all pipeline steps reference existing Python modules (parsers, writers, review)
- Remove any instructions that suggest creating temporary scripts
- Update Step 6 to exclusively use `combine_writer.py` CLI

#### 11 & 12. No Fabrication + Review Tracking

**SKILL.md / tp_prompt.md changes:**
- Strengthen rule: if info not in parsed docx/xlsx → mark `⚠ [推断]` or omit entirely
- Review file naming: default to `<output_dir>/fs_reg_slv_review.md`
- Existing review_writer.py categories already cover: spec_defect (功能规格缺失), reg_missing (寄存器手册缺失), logic_conflict (逻辑冲突), param_undefined (参数未定义), coverage_gap (覆盖缺失)

---

## File Change Summary

| File | Changes | Layer |
|------|---------|-------|
| `writers/xlsx_writer.py` | Font config, line-breaks, border rectangle, red font for ⚠/【配置】 | Format |
| `writers/combine_writer.py` | F-column empty, W-column fallback, I-column fill, J-W validation | Content |
| `templates/tp_prompt.md` | J-W rules, path fallback rule, no-fabrication rule | Content |
| `SKILL.md` | Script consolidation, review naming, I-column instruction | Content |
| `tests/test_xlsx_writer.py` | Font/border/newline/red-font tests | Test |
| `tests/test_combine_writer.py` | F-column/W-fallback/I-fill/J-W tests | Test |
| `tests/conftest.py` | New fixtures for font/newline testing | Test |

---

## Scope Check

This spec covers a single coordinated improvement to the testplan-generator skill. All 11 requirements are related (formatting + content quality) and share the same pipeline. No decomposition needed.
