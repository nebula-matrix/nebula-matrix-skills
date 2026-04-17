# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库定位

这是一个 **Claude Code 技能市场** 仓库，用于分发可复用的插件和技能。后续会持续添加新插件。

## Marketplace 标准结构

Marketplace 遵循 Claude Code 插件系统定义的特定结构：

```
nebula-matrix-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace 索引文件（必需）
├── {plugin-name}/                # 每个插件是顶层目录
│   ├── .claude-plugin/
│   │   └── plugin.json          # 插件元数据（必需）
│   ├── skills/                   # Skills 目录
│   │   └── {skill-name}/
│   │       ├── SKILL.md         # Skill 文件（必需）
│   │       ├── reference/       # 可选：参考文档
│   │       ├── scripts/         # 可选：执行脚本
│   │       └── templates/       # 可选：模板文件
│   ├── commands/                 # 可选：斜杠命令
│   ├── agents/                   # 可选：专用代理
│   └── README.md                 # 插件文档
└── README.md                     # Marketplace 概述
```

## 添加新插件流程

向 marketplace 添加新插件时：

### 1. 创建插件目录结构

```bash
# 创建插件目录
mkdir -p {plugin-name}/.claude-plugin
mkdir -p {plugin-name}/skills/{skill-name}
```

### 2. 创建必需的配置文件

**插件元数据** (`{plugin-name}/.claude-plugin/plugin.json`):
```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "插件功能描述（50-200字符）",
  "skills": "./skills"
}
```

**Skill 文件** (`{plugin-name}/skills/{skill-name}/SKILL.md`):
```markdown
---
name: skill-name
description: 详细描述何时使用此技能。当用户要求 X、Y、Z 时触发。
---

# Skill 标题

给 Claude 的具体指令...
```

### 3. 更新 Marketplace 索引

向 `.claude-plugin/marketplace.json` 添加新插件条目：

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugin-name",
      "description": "插件描述",
      "category": "productivity",
      "tags": ["tag1", "tag2"],
      "keywords": ["keyword1", "keyword2"]
    }
  ]
}
```

## 关键配置要求

### marketplace.json 要求

- **必须**包含 `$schema` 字段，指向官方 schema
- **必须**包含唯一 `name`，使用 kebab-case 格式
- **必须**包含 `plugins` 数组，至少有一个条目
- 每个插件条目：
  - `name` 必须与插件的 `plugin.json` 中的 name 一致
  - `source` 必须是从 marketplace 根目录的相对路径（如 `./plugin-name`）

### plugin.json 要求

- **必须**包含 `name` 字段（kebab-case，唯一标识符）
- `skills` 字段应指向 skills 目录（如 `"./skills"`）
- 推荐使用自动扫描方式：`"skills": "./skills"`（系统会查找所有 SKILL.md 文件）

### SKILL.md 要求

- **必须**位于 `skills/{skill-name}/SKILL.md`（不是插件根目录）
- Frontmatter **必须包含**：
  - `name`: skill 标识符（应与目录名一致）
  - `description`: 详细触发场景（建议 50-200 字符）
- Frontmatter **不支持**：
  - `allowed-tools`
  - `event`、`pattern`、`action`（这些仅用于 hooks）

### 命名规范

- 使用 **kebab-case**: `ppt-builder`、`stock-analysis`、`meeting-summarizer`
- 描述性强：名称应清晰表达功能
- 避免通用词：不要使用 `util`、`helper`、`common`
- Skill 目录名应与 frontmatter 中的 `name` 字段一致

## 提交前验证清单

提交新插件前，请验证：

- [ ] 已更新 marketplace.json，添加新插件条目
- [ ] 插件目录结构正确：`{plugin-name}/.claude-plugin/plugin.json`
- [ ] Skills 位置正确：`{plugin-name}/skills/{skill-name}/SKILL.md`
- [ ] SKILL.md frontmatter 有效（包含 `name` + `description`）
- [ ] marketplace.json 中的插件名与 plugin.json 一致
- [ ] 插件 README.md 已添加，说明用法和要求
- [ ] SKILL.md 中没有使用不支持的 frontmatter 字段
- [ ] 已更新根目录 README.md，添加新插件到插件列表中

## 常见错误及正确做法

❌ **SKILL.md 位置错误**：
```
{plugin-name}/SKILL.md  # 错误 - 应该在 skills/ 子目录中
```

✅ **正确结构**：
```
{plugin-name}/skills/{skill-name}/SKILL.md
```

❌ **无效的 frontmatter 字段**：
```yaml
---
name: skill-name
allowed-tools: [Read, Write]  # 不支持
---
```

✅ **有效 frontmatter**：
```yaml
---
name: skill-name
description: 何时使用此技能的说明
---
```

❌ **名称不匹配**：
```json
// marketplace.json
{"name": "my-plugin", ...}

// plugin.json
{"name": "my_plugin"}  // 错误 - 必须完全一致
```

## 插件配置参考文档

详细的配置规范请参考：[doc/PLUGIN_CONFIGURATION_GUIDE.md](doc/PLUGIN_CONFIGURATION_GUIDE.md)

该参考文档包含：
- 完整的 marketplace.json schema
- 所有 plugin.json 字段说明
- SKILL.md frontmatter 详细要求
- 目录结构示例
- 问题排查指南

## 多技能插件

单个插件可以包含多个技能，它们共享资源：

```
my-plugin/
├── skills/
│   ├── skill-1/SKILL.md
│   ├── skill-2/SKILL.md
│   └── skill-3/SKILL.md
├── templates/        # 所有技能共享
└── scripts/          # 所有技能共享
```

在 plugin.json 中使用 `"skills": "./skills"` 自动发现所有技能。

## 测试插件安装

添加插件后，测试安装：

```bash
# 从本地路径安装
claude plugins add /path/to/nebula-matrix-skills

# 验证插件可用
claude plugins list

# 测试技能触发（使用 SKILL.md frontmatter 中的 skill name）
/{skill-name} [测试提示词]
```

## Git 工作流程

添加新插件时：

1. 创建特性分支：`git checkout -b add-{plugin-name}`
2. 添加插件文件并更新 marketplace.json
3. 更新根目录 README.md，在插件列表中添加新插件
4. 本地测试插件安装
5. 提交，消息格式：`feat: add {plugin-name} plugin`
6. 创建 PR，描述插件功能

## 重要提醒

- 新增插件时，不要修改现有插件的结构
- 保持 marketplace 结构的扁平化（所有插件在根目录下的独立目录）
- 确保每个插件都有完整的 README.md 说明文档
- **务必检查 `.claude-plugin/marketplace.json` 已配置新插件信息**
- **务必更新根目录 README.md，确保插件列表包含最新添加的插件**
- 定期检查并更新 marketplace.json 中的插件列表
