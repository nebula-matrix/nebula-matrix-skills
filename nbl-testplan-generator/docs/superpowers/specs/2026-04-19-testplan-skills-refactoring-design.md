# nbl-testplan-generator 插件重构设计

**目标：** 将 nbl-testplan-generator 插件重构为三个独立的 skills（testplan-func、testplan-cfg、nbl-testplan-generator），解除耦合，支持独立调用和组合调用，集成 `/nbl-docx-to-markdown` 技能处理 docx 文档。

**架构：** Skill 组合调用架构，nbl-testplan-generator 通过 Skill tool 调用 testplan-func 和 testplan-cfg。

**技术栈：** Python 3.12+, openpyxl, pytest, uv

---

## 1. 整体架构

```
nbl-testplan-generator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── nbl-testplan-generator/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── combine_writer.py
│   │   │   ├── xlsx_writer.py
│   │   │   └── validator.py
│   │   ├── review/
│   │   │   └── review_writer.py
│   │   └── templates/
│   │       └── testplan_template.xlsx
│   ├── testplan-func/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── md_parser.py
│   │   │   ├── reg_to_json.py
│   │   │   ├── func_writer.py
│   │   │   ├── xlsx_writer.py
│   │   │   └── validator.py
│   │   └── templates/
│   │       └── func_prompt.md
│   └── testplan-cfg/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── md_parser.py
│       │   ├── reg_to_json.py
│       │   ├── cfg_writer.py
│       │   ├── xlsx_writer.py
│       │   └── validator.py
│       └── templates/
│           └── cfg_prompt.md
└── tests/
    ├── conftest.py
    ├── test_testplan_func.py
    ├── test_testplan_cfg.py
    ├── test_testplan_generator.py
    ├── test_md_parser.py
    ├── test_reg_to_json.py
    ├── test_xlsx_writer.py
    ├── test_validator.py
    └── fixtures/
        ├── sample_spec.md
        ├── sample_reg.xlsx
        └── expected_output/
```

**关键点：**
- 三个 skills 各自维护独立脚本目录，解除耦合
- 共用模板文件位于 `nbl-testplan-generator/templates/`
- 各 skill 有独立的 validator.py 检查输出合法性
- 脚本可重写或重构以适应新架构

---

## 2. testplan-func Skill 设计

**功能：** 独立生成功能特性测试点（Ch1）

### 2.1 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `spec_path` | 是 | — | 功能规格书 .docx 或 .md |
| `reg_path` | 是 | — | 寄存器配置 .xlsx |
| `--output` | 否 | spec同目录 | 输出路径 `{basename}_testplan_func.xlsx` |

### 2.2 处理流程

```
1. 解析参数
2. 文档转换：
   - 如输入是 .docx → 调用 Skill: nbl-docx-to-markdown
   - 如输入是 .md → 直接使用
3. 解析 markdown → 提取 Feature ID、功能详述
4. 解析寄存器 xlsx → JSON
5. 交叉引用分析（Feature ↔ 寄存器）
6. 生成 D-E-F-G 层级测试点
7. 写入 xlsx
8. 运行 validator 检查输出
9. 报告结果
```

### 2.3 输出格式

- xlsx 文件：D-E-F-G 四级结构，G 为最小粒度
- 若材料不足以划分到 G 层级，则 F 为最小粒度
- H-W 列只在最小粒度行输出

---

## 3. testplan-cfg Skill 设计

**功能：** 独立生成配置特性测试点（Ch2），或增量补充到现有 func_xlsx

### 3.1 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `spec_path` | 是 | — | 功能规格书 .docx 或 .md |
| `reg_path` | 是 | — | 寄存器配置 .xlsx |
| `--func-xlsx` | 否 | — | 已有的功能特性 xlsx（可选） |
| `--output` | 否 | spec同目录 | 输出路径 |

### 3.2 处理流程（独立运行，无 --func-xlsx）

```
1. 解析参数
2. 文档转换：
   - 如输入是 .docx → 调用 Skill: nbl-docx-to-markdown
   - 如输入是 .md → 直接使用
3. 解析 markdown → 提取寄存器名称（标记"已在规格中描述"）
4. 解析寄存器 xlsx → JSON
5. 过滤/分组寄存器（排除 *_int_*, *_fifo_* 等）
6. 生成 Ch2 配置特性测试点
7. 写入 xlsx（仅 Ch2）
8. 运行 validator 检查输出
9. 报告结果
```

### 3.3 处理流程（增量模式，提供 --func-xlsx）

```
1. 解析参数
2. 文档转换（同上）
3. 解析 markdown → 提取寄存器名称
4. 解析寄存器 xlsx → JSON
5. 过滤/分组寄存器
6. 从 func_xlsx 提取已覆盖寄存器
7. 交叉引用标记 skip（已在功能特性中覆盖）
8. 追加未覆盖寄存器的测试点
9. 写入 xlsx（整合 Ch1 + Ch2）
10. 运行 validator 检查输出
11. 报告结果
```

