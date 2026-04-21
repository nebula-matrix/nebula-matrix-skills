# nbl-tp-func-gen 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零实现 `nbl-testplan-generator` 插件，包含 `nbl-tp-func-gen` skill，实现从 docx/xlsx 到结构化测试点 xlsx 的完整流水线。

**Architecture:** 混合模型 — Python 负责结构化处理（解析、格式输出、JSON 转换），Claude SKILL.md 负责内容级语义分析（测试点分解、交叉引用、覆盖率设计）。大文档通过分块策略处理。

**Tech Stack:** Python 3.12+, openpyxl, uv, pytest, nbl-docx-to-markdown skill

---

## 文件结构映射

创建前确认磁盘状态：`nbl-testplan-generator/` 目录已被删除（git commit 88d9df7），legacy code 在 `nbl-testplan-generator-backup/` 中。

### 新插件目录结构

```
nebula-matrix-skills/
├── nbl-testplan-generator/                    # 新增插件根目录
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── .gitignore
│   ├── pyproject.toml
│   ├── README.md
│   ├── skills/
│   │   └── nbl-tp-func-gen/
│   │       ├── SKILL.md
│   │       ├── reference/
│   │       │   ├── spec_input/
│   │       │   │   └── testplan-func-system-prompt.md
│   │       │   └── template/
│   │       │       └── testplan_template.xlsx    # 复制自 assets
│   │       └── scripts/
│   │           ├── __init__.py
│   │           ├── parsers/
│   │           │   ├── __init__.py
│   │           │   ├── md_parser.py            # Markdown → spec_tree.json
│   │           │   └── reg_parser.py             # xlsx → reg_info.json
│   │           ├── writers/
│   │           │   ├── __init__.py
│   │           │   └── combine_writer.py         # testplan_raw.json → xlsx
│   │           ├── review/
│   │           │   ├── __init__.py
│   │           │   └── review_writer.py          # testplan_raw.json → review.md
│   │           ├── reg_to_json.py              # CLI 入口
│   │           └── tp_gen.py                   # 统一 CLI 入口（预留）
│   └── tests/                                   # 测试目录
│       ├── __init__.py
│       ├── conftest.py
│       ├── fixtures/
│       │   ├── sample_spec.md
│       │   ├── sample_reg.xlsx
│       │   └── testplan_template.xlsx
│       ├── test_md_parser.py
│       ├── test_reg_parser.py
│       ├── test_combine_writer.py
│       └── test_review_writer.py
```

---

## Task 1: 架构与框架 — 目录结构与配置

**目标:** 搭建完整的插件目录结构、创建所有配置文件、复制模板和参考素材。

**Files:**
- Create: `nbl-testplan-generator/.claude-plugin/plugin.json`
- Create: `nbl-testplan-generator/pyproject.toml`
- Create: `nbl-testplan-generator/.gitignore`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/SKILL.md`（骨架）
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/__init__.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/parsers/__init__.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/writers/__init__.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/review/__init__.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/reference/spec_input/testplan-func-system-prompt.md`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/reference/template/testplan_template.xlsx`
- Create: `nbl-testplan-generator/tests/__init__.py`
- Create: `nbl-testplan-generator/README.md`（骨架）
- Modify: `README.md`（根目录）
- Modify: `.claude-plugin/marketplace.json`（更新 source 路径）

---

### Task 1 Step 1: 创建目录结构

Run:
```bash
mkdir -p nbl-testplan-generator/{.claude-plugin,skills/nbl-tp-func-gen/{scripts/{parsers,writers,review},reference/{spec_input,template}},tests/fixtures}
touch nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/__init__.py
touch nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/parsers/__init__.py
touch nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/writers/__init__.py
touch nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/review/__init__.py
touch nbl-testplan-generator/tests/__init__.py
touch nbl-testplan-generator/tests/fixtures/__init__.py
```

Expected: 目录结构完整创建

---

### Task 1 Step 2: 创建 plugin.json

Create: `nbl-testplan-generator/.claude-plugin/plugin.json`

```json
{
  "name": "nbl-testplan-generator",
  "version": "3.0.0",
  "description": "数字芯片验证测试计划生成器，从功能规格书（.docx）和寄存器配置（.xlsx）生成结构化测试点文档，支持 D-E-F/G 层级分解",
  "skills": "./skills"
}
```

---

### Task 1 Step 3: 创建 pyproject.toml

Create: `nbl-testplan-generator/pyproject.toml`

```toml
[project]
name = "nbl-testplan-generator"
version = "3.0.0"
description = "数字芯片验证测试计划生成器，支持功能特性和配置特性的结构化测试点生成"
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

