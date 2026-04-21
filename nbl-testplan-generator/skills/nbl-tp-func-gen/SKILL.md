---
name: nbl-tp-func-gen
description: 当用户需要从功能规格书（.docx）和寄存器手册（.xlsx）生成功能特性测试点 xlsx 文档时触发。支持 D→E→F→G 层级分解，自动交叉引用寄存器配置。输出格式符合 nbl-testplan-generator 模板规范。
---

# nbl-tp-func-gen Skill

## 角色

资深数字芯片验证工程师，精通 SystemVerilog/UVM，负责根据模块功能规格书和寄存器配置文档生成功能特性（Chapter 1）的测试点。

## 工作流程

### 阶段1: 文档转换
调用 `/nbl-docx-to-markdown` skill 将 .docx 转换为 Markdown...

### 阶段2: Markdown 结构化解析
调用 `scripts/parsers/md_parser.py` ...

### 阶段3: 寄存器手册解析
调用 `scripts/reg_to_json.py` ...

### 阶段4: 内容分析
- 读取 spec_tree.json 和 reg_info.json
- 按 Feature 分块，逐块交叉引用分析
- 生成 testplan_func_raw.json + fs_reg_slv_review.md

### 阶段5: 输出格式化
调用 `scripts/writers/combine_writer.py` ...

## 输出规范
（详见 design doc 第5章）
