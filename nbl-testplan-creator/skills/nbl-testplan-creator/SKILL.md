---
name: nbl-testplan-creator
description: IC验证测试计划生成技能。采用 Markdown-first 工作流：从规格文档逐章节分析生成测试点，全程以 Markdown 为工作文件，最后一次性生成 features.json。
---

# NBL Testplan Creator

## 概述

本技能用于从 IC 模块功能规格文档自动生成验证测试计划。采用 **Markdown-first 工作流**：

- 全程以 Markdown 为唯一工作文件，不直接操作 JSON
- 逐章节串行分析，追加到 `.tp_cache/testplan_draft.md`
- 全部章节完成后执行 `nbl-testplan build` 一次性生成 `.tp_cache/features.json`
- 最后从 `.tp_cache/features.json` 生成最终测试计划文档

**核心优势**：章节失败不污染已有数据，Markdown 便于人工审阅和修改。

## 工作目录结构

工作开始前在当前目录（CWD）创建 `.tp_cache/` 目录存放所有中间文件，CWD 仅保留输入文档和最终交付物：

```
CWD/
├── {doc_name}.docx                           # 用户输入文档（CWD）
│
├── .tp_cache/
│   ├── {doc_name}_decode_work/             # 阶段0：docx转换临时目录
│   │   └── markdown_output/
│   │       └── {doc_name}_decode.md        # 转换后的markdown
│   ├── {doc_name}_docmeta.json            # 阶段1：章节粗划分
│   ├── feature_plan.json                   # 阶段2：Feature规划
│   ├── testplan_draft.md                     # 阶段3：Markdown主工作文件
│   └── features.json                       # 阶段3b：统一数据结构
│
└── {doc_name}_testplan.md                  # 阶段4：最终测试计划文档（CWD）
```

所有中间产物（转换目录、JSON、工作md）统一放入 `.tp_cache/` 管理，CWD 仅保留原始输入和最终输出。

## 工作阶段速查

| 阶段 | 动作 | 核心命令 | 输入 | 输出 |
|------|------|----------|------|------|
| 0 | 格式检测/转换 | 调用 `nbl-docx-to-markdown` | `.docx` | `.tp_cache/{doc_name}_decode_work/markdown_output/{doc_name}_decode.md` |
| 1 | 章节粗划分 | `nbl-testplan doc-meta generate` | `.tp_cache/{doc_name}_decode_work/markdown_output/{doc_name}_decode.md` | `.tp_cache/{doc_name}_docmeta.json` |
| 2 | Feature 规划 | Subagent 分析全文 | `.tp_cache/{doc_name}_docmeta.json` | `.tp_cache/feature_plan.json` + `.tp_cache/testplan_draft.md` 骨架 |
| 3 | 逐章节分析 | Subagent 串行追加到 `.tp_cache/testplan_draft.md` | 章节内容 | `.tp_cache/testplan_draft.md` |
| 3b | Markdown → JSON | `nbl-testplan build` | `.tp_cache/testplan_draft.md` | `.tp_cache/features.json` |
| 4 | 生成文档 | `nbl-testplan format` | `.tp_cache/features.json` | `{doc_name}_testplan.md` |

---

## 阶段0：输入文档处理

**检测输入格式**：
- 输入是 `.docx` 文件 → 调用 `nbl-docx-to-markdown` 技能转换为 markdown
  - 转换工作目录生成在 `.tp_cache/{doc_name}_decode_work/`
  - 转换后的 `.md` 文件位于 `.tp_cache/{doc_name}_decode_work/markdown_output/{doc_name}_decode.md`
- 输入已经是 markdown → 直接复制到 `.tp_cache/` 目录下，进入阶段1

## 阶段1：章节划分（粗框架）

使用 `nbl-testplan doc-meta generate` 进行粗框架划分：

```bash
nbl-testplan doc-meta generate \
  .tp_cache/{doc_name}_decode_work/markdown_output/{doc_name}_decode.md \
  -o .tp_cache/{doc_name}_docmeta.json
```

