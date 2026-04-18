---
name: testplan-func
description: 从功能规格书（.docx）和寄存器手册（.xlsx）生成功能特性测试点（xlsx）。输入spec_path + reg_path，输出 D-E-F/G 层级测试计划。触发：生成功能测试点、验证计划、testplan。
---

# Test Plan Generator - Functional Features

## Overview

Generate Chapter 1 (功能特性) test points from functional specification and register manual.

## When to Use

**Use when:**
- Generating functional test points from .docx specification + .xlsx register manual
- Need structured hierarchical test coverage (D-E-F/G)

**Don't use when:**
- Only need register configuration coverage (use testplan-cfg instead)
- Source documents are not .docx/.xlsx format

## Arguments

Parse `$ARGUMENTS`:
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `spec_path` | Yes | — | Path to functional specification .docx |
| `reg_path` | Yes | — | Path to register configuration .xlsx |
| `--output` | No | spec同目录 | Output path for generated .xlsx |
| `--sample` | No | — | Reference testpoint .xlsx for style |
| `--features` | No | all | Comma-separated feature IDs |

## XLSX Column Hierarchy

测试点输出xlsx采用层级结构：
- **D列**: 特性名 (outline_level 0)
- **E列**: 子特性L1 (outline_level 1)
- **F列**: 子特性L2概述 (outline_level 2) — **主层级**
- **G列**: 子特性L2详情 — **从层级** (一个F可对应多个G)
- **H列**: 备注 — 基于G列
- **I列**: 激励 — 基于G列
- **J列**: 检查 — 基于G列
- **K列**: 覆盖 — 基于G列
- **L列**: 优先级 — 基于G列
- **M列**: 活动 — 基于G列
- **W列**: 路径 — 基于G列

**F-G主从关系**: 一个F列条目可划分为若干个G列条目，H-W列都是G列的属性。

## Instructions

### Step 1: Parse Arguments

If `spec_path` or `reg_path` is missing, ASK the user.

Set `$TP_WORKDIR`:
```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
mkdir -p "$TP_WORKDIR" 2>/dev/null || TP_WORKDIR="$HOME/.tp_cache"
```

### Step 2: Document Conversion

**Use Skill tool to invoke nbl-docx-to-markdown:**
```
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

This will create `$TP_WORKDIR/<basename>_work/markdown_output/<basename>.md`.

**Set spec_md path:**
```
spec_basename=$(basename "$spec_path" .docx)
spec_md="$TP_WORKDIR/${spec_basename}_work/markdown_output/${spec_basename}.md"
```

**Run reg_to_json.py:**
```bash
cd ${CLAUDE_SKILL_DIR}/../nbl-testplan-generator/scripts && uv run python reg_to_json.py "$reg_path" "$TP_WORKDIR/reg.json"
```

### Step 3: Cross-Reference Analysis

1. From spec.md, find "模块特性" section, list Feature IDs (【PA.XXX】)
2. From reg.json, extract register name_index
3. For each feature, extract functional details
4. Build feature_map with related registers

### Step 4: Generate Features

Read template at `${CLAUDE_SKILL_DIR}/templates/func_prompt.md`

Generate D-E-F/G JSON for each feature:
```json
{
  "module_name": "UPA",
  "spec_name": "文档名",
  "chapter": "chapter 1 功能特性",
  "features": [...]
}
```

Save to `$TP_WORKDIR/func_features.json`

### Step 5: Write Output

```bash
cd ${CLAUDE_SKILL_DIR}/../nbl-testplan-generator/scripts && uv run python func_writer.py \
  --func "$TP_WORKDIR/func_features.json" \
  --output "$output_path" \
  --template ${CLAUDE_SKILL_DIR}/../nbl-testplan-generator/templates/testplan_template.xlsx
```

### Step 6: Report

Report to user:
- Number of features processed
- Output file location
- Summary table
