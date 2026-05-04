---
name: nbl-gen-reg
description: IC寄存器生成工具集。从Excel寄存器手册提取数据，生成reg_slv Verilog、UVM RAL模型、寄存器配置表，支持数据校验和多维度筛选。
---

# nbl-gen-reg

## 概述

本工具集用于从寄存器 Excel 手册自动化生成 IC 验证和实现所需的各类寄存器相关代码与数据。采用 **命令行驱动** 的工作流：

- **提取阶段**：从 Excel 提取结构化 JSON 数据，支持单文件或目录批量提取
- **校验阶段**：执行常规数据一致性检查和 CIF 地址范围校验
- **筛选阶段**：按 register/field/BT 级别多维度条件筛选数据
- **生成阶段**：生成 reg_slv Verilog、UVM RAL 模型、寄存器配置表

**核心优势**：统一 CLI 入口、双输入模式（Excel 直输 / JSON 复用）、丰富的数据校验。

## 安装

使用 `uv` 安装（推荐）：

```bash
# 进入项目目录
cd /path/to/reference_core

# 创建虚拟环境并安装
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 验证安装
gen-reg --help
```

安装完成后，`gen-reg` 命令全局可用。

## 指令速查

| 指令 | 功能 | 典型用法 |
|------|------|----------|
| `extract` | 从 Excel 提取 JSON 数据 | `gen-reg extract --excel file.xlsx -o out.json` |
| `check` | 常规数据一致性检查 | `gen-reg check --json out.json` |
| `cif-check` | CIF 地址范围校验 | `gen-reg cif-check --json out.json --cif CIF.xlsx` |
| `filter` | 多维度筛选寄存器/字段 | `gen-reg filter --json out.json --bt pa -o sub.json` |
| `regslv` | 生成 reg_slv Verilog | `gen-reg regslv --json out.json --bt pa -o ./out` |
| `ral` | 生成 UVM RAL 模型 | `gen-reg ral --json out.json --cfg cfg.py -o ./ral_out` |
| `cfg` | 生成寄存器配置表 | `gen-reg cfg --json out.json --bt pa -o ./cfg_out` |
| `help` | 显示完整使用指南 | `gen-reg help` |

**获取帮助**：每个子命令都支持 `--help`：

```bash
gen-reg extract --help
gen-reg regslv --help
gen-reg ral --help
```

## 典型工作流

### 工作流 A：单模块快速生成（Excel 直输模式）

适用于单个 Block，跳过 JSON 中间步骤：

```bash
# 1. 直接生成 reg_slv
gen-reg regslv --excel ASIC.xlsx --sheet pa -o ./out/

# 2. 带数据检查后再生成
gen-reg regslv --excel ASIC.xlsx --sheet pa --check -o ./out/

# 3. 直接生成 RAL
gen-reg ral --excel ASIC.xlsx --bn pa -o ./ral_out/

# 4. 直接生成 cfg
gen-reg cfg --excel ASIC.xlsx --bn pa -o ./cfg_out/
```

### 工作流 B：系统级生成（JSON 复用模式）

适用于多模块系统，JSON 一次提取多次复用：

```bash
# 1. 目录批量提取 JSON（包含所有 BT）
gen-reg extract --excel-dir ./2_Reg/Src/ --prefix ASIC -o all.json

# 2. 数据校验
gen-reg check --json all.json
gen-reg cif-check --json all.json --cif CIF.xlsx

# 3. 系统级 RAL 生成（需 cfg.py）
gen-reg ral --json all.json --cfg ral_cfg.py -o ./ral_out/

# 4. 系统级 cfg 生成
gen-reg cfg --json all.json --cfg cfg.py -o ./cfg_out/

# 5. 单模块 reg_slv 生成
gen-reg regslv --json all.json --bt dmacsec -o ./out/
```

### 工作流 C：数据筛选与审查

```bash
# 1. 列出所有 BT 模块
gen-reg filter --get-bt --json all.json

# 2. 按 BT 级别筛选子集
gen-reg filter --json all.json --level bt --bt pa,ipro -o sub.json

# 3. 按寄存器条件筛选（多条件与逻辑）
gen-reg filter --json all.json --bt pa --rw-attr rw --depth 1 -o filtered.json

# 4. 按 field 级别筛选
gen-reg filter --json all.json --level field --rw-attr rw --field-regex 'en$' -o fields.json
```