**参数说明**：
- `-o, --output`: 输出 JSON 文件路径（可选，默认输出到控制台）
- `--max-depth`: 最大解析深度，`1`=只解析 `#` 一级标题，`2`=解析到 `##` 二级标题，`3`=解析到 `###` 三级标题。默认 `2`

**输出结构**：`.tp_cache/{doc_name}_docmeta.json` 包含 `document_title`、`split_config`、嵌套 `sections` 数组。每个 section 含 `id`、`title`、`level`、`line_start`/`line_end`、`line_count`，以及递归嵌套的 `subsections`（最多 `--max-depth` 层）。

**重要说明**：
- 顶层始终按 `# ` 一级标题切分，子章节按嵌套层级递归提取
- 默认深度为 2，避免生成过细的嵌套；如叶子章节超过 1000 行，脚本会自动打印警告建议增加 `--max-depth`
- 这一步只做粗框架划分，不做智能推荐或过滤
- section ID 格式：`S001`（一级）、`S006.001`（二级）、`S009.001.001`（三级）
- `source_file` 字段自动记录原始 markdown 路径，后续 `doc-meta read` 可直接定位内容
- 后续阶段3通过 `doc-meta read` 按 section ID 提取完整章节内容，无需直接处理原始文档

## 阶段2：Feature 初步规划

调用**独立 subagent** 分析整个文档，生成 Feature 初步规划。

**前置准备**：先用 `doc-meta tree` 查看章节结构，获取 section ID 映射关系：

```bash
nbl-testplan doc-meta tree .tp_cache/{doc_name}_docmeta.json
```

输出示例（带层级 ID）：
```
[S001] # 概述
[S002] # 功能架构
[S003] # 队列管理
  [S003.001] ## 队列创建
  [S003.002] ## 队列映射
[S004] # 中断处理
  [S004.001] ## 中断触发条件
  [S004.002] ## 中断清除机制
```

**Subagent 任务**：理解模块功能架构，识别主要功能域（Feature），为每个 Feature 分配优先级，并基于 `doc-meta tree` 输出映射相关 section ID。

**输出文件**：`.tp_cache/feature_plan.json`

```json
{
  "features": [
    {
      "feature_id": "队列管理",
      "feature_name": "队列管理",
      "description": "队列创建、配置、映射等核心功能",
      "priority": "HIGH",
      "sections_covered": ["S003", "S003.001", "S003.002"]
    },
    {
      "feature_id": "中断处理",
      "feature_name": "中断处理",
      "description": "中断触发、清除、屏蔽机制",
      "priority": "HIGH",
      "sections_covered": ["S004", "S004.001", "S004.002"]
    }
  ]
}
```

**规则**：
- Feature 划分要符合验证思路，不局限于文档章节结构
- `sections_covered` 填写与 Feature 相关的 section ID（支持多级 ID，如 `S003.001`）
- 只要 feature 的 name，不需要 ID，因为 ID 通过 name 编码自动生成
- Subagent 可直接用 `doc-meta read .tp_cache/{doc_name}_docmeta.json S003,S003.001` 读取相关章节内容辅助分析

**动态调整**：后续阶段如发现 Feature 划分不合理，可直接在 `.tp_cache/testplan_draft.md` 中追加新的 `## Feature` heading。

## 阶段3：逐章节分析（Markdown 工作流）

**本阶段全程以 `.tp_cache/testplan_draft.md` 为唯一工作文件，不操作 `.tp_cache/features.json`。**

### 3a. 生成骨架

由阶段2的 subagent 生成 `.tp_cache/testplan_draft.md` 的初始骨架，只包含 `# 文档标题` + `## Feature` heading + 属性块。

`# 文档标题` 应根据实际文档名称生成有意义的标题，如：
- 输入为 `Orion_UVN_Functional_Specification.docx` → `# Orion UVN 功能规格验证测试计划`
- 输入为 `PA_Queue_Management.docx` → `# PA 队列管理验证测试计划`

