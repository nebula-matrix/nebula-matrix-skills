# CLI 完整参考

所有命令通过 `nbl-testplan` 入口执行。安装：`uv tool install -e .`（在项目根目录）。

## nbl-testplan check — 前置格式检查（merge/build 前自动执行）

```bash
nbl-testplan check <md_file>
```

- `md_file`: markdown 文件路径

检查 markdown 格式完整性，检测表格完整性问题（换行截断、列数不匹配、缺失分隔行等）。  
**build 和 merge 执行前会自动调用**，如果检查失败则拒绝执行并输出 AI 修复建议。

可检测的错误类型：
- `TABLE_ROW_TRUNCATED` — 表格行不以 `|` 结尾（单元格内有未转义的换行）
- `TABLE_CONTINUATION` — 疑似表格续行
- `TABLE_COLUMN_MISMATCH` — 表格列数与表头不匹配
- `TABLE_MISSING_SEPARATOR` — 缺少 `|---|---|` 分隔行
- `ORPHAN_SUBFEATURE` — `###` 标题缺少前置 `##` 标题
- `PROPERTY_FORMAT` — 属性行缺少 `: ` 分隔

## nbl-testplan merge — 合并 partial markdown 文件

```bash
nbl-testplan merge <output.md> <partial1.md> [partial2.md ...]
```

- `output.md`: 合并后的完整 markdown 文件路径
- `partialN.md`: 一个或多个 partial markdown 文件

按 Feature 名称合并多个 partial 文件：相同 Feature 的 SubFeature 归并到同一 heading 下，保留属性块（去重），不同 Feature 按 first-seen 顺序排列。文档标题从第一个包含 `# Title` 的 partial 中提取。

**merge 前自动调用 `check` 检查所有 partial 文件，任一文件不通过则全部中止。**

## nbl-testplan init — 初始化 JSON 文件

```bash
nbl-testplan init <file> [--title <title>]
```

- `file`: JSON 文件路径
- `--title`: 文档标题（可选，默认 `Test Plan`）

如果文件已存在，自动创建备份（`.bk` → `.old` → `.bk.{时间戳}`）。

## nbl-testplan tree — 显示 Feature Tree

```bash
nbl-testplan tree <file> [--show-skip]
```

- `file`: JSON 文件路径
- `--show-skip`: 显示被跳过的节点（默认隐藏）

输出格式：
```
[feature_id] feature_name
    -- [sub_feature_id] description
        -- [tp_id] tp_name
```

## nbl-testplan add — 添加节点

#### add feature

```bash
nbl-testplan add feature <file> \
  feature_name="<name>" \
  description="<desc>" \
  priority=<LOW|MID|HIGH> \
  [sections_covered=S001,S002]
```

- `feature_name`: 显示名称
- `description`: 描述
- `priority`: `LOW` / `MID` / `HIGH`
- `sections_covered`: 逗号分隔的章节编号（可选）

#### add subfeature

```bash
nbl-testplan add subfeature <file> <feature_id> \
  description="<name>" \
  [spec_id="<id>"] \
  priority=<LOW|MID|HIGH>
```

- `feature_id`: 父 Feature 的 ID（当前文档中的 fxxx ID）
- `description`: 名称和描述
- `spec_id`: 规格编号（可选）
- `priority`: `LOW` / `MID` / `HIGH`

#### add tp

```bash
nbl-testplan add tp <file> <feature_id>.<sub_feature_id> \
  tp_name="<name>" \
  stimulus="<stimulus>" \
  [checking=by_checker] \
  [priority=MID] \
  [source="<source>"] \
  [category=normal]
```

- `path`: `feature_id.sub_feature_id`（如 `f000.s000`）
- `tp_name`: 测试点名称
- `stimulus`: 配置和激励
- `checking`: `by_checker` / `by_direct_tc` / `by_assertion`（默认 `by_checker`）
- `priority`: 优先级（默认 `MID`）
- `source`: 来源/备注（可选）
- `category`: 类别（默认 `normal`）

## nbl-testplan view — 查看节点详情

```bash
nbl-testplan view <file> <path> [--json]
```

- `path`: `feature_id` 或 `feature_id.sub_feature_id` 或 `feature_id.sub_feature_id.tp_id`
- `--json`: JSON 格式输出（默认纯文本）

## nbl-testplan del — 删除节点

```bash
nbl-testplan del <file> <path> [--force]
```

- `--force`: 跳过确认直接删除

## nbl-testplan edit — 编辑节点字段

```bash
nbl-testplan edit <file> <path> <key>=<value> [...]
```

支持修改任意字段。`priority` 和 `checking` 会自动校验合法性。

## nbl-testplan replace — 替换节点内容

```bash
nbl-testplan replace <file> <path> <key>=<value> [...]
```

与 `edit` 的区别：`replace` 先清空节点的内容字段再写入新值，`edit` 是增量更新。

## nbl-testplan build — 从 markdown 重建 JSON

```bash
nbl-testplan build <file> <md_file>
```

- `file`: JSON 文件路径
- `md_file`: markdown 文件路径

**行为**：
1. **清空**现有 JSON 的 `features` 数组
2. 遇到新的 `## Feature`：自动创建（属性块中 `description`、`priority` 必填）
3. 遇到新的 `### SubFeature`：自动创建（属性块中 `description`、`spec_id`、`priority` 必填）
4. 遇到表格：为当前 SubFeature 添加 Testpoint（自动分配 `tp_id`）
5. 节点已存在：属性覆盖更新，Testpoint 追加

**build 前自动调用 `check` 检查 markdown，不通过则拒绝执行。**

## nbl-testplan import — 从 markdown 增量导入

```bash
nbl-testplan import <file> <md_file>
```

- `file`: JSON 文件路径
- `md_file`: markdown 文件路径（需包含 `## Feature` / `### SubFeature` heading）

**行为**：
1. 解析 markdown 中的 heading + 属性块 + 表格
2. `## Feature` 和 `### SubFeature` 必须已存在于 JSON，否则报错
3. 属性块覆盖更新已有节点的属性
4. 表格中的 Testpoint 追加到对应 SubFeature
5. `tp_id` 自动分配

**import 前自动调用 `check` 检查 markdown，不通过则拒绝执行。**

## nbl-testplan skip — 标记节点为跳过

```bash
nbl-testplan skip <file> <path> [--unskip]
```

- `--unskip`: 取消跳过标记

## nbl-testplan format — 格式化输出

```bash
nbl-testplan format <file> --format <md|csv|excel> [-o <output>]
```

- `--format`: 输出格式，`md` / `csv` / `excel`（默认 `md`）
- `-o`: 输出文件路径（默认 stdout）
- `--no-number`: md 格式下不添加 heading 编号

从 features.json 生成最终测试计划文档。`--format md` 默认包含完整表格（含 `path2source` 列）。

---

## scripts/section_analyzer.py

```bash
python3 scripts/section_analyzer.py .tp_cache/{doc_name}_decode_work/markdown_output/{doc_name}_decode.md -l <1|2|3> -o .tp_cache/sections.json
```

未迁移至 CLI，仍为独立脚本。

- `-l` / `--split-level`: 章节切分层级
  - `1` = 按 `#` 一级标题切分（默认）
  - `2` = 按 `##` 二级标题切分
  - `3` = 按 `###` 三级标题切分
- `-o`: 输出 JSON 文件路径

输出包含每个章节的 `id`、`title`、`level`、`line_start`、`line_end`、`content_preview`。