## 核心指令说明

### extract — 数据提取

从 Excel 提取结构化 JSON 数据，支持单文件或目录批量提取。

```bash
# 单文件
gen-reg extract --excel file.xlsx -o out.json

# 目录批量（带 CIF）
gen-reg extract --excel-dir ./sheets/ --cif CIF.xlsx --prefix ASIC -o all.json
```

### check / cif-check — 数据校验

```bash
# 常规检查（reg_width == field_bits 之和等）
gen-reg check --json out.json

# CIF 地址范围检查
gen-reg cif-check --json out.json --cif CIF.xlsx
```

### filter — 多维度筛选

支持 register/field/BT 三个过滤级别，所有条件之间为"与"逻辑。

| 级别 | 作用 | 关键参数 |
|------|------|----------|
| `bt` | Block 白名单 | `--bt pa,ipro` |
| `register`（默认） | 寄存器级别筛选 | `--rw-attr`, `--reg-type`, `--depth`, `--width`, `--name-regex` |
| `field` | 字段级别筛选 | `--rw-attr`, `--field-regex`, `--default-value`, `--wr-ctrl` |

### regslv / ral / cfg — 代码生成

三个生成指令都支持 **双输入模式**：

| 模式 | 参数 | 适用场景 |
|------|------|----------|
| Excel 模式 | `--excel + --sheet/--bn` | 单模块快速生成 |
| JSON 模式 | `--json + --bt/--cfg` | 系统级生成、JSON 复用 |

JSON 系统级模式（`--json + --cfg`）需要 `cfg.py` 配置文件：

```python
# cfg.py / ral_cfg.py
inst_map = {
    'pa': [1, 0x0050_0000],   # [实例数量, 基地址]
    'dpa': [1, 0x0051_0000],
}
top_name = 'dp'  # 顶层系统名称
```

## 参考文档

如需更详细的参数说明和使用案例，按需查阅以下文档：

| 文档 | 内容 | 何时查阅 |
|------|------|----------|
| [references/cli_references/](references/cli_references/) | 各指令的完整参数说明表 | 需要精确命令参数时 |
| [references/使用案例/](references/使用案例/) | 各指令的实际使用案例和输出示例 | 需要参考具体用法时 |

各指令对应文档：

| 指令 | CLI 参考 | 使用案例 |
|------|----------|----------|
| extract | [extract.md](references/cli_references/extract.md) | [extract.md](references/使用案例/extract.md) |
| check | [check.md](references/cli_references/check.md) | [check.md](references/使用案例/check.md) |
| cif-check | [cif-check.md](references/cli_references/cif-check.md) | [cif-check.md](references/使用案例/cif-check.md) |
| filter | [filter.md](references/cli_references/filter.md) | [filter.md](references/使用案例/filter.md) |
| regslv | [regslv.md](references/cli_references/regslv.md) | [regslv.md](references/使用案例/regslv.md) |
| ral | [ral.md](references/cli_references/ral.md) | [ral.md](references/使用案例/ral.md) |
| cfg | [cfg.md](references/cli_references/cfg.md) | [cfg.md](references/使用案例/cfg.md) |
| help | [help.md](references/cli_references/help.md) | [help.md](references/使用案例/help.md) |

索引文档：[references/使用案例/index.md](references/使用案例/index.md)

## 注意事项

1. **Excel 直接生成时支持 `--check` / `--cif-check`**：`regslv`、`ral`、`cfg` 在 Excel 模式下可附加 `--check` 或 `--cif-check --cif <file>` 在生成前自动校验数据。
2. **JSON 系统级模式需要目录批量提取**：`ral --json + --cfg` 和 `cfg --json + --cfg` 要求 JSON 由 `extract --excel-dir` 生成，确保包含 cfg.py 中 `inst_map` 定义的所有 BT。
3. **filter 多条件为"与"逻辑**：同时指定 `--bt`、`--rw-attr`、`--depth` 等多个条件时，结果必须同时满足所有条件。
4. **范围表达式**：`--depth` 和 `--width` 支持 `N`、`>N`、`>=N`、`<N`、`<=N`、`N-M` 格式，含特殊字符时需用引号包裹。