骨架模板（`sections_covered` 从 `doc-meta tree` 获取）：

```markdown
# {doc_name} 验证测试计划

## 队列管理

- description: VirtIO队列配置、队列映射等核心功能
- priority: HIGH
- sections_covered: S003,S003.001,S003.002

## 中断处理

- description: 中断触发、清除、屏蔽机制
- priority: HIGH
- sections_covered: S004,S004.001,S004.002
```

### 3b. 章节处理策略

主 Agent 根据文档规模选择处理策略，**核心原则：避免多个 subagent 同时竞争同一文件**。

**策略一：直接处理（推荐用于小文档）**
- 适用：各章节 `line_count` 总和较少，主 Agent 上下文能覆盖
- 方式：主 Agent 直接逐feature分析，或自行分解后串行处理
- 优点：无文件竞争，跨章节联动分析可实时参考前面结果
- 内容获取：使用 `nbl-testplan doc-meta read .tp_cache/{doc_name}_docmeta.json S003,S003.001` 读取相关章节内容

**策略二：创建 subagent 分组并行（用于大文档）**
- 适用：各章节 `line_count` 总和较大（> 700 行），主 Agent 或单 subagent 上下文溢出
- **分组原则 — 按 Feature 域拆分，不按 Section 拆分**；主 Agent 参考 `feature_plan.json`，将关联 Feature 合并为 2-3 组，确保每组总行数可控
- **Partial 文件格式（与策略一不同）**：
  - 每个 partial 文件独立输出，按 `## Feature → ### SubFeature → 表格` 的结构组织
  - **`## Feature heading 不可省略`**：`merge` 命令通过 `##` 切分 block 边界，每个 partial 中的每个 Feature 必须完整写出 heading 和属性块，这样脚本在合并的时候才能正确映射到骨架里面
  ```markdown
  ## 队列管理
  - description: 队列配置、映射、复位...
  - priority: HIGH
  - sections_covered: S003,S003.001,S003.002

  ### 队列深度配置
  - sub_feature_name: 队列深度配置
  - description: ...
  - spec_id: 【UVN.001.004】
  - priority: HIGH

  | tp_name | source | stimulus | checking | coverage_requirements | priority | category |
  |---------|--------|----------|----------|----------------------|----------|----------|
  | ...
  ```
- **执行流程**：
  1. 主 Agent 创建 subagent，传入 Feature 列表及 `sections_covered` 中的 section ID 列表
  2. Subagent 使用 `nbl-testplan doc-meta read .tp_cache/{doc_name}_docmeta.json <section_ids>` 读取相关章节内容，逐节分析后输出 `.tp_cache/partial_{N}.md`
  3. 全部完成后主 Agent 调用 `nbl-testplan merge .tp_cache/testplan_draft.md .tp_cache/partial_*.md` 合并
- **并发控制**：同时运行的 subagent 不超过 3 个

```
主 Agent:
  按 Feature 域分组（共 5 个 Feature，合并为 3 组）：
  ├─ subagent-A（队列管理 + 描述符预取）→ partial_a.md
  ├─ subagent-B（中断处理 + DMA 传输）  → partial_b.md
  └─ subagent-C（错误处理）             → partial_c.md
         每组 subagent 独立分析自己的 Feature 域
         ↓ 并行执行 ↓
  主 Agent 串行合并：partial_a → partial_b → partial_c → testplan_draft.md
```

### 3c. Subagent 输出格式规范

Subagent 统一输出独立的 partial 文件，按 `## Feature → ### SubFeature → 表格` 的结构组织。

**`## Feature` 不可省略**：`nbl-testplan merge` 通过 `##` 识别 Feature block 边界，每个 Feature 必须完整写出 heading 及其属性块，用于合并的时候映射骨架的对应feature。