[tool.hatch.build.targets.wheel]
packages = ["src/nbl_testplan_generator"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["skills/nbl-tp-func-gen/scripts"]
```

---

### Task 1 Step 4: 创建 .gitignore

Create: `nbl-testplan-generator/.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary/cache
.tpcache/
.tp_cache/
tests/superpowers/
*_work/
*_output/

# Output files (keep templates)
testplan_output.xlsx
*.md~tmp
```

---

### Task 1 Step 5: 复制模板文件

Run:
```bash
cp /home/alvin.xu/test_center/test_testplan_skills/assets/testplan_template.xlsx \
   nbl-testplan-generator/skills/nbl-tp-func-gen/reference/template/
```

Expected: 模板已复制到 `reference/template/`

---

### Task 1 Step 6: 复制 system prompt

Run:
```bash
cp /home/alvin.xu/nebula-matrix/nebula-matrix-skills/testplan-func-system-prompt.md \
   nbl-testplan-generator/skills/nbl-tp-func-gen/reference/spec_input/
```

---

### Task 1 Step 7: 创建 SKILL.md 骨架

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/SKILL.md`

```markdown
---
name: nbl-tp-func-gen
description: 当用户需要从功能规格书（.docx）和寄存器手册（.xlsx）生成功能特性测试点 xlsx 文档时触发。支持 D→E→F→G 层级分解，自动交叉引用寄存器配置。输出格式符合 nbl-testplan-generator 模板规范。
---

# nbl-tp-func-gen Skill

## 角色

资深数字芯片验证工程师，精通 SystemVerilog/UVM，负责根据模块功能规格书和寄存器配置文档生成功能特性（Chapter 1）的测试点。

## 工作流程

### 阶段1: 文档转换
调用 `/nbl-docx-to-markdown` skill 将 .docx 转换为 Markdown...

### 阶段2: Markdown 结构化解析
调用 `scripts/parsers/md_parser.py` ...

### 阶段3: 寄存器手册解析
调用 `scripts/reg_to_json.py` ...

### 阶段4: 内容分析
- 读取 spec_tree.json + reg_info.json
- 按 Feature 分块，逐块交叉引用分析
- 生成 testplan_func_raw.json + fs_reg_slv_review.md

### 阶段5: 输出格式化
调用 `scripts/writers/combine_writer.py` ...

## 输出规范
（详见 design doc 第5章）
```

---

### Task 1 Step 8: 创建测试 fixture

创建两个 fixture 文件供后续测试使用。

Create: `nbl-testplan-generator/tests/fixtures/sample_spec.md`

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
相关寄存器：`upa_ctrl`、`upa_data_0`

#### PA.002 双向数据交换

UPA模块支持双向数据交换模式，数据可以同时在两个方向传输。
相关寄存器：`upa_ctrl`、`upa_fwd_cfg`

### 2.2 控制功能

#### PA.003 流控机制

UPA模块支持流控机制。
相关寄存器：`upa_ctrl.flow_en`、`upa_fifo_th`

## 3. DFX

测试模式访问寄存器：`test_mode_en`
```

---

Create: `nbl-testplan-generator/tests/conftest.py`

```python
"""Pytest fixtures for nbl-testplan-generator tests."""
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
def sample_template_xlsx(fixtures_dir) -> Path:
    """Return path to template xlsx file."""
    return fixtures_dir / "testplan_template.xlsx"
```

---

### Task 1 Step 9: 编写 README.md 骨架

Create: `nbl-testplan-generator/README.md`

```markdown
# nbl-testplan-generator

数字芯片验证测试计划生成器插件。

## 功能

- 从功能规格书（.docx）和寄存器手册（.xlsx）生成结构化测试点文档
- 支持 D→E→F→G 层级分解
- 自动交叉引用寄存器配置信息
- 生成 `fs_reg_slv_review.md` 记录不确定内容

## 技能

### nbl-tp-func-gen

生成功能特性（Chapter 1）测试点，详见 `skills/nbl-tp-func-gen/SKILL.md`。

## 依赖

- Python >= 3.12
- openpyxl >= 3.1.0
- pytest >= 8.0.0（开发）
```

---

### Task 1 Step 10: 更新根目录 README.md

Modify: `README.md`（确保 nbl-testplan-generator 已在插件列表中）— 如果 marketplace.json 中已有条目则无需修改。

---

### Task 1 Step 11: 提交

Run:
```bash
git add nbl-testplan-generator/
git commit -m "$(cat <<'EOF'
feat: scaffold nbl-testplan-generator plugin and nbl-tp-func-gen skill

- 创建插件目录结构
- 添加 plugin.json, pyproject.toml, .gitignore
- 复制模板和 system prompt 到 reference/
- 创建 SKILL.md 骨架
- 添加测试框架结构

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit created, `git log --oneline -1` shows the new commit

---

## Task 2: Parser 开发 — md_parser.py + reg_parser.py

**目标:** 实现 Markdown 解析器和寄存器手册解析器，带完整测试。输出 `spec_tree.json` 和 `reg_info.json` 结构。

**Files:**
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/parsers/md_parser.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/parsers/reg_parser.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/reg_to_json.py`
- Create: `nbl-testplan-generator/tests/test_md_parser.py`
- Create: `nbl-testplan-generator/tests/test_reg_parser.py`
- Create: `nbl-testplan-generator/tests/fixtures/sample_reg.xlsx`

---

### Task 2 Step 1: 编写 md_parser.py

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/parsers/md_parser.py`

```python
#!/usr/bin/env python3
"""md_parser.py - Parse Markdown spec into spec_tree.json structure.

Reads a Markdown file (converted from docx by nbl-docx-to-markdown),
extracts chapters, feature tree, and cross-reference index.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def parse_spec_tree(filepath: str | Path) -> dict[str, Any]:
    """Parse a Markdown functional spec into spec_tree.json.

    Returns structure:
    {
        "module_name": str,
        "spec_title": str,
        "chapters": [
            {
                "chapter_id": str,
                "chapter_title": str,
                "outline_level": int,
                "content_md": str,
                "features": [...]
            }
        ]
    }
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    # Extract document title from first H1
    spec_title = filepath.stem
    for line in lines:
        if line.startswith("# "):
            spec_title = line[2:].strip()
            break

    # Build chapter list with content segments
    chapters: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    chapter_counter = 0

    for line in lines:
        heading_match = heading_pattern.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            chapter_counter += 1
            if current is not None:
                current["content_md"] = "\n".join(current["_lines"])
            new_chapter = {
                "chapter_id": f"ch{chapter_counter}",
                "chapter_title": title,
                "outline_level": level - 1,
                "content_md": "",
                "features": [],
                "_lines": [],
            }
            chapters.append(new_chapter)
            current = new_chapter
        elif current is not None:
            current["_lines"].append(line)

    if current is not None:
        current["content_md"] = "\n".join(current["_lines"])

    # Identify module_features chapter
    module_features_ch = None
    for ch in chapters:
        if "模块特性" in ch["chapter_title"]:
            module_features_ch = ch
            break

    features: list[dict[str, Any]] = []
    if module_features_ch is not None:
        features = _extract_features(module_features_ch["content_md"])

    # Build feature-specific cross-reference index
    _build_refs(chapters, features)

    # Cleanup
    for ch in chapters:
        del ch["_lines"]

    # Derive module name from spec_title (e.g. "Leonis_PA_Functional_Specification" -> "upa")
    module_name = _infer_module_name(spec_title)

    return {
        "module_name": module_name,
        "spec_title": spec_title,
        "chapters": chapters,
    }


def _extract_features(content: str) -> list[dict[str, Any]]:
    """Extract feature items from the '模块特性' chapter content.

    Pattern: 【PA.XXX】Feature name
    """
    features: list[dict[str, Any]] = []
    # Match 【ID】 followed by description on same line
    feature_pattern = re.compile(r"【(\w+\.\d+)】\s*(.+?)$", re.MULTILINE)
    for match in feature_pattern.finditer(content):
        fid = match.group(1)
        fname = match.group(2).strip()
        features.append({
            "feature_id": fid,
            "feature_name": fname,
            "content_md": f"【{fid}】{fname}",
            "refs": {
                "detail_chapters": [],
                "data_structure_chapters": [],
                "init_chapters": [],
                "error_chapters": [],
                "ctrl_chapters": [],
                "dft_chapters": [],
                "limit_chapters": [],
            }
        })
    return features


def _build_refs(chapters: list, features: list) -> None:
    """Build cross-reference refs for each feature.

    Strategies:
    1. Keyword match: feature name keywords in chapter title
    2. Marker match: feature_id pattern in chapter content
    3. Register back-ref: find chapter that mentions feature registers
    """
    for feat in features:
        keywords = _extract_keywords(feat["feature_name"])
        feat_id = feat["feature_id"]
        for ch in chapters:
            ch_title = ch["chapter_title"]
            ch_content = ch["content_md"]

            # Skip features chapter itself
            if "模块特性" in ch_title:
                continue

            matched = False
            # Strategy 1: keyword in title
            if any(kw in ch_title for kw in keywords):
                matched = True

            # Strategy 2: feature ID marker in content
            if not matched and feat_id in ch_content:
                match_count = ch_content.count(feat_id)
                if match_count >= 1:
                    matched = True

            if matched:
                category = _classify_chapter(ch_title)
                feat["refs"][f"{category}_chapters"].append(ch["chapter_id"])


def _extract_keywords(feature_name: str) -> list[str]:
    """Extract meaningful keywords from a feature name."""
    stop_words = {"支持", "实现", "功能", "机制", "特性", "的", "和", "与"}
    words = feature_name.split()
    keywords = [w for w in words if w not in stop_words and len(w) >= 2]
    return keywords if keywords else words


def _classify_chapter(title: str) -> str:
    """Classify a chapter into a reference category."""
    title_norm = title.lower()
    if any(k in title_norm for k in ("详述", "详细", "detail", "功能详述")):
        return "detail"
    elif any(k in title_norm for k in ("数据结构", "data structure", "格式")):
        return "data_structure"
    elif any(k in title_norm for k in ("初始化", "init", "启动")):
        return "init"
    elif any(k in title_norm for k in ("错误", "error", "异常", "故障", "fault")):
        return "error"
    elif any(k in title_norm for k in ("流控", "流控制", "ctrl", "control", "使能")):
        return "ctrl"
    elif any(k in title_norm for k in ("dft", "dfx", "可测试", "debug")):
        return "dft"
    elif any(k in title_norm for k in ("限制", "limit", "约束", "要求")):
        return "limit"
    else:
        return "detail"


def _infer_module_name(spec_title: str) -> str:
    """Infer short module name from spec title."""
    title_lower = spec_title.lower()
    name_map = {
        "upa": ("upa", "pa", "datapath_upa"),
        "dped": ("dped", "ped", "datapath_dped"),
    }
    for name, keywords in name_map.items():
        if any(k in title_lower for k in keywords):
            return name
    # Fallback: take first letter sequence
    import re as _re
    letters = _re.findall(r"[a-z]+", title_lower)
    return letters[0] if letters else "module"


def get_feature_by_id(spec_tree: dict, feature_id: str) -> dict | None:
    """Look up a feature by its ID in spec_tree."""
    for ch in spec_tree.get("chapters", []):
        for feat in ch.get("features", []):
            if feat.get("feature_id") == feature_id:
                return feat
    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python md_parser.py <spec.md>")
        sys.exit(1)
    result = parse_spec_tree(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

---

### Task 2 Step 2: 编写 test_md_parser.py（先写 failing test）

Create: `nbl-testplan-generator/tests/test_md_parser.py`

```python
"""Tests for md_parser module."""
from pathlib import Path

import pytest

from parsers.md_parser import parse_spec_tree, get_feature_by_id


class TestParseSpecTree:
    """Tests for parse_spec_tree function."""

    def test_returns_dict(self, sample_spec_md):
        """parse_spec_tree should return a dictionary."""
        result = parse_spec_tree(sample_spec_md)
        assert isinstance(result, dict)

    def test_has_module_name(self, sample_spec_md):
        """Result should contain inferred module_name."""
        result = parse_spec_tree(sample_spec_md)
        assert "module_name" in result
        assert result["module_name"] == "upa"

    def test_has_spec_title(self, sample_spec_md):
        """Result should have spec_title from first H1."""
        result = parse_spec_tree(sample_spec_md)
        assert "spec_title" in result
        assert "UPA" in result["spec_title"]

    def test_has_chapters(self, sample_spec_md):
        """Result should have chapters list."""
        result = parse_spec_tree(sample_spec_md)
        assert "chapters" in result
        assert len(result["chapters"]) > 0

    def test_chapters_have_ids(self, sample_spec_md):
        """Each chapter should have chapter_id and chapter_title."""
        result = parse_spec_tree(sample_spec_md)
        for ch in result["chapters"]:
            assert "chapter_id" in ch
            assert "chapter_title" in ch

    def test_module_features_chapter_exists(self, sample_spec_md):
        """Should find '模块特性' chapter."""
        result = parse_spec_tree(sample_spec_md)
        titles = [ch["chapter_title"] for ch in result["chapters"]]
        assert any("模块特性" in t for t in titles)

    def test_extracts_features(self, sample_spec_md):
        """Should extract three features: PA.001, PA.002, PA.003."""
        result = parse_spec_tree(sample_spec_md)
        features_ch = next(
            (ch for ch in result["chapters"] if "模块特性" in ch["chapter_title"]),
            None,
        )
        assert features_ch is not None
        assert "features" in features_ch
        feature_ids = [f["feature_id"] for f in features_ch["features"]]
        assert "PA.001" in feature_ids
        assert "PA.002" in feature_ids
        assert "PA.003" in feature_ids

    def test_feature_has_refs(self, sample_spec_md):
        """Each feature should have refs dict."""
        result = parse_spec_tree(sample_spec_md)
        features_ch = next(
            (ch for ch in result["chapters"] if "模块特性" in ch["chapter_title"]),
            None,
        )
        if features_ch and features_ch["features"]:
            feat = features_ch["features"][0]
            assert "refs" in feat
            assert isinstance(feat["refs"], dict)
            assert "detail_chapters" in feat["refs"]


class TestGetFeatureById:
    """Tests for get_feature_by_id."""

    def test_finds_existing(self, sample_spec_md):
        """Should find PA.001."""
        result = parse_spec_tree(sample_spec_md)
        feat = get_feature_by_id(result, "PA.001")
        assert feat is not None
        assert feat["feature_id"] == "PA.001"

    def test_returns_none_for_missing(self, sample_spec_md):
        """Should return None for nonexistent ID."""
        result = parse_spec_tree(sample_spec_md)
        assert get_feature_by_id(result, "PA.999") is None
```

---

### Task 2 Step 3: 运行 md_parser 测试（首次，应 PASS 因为代码已写）

Run from `nbl-testplan-generator/`:
```bash
cd nbl-testplan-generator
python -m pytest tests/test_md_parser.py -v
```

Expected: All 9 tests PASS

---

### Task 2 Step 4: 编写 reg_parser.py

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/parsers/reg_parser.py`

```python
#!/usr/bin/env python3
"""reg_parser.py - Parse register xlsx into reg_info.json structure."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def parse_register_xlsx(filepath: str | Path) -> dict[str, Any]:
    """Parse a register xlsx into structured reg_info dict.

    Returns structure:
    {
        "module_name": str,
        "registers": [
            {
                "reg_name": str,
                "reg_addr": str,
                "reg_desc": str,
                "fields": [
                    {
                        "field_name": str,
                        "bit_range": str,
                        "rw": str,
                        "reset": str,
                        "desc": str
                    }
                ]
            }
        ]
    }

    Lazy import openpyxl to avoid startup cost.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Register file not found: {filepath}")

    try:
        import openpyxl  # Lazy import
    except ImportError:
        raise ImportError("openpyxl is required. Install: pip install openpyxl")

    wb = openpyxl.load_workbook(filepath, data_only=True)

    module_name = _infer_module_name(filepath.stem)

    result: dict[str, Any] = {
        "module_name": module_name,
        "source_file": filepath.name,
        "registers": [],
        "register_tables": [],
    }

    skip_sheets = {"封面", "地址映射", "address_map", "summary", "sheet1"}

    for sheet_name in wb.sheetnames:
        if sheet_name.lower() in {s.lower() for s in skip_sheets}:
            continue
        ws = wb[sheet_name]
        registers = _parse_register_sheet(ws)
        result["registers"].extend(registers)

    wb.close()
    return result


def _parse_register_sheet(ws) -> list[dict[str, Any]]:
    """Parse a single worksheet containing register definitions.""""
    registers: list[dict[str, Any]] = []

    # Detect header row
    header_row_num = None
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True), 1):
        row_values = [str(v).lower().strip() if v else "" for v in row]
        # Look for common register header fields
        header_keywords = ["offset", "addr", "address", "name", "field", "bit", "description"]
        if sum(1 for kv in header_keywords if any(kv in rv for rv in row_values)) >= 2:
            header_row_num = i
            break

    if header_row_num is None:
        return registers  # No register table detected

    # Build column index from header
    header = [str(v).strip() if v else "" for v in ws.iter_rows(
        min_row=header_row_num, max_row=header_row_num, values_only=True
    ).__next__()]

    col_map: dict[str, int] = {}
    for idx, h in enumerate(header):
        hl = h.lower()
        if "offset" in hl or "addr" in hl:
            col_map["addr"] = idx
        elif "name" in hl and "field" not in hl:
            col_map["reg_name"] = idx
        elif "field" in hl:
            col_map["field_name"] = idx
        elif "bit" in hl:
            col_map["bit_range"] = idx
        elif "rw" in hl or "access" in hl:
            col_map["rw"] = idx
        elif "description" in hl or "desc" in hl:
            col_map["desc"] = idx
        elif "reset" in hl or "default" in hl:
            col_map["reset"] = idx

    current_reg: dict[str, Any] | None = None

    for row in ws.iter_rows(min_row=header_row_num + 1, values_only=True):
        row_values = [str(v) if v is not None else "" for v in row]
        if not any(row_values):
            continue

        reg_name = row_values[col_map.get("reg_name", 0)].strip() if "reg_name" in col_map else ""
        field_name = row_values[col_map.get("field_name", 0)].strip() if "field_name" in col_map else ""

        # If reg_name exists and field_name is empty/new, it's a new register row
        if reg_name and (not field_name or field_name == reg_name):
            if current_reg is not None:
                registers.append(current_reg)
            addr = row_values[col_map.get("addr", 0)] if "addr" in col_map else ""
            desc = row_values[col_map.get("desc", -1)] if "desc" in col_map else ""
            current_reg = {
                "reg_name": reg_name,
                "reg_addr": addr,
                "reg_desc": desc,
                "fields": [],
            }
            # If this row also has a field
            if field_name and field_name != reg_name:
                _add_field(current_reg, row_values, col_map)
        elif current_reg is not None and field_name:
            _add_field(current_reg, row_values, col_map)

    if current_reg is not None:
        registers.append(current_reg)

    return registers


def _add_field(reg: dict, row_values: list, col_map: dict) -> None:
    """Append a field to the current register."""
    field = {
        "field_name": row_values[col_map.get("field_name", 0)] if "field_name" in col_map else "",
        "bit_range": row_values[col_map.get("bit_range", 0)] if "bit_range" in col_map else "",
        "rw": row_values[col_map.get("rw", 0)] if "rw" in col_map else "",
        "reset": row_values[col_map.get("reset", 0)] if "reset" in col_map else "",
        "desc": row_values[col_map.get("desc", -1)] if "desc" in col_map else "",
    }
    reg["fields"].append(field)


def _infer_module_name(stem: str) -> str:
    """Infer module name from filename."""
    stem_lower = stem.lower()
    for name in ("upa", "dped", "uvn"):
        if name in stem_lower:
            return name
    # Fallback: extract first alnum sequence
    m = re.search(r"[a-z]+", stem_lower)
    return m.group(0) if m else "module"


def get_register_by_name(reg_info: dict, reg_name: str) -> dict | None:
    """Find a register by name in reg_info."""
    for reg in reg_info.get("registers", []):
        if reg.get("reg_name") == reg_name:
            return reg
    return None


def get_field_by_name(reg: dict, field_name: str) -> dict | None:
    """Find a field by name within a register."""
    for field in reg.get("fields", []):
        if field.get("field_name") == field_name:
            return field
    return None
```

---

### Task 2 Step 5: 编写 test_reg_parser.py（先写 failing test）

Create: `nbl-testplan-generator/tests/test_reg_parser.py`

```python
"""Tests for reg_parser module."""
from pathlib import Path

import pytest

from parsers.reg_parser import parse_register_xlsx, get_register_by_name


class TestParseRegisterXlsx:
    """Tests for parse_register_xlsx function."""

    def test_returns_dict(self, sample_reg_xlsx):
        """parse_register_xlsx should return a dictionary."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert isinstance(result, dict)

    def test_extracts_module_name(self, sample_reg_xlsx):
        """Should infer module name from filename."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "module_name" in result
        assert result["module_name"] == "upa"

    def test_extracts_registers_list(self, sample_reg_xlsx):
        """Should extract registers list."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "registers" in result
        assert isinstance(result["registers"], list)
        assert len(result["registers"]) > 0

    def test_register_has_name(self, sample_reg_xlsx):
        """First register should have reg_name."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = result["registers"][0]
        assert "reg_name" in reg
        assert reg["reg_name"]

    def test_register_has_fields(self, sample_reg_xlsx):
        """Register should have fields list."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = result["registers"][0]
        assert "fields" in reg
        assert isinstance(reg["fields"], list)

    def test_fields_have_required_keys(self, sample_reg_xlsx):
        """Each field should have field_name, bit_range, rw, reset, desc."""
        result = parse_register_xlsx(sample_reg_xlsx)
        for reg in result["registers"]:
            for field in reg["fields"]:
                assert "field_name" in field
                assert "bit_range" in field
                assert "rw" in field
                assert "reset" in field
                assert "desc" in field


class TestGetRegisterByName:
    """Tests for get_register_by_name."""

    def test_finds_existing(self, sample_reg_xlsx):
        """Should find first register by name."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg_name = result["registers"][0]["reg_name"]
        found = get_register_by_name(result, reg_name)
        assert found is not None
        assert found["reg_name"] == reg_name

    def test_returns_none_for_missing(self, sample_reg_xlsx):
        """Should return None for missing register."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert get_register_by_name(result, "NONEXISTENT") is None
```

---

### Task 2 Step 6: 创建 sample_reg.xlsx fixture

需要创建一个可以被 openpyxl 读取的 xlsx fixture。从 backup 复制或使用 Python 代码创建。

如果 backup 中 fixture 可用，直接复制。否则用 openpyxl 创建。

Run:
```bash
cp /home/alvin.xu/nebula-matrix/nebula-matrix-skills/nbl-testplan-generator-backup/tests/fixtures/sample_reg.xlsx \
   nbl-testplan-generator/tests/fixtures/sample_reg.xlsx 2>/dev/null || echo "Backup missing, create via Python"
```

If copy fails, create via inline Python script (uses openpyxl, which should be installed after `uv sync`):

Create with script:
```python
"""Create a minimal sample_reg.xlsx for testing."""
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "CTRL"
ws.append(["Offset(Addr)", "Name", "Field", "Bits", "Access", "Default", "Description"])
ws.append(["0x0000", "UPA_CTRL", "upa_ctrl", "[31:0]", "RW", "0x0000", "全局控制寄存器"])
ws.append(["", "", "en", "[0]", "RW", "0", "UPA使能"])
ws.append(["", "", "mode", "[2:1]", "RW", "0", "工作模式"])
wb.save("nbl-testplan-generator/tests/fixtures/sample_reg.xlsx")
```

---

### Task 2 Step 7: 编写 reg_to_json.py CLI 入口

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/reg_to_json.py`

```python
#!/usr/bin/env python3
"""reg_to_json.py - CLI to convert register xlsx to JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from parsers.reg_parser import parse_register_xlsx


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Convert register xlsx to JSON")
    parser.add_argument("input", help="Input xlsx file path")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("-m", "--module", help="Module name override")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    result = parse_register_xlsx(input_path)

    if args.module:
        result["module_name"] = args.module

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Written: {output_path}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### Task 2 Step 8: 运行全部 Parser 测试

Ensure `cd nbl-testplan-generator` and run:
```bash
python -m pytest tests/test_md_parser.py tests/test_reg_parser.py -v
```

Expected: All tests PASS

---

### Task 2 Step 9: 提交

Run:
```bash
git add nbl-testplan-generator/
git commit -m "$(cat <<'EOF'
feat(parser): implement md_parser, reg_parser and reg_to_json CLI

- md_parser.py: Markdown → spec_tree.json (chapters, features, refs)
- reg_parser.py: xlsx → reg_info.json (registers, fields hierarchy)
- reg_to_json.py: CLI entry point
- Add tests for both parsers
- Fixtures: sample_spec.md, sample_reg.xlsx

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Writer 开发 — combine_writer.py + review_writer.py

**目标:** 实现 xlsx 格式输出和 review.md 输出，带完整测试。

**Files:**
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/writers/combine_writer.py`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/review/review_writer.py`
- Create: `nbl-testplan-generator/tests/test_combine_writer.py`
- Create: `nbl-testplan-generator/tests/test_review_writer.py`

---

### Task 3 Step 1: 编写 combine_writer.py（D-E-F-G 层级写入）

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/writers/combine_writer.py`

```python
#!/usr/bin/env python3
"""combine_writer.py - Write testplan_raw.json → xlsx using template.

Handles D-E-F-G hierarchy, formatting, borders, fonts, J-W path mapping.
"""
from __future__ import annotations

import re
from copy import copy
from pathlib import Path
from typing import Any


def write_testplan_xlsx(
    testplan_data: dict[str, Any],
    template_path: str | Path,
    output_path: str | Path,
    verify_level: str = "BT",
) -> Path:
    """Write testplan JSON data into an xlsx template.

    Parameters
    ----------
    testplan_data : dict
        Must contain: module_name, spec_name, chapter, features[]
        Each feature: feature, feature_id, subfeatures_l1[]
        Each subfeatures_l1: subfeature_l1, subfeatures_l2[]
        Each subfeatures_l2: subfeature_l2, _confidence, subfeatures_l3[]
        Each subfeatures_l3: subfeature_l3, remarks, stimulus, checking,
                             coverage, priority, activity, path
    template_path : str | Path
        Path to testplan_template.xlsx
    output_path : str | Path
        Output xlsx file path
    verify_level : str
        UT / BT / IT / ST / EMU (default BT)

    Returns
    -------
    Path
        Absolute path to the generated output file
    """
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    STD_FONT = Font(name="微软雅黑", size=10)
    RED_FONT = Font(name="微软雅黑", size=10, color="FF0000")
    THIN_BORDER = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    LEFT_ALIGN_VCENTER = Alignment(vertical="center", horizontal="left", wrap_text=True)

    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # Fixed header info per design doc
    # Row 3: plan / Row 4: weight
    # B4: spec name
    ws.cell(row=4, column=2).value = f"{testplan_data.get('module_name', 'module')}_spec"
    # Chapter row marker
    chapter_row = 6  # After template header (~5 rows)

    # Find the actual first empty data row in template
    # Look for first row after row 5 that has empty D column
    data_start_row = _find_data_start_row(ws)

    # Track min/max rows with content for border application
    content_min_row = data_start_row
    content_max_row = data_start_row

    current_row = data_start_row

    # Write B column chapter marker once
    ws.cell(row=current_row, column=2).value = "chapter 1 功能特性"
    _apply_style(ws.cell(row=current_row, column=2), STD_FONT, LEFT_ALIGN_VCENTER)
    current_row += 1

    features = testplan_data.get("features", [])

    for feature in features:
        feat_row = current_row
        # D column: Feature (outline level 0)
        ws.cell(row=current_row, column=4).value = feature.get("feature", "")
        _apply_style(ws.cell(row=current_row, column=4), STD_FONT, LEFT_ALIGN_VCENTER)
        current_row += 1

        for sub_l1 in feature.get("subfeatures_l1", []):
            # E column: Subfeature L1 (outline level 1)
            ws.cell(row=current_row, column=5).value = sub_l1.get("subfeature_l1", "")
            _apply_style(ws.cell(row=current_row, column=5), STD_FONT, LEFT_ALIGN_VCENTER)
            current_row += 1

            for sub_l2 in sub_l1.get("subfeatures_l2", []):
                # F column: Subfeature L2 (outline level 2)
                ws.cell(row=current_row, column=6).value = sub_l2.get("subfeature_l2", "")
                _apply_style(ws.cell(row=current_row, column=6), STD_FONT, LEFT_ALIGN_VCENTER)

                confidence = sub_l2.get("_confidence", "confirmed")
                l3_list = sub_l2.get("subfeatures_l3", [])

                if l3_list:
                    # F is aggregate; data goes on G rows for each L3
                    sub_l2_row = current_row
                    current_row += 1
                    for sub_l3 in l3_list:
                        ws.cell(row=current_row, column=7).value = sub_l3.get("subfeature_l3", "")
                        _write_data_row(ws, current_row, sub_l3, verify_level, confidence, STD_FONT, RED_FONT, LEFT_ALIGN_VCENTER)
                        current_row += 1
                else:
                    # F is minimum granularity, write data columns here
                    sub_l2["subfeature_l3"] = ""  # Ensure field exists for _write_data_row
                    _write_data_row(ws, current_row, sub_l2, verify_level, confidence, STD_FONT, RED_FONT, LEFT_ALIGN_VCENTER)
                    current_row += 1

        content_max_row = max(content_max_row, current_row)

    # Apply borders to A-W for all content rows
    _apply_borders(ws, content_min_row, content_max_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path.resolve()


def _find_data_start_row(ws) -> int:
    """Find the first empty row after the header."""
    for row in range(6, 50):
        if ws.cell(row=row, column=4).value is None or str(ws.cell(row=row, column=4).value).strip() == "":
            return row
    return 6


def _write_data_row(
    ws,
    row: int,
    data: dict,
    verify_level: str,
    confidence: str,
    std_font: Font,
    red_font: Font,
    alignment: Alignment,
) -> None:
    """Write H through W columns for a single data row."""
    is_inferred = confidence == "inferred"
    font = red_font if is_inferred else std_font

    # H: remarks
    ws.cell(row=row, column=8).value = data.get("remarks", "")
    ws.cell(row=row, column=8).font = font
    ws.cell(row=row, column=8).alignment = alignment

    # I: stimulus (【配置】and 【激励】in red)
    stimulus = data.get("stimulus", "")
    ws.cell(row=row, column=9).value = stimulus
    ws.cell(row=row, column=9).font = std_font
    ws.cell(row=row, column=9).alignment = alignment
    _color_stimulus_markers(ws, row, 9, stimulus)

    # J: checking
    ws.cell(row=row, column=10).value = data.get("checking", "by_checker")
    ws.cell(row=row, column=10).font = font
    ws.cell(row=row, column=10).alignment = alignment

    # K: coverage
    ws.cell(row=row, column=11).value = data.get("coverage", "")
    ws.cell(row=row, column=11).font = font
    ws.cell(row=row, column=11).alignment = alignment

    # M: activity (UT/BT/IT/ST/EMU)
    ws.cell(row=row, column=13).value = data.get("activity", verify_level)
    ws.cell(row=row, column=13).font = font
    ws.cell(row=row, column=13).alignment = alignment

    # W: path
    path = data.get("path", "")
    if not path:
        path = _build_path(data, data.get("checking", "by_checker"))
    ws.cell(row=row, column=23).value = path
    ws.cell(row=row, column=23).font = font
    ws.cell(row=row, column=23).alignment = alignment

    # L is intentionally left blank
    # N-P are reserved, left blank

    # U row=4 weight = 5, V row=4 weight = 95 (set once at top, handled below)


def _color_stimulus_markers(ws, row: int, col: int, text: str) -> None:
    """Color 【配置】and 【激励】markers in red, rest in black."""
    # openpyxl does not support rich text in cell values directly.
    # As a practical fallback: if the cell contains these markers,
    # we render the whole cell in red, since openpyxl rich text is limited.
    if "【配置】" in text or "【激励】" in text:
        ws.cell(row=row, column=col).font = Font(name="微软雅黑", size=10, color="FF0000")
    else:
        ws.cell(row=row, column=col).font = Font(name="微软雅黑", size=10)


def _build_path(data: dict, checking: str) -> str:
    """Build the W column path from checking type."""
    # This is a placeholder: ideally eng_feature_id / eng_subfeature_id are provided
    # For now use raw feature/subfeature names or empty
    feature = data.get("_feature_eng", "")
    subfeature = data.get("_subfeature_eng", "")
    if not feature:
        return ""
    module = data.get("_module", "module")
    if checking == "by_checker":
        return f"Group:$unit::{module}_fcov::cg_{feature}.cp_{subfeature}"
    elif checking == "by_direct_tc":
        return f"Group:$unit::{module}_direct_fcov::direct_{feature}_{subfeature}"
    elif checking == "by_assertion":
        return f"Group:$unit::{module}_assert::assert_{feature}_{subfeature}"
    return ""


def _apply_style(cell, font: Font, alignment: Alignment) -> None:
    cell.font = font
    cell.alignment = alignment


def _apply_borders(ws, min_row: int, max_row: int) -> None:
    """Apply thin borders to A-W columns across content rows."""
    from openpyxl.styles import Border, Side
    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    for row in range(min_row, max_row + 1):
        for col in range(1, 24):  # A=1 through W=23
            if ws.cell(row=row, column=col).value is not None:
                ws.cell(row=row, column=col).border = border
            else:
                ws.cell(row=row, column=col).border = border


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 4:
        print("Usage: python combine_writer.py <testplan.json> <template.xlsx> <output.xlsx>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    result = write_testplan_xlsx(data, sys.argv[2], sys.argv[3])
    print(f"Written: {result}")
```

---

### Task 3 Step 2: 编写 review_writer.py

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/review/review_writer.py`

```python
#!/usr/bin/env python3
"""review_writer.py - Write fs_reg_slv_review.md from review items."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def write_review_md(
    review_items: list[dict[str, Any]],
    output_path: str | Path,
    module_name: str = "",
) -> Path:
    """Generate fs_reg_slv_review.md from review items list.

    Parameters
    ----------
    review_items : list
        Each item: {item_id, feature, question, source, status}
    output_path : str | Path
        Path for output markdown file
    module_name : str
        Module name, optional

    Returns
    -------
    Path
        Absolute path to generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    title = f"# {module_name.upper()} FS/REG 审查记录" if module_name else "# FS/REG 审查记录"
    lines.append(title)
    lines.append("")
    lines.append("> 以下条目为功能规格书或寄存器配置手册中未明确体现的内容，需要用户补充确认。" + "\n")
    lines.append("")

    if not review_items:
        lines.append("*未发现需要确认的条目。*\n")
    else:
        for item in review_items:
            item_id = item.get("item_id", "")
            feature = item.get("feature", "")
            question = item.get("question", "")
            source = item.get("source", "")
            status = item.get("status", "pending")

            lines.append(f"## {item_id}: {feature}")
            lines.append("")
            lines.append(f"- **问题**: {question}")
            lines.append(f"- **来源**: {source}")
            lines.append(f"- **确定信息**: [待填写]")
            lines.append(f"- **状态**: {status}")
            lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("\n## 使用说明")
    lines.append("")
    lines.append("1. 阅读每个条目的问题和来源")
    lines.append("2. 在'确定信息'处填写你的确认或补充说明")
    lines.append("3. 将更新后的文件重新输入给本 skill 进行二次刷新，即可更新测试点文档")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path.resolve()


def write_review_from_testplan(testplan_data: dict[str, Any], output_path: str | Path) -> Path:
    """Convenience: extract review_items from testplan_raw.json and write review md."""
    review_items = testplan_data.get("review_items", [])
    module_name = testplan_data.get("module_name", "")
    return write_review_md(review_items, output_path, module_name)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 3:
        print("Usage: python review_writer.py <testplan.json> <output.md>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    result = write_review_from_testplan(data, sys.argv[2])
    print(f"Written: {result}")
```

---

### Task 3 Step 3: 编写 test_combine_writer.py

Create: `nbl-testplan-generator/tests/test_combine_writer.py`

```python
"""Tests for combine_writer module."""
from pathlib import Path

import pytest

from writers.combine_writer import write_testplan_xlsx


class TestWriteTestplanXlsx:
    """Tests for write_testplan_xlsx."""

    def test_creates_file(self, temp_dir, sample_template_xlsx):
        """Should create output xlsx file."""
        data = {
            "module_name": "UPA",
            "spec_name": "UPA_spec",
            "chapter": "chapter 1 功能特性",
            "features": [],
        }
        output = temp_dir / "test_output.xlsx"
        result = write_testplan_xlsx(data, sample_template_xlsx, output)
        assert output.exists()
        assert result == output.resolve()

    def test_writes_feature_in_column_d(self, temp_dir, sample_template_xlsx):
        """Feature name should appear in column D."""
        data = {
            "module_name": "UPA",
            "spec_name": "UPA_spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "报文编辑范围",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [],
                }
            ],
        }
        output = temp_dir / "test_output.xlsx"
        write_testplan_xlsx(data, sample_template_xlsx, output)

        import openpyxl
        wb = openpyxl.load_workbook(output)
        ws = wb.active

        found = False
        for row in range(1, ws.max_row + 1):
            val = ws.cell(row=row, column=4).value
            if val and "报文编辑范围" in str(val):
                found = True
                break
        assert found, "Feature not found in column D"

    def test_writes_subfeature_l1_in_column_e(self, temp_dir, sample_template_xlsx):
        """Subfeature L1 should appear in column E."""
        data = {
            "module_name": "UPA",
            "spec_name": "UPA_spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "报文编辑范围",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "替换动作",
                            "subfeatures_l2": [],
                        }
                    ],
                }
            ],
        }
        output = temp_dir / "test_output.xlsx"
        write_testplan_xlsx(data, sample_template_xlsx, output)

        import openpyxl
        wb = openpyxl.load_workbook(output)
        ws = wb.active

        found = False
        for row in range(1, ws.max_row + 1):
            val = ws.cell(row=row, column=5).value
            if val and "替换动作" in str(val):
                found = True
                break
        assert found, "Subfeature L1 not found in column E"

    def test_data_row_has_borders(self, temp_dir, sample_template_xlsx):
        """Data rows should have thin borders."""
        data = {
            "module_name": "UPA",
            "spec_name": "UPA_spec",
            "chapter": "chapter 1 功能特性",
            "features": [
                {
                    "feature": "F",
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeature_l1": "E",
                            "subfeatures_l2": [
                                {
                                    "subfeature_l2": "F2overview",
                                    "_confidence": "confirmed",
                                    "subfeatures_l3": [
                                        {
                                            "subfeature_l3": "G3detail",
                                            "remarks": "test",
                                            "stimulus": "test",
                                            "checking": "by_checker",
                                            "coverage": "test",
                                            "priority": "HIGH",
                                            "activity": "BT",
                                            "path": "Group:$unit::upa_fcov::cg_f.cp_e",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        output = temp_dir / "test_output.xlsx"
        write_testplan_xlsx(data, sample_template_xlsx, output)

        import openpyxl
        wb = openpyxl.load_workbook(output)
        ws = wb.active

        # Find a data row (one with column H value)
        for row in range(1, ws.max_row + 1):
            if ws.cell(row=row, column=8).value:
                border = ws.cell(row=row, column=4).border
                assert border is not None
                assert border.left.style is not None
                break
        else:
            pytest.fail("No data row found")
```

---

### Task 3 Step 4: 编写 test_review_writer.py

Create: `nbl-testplan-generator/tests/test_review_writer.py`

```python
"""Tests for review_writer module."""
from pathlib import Path

import pytest

from review.review_writer import write_review_md, write_review_from_testplan


class TestWriteReviewMd:
    """Tests for write_review_md."""

    def test_creates_file(self, temp_dir):
        """Should create the output markdown file."""
        output = temp_dir / "review.md"
        result = write_review_md([], output, "UPA")
        assert output.exists()
        assert result == output.resolve()

    def test_outputs_module_title(self, temp_dir):
        """Should include module name in title."""
        output = temp_dir / "review.md"
        write_review_md([], output, "UPA")
        content = output.read_text(encoding="utf-8")
        assert "UPA FS/REG 审查记录" in content

    def test_writes_review_items(self, temp_dir):
        """Should write all review items."""
        items = [
            {
                "item_id": "R1",
                "feature": "报文编辑范围",
                "question": "编辑范围是否支持小于64B的报文？",
                "source": "spec ch3 PA.1",
                "status": "pending",
            }
        ]
        output = temp_dir / "review.md"
        write_review_md(items, output)
        content = output.read_text(encoding="utf-8")
        assert "R1: 报文编辑范围" in content
        assert "编辑范围是否支持小于64B的报文？" in content
        assert "spec ch3 PA.1" in content

    def test_writes_empty_notice(self, temp_dir):
        """Should note when there are no review items."""
        output = temp_dir / "review.md"
        write_review_md([], output)
        content = output.read_text(encoding="utf-8")
        assert "未发现需要确认的条目" in content


class TestWriteReviewFromTestplan:
    """Tests for write_review_from_testplan convenience function."""

    def test_extracts_and_writes(self, temp_dir):
        """Should extract review_items from testplan dict and write."""
        testplan = {
            "module_name": "UPA",
            "review_items": [
                {
                    "item_id": "R1",
                    "feature": "流控",
                    "question": "FIFO深度是多少？",
                    "source": "spec ch3 PA.3",
                    "status": "pending",
                }
            ],
        }
        output = temp_dir / "review.md"
        write_review_from_testplan(testplan, output)
        content = output.read_text(encoding="utf-8")
        assert "FIFO深度是多少？" in content
```

---

### Task 3 Step 5: 运行全部 Writer 测试

Ensure `cd nbl-testplan-generator` and run:
```bash
python -m pytest tests/test_combine_writer.py tests/test_review_writer.py -v
```

Expected: All tests PASS

---

### Task 3 Step 6: 提交

Run:
```bash
git add nbl-testplan-generator/
git commit -m "$(cat <<'EOF'
feat(writer): implement combine_writer and review_writer

- combine_writer.py: testplan_func_raw.json → xlsx (D-E-F-G hierarchy,
  borders, fonts, J-W path mapping, stimulus coloring)
- review_writer.py: review_items → fs_reg_slv_review.md
- Add tests for both writers

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Skill 完善 — SKILL.md 完整指令与集成

**目标:** 编写完整的 SKILL.md，包含所有 9 个阶段的详细交互指令和 Claude prompt。

**Files:**
- Rewrite: `nbl-testplan-generator/skills/nbl-tp-func-gen/SKILL.md`
- Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/tp_gen.py`（预留 CLI 入口）

---

### Task 4 Step 1: 重写 SKILL.md — 完整交互流程

Rewrite: `nbl-testplan-generator/skills/nbl-tp-func-gen/SKILL.md`

内容必须完整覆盖 design doc 中所有要求。由于 SKILL.md 很长，按以下章节结构编写：

1. Frontmatter (name, description)
2. System Role（资深数字芯片验证工程师角色定义）
3. Task Description
4. Input Requirements（用户必须提供的输入）
5. Phase-by-phase Execution（9 个阶段的详细指令）
6. JSON Output Schema（_confidence, path 英文映射规则）
7. xlsx Format Rules（D-E-F-G, J-W, border/font/color）
8. Review Rules（不擅自推理，记录不确定项）
9. Error Handling（文件不存在、格式错误等）

> **注意:** SKILL.md 正文是 Claude 执行时读取的指令，不是给用户看的文档。它应该包含详细的 prompt 级指令。

具体 SKILL.md 内容参考 design doc 第6章，并且必须：
- 包含 D-E-F-G 层级展开的具体规则
- 包含 J-W 路径映射规则（使用英文标识符）
- 包含 `【配置】` / `【激励】` 必须标红的要求
- 包含 `_confidence: inferred` 标注 `⚠ [推断]` 的要求
- 包含 `fs_reg_slv_review.md` 的结构模板
- 包含流水线交互模式的说明

---

### Task 4 Step 2: 编写 tp_gen.py CLI 入口（预留）

Create: `nbl-testplan-generator/skills/nbl-tp-func-gen/scripts/tp_gen.py`

```python
#!/usr/bin/env python3
"""tp_gen.py - Unified CLI entry point for testplan generation pipeline.

