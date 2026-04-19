---
name: testplan-cfg
description: 从寄存器手册生成配置特性测试点。支持独立模式（仅Ch2）和增量模式（追加到func_xlsx）。输入reg_path，可选func_xlsx。触发：生成配置测试点、寄存器覆盖、testplan cfg。
---

# Test Plan Generator - Configuration Features (Chapter 2)

## Overview

Generate Chapter 2 (配置特性) test points from register manual. Supports two modes:
- **Independent mode**: Generate Ch2-only xlsx from register JSON
- **Incremental mode**: Append Ch2 to existing func_xlsx with cross-reference

## When to Use

**Use when:**
- Generating register configuration coverage
- Already have testplan-func output (incremental mode)
- Need only Ch2 configuration features (independent mode)

**Don't use when:**
- Need only functional features (use testplan-func)
- Missing register manual (.xlsx)

## Arguments

Parse `$ARGUMENTS`:
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `reg_path` | Yes | — | Path to register configuration .xlsx |
| `--output` | Yes | — | Output path for generated .xlsx |
| `--func-xlsx` | No | — | Path to testplan-func output (enables incremental mode) |
| `--template` | No | — | Template xlsx path (required for independent mode) |

## Modes

### Independent Mode

Generate Ch2-only xlsx without cross-reference to Ch1:
```bash
python cfg_writer.py --reg reg.json --output ch2.xlsx --template template.xlsx
```

Use when:
- Only need configuration coverage
- No existing func_xlsx

### Incremental Mode

Append Ch2 to existing func_xlsx with cross-reference:
```bash
python cfg_writer.py --reg reg.json --output combined.xlsx --func-xlsx func.xlsx
```

Use when:
- Have existing func_xlsx from testplan-func
- Need combined Ch1+Ch2 output

## Register Filtering

Automatically excludes registers matching patterns:
- `*_int_*` - Interrupt registers
- `*_fifo_*` - FIFO registers
- `*_fsm*` - FSM registers
- `*_cnt` - Counter registers
- `*_test` - Test registers
- `*_init_*` - Initialization registers
- `*_spare*` - Spare registers
- `*_car_ctrl` - Carrier control

Only includes fields with valid access types: RW, RWC, WO, RWW

## Instructions

### Step 1: Parse Arguments

If `reg_path` is missing, ASK the user.

Determine mode:
```bash
if [[ -n "$func_xlsx" ]]; then
  MODE="incremental"
elif [[ -n "$template" ]]; then
  MODE="independent"
else
  echo "Error: Either --func-xlsx (incremental) or --template (independent) is required"
  exit 1
fi
```

Set `$TP_WORKDIR`:
```bash
OUTPUT_DIR=$(dirname "$output_path")
TP_WORKDIR="${OUTPUT_DIR}/.tp_cache"
mkdir -p "$TP_WORKDIR" 2>/dev/null || TP_WORKDIR="$HOME/.tp_cache"
```

### Step 2: Parse Register Manual

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python reg_to_json.py "$reg_path" "$TP_WORKDIR/reg.json"
```

### Step 3: Generate Ch2

**For Independent Mode:**
```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python cfg_writer.py \
  --reg "$TP_WORKDIR/reg.json" \
  --output "$output_path" \
  --template "$template_path"
```

**For Incremental Mode:**
```bash
cd ${CLAUDE_SKILL_DIR}/scripts && uv run python cfg_writer.py \
  --reg "$TP_WORKDIR/reg.json" \
  --output "$output_path" \
  --func-xlsx "$func_xlsx"
```

### Step 4: Report

Report to user:
- Mode used (independent/incremental)
- Number of registers processed
- Covered vs new registers (incremental mode)
- Output file location

## XLSX Column Hierarchy

测试点输出xlsx采用层级结构：
- **D列**: 寄存器名 (outline_level 0)
- **E列**: 子特性L1 (outline_level 1)
- **F列**: 子特性L2概述 (outline_level 2) — 空白
- **G列**: 子特性L2详情 (outline_level 3) — 空白
- **H列**: 备注 — 域段描述或覆盖标记
- **I列**: 激励 — 【配置】自动生成
- **J-M列**: 检查/覆盖/优先级/活动
- **W列**: 路径 — 反标路径

## Cross-Reference Logic

For incremental mode, registers covered in Ch1 are marked:
- A column = "skip"
- H column = "已在功能特性中覆盖"

This prevents duplicate coverage of registers already tested in functional features.

## Common Mistakes

| Mistake | Why Wrong | Fix |
|---------|-----------|-----|
| Missing template for independent | Independent mode needs template | Provide --template |
| Missing func-xlsx for incremental | Incremental needs func output | Provide --func-xlsx |
| Including RO fields | Only RW/RWC/WO fields belong in Ch2 | Filter by access type |
| Forgetting to filter | Some registers shouldn't be in Ch2 | Use filter_cfg_registers |
