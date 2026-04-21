# nbl-tp-func-gen 设计文档

## 1. 概述

### 1.1 目标

创建一个 Claude Code 插件 `nbl-testplan-generator`，内含一个技能 `nbl-tp-func-gen`，用于：

1. 读取功能规格书（`.docx`）和寄存器手册（`.xlsx`）
2. 交叉引用分析，按 `D→E→F→G` 层级分解功能特性
3. 生成结构化测试点 xlsx 文档（Chapter 1：功能特性）
4. 记录不确定内容到 `fs_reg_slv_review.md`

### 1.2 设计哲学

**混合模型** — Claude 负责内容级语义分析（测试点分解、交叉引用、覆盖率设计），Python 负责结构化处理和机械操作（文档解析、格式输出、JSON 转换）。

大文档（100页+）通过分块索引策略：Python 预分析生成 `spec_tree.json`，Claude 按 Feature 分块处理。

### 1.3 参考素材

- 模板：`/home/alvin.xu/test_center/test_testplan_skills/assets/testplan_template.xlsx`
- UPA 案例：
  - 功能规格：`/home/alvin.xu/test_center/test_testplan_skills/assets/upa/Leonis_PA_Functional_Specification.docx`
  - 寄存器手册：`/home/alvin.xu/test_center/test_testplan_skills/assets/upa/Leonis_datapath_upa.xlsx`
  - 参考测试点：`/home/alvin.xu/test_center/test_testplan_skills/assets/upa/leonis_upa_tp.xlsx`
- DPED 案例：
  - 功能规格：`/home/alvin.xu/test_center/test_testplan_skills/assets/dped/Leonis_PED_Functional_Specification.docx`
  - 寄存器手册：`/home/alvin.xu/test_center/test_testplan_skills/assets/dped/Leonis_datapath_dped.xlsx`
  - 参考测试点：`/home/alvin.xu/test_center/test_testplan_skills/assets/dped/dped_tp.xml`

---

## 2. 插件目录结构

```
nbl-testplan-generator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── nbl-tp-func-gen/
│       ├── SKILL.md
│       ├── reference/
│       │   ├── spec_input/
│       │   │   ├── testplan-func-system-prompt.md   # 功能规格分解指令
│       │   │   └── testplan-cfg-system-prompt.md    # 预留：配置规格分解指令
│       │   ├── template/
│       │   │   └── testplan_template.xlsx         # 测试点文档模板
│       │   └── examples/
│       │       ├── upa/
│       │       │   ├── upa_spec_tree.json         # 参考：upa spec_tree 示例
│       │       │   └── upa_reg_info.json          # 参考：upa reg_info 示例
│       │       └── dped/
│       │           ├── dped_spec_tree.json
│       │           └── dped_reg_info.json
│       └── scripts/
│           ├── __init__.py
│           ├── parsers/
│           │   ├── __init__.py
│           │   ├── md_parser.py
│           │   └── reg_parser.py
│           ├── writers/
│           │   ├── __init__.py
│           │   └── combine_writer.py
│           ├── review/
│           │   ├── __init__.py
│           │   └── review_writer.py
│           ├── reg_to_json.py
│           └── tp_gen.py
├── commands/
└── README.md
```

---

## 3. 数据流与子工作流

### 3.1 五阶段流水线

```
阶段1: Docx→Markdown          阶段2: Markdown结构化解析       阶段3: 寄存器手册→JSON
   │                             │                               │
   ▼                             ▼                               ▼
 [convert.py]                 [md_parser.py]               [reg_parser.py]
   │                             │                               │
   ├────────────── 输出 spec.md ──>├                              │
   │                             ├── 输出 spec_tree.json ──>      │
   │                             │                               ├── 输出 reg_info.json
   │                             │                               │
   └──────────────┬──────────────┴──────────────┬──────────────┘
                  ▼                               ▼
     阶段4: Claude 内容分析 (SKILL.md)
     输入: spec_tree.json + reg_info.json
     输出: testplan_func_raw.json + fs_reg_slv_review.md
                  │
                  ▼
     阶段5: 格式输出 (combine_writer.py)
     输入: testplan_func_raw.json
     输出: testplan.xlsx
```

