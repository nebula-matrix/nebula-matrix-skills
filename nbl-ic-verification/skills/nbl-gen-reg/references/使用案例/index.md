# 使用案例索引

本文档汇总 `gen-reg` 各指令的实际使用案例。所有案例均基于 `/home/alvin.xu/test_center/sheet/` 目录下的真实 Excel 文件编写。

## 可用测试文件

| 文件名 | 说明 |
|--------|------|
| `ASIC_PDT_V2R1_ppe_pa.xlsx` | pa 模块 |
| `ASIC_PDT_V2R1_ppe_ipro.xlsx` | ipro 模块 |
| `ASIC_PDT_V2R1_datapath_bm.xlsx` | bm 模块 |
| `ASIC_PDT_V2R1_datapath_ped.xlsx` | ped 模块 |

## 指令案例目录

| 指令 | 文件 | 说明 |
|------|------|------|
| extract | [extract.md](extract.md) | 从 Excel 提取寄存器数据 |
| check | [check.md](check.md) | 数据一致性检查 |
| cif-check | [cif-check.md](cif-check.md) | CIF 地址范围检查 |
| filter | [filter.md](filter.md) | 筛选 BT / 列出 BT |
| regslv | [regslv.md](regslv.md) | 生成 reg_slv Verilog |
| ral | [ral.md](ral.md) | 生成 UVM RAL 模型 |
| cfg | [cfg.md](cfg.md) | 生成寄存器配置表 |
| help | [help.md](help.md) | 查看帮助 |

## 输出文件预览说明

案例中的输出路径使用 `/tmp/example_*` 作为演示，实际使用时请替换为项目中的目标目录。
