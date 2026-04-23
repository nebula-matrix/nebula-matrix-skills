# Markdown First 工作流指南

本文档详细说明阶段3的 Markdown 工作文件 `.tp_cache/testplan_raw.md` 的格式规范与使用规则。

## 工作文件结构

`.tp_cache/testplan_raw.md` 是阶段3的唯一工作文件，所有章节分析结果追加到此文件中。

### 完整模板

```markdown
# Testplan Raw

## 队列管理

- description: VirtIO队列配置、队列映射等核心功能
- priority: HIGH
- sections_covered: S001,S002

### 队列深度配置

- sub_feature_name: 队列深度配置
- description: 验证队列深度配置功能
- spec_id: 【UVN.001.004】
- priority: HIGH

| tp_name | source | stimulus | checking | coverage_requirements | priority | category |
|---------|---------|----------|----------|----------------------|----------|----------|
| 队列深度32边界 | 3.2.1 队列深度配置 - 验证queue_size_mask_pow=5时队列深度为32 | 【配置】配置queue_size_mask_pow=5 | by_checker | queue_size_mask_pow=5 | HIGH | boundary |
| 队列深度32768边界 | 3.2.1 队列深度配置 - 验证queue_size_mask_pow=15时队列深度为32768 | 【配置】配置queue_size_mask_pow=15 | by_checker | queue_size_mask_pow=15 | HIGH | boundary |

### 队列映射模式

- sub_feature_name: 队列映射模式
- description: 验证队列映射模式
- spec_id: 【UVN.001.005】
- priority: HIGH

| tp_name | source | stimulus | checking | coverage_requirements | priority | category |
|---------|---------|----------|----------|----------------------|----------|----------|
| 2K模式验证 | 3.2.3 队列映射模式 - 验证2K模式使能 | 【配置】使能2K模式 | by_checker | - | HIGH | normal |

## 描述符预取

- description: 描述符预取机制验证
- priority: MID
- sections_covered: S003
```

## Heading 层级规则

| Markdown | 层级 | 作用 |
|----------|------|------|
| `#` | 文档级 | 文档标题，不参与路径映射 |
| `##` | Feature | Feature 节点声明。首次出现自动创建，后续出现更新属性 |
| `###` | SubFeature | SubFeature 节点声明，紧跟的表格为该 SubFeature 的 testpoints |

### `## Feature` 规则

- 文本编码后作为 `feature_id`
- 编码规则：去掉前后空格、所有空格、所有 `.`，全小写
- 首次出现：`description`、`priority` 必填（通过 `-` 属性块）
- 后续出现：属性块中显式字段覆盖更新，未提及字段保持原值
- 同一文档中所有该 Feature 的 SubFeature 应连续出现，不穿插其他 Feature

### `### SubFeature` 规则

支持两种写法：

1. **简写**（推荐）：仅 SubFeature 名称
   ```markdown
   ### 队列深度配置
   ```
   归属到最近的 `## Feature` 节点下。

2. **全路径**：`Feature.SubFeature`
   ```markdown
   ### 队列管理.队列深度配置
   ```
   两段分别编码后拼接。用于跨段引用或文档开头直接声明。

首次出现：`sub_feature_name`、`description`、`spec_id`、`priority` 必填。
后续出现：属性块中显式字段覆盖更新，未提及字段保持原值。表格行始终追加。

## 属性块（`-`）格式

紧跟在 heading 后的连续 `- key: value` 行。

```markdown
## 队列管理

- description: VirtIO队列配置、队列映射等核心功能
- priority: HIGH
- sections_covered: S001,S002
```

### Feature 属性

| 属性 | 必填 | 说明 |
|------|------|------|
| `description` | 首次创建 | Feature 描述 |
| `priority` | 首次创建 | `LOW` / `MID` / `HIGH` |
| `sections_covered` | 推荐 | 关联章节编号，逗号分隔，如 `S001,S002` |
| `skip` | 否 | `true` / `false` |

### SubFeature 属性

| 属性 | 必填 | 说明 |
|------|------|------|
| `sub_feature_name` | 首次创建 | SubFeature 显示名称 |
| `description` | 首次创建 | SubFeature 描述 |
| `spec_id` | 首次创建 | 规格编号，如 `【UVN.001.004】` |
| `priority` | 首次创建 | `LOW` / `MID` / `HIGH` |
| `skip` | 否 | `true` / `false` |

## 表格格式

表格永远归属于最近的 `### SubFeature` heading。

### 表头（必需列）

```markdown
| tp_name | source | stimulus | checking | coverage_requirements | priority | category |
|---------|---------|----------|----------|----------------------|----------|----------|
```

### 列说明

