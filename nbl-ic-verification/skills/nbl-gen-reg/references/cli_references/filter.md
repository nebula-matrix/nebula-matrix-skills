# filter

按多维度条件筛选寄存器或字段数据，支持从 JSON 或 Excel 输入。

## 用法模式

### 模式 A：筛选数据（默认）

必须提供 `--json` 或 `--excel` 作为输入源，且至少指定一个过滤条件。

### 模式 B：列出所有 BT（`--get-bt`）

必须提供 `--json`、`--excel` 或 `--excel-dir` 之一。

## 参数

### 输入源

| 参数 | 短选项 | 类型 | 必填 | 说明 |
|-----|-------|------|-----|------|
| `--json` | `-j` | TEXT | 否* | JSON 文件路径 |
| `--excel` | `-e` | TEXT | 否* | 单个 Excel 文件路径 |
| `--excel-dir` | `-d` | TEXT | 否* | 包含 Excel 文件的目录（仅 `--get-bt` 可用） |

\*注：筛选模式下 `--json`、`--excel` 二者必选其一。`

### 过滤条件（多条件为"与"逻辑）

| 参数 | 短选项 | 类型 | 必填 | 默认值 | 说明 |
|-----|-------|------|-----|-------|------|
| `--bt` | `-b` | TEXT | 否 | - | Block 名称白名单，多个用逗号分隔 |
| `--level` | `-l` | TEXT | 否 | `register` | 过滤级别：`register`（寄存器级别）/ `field`（字段级别）/ `bt`（BT 级别） |
| `--rw-attr` | - | TEXT | 否 | - | rw_attr 白名单，多个用逗号分隔（如: `rw,rww,wo`） |
| `--reg-type` | - | TEXT | 否 | - | reg_type 白名单，多个用逗号分隔（如: `tbl,reg`） |
| `--name-regex` | - | TEXT | 否 | - | register name 正则匹配表达式 |
| `--depth` | - | TEXT | 否 | - | depth 范围表达式（见下方格式说明） |
| `--width` | - | TEXT | 否 | - | width 范围表达式（见下方格式说明） |
| `--field-regex` | - | TEXT | 否 | - | field name 正则匹配表达式 |
| `--default-value` | - | TEXT | 否 | - | field default_value 匹配值（支持十六进制 `0x...`） |
| `--wr-ctrl` | - | TEXT | 否 | - | wr_ctrl 白名单，多个用逗号分隔 |

### 范围表达式格式

`--depth` 和 `--width` 支持以下格式：

| 格式 | 含义 | 示例 |
|------|------|------|
| `N` | 精确等于 N | `--depth 1` |
| `>N` | 大于 N | `--depth ">1"` |
| `>=N` | 大于等于 N | `--depth ">=2"` |
| `<N` | 小于 N | `--depth "<10"` |
| `<=N` | 小于等于 N | `--depth "<=5"` |
| `N-M` | 范围 N 到 M（含） | `--depth "1-10"` |

> 包含特殊字符时建议使用引号包裹。

### 列 BT 模式（`--get-bt`）

| 参数 | 短选项 | 类型 | 必填 | 说明 |
|-----|-------|------|-----|------|
| `--get-bt` | - | FLAG | 否 | 列出所有 `block_type` 为 `bt` 的 Block 名称 |
| `--json` | `-j` | TEXT | 否* | 从 JSON 文件列出 BT |
| `--excel` | `-e` | TEXT | 否* | 从 Excel 单文件提取后列出 BT |
| `--excel-dir` | `-d` | TEXT | 否* | 从 Excel 目录批量提取后列出 BT |
| `--prefix` | `-p` | TEXT | 否 | Excel 文件名前缀（提取模式可用） |

\*注：`--get-bt` 模式下 `--json`、`--excel`、`--excel-dir` 三者必选其一。`

### 输出

| 参数 | 短选项 | 类型 | 必填 | 默认值 | 说明 |
|-----|-------|------|-----|-------|------|
| `--output` | `-o` | TEXT | 否 | `filtered.json` | 筛选后的 JSON 输出路径 |

## 过滤逻辑

所有指定的条件之间为**"与"逻辑**，即结果必须同时满足所有条件。

### register 级别（`--level register`，默认）

- 先匹配 register 级别条件（`--reg-type`、`--name-regex`、`--depth`、`--width`）
- 若指定了 field 级别条件（`--rw-attr`、`--field-regex`、`--default-value`、`--wr-ctrl`），register 必须包含至少一个满足这些条件的 field
- 若 field 条件被指定，保留的 register 中只包含匹配的 fields

### field 级别（`--level field`）

- register 级别条件作用于 field 的父 register：不满足 register 条件的 register 下所有 fields 均被排除
- field 级别条件作用于每个 field：只保留同时满足所有条件的 fields
- 若一个 register 下没有匹配的 fields，该 register 被移除

### BT 级别（`--level bt`）

- 仅按 BT 名称进行白名单筛选，不进一步过滤 register 或 field
- 必须同时指定 `--bt` 提供目标 BT 名称列表
- 其他 register/field 级别条件在 BT 级别下被忽略

## 示例

```bash
# 按 BT 级别筛选（简单 Block 白名单）
gen-reg filter --json reg_data.json --level bt --bt dmacsec -o dmacsec.json

# 从 Excel 直接按 BT 级别筛选
gen-reg filter --excel ASIC_PDT_V3R1_ppe_pa.xlsx --level bt --bt pa -o pa.json

# 按 BT 筛选多个 Block
gen-reg filter --json reg_data.json --level bt --bt dmacsec,sse -o sub.json

# 按 rw_attr 筛选 registers（register 级别，默认）
gen-reg filter --json reg_data.json --bt pa --rw-attr rw -o rw_regs.json

# 按 reg_type 筛选
gen-reg filter --json reg_data.json --reg-type tbl -o tbl_regs.json

# 综合多条件（与逻辑）
gen-reg filter --json reg_data.json --bt pa --rw-attr rw --depth 1 -o result.json

# 按 depth 范围筛选
gen-reg filter --json reg_data.json --depth ">1" -o deep_regs.json

# field 级别筛选
gen-reg filter --json reg_data.json --level field --rw-attr rw --field-regex '.*en' -o fields.json

# 从 JSON 列出所有 BT
gen-reg filter --get-bt --json reg_data.json

# 从 Excel 列出所有 BT
gen-reg filter --get-bt --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx
```

## 注意事项

- 筛选结果保持原始 JSON 的层次结构（Top → Block → Register → Field）
- 输出 JSON 可直接作为 `regslv`、`cfg`、`ral` 的输入
- `--get-bt` 模式下 `--excel-dir` 仍然可用，但普通筛选模式不支持 `--excel-dir`
