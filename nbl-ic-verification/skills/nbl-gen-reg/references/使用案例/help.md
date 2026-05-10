# help 使用案例

## 案例 1：查看完整使用指南

显示 gen_reg_tools 的所有命令、参数和用法说明。

### 命令

```bash
gen-reg help
```

### 终端输出（节选）

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     gen_reg_tools 使用指南                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

gen_reg_tools 是寄存器自动化生成工具集，支持从 Excel 提取寄存器定义并生成：
  - UVM RAL 模型（SystemVerilog）
  - reg_slv Verilog 模块
  - 寄存器配置表（SystemVerilog）

──────────────────────────────────────────────────────────────────────────────
支持的命令
──────────────────────────────────────────────────────────────────────────────

  extract     从 Excel 提取寄存器数据并导出为 JSON
  check       对提取结果进行常规检查
  cif-check   检查寄存器地址是否在 CIF 定义的地址范围内
  filter      按 BT 名称筛选 JSON 数据
  regslv      生成 reg_slv Verilog 代码
  ral         生成 UVM RAL 模型
  cfg         生成寄存器配置表
  help        显示此帮助信息

...（后续为各命令详细说明）
```

---

## 案例 2：查看子命令帮助

查看任意子命令的详细帮助信息。

### 命令

```bash
gen-reg extract --help
```

### 终端输出（节选）

```
 Usage: gen-reg extract [OPTIONS]

 从 Excel 提取寄存器数据并导出为 JSON

 支持两种输入模式，必须且只能选择其中一种：
  - 单个文件模式（--excel）：处理一个 Excel 文件，提取所有有效 sheet
  - 目录模式（--excel-dir）：遍历目录下所有 .xlsx 文件，批量提取

 ...

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --excel      -e      TEXT   单个 Excel 文件路径（.xlsx / .xls）             │
│ --excel-dir  -d      TEXT   包含多个 Excel 文件的目录                        │
│ --cif        -c      TEXT   CIF 地址映射文件路径（可选）...                   │
│ --output     -o      TEXT   JSON 输出路径 [default: reg_data.json]          │
│ --prefix     -p      TEXT   文件名前缀 [default: ASIC_PDT_V3R1]             │
│ --check                     提取后自动执行常规检查                           │
│ --cif-check                 提取后自动执行 CIF 地址范围检查                 │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 其他子命令

```bash
gen-reg regslv --help
gen-reg ral --help
gen-reg filter --help
gen-reg cfg --help
```