### 3.2 各阶段详细定义

| 阶段 | 执行方 | 输入 | 输出 | 说明 |
|------|--------|------|------|------|
| 1. Docx→Markdown | Python (`/nbl-docx-to-markdown skill`) | `*.docx` | `*_work/markdown_output/*.md` | 调用现有 skill 转换后读取 Markdown |
| 2. Markdown 结构化解析 | Python (`md_parser.py`) | `*.md` | `spec_tree.json` | 章节树 + 模块特性 + 交叉引用索引 |
| 3. 寄存器手册解析 | Python (`reg_parser.py`) | `*.xlsx` | `reg_info.json` | 寄存器/字段/表项层级结构化 |
| 4. 内容分析 | Claude (SKILL.md 驱动) | `spec_tree.json` + `reg_info.json` | `testplan_func_raw.json` + `fs_reg_slv_review.md` | 核心分析：交叉引用、层级分解、覆盖率设计 |
| 5. 格式输出 | Python (`combine_writer.py`) | `testplan_func_raw.json` | `testplan.xlsx` | 按模板写入 + 格式化 + 边框 |

### 3.3 Phase 4 内部分解（Claude 核心工作）

Phase 4 由于输入数据量大，采用分块处理策略：

```
Phase 4-A: 分块
   - 读取 spec_tree.json，提取模块特性列表
   - 按 Feature 为最小分析单元，将每个 Feature 及其交叉引用章节打包为一个 chunk
   - 每个 chunk 包含：Feature 基本信息 + refs 中的关联章节内容 + 相关 reg_info

Phase 4-B: 逐块分析（循环）
   For each chunk(Feature):
     1. 读取 chunk 内容（spec + reg），交叉引用分析
     2. D→E 分解：按功能维度/场景维度/配置维度/交互维度解构
     3. E→F/G 分解：细化到最小粒度
     4. 填写 H 列（备注）、I 列（仿真条件）、J 列（检查方式）、K 列（覆盖率）、M 列（验证层次）、W 列（路径）
     5. 不确定内容记录到 review 列表
     6. 结果追加到 testplan_func_raw.json

Phase 4-C: 汇总 review
   - 将所有 review 项汇总生成 fs_reg_slv_review.md
   - 文件包含：每个不确定项的 item_id、关联 feature、问题描述、来源、确定信息占位

Phase 4-D: 用户确认（阻塞等待）
   - 向用户展示 fs_reg_slv_review.md
   - 用户确认/补充信息后，Claude 更新 testplan_func_raw.json
   - 确认完成后进入阶段5
```

---

## 4. 关键 JSON Schema

### 4.1 spec_tree.json

```json
{
  "module_name": "upa",
  "spec_title": "Leonis_PA_Functional_Specification",
  "chapters": [
    {
      "chapter_id": "ch2",
      "chapter_title": "功能概述",
      "content_md": "...完整 Markdown 内容...",
      "outline_level": 1
    },
    {
      "chapter_id": "ch3",
      "chapter_title": "模块特性",
      "outline_level": 1,
      "content_md": "...",
      "features": [
        {
          "feature_id": "PA.1",
          "feature_name": "报文编辑范围",
          "content_md": "模块特性章节中此特性的完整原文...",
          "refs": {
            "detail_chapters": ["ch5.1", "ch5.3"],
            "data_structure_chapters": ["ch6.2"],
            "init_chapters": ["ch8"],
            "error_chapters": ["ch9"],
            "ctrl_chapters": ["ch10"]
          }
        }
      ]
    },
    {
      "chapter_id": "ch5.1",
      "chapter_title": "5.1 报文编辑操作详述",
      "content_md": "...",
      "outline_level": 2
    }
  ]
}
```

