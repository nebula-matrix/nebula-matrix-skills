# nbl-testplan-generator

数字芯片验证测试计划生成器插件。

## 功能

- 从功能规格书（.docx）和寄存器手册（.xlsx）生成结构化测试点文档
- 支持 D->E->F->G 层级分解
- 自动交叉引用寄存器配置信息
- 生成 `fs_reg_slv_review.md` 记录不确定内容

## 已包含技能

### nbl-tp-func-gen

生成功能特性（Chapter 1）测试点，详见 `skills/nbl-tp-func-gen/SKILL.md`。

## 依赖

- Python >= 3.12
- openpyxl >= 3.1.0
- pytest >= 8.0.0（开发）
