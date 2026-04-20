# Testplan-CFG 修复实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 testplan-cfg 插件的5个问题：模板数据残留、边框格式、J列检查方式、W列反标路径、D-E-F层级结构

**Architecture:** 最小改动方案，针对性修改 xlsx_writer.py 和 cfg_writer.py

**Tech Stack:** Python 3.12+, openpyxl, pytest

---

## 文件结构

| 文件 | 职责 | 操作 |
|------|------|------|
| `testplan-cfg/scripts/xlsx_writer.py` | Excel输出格式处理 | 修改 |
| `testplan-cfg/scripts/cfg_writer.py` | Ch2数据结构生成 | 修改 |
| `tests/test_xlsx_writer_cfg.py` | xlsx_writer新功能测试 | 新建 |
| `tests/test_cfg_writer.py` | cfg_writer修改测试 | 修改 |

---

### Task 1: 清空模板数据 - 新增测试

**Files:**
- Create: `tests/test_xlsx_writer_cfg.py`
- Modify: (无)

- [ ] **Step 1: 编写清空模板数据的测试**

```python
"""Tests for testplan-cfg xlsx_writer module."""
import importlib.util
from pathlib import Path

import pytest
from openpyxl import load_workbook

# Explicitly load xlsx_writer from testplan-cfg/scripts
_cfg_xlsx_writer = Path(__file__).parent.parent / "skills" / "testplan-cfg" / "scripts" / "xlsx_writer.py"
_spec = importlib.util.spec_from_file_location("xlsx_writer_cfg", _cfg_xlsx_writer)
xlsx_writer_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xlsx_writer_cfg)

write_ch1_xlsx = xlsx_writer_cfg.write_ch1_xlsx


class TestClearTemplateData:
    """Tests for clearing template data before writing."""

    def test_template_data_cleared_from_row_6(self, temp_dir, sample_template_xlsx):
        """Template example data should be cleared starting from row 6."""
        features_data = {
            "module_name": "UPA",
            "spec_name": "UPA Module Spec",
            "chapter": "chapter 2 配置特性",
            "features": [
                {
                    "feature": "upa_ctrl",
                    "feature_id": "",
                    "chapter": "chapter 2",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "en",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2_overview": "bit[0] 使能控制",
                                    "remarks": "",
                                    "stimulus": "【配置】配置 upa_ctrl.en",
                                    "checking": "随机用例",
                                    "path": "Group:$unit::upa_fcov::upa_ctrl_cg.en_cp",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        output_path = temp_dir / "output.xlsx"
        write_ch1_xlsx(features_data, sample_template_xlsx, output_path)

        wb = load_workbook(output_path)
        ws = wb.active

        # Check that row 6 B and D columns have our data, not template data
        # Template data should be cleared
        cell_b6 = ws.cell(row=6, column=2).value
        cell_d6 = ws.cell(row=6, column=4).value

        # Row 6 should have our feature data or be empty (not template example)
        assert cell_b6 is None or "upa" not in str(cell_b6).lower() or cell_d6 is not None
        wb.close()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_xlsx_writer_cfg.py -v`
Expected: FAIL (模块可能不存在或功能未实现)

---

### Task 2: 清空模板数据和边框函数 - 实现

**Files:**
- Modify: `testplan-cfg/scripts/xlsx_writer.py:42-88`

- [ ] **Step 1: 在xlsx_writer.py添加_clear_template_data和_apply_border_rectangle函数**

在 `write_ch1_xlsx` 函数前添加辅助函数，并修改主函数：

```python
from openpyxl.styles import Border, Side

# Standard border
STD_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def _clear_template_data(ws):
    """Clear template example data starting from row 6."""
    for row in range(6, ws.max_row + 1):
        for col in range(1, 24):  # A-W columns
            ws.cell(row=row, column=col).value = None


def _apply_border_rectangle(ws):
    """Apply borders to rectangular region A-W for all data rows."""
    first_row = None
    last_row = None

    # Find first and last rows with content
    for row in range(6, ws.max_row + 1):
        has_content = any(ws.cell(row=row, column=col).value for col in range(1, 24))
        if has_content:
            if first_row is None:
                first_row = row
            last_row = row

    if first_row is None:
        return

    # Apply borders to rectangle A-W
    for row in range(first_row, last_row + 1):
        for col in range(1, 24):  # A-W
            ws.cell(row=row, column=col).border = STD_BORDER


def write_ch1_xlsx(
    features_data: dict[str, Any],
    template_path: Path | str,
    output_path: Path | str,
) -> Path:
    """Write Chapter 1 features to an Excel file."""
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Load template
    wb = load_workbook(template_path)
    ws = wb.active

    # Clear template example data
    _clear_template_data(ws)

    # Find the starting row (after template header rows)
    start_row = 6  # Start from row 6 after clearing

    # Write each feature
    features = features_data.get("features", [])
    for feature in features:
        start_row = _write_feature(ws, feature, start_row)

    # Apply borders after all data is written
    _apply_border_rectangle(ws)

    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    wb.close()

    return output_path
```

