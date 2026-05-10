# gen-reg CLI 指令索引

> gen_reg_tools 命令行工具的全局说明和指令索引。

---

## 命令格式

```bash
gen-reg <command> [options]
```

## 通用约定

- 参数以 `--` 长选项或 `-` 短选项形式提供
- 必填参数在帮助中标记为 `[required]`
- 可选参数有默认值时会显示默认值
- 布尔型参数（如 `--check`）无需传值，存在即为 `True`
- 所有路径参数均会自动校验：文件存在性和扩展名合法性

## 输入校验规则

| 参数类型 | 允许的扩展名 | 失败行为 |
|---------|------------|---------|
| `--json` | `.json` | 打印错误并退出（退出码 1） |
| `--excel` | `.xlsx`, `.xls` | 打印错误并退出（退出码 1） |
| `--cif` | `.xlsx`, `.xls` | 打印错误并退出（退出码 1） |
| `--cfg` | `.py` | 打印错误并退出（退出码 1） |
| `--excel-dir` | 目录 | 校验目录存在性 |

校验示例：

```bash
gen-reg check --json data.txt
# Error: --json 扩展名应为 .json，但得到: .txt (data.txt)

gen-reg extract --excel data.csv
# Error: --excel 扩展名应为 .xlsx, .xls，但得到: .csv (data.csv)
```

## 指令列表

| 指令 | 说明 | 文档 |
|-----|-----|------|
| `extract` | 从 Excel 提取寄存器数据并导出为 JSON | [extract.md](extract.md) |
| `check` | 对提取结果进行常规检查 | [check.md](check.md) |
| `cif-check` | 检查寄存器地址是否在 CIF 定义的地址范围内 | [cif-check.md](cif-check.md) |
| `filter` | 按 BT 名称筛选 JSON 数据，或列出所有 BT | [filter.md](filter.md) |
| `regslv` | 生成 reg_slv Verilog 代码 | [regslv.md](regslv.md) |
| `ral` | 生成 UVM RAL 模型 | [ral.md](ral.md) |
| `cfg` | 生成寄存器配置表（SystemVerilog） | [cfg.md](cfg.md) |
| `help` | 显示完整使用指南 | [help.md](help.md) |

## 获取子命令帮助

```bash
gen-reg <command> --help
```
