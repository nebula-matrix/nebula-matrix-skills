---
name: nbl-testplan-generator
description: 从功能规格书和寄存器手册生成完整测试点文档（xlsx）。自动调用testplan-func生成Ch1功能特性，然后调用testplan-cfg生成Ch2配置特性，最终合并输出。支持层级分解（D-E-F/G）、outline分组。触发：生成测试点、testplan、验证计划。
---

# Test Plan Generator - Full Pipeline Orchestration

## Overview

Generate complete test point documents by orchestrating two sub-skills:
1. **testplan-func**: Generate Chapter 1 (功能特性) from functional specification
2. **testplan-cfg**: Generate Chapter 2 (配置特性) from register manual

This skill orchestrates the full pipeline: parse documents, generate Ch1 features, generate Ch2 config, combine into final xlsx.

## When to Use

**Use when:**
- Generating complete test plan from functional specification + register manual
- Need both Ch1 (functional) and Ch2 (configuration) features
- Want automated pipeline without manual sub-skill invocation

**Don't use when:**
- Only need functional features (use testplan-func directly)
- Only need configuration features (use testplan-cfg directly)
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

## Architecture

```
nbl-testplan-generator (Orchestrator)
    |
    +-- Step 1: testplan-func (Skill tool)
    |       Parse spec -> Generate Ch1 features JSON
    |
    +-- Step 2: testplan-cfg (Skill tool)
    |       Parse registers -> Cross-ref Ch1 -> Generate Ch2
    |
    +-- Step 3: combine_writer.py
            Combine Ch1 + Ch2 -> Output xlsx
```

## Instructions

### Step 1: Parse Arguments

If `spec_path` or `reg_path` is missing, ASK the user.

Set `$TP_WORKDIR`:
```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
mkdir -p "$TP_WORKDIR" 2>/dev/null || TP_WORKDIR="$HOME/.tp_cache"
echo "Working directory: $TP_WORKDIR"
```

### Step 2: Convert Document (if .docx)

If `spec_path` ends with `.docx`, convert to markdown:

```
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

Set `spec_md`:
```bash
spec_basename=$(basename "$spec_path" .docx)
spec_md="$TP_WORKDIR/${spec_basename}_work/markdown_output/${spec_basename}.md"
```

If `spec_path` ends with `.md`:
```bash
spec_md="$spec_path"
```

### Step 3: Generate Ch1 (Functional Features)

Invoke testplan-func skill:

```
Invoke Skill tool with:
  skill: "nbl-testplan-generator:testplan-func"
  args: "$spec_md $reg_path --output $TP_WORKDIR/func_output.xlsx"
```

This generates:
- `$TP_WORKDIR/func_output.xlsx` - Ch1 output
- `$TP_WORKDIR/func_features.json` - Ch1 features data

### Step 4: Generate Ch2 (Configuration Features)

Invoke testplan-cfg skill in incremental mode:

```
Invoke Skill tool with:
  skill: "nbl-testplan-generator:testplan-cfg"
  args: "$reg_path --output $output_path --func-xlsx $TP_WORKDIR/func_output.xlsx"
```

This generates:
- Final output xlsx with Ch1 + Ch2 combined
- Cross-references covered registers

### Step 5: Validate Output (Optional)

```bash
cd ${CLAUDE_SKILL_DIR}/scripts/writers && uv run python -c "
from combine_writer import validate_jw_correspondence
import json

# Load and validate
with open('$TP_WORKDIR/func_features.json') as f:
    ch1_data = json.load(f)

validate_jw_correspondence(ch1_data)
print('J-W correspondence validated')
"
```

### Step 6: Report Results

Report to user:
- Output file location
- Ch1 statistics: features, subfeatures count
- Ch2 statistics: registers, covered count, new count
- Summary table

**Cleanup intermediate files:**

Ask the user: "中间文件保存在 `$TP_WORKDIR`，是否清除？"
- User confirms -> `rm -rf "$TP_WORKDIR"`
- User declines -> "中间文件保留在 `$TP_WORKDIR`，可手动删除"

## XLSX Output Structure

Final xlsx contains two chapters:

**Chapter 1 (功能特性):**
- D column: Feature name (outline_level 0)
- E column: Subfeature L1 (outline_level 1)
- F column: Subfeature L2 overview (outline_level 2)
- G column: Subfeature L2 detail (outline_level 3)
- H-W columns: Test point attributes

**Chapter 2 (配置特性):**
- D column: Register name
- E column: Subfeature L1
- F-W columns: Configuration test attributes
- Skip marking for registers covered in Ch1

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| spec_path not found | File doesn't exist | Ask user for correct path |
| reg_path not found | File doesn't exist | Ask user for correct path |
| docx conversion failed | nbl-docx-to-markdown error | Check document format |
| Ch1 generation failed | Parsing or LLM error | Check spec structure |
| Ch2 generation failed | Register parsing error | Check register manual format |

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Skipping Ch2 | Configuration coverage is required | Always run both skills |
| Manual JSON editing | Use combine_writer.py | Automate the process |
| Forgetting cleanup | Intermediate files accumulate | Ask user about cleanup |
| Wrong output path | May not have write permission | Use spec directory as default |
