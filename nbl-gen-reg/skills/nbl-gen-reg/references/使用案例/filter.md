# filter 使用案例

## 案例 1：从 JSON 按 BT 级别筛选

使用 `--level bt` 按 Block 名称白名单筛选。仅保留指定 BT，不进一步过滤 register 或 field。

### 前置条件

```bash
gen-reg extract \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx \
  --output /tmp/example_multi.json \
  --prefix ASIC_PDT_V2R1
```

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --level bt \
  --bt pa \
  --output /tmp/pa_only.json
```

### 终端输出

```
筛选完成: /tmp/pa_only.json
```

### 结果预览

```bash
$ python3 -c "
from gen_reg_tools.core.data_model import RegData
data = RegData.from_json('/tmp/pa_only.json')
print(f'Blocks: {len(data.subpart)}')
for b in data.subpart:
    print(f'  - {b.name}: {len(b.subpart)} registers')
"
```

输出：

```
Blocks: 1
  - pa: 143 registers
```

---

## 案例 2：从 Excel 直接按 BT 级别筛选

跳过 JSON 中间步骤，直接从 Excel 文件按 BT 级别筛选。

### 命令

```bash
gen-reg filter \
  --excel /home/alvin.xu/test_center/sheet/ASIC_PDT_V2R1_ppe_ipro.xlsx \
  --level bt \
  --bt ipro \
  --output /tmp/ipro_only.json
```

### 终端输出

```
筛选完成: /tmp/ipro_only.json
```

---

## 案例 3：向后兼容：不带 --level 直接用 --bt 筛选

`--bt` 单独使用时默认进入 `register` 级别，BT 名称作为白名单条件之一。效果与 `--level bt --bt` 类似。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt pa \
  --output /tmp/pa_compat.json
```

### 终端输出

```
筛选完成: /tmp/pa_compat.json
```

### 结果说明

与 `--level bt --bt pa` 效果相同，保留 `pa` Block 下的所有 registers 和 fields。

---

## 案例 4：按 rw_attr 筛选 registers

筛选包含 `rw` 属性字段的 registers。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt pa \
  --rw-attr rw \
  --output /tmp/pa_rw_regs.json
```

### 终端输出

```
筛选完成: /tmp/pa_rw_regs.json
```

### 结果验证

```bash
$ python3 -c "
from gen_reg_tools.core.data_model import RegData
d = RegData.from_json('/tmp/pa_rw_regs.json')
for r in d.subpart[0].subpart[:3]:
    rw_fields = [f.name for f in r.subpart if f.rw_attr == 'rw']
    print(f'{r.name}: {len(rw_fields)} rw fields')
"
```

---

## 案例 5：按 reg_type 筛选

筛选 `tbl` 类型的 registers。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt pa \
  --reg-type tbl \
  --output /tmp/pa_tbl_regs.json
```

### 终端输出

```
筛选完成: /tmp/pa_tbl_regs.json
```

### 结果验证

```bash
$ python3 -c "
from gen_reg_tools.core.data_model import RegData
d = RegData.from_json('/tmp/pa_tbl_regs.json')
for r in d.subpart[0].subpart:
    print(f'{r.name}: type={r.reg_type}')
"
```

---

## 案例 6：综合多条件筛选（与逻辑）

同时使用多个条件，结果必须同时满足所有条件。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt pa \
  --rw-attr rw \
  --depth 1 \
  --reg-type reg \
  --output /tmp/pa_combined.json
```

### 终端输出

```
筛选完成: /tmp/pa_combined.json
```

### 结果说明

输出包含满足以下所有条件的 registers：
- 属于 `pa` Block
- reg_type 为 `reg`
- depth 等于 `1`
- 包含至少一个 `rw_attr == "rw"` 的 field

---

## 案例 7：按 depth 范围筛选

使用范围表达式筛选 depth 大于 1 的 registers。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt pa \
  --depth ">1" \
  --output /tmp/pa_deep_regs.json
```

### 支持的 depth/width 范围表达式

| 格式 | 含义 | 示例 |
|------|------|------|
| `N` | 精确等于 N | `--depth 1` |
| `>N` | 大于 N | `--depth ">1"` |
| `>=N` | 大于等于 N | `--depth ">=2"` |
| `<N` | 小于 N | `--depth "<10"` |
| `<=N` | 小于等于 N | `--depth "<=5"` |
| `N-M` | 范围 N 到 M（含） | `--depth "1-10"` |

---

## 案例 8：field 级别筛选

筛选出满足条件的 fields，而不是整个 registers。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt pa \
  --level field \
  --rw-attr rw \
  --output /tmp/pa_rw_fields.json
```

### 终端输出

```
筛选完成: /tmp/pa_rw_fields.json
```

### 结果说明

输出只包含 `rw_attr == "rw"` 的 fields，每个 register 中不匹配的 fields 被移除。若一个 register 没有匹配的 fields，则整个 register 被移除。

---

## 案例 9：field 级别 + field 名正则筛选

结合 field 级别条件和 field name 正则匹配。

### 命令

```bash
gen-reg filter \
  --json /tmp/example_multi.json \
  --bt bm \
  --level field \
  --rw-attr rw \
  --field-regex 'en$' \
  --output /tmp/bm_en_fields.json
```

### 结果说明

筛选 `bm` Block 中所有 `rw_attr == "rw"` 且 name 以 `en` 结尾的 fields。

---

## 案例 10：从 JSON 列出所有 BT（--get-bt）

不执行筛选，仅列出 JSON 中所有 block_type 为 "bt" 的 Block 名称。

### 命令

```bash
gen-reg filter --get-bt --json /tmp/example_multi.json
```

### 终端输出

```
共找到 1 个 BT 模块：
  - pa
```

---

## 案例 11：从 Excel 单文件列出 BT

直接从 Excel 提取后列出 BT，无需先生成 JSON。

### 命令

```bash
gen-reg filter \
  --get-bt \
  --excel /home/alvin.xu/test_center/sync_rslt-main/2_Reg/Src/ASIC_PDT_V2R1_ppe_pa.xlsx
```

### 终端输出

```
共找到 1 个 BT 模块：
  - pa
```

---

## 案例 12：从 Excel 目录批量列出 BT

遍历目录下所有有效 Excel，提取后合并列出所有 BT。

### 命令

```bash
gen-reg filter \
  --get-bt \
  --excel-dir /home/alvin.xu/test_center/sheet \
  --prefix ASIC_PDT_V2R1
```

### 终端输出

```
共找到 4 个 BT 模块：
  - pa
  - ipro
  - bm
  - ped
```

---

## 案例 13：缺少输入参数

筛选模式下未指定 `--json` 或 `--excel`，会报错。

### 命令

```bash
gen-reg filter --bt pa -o /tmp/out.json
```

### 终端输出

```
Error: 请指定 --json 或 --excel
```

### 返回值

退出码 `1`

---

## 案例 14：缺少过滤条件

输入源已指定但未提供任何过滤条件，会报错。

### 命令

```bash
gen-reg filter --json /tmp/example_multi.json -o /tmp/out.json
```

### 终端输出

```
Error: 请至少指定一个过滤条件（如 --bt, --rw-attr, --reg-type 等）
```

### 返回值

退出码 `1`
