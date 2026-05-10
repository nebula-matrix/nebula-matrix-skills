# Test Plan Generator - Functional Features (Chapter 1)

## System Role

资深数字芯片验证工程师，精通 SystemVerilog/UVM，负责根据模块功能规格书以及寄存器配置文档生成结构化测试点。

## Task Description

从功能规格书（.docx/.md）和寄存器手册（.xlsx）生成 Chapter 1（功能特性）测试点，输出结构化 xlsx 文件。

# 功能需求

使用superpower工作流，帮我创建一个nbl-tp-gen的插件以及nbl-tp-func-gen的skills，首先发动头脑风暴，完善需求，现在的初步想法如下：
- 聚焦于数字芯片逻辑验证领域，基于功能规格书（.docx）和寄存器配置手册(.xlsx)生成测试点文档（.xlsx）
- 实现将一个较长内容的docx功能规格文档（最多可能100页）和寄存器配置手册转换为功能测试点文档，其中功能规格文档包括但不限于功能概述、模块特性、参数列表、性能描述、数据结构描述、功能详述、流控描述、初始化、错误处理、DFX、应用限制组成（有些部分会省略）。
- 测试点文档聚焦于对功能规格文档中，以模块特性为骨架，以功能规格文档的其他内容以及寄存器配置手册为血肉进行交叉引用提取，逐一分解分析，从一个模块特性中分解为子特性，子特性根据场景有可能分为多个子特性，另外需要对每个子特性加上简述、仿真条件/策略（激励如何产生、配置如何配置）、预期结果、sv中的覆盖率covergroup如何建仓这几个维度。
- 生成的测试点文档模板路径：/home/alvin.xu/test_center/test_testplan_skills/assets/testplan_template.xlsx
- 提供案例：
  - UPA：
    - 功能规格文档路径为：/home/alvin.xu/test_center/test_testplan_skills/assets/upa/Leonis_PA_Functional_Specification.docx
    - 寄存器配置手册路径为：/home/alvin.xu/test_center/test_testplan_skills/assets/upa/Leonis_datapath_upa.xlsx
    - 可供参考的测试点文档路径为：/home/alvin.xu/test_center/test_testplan_skills/assets/upa/leonis_upa_tp.xlsx
  - DPED：
    - 功能规格文档路径为：/home/alvin.xu/test_center/test_testplan_skills/assets/dped/Leonis_PED_Functional_Specification.docx
    - 寄存器配置手册路径为：/home/alvin.xu/test_center/test_testplan_skills/assets/dped/Leonis_datapath_dped.xlsx
    - 可供参考的测试点文档路径为：/home/alvin.xu/test_center/test_testplan_skills/assets/dped/dped_tp.xml
- 功能规格书以及寄存器手册中没有明确体现的内容，不可以擅自推理填写；功能规格书以及寄存器手册中没有明确体现的内容，但测试点文档可能涉及的，可能就是功能规格书以及寄存器手册可能存在的问题点，需要在对话中进行询问确定，不可以擅自添加不存在的信息，并在测试点文档保存路径新建一个fs_reg_slv_review.md进行记录。每个潜在的问题点需要有一项：确定信息，用于让用户确定是否为问题，或补充说明，支持后续用户将此fs_reg_slv_review.md刷新确定信息后，输入给此skills，进行二次刷新测试点，将之前不确定点进行刷新；
- 需要询问用户最终结果的保存路径；
- 需要具有移植性，使用相对路径，确保可以在其他机器上运行，例如可以通过设置工作目录 `$TP_WORKDIR`，相对工作目录进行
- 生成的测试点文档要求：
  - 可读性要强，与模板保持一样的边框格式、单元格内容按需换行；
  - 潜在的测试点，但在功能规格书以及寄存器手册没有提及的，可以使用特殊格式进行衬托
  - 输出的测试点文档格式，参考；/home/alvin.xu/test_center/test_testplan_skills/assets/testplan_template.xlsx，要求：
    - 表头存在的内容不可以更改；
    - 层级分解策略：测试点必须严格遵循 D→E→F→G列的层级从属关系，每一层占独立行
      - A 列：不需要填写东西，确保第三行和第四行的内容，分别为plan和weight
      - B 列：spec改为{模块名}_spec即可，chapter单元格目前只写为chapter 1 功能特性即可，其他不需要修改；（模块名通过输入文件名确定）
      - C 列：不动
      - D 列 - Feature（顶层特性）：从功能规格书模块特性章节提取的顶层特性名称，例如：报文编辑范围、报文丢弃、指针拆链
      - E 列 - Subfeature L1（一级子特性）：D 层特性的子分类，按功能维度分解：如替换动作、增删动作、TTL动作；按配置模式分解：如添加tnl、添加mirror；
      - F 列 - Subfeature L2（二级子特性）：E 层子特性的具体验证点，概述性描述
      - G 列 - Subfeature L3（三级子特性，最小粒度）：详细规格点描述（可含配置枚举、参数范围等）
        - 可选项，如果F列已经足够表达功能，则不需要填写G列，此时F列视为最小粒度
      - F/G分解维度：
        - 功能维度：功能特性包含的基础功能
        - 场景维度：正常/边界/异常
        - 配置维度：mode 字段枚举值，使能/禁止组合
        - 交互维度：多动作组合、多配置组合、跨模块场景
      - H 列：对于此测试点的描述，体现测试点来源，还需要从功能规格书或寄存器配置手册体现额外的解释，例如此功能的作用是什么，触发条件是什么，与那些寄存器配置有关等等；
      - I 列：仿真条件，包括配置和激励两个维度，其中配置主要与寄存器配置手册挂钩；激励则说明需要生成什么样的报文数据即可，例如模块如果涉及入口info和- data的输入，则入口info有哪些域段需要填写哪种值，data需要发送多长、什么的数据包。
      - J 列：检查的方式，包括但不限于by_checker随机用例覆盖、直接用例覆盖、断言用例覆盖
      - K 列：功能覆盖率仓位抽象化，枚举需要创建的仓位，是直接用例/断言直接覆盖，还是通过功能覆盖仓，覆盖到此行的功能点，一般需要考虑配置、处理场景、激励，注意cross交叉收集的场景，例如某个开关开启的情况下，收集某值的某某范围；如果可以从功能规格书或寄存器配置手册得到收集的值/范围，则具体到值/范围
      - L 列：不需要填写
      - M 列：根据用户输入的验证层次，选择UT（单元测试）/BT（模块测试）/IT（集成测试）/ST（soc测试）/EMU（fpga测试）
      - N-P 列：不需要填写
      - U列在第4行，与weight对应的单元格，固定填写5即可
      - V列在第4行，与weight对应的单元格，固定填写95即可
      - W列：参考模板提供的格式，按照断言、功能或直接用例，创建覆盖率仓路径，如果涉及多个反标路径，则需要通过英文输入法的逗号`,`进行连接

