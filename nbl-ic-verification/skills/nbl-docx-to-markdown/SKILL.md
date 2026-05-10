---
name: nbl-docx-to-markdown
description: NBL企业定制的 DOCX 转 Markdown 技能。将复杂的 Word 文档转换为完整 Markdown 格式，支持处理图片、Visio 图表、表格，并优化文档结构。特别适用于包含寄存器描述、表项定义等技术文档转换。能够将 [xxx] 格式的寄存器域段、表项标记自动转换为 `[xxx]` 代码格式。
---

# NBL DOCX 转 Markdown

## 快速开始

```bash
python3 scripts/convert.py <input.docx>
```

**使用流程**：
1. 调用 `convert.py` 执行转换
2. **观察 LOG 输出**，关注标题验证阶段的检测结果
3. 若检测到章节遗漏或标题不连续，**修复输出的 Markdown**
4. 确保最终 Markdown 标题结构完整、可消费

[详细技术原理与实现说明 → 参考文档](references/technical_details.md)

---

## 关键步骤

### 1. 执行转换

```bash
# 基本用法（推荐）
# 脚本自动基于 docx 文件名创建工作目录，空格自动转为下划线
python3 scripts/convert.py input.docx

# 指定工作目录（可选）
python3 scripts/convert.py input.docx --output-dir <doc_name>_convert/
```

> **参数说明**：
> - `--output-dir`: 显式指定工作目录路径。注意：不指定此参数时，脚本会自动基于 docx 文件名创建目录，空格自动转为下划线；若显式指定路径，路径中的空格不会自动处理，建议手动替换为 `_`。

输出目录结构（按处理顺序）：

```
<doc_name>_convert/
├── 1. docx_preprocessed/           # 接受修订后的 docx
├── 2. html_source_by_LibreOffice/  # LibreOffice HTML 输出
├── 3. crosscheck_by_Pandoc/        # Pandoc 交叉参考文件
└── 4. markdown_output/             # 最终 Markdown 输出
    ├── *.md                        # 主输出文件
    └── assets/                     # 图片资源
```

### 2. 检查 LOG 输出（重要）

转换脚本会打印详细的标题验证信息，**必须关注**以下内容：

**标题结构列表**：
```
[主输出 - Main Output] 标题结构:
   H1 headings (10):
      1. 2 模块特性
      2. 3 参考文档
      ...
   H2 headings (14):
      ...

[参考文档 - Pandoc Reference] 标题结构:
   H1 headings (0):
      (无H1标题)
```

**章节遗漏检测**：
```
⚠️  [章节遗漏检测] H1章节号不连续，以下章节可能缺失: 1
   当前章节序列: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
   预期章节序列: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
```

**说明**：
- Pandoc 参考仅用于交叉比对，不一定完全正确（Word 非标准样式时 Pandoc 也会丢失标题）
- 最终目标是**主输出的 Markdown 标题结构完整、可消费**

### 3. 修复 Markdown 标题（按需）

**何时需要修复**：
- LOG 中显示章节号不连续（如从 `2` 开始，缺少 `1`）
- H1 标题数量明显少于文档实际章节数
- 某些章节内容在 Markdown 中以普通文本存在，而非 `# ` 标题

**修复方法**：
1. 读取主输出 Markdown 文件（`4. markdown_output/*.md`）
2. 找到被遗漏的章节内容（通常是 `1**功能概述**` 或普通文本）
3. 修正为标准 Markdown 标题格式：
   ```markdown
   # 1 功能概述
   
   # 2 模块特性
   ```
4. 确保章节编号连续，层级正确

**不要**：
- 不要修改原始 Word 文档（无法消费）
- 不要复制 Pandoc 参考文件的其他内容（表格、图片路径等可能不如主输出）
- 不要完全信任 Pandoc 参考（其自身也可能遗漏标题）

### 4. 确认输出

修复后确认：
- 所有章节都有对应的 `# ` H1 标题
- 子章节有对应的 `## ` H2 标题
- 图片路径正确（`assets/` 目录下）
- 表格保留为 HTML 格式（正常）

---

## 注意事项

1. **标题检测是必选项** — 必须观察 LOG 中的标题验证结果
2. **Pandoc 参考不一定正确** — Word 非标准样式时 Pandoc 也会丢失标题
3. **最终目标是 Markdown 结构合理** — 确保后续 `nbl-testplan` 等工具能正确解析
4. **仅修复标题层级** — 保持主输出的表格格式、图片路径等内容不变