**交叉引用索引策略（`refs` 字段）**：

1. **显式引用扫描**：识别 "详见 5.1 节"、"参考第6章" 等显式引用语句
2. **关键词匹配**：Feature 名称（或其关键字）出现在其他章节的标题或段落中
3. **寄存器关联**：Feature 涉及的寄存器域段名称出现在其他章节中

### 4.2 reg_info.json

```json
{
  "module_name": "upa",
  "registers": [
    {
      "reg_name": "GLOBAL_CTRL",
      "reg_addr": "0x000",
      "reg_desc": "全局控制寄存器",
      "fields": [
        {
          "field_name": "edit_en",
          "bit_range": "[0]",
          "rw": "RW",
          "reset": "0",
          "desc": "报文编辑使能"
        },
        {
          "field_name": "edit_mode",
          "bit_range": "[2:1]",
          "rw": "RW",
          "reset": "0",
          "desc": "编辑模式：0=replace, 1=insert, 2=delete"
        }
      ]
    }
  ],
  "register_tables": [
    {
      "table_name": "Edit Action Config",
      "entries": []
    }
  ]
}
```

### 4.3 testplan_func_raw.json

此结构为 Claude 分析和 Python 写 xlsx 的接口约定：

```json
{
  "module_name": "upa",
  "spec_name": "upa_spec",
  "chapter": "chapter 1 功能特性",
  "review_items": [
    {
      "item_id": "R1",
      "feature": "报文编辑范围",
      "question": "编辑范围是否支持小于64B的报文？",
      "source": "spec ch3 PA.1",
      "status": "pending"
    }
  ],
  "features": [
    {
      "feature": "报文编辑范围",
      "feature_id": "PA.1",
      "subfeatures_l1": [
        {
          "subfeature_l1": "替换动作",
          "subfeatures_l2": [
            {
              "subfeature_l2": "正常场景-TTL字段替换",
              "_confidence": "confirmed",
              "subfeatures_l3": [
                {
                  "subfeature_l3": "TTL=128替换为64",
                  "remarks": "来源: PA.1 报文编辑范围; 详见 ch5.1 节，触发条件为edit_en=1且mode=0",
                  "stimulus": "【配置】GLOBAL_CTRL.edit_en=1, edit_mode=0(REPLACE)\\n【激励】发送 IPv4 报文，TTL=128",
                  "checking": "by_checker",
                  "coverage": "cp_ttl_values: 0-255, 跨edit_mode={0,1,2}",
                  "priority": "HIGH",
                  "activity": "BT",
                  "path": "Group:$unit::upa_fcov::cg_pkt_edt.cp_repl_ttl"
                }
              ]
            },
            {
              "subfeature_l2": "异常场景-不支持的报文类型",
              "_confidence": "inferred",
              "subfeatures_l3": [
                {
                  "subfeature_l3": "非IPv4报文进入编辑模块",
                  "remarks": "⚠ [推断] 功能规格书未明确提及不支持非IPv4报文的处理行为",
                  "stimulus": "【配置】GLOBAL_CTRL.edit_en=1\\n【激励】发送非IPv4报文",
                  "checking": "by_direct_tc",
                  "coverage": "cp_pkt_type cross edit_en",
                  "priority": "MID",
                  "activity": "BT",
                  "path": "Group:$unit::upa_direct_fcov::direct_pkt_edt_repl"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**关键约定**：

- `_confidence` 字段：\`confirmed\`（spec/reg 中明确提及）或 \`inferred\`（推断内容）
- `path` 字段：使用 **英文标识符**，不直接使用中文。规则：
  - `by_checker` → `Group:$unit::{module_name}_fcov::cg_{eng_feature_id}.cp_{eng_subfeature_id}`
  - `by_direct_tc` → `Group:$unit::{module_name}_direct_fcov::direct_{eng_feature_id}_{eng_subfeature_id}`
  - `by_assertion` → `Group:$unit::{module_name}_assert::assert_{eng_feature_id}_{eng_subfeature_id}`
  - 中文 Feature/Subfeature 到英文缩写的映射在 `combine_writer.py` 中实现（或通过 `_eng_id` 字段提供）
- `remarks` 中推断内容标注 `⚠ [推断]`
- `stimulus` 中 `【配置】` 和 `【激励】` 标记为红色字体（在 xlsx 输出时处理）

---

## 5. xlsx 输出规范（combine_writer.py）

### 5.1 单元格格式要求

| 属性 | 要求 |
|------|------|
| 对齐方式 | 垂直居中、左对齐 |
| 字体 | 微软雅黑、字号 10、黑色 |
| I列特殊 | 其中 `【配置】` 和 `【激励】` 字体颜色为 **红色** |
| 边框 | A-W 列、第一行到最后一行有内容的行全部添加边框 |
| 推断标记 | 包含 `⚠ [推断]` 的行，对应单元格字体颜色为红色 |
| U-V列 | **不需要**默认隐藏 |
| 换行 | 遇到分号 `;`、句号 `。`、冒号 `:`、括号说明时另起一行 |

### 5.2 列定义

| 列 | 内容 | 说明 |
|----|------|------|
| A | 空 | 第三行=plan，第四行=weight |
| B | spec 名称 + chapter | 格式：`{模块名}_spec`，chapter 固定写 `chapter 1 功能特性`，chapter 出现一次标记功能特性开始 |
| C | 不动 | 预留 |
| D | Feature | 顶层特性，outline_level 0 |
| E | Subfeature L1 | 一级子特性，outline_level 1 |
| F | Subfeature L2 | 二级子特性概述，outline_level 2 |
| G | Subfeature L3 | 三级子特性详情，outline_level 3，可选项 |
| H | 备注 | 测试点来源、触发条件、相关寄存器等 |
| I | 仿真条件 | 配置（寄存器）+ 激励（报文数据） |
| J | 检查方式 | by_checker / by_direct_tc / by_assertion |
| K | 功能覆盖率 | covergroup 抽象，枚举需要创建的仓位 |
| L | 空 | 预留 |
| M | 验证层次 | UT/BT/IT/ST/EMU |
| N-P | 空 | 预留 |
| U | weight | 第4行对应单元格固定填写 **5** |
| V | weight | 第4行对应单元格固定填写 **95** |
| W | 覆盖率路径 | 按 J 列类型确定路径规则 |

### 5.3 D-E-F-G 层级规则

```
D（特性名）    → outline_level 0
E（子特性L1）  → outline_level 1
F（子特性L2）  → outline_level 2
G（子特性L3）  → outline_level 3
```

规则：
- 一个 F 可划分为多个 G，每个 G 另起一行
- 若材料不足以划分 G，则 F 为最小粒度（level 2）
- H-W 列只在最小粒度行输出（有 G 则在 G 行，否则在 F 行）

### 5.4 J列和W列关系

| J (checking) | W (path) 格式 |
|--------------|--------------|
| `by_checker` | `Group:$unit::{module_name}_fcov::cg_{eng_feature_id}.cp_{eng_subfeature_id}` |
| `by_direct_tc` | `Group:$unit::{module_name}_direct_fcov::direct_{eng_feature_id}_{eng_subfeature_id}` |
| `by_assertion` | `Group:$unit::{module_name}_assert::assert_{eng_feature_id}_{eng_subfeature_id}` |

---

## 6. SKILL.md 交互流程设计

### 6.1 SKILL.md 核心指令

SKILL.md 是 Claude 执行测试点生成的主控脚本，定义完整的交互流程：

```
1. 接收用户输入：
   - 功能规格书路径（.docx）
   - 寄存器配置手册路径（.xlsx）
   - 输出目录（如不提供，默认 $HOME 或 $TP_WORKDIR）
   - 验证层次（UT/BT/IT/ST/EMU）