```markdown
## 队列管理

- description: 队列配置、映射、复位...
- priority: HIGH
- sections_covered: S003,S003.001,S003.002

### 队列深度配置

- sub_feature_name: 队列深度配置
- description: ...
- spec_id: 【UVN.001.004】
- priority: HIGH

| tp_name | source | stimulus | checking | coverage_requirements | priority | category |
|---------|--------|----------|----------|----------------------|----------|----------|
| ...
```

[Subagent 完整 Prompt 模板和自检清单见 references/subagent_prompt.md](references/subagent_prompt.md)
[Heading 规则、属性块格式、表格格式见 references/markdown_first_guide.md](references/markdown_first_guide.md)

### 3d. 自检要求

每个 subagent 输出前必须完成自检：

1. **内容质量检查**：
   - 是否覆盖了章节中的所有功能点？
   - 是否测试了边界值（最大/最小/临界）？
   - 是否测试了配置项之间的组合？
   - 是否识别了跨章节的联动关系？
   - 是否覆盖了异常和错误处理场景？
   - coverage_requirements 是否枚举了需要覆盖的取值/场景？
   - stimulus 描述是否具体可执行？
   - checking 方式是否明确？

2. **格式规范检查**：
   - 运行 `nbl-testplan check <partial_file.md>`，确保**零错误**（`TABLE_ROW_TRUNCATED`、`TABLE_COLUMN_MISMATCH`、`TABLE_MISSING_SEP`、`ORPHAN_SUBFEATURE`、`PROPERTY_FORMAT`），零 `ORPHAN_SUBFEATURE` 警告。
   - 每个 `## Feature` heading 不可省略。
   - 表格字段换行统一使用 `<br>`，禁止真实换行。
   - 属性块格式严格为 `- key: value`，禁止加粗 key。

自检未通过时必须在内部修改完善后再输出。

## 阶段3b：Markdown → JSON 转换

全部章节写入 `.tp_cache/testplan_draft.md` 后，执行一次性转换：

```bash
nbl-testplan build .tp_cache/features.json .tp_cache/testplan_draft.md
```

**行为**：
1. **清空**现有 `.tp_cache/features.json` 的 `features` 数组（如果已存在）
2. 遇到新的 `## Feature`：自动创建（属性块中 `description`、`priority` 必填）
3. 遇到新的 `### SubFeature`：自动创建（属性块中 `description`、`spec_id`、`priority` 必填）
4. 遇到表格：为当前 SubFeature 添加 Testpoint（自动分配 `tp_id`）
5. 如果 Feature/SubFeature 已存在：属性块中显式字段覆盖更新，未提及字段保持原值；Testpoint 始终追加

**自检**：转换后查看 tree 确保结构完整
```bash
nbl-testplan tree .tp_cache/features.json
```

[常见 build/import 错误说明见 references/markdown_first_guide.md](references/markdown_first_guide.md)

## 阶段4：生成测试计划

从统一的 `.tp_cache/features.json` 生成最终测试计划文档。

**步骤1：验证数据完整性**
```bash
nbl-testplan tree .tp_cache/features.json
nbl-testplan tree .tp_cache/features.json --show-skip
```

**步骤2：生成最终文档**
```bash
nbl-testplan format .tp_cache/features.json --format md -o {doc_name}_testplan.md
```

## 路径编码规则

Feature / SubFeature ID 由名称自动编码生成：

- 去掉前后空白、所有空格、所有英文句点 `.`
- 全小写
- 示例：`"Virt IO 队列管理"` → `"virtio队列管理"`

路径格式：`feature_id.sub_feature_id.tp_id`（如 `队列管理.队列深度.t000`）

## 核心文件说明