### 3.4 输出文件命名

- 独立运行：`{basename}_testplan_cfg.xlsx`
- 增量模式：默认覆盖 `--func-xlsx`，或指定 `--output`

---

## 4. nbl-testplan-generator Skill 设计

**功能：** 整合调用 testplan-func 和 testplan-cfg，生成完整测试计划

### 4.1 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `spec_path` | 是 | — | 功能规格书 .docx 或 .md |
| `reg_path` | 是 | — | 寄存器配置 .xlsx |
| `--output` | 否 | spec同目录 | 输出路径 `{basename}_testplan.xlsx` |
| `--mode` | 否 | batch | 处理模式：single/batch |
| `--features` | 否 | all | 指定处理的 Feature ID |
| `--refresh-review` | 否 | — | review 文件路径（刷新模式） |

### 4.2 处理流程

```
1. 解析参数
2. 调用 Skill: testplan-func → 生成 func_xlsx
3. 调用 Skill: testplan-cfg（传入 func_xlsx）→ 生成整合 xlsx
4. 运行 combine_writer 处理整合细节
5. 运行 validator 检查输出
6. 生成 review 文件（如有问题）
7. 报告结果
```

### 4.3 整合逻辑

- Ch1（功能特性）在前
- Ch2（配置特性）在后
- 保留所有 skip 标记和交叉引用信息

### 4.4 刷新模式（--refresh-review）

- 解析用户确认的 review 反馈
- 更新测试点（确认/否定/部分确认）
- 重新生成 xlsx 和 review

---

## 5. 关键约束

### 5.1 docx 处理必须调用 `/nbl-docx-to-markdown`

```
❌ 禁止：自建脚本直接解析 .docx 文件
✅ 必须：使用 Skill tool 调用 nbl-docx-to-markdown

示例代码（SKILL.md 中）：
Invoke Skill tool with:
  skill: "nbl-docx-to-markdown"
  args: "$spec_path --output-dir $TP_WORKDIR"
```

### 5.2 D-E-F-G 层级结构

```
D（特性名）→ outline_level 0
E（子特性L1）→ outline_level 1
F（子特性L2概述）→ outline_level 2
G（子特性L2详情）→ outline_level 3

规则：
- 一个 F 可划分为多个 G，每个 G 另起一行
- 若材料不足以划分 G，则 F 为最小粒度（level 2）
- H-W 列只在最小粒度行输出（有 G 则在 G 行，否则在 F 行）
```

**xlsx 输出示例（有 G 层级）：**

| 行号 | D | E | F | G | H | I | J-L | M | W | level |
|------|---|---|---|---|---|---|-----|---|---|-------|
| 6 | 特性A | | | | | | | | | 0 |
| 7 | | 子特性A1 | | | | | | | | 1 |
| 8 | | | 概述1 | | | | | | | 2 |
| 9 | | | | 详情1a | 备注 | 激励 | ... | BT | 路径 | 3 |
| 10 | | | | 详情1b | 备注 | 激励 | ... | BT | 路径 | 3 |
| 11 | | | 概述2 | | | | | | | 2 |
| 12 | | | | 详情2a | 备注 | 激励 | ... | BT | 路径 | 3 |

**xlsx 输出示例（无 G 层级，F 为最小粒度）：**

| 行号 | D | E | F | G | H | I | J-L | M | W | level |
|------|---|---|---|---|---|---|-----|---|---|-------|
| 6 | 特性A | | | | | | | | | 0 |
| 7 | | 子特性A1 | | | | | | | | 1 |
| 8 | | | 概述1 | | 备注 | 激励 | ... | BT | 路径 | 2 |
| 9 | | | 概述2 | | 备注 | 激励 | ... | BT | 路径 | 2 |

### 5.3 输出文件命名规范

```
testplan-func: {basename}_testplan_func.xlsx
testplan-cfg:  {basename}_testplan_cfg.xlsx（独立运行）
nbl-testplan-generator: {basename}_testplan.xlsx
```

### 5.4 Skill 组合调用

```
nbl-testplan-generator 调用方式：

Invoke Skill tool with:
  skill: "testplan-func"
  args: "$spec_path $reg_path --output $func_output"

Invoke Skill tool with:
  skill: "testplan-cfg"
  args: "$spec_path $reg_path --func-xlsx $func_output --output $final_output"
```

---

## 6. 测试策略

**测试框架：** pytest

### 6.1 测试覆盖范围

