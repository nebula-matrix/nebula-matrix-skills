# nbl-testplan-generator

数字芯片验证测试计划生成器插件。从功能规格书（.docx）和寄存器配置手册（.xlsx）生成功能特性（Chapter 1）的结构化测试点 xlsx 文档。

## 功能

- **自动文档转换**: 调用 `nbl-docx-to-markdown` skill 将 Word 功能规格书转换为 Markdown
- **结构化解析**: 将 Markdown 解析为 `spec_tree.json`，提取模块特性和交叉引用索引
- **寄存器解析**: 将寄存器手册 xlsx 解析为 `reg_info.json`
- **智能分析**: Claude 按 Feature 分块交叉引用分析，自动生成 D→E→F→G 层级分解
- **覆盖率路径**: 自动生成基于英文缩写 `_eng_id` 的 SystemVerilog 覆盖率路径（W 列）
- **审查记录**: 生成 `fs_reg_slv_review.md` 记录不确定内容，支持二次刷新

## 已包含技能

### nbl-tp-func-gen

生成功能特性（Chapter 1）测试点文档。

**触发方式**: 在 Claude Code 中输入 `/nbl-tp-func-gen`，后接功能规格书路径和寄存器手册路径。

**示例**:
```
/nbl-tp-func-gen 从 /path/to/spec.docx 和 /path/to/reg.xlsx 生成测试点
```

**输入要求**:
1. 功能规格书路径（.docx）
2. 寄存器配置手册路径（.xlsx）
3. 输出目录（可选，默认 $HOME）
4. 验证层次（可选，默认 BT）

**输出文件**:
- `{output_dir}/testplan_func.xlsx` — 主输出：结构化测试点文档
- `{output_dir}/fs_reg_slv_review.md` — 审查记录：不确定内容汇总
- `{output_dir}/spec_tree.json` — 规格书结构化 JSON（中间产物）
- `{output_dir}/reg_info.json` — 寄存器配置 JSON（中间产物）
- `{output_dir}/testplan_func_raw.json` — 测试点原始 JSON（中间产物）

## 技术栈

- Python >= 3.12
- openpyxl >= 3.1.0
- pytest >= 8.0.0（开发）
- LibreOffice + Pandoc（通过 nbl-docx-to-markdown）

## 目录结构

```
nbl-testplan-generator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── nbl-tp-func-gen/
│       ├── SKILL.md                          # Claude 执行指令
│       ├── reference/
│       │   ├── spec_input/                   # 功能规格系统提示词
│       │   └── template/                     # 测试点 xlsx 模板
│       └── scripts/
│           ├── parsers/
│           │   ├── md_parser.py              # Markdown -> spec_tree.json
│           │   └── reg_parser.py             # xlsx -> reg_info.json
│           ├── writers/
│           │   └── combine_writer.py         # JSON -> xlsx
│           ├── review/
│           │   └── review_writer.py          # JSON -> review.md
│           ├── reg_to_json.py                # 寄存器解析 CLI
│           └── tp_gen.py                     # 统一 CLI 入口
└── tests/                                    # 测试目录
```

## 测试

```bash
cd nbl-testplan-generator
uv run pytest tests/ -v
```

## D→E→F→G 层级说明

| 列 | 层级 | 说明 |
|---|---|---|
| D | Feature | 顶层特性（如：报文编辑范围） |
| E | Subfeature L1 | 一级子特性（如：替换动作） |
| F | Subfeature L2 | 二级子特性概述（如：正常场景-TTL字段替换） |
| G | Subfeature L3 | 三级子特性详情（最小粒度，如：TTL=128替换为64） |

## License

企业内部使用。
