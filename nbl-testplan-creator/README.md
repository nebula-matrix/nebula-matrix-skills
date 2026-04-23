# nbl-testplan-creator

NBL 企业 IC 验证测试计划生成插件，采用 Markdown-first 工作流从功能规格文档自动生成结构化测试点。

## 概述

本插件提供 IC 验证测试计划生成技能，核心特点：

- **Markdown-first 工作流**：全程以 Markdown 为唯一工作文件，不直接操作 JSON
- **逐章节串行分析**：按章节追加到主工作文件，失败不污染已有数据
- **自动 ID 编码**：Feature / SubFeature / Testpoint ID 由名称自动编码生成
- **CLI 工具支持**：提供 `nbl-testplan` 命令行工具用于构建、格式化、合并、检查

## 技能使用

安装 marketplace 后触发：

```
/nbl-testplan-creator 从 xxx.docx 生成测试计划
```

## 安装 CLI 工具

```bash
cd skills/nbl-testplan-creator/scripts
pip install .
```

安装后可用命令：

| 命令 | 说明 |
|------|------|
| `nbl-testplan build` | Markdown → JSON 转换 |
| `nbl-testplan format` | JSON → 最终文档 |
| `nbl-testplan merge` | 合并 partial Markdown 文件 |
| `nbl-testplan check` | 格式检查 |
| `nbl-testplan tree` | 查看结构树 |

## 目录结构

```
nbl-testplan-creator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── nbl-testplan-creator/
│       ├── SKILL.md           # 技能主文件
│       ├── references/        # 参考文档（格式规范、CLI参考、最佳实践）
│       ├── scripts/           # CLI 工具（Python 包）
│       └── assets/            # 资源文件
├── archive/                   # 历史脚本存档
└── README.md                  # 本文件
```

## 参考文档

- [markdown_first_guide.md](skills/nbl-testplan-creator/references/markdown_first_guide.md) — Markdown 工作流完整规范
- [cli_reference.md](skills/nbl-testplan-creator/references/cli_reference.md) — CLI 参数说明
- [best_practices.md](skills/nbl-testplan-creator/references/best_practices.md) — Feature 规划与 Testpoint 设计最佳实践
- [ic_verification_guide.md](skills/nbl-testplan-creator/references/ic_verification_guide.md) — IC 验证方法论
- [workflow_examples.md](skills/nbl-testplan-creator/references/workflow_examples.md) — 完整使用示例

## 版本

- **插件版本**: 1.0.0
- **CLI 版本**: 1.0.0 (nbl_testplan_creator)
