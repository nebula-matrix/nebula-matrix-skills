# ral

生成 UVM RAL（Register Abstraction Layer）模型，支持前门和后门两种访问方式。

## 用法模式

必须且只能选择以下三种输入模式之一：

- **Excel 单文件模式**：`--excel <file> --bn <block_name>`
- **Excel 目录模式**：`--excel-dir <dir> --cfg <cfg.py>`
- **JSON 模式**：`--json <file> --cfg <cfg.py>`（JSON 必须由目录批量提取得到，且必须包含 cfg 中指定的所有 BT）

## 参数

| 参数 | 短选项 | 类型 | 必填 | 默认值 | 说明 |
|-----|-------|------|-----|-------|-----|
| `--excel` | `-e` | TEXT | 否 | - | 寄存器 Excel 文件路径（Excel 单文件模式） |
| `--excel-dir` | `-d` | TEXT | 否 | - | 包含 Excel 文件的目录路径（Excel 目录模式） |
| `--prefix` | `-p` | TEXT | 否 | - | Excel 文件名前缀（`--excel-dir` 模式下可用，如: `ASIC_PDT_V2R1`） |
| `--json` | `-j` | TEXT | 否 | - | 由 `gen-reg extract` 生成的 JSON 文件路径（JSON 模式） |
| `--bn` | `-b` | TEXT | 否 | - | 目标 Block 名称（Excel 单文件模式专用） |
| `--cfg` | `-c` | TEXT | 否 | - | RAL 配置 Python 脚本路径（系统级模式专用），定义块间层次关系等 |
| `--output` | `-o` | TEXT | 否 | `./ral_out` | 生成的 UVM RAL 代码输出目录 |
| `--check` | - | FLAG | 否 | `False` | Excel 单文件模式专用：生成前先执行常规数据检查 |
| `--cif-check` | - | FLAG | 否 | `False` | Excel 单文件模式专用：生成前先执行 CIF 地址范围检查（需配合 `--cif`） |
| `--cif` | - | TEXT | 否 | - | CIF 地址映射表 Excel 文件路径（配合 `--cif-check` 使用） |

## 输出文件

最终输出 2 个文件，`{name}` 规则见下方说明。

| 文件名 | 说明 |
|-------|-----|
| `ral_sys_{name}_block.sv` | 拼接文件，包含 ral_reg + ral_block + ral_mem + ral_vreg + ral_bkdr + ral_sys_block 共 6 个部分 |
| `ral_{name}_block_intf.sv` | Block 接口定义 |

### `{name}` 取值规则

- **Excel 单文件模式**：`name = --bn 的值（小写）`
  - 示例：`--bn pa` → 文件名为 `ral_sys_pa_block.sv` / `ral_pa_block_intf.sv`
- **Excel 目录模式 / JSON 模式**：`name = cfg.py 中 top_name 的值（小写）`
  - 示例：cfg 中 `top_name = 'dp'` → 文件名为 `ral_sys_dp_block.sv` / `ral_dp_block_intf.sv`

### 配置文件样例

```python
# ral_cfg.py
inst_map = {
    'pa': [1, 0x0050_0000],
    'dpa': [1, 0x0051_0000],
}

top_name = 'dp'  # 文件名将使用此值的小写形式
```

**配置文件说明：**

| 变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `inst_map` | `dict[str, list]` | 是 | 定义各 BT 的实例信息。Key 为 BT 名称（小写）；Value 为 `[count, base_addr]` 列表，其中 `count` 为该 BT 的实例数量，`base_addr` 为该 BT 的基地址 |
| `top_name` | `str` | 是 | 顶层系统名称，RAL 输出文件名使用此值的小写形式 |

## 系统级模式前置要求

Excel 目录模式和 JSON 模式都需要 cfg.py 中 `inst_map` 定义的所有 BT 都存在于数据中。运行时会自动校验：

- 若 cfg 中的某个 BT 在数据中不存在 → **报错退出**
- 若数据中存在但 cfg 中未列出的 BT → **不影响生成**

### 校验失败示例

```bash
gen-reg ral --json only_pa.json --cfg ral_cfg.py -o ./ral_out/
```

输出：

```
Error: 配置文件中的 BT 在 JSON 中未找到: dpa
```

## 示例

```bash
# 从 Excel 生成单个 Block 的 RAL
gen-reg ral --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec -o ./ral_out/

# 从 Excel 生成，同时执行数据检查
gen-reg ral --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec --check -o ./ral_out/

# 从 Excel 生成，同时执行 CIF 地址范围检查
gen-reg ral --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec --cif-check --cif CIF.xlsx -o ./ral_out/

# 从 Excel 目录 + cfg.py 直接生成系统级 RAL（无需先提取 JSON）
gen-reg ral --excel-dir ./2_Reg/Src/ --cfg ral_cfg.py --prefix ASIC_PDT_V2R1 -o ./ral_out/

# 从 JSON + cfg.py 生成系统级 RAL（JSON 需包含 cfg 中所有 BT）
gen-reg extract --excel-dir ./2_Reg/Src/ --prefix Leonis -o all.json
gen-reg ral --json all.json --cfg ral_cfg.py -o ./ral_out/
```
