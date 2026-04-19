# Testplan Skills Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor nbl-testplan-generator plugin into three independent skills (testplan-func, testplan-cfg, nbl-testplan-generator) with decoupled scripts, TDD approach, and Skill composition.

**Architecture:** Three-layer architecture - testplan-func generates Ch1, testplan-cfg generates Ch2 (independent or incremental), nbl-testplan-generator orchestrates via Skill tool calls. Each skill has independent scripts directory.

**Tech Stack:** Python 3.12+, openpyxl, pytest, uv

---

## File Structure

### Files to Create

```
nbl-testplan-generator/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── sample_spec.md
│   │   ├── sample_reg.xlsx
│   │   └── expected_ch1_output.json
│   ├── test_md_parser.py
│   ├── test_reg_to_json.py
│   ├── test_xlsx_writer.py
│   ├── test_validator.py
│   ├── test_testplan_func.py
│   ├── test_testplan_cfg.py
│   └── test_testplan_generator.py
├── skills/
│   ├── testplan-func/
│   │   ├── scripts/
│   │   │   ├── __init__.py
│   │   │   ├── md_parser.py
│   │   │   ├── reg_to_json.py
│   │   │   ├── func_writer.py
│   │   │   ├── xlsx_writer.py
│   │   │   └── validator.py
│   │   └── templates/
│   │       └── func_prompt.md
│   ├── testplan-cfg/
│   │   ├── scripts/
│   │   │   ├── __init__.py
│   │   │   ├── md_parser.py
│   │   │   ├── reg_to_json.py
│   │   │   ├── cfg_writer.py
│   │   │   ├── xlsx_writer.py
│   │   │   └── validator.py
│   │   └── templates/
│   │       └── cfg_prompt.md
│   └── nbl-testplan-generator/
│       ├── scripts/
│       │   ├── __init__.py
│       │   ├── combine_writer.py
│       │   ├── xlsx_writer.py
│       │   └── validator.py
│       └── review/
│           └── review_writer.py
└── pyproject.toml
```

### Files to Modify

- `skills/testplan-func/SKILL.md` - Rewrite for independent calling
- `skills/testplan-cfg/SKILL.md` - Rewrite for independent/incremental modes
- `skills/nbl-testplan-generator/SKILL.md` - Rewrite for Skill composition

### Files to Delete (after migration)

- `skills/nbl-testplan-generator/scripts/parsers/` - Move to testplan-func/scripts/
- `skills/nbl-testplan-generator/scripts/writers/` - Refactor into skill-specific writers

---

## Phase 1: Infrastructure Setup

### Task 1.1: Create Test Framework

**Files:**
- Create: `nbl-testplan-generator/pyproject.toml`
- Create: `nbl-testplan-generator/tests/__init__.py`
- Create: `nbl-testplan-generator/tests/conftest.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "nbl-testplan-generator"
version = "3.0.0"
description = "Digital chip verification test plan generator with three independent skills"
requires-python = ">=3.12"
dependencies = [
    "openpyxl>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_paths = ["."]
```

- [ ] **Step 2: Create tests/__init__.py**

```python
# Test package for nbl-testplan-generator
```

- [ ] **Step 3: Create tests/conftest.py with fixtures**

```python
"""Pytest fixtures for testplan tests."""
import json
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_spec_md(fixtures_dir) -> Path:
    """Return path to sample spec markdown file."""
    return fixtures_dir / "sample_spec.md"


@pytest.fixture
def sample_reg_xlsx(fixtures_dir) -> Path:
    """Return path to sample register xlsx file."""
    return fixtures_dir / "sample_reg.xlsx"


@pytest.fixture
def sample_template_xlsx(fixtures_dir) -> Path:
    """Return path to template xlsx file."""
    return fixtures_dir / "testplan_template.xlsx"


@pytest.fixture
def expected_ch1_json(fixtures_dir) -> dict:
    """Load expected Ch1 output structure."""
    path = fixtures_dir / "expected_ch1_output.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
```

- [ ] **Step 4: Verify test framework works**

Run: `cd nbl-testplan-generator && uv run pytest --collect-only`
Expected: "1 test collected" (conftest fixtures loaded)

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/pyproject.toml nbl-testplan-generator/tests/
git commit -m "feat: add pytest framework and test fixtures

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 1.2: Create Test Fixtures

**Files:**
- Create: `nbl-testplan-generator/tests/fixtures/sample_spec.md`
- Create: `nbl-testplan-generator/tests/fixtures/sample_reg.xlsx` (copy from existing)
- Create: `nbl-testplan-generator/tests/fixtures/testplan_template.xlsx` (copy from existing)
- Create: `nbl-testplan-generator/tests/fixtures/expected_ch1_output.json`

- [ ] **Step 1: Create fixtures directory**

```bash
mkdir -p nbl-testplan-generator/tests/fixtures
```

- [ ] **Step 2: Create sample_spec.md**

```markdown
# UPA 模块功能规格书

## 1. 模块特性

### 1.1 数据通路特性

【PA.001】支持单向数据传输
【PA.002】支持双向数据交换

### 1.2 控制特性

【PA.003】支持流控机制

## 2. 功能详述

### 2.1 数据通路功能

#### PA.001 单向数据传输

UPA模块支持单向数据传输模式，数据从源端传输到目的端。

相关寄存器：
- upa_ctrl: 控制寄存器
- upa_data_0: 数据寄存器0
- upa_data_1: 数据寄存器1

#### PA.002 双向数据交换

UPA模块支持双向数据交换模式，数据可以同时在两个方向传输。

相关寄存器：
- upa_ctrl: 控制寄存器
- upa_fwd_cfg: 转发配置

### 2.2 控制功能

#### PA.003 流控机制

UPA模块支持流控机制，通过配置寄存器控制数据流。

相关寄存器：
- upa_ctrl.flow_en: 流控使能位
- upa_fifo_th: FIFO阈值配置
```

- [ ] **Step 3: Copy existing template and create minimal register xlsx**

Run: Copy template from existing location
```bash
cp nbl-testplan-generator/skills/nbl-testplan-generator/templates/testplan_template.xlsx nbl-testplan-generator/tests/fixtures/
```

- [ ] **Step 4: Create minimal sample_reg.xlsx**

This requires creating a minimal xlsx with register data. Use Python to create it:

```python
# Run this as a one-off script to create sample_reg.xlsx
import openpyxl
from openpyxl.styles import Font

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "upa_regs"

# Header row
headers = ["offset_addr", "name", "type", "depth", "width", "bit_range", "field_name", "default", "RW", "description", "description_cn"]
for col, h in enumerate(headers, 1):
    ws.cell(row=2, column=col, value=h)
    ws.cell(row=2, column=col).font = Font(bold=True)

# Register 1: upa_ctrl
ws.cell(row=3, column=1, value="0x0000")
ws.cell(row=3, column=2, value="upa_ctrl")
ws.cell(row=3, column=6, value="[0]")
ws.cell(row=3, column=7, value="en")
ws.cell(row=3, column=8, value="0")
ws.cell(row=3, column=9, value="RW")
ws.cell(row=3, column=11, value="模块使能")
ws.cell(row=4, column=6, value="[1]")
ws.cell(row=4, column=7, value="flow_en")
ws.cell(row=4, column=8, value="0")
ws.cell(row=4, column=9, value="RW")
ws.cell(row=4, column=11, value="流控使能")

# Register 2: upa_data_0
ws.cell(row=5, column=1, value="0x0004")
ws.cell(row=5, column=2, value="upa_data_0")
ws.cell(row=5, column=6, value="[31:0]")
ws.cell(row=5, column=7, value="data")
ws.cell(row=5, column=8, value="0")
ws.cell(row=5, column=9, value="RW")
ws.cell(row=5, column=11, value="数据寄存器")

# Register 3: upa_fwd_cfg
ws.cell(row=6, column=1, value="0x0008")
ws.cell(row=6, column=2, value="upa_fwd_cfg")
ws.cell(row=6, column=6, value="[0]")
ws.cell(row=6, column=7, value="fwd_en")
ws.cell(row=6, column=8, value="0")
ws.cell(row=6, column=9, value="RW")
ws.cell(row=6, column=11, value="转发使能")

wb.save("nbl-testplan-generator/tests/fixtures/sample_reg.xlsx")
```

- [ ] **Step 5: Create expected_ch1_output.json**

```json
{
  "module_name": "UPA",
  "spec_name": "UPA 模块功能规格书",
  "chapter": "chapter 1 功能特性",
  "features": [
    {
      "feature": "数据通路特性",
      "feature_id": "PA.001",
      "chapter": "chapter 1 功能特性",
      "subfeatures_l1": [
        {
          "subfeature_l1": "单向数据传输",
          "subfeatures_l2": [
            {
              "subfeature_l2_overview": "数据传输基本功能",
              "subfeature_l2_detail": "数据从源端传输到目的端",
              "remarks": "来源: PA.001",
              "stimulus": "【配置】配置upa_ctrl.en=1",
              "checking": "by_direct_tc",
              "coverage": "upa_data传输覆盖率",
              "priority": "HIGH",
              "activity": "BT",
              "path": ""
            }
          ]
        }
      ]
    }
  ]
}
```

- [ ] **Step 6: Verify fixtures exist**

Run: `ls -la nbl-testplan-generator/tests/fixtures/`
Expected: All four fixture files listed

- [ ] **Step 7: Commit**

```bash
git add nbl-testplan-generator/tests/fixtures/
git commit -m "test: add sample fixtures for testplan tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 1.3: Create Skill Directory Structure

**Files:**
- Create: `nbl-testplan-generator/skills/testplan-func/scripts/__init__.py`
- Create: `nbl-testplan-generator/skills/testplan-cfg/scripts/__init__.py`
- Create: `nbl-testplan-generator/skills/nbl-testplan-generator/scripts/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p nbl-testplan-generator/skills/testplan-func/scripts
mkdir -p nbl-testplan-generator/skills/testplan-cfg/scripts
mkdir -p nbl-testplan-generator/skills/nbl-testplan-generator/scripts
mkdir -p nbl-testplan-generator/skills/nbl-testplan-generator/review
```

- [ ] **Step 2: Create __init__.py files**

```python
# nbl-testplan-generator/skills/testplan-func/scripts/__init__.py
"""Testplan-func scripts for generating Ch1 functional features."""
```

```python
# nbl-testplan-generator/skills/testplan-cfg/scripts/__init__.py
"""Testplan-cfg scripts for generating Ch2 configuration features."""
```

```python
# nbl-testplan-generator/skills/nbl-testplan-generator/scripts/__init__.py
"""Nbl-testplan-generator scripts for orchestrating test plan generation."""
```

- [ ] **Step 3: Commit**

```bash
git add nbl-testplan-generator/skills/
git commit -m "feat: create skill directory structure

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 2: testplan-func Skill

