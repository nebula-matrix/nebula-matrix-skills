# check 使用案例

## 案例 1：检查通过

对已提取的 JSON 执行常规检查，数据无误时输出 "检查通过"。

### 前置条件

已有一个检查通过的 JSON 文件。以下示例使用修复后的数据：

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --output /tmp/pass_extract.json \
  --prefix ASIC_PDT_V2R1
```

### 命令

```bash
gen-reg check --json /tmp/pass_extract.json
```

### 终端输出

```
检查通过
```

### 返回值

退出码 `0`

---

## 案例 2：检查失败（数据错误）

使用实际测试数据（含已知问题），检查会报出 `upa_ext_conf_table` 的宽度不匹配。

### 前置条件

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --output /tmp/fail_extract.json \
  --prefix ASIC_PDT_V2R1
```

### 命令

```bash
gen-reg check --json /tmp/fail_extract.json
```

### 终端输出

```
ERROR, module: pa reg: upa_ext_conf_table, offset_addr: 0x5000, reg_width(32) shoule be equal with all(field_bits)(28)!
```

### 返回值

退出码 `1`

### 问题说明

- **问题寄存器**：`upa_ext_conf_table`（offset: 0x5000）
- **问题**：寄存器声明宽度为 32，但各字段 bits 之和为 28
- **建议**：确认是否缺少 `rsv` 字段填充至 32 bit

---

## 案例 3：检查非 JSON 文件

校验会拦截扩展名不合法的文件。

### 命令

```bash
gen-reg check --json /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx
```

### 终端输出

```
Error: --json 扩展名应为 .json，但得到: .xlsx (/home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx)
```

### 返回值

退出码 `1`
