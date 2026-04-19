---
name: testplan-func
description: 从功能规格书（.docx/.md）和寄存器手册（.xlsx）生成功能特性测试点（xlsx）。输入spec_path + reg_path，输出 D-E-F-G 层级测试计划，G列在outline_level 3，H-W列仅在最小粒度行。触发：生成功能测试点、验证计划、testplan。
---

# Test Plan Generator - Functional Features (Chapter 1)

## Overview

Generate Chapter 1 (功能特性) test points from functional specification and register manual. Outputs a structured xlsx with D-E-F-G hierarchy where G is at outline_level 3 and H-W columns appear only at minimum granularity rows.

## When to Use

**Use when:**
- Generating functional test points from .docx/.md specification + .xlsx register manual
- Need structured hierarchical test coverage (D-E-F-G)

**Don't use when:**
- Only need register configuration coverage (use testplan-cfg instead)
- Source documents are not .docx/.xlsx/.md format

## Arguments

Parse `$ARGUMENTS`:
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `spec_path` | Yes | — | Path to functional specification (.docx or .md) |
| `reg_path` | Yes | — | Path to register configuration .xlsx |
| `--output` | No | spec同目录 | Output path for generated .xlsx |
| `--sample` | No | — | Reference testpoint .xlsx for style |
| `--features` | No | all | Comma-separated feature IDs |

## XLSX Column Hierarchy

测试点输出xlsx采用层级结构，使用Excel outline_level实现分组：
- **D列**: 特性名 (outline_level 0)
- **E列**: 子特性L1 (outline_level 1)
- **F列**: 子特性L2概述 (outline_level 2)
- **G列**: 子特性L2详情 (outline_level 3) — **最小粒度**
- **H-W列**: 仅在最小粒度行（G存在则G行，否则F行）

**F-G主从关系**: 一个F列条目可划分为若干个G列条目，H-W列都是最小粒度行的属性。

## Instructions

### Step 1: Parse Arguments

If `spec_path` or `reg_path` is missing, ASK the user.

Determine input type:
```bash
if [[ "$spec_path" == *.docx ]]; then
  INPUT_TYPE="docx"
elif [[ "$spec_path" == *.md ]]; then
  INPUT_TYPE="md"
else
  echo "Error: spec_path must be .docx or .md"
  exit 1
fi
```

Set `$TP_WORKDIR`:
```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
mkdir -p "$TP_WORKDIR" 2>/dev/null || TP_WORKDIR="$HOME/.tp_cache"
```

### Step 2: Document Conversion

**If INPUT_TYPE is "docx":**

Use Skill tool to invoke nbl-docx-to-markdown:
```
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

This creates `$TP_WORKDIR/<basename>_work/markdown_output/<basename>.md`.

Set spec_md path:
```bash
spec_basename=$(basename "$spec_path" .docx)
spec_md="$TP_WORKDIR/${spec_basename}_work/markdown_output/${spec_basename}.md"
```

**If INPUT_TYPE is "md":**
```bash
spec_md="$spec_path"
spec_basename=$(basename "$spec_path" .md)
```

### Step 3: Parse Documents

**Parse Markdown specification:**
```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python md_parser.py "$spec_md" "$TP_WORKDIR/spec_parsed.json"
```

**Parse Register xlsx:**
```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python reg_to_json.py "$reg_path" "$TP_WORKDIR/reg.json"
```

### Step 4: Cross-Reference Analysis

1. Read `$TP_WORKDIR/spec_parsed.json` to understand document structure
2. From spec_parsed.json, find "模块特性" section, list Feature IDs (【PA.XXX】)
3. From reg.json, extract register name_index
4. For each feature, extract functional details
5. Build feature_map with related registers

### Step 5: Generate Features

Read template at `${CLAUDE_SKILL_DIR}/templates/func_prompt.md`

Generate D-E-F/G JSON for each feature following this schema:
```json
{
  "module_name": "UPA",
  "spec_name": "文档名",
  "chapter": "chapter 1 功能特性",
  "features": [
    {
      "feature": "顶层特性名（D列）",
      "feature_id": "PA.XXX",
      "subfeatures_l1": [
        {
          "subfeature_l1": "一级子特性（E列）",
          "subfeatures_l2": [
            {
              "subfeature_l2_overview": "二级概述（F列）",
              "subfeature_l2_detail": "二级详细（G列，可留空）",
              "remarks": "来源: PA.XXX",
              "stimulus": "【配置】...\n【激励】...",
              "checking": "by_checker/by_direct_tc/by_assertion",
              "coverage": "covergroup抽象",
              "priority": "HIGH/MID/LOW",
              "activity": "BT",
              "path": "覆盖率路径"
            }
          ]
        }
      ]
    }
  ]
}
```

**Critical rules:**
- D-E-F-G is strict hierarchy, each level occupies its own row
- G column (subfeature_l2_detail) is optional — leave empty if D+E+F is sufficient
- H-W columns only at minimum granularity (G row if G exists, else F row)
- stimulus must reference specific register names and fields
- Do NOT fabricate registers — mark uncertain ones with `⚠ [推断]`

Save to `$TP_WORKDIR/func_features.json`

### Step 6: Write Output

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python xlsx_writer.py \
  "$TP_WORKDIR/func_features.json" \
  "${CLAUDE_SKILL_DIR}/../nbl-testplan-generator/templates/testplan_template.xlsx" \
  "$output_path"
```

### Step 7: Validate Output (Optional)

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python validator.py \
  --xlsx "$output_path" \
  --json "$TP_WORKDIR/func_features.json"
```

### Step 8: Report

Report to user:
- Number of features processed
- Output file location
- Summary table

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Skipping parsing stage | Direct LLM extraction loses structure | Use md_parser.py |
| H-W at D/E level | H-W only at minimum granularity | Check G/F level |
| Forgetting outline levels | Excel grouping requires outline_level | Use xlsx_writer.py |
| Fabricating registers | Must not invent non-existent data | Mark with ⚠ [推断] |
