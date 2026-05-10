# NBL DOCX 转 Markdown — 技术原理与实现细节

## 处理流程

转换流程分为三个主要阶段，每个阶段包含若干自动化步骤：

### 阶段一：LibreOffice 转换与后处理
1. **LibreOffice 转换为 HTML** - 导出媒体到 `2. html_source_by_LibreOffice/` 目录
2. **HTML 后处理** - 修复章节标题格式（`<p>` → `<h1>`），将 `[xxx]` 转换为 `<code>[xxx]</code>`

### 阶段二：Markdown 生成与清理
3. **Pandoc 转换** - HTML 转 Markdown，复制资源到 `assets/`，修复路径，清理多余 HTML 标签

### 阶段三：验证与修复
4. **标题结构验证** - 生成 Pandoc 参考文件（`3. crosscheck_by_Pandoc/`），语义化对比一级标题

---

## 后处理细节

### 章节标题修复

LibreOffice 导出 HTML 时，Word 文档中的章节标题有时以 `<p>` 标签输出（如 `<p>8<font>初始化</font></p>`），而非标准 `<h1>`。后处理脚本通过正则表达式识别这些模式并转换为标准 `<h1>` 标签：

- **Pattern A0**: `<p page-break><a name>...</a><font>数字</font><font>标题</font></p>` → `<h1>数字 标题</h1>`
- **Pattern A0b**: `<p page-break><font>10DFX</font></p>` → `<h1>10 DFX</h1>`
- **Pattern A1-A4**: 处理数字与中文字符之间的空格

### 寄存器/表项标记

将 `[xxx]` 转换为 `<code>[xxx]</code>`，最终呈现为 `` `xxx` `` 代码格式：

```python
pattern = r'(\[[^<>]+?\])'
replacement = r'<code>\1</code>'
```

适用于技术文档中的寄存器域段、表项名称、配置字段等。

---

## Markdown 清理与优化

Pandoc 转换后会自动执行：
- 复制图片到 `assets/` 目录
- 更新图片路径为相对路径 `assets/`
- 将 `<img>` 标签转换为 Markdown 格式 `![alt](src)`
- 清理多余 HTML 标签（span、font、b、i 等），保留表格

生成的 Markdown 特点：
- 使用 CommonMark 格式
- **表格保留为 HTML 格式**（Markdown 表格能力有限）
- 图片引用使用相对路径 `assets/`
- 代码标记使用反引号

---

## 验证机制详解

### 标题提取

从主输出和 Pandoc 参考文件中分别提取 H1/H2/H3 标题：

```python
def extract_headings(md_path: Path) -> list[tuple[str, str]]:
    # 返回 [(level, title), ...]
    # level: 'h1', 'h2', 'h3'
    # 例如: ('h1', '2 模块特性')
```

### 语义化对比

1. **章节号连续性检查**：提取 H1 标题的前导数字，检查是否连续（1, 2, 3, ...）
2. **语义匹配**：移除章节编号后进行对比，检测遗漏/多余标题
3. **H2 对照**：当 Pandoc 参考无 H1 时，使用 H2 进行交叉验证

### 常见场景

| 场景 | 主输出 H1 | 参考 H1 | 说明 |
|------|-----------|---------|------|
| Word 标准样式 | 正确 | 正确 | 正常对比 |
| Word 自定义样式 | 正确（LibreOffice 修复） | 缺失 | 以主输出为准 |
| 第一章格式特殊 | 遗漏 | 可能正确/遗漏 | 需人工检查修复 |

---

## 依赖要求

- **LibreOffice** (`libreoffice` 命令) — DOCX 转 HTML
- **Pandoc** (`pandoc` 命令) — HTML 转 Markdown
- **python3-uno** (可选但推荐) — 接受 DOCX 审阅修订

安装：
```bash
sudo apt install libreoffice-writer pandoc python3-uno
```

验证：
```bash
libreoffice --version
pandoc --version
```

---

## 输出示例

```bash
$ python3 scripts/convert.py spec.docx --output-dir spec_convert/

📁 Work directory: spec_convert/
📁 HTML source: spec_convert/2. html_source_by_LibreOffice
📁 Markdown output: spec_convert/4. markdown_output

--- Step 0: Accept all revisions ---
✅ Using accepted revision file: spec_convert/1. docx_preprocessed/spec_accepted.docx

--- Step 1: LibreOffice DOCX -> HTML ---
✅ HTML created: spec_convert/2. html_source_by_LibreOffice/spec_source.html

--- Step 2: Post-processing HTML ---
✅ Post-processed: 334 bracket patterns converted, 16 headings fixed

--- Step 3: Generate Pandoc crosscheck reference ---
   Reference saved: spec_convert/3. crosscheck_by_Pandoc/spec_direct_pandoc_markdown_cross_check.md

--- Step 4: Pandoc HTML -> Markdown ---
✅ Markdown created: spec_convert/4. markdown_output/spec.md

--- Step 5: Copy assets ---
✅ Copied 23 images to assets/

--- Step 6: Fix markdown paths ---
✅ Image paths updated

--- Step 7: Clean HTML tags ---
✅ HTML tags cleaned (tables preserved, img -> markdown)

--- Step 8: Validate headings ---
   [主输出 - Main Output] 标题结构:
      H1 headings (11):
         1. 1 功能概述
         2. 2 模块特性
         ...
   [参考文档 - Pandoc Reference] 标题结构:
      H1 headings (0):
         (无H1标题 - Word文档章节标题未使用标准Heading 1样式)
   ...

==================================================
✅ Conversion complete!
   Markdown:  spec_convert/4. markdown_output/spec.md
   Check:     spec_convert/3. crosscheck_by_Pandoc/spec_direct_pandoc_markdown_cross_check.md
   Assets:    spec_convert/4. markdown_output/assets
   HTML:      spec_convert/2. html_source_by_LibreOffice
==================================================
```
