---
name: nbl-testplan-generator
description: Generate structured test point documents (.xlsx) for digital chip verification from functional specification (.docx) and register configuration (.xlsx). Supports hierarchical decomposition (D-E-F/G), Chapter 1 功能特性, Chapter 2 配置特性, outline grouping, and review-based refresh workflow.
---

# Test Plan Generator for Digital Chip Verification

## Overview

Generate structured test point documents for digital chip verification from functional specifications and register manuals. Uses multi-stage pipeline: parse documents to JSON, cross-reference features with registers, generate hierarchical test points (D-E-F/G), write xlsx with outline grouping, and produce review reports for document gaps.

## When to Use

**Use when:**
- Generating test points from functional specification (.docx) and register manual (.xlsx)
- Need structured hierarchical test coverage (D-E-F/G) with Chapter 1 (功能特性) and Chapter 2 (配置特性)
- Refreshing test points based on user-confirmed review feedback

**Don't use when:**
- Source documents are not .docx/.xlsx format
- Need simple test lists without hierarchy
- User wants only register-level documentation (not test points)

## Arguments

- `$ARGUMENTS` — positional args and options

## Instructions

### Critical Rules (Read Before Acting)

**Multi-stage process is REQUIRED. DO NOT skip stages. DO NOT combine steps.**

### Step 1: Parse Arguments

Parse `$ARGUMENTS` to extract:

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `spec_path` | Yes | — | Path to functional specification .docx |
| `reg_path` | Yes | — | Path to register configuration .xlsx |
| `--output` | No | spec同目录 | Output path for generated .xlsx |
| `--sample` | No | — | Reference testpoint .xlsx for style and incremental append |
| `--level` | No | BT | Verification level: UT/BT/IT/ST/EMU |
| `--mode` | No | batch | Processing mode: single/batch |
| `--features` | No | all | Comma-separated feature IDs to process |
| `--module` | No | from spec filename | Module name |
| `--refresh-review` | No | — | Path to review .md for refresh mode |

**VIOLATION:** If `spec_path` or `reg_path` is missing, ASK the user. Do not guess.
**VIOLATION:** If `--output` uses default, INFORM the user of the final path before proceeding.

**Work directory for intermediate files:**

After resolving `--output`, derive the intermediate files directory:

```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
if ! mkdir -p "$TP_WORKDIR" 2>/dev/null; then
    TP_WORKDIR="$HOME/.tp_cache"
    mkdir -p "$TP_WORKDIR" 2>/dev/null
    echo "⚠ 输出目录无写权限，中间文件将保存到 $TP_WORKDIR"
fi
echo "中间文件目录: $TP_WORKDIR"
```

**Fallback chain:** `{output_dir}/.tp_cache/` → `~/.tp_cache/`

All subsequent steps use `$TP_WORKDIR` for intermediate JSON files (parsed data, Ch1 features, review data).

### Step 2: Parse Documents (Stage 1)

**Convert spec.docx to Markdown using nbl-docx-to-markdown skill:**

