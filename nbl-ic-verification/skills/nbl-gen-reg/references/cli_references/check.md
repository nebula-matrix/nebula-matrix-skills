# check

对 `extract` 生成的 JSON 进行常规数据一致性检查。

## 参数

| 参数 | 短选项 | 类型 | 必填 | 说明 |
|-----|-------|------|-----|-----|
| `--json` | `-j` | TEXT | 是 | 由 `gen-reg extract` 生成的 JSON 文件路径 |

## 检查项

- `offset_addr` 是否为 4 的倍数
- `offset_addr` 是否在同 Block 内重复
- `reg_name` 是否在同 Block 内重复
- `reg_width` 是否等于所有 `field_bits` 之和
- `tbl` 类型寄存器之后是否出现非 `tbl` 类型寄存器
- `tbl` width 是否小于 1024

## 示例

```bash
gen-reg check --json reg_data.json
```

## 返回值

- 全部通过：输出 `检查通过`，退出码 0
- 存在错误：列出所有错误并退出码 1
