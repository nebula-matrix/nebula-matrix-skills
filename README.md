# Nebula Matrix Skills

这是 Nebula Matrix 技能市场，提供企业级生产力工具和自动化解决方案。

## 目录结构

```
nebula-matrix-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace 配置文件
├── nbl-ppt-builder/              # NBL PPT 构建工具插件
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件配置
│   ├── skills/
│   │   └── nbl-ppt-builder/
│   │       ├── SKILL.md         # 技能主文件
│   │       ├── reference/       # 参考文档
│   │       ├── scripts/         # 执行脚本
│   │       └── templates/       # 模板文件
│   └── README.md
├── nbl-skill-constructor/        # NBL 技能构造器插件
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件配置
│   └── skills/
│       └── nbl-skill-constructor/
│           ├── SKILL.md         # 技能主文件
│           ├── references/      # 参考文档
│           └── scripts/         # 执行脚本
├── nbl-ic-verification/          # NBL IC 验证工具集合插件
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件配置
│   ├── skills/
│   │   ├── nbl-docx-to-markdown/  # DOCX 转 Markdown 技能
│   │   │   ├── SKILL.md         # 技能主文件
│   │   │   ├── assets/          # 资源文件
│   │   │   ├── references/      # 参考文档
│   │   │   └── scripts/         # 执行脚本
│   │   └── nbl-testplan-generator/ # 测试计划生成技能
│   │       ├── SKILL.md         # 技能主文件
│   │       ├── references/      # 参考文档
│   │       └── scripts/         # 执行脚本
│   ├── tests/                   # 测试文件
│   ├── README.md                # 插件文档
│   └── pyproject.toml           # 项目配置
├── nbl-testplan-creator/         # NBL IC 验证测试计划生成器插件（Markdown-first）
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件配置
│   └── skills/
│       └── nbl-testplan-creator/
│           ├── SKILL.md         # 技能主文件
│           ├── references/      # 参考文档
│           └── scripts/         # 执行脚本
├── nbl-gen-reg/                  # NBL IC 寄存器生成工具插件
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件配置
│   ├── skills/
│   │   └── nbl-gen-reg/
│   │       ├── SKILL.md         # 技能主文件
│   │       ├── references/      # 参考文档
│   │       └── scripts/         # Python 代码与 CLI
│   └── README.md
└── README.md                     # 本文件
```

## 已包含的插件

### nbl-ppt-builder

**描述**: NBL 企业 PPT 构建工具，包含标准模板、配色方案和内容规范

**分类**: productivity

**标签**: ppt, presentation, document, templates

**功能**:
- 使用 HTML 模板生成企业 PPT
- 支持标准配色方案和布局
- 自动转换为 PPTX 格式
- 包含封面、内容、结尾等模板

### nbl-skill-constructor

**描述**: NBL 企业技能构造规范与开发指南，用于在 workspace 中创建和调试符合 NBL 标准的 skill

**分类**: development

**标签**: skill, development, creator, tool

**功能**:
- 在 workspace 中初始化技能目录结构
- 提供标准化的 skill 开发模板
- 包含脚本复杂度决策树和最佳实践指导
- 支持技能打包和验证工具
- 帮助开发者快速创建符合规范的 Claude Code 技能

### nbl-ic-verification

**描述**: NBL IC 验证工具集合，面向芯片验证工程师提供文档转换与测试点生成能力

**分类**: development

**标签**: ic, verification, testplan, docx, markdown, chip

**包含技能**:

**1. nbl-docx-to-markdown** — DOCX 转 Markdown 工具
- 使用 LibreOffice + Pandoc 将 Word 文档转换为 Markdown
- 支持处理图片、Visio图表，自动复制到 assets 目录
- 保留表格为 HTML 格式以确保兼容性
- 自动修复章节标题格式，将 `[xxx]` 标记转换为代码格式
- 验证转换结果，发现结构差异时强制修复
- 特别适用于包含寄存器描述、表项定义等技术文档

**2. nbl-testplan-generator** — 测试计划生成器
- 调用 `nbl-docx-to-markdown` skill 将 Word 功能规格书转换为 Markdown
- 将 Markdown 解析为 `spec_tree.json`，提取模块特性和交叉引用索引
- 将寄存器手册 xlsx 解析为 `reg_info.json`
- Claude 按 Feature 分块交叉引用分析，自动生成 D→E→F→G 层级分解
- 自动生成基于英文缩写 `_eng_id` 的 SystemVerilog 覆盖率路径（W 列）
- 生成 `fs_reg_slv_review.md` 记录不确定内容，支持二次刷新

### nbl-testplan-creator

**描述**: NBL 企业 IC 验证测试计划生成器，采用 Markdown-first 工作流从规格文档逐章节生成结构化测试点

**分类**: development

**标签**: testplan, verification, chip, testpoint

**功能**:
- 采用 Markdown-first 工作流，全程以 Markdown 为唯一工作文件
- 逐章节串行分析测试点，失败不污染已有数据
- 自动生成 Feature / SubFeature / Testpoint 层级编码 ID
- 提供 `nbl-testplan` CLI 工具支持构建、格式化、合并、检查
- 支持子 Agent 分组并行处理大文档

### nbl-gen-reg

**描述**: NBL IC寄存器生成工具插件。从Excel寄存器手册提取数据，生成reg_slv Verilog、UVM RAL模型、寄存器配置表，支持数据校验和多维度筛选

**分类**: development

**标签**: register, verilog, uvm, ral, chip, verification

**功能**:
- 从Excel寄存器手册提取结构化JSON数据，支持单文件或目录批量提取
- 执行常规数据一致性检查和CIF地址范围校验
- 按BT/register/field级别多维度条件筛选寄存器数据
- 生成reg_slv Verilog模块（支持APB/AXI-Lite总线接口）
- 生成UVM RAL模型（支持单Block和系统级两种模式）
- 生成寄存器配置表（SystemVerilog），支持单BT和多BT合并输出

## 如何使用

### 安装 Marketplace

在 Claude Code 中，通过以下命令安装此 marketplace:

```bash
# 使用本地路径安装
claude plugins add /home/catmouse/Github_Project/nebula-matrix-skills

# 或使用 git URL 安装
claude plugins add https://github.com/your-username/nebula-matrix-skills.git
```

### 使用插件中的技能

安装后，可以通过以下方式使用技能:

```bash
# 触发 PPT 构建技能
/ppt-builder 创建一个企业介绍 PPT

# 触发技能构造器
/skill-constructor 帮我创建一个新的数据分析技能
```

或者直接描述需求:

```
帮我创建一个产品发布的演示文稿
```

## 添加新插件

要向此 marketplace 添加新插件，请遵循以下步骤:

1. 在根目录创建新的插件目录
2. 在插件目录中创建 `.claude-plugin/plugin.json` 配置文件
3. 在 `skills/` 目录下添加技能
4. 更新 `.claude-plugin/marketplace.json`，添加新插件条目

## 配置参考

详细配置说明请参考: [PLUGIN_CONFIGURATION_GUIDE.md](doc/PLUGIN_CONFIGURATION_GUIDE.md)

## 版本信息

- **Marketplace 版本**: 1.0.0
- **创建日期**: 2026-04-13
- **维护团队**: Nebula Matrix Team

## 许可证

本 marketplace 下的各插件遵循各自的许可证声明。
