# Testplan-CFG 修复设计文档

**日期**: 2026-04-20
**目标**: 修复 testplan-cfg 插件的5个问题

---

## 问题清单

| # | 问题 | 修改文件 |
|---|------|---------|
| 1 | 生成的测试点包含模板示例数据残留 | xlsx_writer.py |
| 2 | 单元格边框格式不正确 | xlsx_writer.py |
| 3 | J列检查方式缺失 | cfg_writer.py |
| 4 | W列反标路径缺失 | cfg_writer.py |
| 5 | D-E-F层级结构不正确 | cfg_writer.py |

---

## 设计详情

### 1. 模板数据残留

**文件**: `testplan-cfg/scripts/xlsx_writer.py`

**修改**: 在写入数据前清空模板数据行，从第6行开始清空（包括第6行的B列和D列）。

```python
def _clear_template_data(ws):
    """Clear template example data starting from row 6."""
    for row in range(6, ws.max_row + 1):
        for col in range(1, 24):  # A-W columns
            ws.cell(row=row, column=col).value = None
```

**调用位置**: `write_ch1_xlsx` 函数中，加载模板后立即调用。

---

### 2. 单元格边框格式

**文件**: `testplan-cfg/scripts/xlsx_writer.py`

**修改**: 写入所有数据后，后处理步骤应用矩形边框。

```python
def _apply_border_rectangle(ws):
    """Apply borders to rectangular region A-W for all data rows."""
    first_row = None
    last_row = None

    # Find first and last rows with content
    for row in range(6, ws.max_row + 1):
        has_content = any(ws.cell(row=row, column=col).value for col in range(1, 24))
        if has_content:
            if first_row is None:
                first_row = row
            last_row = row

    if first_row is None:
        return

    # Apply borders to rectangle A-W
    for row in range(first_row, last_row + 1):
        for col in range(1, 24):  # A-W
            ws.cell(row=row, column=col).border = STD_BORDER
```

**调用位置**: `write_ch1_xlsx` 函数末尾，保存前调用。

---

### 3. J列检查方式

**文件**: `testplan-cfg/scripts/cfg_writer.py`

**修改**: Ch2配置特性默认J列填充"随机用例"。

**J列可选值**:
- 直接用例
- 随机用例
- 断言检查

**默认**: 随机用例

```python
# 在 cross_ref_cfg 或 build_ch2_json 中设置
"checking": "随机用例",
```

---

### 4. W列反标路径

**文件**: `testplan-cfg/scripts/cfg_writer.py`

**修改**: 根据寄存器名和域段名自动生成反标路径。

**路径格式**:
```
Group:$unit::{module_name}_fcov::{reg_name}_cg.{field_name}_cp
```

**生成逻辑**:
- `module_name`: 寄存器名第一个下划线前缀（如 `upa_pri_sel_conf` → `upa`）
- `reg_name`: 完整寄存器名
- `field_name`: 域段名

**示例**:
- 寄存器: `upa_pri_sel_conf`
- 域段: `pri_sel`
- 路径: `Group:$unit::upa_fcov::upa_pri_sel_conf_cg.pri_sel_cp`

**多域段处理**: 每个域段单独一行，各自有独立的路径。

---

### 5. D-E-F层级结构

**文件**: `testplan-cfg/scripts/cfg_writer.py`

**修改**: 重构Ch2数据结构为三级层次。

| 列 | 内容 | outline_level | 说明 |
|---|------|---------------|------|
| D | 寄存器名称 | 0 | 如 `upa_pri_sel_conf` |
| E | 域段名称 | 1 | 如 `pri_disen`, `pri_sel` |
| F | bit范围含义 | 2 | 如 `bit[4] pri/TOS选择; bit[3:0]为port vlan选择` |

**数据结构**:
```python
{
    "register_name": "upa_pri_sel_conf",
    "subfeatures_l1": [
        {
            "subfeature_l1": "pri_disen",  # E列：域段名
            "subfeatures_l2": [{
                "subfeature_l2_overview": "bit[0] 使能控制",  # F列：bit含义
                "remarks": "...",
                "stimulus": "【配置】...",
                "checking": "随机用例",
                "path": "Group:$unit::upa_fcov::upa_pri_sel_conf_cg.pri_disen_cp"
            }]
        },
        {
            "subfeature_l1": "pri_sel",  # E列
            "subfeatures_l2": [{
                "subfeature_l2_overview": "bit[4] pri/TOS选择; bit[3:0]为port vlan选择",
                "remarks": "...",
                "stimulus": "【配置】...",
                "checking": "随机用例",
                "path": "Group:$unit::upa_fcov::upa_pri_sel_conf_cg.pri_sel_cp"
            }]
        }
    ]
}
```

**关键变更**:
- 每个域段一行（而非每个寄存器一行）
- E列填域段名（从寄存器JSON的fields中提取）
- F列填bit范围描述（从域段的range和description组合）

---

## 文件修改汇总

| 文件 | 修改内容 |
|------|---------|
| `testplan-cfg/scripts/xlsx_writer.py` | 新增 `_clear_template_data`、`_apply_border_rectangle` 函数 |
| `testplan-cfg/scripts/cfg_writer.py` | 修改 `build_ch2_json` 数据结构，新增 `_generate_fcov_path` 函数 |

---

## 验证方案

1. 运行 testplan-cfg 生成测试点
2. 检查输出xlsx：
   - 无模板示例数据残留
   - 边框覆盖完整矩形区域
   - J列默认为"随机用例"
   - W列路径格式正确
   - D-E-F层级结构正确