2. 阶段1：调用 /nbl-docx-to-markdown skill
   - 将 .docx 转换为 Markdown
   - 读取生成的 .md 文件

3. 阶段2：调用 md_parser.py
   - 解析 .md → spec_tree.json
   - 提取模块特性，建立交叉引用索引

4. 阶段3：调用 reg_to_json.py
   - 解析 .xlsx → reg_info.json

5. 阶段4：内容分析（Claude 核心）
   - 读取 spec_tree.json 和 reg_info.json
   - 按 Feature 分块，逐块分析
   - 对每块：交叉引用 → 分解 → 填写各列 → 记录 review
   - 汇总生成 testplan_func_raw.json + fs_reg_slv_review.md

6. 阶段4-D：用户确认
   - 向用户展示 fs_reg_slv_review.md
   - 等待用户补充确认信息
   - 更新 testplan_func_raw.json

7. 阶段5：调用 combine_writer.py
   - testplan_func_raw.json → testplan.xlsx（按模板格式化）

8. 验证检查
   - 检查输出格式是否符合模板要求
   - 检查 D-E-F-G 层级是否正确
   - 检查 J-W 关系是否正确

9. 输出
   - 主输出：{output_dir}/testplan_func.xlsx
   - 副输出：{output_dir}/fs_reg_slv_review.md
   - 中间文件：{output_dir}/spec_tree.json, reg_info.json, testplan_func_raw.json
