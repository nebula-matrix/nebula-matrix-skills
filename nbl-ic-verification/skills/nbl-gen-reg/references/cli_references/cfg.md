# cfg

生成寄存器配置表（SystemVerilog），用于验证环境中的寄存器配置管理。

## 用法模式

必须且只能选择以下三种输入模式之一：

- **Excel 模式**：`--excel <file> --bn <block_name>`
- **JSON 单 bt 模式**：`--json <file> --bt <block_name>`
- **JSON 系统级模式**：`--json <file> --cfg <cfg.py>`（JSON 必须由目录批量提取得到，且必须包含 cfg 中指定的所有 BT）

## 参数

| 参数 | 短选项 | 类型 | 必填 | 默认值 | 说明 |
|-----|-------|------|-----|-------|-----|
| `--excel` | `-e` | TEXT | 否 | - | 寄存器 Excel 文件路径（Excel 模式） |
| `--json` | `-j` | TEXT | 否 | - | 由 `gen-reg extract` 生成的 JSON 文件路径（JSON 模式） |
| `--bn` | - | TEXT | 否 | - | 目标 Block 名称（Excel 模式专用） |
| `--bt` | `-b` | TEXT | 否 | - | 目标 Block 名称（JSON 单 bt 模式专用） |
| `--cfg` | `-c` | TEXT | 否 | - | 配置 Python 脚本路径（JSON 系统级模式专用），定义 `inst_map` |
| `--output` | `-o` | TEXT | 否 | `./cfg_out` | 生成的配置表文件输出目录 |
| `--check` | - | FLAG | 否 | `False` | Excel 模式专用：生成前先执行常规数据检查 |
| `--cif-check` | - | FLAG | 否 | `False` | Excel 模式专用：生成前先执行 CIF 地址范围检查（需配合 `--cif`） |
| `--cif` | - | TEXT | 否 | - | CIF 地址映射表 Excel 文件路径（配合 `--cif-check` 使用） |

## 输出文件

每个 Block 生成三个 SystemVerilog 文件：

| 文件名 | 说明 |
|-------|-----|
| `{bt}_reg_tbl_cfg_decl.sv` | 配置表结构体声明 |
| `{bt}_reg_tbl_cfg.sv` | 配置表实例化及赋值逻辑 |
| `{bt}_init_cfg_by_ral.sv` | RAL 配置表初始化代码 |

### 系统级模式（JSON + cfg.py）

当使用 `--json + --cfg` 时，会为 cfg.py 中 `inst_map` 定义的 **所有 BT** 各生成一套上述三个文件。

### 配置文件样例

```python
# cfg.py
inst_map = {
    'bm': [1, 0x0050_0000],
    'ped': [1, 0x0051_0000],
}

top_name = 'datapath'  # 仅用于校验，不影响 cfg 输出文件名
```

**配置文件说明：**

| 变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `inst_map` | `dict[str, list]` | 是 | 定义各 BT 的实例信息。Key 为 BT 名称（小写）；Value 为 `[count, base_addr]` 列表，其中 `count` 为该 BT 的实例数量，`base_addr` 为该 BT 的基地址 |
| `top_name` | `str` | 是 | 顶层系统名称，仅用于校验完整性，不影响 cfg 输出文件名 |

### JSON 系统级模式前置要求

JSON 文件必须通过目录批量提取（`gen-reg extract --excel-dir`）获得，确保包含 cfg 中 `inst_map` 定义的所有 BT。运行时会自动校验：

- 若 cfg 中的某个 BT 在 JSON 中不存在 → **报错退出**
- 若 JSON 中存在但 cfg 中未列出的 BT → **不影响生成**

## 示例

```bash
# 从 Excel 直接生成单个 Block 的配置表
gen-reg cfg --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec -o ./cfg_out/

# 从 Excel 生成并执行数据检查
gen-reg cfg --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec --check -o ./cfg_out/

# 从 JSON 单 bt 生成
gen-reg cfg --json reg_data.json --bt dmacsec -o ./cfg_out/

# 从 JSON + cfg.py 系统级生成（为所有 BT 生成配置表）
gen-reg extract --excel-dir ./2_Reg/Src/ --prefix Leonis -o all.json
gen-reg cfg --json all.json --cfg cfg.py -o ./cfg_out/
```

## 注意事项

- `--check` 和 `--cif-check` 仅在 Excel 直接输入模式下有效
- JSON 模式下数据应在提取阶段已通过 `check` / `cif-check` 命令验证
- 系统级模式（`--json + --cfg`）下，输出目录中会包含多个 BT 的配置表文件
- 内部通过 `CfgProcessor` → `CfgRenderer` 链路生成