Reserved for future use. Currently SKILL.md orchestrates the pipeline.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def resolve_path(path_str: str) -> Path:
    """Resolve a path, supporting $TP_WORKDIR."""
    path_str = os.path.expandvars(path_str)
    path_str = os.path.expanduser(path_str)
    return Path(path_str).resolve()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Testplan Generation Pipeline")
    parser.add_argument("spec_docx", help="Functional spec .docx path")
    parser.add_argument("reg_xlsx", help="Register xlsx path")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory")
    parser.add_argument("-l", "--level", default="BT", choices=["UT", "BT", "IT", "ST", "EMU"])
    args = parser.parse_args(argv)

    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Pipeline not yet implemented via CLI.")
    print(f"Please use the SKILL.md workflow (nbl-tp-func-gen skill).")
    print(f"Output directory would be: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### Task 4 Step 3: 验证 SKILL.md 结构

Run:
```bash
cd nbl-testplan-generator
# Check frontmatter is valid
head -5 skills/nbl-tp-func-gen/SKILL.md
```

Expected: `---` block with `name: nbl-tp-func-gen` and `description:`

---

### Task 4 Step 4: 提交

Run:
```bash
git add nbl-testplan-generator/
git commit -m "$(cat <<'EOF'
feat(skill): complete SKILL.md with full orchestration and tp_gen CLI

- SKILL.md: 9-stage pipeline with complete Claude instructions
- System prompt integration, D-E-F-G rules, J-W path mapping
- Review record format, interactive pipeline mode
- tp_gen.py: unified CLI entry point (reserved)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: 验证与收尾 — 端到端测试 + 文档

**目标:** 使用 UPA 案例进行端到端验证，修复问题，更新 README 和 marketplace。

**Files:**
- Rewrite: `nbl-testplan-generator/README.md`
- Check: `.claude-plugin/marketplace.json`
- Check: Root `README.md`

---

### Task 5 Step 1: UPA 案例端到端验证

验证流程（手动阶段，Claude 作为执行者）：

1. 确认模板已复制：`nbl-testplan-generator/skills/nbl-tp-func-gen/reference/template/testplan_template.xlsx`
2. 使用 `nbl-docx-to-markdown` skill 转换 UPA docx 为 md
3. 运行 md_parser.py 得到 spec_tree.json
4. 运行 reg_to_json.py 得到 reg_info.json
5. Claude 分析这两个 JSON 生成 testplan_func_raw.json
6. 运行 combine_writer.py 生成 testplan.xlsx
7. 检查输出：
   - D-E-F-G 层级正确
   - 边框完整
   - 字体正确（微软雅黑 10pt）
   - J-W 关系正确
   - 无 placeholder / TODO 遗留

Run parser end-to-end:
```bash
cd nbl-testplan-generator
# Use nbl-docx-to-markdown skill output, or fallback to sample_spec.md fixture
python skills/nbl-tp-func-gen/scripts/parsers/md_parser.py tests/fixtures/sample_spec.md > /tmp/spec_tree.json
python skills/nbl-testplan-generator/scripts/reg_to_json.py /path/to/Leonis_datapath_upa.xlsx -o /tmp/reg_info.json
```

---

### Task 5 Step 2: 修复已知问题

通过端到端验证可能发现的问题：
- md_parser 的交叉引用匹配不准确 → 调整关键词提取 / 章节分类
- reg_parser 的 sheet 识别失败 → 更新 skip_sheets 或 header detection
- combine_writer 的行号偏移问题 → 调整 data_start_row detection
- 边框应用不完整 → 确认 _apply_borders 逻辑
- 字体非微软雅黑（openpyxl 在 Linux 上可能缺少字体）→ 确认 Font(name=...) 设置正确

修复后立即运行相关测试：
```bash
python -m pytest tests/ -v
```

---

### Task 5 Step 3: 更新 README.md

Rewrite: `nbl-testplan-generator/README.md`

```markdown
# nbl-testplan-generator

数字芯片验证测试计划生成器插件。

## 功能

从功能规格书（.docx）和寄存器配置手册（.xlsx）生成结构化测试点 xlsx 文档，支持 `D→E→F→G` 层级分解和自动交叉引用寄存器配置信息。

### 核心特性

- **文档转换**: 调用 `nbl-docx-to-markdown skill` 转换 docx 为 Markdown
- **结构化解析**: Markdown → `spec_tree.json`，含章节树、模块特性和交叉引用索引
- **寄存器解析**: xlsx → `reg_info.json`，层级化寄存器/字段结构
- **智能分析**: Claude 按 Feature 分块分析，自动交叉引用规格书和寄存器配置
- **标准输出**: 符合 `testplan_template.xlsx` 格式的 xlsx，含边框、字体、层级
- **审查记录**: 生成 `fs_reg_slv_review.md` 记录不确定内容，支持二次刷新

## 已包含技能

### nbl-tp-func-gen

生成功能特性（Chapter 1）测试点，详见 `skills/nbl-tp-func-gen/SKILL.md`。

## 使用方法

```bash
#  Claude Code 中触发
/nbl-tp-func-gen 从 /path/to/spec.docx 和 /path/to/reg.xlsx 生成测试点
```

## 依赖

- Python >= 3.12
- openpyxl >= 3.1.0
- pytest >= 8.0.0（开发）
- LibreOffice + Pandoc（通过 nbl-docx-to-markdown）

## 目录结构

```
nbl-testplan-generator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── nbl-tp-func-gen/
│       ├── SKILL.md
│       ├── reference/
│       │   ├── spec_input/
│       │   └── template/
│       └── scripts/
│           ├── parsers/
│           ├── writers/
│           ├── review/
│           ├── reg_to_json.py
│           └── tp_gen.py
└── tests/
```

## 测试

```bash
cd nbl-testplan-generator
pytest tests/ -v
```
```

---

### Task 5 Step 4: 检查 marketplace.json

确认 `.claude-plugin/marketplace.json` 中 `nbl-testplan-generator` 条目正确：

```json
{
  "name": "nbl-testplan-generator",
  "source": "./nbl-testplan-generator",
  "description": "数字芯片验证测试计划生成器...",
  "category": "development",
  "tags": ["testplan", "verification", "chip", "document"],
  "keywords": ["testplan", "verification", "chip", "docx", "xlsx", "test", "generator"]
}
```

---

### Task 5 Step 5: 最终提交

Run:
```bash
git add nbl-testplan-generator/ .claude-plugin/marketplace.json README.md
git commit -m "$(cat <<'EOF'
feat: complete nbl-tp-func-gen skill with E2E validation

- Parser + Writer + Review 组件完成并通过测试
- SKILL.md 完整交互指令覆盖 9 阶段流水线
- README.md 完整使用说明
- 验证通过 UPA 案例

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## 自检清单（Spec Coverage）

| Design Doc 章节 | 对应 Task | 状态 |
|------------------|----------|------|
| 2. 目录结构      | Task 1   | ✅ 覆盖 |
| 4.1 spec_tree.json schema | Task 2 | ✅ 覆盖 |
| 4.2 reg_info.json schema  | Task 2 | ✅ 覆盖 |
| 4.3 testplan_raw.json schema | Task 3 + 4 | ✅ 覆盖 |
| 5. xlsx 输出规范（格式/font/border） | Task 3 | ✅ 覆盖 |
| 5.3 D-E-F-G层级 | Task 3 | ✅ 覆盖 |
| 5.4 J-W关系    | Task 3 + 4 | ✅ 覆盖 |
| 6. SKILL.md交互流程 | Task 4 | ✅ 覆盖 |
| 7. 脚本设计     | Task 2 + 3 | ✅ 覆盖 |
| 9. 移植性($TP_WORKDIR) | Task 1 + 4 | ✅ 覆盖 |
| 10. 验证策略    | Task 5 | ✅ 覆盖 |

---

## 执行方式选择

**方案一：Subagent-Driven（推荐）** — 每 Task 分配一个新鲜 subagent，减少上下文爆炸，每个 subagent 只专注少量文件。

**方案二：Inline Execution** — 在当前 session 中逐 step 执行，由我直接编辑文件、运行测试。

> 设计文档中列出的 5 个 Subagent 对应本计划的 5 个 Task。推荐按 Task 逐个执行，每个 Task 完成后 review 再进入下一个。