```
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

This creates `$TP_WORKDIR/<basename>_work/markdown_output/<basename>.md`.

**Set spec_md path:**
```
spec_basename=$(basename "$spec_path" .docx)
spec_md="$TP_WORKDIR/${spec_basename}_work/markdown_output/${spec_basename}.md"
```

**Parse Markdown and register files:**

```bash
cd ${CLAUDE_SKILL_DIR} && uv run python parsers/md_parser.py "$spec_md" "$TP_WORKDIR/tp_docx_parsed.json"
```

```bash
cd ${CLAUDE_SKILL_DIR} && uv run python parsers/reg_parser.py "$reg_path" "$TP_WORKDIR/tp_reg_parsed.json"
```

If `--sample` provided:
```bash
cd ${CLAUDE_SKILL_DIR} && uv run python parsers/sample_parser.py "$sample_path" "$TP_WORKDIR/tp_sample_parsed.json"
```

After parsing, read the JSON output files to understand document structure.

### Step 3: Cross-Reference Analysis (Stage 2)

Analyze parsed data in conversation:

1. From `docx_parsed.json`, find "模块特性" section and list all Feature IDs (e.g., 【PA.XXX】)
2. For each Feature ID, find corresponding content in "功能详述" section
3. Cross-reference register names in descriptions with `reg_parsed.json`
4. Extract related parameters and constraints
5. Build feature_map: `Feature ID -> {description, functional_details, related_registers, parameters, constraints, potential_issues}`

If `--features` specified, filter to only those IDs.

### Step 4: Generate Chapter 1 Test Points (Stage 3)

For each module feature, generate test points:

1. Read prompt template at `${CLAUDE_SKILL_DIR}/templates/tp_prompt.md`
2. Fill template with feature-specific data
3. Generate D-E-F/G hierarchical test points as JSON following this schema:

```json
{
  "module_name": "UPA",
  "spec_name": "文档名",
  "chapter": "chapter 1 功能特性",
  "features": [
    {
      "feature": "顶层特性名（D列）",
      "feature_id": "PA.XXX",
      "chapter": "chapter 1 功能特性",
      "subfeatures_l1": [
        {
          "subfeature_l1": "一级子特性名（E列）",
          "subfeatures_l2": [
            {
              "subfeature_l2_overview": "概述（F列，简短）",
              "subfeature_l2_detail": "详细规格（G列，可留空）",
              "remarks": "来源: PA.XXX",
              "stimulus": "【配置】...\n【激励】...",
              "checking": "by_checker/by_direct_tc/by_assertion",
              "coverage": "covergroup抽象表达",
              "priority": "HIGH/MID/LOW",
              "activity": "BT",
              "path": "覆盖率仓路径"
            }
          ]
        }
      ]
    }
  ]
}
```

**Critical rules for generation:**
- D-E-F/G is strict hierarchy, each level occupies its own row
- G column is optional — leave empty if D+E+F is sufficient
- stimulus must reference specific register names and fields
- coverage must consider cross scenarios
- Do NOT fabricate registers or parameters — mark uncertain ones with `⚠ [推断]`
- Every feature must cover: normal, boundary, and error scenarios
- After generating each feature, immediately append to xlsx to prevent data loss

**Decomposition dimensions:**
- Function: each independent operation
- Scenario: normal/boundary/error
- Configuration: mode field enums, enable/disable combinations
- Interaction: multi-action combinations, cross-module scenarios

**Mode control:**
- `single`: After each feature, show summary and ask user whether to continue
- `batch`: Process all features continuously, summarize at end

### Step 5: Generate Chapter 2 Configuration Coverage (Stage 4)

From `reg_parsed.json`, generate register-level test points using `combine_writer.py`:

1. The `combine_writer.py` handles:
   - Filter: exclude int/car_ctrl/fifo_th/spare/cnt/fifo_status/fsm/bp/test/init registers
   - Group: merge numbered variants (_0/_1/_2 → base_0/1/2)
   - Cross-ref: check covered_regs mapping from Chapter 1
     - If already covered -> A="skip", H="寄存器描述 【已在功能特性 [PA.XXX] 中覆盖】", I/J/K copy from Ch1
     - If not covered -> I=【配置】auto-generated from RW field info, W="【反标路径暂无法确定】"
   - H column: always include register/field description from manual
   - F column: empty (D+E columns express register+field)
   - Only RW/RWW fields (skip ro/rwc/rctr/sctr/rc/rsv)
2. Run `validate_jw_correspondence` on Ch1 data to auto-correct J-W paths for by_direct_tc and by_assertion checking types

### Step 6: Write Output (Stage 5)

After generating Ch1 test points:

1. Save Ch1 features JSON to `$TP_WORKDIR/tp_ch1_features.json`

2. Run combine_writer (handles Ch2 + merge + xlsx write in one command):
```bash
cd ${CLAUDE_SKILL_DIR} && uv run python writers/combine_writer.py \
  --ch1 "$TP_WORKDIR/tp_ch1_features.json" \
  --reg "$TP_WORKDIR/tp_reg_parsed.json" \
  --output "$output_path" \
  --template ${CLAUDE_SKILL_DIR}/templates/testplan_template.xlsx
