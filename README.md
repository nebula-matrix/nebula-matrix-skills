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
├── nbl-docx-to-markdown/         # NBL DOCX 转 Markdown 插件
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件配置
│   └── skills/
│       └── nbl-docx-to-markdown/
│           ├── SKILL.md         # 技能主文件
│           ├── assets/          # 资源文件
│           ├── references/      # 参考文档
│           └── scripts/         # 执行脚本
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

### nbl-docx-to-markdown

**描述**: NBL企业定制的 DOCX 转 Markdown 工具，支持复杂 Word 文档转换，包含图片、Visio图表、表格处理及技术文档优化

**分类**: productivity

**标签**: docx, markdown, converter, document

**功能**:
- 使用 LibreOffice + Pandoc 将 Word 文档转换为 Markdown
- 支持处理图片、Visio图表，自动复制到 assets 目录
- 保留表格为 HTML 格式以确保兼容性
- 自动修复章节标题格式，将 `[xxx]` 标记转换为代码格式
- 验证转换结果，发现结构差异时强制修复
- 特别适用于包含寄存器描述、表项定义等技术文档

### nbl-testplan-generator

**描述**: 数字芯片验证测试计划生成器，从功能规格书（.docx）和寄存器配置（.xlsx）生成结构化测试点文档

**分类**: development

**标签**: testplan, verification, chip, document

**功能**:
- 从功能规格书（.docx）解析模块功能特性
- 从寄存器手册（.xlsx）提取寄存器配置信息
- 生成 D-E-F/G 层级结构化测试点文档
- 支持功能特性（testplan-func）和配置特性（testplan-cfg）分开生成
- 提供 review 刷新机制，支持增量更新测试点

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