| 文件 | 作用 | 生命周期 |
|------|------|----------|
| `.tp_cache/{doc_name}_decode_work/markdown_output/{doc_name}_decode.md` | 转换后的输入规格文档 | 阶段0输出，阶段1-3消费 |
| `.tp_cache/{doc_name}_docmeta.json` | 章节粗划分结果（含嵌套 subsection ID、行号范围、`source_file` 路径） | 阶段1输出，阶段2-3通过 `doc-meta tree/read/info` 消费 |
| `.tp_cache/feature_plan.json` | Feature 初步规划 | 阶段2输出，可动态更新 |
| `.tp_cache/testplan_draft.md` | **阶段3主工作文件**，包含所有 heading + 属性块 + 表格 | 持续追加，阶段3b前完成 |
| `.tp_cache/features.json` | 统一的三级结构数据（Feature → SubFeature → Testpoint） | 阶段3b生成，阶段4消费 |
| `{doc_name}_testplan.md` | 最终测试计划文档 | CWD，阶段4输出，文件名关联输入文档名 |

## doc-meta 命令速查

阶段1-3 通过 `nbl-testplan doc-meta` 子命令操作 `.tp_cache/{doc_name}_docmeta.json`：

| 子命令 | 用途 | 示例 |
|--------|------|------|
| `generate` | 从 markdown 生成章节元数据 | `nbl-testplan doc-meta generate spec.md -l 1 -o {doc_name}_docmeta.json` |
| `tree` | 显示章节目录树（带层级 ID） | `nbl-testplan doc-meta tree {doc_name}_docmeta.json` |
| `stats` | 显示文档统计概览 | `nbl-testplan doc-meta stats {doc_name}_docmeta.json` |
| `read` | 读取指定章节内容（支持多选，逗号分隔） | `nbl-testplan doc-meta read {doc_name}_docmeta.json S003,S003.001` |
| `info` | 查看指定章节的元数据 | `nbl-testplan doc-meta info {doc_name}_docmeta.json S003.001` |

## 参考文档

按需读取以下 reference 文件获取详细指导：

| Reference | 内容 | 何时读取 |
|-----------|------|----------|
| [references/markdown_first_guide.md](references/markdown_first_guide.md) | `testplan_draft.md` 完整模板、Heading 规则、属性块、表格格式、编码规则、build/import 常见错误 | 阶段3编写/审阅 markdown 时 |
| [references/subagent_prompt.md](references/subagent_prompt.md) | Phase 3 Subagent 完整 Prompt 模板、自检清单、输出格式 | 创建阶段3 subagent 时 |
| [references/cli_reference.md](references/cli_reference.md) | 所有 CLI 命令的完整参数说明 | 需要精确命令参数时 |
| [references/workflow_examples.md](references/workflow_examples.md) | 6 个完整使用示例（完整流程、单章节分析、自检修正、跨章节联动、动态调整 Feature、查看 tree） | 需要参考具体场景执行方式时 |
| [references/best_practices.md](references/best_practices.md) | Feature 规划原则、串行策略、Testpoint 设计策略（normal/boundary/combination/linkage/exception 占比）、自检清单、审查要点 | 需要验证工作质量时 |
| [references/ic_verification_guide.md](references/ic_verification_guide.md) | IC 验证测试点提取方法论 | 规划测试策略时 |
| [references/testplan_template.md](references/testplan_template.md) | 标准测试计划文档模板 | 生成最终文档前参考格式 |

## 注意事项

1. **弹性处理**：主 Agent 根据 `{doc_name}_docmeta.json` 中各章节 `line_count` 总和判断规模——≤500 行串行处理，>500 行按 Feature 域创建 subagent 分组并行（2-3 个），最后串行合并，避免 API 访问限制并保证后续章节可参考前面结果。每个 subagent 工作前必须先读取 `.tp_cache/testplan_draft.md` 获取当前完整内容；subagent 读取原始规格内容时通过 `nbl-testplan doc-meta read .tp_cache/{doc_name}_docmeta.json <section_ids>` 按 ID 提取，不直接操作原始 markdown。
2. **Markdown 为唯一数据源**：阶段3全程不操作 `.tp_cache/features.json`，所有修改通过编辑 `.tp_cache/testplan_draft.md` 完成，最后 `build` 生成。
3. **`testplan_formatter.py` 为旧版工具**：用于从多个 `S*_testpoints.json` 汇总生成测试计划。当前工作流使用统一的 `features.json` + `nbl-testplan format`，无需此工具。
