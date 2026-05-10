# 工作流示例

## 示例1：完整流程

```
用户：帮我根据 Orion_UVN_Functional_Specification.docx 生成测试计划

Agent 执行：
1. 检测到 docx 格式，调用 nbl-docx-to-markdown 转换 → `.tp_cache/Orion_UVN_Functional_Specification_decode_work/markdown_output/Orion_UVN_Functional_Specification_decode.md`
2. 调用 nbl-testplan doc-meta generate -l 1 生成 .tp_cache/{doc_name}_docmeta.json（11个章节）
3. 调用 nbl-testplan init 创建 .tp_cache/features.json
4. 调用独立 subagent 分析文档，生成 .tp_cache/testplan_draft.md 骨架
5. 处理章节（各章节 `line_count` 总和约 1514 行）：
   - 主 Agent 按 Feature 将 11 章分为 3 组：
     - Group-A（队列管理/描述符预取）→ subagent 生成 `.tp_cache/partial_a.md`
     - Group-B（性能描述/功能详述）→ subagent 生成 `.tp_cache/partial_b.md`
     - Group-C（流控/初始化/错误处理/DFX/低功耗）→ subagent 生成 `.tp_cache/partial_c.md`
   - 主 Agent 串行合并：partial_a → partial_b → partial_c → 合并到 `.tp_cache/testplan_draft.md`

   （小规模文档示例：`line_count` 总和 ≤ 500 行 → 主 Agent 直接逐章串行追加到 testplan_draft.md）
6. 调用 nbl-testplan build 从 .tp_cache/testplan_draft.md 生成 .tp_cache/features.json
7. 调用 nbl-testplan tree 验证完整结构
8. 调用 nbl-testplan format 生成 Markdown 测试计划
```

## 示例2：单个章节的分析过程

```
用户：查看 S002 章节的处理详情

Agent 执行：
调用 subagent 分析 S002 章节 → 追加到 .tp_cache/testplan_draft.md

测试点分布：
- normal: 15个（典型配置、业务流程、数据通路）
- boundary: 5个（最大值2048、最小值1、临界值0、溢出、下溢）
- combination: 3个（队列数量×映射模式、并发队列访问、时序冲突）
- linkage: 2个（与S001中断配置联动、章节内队列配置与调度联动）
- exception: 2个（非法配置、错误处理）
- 总计: 27个测试点

自检结果：
{
  "covered_functions": ["队列配置", "队列映射", "队列调度"],
  "boundary_covered": ["最大值2048", "最小值1", "临界值0"],
  "combination_covered": ["队列数量×映射模式"],
  "linkage_covered": ["与S001中断配置联动"],
  "exception_covered": ["非法配置", "错误处理"],
  "cross_section_deps": [{"depends_on": "S001", "type": "配置依赖"}],
  "missing_items": [],
  "quality_check": "通过自检，所有维度测试点覆盖完整"
}
```

## 示例3：自检发现问题并修改

```
用户：subagent 如何进行自检？

场景：subagent 生成测试点后，发现遗漏

subagent 内部流程：
1. 生成初始测试点（20个）
2. 执行自检清单：
   ✓ 是否覆盖了所有功能点？
     - 发现：遗漏了"队列删除"功能
   ✓ 是否测试了边界值？
     - 发现：缺少最小值边界测试
   ✓ 是否覆盖了联动关系？
     - 发现：未识别与S001的依赖
3. 内部修改完善：
   - 新增队列删除功能的 normal 测试点
   - 补充最小值边界测试点
   - 补充与S001的联动测试点
4. 输出最终版本（27个测试点）：
   {
     "self_review": {
       "covered_functions": ["队列配置", "队列映射", "队列删除"],
       "missing_items": [],
       "quality_check": "通过自检，已补充遗漏的测试点"
     }
   }
```

## 示例4：跨章节联动识别

```
用户：subagent 如何处理跨章节联动？

场景：处理 S003 章节时，参考 S001/S002 的摘要

subagent 内部流程：
1. 读取"已分析章节摘要"：
   - S001: 队列配置、中断配置
   - S002: 队列调度、队列映射
2. 分析 S003 章节内容，识别联动：
   - S003的"中断处理"功能依赖 S001的"中断配置"
   - S003的"报文分发"功能与 S002的"队列调度"有交互
3. 生成联动测试点：
   {
     "tp_id": "TP020",
     "category": "linkage",
     "related_section": "S001",
     "stimulus": "【配置】按S001章节配置中断向量表\n【激励】触发S003章节的中断事件"
   }
4. 自检确认联动覆盖完整
```

## 示例5：动态调整 Feature

```
用户：subagent 发现内容不适合现有 Feature，如何处理？

场景：分析 S004 章节时，发现需要新 Feature

subagent 处理：
1. 分析 S004 章节内容
2. 发现涉及"错误检测机制"，不适合挂载到现有 Feature
3. 在 .tp_cache/testplan_draft.md 中追加新 Feature：

   ```markdown
   ## 错误处理

   - description: 错误检测和中断上报功能
   - priority: HIGH
   - sections_covered: S004
   ```

4. 继续在新 Feature 下追加 SubFeature 和 Testpoint
```

## 示例6：查看 Feature Tree 结构

```
用户：显示当前的 Feature 层级结构

Agent 执行：
nbl-testplan tree .tp_cache/features.json

输出：
[f000] 队列管理
    -- [s000] 队列数量与映射模式
        -- [t000] 验证2K队列模式正常功能
        -- [t001] 验证1K队列模式正常功能
    -- [s001] 队列深度配置
        -- [t000] 验证最小队列深度32
[f001] 描述符预取
    -- [s000] 无包触发预取
        -- [t000] 验证先使能后notify触发无包预取
```

## 示例7：merge 与 check 配合使用

```
用户：并行生成了两个 partial 文件，需要合并

Agent 执行：
1. 检查各 partial 格式（merge 会自动执行）
2. 如果 partial_a.md 有格式错误：
   ❌ partial_a.md 格式检查未通过，发现 N 个错误，合并已中止:
      [ERROR] 第 266 行 | TABLE_ROW_TRUNCATED
      ...
   AI 提示: 请将跨行的单元格内容合并为一行，并用 <br> 替代换行符；
           确保每个表格行末尾以 | 结尾。
3. 修复后重新执行：
   nbl-testplan merge .tp_cache/testplan_draft.md .tp_cache/partial_a.md .tp_cache/partial_b.md
```
