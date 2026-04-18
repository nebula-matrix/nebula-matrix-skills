---
name: testplan-cfg
description: 从功能规格书、寄存器手册和func输出xlsx生成配置特性测试点。输入spec_path + reg_path + func_xlsx，追加Ch2到输出。触发：生成配置测试点、寄存器覆盖、testplan cfg。
---

# Test Plan Generator - Configuration Features

## Overview

Generate Chapter 2 (配置特性) test points, appending to existing func xlsx.

## When to Use

**Use when:**
- Generating register configuration coverage
- Already have testplan-func output
- Need to add Ch2 configuration features

**Don't use when:**
- Need only functional features (use testplan-func)
- Missing func xlsx output

## Arguments

Parse `$ARGUMENTS`:
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `spec_path` | Yes | — | Path to functional specification .docx |
| `reg_path` | Yes | — | Path to register configuration .xlsx |
| `func_path` | Yes | — | Path to testplan-func output xlsx |
| `--output` | No | func_path | Output path (default overwrites func_path) |

## XLSX Column Hierarchy

测试点输出xlsx采用层级结构：
- **D列**: 特性名/寄存器名 (outline_level 0)
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

If any required argument missing, ASK the user.

### Step 2: Document Conversion

Run reg_to_json.py:
```bash
cd ${CLAUDE_SKILL_DIR}/../../scripts && uv run python reg_to_json.py "$reg_path" "$TP_WORKDIR/reg.json"
```

### Step 3: Extract Covered Registers

The cfg_writer.py handles this automatically from func_path.

### Step 4: Generate Ch2

```bash
cd ${CLAUDE_SKILL_DIR}/../../scripts && uv run python cfg_writer.py \
  --func-xlsx "$func_path" \
  --reg "$TP_WORKDIR/reg.json" \
  --output "$output_path"
```

### Step 5: Report

Report to user:
- Number of registers processed
- Covered vs uncovered count
- Output file location
