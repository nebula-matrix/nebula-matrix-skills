# ral 使用案例

## 案例 1：从 Excel 生成单个 Block 的 RAL

直接从 Excel 文件生成指定 Block 的 UVM RAL 模型。最终输出 2 个文件，`name` 取自 `--bn`（小写）。

### 命令

```bash
gen-reg ral \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --bn pa \
  --output /tmp/example_ral
```

### 终端输出

```
  已生成: /tmp/example_ral/ral_sys_pa_block.sv
  已生成: /tmp/example_ral/ral_pa_block_intf.sv
RAL 生成完成: /tmp/example_ral
RAL 生成完成（Excel）: /tmp/example_ral
```

### 结果预览

```bash
$ ls -lh /tmp/example_ral/
total 740K
-rw-rw-r-- 1 user user 494K May  3 12:00 ral_sys_pa_block.sv
-rw-rw-r-- 1 user user 241K May  3 12:00 ral_pa_block_intf.sv

$ wc -l /tmp/example_ral/*.sv
  12673 /tmp/example_ral/ral_sys_pa_block.sv
   4484 /tmp/example_ral/ral_pa_block_intf.sv
  17157 total
```

### 文件说明

| 文件 | 说明 |
|------|------|
| `ral_sys_pa_block.sv` | 拼接了 ral_reg + ral_block + ral_mem + ral_vreg + ral_bkdr + ral_sys_block 共 6 个部分 |
| `ral_pa_block_intf.sv` | Block 接口定义 |

---

## 案例 2：从 JSON + cfg.py 生成系统级 RAL

从 JSON 和 RAL 配置脚本生成完整系统级 RAL。JSON 必须由目录批量提取，且必须包含 cfg 中 `inst_map` 定义的所有 BT。

### 前置条件

```bash
# 1. 目录批量提取 JSON（确保包含所有 BT）
gen-reg extract \
  --excel-dir /home/alvin.xu/test_center/sheet \
  --output /tmp/all.json \
  --prefix ASIC_PDT_V2R1

# 2. 准备 ral_cfg.py（必须定义 top_name 和 inst_map）
cat > /tmp/ral_cfg.py << 'EOF'
inst_map = {
    'pa': [1, 0x0050_0000],
    'dpa': [1, 0x0051_0000],
}

top_name = 'dp'
EOF
```

**配置文件说明：**

| 变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `inst_map` | `dict[str, list]` | 是 | 定义各 BT 的实例信息。Key 为 BT 名称（小写）；Value 为 `[count, base_addr]` 列表，其中 `count` 为该 BT 的实例数量，`base_addr` 为该 BT 的基地址 |
| `top_name` | `str` | 是 | 顶层系统名称，RAL 输出文件名使用此值的小写形式 |

### 命令

```bash
gen-reg ral \
  --json /tmp/all.json \
  --cfg /tmp/ral_cfg.py \
  --output /tmp/example_ral_sys
```

### 终端输出

```
  已生成: /tmp/example_ral_sys/ral_sys_dp_block.sv
  已生成: /tmp/example_ral_sys/ral_dp_block_intf.sv
RAL 生成完成（JSON+cfg）: /tmp/example_ral_sys
```

### 结果预览

```bash
$ ls -lh /tmp/example_ral_sys/
total 740K
-rw-rw-r-- 1 user user 494K May  3 12:00 ral_sys_dp_block.sv
-rw-rw-r-- 1 user user 241K May  3 12:00 ral_dp_block_intf.sv
```

---

## 案例 3：从 Excel 目录 + cfg.py 直接生成系统级 RAL

无需先提取 JSON，直接指定 Excel 目录和 cfg.py 一步生成系统级 RAL。

### 前置条件

```bash
# 准备 ral_cfg.py（必须定义 top_name 和 inst_map）
cat > /tmp/ral_cfg.py << 'EOF'
inst_map = {
    'bm': [1, 0x0050_0000],
    'ped': [1, 0x0051_0000],
}

top_name = 'datapath'
EOF
```

### 命令

```bash
gen-reg ral \
  --excel-dir /home/alvin.xu/test_center/sheet \
  --cfg /tmp/ral_cfg.py \
  --prefix ASIC_PDT_V2R1 \
  --output /tmp/example_ral_excel_dir
```

### 终端输出

```
  已生成: /tmp/example_ral_excel_dir/ral_sys_datapath_block.sv
  已生成: /tmp/example_ral_excel_dir/ral_datapath_block_intf.sv
RAL 生成完成（Excel-dir+cfg）: /tmp/example_ral_excel_dir
```

### 结果预览

```bash
$ ls -lh /tmp/example_ral_excel_dir/
total 740K
-rw-rw-r-- 1 user user 494K May  3 12:00 ral_sys_datapath_block.sv
-rw-rw-r-- 1 user user 241K May  3 12:00 ral_datapath_block_intf.sv
```

---

## 案例 4：JSON 中缺少 cfg 指定的 BT（校验失败）

若 JSON 只包含 `pa`，但 cfg 要求 `pa` 和 `dpa`，会报错退出。

### 前置条件

```bash
# 只提取了 pa
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --output /tmp/only_pa.json \
  --prefix ASIC_PDT_V2R1
```

### 命令

```bash
gen-reg ral \
  --json /tmp/only_pa.json \
  --cfg /tmp/ral_cfg.py \
  --output /tmp/example_ral_fail
```

### 终端输出

```
Error: 配置文件中的 BT 在 JSON 中未找到: dpa
```

### 返回值

退出码 `1`

---

## 案例 6：从 Excel 直接生成并执行数据检查（失败）

Excel 直接生成时添加 `--check`，会在生成前先执行常规数据检查。若数据有误则报错退出，不会生成文件。

### 命令

```bash
gen-reg ral \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --bn pa \
  --check \
  --output /tmp/example_ral_check_fail
```

### 终端输出

```
ERROR, module: pa reg: upa_ext_conf_table, offset_addr: 0x5000, reg_width(32) shoule be equal with all(field_bits)(28)!
```

### 返回值

退出码 `1`

---

## 案例 7：从 Excel 直接生成并执行 CIF 检查

Excel 直接生成时添加 `--cif-check --cif <file>`，会在生成前先验证寄存器地址是否落在 CIF 定义的范围内。

### 命令

```bash
gen-reg ral \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --bn pa \
  --cif-check \
  --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx \
  --output /tmp/example_ral_cif
```

### 终端输出（通过时）

```
  已生成: /tmp/example_ral_cif/ral_sys_pa_block.sv
  已生成: /tmp/example_ral_cif/ral_pa_block_intf.sv
RAL 生成完成: /tmp/example_ral_cif
RAL 生成完成（Excel）: /tmp/example_ral_cif
```

### 返回值

退出码 `0`

---

## 案例 8：缺少必需参数

未提供有效的参数组合时，会报错。

### 命令

```bash
gen-reg ral --json /tmp/example.json --output /tmp/out
```

### 终端输出

```
Error: 请指定 --excel + --bn 或 --excel-dir + --cfg 或 --json + --cfg
```

### 返回值

退出码 `1`