## 测试点输出xlsx格式要求

- 除了表头，其他测试点单元格格式统一为垂直居中、左对齐；
- 除了表头，其他单元格字体格式统一为：微软雅黑、字号为10、字体颜色为黑色、I列中`【配置】`和`【激励】`字体颜色为红色；
- 单元格中的内容注意换行，例如遇到分号，句号，冒号，括号说明需要另起一行；
- 单元格添加边框的逻辑可以归纳于，获得包含内容单元格所在的行，将A-W列，以及第一行到最后一行有内容的行范围，全部添加边框。
- U-V列不需要默认隐藏
- B列中，每个部分的chapter出现一次，意在指明功能特性和配置特性的开始行
- 潜在的测试点，但在功能规格书以及寄存器手册没有提及的，可以使用特殊格式进行衬托，例如标有` ⚠ [推断]`提示，字体颜色为红色；
- K列，如果可以从功能规格书或寄存器配置手册得到收集的值/范围，则具体到值/范围


## D-E-F-G 层级结构

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


## J列和W列关系 

W列根据J列的检查类型确定反标路径，反标路径语法和WJ关系如下
| J (checking) | W (path) |
|--------------|----------|
| `by_checker` | `Group:$unit::{模块名}_fcov::cg_{D列信息}.cp_{E列信息}` |
| `by_direct_tc` | `Group:$unit::{模块名}_direct_fcov::direct_{D列信息}_{E列信息}` |
| `by_assertion` | `Group:$unit::{模块名}_assert::assert_{D列信息}_{E列信息}` |

## 寄存器配置文件转换为JSON格式参考结构

```json
{
  "module_name": "UPA",
  "spec_name": "文档名",
  "chapter": "chapter 1 功能特性",
  "features": [
    {
      "feature": "顶层特性名（D列）",
      "feature_id": "PA.XXX",
      "subfeatures_l1": [
        {
          "subfeature_l1": "一级子特性（E列）",
          "subfeatures_l2": [
            {
              "subfeature_l2": "二级概述（F列）",
              "subfeatures_l3": [
                {
                  "subfeature_l3": "二级详述（E列）",
                  "remarks": "来源: PA.XXX",
                  "stimulus": "【配置】...\\n【激励】...",
                  "checking": "by_checker/by_direct_tc/by_assertion",
                  "coverage": "covergroup抽象",
                  "priority": "HIGH/MID/LOW",
                  "activity": "BT",
                  "path": "覆盖率路径"
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

# 其他需求

- 涉及输出的操作都需要检查操作，确定输出的结果符合预期，例如检查测试点文档的格式

# 强制要求

- 按照/home/alvin.xu/nebula-matrix/nebula-matrix-skills/CLAUDE.md和/home/alvin.xu/nebula-matrix/nebula-matrix-skills/doc/PLUGIN_CONFIGURATION_GUIDE.md文档的要求，在/home/alvin.xu/nebula-matrix/nebula-matrix-skills/home/alvin.xu/nebula-matrix/nebula-matrix-skills中创建合法的插件和skills文件夹和文件
- 将生成的插件和skills在/home/alvin.xu/nebula-matrix/nebula-matrix-skills/README.md中给出介绍
- 涉及docx文件的操作，强制要求调用`/nbl-docx-to-markdown`的skills将其处理为markdown后，在此基础上进行处理
- 按照任务的复杂程度，将其切分为若干个subagent或通过agent teams进行，避免上下文受限，例如将功能实现进行头脑风暴的任务封为一个subagent，后续执行writing-plans将其输出作为输入，重启一个新的agent进行工作，且在工作过程中，将每步分为若干个subagent头尾相连进行串行运行
- 最后成品也推荐subagent串行运行

# 运行要求

- 中间产物、git注释都使用中文
- 中间产物如果用户不指定的话，默认放在home目录
- python通过uv管理
- 插件或skills中产生的中间临时文件，例如tests/superpowers目录等加入到.gitignore