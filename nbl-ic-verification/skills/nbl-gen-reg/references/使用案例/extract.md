# extract 使用案例

## 案例 1：从单个 Excel 提取（不带 CIF）

从单个 Excel 文件提取寄存器数据，不指定 CIF 地址映射。

### 命令

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --output /tmp/example_extract.json \
  --prefix ASIC_PDT_V2R1
```

### 终端输出

```
提取完成: /tmp/example_extract.json
```

### 结果预览

```bash
$ ls -lh /tmp/example_extract.json
-rw-rw-r-- 1 user user 223K May  3 12:00 /tmp/example_extract.json

$ python3 -c "
from gen_reg_tools.core.data_model import RegData
data = RegData.from_json('/tmp/example_extract.json')
print(f'Block: {data.subpart[0].name}')
print(f'Registers: {len(data.subpart[0].subpart)}')
"
```

输出：

```
Block: pa
Registers: 143
```

---

## 案例 2：从单个 Excel 提取（带 CIF）

从单个 Excel 提取，同时指定 CIF 地址映射文件。

### 命令

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx \
  --output /tmp/example_extract_cif.json \
  --prefix ASIC_PDT_V2R1
```

### 终端输出

```
提取完成: /tmp/example_extract_cif.json
```

---

## 案例 3：从目录批量提取

遍历目录下所有符合前缀格式的 Excel 文件，批量提取。

### 命令

```bash
gen-reg extract \
  --excel-dir /home/alvin.xu/test_center/sheet \
  --output /tmp/example_dir_extract.json \
  --prefix ASIC_PDT_V2R1
```

### 终端输出

```
提取完成: /tmp/example_dir_extract.json
```

### 结果预览

```bash
$ python3 -c "
from gen_reg_tools.core.data_model import RegData
data = RegData.from_json('/tmp/example_dir_extract.json')
for block in data.subpart:
    print(f'Block: {block.name}, Registers: {len(block.subpart)}')
"
```

输出（示例，实际取决于目录中的有效文件）：

```
Block: pa, Registers: 143
Block: ipro, Registers: 89
Block: bm, Registers: 56
```

---

## 案例 4：提取并自动检查

提取完成后立即执行常规检查和 CIF 检查。

### 命令

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --cif ./ASIC_PDT_V2R1_CIF地址映射.xlsx \
  --check \
  --cif-check \
  --output /tmp/example_extract_checked.json \
  --prefix ASIC_PDT_V2R1
```

### 终端输出（检查通过时）

```
检查通过
CIF 检查通过
提取完成: /tmp/example_extract_checked.json
```

### 终端输出（检查失败时）

```
ERROR, module: pa reg: upa_ext_conf_table, offset_addr: 0x5000, reg_width(32) shoule be equal with all(field_bits)(28)!
```

此时命令退出码为 1，需要修复数据后重新提取。
