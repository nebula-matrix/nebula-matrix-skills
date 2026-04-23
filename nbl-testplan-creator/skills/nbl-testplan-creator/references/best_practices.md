# 最佳实践

## 1. 粗划分粒度选择

根据文档大小和复杂度选择合适的切分层级：

| 文档大小 | 建议层级 | 说明 |
|----------|----------|------|
| < 1000 行 | 一级标题 (`-l 1`) | 文档较小，按 `#` 切分即可 |
| 1000-3000 行 | 一级标题 (`-l 1`) | 中等文档，一级标题通常够用 |
| > 3000 行 | 二级标题 (`-l 2`) | 大文档，按 `##` 切分避免章节过大 |

## 2. Feature 规划原则

**划分依据**：
- 优先按**验证功能域**划分，而非简单跟随文档章节
- 每个 Feature 应具有独立的验证价值
- 考虑验证资源分配（优先级设置）

**动态调整时机**：
- 当某个章节内容明显不适合现有 Feature 时，果断新增
- 避免强行挂载导致逻辑混乱
- 新增 Feature 后直接追加到 `.tp_cache/testplan_raw.md`

## 3. 弹性执行策略

**策略选择**（由主 Agent 根据内容规模决定）：
- **小规模文档（`sections.json` 中各章节 `line_count` 总和 ≤ 500）**：主 Agent 直接串行处理，或自己拆分后逐章分析
- **大规模文档（`line_count` 总和 > 500）**：按 Feature 域分组并行，各 subagent 生成 partial 文件，最后主 Agent 串行合并
- **并发上限**：同时运行的 subagent 不超过 3 个，防止 API 访问限制

**分组并行 + 串行合并**（大文档模式）：
1. 主 Agent 按 **Feature 域** 进行分组（不按 Section 拆分）：
   - 每个 Feature 作为一个独立的分析单元，完整分配给单个 subagent
   - 同一 Feature 的全部 SubFeature 和 Testpoint 由同一个 subagent 负责，合并后该 Feature 内容自然连续
   - 将关联性强的相邻 Feature 合并到同一组，控制每组涉及的章节总行数在合理范围
2. 针对每组 Feature，主 Agent 创建一个独立的 subagent，将对应 Feature 及其涉及的章节信息作为上下文传入；该 subagent 自行读取 `sections.json` 定位相关章节、逐节分析并生成 `.tp_cache/partial_{N}.md`
3. 主 Agent 调用 `nbl-testplan merge` 合并所有 partial 文件到 `testplan_raw.md`
   ```bash
   nbl-testplan merge .tp_cache/testplan_raw.md .tp_cache/partial_*.md
   ```

   **merge 前会自动调用 `check` 检查所有 partial 文件，如果有格式错误则拒绝合并并输出 AI 修复建议。**
4. 合并后检查：同一 Feature 的 SubFeature 是否连续出现，不要穿插其他 Feature

**为什么按 Feature 分组，而不是按 Section**：
- 同一 section 往往涉及多个 Feature，按 Section 拆分会导致一个 Feature 的测试点分散到多个 subagent 中
- 按 Feature 分组保证 Feature 完整性，合并时无需再重组
- partial 文件方式让每个 subagent 写独立文件，合并逻辑清晰可控
- 同时多个 subagent 追加同一文件会导致内容交错、heading 冲突

**自检机制**：
- subagent 必须完成自检后才能输出
- 自检发现的问题必须在内部修改完善
- 输出中包含 self_review 字段，记录自检结果

## 4. Testpoint 设计策略（全维度覆盖）

### normal — 正常场景（约 50-60%）

- 典型配置和业务流程
- 常用功能的验证
- 基本的数据通路测试
- 标准使用场景

### boundary — 边界条件（约 20-30%）

- 最大值、最小值、临界值测试
- 溢出、下溢场景
- 边界组合测试

**提取要点**：
- 数据宽度的最大值和最小值
- 地址空间的边界
- 计数器的溢出和下溢
- FIFO 的满和空状态
- 时钟频率的最大最小限制

### combination — 组合场景（约 10-20%）

- 配置项组合测试
- 并发访问、时序冲突
- 多种条件同时生效的场景

### linkage — 联动场景（约 5-10%）

- 章节内 SubFeature 联动
- 跨章节功能依赖（参考已分析章节摘要）

### exception — 异常场景（约 5-10%）

- 错误配置、非法输入
- 故障注入、异常处理
- 错误恢复能力

## 5. 字段填写要求

| 字段 | 要求 |
|------|------|
| `stimulus` | 配置和激励要具体可执行，使用【配置】和【激励】标签区分 |
| `checking` | 明确检查方式：`by_checker` / `by_direct_tc` / `by_assertion` |
| `coverage_requirements` | 枚举需覆盖的取值/场景（值域、边界点、组合矩阵等），作为 covergroup 实现参考 |
| `category` | 标记测试点类别：`normal` / `boundary` / `combination` / `linkage` / `exception` |
| `spec_id` | 关联到规格条款，如 `【UVN.001.004】` |

## 6. 自检清单

### 功能覆盖
- [ ] 覆盖了章节中的所有功能点
- [ ] 每个 SubFeature 有足够的测试点（通常 >= 3 个）

### 边界覆盖
- [ ] 边界值覆盖（最大/最小/临界）
- [ ] 溢出、下溢场景

### 组合覆盖
- [ ] 配置项之间的组合测试
- [ ] 并发访问、时序冲突

### 联动覆盖
- [ ] 章节内 SubFeature 的依赖关系
- [ ] 跨章节功能依赖

### 异常覆盖
- [ ] 错误配置、非法输入
- [ ] 故障注入场景

### 质量检查
- [ ] stimulus 描述可执行性
- [ ] checking 方式明确性
- [ ] 无重复测试点

## 7. 结果审查要点

**审查自检结果**：
- 检查 self_review 字段，确认自检通过
- 关注 missing_functions 和 missing_items
- 验证 quality_check 的合理性

**审查 Feature 划分**：
- 使用 `nbl-testplan tree` 查看整体结构
- 检查 Feature 是否覆盖所有验证需求
- 确认优先级分配合理

**审查 Testpoint 质量**：
- 检查各类别测试点的分布比例
- 正常场景应占 50-60%，边界组合占 30-40%，联动异常占 10-20%
- 确认 stimulus 和 checking 可执行
- 验证覆盖率定义合理

## 8. 文件管理

**核心文件**：
- `.tp_cache/sections.json`：阶段1输出，粗框架划分
- `.tp_cache/feature_plan.json`：阶段2输出，Feature 初步规划（动态更新）
- `.tp_cache/testplan_raw.md`：阶段3主工作文件，Markdown 为唯一数据源
- `.tp_cache/features.json`：阶段3b输出，统一三级结构数据
- `testplan.md`：阶段4输出，最终测试计划文档（CWD）

**版本管理建议**：
- 所有文件建议 git 版本管理
- 每个阶段完成后提交一个 commit
- 便于追溯处理历史和问题定位

## 9. Markdown 编辑建议

- feature_name 和 sub_feature_name 中不要包含 `.`
- 表格字段中换行统一使用 `<br>`，禁止在表格单元格内直接换行或使用 `\n`，确保 Markdown 表格解析正确
- 同一 Feature 下的所有 SubFeature 连续出现，不要穿插其他 Feature
- 追加到已有 SubFeature 时，只需要在对应 `### heading` 下添加新表格行
- 不要修改 `.tp_cache/testplan_raw.md` 中已有的其他章节内容