```

3. Write review (if any issues found):
```bash
cd ${CLAUDE_SKILL_DIR} && uv run python review/review_writer.py "$TP_WORKDIR/tp_review_data.json" "$review_output_path"
```
Review file defaults to `<output_dir>/fs_reg_slv_review.md`.

The pipeline handles:
- Ch2 register filtering and grouping (combine_writer)
- Cross-reference with Ch1 for skip marking
- J-W correspondence validation (by_direct_tc/by_assertion path auto-generation)
- xlsx_writer formatting: 微软雅黑 10号字体, 红色字体 for ⚠/【配置】, 矩形边框 A-W, 自动换行

### Step 7: Refresh Mode (Optional)

If `--refresh-review` is provided:

1. Parse the review file to extract user resolutions
2. For each resolved issue:
   - "确认" -> remove ⚠ marker, convert to formal test point
   - "否定" -> delete the inferred test point
   - "部分确认 + details" -> modify test point per details
3. Regenerate testpoint xlsx + new review (only unresolved issues)

### Step 8: Report Results

Report to user:
- Number of Chapter 1 features processed and test points generated
- Number of Chapter 2 registers covered (rw/rww) vs skipped
- Output file locations (xlsx + review md)
- Summary table of features and test point counts
- List of review issues (if any)

**Cleanup intermediate files:**

After reporting results, ask the user:
"中间文件保存在 `$TP_WORKDIR`，是否清除？"
- User confirms → `rm -rf "$TP_WORKDIR"`
- User declines → inform user: "中间文件保留在 `$TP_WORKDIR`，可手动删除"

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Skipping parsing stage | Direct LLM extraction loses structure | Use parsers |
| Flattening hierarchy | D-E-F/G structure is mandatory | Each level = own row |
| Ignoring sample reference | Sample provides format/style hints | Parse sample first |
| Fabricating registers | Registers must exist in manual | Mark with ⚠ [推断] |
| Forgetting Chapter 2 | Register coverage is required | Always generate ch2 |
| Using merge for outline | Cell merging != row grouping | Use outline_level |
| Writing stimuli for all ch2 | Config features don't always need stimuli | Mainly 【配置】 |
| Including readonly fields in ch2 | Only rw/rww belong in config coverage | Filter by access type |
| Writing ad-hoc Python scripts for combining JSON | combine_writer handles all Ch2 logic | Use combine_writer CLI |
| Forgetting cell formatting | xlsx_writer applies borders/alignment automatically | Verify output |
| J-W column mismatch | by_direct_tc needs direct_fcov path, by_assertion needs assert path | Use validate_jw_correspondence |
| Fabricating spec info | Must not invent non-existent data | Use ⚠ [推断] or omit entirely |
| Creating temp scripts | All logic consolidated in combine_writer/xlsx_writer | Use existing CLI modules |
| Hardcoding /tmp for intermediate files | /tmp may have permission issues or be cleared unpredictably | Use $TP_WORKDIR derived from output path |

## Red Flags — STOP and Fix

- "I can read the docx directly" -> NO. Use parsers
- "The hierarchy is too complex" -> NO. D-E-F/G is mandatory
- "I'll skip Chapter 2" -> NO. Register coverage is required
- "I'll merge cells for grouping" -> NO. Use outline_level
- "I can guess the output path" -> INFORM user, don't guess
- "This register field must exist" -> If not in parsed data, mark ⚠ [推断]
