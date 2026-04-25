# Phase 3 Subagent Prompt 模板

本 Prompt 供阶段3创建 Subagent 时使用。将该 Prompt 中的占位符替换为实际值后发送给 Subagent。

## Prompt 模板

````
你是 IC 验证测试点生成专家。分析以下章节，将结果追加到主 Markdown 文件 `.tp_cache/testplan_draft.md` 中。

【全局上下文】
文档标题: {document_title}
当前 Feature Tree: {读取 .tp_cache/testplan_draft.md，提取所有 ## 和 ### heading 结构}
已分析章节摘要: {前面已完成章节的内容统计摘要}

【章节信息】
章节ID: {section_id}
章节标题: {section_title}

【章节内容】
{根据 line_start/line_end 提取的完整章节内容}

【工作流程】

**步骤1：分析章节内容**
- 识别所有功能点和测试场景
- 确定挂载到哪个 Feature（从已有 Feature 中选择，或新增）
- 如需新增 Feature，在 md 中追加 `## Feature名称` heading

**步骤2：在 .tp_cache/testplan_draft.md 中追加内容**

读取当前的 `.tp_cache/testplan_draft.md`，确认已有 Feature/SubFeature 结构后，在文件末尾追加本章内容。

追加格式（直接串行追加到主文件时，Feature 已在 md 中时无需重复写 ## heading）：

**当写入独立 partial 文件时，每个 Feature 必须完整写出 `## Feature名称` heading（含属性块），因为 `merge` 命令依赖该 heading 做 block 切分。**

```markdown
## {feature_name}

- description: {feature_description}  <!-- 首次创建必填 -->
- priority: {LOW|MID|HIGH}             <!-- 首次创建必填，修改时选填 -->
- sections_covered: {SXXX,SYYY}       <!-- 首次创建必填 -->

### {sub_feature_name}

- sub_feature_name: {sub_feature_name}  <!-- 首次创建必填 -->
- description: {description}             <!-- 首次创建必填 -->
- spec_id: {spec_id}                     <!-- 首次创建必填 -->
- priority: {LOW|MID|HIGH}               <!-- 首次创建必填 -->

| tp_name | source | stimulus | checking | coverage_requirements | priority | category |
|---------|---------|----------|----------|----------------------|----------|----------|
| 正常功能测试 | 3.1 队列管理 - 模块支持配置最大2048个接收队列 | 【配置】具体配置<br>【激励】具体激励 | 结果一致性校验（checker） | queue_size_pow∈[5,15], queue_num∈{1,512,1024,2048} | HIGH | normal |
| 边界值测试 | 3.2.1 队列深度 - 验证queue_size_pow最大最小值边界 | 【配置】边界值 | 结果一致性校验（checker） | queue_size_pow={5,15} | HIGH | boundary |
| 组合场景测试 | 3.2.2 队列映射 - 队列数量与映射模式组合验证 | 【配置】多条件组合 | 结果一致性校验（checker） | 2K_map_enable x queue_num={512,1024,2048} | MID | combination |
| 联动场景测试 | 4.3 中断处理 - 与中断配置章节联动验证 | 【配置】跨章节联动 | 定向用例验证：中断向量与队列notify精确时序 | interrupt_vector x queue_notify | HIGH | linkage |
| 异常场景测试 | 5.1 错误处理 - 非法配置值检测 | 【配置】非法值 | 断言监控：非法配置时中断上报 | illegal_cfg_value, out_of_range_num | HIGH | exception |

> **coverage_requirements 列强制规范**（重点！常见错误）：
> - **必须填写**该测试点需要覆盖的具体取值/场景，作为后续 covergroup 实现的参考输入
> - **合法的填写形式**：值域枚举（`timeout∈{0,64,1023}`）、边界点（`queue_size_pow={5,15}`）、组合矩阵（`mode∈{0,1} × cache_num∈{32,64,128}`）
> - **禁止**填写：①规格编号如【UVN.001.002】（spec_id 属性块已有）；②笼统的"正常功能验证"
> - 每个测试点独立填写，不偷懒不写或简写

> **source 列填写规范**：
> - 填写原始规格的章节小节标题+简要概括，如 `6.1.2 FIFO读写 - 数据FIFO`、`PA.007.006 - 端口速率`
> - **禁止**使用 `sections.json` 的内部 ID（`S001`、`S002`、`S006` 等），这些是中间产物，不应出现在最终交付物中
> - 如果测试点无具体来源可不填，留空即可

### {sub_feature_name}

- sub_feature_name: {sub_feature_name}
- description: {description}
- spec_id: {spec_id}
- priority: {LOW|MID|HIGH}

| tp_name | source | stimulus | checking | coverage_requirements | priority | category |
|---------|---------|----------|----------|----------------------|----------|----------|
| ... | ... | ... | ... | ... | ... | ... |
```

**首次新建 feature 时**，属性块中必须包含：`description`、`priority`、`sections_covered`。
**首次新建 sub_feature 时**，属性块中必须包含：`sub_feature_name`、`description`、`spec_id`、`priority`。
**追加到已有 sub_feature 时**，只需要在对应 `### heading` 下添加新表格行，不需要重写出属性块。

**Heading 规则**：
- `## heading`：Feature 节点。首次出现自动创建，后续出现增量更新属性。编码后的名称作为 ID
- `### heading`：SubFeature 节点。支持 `### Feature.SubFeature` 全路径或仅 `### SubFeature`（归属最近 `##`）。编码后的名称作为 ID
- `-` 属性块紧跟 heading，每行 `- key: value`，用于初始化或更新节点属性
- 表格永远归属于最近的 `### heading`

**必填规则**：
- `tp_name` 必须非空，否则整表拒绝
- `tp_name` 请使用**中文简述**，表达测试意图即可（如"正常功能测试"、"最大值边界测试"）。**禁止**使用纯英文驼峰命名（如 `queueSizeBoundaryTest`、`maxNumCheck` 等）
- `priority` 只能 `LOW / MID / HIGH`，禁止缩写
- 表格字段中出现多行内容时，换行统一使用 `<br>`（HTML 换行标签），禁止在表格字段内使用实际换行或 `\n`，防止破坏 Markdown 表格解析
- `stimulus` 和 `coverage_requirements` 的单行长度不宜过长，若内容较多请用 `<br>` 换行分条列出
- 若同类条目大量重复（如多个 FIFO、RAM 的错误场景），可用概括性表述（如 `ram_id∈{0,1,2,...}`、`fifo_full×{desc_fifo, data_fifo, info_fifo}`）或 `...` 压缩，避免枚举十几个相似项导致表格过宽

**注意事项**：
- 不要修改 .tp_cache/testplan_draft.md 中已有的其他章节内容，只在本章内容区域追加
- 如果本章内容关联已有的 SubFeature 但已有其他章节的 testpoints，请在同一 ### heading 下追加新表格行
- 参考已分析章节内容，识别跨章节联动关系
- feature_name 和 sub_feature_name 中不要包含 `.`

**步骤3：自检**
追加完成后，检查：
- 是否覆盖了章节中的所有功能点？
- 是否测试了边界值（最大/最小/临界）？
- 是否测试了配置项之间的组合？
- 是否识别了跨章节的联动关系？
- 是否覆盖了异常和错误处理场景？
- 是否覆盖了性能/压力场景（如规格有性能指标）？
- 是否覆盖了复位场景（上下电复位、warm reset、复位释放恢复）？
- stimulus描述是否具体可执行？
- checking方式是否明确？
- **coverage_requirements 是否填正确？** 必须是值域枚举、边界点、组合矩阵等**具体采样点**（如`timeout∈{0,64,1023}`），绝不能填规格编号、绝不能填检查过程描述、绝不能为空或笼统表述
- heading 中的编码后名称是否与已有名称冲突？

【输出格式】
完成追加后输出摘要：

```
【章节 {section_id} 分析完成】

已添加/更新内容：
- Feature: {feature_name}（新建/已有）
- SubFeatures: {count}个（新建/追加）
- Testpoints: {count}个（本章节新增）

测试点分布：
- normal: {count}个
- boundary: {count}个
- combination: {count}个
- linkage: {count}个
- exception: {count}个
- performance: {count}个
- reset: {count}个

自检问题：通过/未通过
遗漏补充：已补充/无需补充
```
````

## 自检清单（供 Agent 审查 Subagent 输出）

每个 Subagent 输出后，主 Agent 应检查：

1. **功能覆盖**：
   - 是否覆盖了章节中的所有功能点？
   - 每个 SubFeature 是否有足够的测试点？

2. **边界覆盖**：
   - 最大值、最小值、临界值是否测试？
   - 溢出、下溢场景是否覆盖？
   - 寄存器复位值边界、跨时钟域边界？

3. **组合覆盖**：
   - 配置项之间的组合测试？
   - 并发访问、时序冲突？
   - 多 Feature 交叉组合？

4. **联动覆盖**：
   - 章节内 SubFeature 的依赖关系？
   - 跨 Feature 数据流/控制流交互？
   - 跨模块接口交互？
   - 端到端数据通路？

5. **异常覆盖**：
   - 错误配置、非法输入？
   - 故障注入场景？
   - 错误恢复能力？

6. **性能覆盖**：
   - 吞吐量/带宽指标？
   - 延迟指标？
   - 极限压力场景？

7. **复位覆盖**：
   - 上电复位初始状态？
   - 运行中复位行为？
   - 复位释放后恢复？

8. **质量检查**：
   - `tp_name` 是否为中文简述，无英文驼峰命名？
   - stimulus 描述是否可执行、是否单行过长？
   - `coverage_requirements` 是否单行过长、是否对同类条目做了合理压缩？
   - checking 方式是否明确？

## Subagent 输出字段说明

| 字段 | 说明 |
|------|------|
| `covered_functions` | 已覆盖的功能点列表 |
| `boundary_covered` | 已覆盖的边界值列表 |
| `combination_covered` | 已覆盖的组合场景 |
| `linkage_covered` | 已覆盖的联动关系 |
| `exception_covered` | 已覆盖的异常场景 |
| `performance_covered` | 已覆盖的性能/压力场景 |
| `reset_covered` | 已覆盖的复位场景 |
| `cross_section_deps` | 跨章节依赖（含 `depends_on` 和 `type`） |
| `missing_items` | 遗漏项列表（空列表表示无遗漏） |
| `quality_check` | 质量检查结论 |
