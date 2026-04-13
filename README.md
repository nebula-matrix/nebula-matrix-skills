# Nebula Matrix Skills Marketplace

这是 Nebula Matrix 技能市场，提供企业级生产力工具和自动化解决方案。

## 目录结构

```
nebula-matrix-skills-marketplace/
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

## 如何使用

### 安装 Marketplace

在 Claude Code 中，通过以下命令安装此 marketplace:

```bash
# 使用本地路径安装
claude plugins add /home/catmouse/Github_Project/nebula-matrix-skills-marketplace

# 或使用 git URL 安装
claude plugins add https://github.com/your-username/nebula-matrix-skills-marketplace.git
```

### 使用插件中的技能

安装后，可以通过以下方式使用技能:

```bash
# 触发 PPT 构建技能
/ppt-builder 创建一个企业介绍 PPT
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

详细配置说明请参考: [PLUGIN_CONFIGURATION_GUIDE.md](https://github.com/luyufan498/yf-skills/blob/main/docs/PLUGIN_CONFIGURATION_GUIDE.md)

## 版本信息

- **Marketplace 版本**: 1.0.0
- **创建日期**: 2026-04-13
- **维护团队**: Nebula Matrix Team

## 许可证

本 marketplace 下的各插件遵循各自的许可证声明。

---

更多信息请访问: https://github.com/luyufan498/yf-skills