```

### 6.2 交互模式：流水线模式

用户输入后，Claude 一次性完成所有分析，将所有不确定点和需确认项汇总在一份 `fs_reg_slv_review.md` 中，然后一次性向用户提问。用户确认后，一次性生成最终 xlsx。每次输入后只问一轮，不要求边分析边问。

---

## 7. 关键脚本设计

### 7.1 md_parser.py

**职责**：解析 Markdown 章节树，提取模块特性，建立交叉引用索引。

**关键能力**：
- 章节标题识别：按 `#` 层级建立 `outline_level` 映射
- 模块特性提取：在 "模块特性" 章节下，按列表/子标题解析 Feature 列表
- 交叉引用索引：为每个 Feature，扫描全文档建立 `refs`：
  - `detail_chapters`：功能详述章节
  - `data_structure_chapters`：数据结构章节
  - `init_chapters`：初始化章节
  - `error_chapters`：错误处理章节
  - `ctrl_chapters`：流控章节
  - `dft_chapters`：DFX 章节
  - `limit_chapters`：应用限制章节

**算法（交叉引用匹配）**：
1. 提取 Feature 名称及其关键词（去除通用词如 "支持"、"功能"）
2. 遍历所有章节标题和内容段落
3. 若章节标题中包含 Feature 关键词，或内容段落中出现 Feature 名称 ≥ 3 次，则标记为关联
4. 匹配寄存器域段标记（如 `` `edit_en` ``、`` `GLOBAL_CTRL` ``），建立 reg 关联

### 7.2 reg_parser.py

**职责**：解析寄存器手册 xlsx，生成层级化的 `reg_info.json`。

**关键能力**：
- 寄存器表识别：按 sheet 识别寄存器描述表（表头含 Address/Field/Bit/Description 等）
- 寄存器层级提取：
  - 寄存器名（合并单元格行）→ register
  - 字段行 → field（bit_range, rw, reset, desc）
- 配置表识别：区分寄存器表和配置参数表

**输出约束**：寄存器信息输出为 JSON 格式，保存到本地，供后续操作读取检索。

### 7.3 combine_writer.py

**职责**：将 `testplan_func_raw.json` 写入 xlsx 模板。

**关键能力**：
- 模板读取：使用 `openpyxl.load_workbook()` 加载模板
- 层级展开：解析 `D→E→F→G` 层级，按行写入
- 格式控制：
  - 字体：`微软雅黑, 10pt, 黑色`；`【配置】`/`【激励】` 红色；推断标记红色
  - 对齐：垂直居中、左对齐
  - 边框：A-W × 内容行范围，全部添加 thin border
  - 换行：在 `;` `。` `:` 后自动插入换行（通过设置 `wrap_text=True` 实现）
