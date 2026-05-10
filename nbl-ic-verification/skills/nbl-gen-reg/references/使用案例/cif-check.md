# cif-check 使用案例

## 案例 1：CIF 检查通过

验证 JSON 中所有寄存器地址是否落在 CIF 地址映射表定义的范围内。

### 前置条件

已提取 JSON 和 CIF 文件：

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx \
  --output /tmp/example_cif.json \
  --prefix ASIC_PDT_V2R1
```

### 命令

```bash
gen-reg cif-check --json /tmp/example_cif.json --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx
```

### 终端输出（通过时）

```
CIF 检查通过
```

### 返回值

退出码 `0`

---

## 案例 2：CIF 检查失败（地址越界）

某 Block 的寄存器地址超出 CIF 定义的模块地址空间。

### 命令

```bash
gen-reg cif-check --json /tmp/example_cif.json --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx
```

### 终端输出（失败时，示例）

```
Error: Block 'pa' register 'config_reg' offset_addr=0x5000 exceeds CIF range [0x1000, 0x4000]
```

### 返回值

退出码 `1`

---

## 案例 3：校验失败（文件不存在或扩展名错误）

### 命令

```bash
gen-reg cif-check --json /tmp/nonexistent.json --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx
```

### 终端输出

```
Error: --json 不存在: /tmp/nonexistent.json
```

### 命令

```bash
gen-reg cif-check --json /tmp/example.json --cif /tmp/config.py
```

### 终端输出

```
Error: --cif 扩展名应为 .xlsx, .xls，但得到: .py (/tmp/config.py)
```

### 返回值

退出码 `1`
