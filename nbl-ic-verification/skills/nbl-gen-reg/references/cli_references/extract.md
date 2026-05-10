# extract

从 Excel 提取寄存器数据并导出为 JSON。

## 用法模式

必须且只能选择以下两种输入模式之一：

- **单文件模式**：`--excel <file.xlsx>`
- **目录模式**：`--excel-dir <directory>`

## 参数

| 参数 | 短选项 | 类型 | 必填 | 默认值 | 说明 |
|-----|-------|------|-----|-------|-----|
| `--excel` | `-e` | TEXT | 否 | - | 单个 Excel 文件路径（.xlsx 或 .xls） |
| `--excel-dir` | `-d` | TEXT | 否 | - | 包含多个 Excel 文件的目录，递归遍历 |
| `--cif` | `-c` | TEXT | 否 | - | CIF 地址映射 Excel 文件路径。若未指定，则 `--cif-check` 自动关闭 |
| `--output` | `-o` | TEXT | 否 | `reg_data.json` | 提取结果的 JSON 输出路径 |
| `--prefix` | `-p` | TEXT | 否 | `ASIC_PDT_V3R1` | Excel 文件名前缀，用于解析 it_name 和 bt_name |
| `--check` | - | FLAG | 否 | `False` | 提取完成后自动执行常规检查 |
| `--cif-check` | - | FLAG | 否 | `False` | 提取完成后自动执行 CIF 地址范围检查（仅在指定 `--cif` 时生效） |

## 文件名格式

Excel 文件名需符合：`{prefix}_{it_name}_{bt_name}.xlsx`

示例：`ASIC_PDT_V3R1_lb_emp_sse.xlsx`
- `it_name` = `lb`
- `bt_name` = `emp_sse`

若文件名以 `prefix_` 开头但缺少 it 或 bt 部分，将报错提示格式错误。

## 示例

```bash
# 从单个 Excel 提取（不带 CIF）
gen-reg extract --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx -o data.json

# 从单个 Excel 提取（带 CIF）
gen-reg extract --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --cif CIF.xlsx -o data.json

# 从目录批量提取
gen-reg extract --excel-dir ./2_Reg/Src/ --prefix Leonis -o all.json

# 提取后立即执行检查
gen-reg extract --excel-dir ./2_Reg/Src/ --cif CIF.xlsx --check --cif-check -o data.json
```

## 注意事项

- xlrd 1.2.0 + openpyxl 双后端支持 xlsx/xls
- 非标准 Excel 文件（如 `%TSD-Header` 加密格式）会被自动跳过
- openpyxl 模式下空单元格值会被强制转为空字符串 `""`