- Path 生成：`by_checker`/`by_direct_tc`/`by_assertion` → 按规则生成英文 path
- B 列 chapter 标记：功能特性开始前在 B 列写 `chapter 1 功能特性`
- U/V 列：第4行对应位置固定填入 5 / 95

### 7.4 review_writer.py

**职责**：汇总 review 项，生成 `fs_reg_slv_review.md`。

**输出格式**：

```markdown
# FS/REG 审查记录

## R1: 报文编辑范围

- **问题**: 编辑范围是否支持小于64B的报文？
- **来源**: 模块特性 PA.1, ch3
- **确定信息**: [待填写]
- **状态**: pending

---

## R2: 错误处理...
```

---

## 8. Subagent 分工策略

由于本任务复杂度高，在实现时按照 superpower 工作流切分为多个 subagent：

| Subagent | 职责 | 输入 | 输出 |
|----------|------|------|------|
| **Agent-1: 架构与框架** | 搭建插件目录结构、创建 plugin.json、SKILL.md 骨架、README.md | system prompt + CLAUDE.md | 完整目录结构 + 配置文件 |
| **Agent-2: Parser 开发** | 实现 md_parser.py + reg_parser.py + reg_to_json.py | Markdown/xlsx 参考素材 | 可运行的 parser 脚本 + 测试通过的 JSON 输出 |
| **Agent-3: Writer 开发** | 实现 combine_writer.py + review_writer.py + 模板处理 | testplan_template.xlsx + 示例 JSON | 可运行的 writer 脚本 + 测试通过的 xlsx 输出 |
| **Agent-4: Skill 完善** | 完善 SKILL.md 中的完整交互流程指令、集成所有脚本 | 前面所有输出 | 完整的 SKILL.md + 端到端测试 |
| **Agent-5: 验证与收尾** | 端到端测试（UPA 案例）、修复问题、更新 README/marketplace | UPA 输入素材 | 验证通过的完整插件 |

各 Agent 间通过文件传递：前一 Agent 的输出目录作为后一 Agent 的输入目录。

---

## 9. 移植性设计

### 9.1 路径策略

- 支持环境变量 `TP_WORKDIR` 作为工作目录基准
- 所有中间产物和输出使用相对路径（相对于 `TP_WORKDIR` 或用户指定的输出目录）
- 脚本中通过 `os.environ.get('TP_WORKDIR', os.getcwd())` 获取基准目录

### 9.2 依赖管理

- Python 环境通过 `uv` 管理
- 依赖声明在 `pyproject.toml` 中：`openpyxl`, `markdown` 等
- 可选：提供 `requirements.txt` 作为备选

---

## 10. 验证策略

### 10.1 单元验证

| 组件 | 验证方式 | 通过标准 |
|------|----------|----------|
| md_parser.py | 对 UPA docx 转出的 md 解析 | 生成的 spec_tree.json 包含所有预期 features |
| reg_parser.py | 对 UPA xlsx 解析 | 生成的 reg_info.json 包含所有预期寄存器/字段 |
| combine_writer.py | 用示例 JSON 写入模板 | 生成的 xlsx 格式与模板一致，层级正确 |

### 10.2 端到端验证

以 UPA 案例为端到端测试用例：
- 输入：完整 UPA docx + xlsx
- 输出：testplan.xlsx
- 验证点：
  - 格式：边框、字体、对齐方式符合要求
  - 内容：D-E-F-G 层级与参考测试点对齐
  - 覆盖率：J-W 关系正确

---

## 11. 运行要求

- 中间产物、git 注释均使用中文
- Python 通过 `uv` 管理
- 中间临时文件（如 `.tp_cache/`、`tests/superpowers/` 等）加入 `.gitignore`
- 涉及 docx 操作必须调用 `/nbl-docx-to-markdown skill`

---

*设计文档版本: 1.0*
*日期: 2026-04-21*
