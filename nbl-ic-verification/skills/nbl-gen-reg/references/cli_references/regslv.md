# regslv

生成 `reg_slv` Verilog 模块（寄存器从机），支持 APB/AXI-Lite 总线接口。

## 用法模式

必须且只能选择以下两种输入模式之一：

- **Excel 模式**：`--excel <file> --sheet <sheet_name>`
- **JSON 模式**：`--json <file> --bt <block_name>`

## 参数

| 参数 | 短选项 | 类型 | 必填 | 默认值 | 说明 |
|-----|-------|------|-----|-------|-----|
| `--excel` | `-e` | TEXT | 否 | - | 寄存器 Excel 文件路径（Excel 模式） |
| `--json` | `-j` | TEXT | 否 | - | 由 `gen-reg extract` 生成的 JSON 文件路径（JSON 模式） |
| `--sheet` | `-s` | TEXT | 否 | - | Excel 中目标 Sheet 名称（Excel 模式专用） |
| `--bt` | `-b` | TEXT | 否 | - | 目标 Block 名称（JSON 模式专用） |
| `--output` | `-o` | TEXT | 否 | `./out` | 生成的 Verilog 文件输出目录 |
| `--check` | - | FLAG | 否 | `False` | Excel 模式专用：生成前先执行常规数据检查 |
| `--cif-check` | - | FLAG | 否 | `False` | Excel 模式专用：生成前先执行 CIF 地址范围检查（需配合 `--cif`） |
| `--cif` | - | TEXT | 否 | - | CIF 地址映射表 Excel 文件路径（配合 `--cif-check` 使用） |
| `--config` | - | TEXT | 否 | - | 生成配置项，格式 `key=value,key2=value2`（暂未实现） |

## 输出文件

- `{bt}_reg_slv.sv` — 完整的 reg_slv Verilog 模块

## 示例

```bash
# 从 Excel 直接生成
gen-reg regslv --excel ASIC_PDT_V3R1_intf_eth.xlsx --sheet eth_a2mti_mclk -o ./out/

# 从 Excel 生成，同时执行数据检查
gen-reg regslv --excel ASIC_PDT_V3R1_intf_eth.xlsx --sheet eth_a2mti_mclk --check -o ./out/

# 从 Excel 生成，同时执行 CIF 地址范围检查
gen-reg regslv --excel ASIC_PDT_V3R1_intf_eth.xlsx --sheet eth_a2mti_mclk --cif-check --cif CIF.xlsx -o ./out/

# 从 JSON 生成
gen-reg regslv --json reg_data.json --bt eth_a2mti_mclk -o ./out/
```

## 注意事项

- `--check` 和 `--cif-check` 仅在 Excel 直接输入模式下有效，JSON 模式下数据应在提取阶段已通过 `check` / `cif-check` 命令验证
- 多时钟域生成（`multi_ck`）暂未实现
- 内部通过 `RegProcessor` → `RegSlvRenderer` 链路生成
- 模板使用 Jinja2，`tpl_dict` 方式访问数据