| 列名 | 必填 | 说明 |
|------|------|------|
| `tp_name` | 是 | 测试点名称，必须非空 |
| `source` | 否 | 来源/备注，引用原始文档的章节小节标题+简要概括 |
| `stimulus` | 是 | 配置和激励，多行内容换行统一使用 `<br>`，禁止在单元格内直接换行 |
| `checking` | 是 | `by_checker` / `by_direct_tc` / `by_assertion` |
| `priority` | 是 | `LOW` / `MID` / `HIGH`，禁止缩写 |
| `category` | 否 | `normal` / `boundary` / `combination` / `linkage` / `exception` |
| `coverage_requirements` | 否 | 期望填写。枚举该测试点需覆盖的具体取值/场景（如值域、边界点、组合矩阵等），作为后续 covergroup 实现的参考 |

## 路径编码规则

Feature / SubFeature ID 由名称自动编码：

```python
def encode_name(name: str) -> str:
    return re.sub(r'[\s\.]+', '', name.strip()).lower()
```

| 原始名称 | 编码后 ID |
|----------|-----------|
| `Virt IO 队列管理` | `virtio队列管理` |
| `队列.管理` | `队列管理` |
| `队列管理  ` | `队列管理` |
| `最大队列数与映射模式` | `最大队列数与映射模式` |

路径格式：`feature_id.sub_feature_id.tp_id`

示例：`virtio队列管理.队列深度配置.t000`

## build 与 import 的区别

| 命令 | 作用 | 对 JSON 的影响 | strict 模式 |
|------|------|----------------|-------------|
| `build` | 从 markdown **重建** features.json | **清空后重建** | `False`（允许创建新节点） |
| `import` | 从 markdown **增量导入** features.json | **追加/更新** | `True`（仅允许更新已有节点） |

### build 命令

```bash
nbl-testplan build .tp_cache/features.json .tp_cache/testplan_raw.md
```

1. 初始化（清空现有 `.tp_cache/features.json` 的 `features` 数组）
2. 遇到新的 `## Feature`：自动创建（从属性块读取必填字段）
3. 遇到新的 `### SubFeature`：自动创建（从属性块读取必填字段）
4. 遇到表格：为当前 SubFeature 添加 Testpoint（自动分配 `tp_id`）
5. 节点已存在：属性覆盖更新，Testpoint 追加

**build 前会自动运行 `check` 检查 markdown 格式，如果有错误则拒绝执行。**

### import 命令

```bash
nbl-testplan import .tp_cache/features.json new_section.md
```

1. 解析 markdown 中的 heading + 属性块 + 表格
2. `## Feature` 和 `### SubFeature` 必须已存在于 JSON，否则报错
3. 应用属性更新（覆盖已有值）
4. 表格 Testpoint 追加到对应 SubFeature

## 常见错误

### 1. 表格缺少归属 heading

```
❌ 错误：第 X 行开始的表格缺少归属的 ### SubFeature heading
```

原因：表格上方没有 `### SubFeature` heading。
解决：在表格前添加 `### SubFeature名称` heading。

### 2. Feature 缺少必填属性

```
❌ 错误：第 X 行 ## heading 缺少 `description`，创建 Feature 时必填
```

原因：build 时遇到新的 `## Feature`，但属性块缺少 `description` 或 `priority`。
解决：补充属性块中的必填字段。

### 3. SubFeature 缺少必填属性

```
❌ 错误：第 X 行 ### heading 缺少 `spec_id`，创建 SubFeature 时必填
```

原因：build 时遇到新的 `### SubFeature`，但属性块缺少 `description`、`spec_id` 或 `priority`。
解决：补充属性块中的必填字段。

### 4. 路径不存在（import 模式）

```
❌ 错误：路径 'xxx' 不存在（第 X 行 heading）
```

原因：import 模式下 heading 对应的 Feature/SubFeature 在 JSON 中不存在。
解决：先用 build 创建骨架，或用 `add feature` / `add subfeature` 手动创建。

### 5. 表格缺少必需列

```
❌ 错误：表格缺少必需列 'tp_name'
```

原因：表头缺少 `tp_name`、`stimulus`、`checking`、`priority` 之一。
解决：补充完整表头。

### 6. 表格行缺少必填值

```
❌ 错误：第 X 行（归属 xxx）缺少必填值 'tp_name'
```

原因：某行 `tp_name`、`stimulus`、`checking`、`priority` 有空值。
解决：补充该行空值。

### 7. priority 值无效

```
❌ 错误：第 X 行 priority 值 'P0' 无效，请使用 LOW/MID/HIGH
```

原因：`priority` 不是 `LOW` / `MID` / `HIGH`。
解决：修正为 `LOW`、`MID` 或 `HIGH`。