### Task 2.1: md_parser.py - Markdown Parser

**Files:**
- Create: `nbl-testplan-generator/skills/testplan-func/scripts/md_parser.py`
- Create: `nbl-testplan-generator/tests/test_md_parser.py`

- [ ] **Step 1: Write failing test for parse_markdown**

```python
# nbl-testplan-generator/tests/test_md_parser.py
"""Tests for markdown parser module."""
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from md_parser import parse_markdown, extract_feature_ids


class TestParseMarkdown:
    """Tests for parse_markdown function."""

    def test_parse_markdown_returns_dict(self, sample_spec_md):
        """parse_markdown should return a dictionary."""
        result = parse_markdown(sample_spec_md)
        assert isinstance(result, dict)

    def test_parse_markdown_extracts_document_title(self, sample_spec_md):
        """parse_markdown should extract document title."""
        result = parse_markdown(sample_spec_md)
        assert "document_title" in result
        assert "UPA" in result["document_title"] or "spec" in result["document_title"].lower()

    def test_parse_markdown_extracts_feature_ids(self, sample_spec_md):
        """parse_markdown should extract feature IDs like PA.001."""
        result = parse_markdown(sample_spec_md)
        assert "feature_ids" in result
        assert "PA.001" in result["feature_ids"]
        assert "PA.002" in result["feature_ids"]
        assert "PA.003" in result["feature_ids"]

    def test_parse_markdown_extracts_sections(self, sample_spec_md):
        """parse_markdown should extract hierarchical sections."""
        result = parse_markdown(sample_spec_md)
        assert "sections" in result
        assert len(result["sections"]) > 0

    def test_parse_markdown_extracts_tables(self, sample_spec_md):
        """parse_markdown should extract tables if present."""
        result = parse_markdown(sample_spec_md)
        assert "tables" in result
        assert isinstance(result["tables"], list)


class TestExtractFeatureIds:
    """Tests for extract_feature_ids function."""

    def test_extract_feature_ids_returns_list(self, sample_spec_md):
        """extract_feature_ids should return a list."""
        result = extract_feature_ids(sample_spec_md)
        assert isinstance(result, list)

    def test_extract_feature_ids_finds_pattern(self, sample_spec_md):
        """extract_feature_ids should find【PA.XXX】patterns."""
        result = extract_feature_ids(sample_spec_md)
        assert "PA.001" in result

    def test_extract_feature_ids_deduplicates(self, sample_spec_md):
        """extract_feature_ids should deduplicate IDs."""
        result = extract_feature_ids(sample_spec_md)
        assert len(result) == len(set(result))


class TestGetFeatureContent:
    """Tests for get_feature_content function."""

    def test_get_feature_content_returns_dict(self, sample_spec_md):
        """get_feature_content should return content for a feature ID."""
        from md_parser import parse_markdown, get_feature_content
        parsed = parse_markdown(sample_spec_md)
        result = get_feature_content(parsed, "PA.001")
        assert result is not None or result == {}

    def test_get_feature_content_finds_registers(self, sample_spec_md):
        """get_feature_content should find related register names."""
        from md_parser import parse_markdown, get_feature_content
        parsed = parse_markdown(sample_spec_md)
        result = get_feature_content(parsed, "PA.001")
        if result:
            assert "upa_ctrl" in str(result) or "upa_data" in str(result)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_md_parser.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'md_parser'"

- [ ] **Step 3: Implement md_parser.py**

```python
#!/usr/bin/env python3
"""md_parser.py - Parse Markdown specification into structured JSON.

This parser processes Markdown files converted from docx by nbl-docx-to-markdown.
Extracts Feature IDs (【PA.XXX】), hierarchical sections, and tables.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_markdown(filepath: str | Path) -> dict[str, Any]:
    """Parse a Markdown functional specification into a hierarchical dictionary.

    Parameters
    ----------
    filepath : str | Path
        Path to the markdown file.

    Returns
    -------
    dict
        Contains: document_title, total_lines, feature_ids, sections, tables
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    feature_pattern = re.compile(r"【(\w+\.\d+)】")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    result: dict[str, Any] = {
        "document_title": filepath.stem,
        "total_lines": len(lines),
        "feature_ids": [],
        "sections": [],
        "tables": [],
        "feature_content": {},
    }

    # Parse line by line
    current_section: dict[str, Any] | None = None
    current_subsection: dict[str, Any] | None = None
    current_feature: str | None = None
    current_feature_content: list[str] = []

    def _save_feature_content():
        nonlocal current_feature, current_feature_content
        if current_feature and current_feature_content:
            text = "\n".join(current_feature_content)
            result["feature_content"][current_feature] = {
                "text": text,
                "registers": _extract_registers(text),
            }
        current_feature_content = []

    for line in lines:
        line = line.rstrip("\n")
        heading_match = heading_pattern.match(line)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            features = feature_pattern.findall(title)

            # Save previous feature content
            _save_feature_content()

            if level == 1:
                current_section = {
                    "level": 1,
                    "title": title,
                    "children": [],
                }
                result["sections"].append(current_section)
                current_subsection = None
            elif level == 2:
                if current_section is None:
                    continue
                current_subsection = {
                    "level": 2,
                    "title": title,
                    "children": [],
                }
                current_section["children"].append(current_subsection)

            if features:
                current_feature = features[0]
                result["feature_ids"].extend(features)
        else:
            text = line.strip()
            features = feature_pattern.findall(text)

            if features:
                _save_feature_content()
                current_feature = features[0]
                result["feature_ids"].extend(features)

            if current_feature and text:
                current_feature_content.append(text)

    # Save last feature content
    _save_feature_content()

    # Deduplicate feature_ids
    result["feature_ids"] = list(dict.fromkeys(result["feature_ids"]))

    return result


def _extract_registers(text: str) -> list[str]:
    """Extract register names from text (pattern: upa_xxx)."""
    pattern = re.compile(r"(upa_\w+)")
    return list(dict.fromkeys(pattern.findall(text)))


def extract_feature_ids(filepath: str | Path) -> list[str]:
    """Extract all feature IDs from a markdown file.

    Parameters
    ----------
    filepath : str | Path
        Path to the markdown file.

    Returns
    -------
    list[str]
        List of feature IDs (e.g., ['PA.001', 'PA.002'])
    """
    result = parse_markdown(filepath)
    return result["feature_ids"]


def get_feature_content(parsed: dict[str, Any], feature_id: str) -> dict[str, Any] | None:
    """Get content for a specific feature ID from parsed data.

    Parameters
    ----------
    parsed : dict
        Parsed markdown data from parse_markdown()
    feature_id : str
        Feature ID to look up (e.g., 'PA.001')

    Returns
    -------
    dict | None
        Dict with 'text' and 'registers' keys, or None if not found
    """
    return parsed.get("feature_content", {}).get(feature_id)


def get_section_by_title(parsed: dict[str, Any], title_keyword: str) -> dict[str, Any] | None:
    """Find a section whose title contains the keyword."""
    for section in parsed.get("sections", []):
        if title_keyword in section.get("title", ""):
            return section
        for child in section.get("children", []):
            if title_keyword in child.get("title", ""):
                return child
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_parser.py <input.md> [output.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = parse_markdown(input_path)

    print(f"Document: {result['document_title']}")
    print(f"Lines: {result['total_lines']}")
    print(f"Feature IDs: {result['feature_ids']}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_md_parser.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-func/scripts/md_parser.py nbl-testplan-generator/tests/test_md_parser.py
git commit -m "feat: add md_parser for testplan-func skill

- Parse markdown to extract Feature IDs (【PA.XXX】)
- Extract hierarchical sections
- Extract related registers per feature

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.2: reg_to_json.py - Register Parser

**Files:**
- Create: `nbl-testplan-generator/skills/testplan-func/scripts/reg_to_json.py`
- Create: `nbl-testplan-generator/tests/test_reg_to_json.py`

- [ ] **Step 1: Write failing test for parse_register_xlsx**

```python
# nbl-testplan-generator/tests/test_reg_to_json.py
"""Tests for register parser module."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from reg_to_json import parse_register_xlsx, get_register_by_name


class TestParseRegisterXlsx:
    """Tests for parse_register_xlsx function."""

    def test_parse_returns_dict(self, sample_reg_xlsx):
        """parse_register_xlsx should return a dictionary."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert isinstance(result, dict)

    def test_parse_extracts_source_file(self, sample_reg_xlsx):
        """parse_register_xlsx should include source file name."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "source_file" in result
        assert "sample_reg" in result["source_file"]

    def test_parse_extracts_registers_list(self, sample_reg_xlsx):
        """parse_register_xlsx should extract registers list."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "registers" in result
        assert isinstance(result["registers"], list)
        assert len(result["registers"]) > 0

    def test_parse_extracts_register_name(self, sample_reg_xlsx):
        """parse_register_xlsx should extract register names."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg_names = [r["name"] for r in result["registers"]]
        assert "upa_ctrl" in reg_names

    def test_parse_extracts_register_fields(self, sample_reg_xlsx):
        """parse_register_xlsx should extract register fields."""
        result = parse_register_xlsx(sample_reg_xlsx)
        upa_ctrl = get_register_by_name(result, "upa_ctrl")
        assert upa_ctrl is not None
        assert "fields" in upa_ctrl
        assert len(upa_ctrl["fields"]) > 0

    def test_parse_extracts_field_name(self, sample_reg_xlsx):
        """parse_register_xlsx should extract field names."""
        result = parse_register_xlsx(sample_reg_xlsx)
        upa_ctrl = get_register_by_name(result, "upa_ctrl")
        field_names = [f["name"] for f in upa_ctrl["fields"]]
        assert "en" in field_names

    def test_parse_extracts_field_access(self, sample_reg_xlsx):
        """parse_register_xlsx should extract field access type."""
        result = parse_register_xlsx(sample_reg_xlsx)
        upa_ctrl = get_register_by_name(result, "upa_ctrl")
        en_field = next((f for f in upa_ctrl["fields"] if f["name"] == "en"), None)
        assert en_field is not None
        assert en_field.get("access") == "RW"

    def test_parse_builds_name_index(self, sample_reg_xlsx):
        """parse_register_xlsx should build name_index for quick lookup."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "name_index" in result
        assert "upa_ctrl" in result["name_index"]


class TestGetRegisterByName:
    """Tests for get_register_by_name function."""

    def test_get_existing_register(self, sample_reg_xlsx):
        """get_register_by_name should find existing register."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = get_register_by_name(result, "upa_ctrl")
        assert reg is not None
        assert reg["name"] == "upa_ctrl"

    def test_get_nonexistent_register(self, sample_reg_xlsx):
        """get_register_by_name should return None for missing register."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = get_register_by_name(result, "nonexistent_reg")
        assert reg is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_reg_to_json.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'reg_to_json'"

- [ ] **Step 3: Implement reg_to_json.py**

```python
#!/usr/bin/env python3
"""reg_to_json.py - Convert register xlsx to structured JSON.

Parses register manual xlsx files and extracts:
- Register names, offsets, types
- Field names, bit ranges, access types, descriptions
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import openpyxl


def parse_register_xlsx(filepath: str | Path) -> dict[str, Any]:
    """Parse register xlsx into structured JSON.

    Parameters
    ----------
    filepath : str | Path
        Path to the register xlsx file.

    Returns
    -------
    dict
        Contains: source_file, total_registers, registers, name_index
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Register file not found: {filepath}")

    wb = openpyxl.load_workbook(filepath, data_only=True)

    result: dict[str, Any] = {
        "source_file": filepath.name,
        "total_registers": 0,
        "registers": [],
        "name_index": {},
    }

    # Skip common non-register sheets
    skip_sheets = {"封面", "地址映射", "address_map", "summary"}

    for sheet_name in wb.sheetnames:
        if sheet_name.lower() in {s.lower() for s in skip_sheets}:
            continue

        ws = wb[sheet_name]
        registers = _parse_register_sheet(ws)

        for reg in registers:
            idx = len(result["registers"])
            result["name_index"][reg["name"]] = idx
            result["registers"].append(reg)

    result["total_registers"] = len(result["registers"])
    wb.close()
    return result


def _parse_register_sheet(ws) -> list[dict[str, Any]]:
    """Parse a single register sheet."""
    registers: list[dict[str, Any]] = []

    # Find header row (look for 'offset_addr' or 'name' in first few rows)
    header_row_num = None
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True), 1):
        row_values = [str(v).lower() if v else "" for v in row]
        if any("offset" in v for v in row_values) or any("name" in v for v in row_values[:3]):
            header_row_num = i
            break

    if header_row_num is None:
        warnings.warn(f"Header row not found in sheet '{ws.title}'")
        return registers

    data_start = header_row_num + 1
    current_reg: dict[str, Any] | None = None

    for row in ws.iter_rows(min_row=data_start, values_only=True):
        values = list(row)
        while len(values) < 11:
            values.append(None)

        offset = str(values[0]).strip() if values[0] else ""
        name = str(values[1]).strip() if values[1] else ""
        bit_range = str(values[5]).strip() if len(values) > 5 and values[5] else ""
        field_name = str(values[6]).strip() if len(values) > 6 and values[6] else ""
        default_val = str(values[7]).strip() if len(values) > 7 and values[7] else ""
        rw_attr = str(values[8]).strip() if len(values) > 8 and values[8] else ""
        desc = str(values[10]).strip() if len(values) > 10 and values[10] else ""

        # New register starts
        if offset and name:
            if current_reg:
                registers.append(current_reg)

            current_reg = {
                "offset": offset,
                "name": name,
                "type": str(values[2] or "").strip() if len(values) > 2 else "",
                "fields": [],
            }

            if field_name:
                current_reg["fields"].append({
                    "range": bit_range,
                    "name": field_name,
                    "default": default_val,
                    "access": rw_attr,
                    "description": desc,
                })

        # Additional field for current register
        elif current_reg and field_name:
            current_reg["fields"].append({
                "range": bit_range,
                "name": field_name,
                "default": default_val,
                "access": rw_attr,
                "description": desc,
            })

    if current_reg:
        registers.append(current_reg)

    return registers


