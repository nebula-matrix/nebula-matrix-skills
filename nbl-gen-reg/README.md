# nbl-gen-reg

NBL IC寄存器生成工具插件。从Excel寄存器手册提取数据，生成IC验证和实现所需的各类寄存器相关代码与数据。

## 功能

- **extract**: 从Excel提取寄存器数据并导出为JSON（支持单文件/目录批量提取）
- **check**: 常规数据一致性检查（offset_addr、reg_width与field_bits等）
- **cif-check**: CIF地址范围检查
- **filter**: 按BT/register/field级别多维度条件筛选数据
- **regslv**: 生成reg_slv Verilog模块
- **ral**: 生成UVM RAL模型（支持单Block/系统级两种模式）
- **cfg**: 生成寄存器配置表（SystemVerilog）

## 安装

通过 uv 安装 CLI 工具：

```bash
uv tool install --editable ./skills/nbl-gen-reg/scripts/
```

安装后通过 `gen-reg` 命令调用：

```bash
gen-reg extract --excel ASIC_PDT_V3R1_ppe_pa.xlsx -o data.json
gen-reg ral --excel ASIC_PDT_V3R1_ppe_pa.xlsx --bn pa -o ./ral_out/
gen-reg regslv --json data.json --bt pa -o ./regslv_out/
```

## 依赖

- Python >= 3.12
- uv (Python 包管理器)
- openpyxl / xlrd (Excel 解析)
- typer (CLI 框架)
- jinja2 (模板渲染)

## 目录结构

```
nbl-gen-reg/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── nbl-gen-reg/
│       ├── SKILL.md              # 技能主文件
│       ├── scripts/              # Python 代码 (gen_reg_tools)
│       │   ├── gen_reg_tools/    # 核心包
│       │   ├── pyproject.toml    # uv 项目配置
│       │   └── uv.lock
│       └── references/           # CLI 参考文档和使用案例
│           ├── cli_references/
│           └── 使用案例/
└── README.md
```
