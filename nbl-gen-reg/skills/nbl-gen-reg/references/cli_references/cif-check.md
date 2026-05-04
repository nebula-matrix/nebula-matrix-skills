# cif-check

验证寄存器地址是否落在 CIF 地址映射表定义的模块地址空间内。

## 参数

| 参数 | 短选项 | 类型 | 必填 | 说明 |
|-----|-------|------|-----|-----|
| `--json` | `-j` | TEXT | 是 | 由 `gen-reg extract` 生成的 JSON 文件路径 |
| `--cif` | `-c` | TEXT | 是 | CIF 地址映射 Excel 文件路径 |

## 示例

```bash
gen-reg cif-check --json reg_data.json --cif ASIC_PDT_V3R1_CIF.xlsx
```

## 返回值

- 全部通过：输出 `CIF 检查通过`，退出码 0
- 存在错误：列出所有错误并退出码 1
