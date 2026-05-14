# nbl-ic-verification

NBL IC 验证工具集合插件。面向芯片验证工程师提供文档转换、测试点生成与寄存器建模能力。

## 包含技能

### 1. nbl-docx-to-markdown — DOCX 转 Markdown

将 Word 技术文档转换为 Markdown 格式。

**触发方式**: `/nbl-docx-to-markdown <docx路径>`

### 2. nbl-gen-reg — 寄存器生成工具

从 Excel 寄存器手册提取数据，生成 Verilog / UVM RAL / 配置表。

**触发方式**: `/nbl-gen-reg <命令> [参数]`

### 3. nbl-testplan-creator — Markdown-first 测试计划生成器

采用 Markdown-first 工作流，从规格文档逐章节生成结构化测试点。

**触发方式**: `/nbl-testplan-creator <docx路径>`

## 技术栈

- Python >= 3.12（通过 uv 管理）
- openpyxl >= 3.1.0
- LibreOffice + Pandoc（docx 转换）

## 依赖管理

所有脚本调用均通过 `uv run` 执行，不直接使用系统 Python 或 pip/apt。

## 目录结构

```
nbl-ic-verification/
├── skills/
│   ├── nbl-docx-to-markdown/    # DOCX 转 Markdown 技能
│   ├── nbl-gen-reg/             # 寄存器生成技能
│   └── nbl-testplan-creator/    # 测试计划生成器（Markdown-first）
├── README.md
└── pyproject.toml
```

## License

企业内部使用。