| 测试类 | 测试内容 |
|--------|----------|
| testplan-func 独立调用 | 输入 docx/md，验证输出 xlsx 结构正确 |
| testplan-cfg 独立调用 | 输入 docx/md + xlsx，验证输出仅 Ch2 |
| testplan-cfg 增量模式 | 输入 func_xlsx，验证 skip 标记正确 |
| nbl-testplan-generator | 验证整合输出包含 Ch1 + Ch2 |
| Skill 调用验证 | 确认使用 `/nbl-docx-to-markdown`，非直接解析 docx |
| D-E-F-G 层级 | 验证 outline_level 正确，H-W 列仅在最小粒度 |
| 输出文件命名 | 验证命名规范符合约束 |
| 边界情况 | 无 Feature ID、无寄存器、空文档等 |

### 6.2 测试目录结构

```
tests/
├── conftest.py                    # 公共 fixtures
├── test_testplan_func.py          # testplan-func 测试
├── test_testplan_cfg.py           # testplan-cfg 测试
├── test_testplan_generator.py     # nbl-testplan-generator 测试
├── test_md_parser.py              # markdown 解析测试
├── test_reg_to_json.py            # 寄存器解析测试
├── test_xlsx_writer.py            # xlsx 输出测试
├── test_validator.py              # 输出验证测试
└── fixtures/
    ├── sample_spec.md             # 测试用 markdown
    ├── sample_reg.xlsx            # 测试用寄存器
    └── expected_output/           # 预期输出
```

---

## 7. 实现优先级

### 阶段 1：基础设施
- 1.1 创建目录结构（三个 skills 的 scripts/）
- 1.2 提取/复制/重写公共脚本到各 skill
- 1.3 创建测试 fixtures（sample_spec.md, sample_reg.xlsx）

### 阶段 2：testplan-func（可独立测试）
- 2.1 md_parser.py（处理 markdown）
- 2.2 reg_to_json.py（解析寄存器）
- 2.3 func_writer.py（生成 Ch1）
- 2.4 xlsx_writer.py（格式化输出）
- 2.5 validator.py（输出检查）
- 2.6 SKILL.md（调用流程）
- 2.7 单元测试 + 集成测试

### 阶段 3：testplan-cfg（可独立测试）
- 3.1 md_parser.py（提取寄存器名称）
- 3.2 reg_to_json.py
- 3.3 cfg_writer.py（支持独立/增量模式）
- 3.4 xlsx_writer.py
- 3.5 validator.py
- 3.6 SKILL.md
- 3.7 单元测试 + 集成测试

### 阶段 4：nbl-testplan-generator（整合层）
- 4.1 combine_writer.py（整合逻辑）
- 4.2 review_writer.py（review 生成）
- 4.3 validator.py
- 4.4 SKILL.md（Skill 组合调用）
- 4.5 集成测试

### 阶段 5：验收测试
- 5.1 端到端测试（三个 skills 交叉使用）
- 5.2 输出合法性验证
- 5.3 Skill 调用链验证（确保调用 /nbl-docx-to-markdown）

### 关键里程碑
- 阶段 2 完成：testplan-func 可独立使用
- 阶段 3 完成：testplan-cfg 可独立使用
- 阶段 4 完成：nbl-testplan-generator 可整合调用
- 阶段 5 完成：所有功能验收通过

---

## 8. 原有功能保留清单

| 功能 | 归属 Skill | 说明 |
|------|------------|------|
| 解析 spec docx → markdown | testplan-func, testplan-cfg | 通过 `/nbl-docx-to-markdown` |
| 解析寄存器 xlsx → JSON | testplan-func, testplan-cfg | reg_to_json.py |
| 交叉引用分析（Feature ↔ 寄存器）| testplan-func | md_parser + reg_to_json |
| 生成 D-E-F-G 层级功能特性 | testplan-func | func_writer.py |
| 过滤/分组寄存器 | testplan-cfg | cfg_writer.py |
| 交叉引用标记 skip | testplan-cfg | cfg_writer.py |
| 整合 Ch1 + Ch2 | nbl-testplan-generator | combine_writer.py |
| 生成 review 文件 | nbl-testplan-generator | review_writer.py |
| 刷新模式（--refresh-review）| nbl-testplan-generator | SKILL.md 流程 |
| J-W 路径对应验证 | nbl-testplan-generator | combine_writer.py |

---

## 9. 文件变更摘要

| 文件 | 操作 | 说明 |
|------|------|------|
| skills/testplan-func/SKILL.md | 重写 | 完整独立调用流程 |
| skills/testplan-func/scripts/* | 新建/重写 | 独立脚本目录 |
| skills/testplan-cfg/SKILL.md | 重写 | 支持独立/增量模式 |
| skills/testplan-cfg/scripts/* | 新建/重写 | 独立脚本目录 |
| skills/nbl-testplan-generator/SKILL.md | 重写 | Skill 组合调用 |
| skills/nbl-testplan-generator/scripts/* | 重构 | 整合层脚本 |
| tests/* | 新建 | 完整测试套件 |