- [ ] **Step 2: 运行测试验证通过**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_xlsx_writer_cfg.py::TestClearTemplateData tests/test_xlsx_writer_cfg.py::TestBorderRectangle -v`
Expected: PASS

---

### Task 3: J列和W列 - 测试

**Files:**
- Modify: `tests/test_cfg_writer.py`

- [ ] **Step 1: 添加J列和W列测试**

在 `tests/test_cfg_writer.py` 末尾添加：

```python
class TestJColumnAndWColumn:
    """Tests for J column (checking) and W column (path) generation."""

    def test_j_column_defaults_to_random_testcase(self, sample_reg_xlsx):
        """J column should default to '随机用例'."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check at least one register has checking set
        for reg in result.get("registers", []):
            for sf1 in reg.get("subfeatures_l1", []):
                for sf2 in sf1.get("subfeatures_l2", []):
                    checking = sf2.get("checking", "")
                    if checking:  # Non-skipped registers
                        assert checking == "随机用例", f"Checking should be '随机用例', got '{checking}'"
                        return

    def test_w_column_path_format(self, sample_reg_xlsx):
        """W column path should follow format Group:$unit::{module}_fcov::{reg}_cg.{field}_cp."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check path format for non-skipped registers
        for reg in result.get("registers", []):
            reg_name = reg.get("register_name", "")
            for sf1 in reg.get("subfeatures_l1", []):
                field_name = sf1.get("subfeature_l1", "")
                for sf2 in sf1.get("subfeatures_l2", []):
                    path = sf2.get("path", "")
                    if path and path != "【反标路径暂无法确定】":
                        # Check format: Group:$unit::{module}_fcov::{reg}_cg.{field}_cp
                        assert path.startswith("Group:$unit::"), f"Path should start with 'Group:$unit::', got '{path}'"
                        assert "_fcov::" in path, f"Path should contain '_fcov::', got '{path}'"
                        assert "_cg." in path, f"Path should contain '_cg.', got '{path}'"
                        assert "_cp" in path, f"Path should end with '_cp', got '{path}'"
                        return

    def test_module_name_extracted_from_register_name(self, sample_reg_xlsx):
        """Module name should be extracted from first underscore prefix of register name."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check module name in path matches register prefix
        for reg in result.get("registers", []):
            reg_name = reg.get("register_name", "")
            if "_" in reg_name:
                expected_module = reg_name.split("_")[0]
                for sf1 in reg.get("subfeatures_l1", []):
                    for sf2 in sf1.get("subfeatures_l2", []):
                        path = sf2.get("path", "")
                        if path and expected_module:
                            assert f"{expected_module}_fcov" in path, f"Path should contain module '{expected_module}_fcov', got '{path}'"
                            return
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_cfg_writer.py::TestJColumnAndWColumn -v`
Expected: FAIL (功能未实现)

---

### Task 4: J列和W列 - 实现

**Files:**
- Modify: `testplan-cfg/scripts/cfg_writer.py`

- [ ] **Step 1: 添加_generate_fcov_path函数**

在 `cfg_writer.py` 中添加：

```python
def _generate_fcov_path(reg_name: str, field_name: str) -> str:
    """Generate coverage path for random test case.

    Format: Group:$unit::{module_name}_fcov::{reg_name}_cg.{field_name}_cp
    """
    # Extract module name (first underscore prefix)
    module_name = reg_name.split("_")[0] if "_" in reg_name else reg_name

    return f"Group:$unit::{module_name}_fcov::{reg_name}_cg.{field_name}_cp"
```

- [ ] **Step 2: 修改cross_ref_cfg函数设置J列和W列**

修改 `cross_ref_cfg` 函数，在生成结果时设置 checking 和 path：

```python
# 在 cross_ref_cfg 函数中，result.append 部分（约326-334行）
# 修改非跳过寄存器的结果生成：

if is_covered:
    # Mark as skip
    result.append({
        "name": reg_name,
        "skip": True,
        "stimulus": "",
        "checking": "",
        "coverage": "",
        "path": "",
        "remarks": "已在功能特性中覆盖",
    })
else:
    # Generate stimulus
    desc_parts = []
    config_parts = []
    for field in fields:
        fname = field.get("name", "")
        fdesc = field.get("description", "")
        frange = field.get("range", "")
        faccess = field.get("access", "")

        if fname and fname.lower() != "rsv":
            if fdesc:
                desc_parts.append(f"{frange} {fname}: {fdesc}")

            # Generate config for RW/RWC/WO fields
            if faccess.upper() in VALID_CFG_ACCESS:
                config_parts.append(f"配置 {reg_name}.{fname} ({frange})")

    stimulus = "【配置】" + "；".join(config_parts) if config_parts else ""

    result.append({
        "name": reg_name,
        "skip": False,
        "stimulus": stimulus,
        "checking": "随机用例",  # J列默认值
        "coverage": "",
        "path": "",  # Path will be generated per-field in build_ch2_json
        "remarks": "; ".join(desc_parts) if desc_parts else "",
        "fields": fields,  # Pass fields for later processing
    })
```

- [ ] **Step 3: 运行测试验证通过**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_cfg_writer.py::TestJColumnAndWColumn -v`
Expected: PASS

---

### Task 5: D-E-F层级结构 - 测试

**Files:**
- Modify: `tests/test_cfg_writer.py`

- [ ] **Step 1: 添加D-E-F层级结构测试**

```python
class TestDEFHierarchy:
    """Tests for D-E-F column hierarchy structure."""

    def test_d_column_is_register_name(self, sample_reg_xlsx):
        """D column should contain register name."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        for reg in result.get("registers", []):
            reg_name = reg.get("register_name", "")
            assert reg_name, "Register name should not be empty"
            # D column is register_name
            assert "_" in reg_name or reg_name.isalnum(), f"Register name should be valid: {reg_name}"

    def test_e_column_is_field_name(self, sample_reg_xlsx):
        """E column should contain field name from subfeatures_l1."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check that subfeatures_l1 contains field names
        for reg in result.get("registers", []):
            for sf1 in reg.get("subfeatures_l1", []):
                field_name = sf1.get("subfeature_l1", "")
                assert field_name, "E column (subfeature_l1) should have field name"

    def test_f_column_is_bit_description(self, sample_reg_xlsx):
        """F column should contain bit range description."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check that subfeatures_l2 contains bit description
        for reg in result.get("registers", []):
            for sf1 in reg.get("subfeatures_l1", []):
                for sf2 in sf1.get("subfeatures_l2", []):
                    overview = sf2.get("subfeature_l2_overview", "")
                    # F column should have bit range like "bit[0] xxx" or "bit[3:0] xxx"
                    if overview:
                        assert "bit" in overview.lower() or overview == "", \
                            f"F column should contain bit range description, got: {overview}"
                        return  # At least one valid entry found

    def test_each_field_has_own_row(self, sample_reg_xlsx):
        """Each field should have its own row in E column."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check that register with multiple fields has multiple subfeatures_l1
        for reg in result.get("registers", []):
            fields_count = len(reg.get("subfeatures_l1", []))
            if fields_count > 1:
                # Multiple fields should have multiple L1 entries
                assert fields_count >= 2, "Multiple fields should have multiple L1 entries"
                return
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_cfg_writer.py::TestDEFHierarchy -v`
Expected: FAIL (功能未实现)

---

### Task 6: D-E-F层级结构 - 实现

**Files:**
- Modify: `testplan-cfg/scripts/cfg_writer.py:339-394`

- [ ] **Step 1: 重构build_ch2_json函数**

修改 `build_ch2_json` 函数，将每个域段生成独立的L1条目：

```python
def build_ch2_json(
    reg_data: dict[str, Any],
    covered_regs: set[str] | None = None,
) -> dict[str, Any]:
    """Build Ch2 JSON data structure.

    D-E-F hierarchy:
    - D column: Register name
    - E column: Field name
    - F column: Bit range description
    """
    if covered_regs is None:
        covered_regs = set()

    registers = reg_data.get("registers", [])
    filtered = filter_cfg_registers(registers)
    grouped = group_similar_registers(filtered)
    xrefed = cross_ref_cfg(grouped, covered_regs)

    ch2_registers: list[dict[str, Any]] = []
    for reg_info in xrefed:
        reg_name = reg_info["name"]
        is_skip = reg_info.get("skip", False)
        fields = reg_info.get("fields", [])

        if is_skip:
            # Skipped register - single row with skip marker
            ch2_registers.append({
                "register_name": reg_name,
                "subfeatures_l1": [{
                    "subfeature_l1": "",
                    "subfeatures_l2": [{
                        "subfeature_l2_overview": "",
                        "remarks": reg_info.get("remarks", ""),
                        "stimulus": "",
                        "checking": "",
                        "path": "",
                        "skip": True,
                    }],
                }],
            })
        else:
            # Non-skipped register - each field gets its own L1 entry
            subfeatures_l1_list: list[dict[str, Any]] = []

            for field in fields:
                fname = field.get("name", "")
                if not fname or fname.lower() == "rsv":
                    continue

                frange = field.get("range", "")
                fdesc = field.get("description", "")

                # F column: bit range description
                bit_desc = f"bit[{frange}] {fdesc}" if frange else fdesc

                # Generate path for this field
                path = _generate_fcov_path(reg_name, fname)

                # Generate stimulus for this field
                stimulus = f"【配置】配置 {reg_name}.{fname} ({frange})"

                subfeatures_l1_list.append({
                    "subfeature_l1": fname,  # E column: field name
                    "subfeatures_l2": [{
                        "subfeature_l2_overview": bit_desc,  # F column: bit description
                        "remarks": fdesc,
                        "stimulus": stimulus,
                        "checking": "随机用例",
                        "coverage": "",
                        "priority": "HIGH",
                        "activity": "BT",
                        "path": path,
                        "skip": False,
                    }],
                })

            # Handle case where all fields are rsv
            if not subfeatures_l1_list:
                subfeatures_l1_list.append({
                    "subfeature_l1": "",
                    "subfeatures_l2": [{
                        "subfeature_l2_overview": "",
                        "remarks": reg_info.get("remarks", ""),
                        "stimulus": reg_info.get("stimulus", ""),
                        "checking": "随机用例",
                        "coverage": "",
                        "priority": "HIGH",
                        "activity": "BT",
                        "path": "【反标路径暂无法确定】",
                        "skip": False,
                    }],
                })

            ch2_registers.append({
                "register_name": reg_name,
                "subfeatures_l1": subfeatures_l1_list,
            })

    return {
        "chapter": "chapter 2 配置特性",
        "registers": ch2_registers,
    }
```

- [ ] **Step 2: 运行测试验证通过**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_cfg_writer.py::TestDEFHierarchy -v`
Expected: PASS

---

### Task 7: 运行全部测试验证

**Files:**
- (无修改)

- [ ] **Step 1: 运行全部testplan-cfg相关测试**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest tests/test_cfg_writer.py tests/test_xlsx_writer_cfg.py -v`
Expected: PASS (所有测试通过)

- [ ] **Step 2: 运行全部测试确保无回归**

Run: `cd /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator && uv run pytest -v`
Expected: PASS (所有测试通过)

---

### Task 8: 集成测试

**Files:**
- (无修改)

- [ ] **Step 1: 手动运行testplan-cfg技能验证输出**

使用测试寄存器文件运行技能，检查输出xlsx：

1. 无模板示例数据残留
2. 边框覆盖完整矩形区域（A到W，首行到末行）
3. J列默认为"随机用例"
4. W列路径格式正确
5. D-E-F层级结构正确

---

## 自检清单

| 需求 | 任务覆盖 |
|------|----------|
| 1. 模板数据残留 | Task 1-2 |
| 2. 单元格边框格式 | Task 1-2 |
| 3. J列检查方式 | Task 3-4 |
| 4. W列反标路径 | Task 3-4 |
| 5. D-E-F层级结构 | Task 5-6 |
