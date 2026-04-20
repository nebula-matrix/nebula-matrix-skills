---
name: nbl-docx-to-markdown
description: NBL企业定制的 DOCX 转 Markdown 技能。将复杂的 Word 文档转换为完整 Markdown 格式，支持处理图片、Visio 图表、表格，并优化文档结构。特别适用于包含寄存器描述、表项定义等技术文档转换。能够将 [xxx] 格式的寄存器域段、表项标记自动转换为 `[xxx]` 代码格式。
---

# NBL DOCX 转 Markdown

## 工作流程

转换流程分为三个主要阶段，每个阶段包含若干自动化步骤：

### 阶段一：LibreOffice 转换与后处理
1. **LibreOffice 转换为 HTML** - 导出媒体到 `html_source/` 目录
2. **HTML 后处理** - 修复章节标题格式（`<p>` → `<h1>`），将 `[xxx]` 转换为 `<code>[xxx]</code>`

### 阶段二：Markdown 生成与清理
3. **Pandoc 转换** - HTML 转 Markdown，复制资源到 `assets/`，修复路径，清理多余 HTML 标签

### 阶段三：验证与修复
4. **标题结构验证与修复** - 生成 Pandoc 参考文件，语义化对比一级标题，发现差异时必须修复

## 使用方法

```bash
# 基本用法 - 输出到默认目录
python3 scripts/convert.py <input.docx>

# 指定输出目录
python3 scripts/convert.py <input.docx> --output-dir <directory>

# 指定 Markdown 文件名
python3 scripts/convert.py <input.docx> --output <output.md>
```

## 转换流程

### 1. 创建目录结构

所有文件名中的空格自动转换为下划线 `_`：

```
<basename>_work/              # 工作目录（空格转下划线）
├── html_source/              # LibreOffice 原始输出
│   ├── <basename>_source.html    # 原始 HTML
│   ├── <basename>_processed.html # 后处理 HTML（修复标题、[xxx]等）
│   └── *.png                  # 原始图片
└── markdown_output/           # 最终输出
    ├── <basename>.md          # Markdown 文件（与输入同名）
    ├── <basename>_direct_pandoc_markdown_cross_check.md # Pandoc 直接转换（用于验证）
    └── assets/                # 图片副本
```

### 2. 后处理细节

HTML 后处理会执行以下操作：

**章节标题修复**
- 识别 LibreOffice 以 `<p>` 标签输出的章节标题（如 `<p>8<font>初始化</font></p>`）
- 转换为标准 `<h1>` 标签，确保 Pandoc 正确识别为一级标题
- 处理多种格式变体（嵌套 `<font>`、`<span>`、数字文本混合等）

**寄存器/表项标记**
- 将 `[xxx]` 转换为 `<code>[xxx]</code>`，最终呈现为 `` `xxx` `` 代码格式
- 适用于技术文档中的寄存器域段、表项名称、配置字段等

### 3. Markdown 清理与优化

Pandoc 转换后会自动执行：
- 复制图片到 `markdown/assets/` 目录
- 更新图片路径为相对路径 `assets/`
- 将 `<img>` 标签转换为 Markdown 格式 `![alt](src)`
- 清理多余 HTML 标签（span、font、b、i 等），保留表格

生成的 Markdown 特点：
- 使用 CommonMark 格式
- **表格保留为 HTML 格式**（Markdown 表格能力有限）
- 图片引用使用相对路径 `assets/`
- 代码标记使用反引号

### 4. 验证与修复机制

**验证步骤为必选项，发现差异必须修复。**

**自动对比**
1. 使用 Pandoc 直接转换 DOCX 生成参考文件
2. 提取两个版本的一级标题进行语义对比（移除章节编号后比较）
3. 报告差异：
   - `❌ MISSING`: 参考文件中有但主输出缺少的章节
   - `⚠️ EXTRA`: 主输出中有但参考文件没有的章节

**强制修复流程**
当验证发现标题结构不一致时，必须执行以下修复：

1. **分析差异** - 对比主输出和 `_direct_pandoc_markdown_cross_check.md` 中的标题列表
2. **语义化修复** - 直接使用 Edit 能力修复主输出的 MD 文件：
   - 参考 `_direct_pandoc_markdown_cross_check.md` 中的一级标题（通常正确）
   - 在主输出 MD 中添加缺失的一级标题、修正错误标题
   - 保持原有内容结构，仅修正标题层级
3. **重新验证** - 确认修复后的一级标题结构与参考文件一致

**注意事项**：
- Pandoc 直接转换的一级标题通常正确，其他部分（表格、图片路径等）可能不如主输出
- 仅参考一级标题，不要复制参考文件的其他内容
- 修复时保持主输出的表格格式和图片路径
- **序号处理**：`_direct_pandoc_markdown_cross_check.md` 的一级标题会丢失序号，仅参考标题文本确认章节是否遗漏；补充 `#` 符号时，序号保留主输出中的原有格式

修复完成前，转换不视为成功。

## 依赖要求

- LibreOffice (`libreoffice` 命令)
- Pandoc (`pandoc` 命令)

安装依赖：
```bash
# Ubuntu/Debian
sudo apt install libreoffice-writer pandoc

# macOS
brew install libreoffice pandoc
```

## 输出示例

```bash
$ python3 scripts/convert.py spec.docx

📁 Work directory: spec_work/
📁 HTML source: spec_work/html_source
📁 Markdown output: spec_work/markdown_output

--- Phase 1: LibreOffice Conversion & Post-processing ---
✅ HTML created: spec_work/html_source/spec_source.html
✅ Post-processed: 334 bracket patterns converted, 16 headings fixed

--- Phase 2: Markdown Generation & Cleanup ---
✅ Markdown created: spec_work/markdown_output/spec.md
✅ Copied 23 images to assets/
✅ Image paths updated
✅ HTML tags cleaned (tables preserved, img -> markdown)

--- Phase 3: Verification & Fix ---
✅ Heading structure validated (semantics match reference)
   (If differences found, fix Pattern A0/A0b in convert.py and re-run)

==================================================
✅ Conversion complete!
   Markdown:  spec_work/markdown_output/spec.md
   Check:     spec_work/markdown_output/spec_direct_pandoc_markdown_cross_check.md
   Assets:    spec_work/markdown_output/assets
   HTML:      spec_work/html_source
==================================================
```