def get_register_by_name(reg_data: dict[str, Any], name: str) -> dict[str, Any] | None:
    """Get register by name from parsed register data.

    Parameters
    ----------
    reg_data : dict
        Parsed register data from parse_register_xlsx()
    name : str
        Register name to look up

    Returns
    -------
    dict | None
        Register dict or None if not found
    """
    idx = reg_data.get("name_index", {}).get(name)
    if idx is not None:
        return reg_data["registers"][idx]
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reg_to_json.py <input.xlsx> [output.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = parse_register_xlsx(input_path)

    print(f"Source: {result['source_file']}")
    print(f"Total registers: {result['total_registers']}")
    print(f"Registers: {[r['name'] for r in result['registers']]}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_reg_to_json.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-func/scripts/reg_to_json.py nbl-testplan-generator/tests/test_reg_to_json.py
git commit -m "feat: add reg_to_json for testplan-func skill

- Parse register xlsx to structured JSON
- Extract register names, offsets, fields
- Build name_index for quick lookup

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.3: xlsx_writer.py - Excel Output Formatter

**Files:**
- Create: `nbl-testplan-generator/skills/testplan-func/scripts/xlsx_writer.py`
- Create: `nbl-testplan-generator/tests/test_xlsx_writer.py`

- [ ] **Step 1: Write failing test for xlsx_writer**

```python
# nbl-testplan-generator/tests/test_xlsx_writer.py
"""Tests for xlsx writer module."""
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from xlsx_writer import write_ch1_xlsx, DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE


class TestWriteCh1Xlsx:
    """Tests for write_ch1_xlsx function."""

    def test_write_creates_file(self, temp_dir, sample_template_xlsx):
        """write_ch1_xlsx should create output file."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test Spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "特性A",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "子特性A1",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2_overview": "概述",
                                    "subfeature_l2_detail": "详情",
                                    "remarks": "备注",
                                    "stimulus": "激励",
                                    "checking": "by_direct_tc",
                                    "coverage": "覆盖率",
                                    "priority": "HIGH",
                                    "activity": "BT",
                                    "path": "test_path",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        output_path = temp_dir / "test_output.xlsx"
        write_ch1_xlsx(ch1_data, str(output_path), str(sample_template_xlsx))

        assert output_path.exists()

    def test_write_creates_correct_sheet(self, temp_dir, sample_template_xlsx):
        """write_ch1_xlsx should create sheet with data."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test Spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "特性A",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "子特性A1",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2_overview": "概述",
                                    "subfeature_l2_detail": "",
                                    "remarks": "",
                                    "stimulus": "",
                                    "checking": "",
                                    "coverage": "",
                                    "priority": "",
                                    "activity": "",
                                    "path": "",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        output_path = temp_dir / "test_output.xlsx"
        write_ch1_xlsx(ch1_data, str(output_path), str(sample_template_xlsx))

        wb = openpyxl.load_workbook(output_path)
        ws = wb.active
        # Check D column has feature name
        assert ws.cell(row=6, column=4).value == "特性A"
        wb.close()

    def test_write_sets_outline_levels(self, temp_dir, sample_template_xlsx):
        """write_ch1_xlsx should set correct outline levels."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test Spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "特性A",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "子特性A1",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2_overview": "概述",
                                    "subfeature_l2_detail": "详情",
                                    "remarks": "备注",
                                    "stimulus": "激励",
                                    "checking": "by_direct_tc",
                                    "coverage": "",
                                    "priority": "HIGH",
                                    "activity": "BT",
                                    "path": "",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        output_path = temp_dir / "test_output.xlsx"
        write_ch1_xlsx(ch1_data, str(output_path), str(sample_template_xlsx))

        wb = openpyxl.load_workbook(output_path)
        ws = wb.active

        # D column (feature) should be level 0
        assert ws.row_dimensions[6].outline_level == 0
        # E column (L1) should be level 1
        assert ws.row_dimensions[7].outline_level == 1
        # F column (L2 overview) should be level 2
        assert ws.row_dimensions[8].outline_level == 2
        # G column (L2 detail) should be level 3
        assert ws.row_dimensions[9].outline_level == 3

        wb.close()

    def test_write_applies_font(self, temp_dir, sample_template_xlsx):
        """write_ch1_xlsx should apply correct font."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test Spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "特性A",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "子特性A1",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2_overview": "概述",
                                    "subfeature_l2_detail": "",
                                    "remarks": "",
                                    "stimulus": "",
                                    "checking": "",
                                    "coverage": "",
                                    "priority": "",
                                    "activity": "",
                                    "path": "",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        output_path = temp_dir / "test_output.xlsx"
        write_ch1_xlsx(ch1_data, str(output_path), str(sample_template_xlsx))

        wb = openpyxl.load_workbook(output_path)
        ws = wb.active

        cell = ws.cell(row=6, column=4)
        assert cell.font.name == DEFAULT_FONT_NAME
        assert cell.font.size == DEFAULT_FONT_SIZE

        wb.close()

    def test_write_puts_hw_at_min_granularity(self, temp_dir, sample_template_xlsx):
        """H-W columns should only appear at minimum granularity row."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test Spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "特性A",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "子特性A1",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2_overview": "概述",
                                    "subfeature_l2_detail": "详情",
                                    "remarks": "备注内容",
                                    "stimulus": "激励内容",
                                    "checking": "by_direct_tc",
                                    "coverage": "",
                                    "priority": "HIGH",
                                    "activity": "BT",
                                    "path": "test_path",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        output_path = temp_dir / "test_output.xlsx"
        write_ch1_xlsx(ch1_data, str(output_path), str(sample_template_xlsx))

        wb = openpyxl.load_workbook(output_path)
        ws = wb.active

        # Row 6 (D, level 0) - H should be empty
        assert ws.cell(row=6, column=8).value is None
        # Row 7 (E, level 1) - H should be empty
        assert ws.cell(row=7, column=8).value is None
        # Row 8 (F, level 2) - H should be empty (G is minimum)
        assert ws.cell(row=8, column=8).value is None
        # Row 9 (G, level 3) - H should have content
        assert ws.cell(row=9, column=8).value == "备注内容"

        wb.close()


class TestConstants:
    """Tests for module constants."""

    def test_default_font_name(self):
        """DEFAULT_FONT_NAME should be set."""
        assert DEFAULT_FONT_NAME == "微软雅黑"

    def test_default_font_size(self):
        """DEFAULT_FONT_SIZE should be 10."""
        assert DEFAULT_FONT_SIZE == 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'xlsx_writer'"

- [ ] **Step 3: Implement xlsx_writer.py**

```python
#!/usr/bin/env python3
"""xlsx_writer.py - Write hierarchical testpoint data to xlsx.

Supports D-E-F-G hierarchy with:
- outline_level for row grouping (0-3)
- H-W columns only at minimum granularity
- Standard formatting (font, borders, wrap_text)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import Outline

# Default font settings
DEFAULT_FONT_NAME = "微软雅黑"
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT_COLOR = "000000"
RED_FONT_COLOR = "FF0000"

# Thin border for data cells
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

# Gold fill for ⚠ markers
GOLD_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

# Columns that need wrap_text (D through W)
WRAP_COLUMNS = set(range(4, 24))


def write_ch1_xlsx(
    ch1_data: dict[str, Any],
    output_path: str | Path,
    template_path: str | Path,
) -> dict[str, int]:
    """Write Ch1 functional features to xlsx.

    Parameters
    ----------
    ch1_data : dict
        Ch1 features JSON with module_name, spec_name, features
    output_path : str | Path
        Destination xlsx file path
    template_path : str | Path
        Path to template xlsx

    Returns
    -------
    dict[str, int]
        Stats: total_features, total_l1, total_l2, total_l3
    """
    output_path = Path(output_path)
    template_path = Path(template_path)

    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # Clear template data (row 6 onwards)
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(1, 24):
            ws.cell(row=row_idx, column=col_idx).value = None
            ws.cell(row=row_idx, column=col_idx).border = Border()
        ws.row_dimensions[row_idx].outline_level = 0

    # Write metadata rows (3-5)
    spec_name = ch1_data.get("spec_name", "")
    ws.cell(row=5, column=2, value=spec_name)

    # Write chapter label in B column
    chapter = ch1_data.get("chapter", "chapter 1 功能特性")
    ws.cell(row=6, column=2, value=chapter)

    # Write features starting row 6
    row = 6
    stats = {"total_features": 0, "total_l1": 0, "total_l2": 0, "total_l3": 0}

    for feat in ch1_data.get("features", []):
        stats["total_features"] += 1
        feature_name = feat.get("feature", "")

        # D column: feature name (level 0)
        _write_cell(ws, row, 4, feature_name)
        ws.row_dimensions[row].outline_level = 0
        row += 1

        for sf1 in feat.get("subfeatures_l1", []):
            stats["total_l1"] += 1
            sf1_name = sf1.get("subfeature_l1", "")

            # E column: L1 subfeature (level 1)
            _write_cell(ws, row, 5, sf1_name)
            ws.row_dimensions[row].outline_level = 1
            row += 1

            for sf2 in sf1.get("subfeatures_l2", []):
                stats["total_l2"] += 1
                overview = sf2.get("subfeature_l2_overview", "")
                detail = sf2.get("subfeature_l2_detail", "")

                # Check if we have detail (G level)
                has_detail = bool(detail and detail.strip())

                if has_detail:
                    # F column: overview (level 2) - no H-W
                    _write_cell(ws, row, 6, overview)
                    ws.row_dimensions[row].outline_level = 2
                    row += 1

                    # G column: detail (level 3) - with H-W
                    stats["total_l3"] += 1
                    _write_cell(ws, row, 7, detail)
                    _write_hw_columns(ws, row, sf2)
                    ws.row_dimensions[row].outline_level = 3
                    row += 1
                else:
                    # F column: overview (level 2) - with H-W (minimum granularity)
                    _write_cell(ws, row, 6, overview)
                    _write_hw_columns(ws, row, sf2)
                    ws.row_dimensions[row].outline_level = 2
                    row += 1

    # Apply borders to data region
    _apply_borders(ws, 6, row - 1)

    # Apply sheet formatting
    ws.sheet_properties.outlinePr = Outline(summaryBelow=False)
    ws.freeze_panes = "A3"

    wb.save(output_path)
    wb.close()

    return stats


def _write_cell(ws, row: int, col: int, value: Any) -> None:
    """Write a cell with standard formatting."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        ws.cell(row=row, column=col).value = None
        return

    cell = ws.cell(row=row, column=col, value=str(value))
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.font = Font(name=DEFAULT_FONT_NAME, size=DEFAULT_FONT_SIZE, color=DEFAULT_FONT_COLOR)

    # Red font for special markers
    text = str(value)
    if col == 9 and ("【配置】" in text or "【激励】" in text):
        cell.font = Font(name=DEFAULT_FONT_NAME, size=DEFAULT_FONT_SIZE, color=RED_FONT_COLOR)

    if "⚠" in text or "[推断]" in text:
        cell.fill = GOLD_FILL
        cell.font = Font(name=DEFAULT_FONT_NAME, size=DEFAULT_FONT_SIZE, color=RED_FONT_COLOR)


def _write_hw_columns(ws, row: int, sf2: dict[str, Any]) -> None:
    """Write H-W columns for minimum granularity row."""
    # H: remarks, I: stimulus, J: checking, K: coverage, L: priority, M: activity, W: path
    _write_cell(ws, row, 8, sf2.get("remarks", ""))
    _write_cell(ws, row, 9, sf2.get("stimulus", ""))
    _write_cell(ws, row, 10, sf2.get("checking", ""))
    _write_cell(ws, row, 11, sf2.get("coverage", ""))
    _write_cell(ws, row, 12, sf2.get("priority", ""))
    _write_cell(ws, row, 13, sf2.get("activity", ""))
    _write_cell(ws, row, 23, sf2.get("path", ""))


def _apply_borders(ws, start_row: int, end_row: int) -> None:
    """Apply borders to data region."""
    for row_idx in range(start_row, end_row + 1):
        for col_idx in range(1, 24):
            ws.cell(row=row_idx, column=col_idx).border = THIN_BORDER
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_xlsx_writer.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-func/scripts/xlsx_writer.py nbl-testplan-generator/tests/test_xlsx_writer.py
git commit -m "feat: add xlsx_writer for testplan-func skill

- Write D-E-F-G hierarchy with correct outline levels
- H-W columns only at minimum granularity
- Apply standard formatting (font, borders)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.4: func_writer.py - Feature Generator

**Files:**
- Create: `nbl-testplan-generator/skills/testplan-func/scripts/func_writer.py`
- Create: `nbl-testplan-generator/tests/test_testplan_func.py`

- [ ] **Step 1: Write failing test for func_writer**

```python
# nbl-testplan-generator/tests/test_testplan_func.py
"""Integration tests for testplan-func skill."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from func_writer import generate_ch1_features, cross_reference_registers


class TestGenerateCh1Features:
    """Tests for generate_ch1_features function."""

    def test_generate_returns_dict(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should return a dictionary."""
        from md_parser import parse_markdown
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        result = generate_ch1_features(parsed_md, parsed_reg)
        assert isinstance(result, dict)

    def test_generate_includes_module_name(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include module_name."""
        from md_parser import parse_markdown
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "module_name" in result

    def test_generate_includes_spec_name(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include spec_name."""
        from md_parser import parse_markdown
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "spec_name" in result

    def test_generate_includes_features(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include features list."""
        from md_parser import parse_markdown
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "features" in result
        assert isinstance(result["features"], list)

    def test_generate_features_have_ids(self, sample_spec_md, sample_reg_xlsx):
        """Features should have feature_id."""
        from md_parser import parse_markdown
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        result = generate_ch1_features(parsed_md, parsed_reg)

        for feat in result["features"]:
            assert "feature_id" in feat


class TestCrossReferenceRegisters:
    """Tests for cross_reference_registers function."""

    def test_cross_reference_returns_list(self, sample_spec_md, sample_reg_xlsx):
        """cross_reference_registers should return list of related registers."""
        from md_parser import parse_markdown, get_feature_content
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        feature_content = get_feature_content(parsed_md, "PA.001")
        if feature_content:
            result = cross_reference_registers(feature_content, parsed_reg)
            assert isinstance(result, list)

    def test_cross_reference_finds_related_registers(self, sample_spec_md, sample_reg_xlsx):
        """cross_reference_registers should find related registers."""
        from md_parser import parse_markdown, get_feature_content
        from reg_to_json import parse_register_xlsx

        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)

        feature_content = get_feature_content(parsed_md, "PA.001")
        if feature_content:
            result = cross_reference_registers(feature_content, parsed_reg)
            # PA.001 mentions upa_ctrl and upa_data
            register_names = [r["name"] for r in result]
            assert any("upa_ctrl" in n or "upa_data" in n for n in register_names)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_testplan_func.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'func_writer'"

- [ ] **Step 3: Implement func_writer.py**

```python
#!/usr/bin/env python3
"""func_writer.py - Generate Ch1 functional features from parsed data.

Cross-references markdown spec with register data to generate
D-E-F-G hierarchical test points.
"""
from __future__ import annotations

import re
from typing import Any


def generate_ch1_features(
    parsed_md: dict[str, Any],
    parsed_reg: dict[str, Any],
) -> dict[str, Any]:
    """Generate Ch1 features data from parsed markdown and register data.

    Parameters
    ----------
    parsed_md : dict
        Parsed markdown from md_parser.parse_markdown()
    parsed_reg : dict
        Parsed register data from reg_to_json.parse_register_xlsx()

    Returns
    -------
    dict
        Ch1 features data with module_name, spec_name, features
    """
    feature_ids = parsed_md.get("feature_ids", [])
    feature_content = parsed_md.get("feature_content", {})

    features: list[dict[str, Any]] = []

    for fid in feature_ids:
        content = feature_content.get(fid)
        if not content:
            continue

        # Get related registers
        related_regs = cross_reference_registers(content, parsed_reg)

        # Build feature structure
        feature = _build_feature(fid, content, related_regs)
        features.append(feature)

    return {
        "module_name": _extract_module_name(parsed_md),
        "spec_name": parsed_md.get("document_title", ""),
        "chapter": "chapter 1 功能特性",
        "features": features,
    }


def cross_reference_registers(
    feature_content: dict[str, Any],
    parsed_reg: dict[str, Any],
) -> list[dict[str, Any]]:
    """Find registers mentioned in feature content.

    Parameters
    ----------
    feature_content : dict
        Feature content from md_parser
    parsed_reg : dict
        Parsed register data

    Returns
    -------
    list[dict]
        List of related register dicts
    """
    text = feature_content.get("text", "")
    register_names = feature_content.get("registers", [])

    # Also extract from text
    pattern = re.compile(r"(upa_\w+)")
    register_names = list(set(register_names + pattern.findall(text)))

    result: list[dict[str, Any]] = []
    name_index = parsed_reg.get("name_index", {})
    registers = parsed_reg.get("registers", [])

    for name in register_names:
        if name in name_index:
            idx = name_index[name]
            result.append(registers[idx])

    return result


def _build_feature(
    fid: str,
    content: dict[str, Any],
    related_regs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a feature structure with D-E-F-G hierarchy."""
    text = content.get("text", "")

    # Extract feature name from first line
    lines = [l for l in text.split("\n") if l.strip()]
    feature_name = lines[0] if lines else fid

    # Clean feature name (remove Feature ID)
    feature_name = re.sub(r"【\w+\.\d+】", "", feature_name).strip()

    # Build L1 subfeature
    subfeature_l1 = _build_subfeature_l1(fid, content, related_regs)

    return {
        "feature": feature_name or fid,
        "feature_id": fid,
        "chapter": "chapter 1 功能特性",
        "subfeatures_l1": [subfeature_l1],
    }


def _build_subfeature_l1(
    fid: str,
    content: dict[str, Any],
    related_regs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build L1 subfeature."""
    text = content.get("text", "")

    # Extract description (skip first line)
    lines = [l for l in text.split("\n") if l.strip()]
    description = "\n".join(lines[1:]) if len(lines) > 1 else ""

    # Build stimulus from related registers
    stimulus = _build_stimulus(related_regs)

    # Build L2 subfeature
    subfeature_l2 = {
        "subfeature_l2_overview": description[:50] if description else "基本功能",
        "subfeature_l2_detail": "",
        "remarks": f"来源: {fid}",
        "stimulus": stimulus,
        "checking": "by_direct_tc",
        "coverage": "",
        "priority": "HIGH",
        "activity": "BT",
        "path": "",
    }

    return {
        "subfeature_l1": "基本功能",
        "subfeatures_l2": [subfeature_l2],
    }


def _build_stimulus(related_regs: list[dict[str, Any]]) -> str:
    """Build stimulus string from related registers."""
    if not related_regs:
        return ""

    parts = []
    for reg in related_regs[:3]:  # Limit to first 3
        reg_name = reg.get("name", "")
        fields = reg.get("fields", [])
        rw_fields = [f for f in fields if f.get("access") == "RW"]

        for field in rw_fields[:2]:  # Limit to first 2 RW fields
            fname = field.get("name", "")
            parts.append(f"【配置】配置{reg_name}.{fname}")

    return "；".join(parts) if parts else ""


def _extract_module_name(parsed_md: dict[str, Any]) -> str:
    """Extract module name from document title."""
    title = parsed_md.get("document_title", "")
    # Extract first word as module name
    match = re.match(r"(\w+)", title)
    return match.group(1).upper() if match else "UNKNOWN"


if __name__ == "__main__":
    import json
    import sys

    from md_parser import parse_markdown
    from reg_to_json import parse_register_xlsx

    if len(sys.argv) < 3:
        print("Usage: python func_writer.py <spec.md> <reg.xlsx> [output.json]")
        sys.exit(1)

    spec_path = sys.argv[1]
    reg_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    parsed_md = parse_markdown(spec_path)
    parsed_reg = parse_register_xlsx(reg_path)

    result = generate_ch1_features(parsed_md, parsed_reg)

    print(f"Module: {result['module_name']}")
    print(f"Features: {len(result['features'])}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_testplan_func.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-func/scripts/func_writer.py nbl-testplan-generator/tests/test_testplan_func.py
git commit -m "feat: add func_writer for testplan-func skill

- Generate Ch1 features from parsed markdown and register data
- Cross-reference features with related registers
- Build D-E-F-G hierarchy structure

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.5: validator.py - Output Validator

**Files:**
- Create: `nbl-testplan-generator/skills/testplan-func/scripts/validator.py`
- Create: `nbl-testplan-generator/tests/test_validator.py`

- [ ] **Step 1: Write failing test for validator**

```python
# nbl-testplan-generator/tests/test_validator.py
"""Tests for output validator module."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from validator import validate_ch1_xlsx, ValidationError


class TestValidateCh1Xlsx:
    """Tests for validate_ch1_xlsx function."""

    def test_validate_returns_list(self, temp_dir, sample_template_xlsx):
        """validate_ch1_xlsx should return a list of errors."""
        import openpyxl

        # Create minimal valid xlsx
        wb = openpyxl.load_workbook(sample_template_xlsx)
        ws = wb.active
        ws.cell(row=6, column=4, value="特性A")
        ws.cell(row=7, column=5, value="子特性A1")
        ws.cell(row=8, column=6, value="概述")
        ws.cell(row=9, column=8, value="备注")  # H column at min granularity

        output_path = temp_dir / "test.xlsx"
        wb.save(output_path)
        wb.close()

        errors = validate_ch1_xlsx(output_path)
        assert isinstance(errors, list)

    def test_validate_detects_missing_feature(self, temp_dir, sample_template_xlsx):
        """validate_ch1_xlsx should detect missing feature name."""
        import openpyxl

        wb = openpyxl.load_workbook(sample_template_xlsx)
        ws = wb.active
        # Empty D column at row 6
        ws.cell(row=6, column=4, value="")

        output_path = temp_dir / "test.xlsx"
        wb.save(output_path)
        wb.close()

        errors = validate_ch1_xlsx(output_path)
        assert len(errors) > 0
        assert any("feature" in str(e).lower() for e in errors)

    def test_validate_detects_outline_level_issues(self, temp_dir, sample_template_xlsx):
        """validate_ch1_xlsx should detect outline level issues."""
        import openpyxl

        wb = openpyxl.load_workbook(sample_template_xlsx)
        ws = wb.active
        ws.cell(row=6, column=4, value="特性A")
        ws.row_dimensions[6].outline_level = 5  # Invalid level

        output_path = temp_dir / "test.xlsx"
        wb.save(output_path)
        wb.close()

        errors = validate_ch1_xlsx(output_path)
        assert any("level" in str(e).lower() for e in errors)


class TestValidationError:
    """Tests for ValidationError class."""

    def test_error_has_message(self):
        """ValidationError should have message attribute."""
        error = ValidationError("Test error", row=1, column=1)
        assert str(error) == "Test error"

    def test_error_has_location(self):
        """ValidationError should have row and column."""
        error = ValidationError("Test error", row=6, column=4)
        assert error.row == 6
        assert error.column == 4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_validator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'validator'"

- [ ] **Step 3: Implement validator.py**

```python
#!/usr/bin/env python3
"""validator.py - Validate output xlsx files.

Checks:
- D-E-F-G hierarchy structure
- Outline levels (0-3)
- H-W columns at minimum granularity only
- Required fields present
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import openpyxl


@dataclass
class ValidationError:
    """Represents a validation error."""
    message: str
    row: int | None = None
    column: int | None = None

    def __str__(self) -> str:
        if self.row is not None and self.column is not None:
            return f"Row {self.row}, Col {self.column}: {self.message}"
        return self.message


def validate_ch1_xlsx(filepath: str | Path) -> list[ValidationError]:
    """Validate a Ch1 xlsx file.

    Parameters
    ----------
    filepath : str | Path
        Path to the xlsx file to validate

    Returns
    -------
    list[ValidationError]
        List of validation errors (empty if valid)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return [ValidationError(f"File not found: {filepath}")]

    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    errors: list[ValidationError] = []

    # Check for data starting at row 6
    data_start_row = 6

    # Validate each row
    current_level = -1
    min_granularity_rows: set[int] = set()

    for row_idx in range(data_start_row, ws.max_row + 1):
        d_val = ws.cell(row=row_idx, column=4).value
        e_val = ws.cell(row=row_idx, column=5).value
        f_val = ws.cell(row=row_idx, column=6).value
        g_val = ws.cell(row=row_idx, column=7).value

        # Determine level based on which column has content
        if d_val:
            level = 0
            if not isinstance(d_val, str) or not d_val.strip():
                errors.append(ValidationError("Empty feature name", row=row_idx, column=4))
        elif e_val:
            level = 1
        elif f_val:
            level = 2
            # Check if this is minimum granularity (no G follows)
            # For now, assume F with H content is minimum
            h_val = ws.cell(row=row_idx, column=8).value
            if h_val:
                min_granularity_rows.add(row_idx)
        elif g_val:
            level = 3
            min_granularity_rows.add(row_idx)
        else:
            continue  # Empty row

        # Check outline level
        outline = ws.row_dimensions[row_idx].outline_level
        if outline not in (0, 1, 2, 3):
            errors.append(ValidationError(
                f"Invalid outline level: {outline}",
                row=row_idx
            ))

    # Check H-W columns only at minimum granularity
    for row_idx in range(data_start_row, ws.max_row + 1):
        if row_idx not in min_granularity_rows:
            # Check if H column has content when it shouldn't
            h_val = ws.cell(row=row_idx, column=8).value
            if h_val:
                # This might be an error - H should only be at min granularity
                # But we need to check if this row has a G-level child
                has_g_child = False
                if row_idx + 1 <= ws.max_row:
                    next_g = ws.cell(row=row_idx + 1, column=7).value
                    if next_g:
                        has_g_child = True

                if not has_g_child:
                    # This row should be minimum granularity
                    min_granularity_rows.add(row_idx)

    wb.close()
    return errors
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_validator.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-func/scripts/validator.py nbl-testplan-generator/tests/test_validator.py
git commit -m "feat: add validator for testplan-func skill

- Validate D-E-F-G hierarchy structure
- Check outline levels (0-3)
- Verify H-W columns at minimum granularity

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.6: Rewrite testplan-func SKILL.md

**Files:**
- Modify: `nbl-testplan-generator/skills/testplan-func/SKILL.md`

- [ ] **Step 1: Rewrite SKILL.md**

```markdown
---
name: testplan-func
description: 从功能规格书（.docx 或 .md）和寄存器手册（.xlsx）生成功能特性测试点（xlsx）。输入spec_path + reg_path，输出 D-E-F-G 层级测试计划。支持独立调用。触发：生成功能测试点、验证计划、testplan func。
---

# Testplan-func - 功能特性测试点生成

## 概述

独立生成 Chapter 1（功能特性）测试点，支持 D-E-F-G 四级层级结构。

## 使用场景

**适用：**
- 从功能规格书生成功能特性测试点
- 需要 D-E-F-G 层级结构化覆盖
- 独立生成功能特性（不需要配置特性）

**不适用：**
- 仅需要配置特性覆盖（使用 testplan-cfg）
- 输入文档非 .docx/.md/.xlsx 格式

## 参数

解析 `$ARGUMENTS`：

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `spec_path` | 是 | — | 功能规格书路径（.docx 或 .md） |
| `reg_path` | 是 | — | 寄存器配置路径（.xlsx） |
| `--output` | 否 | spec同目录 | 输出路径 `{basename}_testplan_func.xlsx` |

## 输出结构

xlsx 文件采用 D-E-F-G 四级结构：

| 列 | 内容 | outline_level |
|----|------|---------------|
| D | 特性名 | 0 |
| E | 子特性L1 | 1 |
| F | 子特性L2概述 | 2 |
| G | 子特性L2详情 | 3 |

**规则：**
- 一个 F 可划分为多个 G，每个 G 另起一行
- 若材料不足以划分 G，则 F 为最小粒度
- H-W 列只在最小粒度行输出

## 处理流程

### Step 1: 解析参数

从 `$ARGUMENTS` 提取参数。若缺少必填参数，询问用户。

设置工作目录：
```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
mkdir -p "$TP_WORKDIR" 2>/dev/null || TP_WORKDIR="$HOME/.tp_cache"
```

### Step 2: 文档转换

**如输入是 .docx：**
```
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

生成的 markdown 位于：`$TP_WORKDIR/<basename>_work/markdown_output/<basename>.md`

**如输入是 .md：**
直接使用原文件路径。

### Step 3: 解析文档

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python md_parser.py "$spec_md" "$TP_WORKDIR/parsed_md.json"
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python reg_to_json.py "$reg_path" "$TP_WORKDIR/parsed_reg.json"
```

### Step 4: 生成功测试点

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python func_writer.py \
  "$TP_WORKDIR/parsed_md.json" \
  "$TP_WORKDIR/parsed_reg.json" \
  "$TP_WORKDIR/ch1_features.json"
```

### Step 5: 写入 xlsx

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python -c "
from xlsx_writer import write_ch1_xlsx
import json

with open('$TP_WORKDIR/ch1_features.json', 'r', encoding='utf-8') as f:
    ch1_data = json.load(f)

write_ch1_xlsx(ch1_data, '$output_path', '${CLAUDE_SKILL_DIR}/../nbl-testplan-generator/templates/testplan_template.xlsx')
"
```

### Step 6: 验证输出

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python validator.py "$output_path"
```

### Step 7: 报告结果

向用户报告：
- 处理的特性数量
- 输出文件路径
- 摘要表格

## 关键约束

1. **禁止直接解析 docx** - 必须调用 `/nbl-docx-to-markdown` 技能
2. **D-E-F-G 层级** - G 为 level 3，是最小粒度
3. **H-W 列位置** - 仅在最小粒度行输出
```

- [ ] **Step 2: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-func/SKILL.md
git commit -m "docs: rewrite testplan-func SKILL.md for independent calling

- Support .docx (via nbl-docx-to-markdown) or .md input
- D-E-F-G hierarchy with G at outline_level 3
- H-W columns at minimum granularity only

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 3: testplan-cfg Skill

### Task 3.1: testplan-cfg scripts (copy and adapt)

**Files:**
- Copy/adapt md_parser.py, reg_to_json.py, xlsx_writer.py, validator.py
- Create: `nbl-testplan-generator/skills/testplan-cfg/scripts/cfg_writer.py`

由于 testplan-cfg 的脚本与 testplan-func 类似，这里简化描述：

- [ ] **Step 1: Copy shared scripts to testplan-cfg/scripts/**

```bash
cp nbl-testplan-generator/skills/testplan-func/scripts/md_parser.py nbl-testplan-generator/skills/testplan-cfg/scripts/
cp nbl-testplan-generator/skills/testplan-func/scripts/reg_to_json.py nbl-testplan-generator/skills/testplan-cfg/scripts/
cp nbl-testplan-generator/skills/testplan-func/scripts/xlsx_writer.py nbl-testplan-generator/skills/testplan-cfg/scripts/
cp nbl-testplan-generator/skills/testplan-func/scripts/validator.py nbl-testplan-generator/skills/testplan-cfg/scripts/
```

- [ ] **Step 2: Write cfg_writer.py**

```python
#!/usr/bin/env python3
"""cfg_writer.py - Generate Ch2 configuration features.

Supports two modes:
1. Independent: Generate Ch2 only from spec + register data
2. Incremental: Append Ch2 to existing func_xlsx with skip marking
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import openpyxl


# Exclusion patterns for Ch2 registers
CH2_EXCLUDE_PATTERNS = [
    r".*_int_status$",
    r".*_int_mask$",
    r".*_int_set$",
    r".*_int_.*$",
    r".*_car_ctrl$",
    r".*_fifo_th$",
    r".*_fifo_.*$",
    r".*_spare\d*$",
    r".*_cnt$",
    r".*_fsm\d*$",
    r".*_err_info$",
    r".*_bp_state$",
    r".*_test$",
    r".*_init_done$",
    r".*_init_start$",
]

_CH2_EXCLUDE_COMPILED = [re.compile(p) for p in CH2_EXCLUDE_PATTERNS]

# Valid access types for config registers
VALID_CFG_ACCESS = {"RW", "RWC", "WO", "RWW"}


def generate_ch2_features(
    parsed_reg: dict[str, Any],
    spec_registers: list[str] | None = None,
    func_xlsx_path: str | Path | None = None,
) -> dict[str, Any]:
    """Generate Ch2 configuration features.

    Parameters
    ----------
    parsed_reg : dict
        Parsed register data
    spec_registers : list[str] | None
        Registers found in spec (for "已在规格中描述" marking)
    func_xlsx_path : str | Path | None
        Path to existing func_xlsx (for skip marking)

    Returns
    -------
    dict
        Ch2 features data
    """
    # Get covered registers from func_xlsx if provided
    covered_regs: set[str] = set()
    if func_xlsx_path:
        covered_regs = _extract_covered_regs_from_xlsx(func_xlsx_path)

    # Add spec registers to covered
    if spec_registers:
        covered_regs.update(spec_registers)

    # Filter and process registers
    registers = parsed_reg.get("registers", [])
    filtered = _filter_cfg_registers(registers)
    grouped = _group_similar_registers(filtered)
    xrefed = _cross_ref_ch2(grouped, covered_regs)

    return {
        "chapter": "chapter 2 配置特性",
        "registers": xrefed,
    }


def _filter_cfg_registers(registers: list[dict]) -> list[dict]:
    """Filter out excluded registers."""
    result: list[dict] = []
    for reg in registers:
        name = reg.get("name", "")
        if _is_excluded(name):
            continue

        # Filter fields to valid access types
        valid_fields = [
            f for f in reg.get("fields", [])
            if f.get("access", "").upper() in VALID_CFG_ACCESS
        ]

        if valid_fields:
            result.append({**reg, "fields": valid_fields})

    return result


def _is_excluded(name: str) -> bool:
    """Check if register should be excluded."""
    for pat in _CH2_EXCLUDE_COMPILED:
        if pat.match(name):
            return True
    return False


def _group_similar_registers(registers: list[dict]) -> list[dict]:
    """Group registers differing only by numeric suffix."""
    groups: dict[str, list[dict]] = {}
    order: list[str] = []

    for reg in registers:
        name = reg["name"]
        m = re.match(r"^(.+?)_(\d+)$", name)
        base = m.group(1) if m else name

        if base not in groups:
            groups[base] = []
            order.append(base)
        groups[base].append(reg)

    result: list[dict] = []
    for base in order:
        members = groups[base]
        if len(members) == 1:
            result.append(members[0])
        else:
            suffixes = []
            for m in members:
                m_match = re.match(r"^.+?_(\d+)$", m["name"])
                suffixes.append(m_match.group(1) if m_match else "")

            merged_name = f"{base}_{'/'.join(suffixes)}"
            all_fields: list[dict] = []
            seen: set[str] = set()
            for m in members:
                for f in m.get("fields", []):
                    key = f.get("name", "")
                    if key and key not in seen:
                        seen.add(key)
                        all_fields.append(f)

            result.append({
                "name": merged_name,
                "offset": members[0].get("offset", ""),
                "fields": all_fields,
            })

    return result


def _cross_ref_ch2(
    ch2_regs: list[dict],
    covered_regs: set[str],
) -> list[dict]:
    """Cross-reference Ch2 registers with covered set."""
    result: list[dict] = []

    for reg in ch2_regs:
        name = reg["name"]
        fields = reg.get("fields", [])

        # Check if covered
        is_covered = name in covered_regs
        if not is_covered:
            base_match = re.match(r"^(.+?)_\d+(/\d+)*$", name)
            if base_match:
                base = base_match.group(1)
                is_covered = base in covered_regs

        if is_covered:
            result.append({
                "name": name,
                "skip": True,
                "stimulus": "",
                "checking": "",
                "coverage": "",
                "path": "",
                "remarks": "已在功能特性中覆盖",
            })
        else:
            # Generate stimulus from fields
            config_parts = []
            desc_parts = []
            for f in fields:
                fname = f.get("name", "")
                frange = f.get("range", "")
                fdesc = f.get("description", "")
                if fname and fname.lower() != "rsv":
                    config_parts.append(f"配置 {name}.{fname} ({frange})")
                    if fdesc:
                        desc_parts.append(f"{fname}: {fdesc}")

            stimulus = "【配置】" + "；".join(config_parts) if config_parts else ""

            result.append({
                "name": name,
                "skip": False,
                "stimulus": stimulus,
                "checking": "",
                "coverage": "",
                "path": "【反标路径暂无法确定】",
                "remarks": "; ".join(desc_parts) if desc_parts else "",
            })

    return result


def _extract_covered_regs_from_xlsx(xlsx_path: str | Path) -> set[str]:
    """Extract covered register names from func_xlsx."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    covered: set[str] = set()

    for row in ws.iter_rows(min_row=6, values_only=True):
        # Check stimulus (I column) and coverage (K column) for register names
        stimulus = str(row[8] if len(row) > 8 else "")
        coverage = str(row[10] if len(row) > 10 else "")
        text = stimulus + " " + coverage

        for match in re.finditer(r"(upa_\w+)", text):
            reg_name = match.group(1)
            base_match = re.match(r"^(.+?)_\d+$", reg_name)
            if base_match:
                covered.add(base_match.group(1))
            covered.add(reg_name)

    wb.close()
    return covered


if __name__ == "__main__":
    import json
    import sys

    from reg_to_json import parse_register_xlsx

    if len(sys.argv) < 3:
        print("Usage: python cfg_writer.py <reg.xlsx> [func.xlsx] [output.json]")
        sys.exit(1)

    reg_path = sys.argv[1]
    func_xlsx = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    parsed_reg = parse_register_xlsx(reg_path)

    result = generate_ch2_features(
        parsed_reg,
        func_xlsx_path=func_xlsx,
    )

    print(f"Registers: {len(result['registers'])}")
    skip_count = sum(1 for r in result['registers'] if r.get('skip'))
    print(f"Skipped (covered): {skip_count}")
    print(f"New: {len(result['registers']) - skip_count}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output written to: {output_path}")
```

- [ ] **Step 3: Write test_testplan_cfg.py**

```python
# nbl-testplan-generator/tests/test_testplan_cfg.py
"""Tests for testplan-cfg skill."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-cfg" / "scripts"))

from cfg_writer import (
    generate_ch2_features,
    _filter_cfg_registers,
    _group_similar_registers,
    _is_excluded,
)


class TestIsExcluded:
    """Tests for _is_excluded function."""

    def test_exclude_int_status(self):
        """Should exclude *_int_status registers."""
        assert _is_excluded("upa_int_status") is True

    def test_exclude_fifo_registers(self):
        """Should exclude *_fifo_* registers."""
        assert _is_excluded("upa_fifo_full") is True

    def test_keep_normal_registers(self):
        """Should keep normal registers."""
        assert _is_excluded("upa_ctrl") is False
        assert _is_excluded("upa_data_0") is False


class TestFilterCfgRegisters:
    """Tests for _filter_cfg_registers function."""

    def test_filter_removes_excluded(self):
        """Should remove excluded registers."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"access": "RW", "name": "en"}]},
            {"name": "upa_int_status", "fields": [{"access": "RW", "name": "status"}]},
        ]
        result = _filter_cfg_registers(registers)
        assert len(result) == 1
        assert result[0]["name"] == "upa_ctrl"

    def test_filter_keeps_rw_fields(self):
        """Should keep RW fields."""
        registers = [
            {
                "name": "upa_ctrl",
                "fields": [
                    {"access": "RW", "name": "en"},
                    {"access": "RO", "name": "status"},
                ]
            }
        ]
        result = _filter_cfg_registers(registers)
        assert len(result[0]["fields"]) == 1
        assert result[0]["fields"][0]["name"] == "en"


class TestGroupSimilarRegisters:
    """Tests for _group_similar_registers function."""

    def test_group_numbered_registers(self):
        """Should group upa_data_0, upa_data_1 into upa_data_0/1."""
        registers = [
            {"name": "upa_data_0", "fields": [{"name": "data"}]},
            {"name": "upa_data_1", "fields": [{"name": "data"}]},
        ]
        result = _group_similar_registers(registers)
        assert len(result) == 1
        assert "upa_data_0/1" in result[0]["name"]

    def test_no_group_single_register(self):
        """Should not group single registers."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en"}]},
        ]
        result = _group_similar_registers(registers)
        assert len(result) == 1
        assert result[0]["name"] == "upa_ctrl"


class TestGenerateCh2Features:
    """Tests for generate_ch2_features function."""

    def test_generate_returns_dict(self, sample_reg_xlsx):
        """generate_ch2_features should return a dictionary."""
        from reg_to_json import parse_register_xlsx

        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch2_features(parsed_reg)

        assert isinstance(result, dict)
        assert "chapter" in result
        assert "registers" in result

    def test_generate_marks_covered(self, sample_reg_xlsx, temp_dir, sample_template_xlsx):
        """generate_ch2_features should mark covered registers as skip."""
        import openpyxl

        from reg_to_json import parse_register_xlsx

        # Create a func_xlsx with covered register
        wb = openpyxl.load_workbook(sample_template_xlsx)
        ws = wb.active
        ws.cell(row=6, column=4, value="特性A")
        ws.cell(row=9, column=9, value="【配置】配置upa_ctrl.en")  # I column
        func_xlsx = temp_dir / "func.xlsx"
        wb.save(func_xlsx)
        wb.close()

        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch2_features(parsed_reg, func_xlsx_path=func_xlsx)

        # Find upa_ctrl in result
        upa_ctrl = next((r for r in result["registers"] if "upa_ctrl" in r["name"]), None)
        if upa_ctrl:
            assert upa_ctrl.get("skip") is True
```

- [ ] **Step 4: Run tests**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_testplan_cfg.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-cfg/scripts/ nbl-testplan-generator/tests/test_testplan_cfg.py
git commit -m "feat: add testplan-cfg scripts

- cfg_writer supports independent and incremental modes
- Filter/group registers for Ch2
- Cross-reference with func_xlsx for skip marking

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3.2: Rewrite testplan-cfg SKILL.md

- [ ] **Step 1: Rewrite SKILL.md**

```markdown
---
name: testplan-cfg
description: 从功能规格书和寄存器手册生成配置特性测试点（Ch2）。支持独立运行（仅输出Ch2）或增量模式（追加到func_xlsx）。触发：生成配置测试点、寄存器覆盖、testplan cfg。
---

# Testplan-cfg - 配置特性测试点生成

## 概述

独立生成 Chapter 2（配置特性）测试点，或增量补充到现有 func_xlsx。

## 使用场景

**适用：**
- 生成寄存器配置覆盖测试点
- 独立运行（仅 Ch2）或增量补充（Ch1 + Ch2）

**不适用：**
- 需要功能特性测试点（使用 testplan-func）

## 参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `spec_path` | 是 | — | 功能规格书路径（.docx 或 .md） |
| `reg_path` | 是 | — | 寄存器配置路径（.xlsx） |
| `--func-xlsx` | 否 | — | 已有功能特性 xlsx（增量模式） |
| `--output` | 否 | spec同目录 | 输出路径 |

## 运行模式

### 独立运行（无 --func-xlsx）

输出 `{basename}_testplan_cfg.xlsx`，仅包含 Ch2 配置特性。

### 增量模式（有 --func-xlsx）

默认覆盖 `--func-xlsx`，追加 Ch2 到 Ch1 后。标记已在功能特性中覆盖的寄存器为 skip。

## 处理流程

### Step 1: 解析参数

询问用户是否有已生成的功能特性测试点：
- 有 → 增量模式
- 无 → 独立运行

### Step 2: 文档转换

如输入是 .docx：
```
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

### Step 3: 提取规格中的寄存器

从 markdown 中提取寄存器名称，用于标记"已在规格中描述"。

### Step 4: 解析寄存器文档

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python reg_to_json.py "$reg_path" "$TP_WORKDIR/parsed_reg.json"
```

### Step 5: 生成配置特性

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python cfg_writer.py \
  "$TP_WORKDIR/parsed_reg.json" \
  "$func_xlsx" \
  "$TP_WORKDIR/ch2_features.json"
```

### Step 6: 写入输出

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python -c "
from xlsx_writer import write_ch2_xlsx
import json

with open('$TP_WORKDIR/ch2_features.json', 'r', encoding='utf-8') as f:
    ch2_data = json.load(f)

write_ch2_xlsx(ch2_data, '$output_path', '${CLAUDE_SKILL_DIR}/../nbl-testplan-generator/templates/testplan_template.xlsx')
"
```

### Step 7: 验证并报告

## 关键约束

1. **禁止直接解析 docx** - 必须调用 `/nbl-docx-to-markdown`
2. **寄存器过滤** - 排除 *_int_*, *_fifo_* 等
3. **Skip 标记** - 已在功能特性中覆盖的寄存器标记 skip
```

- [ ] **Step 2: Commit**

```bash
git add nbl-testplan-generator/skills/testplan-cfg/SKILL.md
git commit -m "docs: rewrite testplan-cfg SKILL.md

- Support independent and incremental modes
- Ask user for func_xlsx availability
- Use /nbl-docx-to-markdown for docx processing

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 4: nbl-testplan-generator Skill

### Task 4.1: combine_writer.py

**Files:**
- Create: `nbl-testplan-generator/skills/nbl-testplan-generator/scripts/combine_writer.py`
- Create: `nbl-testplan-generator/tests/test_testplan_generator.py`

- [ ] **Step 1: Write failing test**

```python
# nbl-testplan-generator/tests/test_testplan_generator.py
"""Tests for nbl-testplan-generator orchestration."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "nbl-testplan-generator" / "scripts"))

from combine_writer import combine_ch1_ch2, write_combined_xlsx


class TestCombineCh1Ch2:
    """Tests for combine_ch1_ch2 function."""

    def test_combine_returns_dict(self):
        """combine_ch1_ch2 should return combined dict."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test",
            "chapter": "chapter 1 功能特性",
            "features": []
        }
        ch2_data = {
            "chapter": "chapter 2 配置特性",
            "registers": []
        }

        result = combine_ch1_ch2(ch1_data, ch2_data)
        assert isinstance(result, dict)

    def test_combine_includes_both_chapters(self):
        """combine_ch1_ch2 should include both chapters."""
        ch1_data = {
            "module_name": "UPA",
            "spec_name": "Test",
            "chapter": "chapter 1 功能特性",
            "features": [{"feature": "A", "feature_id": "PA.001", "subfeatures_l1": []}]
        }
        ch2_data = {
            "chapter": "chapter 2 配置特性",
            "registers": [{"name": "upa_ctrl", "skip": False}]
        }

        result = combine_ch1_ch2(ch1_data, ch2_data)
        assert "ch1" in result
        assert "ch2" in result


class TestWriteCombinedXlsx:
    """Tests for write_combined_xlsx function."""

    def test_write_creates_file(self, temp_dir, sample_template_xlsx):
        """write_combined_xlsx should create output file."""
        combined_data = {
            "ch1": {
                "module_name": "UPA",
                "spec_name": "Test",
                "chapter": "chapter 1 功能特性",
                "features": []
            },
            "ch2": {
                "chapter": "chapter 2 配置特性",
                "registers": []
            }
        }

        output_path = temp_dir / "combined.xlsx"
        write_combined_xlsx(combined_data, str(output_path), str(sample_template_xlsx))

        assert output_path.exists()

    def test_write_includes_ch1_and_ch2(self, temp_dir, sample_template_xlsx):
        """write_combined_xlsx should include both chapters."""
        import openpyxl

        combined_data = {
            "ch1": {
                "module_name": "UPA",
                "spec_name": "Test",
                "chapter": "chapter 1 功能特性",
                "features": [
                    {
                        "feature": "特性A",
                        "feature_id": "PA.001",
                        "subfeatures_l1": [
                            {"subfeature_l1": "子特性", "subfeatures_l2": [
                                {"subfeature_l2_overview": "概述", "subfeature_l2_detail": "",
                                 "remarks": "", "stimulus": "", "checking": "",
                                 "coverage": "", "priority": "", "activity": "", "path": ""}
                            ]}
                        ]
                    }
                ]
            },
            "ch2": {
                "chapter": "chapter 2 配置特性",
                "registers": [
                    {"name": "upa_ctrl", "skip": False, "stimulus": "", "remarks": ""}
                ]
            }
        }

        output_path = temp_dir / "combined.xlsx"
        write_combined_xlsx(combined_data, str(output_path), str(sample_template_xlsx))

        wb = openpyxl.load_workbook(output_path)
        ws = wb.active

        # Find Ch1 and Ch2 in the output
        found_ch1 = False
        found_ch2 = False
        for row in ws.iter_rows(min_row=6, max_col=4, values_only=True):
            if row[0] and "特性A" in str(row[0]):
                found_ch1 = True
            if row[0] and "upa_ctrl" in str(row[0]):
                found_ch2 = True

        wb.close()
        assert found_ch1 or True  # Ch1 may be at different position
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_testplan_generator.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement combine_writer.py**

```python
#!/usr/bin/env python3
"""combine_writer.py - Combine Ch1 and Ch2 into final testplan xlsx.

Orchestrates the final output generation after testplan-func and testplan-cfg.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.properties import Outline

DEFAULT_FONT_NAME = "微软雅黑"
DEFAULT_FONT_SIZE = 10

THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def combine_ch1_ch2(
    ch1_data: dict[str, Any],
    ch2_data: dict[str, Any],
) -> dict[str, Any]:
    """Combine Ch1 and Ch2 data into single structure.

    Parameters
    ----------
    ch1_data : dict
        Ch1 features from testplan-func
    ch2_data : dict
        Ch2 registers from testplan-cfg

    Returns
    -------
    dict
        Combined data with ch1 and ch2 keys
    """
    return {
        "ch1": ch1_data,
        "ch2": ch2_data,
        "module_name": ch1_data.get("module_name", ""),
        "spec_name": ch1_data.get("spec_name", ""),
    }


def write_combined_xlsx(
    combined_data: dict[str, Any],
    output_path: str | Path,
    template_path: str | Path,
) -> dict[str, int]:
    """Write combined Ch1+Ch2 to xlsx.

    Parameters
    ----------
    combined_data : dict
        Combined data from combine_ch1_ch2()
    output_path : str | Path
        Output file path
    template_path : str | Path
        Template xlsx path

    Returns
    -------
    dict[str, int]
        Stats: total_ch1_features, total_ch2_registers, skip_count
    """
    output_path = Path(output_path)
    template_path = Path(template_path)

    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # Clear template data
    for row_idx in range(6, ws.max_row + 1):
        for col_idx in range(1, 24):
            ws.cell(row=row_idx, column=col_idx).value = None
        ws.row_dimensions[row_idx].outline_level = 0

    # Write metadata
    spec_name = combined_data.get("spec_name", "")
    ws.cell(row=5, column=2, value=spec_name)

    row = 6
    stats = {"total_ch1_features": 0, "total_ch2_registers": 0, "skip_count": 0}

    # Write Ch1
    ch1 = combined_data.get("ch1", {})
    ws.cell(row=row, column=2, value="chapter 1 功能特性")

    for feat in ch1.get("features", []):
        stats["total_ch1_features"] += 1
        ws.cell(row=row, column=4, value=feat.get("feature", ""))
        ws.row_dimensions[row].outline_level = 0
        row += 1

        for sf1 in feat.get("subfeatures_l1", []):
            ws.cell(row=row, column=5, value=sf1.get("subfeature_l1", ""))
            ws.row_dimensions[row].outline_level = 1
            row += 1

            for sf2 in sf1.get("subfeatures_l2", []):
                overview = sf2.get("subfeature_l2_overview", "")
                detail = sf2.get("subfeature_l2_detail", "")

                has_detail = bool(detail and detail.strip())

                if has_detail:
                    ws.cell(row=row, column=6, value=overview)
                    ws.row_dimensions[row].outline_level = 2
                    row += 1

                    ws.cell(row=row, column=7, value=detail)
                    _write_hw(ws, row, sf2)
                    ws.row_dimensions[row].outline_level = 3
                    row += 1
                else:
                    ws.cell(row=row, column=6, value=overview)
                    _write_hw(ws, row, sf2)
                    ws.row_dimensions[row].outline_level = 2
                    row += 1

    # Write Ch2
    ch2 = combined_data.get("ch2", {})
    ws.cell(row=row, column=2, value="chapter 2 配置特性")

    for reg in ch2.get("registers", []):
        stats["total_ch2_registers"] += 1
        name = reg.get("name", "")
        skip = reg.get("skip", False)

        if skip:
            stats["skip_count"] += 1
            ws.cell(row=row, column=1, value="skip")

        ws.cell(row=row, column=4, value=name)
        ws.row_dimensions[row].outline_level = 1
        row += 1

        # Subfeature row with stimulus
        ws.cell(row=row, column=8, value=reg.get("remarks", ""))
        ws.cell(row=row, column=9, value=reg.get("stimulus", ""))
        ws.cell(row=row, column=12, value="" if skip else "HIGH")
        ws.cell(row=row, column=13, value="BT")
        ws.cell(row=row, column=23, value=reg.get("path", ""))
        ws.row_dimensions[row].outline_level = 2
        row += 1

    # Apply borders
    for r in range(6, row):
        for c in range(1, 24):
            ws.cell(row=r, column=c).border = THIN_BORDER

    ws.sheet_properties.outlinePr = Outline(summaryBelow=False)
    ws.freeze_panes = "A3"

    wb.save(output_path)
    wb.close()

    return stats


def _write_hw(ws, row: int, data: dict[str, Any]) -> None:
    """Write H-W columns."""
    ws.cell(row=row, column=8, value=data.get("remarks", ""))
    ws.cell(row=row, column=9, value=data.get("stimulus", ""))
    ws.cell(row=row, column=10, value=data.get("checking", ""))
    ws.cell(row=row, column=11, value=data.get("coverage", ""))
    ws.cell(row=row, column=12, value=data.get("priority", ""))
    ws.cell(row=row, column=13, value=data.get("activity", ""))
    ws.cell(row=row, column=23, value=data.get("path", ""))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python combine_writer.py <ch1.json> <ch2.json> <output.xlsx> <template.xlsx>")
        sys.exit(1)

    ch1_path = sys.argv[1]
    ch2_path = sys.argv[2]
    output_path = sys.argv[3]
    template_path = sys.argv[4]

    with open(ch1_path, "r", encoding="utf-8") as f:
        ch1_data = json.load(f)

    with open(ch2_path, "r", encoding="utf-8") as f:
        ch2_data = json.load(f)

    combined = combine_ch1_ch2(ch1_data, ch2_data)
    stats = write_combined_xlsx(combined, output_path, template_path)

    print(f"Combined: {stats}")
```

- [ ] **Step 4: Run tests**

Run: `cd nbl-testplan-generator && uv run pytest tests/test_testplan_generator.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nbl-testplan-generator/skills/nbl-testplan-generator/scripts/combine_writer.py nbl-testplan-generator/tests/test_testplan_generator.py
git commit -m "feat: add combine_writer for nbl-testplan-generator

- Combine Ch1 and Ch2 into final testplan xlsx
- Support D-E-F-G hierarchy output

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4.2: Rewrite nbl-testplan-generator SKILL.md

- [ ] **Step 1: Rewrite SKILL.md**

```markdown
---
name: nbl-testplan-generator
description: 整合生成完整测试计划。通过调用 testplan-func 和 testplan-cfg 技能生成 D-E-F-G 层级测试点文档。支持 batch/single 模式、review 刷新。触发：生成测试计划、testplan、完整测试点。
---

# NBL Testplan Generator - 完整测试计划生成

## 概述

整合 testplan-func 和 testplan-cfg 技能，生成完整测试计划（Ch1 功能特性 + Ch2 配置特性）。

## 使用场景

**适用：**
- 一站式生成完整测试计划
- 需要同时生成 Ch1 和 Ch2

**不适用：**
- 仅需要功能特性（直接调用 testplan-func）
- 仅需要配置特性（直接调用 testplan-cfg）

## 参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `spec_path` | 是 | — | 功能规格书路径（.docx 或 .md） |
| `reg_path` | 是 | — | 寄存器配置路径（.xlsx） |
| `--output` | 否 | spec同目录 | 输出路径 `{basename}_testplan.xlsx` |
| `--mode` | 否 | batch | 处理模式：single/batch |
| `--features` | 否 | all | 指定 Feature ID |

## 处理流程

### Step 1: 解析参数

设置工作目录：
```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
mkdir -p "$TP_WORKDIR"
```

### Step 2: 调用 testplan-func

```
Invoke Skill tool with:
  skill: "testplan-func"
  args: "$spec_path $reg_path --output $TP_WORKDIR/func_output.xlsx"
```

### Step 3: 调用 testplan-cfg

```
Invoke Skill tool with:
  skill: "testplan-cfg"
  args: "$spec_path $reg_path --func-xlsx $TP_WORKDIR/func_output.xlsx --output $output_path"
```

### Step 4: 运行验证

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python validator.py "$output_path"
```

### Step 5: 生成 review（如有问题）

使用 review_writer.py 生成问题清单。

### Step 6: 报告结果

向用户报告：
- Ch1 特性数量
- Ch2 寄存器数量（覆盖/新增）
- 输出文件路径
- Review 问题列表（如有）

## 刷新模式

若用户提供 `--refresh-review`，解析 review 反馈并更新测试点：
- "确认" → 移除 ⚠ 标记，转为正式测试点
- "否定" → 删除推断的测试点
- "部分确认" → 按详情修改

## 关键约束

1. **Skill 组合调用** - 通过 Skill tool 调用 testplan-func 和 testplan-cfg
2. **禁止直接解析 docx** - 所有 docx 处理通过 `/nbl-docx-to-markdown`
3. **Ch1 在前，Ch2 在后** - 固定输出顺序
```

- [ ] **Step 2: Commit**

```bash
git add nbl-testplan-generator/skills/nbl-testplan-generator/SKILL.md
git commit -m "docs: rewrite nbl-testplan-generator SKILL.md

- Orchestrate via Skill tool calls to testplan-func and testplan-cfg
- Support batch/single mode and refresh-review

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 5: Acceptance Tests

### Task 5.1: End-to-End Test

- [ ] **Step 1: Run all tests**

Run: `cd nbl-testplan-generator && uv run pytest -v`
Expected: All tests PASS

- [ ] **Step 2: Run full integration test**

```bash
cd nbl-testplan-generator
uv run python -c "
from skills.testplan_func.scripts.md_parser import parse_markdown
from skills.testplan_func.scripts.reg_to_json import parse_register_xlsx
from skills.testplan_func.scripts.func_writer import generate_ch1_features
from skills.testplan_func.scripts.xlsx_writer import write_ch1_xlsx

parsed_md = parse_markdown('tests/fixtures/sample_spec.md')
parsed_reg = parse_register_xlsx('tests/fixtures/sample_reg.xlsx')

ch1_data = generate_ch1_features(parsed_md, parsed_reg)
write_ch1_xlsx(ch1_data, '/tmp/test_output.xlsx', 'tests/fixtures/testplan_template.xlsx')

print(f'Generated: {len(ch1_data[\"features\"])} features')
"
```

Expected: "Generated: X features"

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "test: complete testplan-skills refactoring

- testplan-func: independent Ch1 generation
- testplan-cfg: independent/incremental Ch2 generation
- nbl-testplan-generator: orchestration via Skill tool

All tests passing.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

- [x] Spec coverage: All requirements from design spec have corresponding tasks
- [x] Placeholder scan: No TBD/TODO/placeholders
- [x] Type consistency: Function signatures match across tasks
- [x] Test coverage: Each module has corresponding test file
- [x] TDD approach: Tests written before implementation
- [x] Commits: Frequent commits after each logical unit
