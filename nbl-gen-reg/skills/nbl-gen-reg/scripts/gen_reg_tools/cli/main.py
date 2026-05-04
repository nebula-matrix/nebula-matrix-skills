import os
import typer
from typing import Optional

app = typer.Typer(
    help="gen_reg_tools 统一命令行入口",
    rich_markup_mode="rich",
)


def _validate_path(path: str, expected_exts: list[str], label: str) -> None:
    """校验文件路径：存在性 + 扩展名。不符合则打印警告并退出。"""
    if not os.path.exists(path):
        typer.echo(f"Error: {label} 不存在: {path}")
        raise typer.Exit(1)
    ext = os.path.splitext(path)[1].lower()
    if ext not in expected_exts:
        typer.echo(
            f"Error: {label} 扩展名应为 {', '.join(expected_exts)}，但得到: {ext} ({path})"
        )
        raise typer.Exit(1)


@app.command()
def extract(
    excel: Optional[str] = typer.Option(
        None, "--excel", "-e",
        help="单个 Excel 文件路径（支持 .xlsx 和 .xls）"
    ),
    excel_dir: Optional[str] = typer.Option(
        None, "--excel-dir", "-d",
        help="包含多个 Excel 文件的目录，自动遍历所有子目录中的 .xlsx 文件"
    ),
    cif: Optional[str] = typer.Option(
        None, "--cif", "-c",
        help="CIF 地址映射文件路径（Excel 格式），用于提取基地址信息。若未指定，则 --cif-check 自动关闭"
    ),
    output: str = typer.Option(
        "reg_data.json", "--output", "-o",
        help="提取结果的 JSON 输出文件路径"
    ),
    prefix: Optional[str] = typer.Option(
        None, "--prefix", "-p",
        help="Excel 文件名前缀，用于解析 it_name 和 bt_name。默认值为 ASIC_PDT_V3R1"
    ),
    check_flag: bool = typer.Option(
        False, "--check",
        help="提取完成后自动执行常规检查（offset_addr 合法性、重复性、reg_width 一致性等）"
    ),
    cif_check_flag: bool = typer.Option(
        False, "--cif-check",
        help="提取完成后自动执行 CIF 地址范围检查，验证所有寄存器地址是否在 CIF 定义的模块地址范围内"
    ),
):
    """从 Excel 提取寄存器数据并导出为 JSON

    支持两种输入模式，必须且只能选择其中一种：
    - 单个文件模式（--excel）：处理一个 Excel 文件，提取所有有效 sheet
    - 目录模式（--excel-dir）：遍历目录下所有 .xlsx 文件，批量提取

    文件名格式要求：{prefix}_{it_name}_{bt_name}.xlsx
    例：ASIC_PDT_V3R1_lb_emp_sse.xlsx  →  it_name="lb", bt_name="emp_sse"
    若文件名以 prefix_ 开头但缺少 it 或 bt 部分，将报错提示格式错误。

    提取的 JSON 结构为层级树：Top → Block → Register → Field

    [bold]用法示例：[/bold]

    1. 提取单个文件（不带 CIF）：
       $ gen-reg extract --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx -o data.json

    2. 提取单个文件（带 CIF）：
       $ gen-reg extract --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --cif CIF.xlsx -o data.json

    3. 提取整个目录（含自定义前缀）：
       $ gen-reg extract --excel-dir ./2_Reg/Src/ --cif ./2_Reg/ --prefix Leonis -o all.json

    4. 提取并立即执行检查：
       $ gen-reg extract --excel-dir ./2_Reg/Src/ --cif CIF.xlsx --check --cif-check -o data.json
    """
    from gen_reg_tools.extractor.pipeline import Extractor
    from gen_reg_tools.checker.normal_check import NormalChecker
    from gen_reg_tools.checker.cif_check import CifChecker

    if excel:
        _validate_path(excel, [".xlsx", ".xls"], "--excel")
    if excel_dir:
        if not os.path.isdir(excel_dir):
            typer.echo(f"Error: --excel-dir 不是有效目录: {excel_dir}")
            raise typer.Exit(1)
    if cif:
        _validate_path(cif, [".xlsx", ".xls"], "--cif")

    cif_path = cif if cif else "/dev/null"

    if excel:
        data = Extractor.extract_file(excel, cif_path, prefix=prefix)
    elif excel_dir:
        data = Extractor.extract_dir(excel_dir, cif_path, prefix=prefix)
    else:
        typer.echo("Error: 请指定 --excel 或 --excel-dir")
        raise typer.Exit(1)

    if check_flag:
        result = NormalChecker.check(data)
        if not result.passed:
            for error in result.errors:
                typer.echo(error)
            raise typer.Exit(1)

    if cif and cif_check_flag:
        result = CifChecker.check(data, cif)
        if not result.passed:
            for error in result.errors:
                typer.echo(error)
            raise typer.Exit(1)

    data.to_json(output)
    typer.echo(f"提取完成: {output}")


@app.command()
def check(
    json_path: str = typer.Option(
        ..., "--json", "-j",
        help="由 gen-reg extract 生成的 JSON 文件路径"
    ),
):
    """对提取结果进行常规检查

    检查项包括：
    - offset_addr 是否为 4 的倍数
    - offset_addr 是否在同 Block 内重复
    - reg_name 是否在同 Block 内重复
    - reg_width 是否等于所有 field_bits 之和
    - tbl 类型寄存器之后是否出现非 tbl 类型寄存器
    - tbl width 是否小于 1024
    - 以及更多一致性校验...

    所有检查项均通过则输出 "检查通过"，否则列出所有错误并退出码为 1。

    [bold]用法示例：[/bold]

    $ gen-reg check --json reg_data.json
    """
    _validate_path(json_path, [".json"], "--json")

    from gen_reg_tools.core.data_model import RegData
    from gen_reg_tools.checker.normal_check import NormalChecker

    data = RegData.from_json(json_path)
    result = NormalChecker.check(data)

    if result.passed:
        typer.echo("检查通过")
    else:
        for error in result.errors:
            typer.echo(error)
        raise typer.Exit(1)


@app.command()
def cif_check(
    json_path: str = typer.Option(
        ..., "--json", "-j",
        help="由 gen-reg extract 生成的 JSON 文件路径"
    ),
    cif: str = typer.Option(
        ..., "--cif", "-c",
        help="CIF 地址映射 Excel 文件路径"
    ),
):
    """检查寄存器地址是否在 CIF 定义的地址范围内

    读取 CIF 地址映射表中各模块的基地址和大小，验证 JSON 中每个 Block
    的所有寄存器 offset_addr 是否落在该模块的地址空间内。

    [bold]用法示例：[/bold]

    $ gen-reg cif-check --json reg_data.json --cif ASIC_PDT_V3R1_CIF.xlsx
    """
    _validate_path(json_path, [".json"], "--json")
    _validate_path(cif, [".xlsx", ".xls"], "--cif")

    from gen_reg_tools.core.data_model import RegData
    from gen_reg_tools.checker.cif_check import CifChecker

    data = RegData.from_json(json_path)
    result = CifChecker.check(data, cif)

    if result.passed:
        typer.echo("CIF 检查通过")
    else:
        for error in result.errors:
            typer.echo(error)
        raise typer.Exit(1)


@app.command()
def regslv(
    excel: Optional[str] = typer.Option(
        None, "--excel", "-e",
        help="寄存器 Excel 文件路径（与 --sheet 配合）"
    ),
    json_path: Optional[str] = typer.Option(
        None, "--json", "-j",
        help="由 gen-reg extract 生成的 JSON 文件路径（与 --bt 配合）"
    ),
    sheet: Optional[str] = typer.Option(
        None, "--sheet", "-s",
        help="Excel 中目标 Sheet 名称（Excel 模式专用）"
    ),
    bt: Optional[str] = typer.Option(
        None, "--bt", "-b",
        help="目标 Block 名称（JSON 模式专用）"
    ),
    output: str = typer.Option(
        "./out", "--output", "-o",
        help="生成的 Verilog 文件输出目录"
    ),
    config: Optional[str] = typer.Option(
        None, "--config",
        help="生成配置项，格式: key=value,key2=value2（暂未实现）"
    ),
    check_flag: bool = typer.Option(
        False, "--check",
        help="Excel 模式下：提取后自动执行常规检查"
    ),
    cif_check_flag: bool = typer.Option(
        False, "--cif-check",
        help="Excel 模式下：提取后自动执行 CIF 地址范围检查（需同时指定 --cif）"
    ),
    cif: Optional[str] = typer.Option(
        None, "--cif", "-c",
        help="CIF 地址映射文件路径（Excel 模式下配合 --cif-check 使用）"
    ),
):
    """生成 reg_slv Verilog 代码

    reg_slv 是寄存器从机的 Verilog 模块，支持 APB/AXI-Lite 等总线接口，
    将软件访问转化为对内部寄存器的读写。

    支持两种输入模式，必须且只能选择其中一种：
    - Excel 模式（--excel + --sheet）：直接从单个 Excel sheet 生成
    - JSON 模式（--json + --bt）：从提取后的 JSON 数据中筛选指定 Block

    [bold]用法示例：[/bold]

    1. 从 Excel 直接生成：
       $ gen-reg regslv --excel ASIC_PDT_V3R1_intf_eth.xlsx --sheet eth_a2mti_mclk -o ./out/

    2. 从 Excel 生成并检查：
       $ gen-reg regslv --excel ASIC_PDT_V3R1_ppe_pa.xlsx --sheet pa --check -o ./out/

    3. 从 JSON 生成：
       $ gen-reg regslv --json reg_data.json --bt eth_a2mti_mclk -o ./out/
    """
    if excel:
        _validate_path(excel, [".xlsx", ".xls"], "--excel")
    if json_path:
        _validate_path(json_path, [".json"], "--json")
    if cif:
        _validate_path(cif, [".xlsx", ".xls"], "--cif")

    from gen_reg_tools.regslv import RegSlvGenerator

    if excel and sheet:
        # Excel 模式：先提取并可选检查，再生成
        if check_flag or (cif and cif_check_flag):
            from gen_reg_tools.extractor.pipeline import Extractor
            from gen_reg_tools.checker.normal_check import NormalChecker
            from gen_reg_tools.checker.cif_check import CifChecker

            data = Extractor.extract_file(excel, cif if cif else "/dev/null")

            if check_flag:
                result = NormalChecker.check(data)
                if not result.passed:
                    for error in result.errors:
                        typer.echo(error)
                    raise typer.Exit(1)
                typer.echo("检查通过")

            if cif and cif_check_flag:
                result = CifChecker.check(data, cif)
                if not result.passed:
                    for error in result.errors:
                        typer.echo(error)
                    raise typer.Exit(1)
                typer.echo("CIF 检查通过")

        RegSlvGenerator.generate(excel_path=excel, sheet=sheet, output_dir=output)
        typer.echo(f"reg_slv 生成完成（Excel）: {output}")
    elif json_path and bt:
        RegSlvGenerator.generate(json_path=json_path, bt=bt, output_dir=output)
        typer.echo(f"reg_slv 生成完成（JSON）: {output}")
    else:
        typer.echo("Error: 请指定 --excel + --sheet 或 --json + --bt")
        raise typer.Exit(1)


@app.command()
def ral(
    excel: Optional[str] = typer.Option(
        None, "--excel", "-e",
        help="寄存器 Excel 文件路径（与 --bn 配合）"
    ),
    excel_dir: Optional[str] = typer.Option(
        None, "--excel-dir", "-d",
        help="包含 Excel 文件的目录路径（与 --cfg 配合）"
    ),
    prefix: Optional[str] = typer.Option(
        None, "--prefix", "-p",
        help="Excel 文件名前缀（--excel-dir 模式下可用，如: ASIC_PDT_V2R1）"
    ),
    json_path: Optional[str] = typer.Option(
        None, "--json", "-j",
        help="由 gen-reg extract 生成的 JSON 文件路径（与 --cfg 配合）"
    ),
    bn: Optional[str] = typer.Option(
        None, "--bn", "-b",
        help="目标 Block 名称（Excel 单文件模式专用）"
    ),
    cfg_path: Optional[str] = typer.Option(
        None, "--cfg", "-c",
        help="RAL 配置 Python 脚本路径（系统级模式专用），定义块间层次关系等"
    ),
    output: str = typer.Option(
        "./ral_out", "--output", "-o",
        help="生成的 UVM RAL 代码输出目录"
    ),
    check_flag: bool = typer.Option(
        False, "--check",
        help="Excel 模式下：提取后自动执行常规检查"
    ),
    cif_check_flag: bool = typer.Option(
        False, "--cif-check",
        help="Excel 模式下：提取后自动执行 CIF 地址范围检查（需同时指定 --cif）"
    ),
    cif: Optional[str] = typer.Option(
        None, "--cif",
        help="CIF 地址映射文件路径（Excel 模式下配合 --cif-check 使用）"
    ),
):
    """生成 UVM RAL（Register Abstraction Layer）模型

    RAL 模型是 UVM 验证环境的核心组件，提供面向对象的寄存器访问接口，
    支持前门（通过总线）和后门（通过 HDL 路径）两种访问方式。

    支持三种输入模式，必须且只能选择其中一种：
    - Excel 单文件模式（--excel + --bn）：直接从单个 Excel 生成单个 Block 的 RAL
    - Excel 目录模式（--excel-dir + --cfg）：从目录批量提取 + cfg.py 生成系统级 RAL
    - JSON 模式（--json + --cfg）：从 JSON + cfg.py 生成完整系统级 RAL

    [bold]用法示例：[/bold]

    1. 从 Excel 生成单个 Block 的 RAL：
       $ gen-reg ral --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec -o ./ral_out/

    2. 从 Excel 生成并检查：
       $ gen-reg ral --excel ASIC_PDT_V3R1_ppe_pa.xlsx --bn pa --check -o ./ral_out/

    3. 从 Excel 目录 + cfg.py 生成系统级 RAL：
       $ gen-reg ral --excel-dir ./2_Reg/Src/ --cfg ral_cfg.py -o ./ral_out/

    4. 从 JSON + cfg.py 生成系统级 RAL：
       $ gen-reg ral --json reg_data.json --cfg ral_cfg.py -o ./ral_out/
    """
    if excel:
        _validate_path(excel, [".xlsx", ".xls"], "--excel")
    if excel_dir:
        if not os.path.isdir(excel_dir):
            typer.echo(f"Error: --excel-dir 不是有效目录: {excel_dir}")
            raise typer.Exit(1)
    if json_path:
        _validate_path(json_path, [".json"], "--json")
    if cfg_path:
        _validate_path(cfg_path, [".py"], "--cfg")
    if cif:
        _validate_path(cif, [".xlsx", ".xls"], "--cif")

    from gen_reg_tools.ral import RalGenerator

    if excel and bn:
        # Excel 单文件模式：先提取并可选检查，再生成
        if check_flag or (cif and cif_check_flag):
            from gen_reg_tools.extractor.pipeline import Extractor
            from gen_reg_tools.checker.normal_check import NormalChecker
            from gen_reg_tools.checker.cif_check import CifChecker

            data = Extractor.extract_file(excel, cif if cif else "/dev/null")

            if check_flag:
                result = NormalChecker.check(data)
                if not result.passed:
                    for error in result.errors:
                        typer.echo(error)
                    raise typer.Exit(1)
                typer.echo("检查通过")

            if cif and cif_check_flag:
                result = CifChecker.check(data, cif)
                if not result.passed:
                    for error in result.errors:
                        typer.echo(error)
                    raise typer.Exit(1)
                typer.echo("CIF 检查通过")

        RalGenerator.generate(excel_path=excel, bn=bn, output_dir=output)
        typer.echo(f"RAL 生成完成（Excel）: {output}")
    elif excel_dir and cfg_path:
        # Excel 目录 + cfg.py 模式：直接提取目录并生成系统级 RAL
        RalGenerator.generate(excel_dir=excel_dir, cfg_path=cfg_path, prefix=prefix, output_dir=output)
        typer.echo(f"RAL 生成完成（Excel-dir+cfg）: {output}")
    elif json_path and cfg_path:
        RalGenerator.generate(json_path=json_path, cfg_path=cfg_path, output_dir=output)
        typer.echo(f"RAL 生成完成（JSON+cfg）: {output}")
    else:
        typer.echo("Error: 请指定 --excel + --bn 或 --excel-dir + --cfg 或 --json + --cfg")
        raise typer.Exit(1)


@app.command()
def cfg(
    excel: Optional[str] = typer.Option(
        None, "--excel", "-e",
        help="寄存器 Excel 文件路径（与 --bn 配合）"
    ),
    json_path: Optional[str] = typer.Option(
        None, "--json", "-j",
        help="由 gen-reg extract 生成的 JSON 文件路径（与 --bt 或 --cfg 配合）"
    ),
    bn: Optional[str] = typer.Option(
        None, "--bn",
        help="目标 Block 名称（Excel 模式专用）"
    ),
    bt: Optional[str] = typer.Option(
        None, "--bt", "-b",
        help="目标 Block 名称（JSON 单 bt 模式专用）"
    ),
    cfg_path: Optional[str] = typer.Option(
        None, "--cfg", "-c",
        help="配置 Python 脚本路径（JSON 系统级模式专用），定义 inst_map"
    ),
    output: str = typer.Option(
        "./cfg_out", "--output", "-o",
        help="生成的配置表文件输出目录"
    ),
    check_flag: bool = typer.Option(
        False, "--check",
        help="Excel 模式下：提取后自动执行常规检查"
    ),
    cif_check_flag: bool = typer.Option(
        False, "--cif-check",
        help="Excel 模式下：提取后自动执行 CIF 地址范围检查（需同时指定 --cif）"
    ),
    cif: Optional[str] = typer.Option(
        None, "--cif",
        help="CIF 地址映射文件路径（Excel 模式下配合 --cif-check 使用）"
    ),
):
    """生成寄存器配置表（SystemVerilog）

    输出三个 SystemVerilog 文件：
    - 单 BT 模式（--excel + --bn / --json + --bt）：
      {bt}_reg_tbl_cfg_decl.sv / {bt}_reg_tbl_cfg.sv / {bt}_init_cfg_by_ral.sv
    - 多 BT 系统级模式（--json + --cfg）：
      {top_name}_reg_tbl_cfg_decl.sv（汇总所有 BT 的结构体声明）
      {top_name}_reg_tbl_cfg.sv（按 BT 顺序拼接所有类定义）
      {top_name}_init_cfg_by_ral.sv（按 BT 顺序拼接所有 task）

    支持三种输入模式，必须且只能选择其中一种：
    - Excel 模式（--excel + --bn）：直接从单个 Excel 生成单个 Block 的配置表
    - JSON 单 bt 模式（--json + --bt）：从 JSON 生成指定 Block 的配置表
    - JSON 系统级模式（--json + --cfg）：从 JSON + cfg.py 为所有 Block 生成配置表

    [bold]用法示例：[/bold]

    1. 从 Excel 直接生成：
       $ gen-reg cfg --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx --bn dmacsec -o ./cfg_out/

    2. 从 Excel 生成并检查：
       $ gen-reg cfg --excel ASIC_PDT_V3R1_ppe_pa.xlsx --bn pa --check -o ./cfg_out/

    3. 从 JSON 单 bt 生成：
       $ gen-reg cfg --json reg_data.json --bt dmacsec -o ./cfg_out/

    4. 从 JSON + cfg.py 系统级生成：
       $ gen-reg cfg --json all.json --cfg cfg.py -o ./cfg_out/
    """
    if excel:
        _validate_path(excel, [".xlsx", ".xls"], "--excel")
    if json_path:
        _validate_path(json_path, [".json"], "--json")
    if cfg_path:
        _validate_path(cfg_path, [".py"], "--cfg")
    if cif:
        _validate_path(cif, [".xlsx", ".xls"], "--cif")

    from gen_reg_tools.cfg import CfgGenerator

    if excel and bn:
        if check_flag or (cif and cif_check_flag):
            from gen_reg_tools.extractor.pipeline import Extractor
            from gen_reg_tools.checker.normal_check import NormalChecker
            from gen_reg_tools.checker.cif_check import CifChecker

            data = Extractor.extract_file(excel, cif if cif else "/dev/null")

            if check_flag:
                result = NormalChecker.check(data)
                if not result.passed:
                    for error in result.errors:
                        typer.echo(error)
                    raise typer.Exit(1)
                typer.echo("检查通过")

            if cif and cif_check_flag:
                result = CifChecker.check(data, cif)
                if not result.passed:
                    for error in result.errors:
                        typer.echo(error)
                    raise typer.Exit(1)
                typer.echo("CIF 检查通过")

        CfgGenerator.generate(excel_path=excel, bn=bn, output_dir=output)
        typer.echo(f"cfg 生成完成（Excel）: {output}")
    elif json_path and bt:
        CfgGenerator.generate(json_path=json_path, bt=bt, output_dir=output)
        typer.echo(f"cfg 生成完成（JSON+bt）: {output}")
    elif json_path and cfg_path:
        CfgGenerator.generate(json_path=json_path, cfg_path=cfg_path, output_dir=output)
        typer.echo(f"cfg 生成完成（JSON+cfg）: {output}")
    else:
        typer.echo("Error: 请指定 --excel + --bn 或 --json + --bt 或 --json + --cfg")
        raise typer.Exit(1)


@app.command(name="filter")
def filter_cmd(
    get_bt: bool = typer.Option(
        False, "--get-bt",
        help="列出所有 block_type 为 'bt' 的 Block 名称，不执行筛选"
    ),
    json_path: Optional[str] = typer.Option(
        None, "--json", "-j",
        help="由 gen-reg extract 生成的 JSON 文件路径"
    ),
    excel: Optional[str] = typer.Option(
        None, "--excel", "-e",
        help="单个 Excel 文件路径"
    ),
    excel_dir: Optional[str] = typer.Option(
        None, "--excel-dir", "-d",
        help="包含 Excel 文件的目录（--get-bt 模式下可用）"
    ),
    bt: Optional[str] = typer.Option(
        None, "--bt", "-b",
        help="要保留的 BT 名称，多个用逗号分隔（如: dmacsec,sse,padpt）"
    ),
    level: str = typer.Option(
        "register", "--level", "-l",
        help="过滤级别: register（寄存器级别）/ field（字段级别）/ bt（BT 级别）"
    ),
    rw_attr: Optional[str] = typer.Option(
        None, "--rw-attr",
        help="rw_attr 白名单，多个用逗号分隔（如: rw,rww,wo）"
    ),
    reg_type: Optional[str] = typer.Option(
        None, "--reg-type",
        help="reg_type 白名单，多个用逗号分隔（如: tbl,reg）"
    ),
    name_regex: Optional[str] = typer.Option(
        None, "--name-regex",
        help="register name 正则匹配表达式"
    ),
    depth: Optional[str] = typer.Option(
        None, "--depth",
        help="depth 范围表达式（如: 1, >1, >=2, <10, 1-10）"
    ),
    width: Optional[str] = typer.Option(
        None, "--width",
        help="width 范围表达式（如: 32, >=16, 16-64）"
    ),
    field_regex: Optional[str] = typer.Option(
        None, "--field-regex",
        help="field name 正则匹配表达式"
    ),
    default_value: Optional[str] = typer.Option(
        None, "--default-value",
        help="field default_value 匹配值（支持十六进制 0x... 或十进制）"
    ),
    wr_ctrl: Optional[str] = typer.Option(
        None, "--wr-ctrl",
        help="wr_ctrl 白名单，多个用逗号分隔"
    ),
    output: str = typer.Option(
        "filtered.json", "--output", "-o",
        help="筛选后的 JSON 输出文件路径"
    ),
    prefix: Optional[str] = typer.Option(
        None, "--prefix", "-p",
        help="Excel 文件名前缀（--get-bt + --excel/--excel-dir 模式下可用）"
    ),
):
    """按多维度条件筛选寄存器或字段数据

    支持从 JSON 或 Excel 输入，按寄存器级别（register）或字段级别（field）
    进行多维度综合过滤，所有条件之间为"与"逻辑。

    [bold]用法示例：[/bold]

    1. 从 JSON 按 BT 筛选（向后兼容）：
       $ gen-reg filter --json reg_data.json --bt dmacsec -o dmacsec.json

    2. 从 Excel 直接筛选：
       $ gen-reg filter --excel ASIC_PDT_V3R1_ppe_pa.xlsx --bt pa -o pa.json

    3. 按 rw_attr 筛选 registers：
       $ gen-reg filter --json reg_data.json --bt pa --rw-attr rw -o rw_regs.json

    4. 按 reg_type 筛选：
       $ gen-reg filter --json reg_data.json --reg-type tbl -o tbl_regs.json

    5. 综合多条件（与逻辑）：
       $ gen-reg filter --json reg_data.json --bt pa --rw-attr rw --depth 1 -o result.json

    6. field 级别筛选：
       $ gen-reg filter --json reg_data.json --level field --rw-attr rw --field-regex '.*en' -o fields.json

    7. 从 JSON 列出所有 BT：
       $ gen-reg filter --get-bt --json reg_data.json

    8. 从 Excel 列出所有 BT：
       $ gen-reg filter --get-bt --excel ASIC_PDT_V3R1_ppe_dmacsec.xlsx
    """
    from gen_reg_tools.core.data_model import RegData
    from gen_reg_tools.core.traversal import RegDataTraverser
    from gen_reg_tools.filter.filter import RegFilter

    if get_bt:
        if json_path:
            _validate_path(json_path, [".json"], "--json")
            data = RegData.from_json(json_path)
        elif excel:
            _validate_path(excel, [".xlsx", ".xls"], "--excel")
            from gen_reg_tools.extractor.pipeline import Extractor
            data = Extractor.extract_file(excel, "/dev/null", prefix=prefix)
        elif excel_dir:
            if not os.path.isdir(excel_dir):
                typer.echo(f"Error: --excel-dir 不是有效目录: {excel_dir}")
                raise typer.Exit(1)
            from gen_reg_tools.extractor.pipeline import Extractor
            data = Extractor.extract_dir(excel_dir, "/dev/null", prefix=prefix)
        else:
            typer.echo("Error: --get-bt 模式下需指定 --json、--excel 或 --excel-dir 之一")
            raise typer.Exit(1)

        bt_names = RegDataTraverser.get_all_bt_names(data)
        if not bt_names:
            typer.echo("未找到 block_type 为 'bt' 的 Block")
            return

        typer.echo(f"共找到 {len(bt_names)} 个 BT 模块：")
        for name in bt_names:
            typer.echo(f"  - {name}")
        return

    # 普通筛选模式
    # 1. 确定输入源
    if json_path:
        _validate_path(json_path, [".json"], "--json")
        data = RegData.from_json(json_path)
    elif excel:
        _validate_path(excel, [".xlsx", ".xls"], "--excel")
        from gen_reg_tools.extractor.pipeline import Extractor
        data = Extractor.extract_file(excel, "/dev/null")
    else:
        typer.echo("Error: 请指定 --json 或 --excel")
        raise typer.Exit(1)

    # 2. BT 级别模式：直接按 BT 名称筛选
    if level == "bt":
        if not bt:
            typer.echo("Error: --level bt 模式下需指定 --bt")
            raise typer.Exit(1)
        bt_names = [b.strip() for b in bt.split(",")]
        filtered = RegFilter.by_bt(data, bt_names)
        filtered.to_json(output)
        typer.echo(f"筛选完成: {output}")
        return

    # 3. register/field 级别：检查至少有一个过滤条件
    has_condition = any([
        bt,
        rw_attr,
        reg_type,
        name_regex,
        depth,
        width,
        field_regex,
        default_value,
        wr_ctrl,
    ])
    if not has_condition:
        typer.echo("Error: 请至少指定一个过滤条件（如 --bt, --rw-attr, --reg-type 等）")
        raise typer.Exit(1)

    # 4. 解析参数
    bt_names = [b.strip() for b in bt.split(",")] if bt else None
    rw_attr_list = [a.strip() for a in rw_attr.split(",")] if rw_attr else None
    reg_type_list = [t.strip() for t in reg_type.split(",")] if reg_type else None
    wr_ctrl_list = [w.strip() for w in wr_ctrl.split(",")] if wr_ctrl else None

    dv = None
    if default_value:
        dv = int(default_value, 0)  # 自动解析 0x... 或十进制

    # 5. 执行过滤
    filtered = RegFilter.filter_data(
        data,
        level=level,
        bt_names=bt_names,
        rw_attr=rw_attr_list,
        reg_type=reg_type_list,
        name_regex=name_regex,
        depth_expr=depth,
        width_expr=width,
        field_regex=field_regex,
        default_value=dv,
        wr_ctrl=wr_ctrl_list,
    )

    filtered.to_json(output)
    typer.echo(f"筛选完成: {output}")


@app.command(name="help")
def help_cmd():
    """显示 gen_reg_tools 完整使用指南"""
    guide = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     gen_reg_tools 使用指南                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

gen_reg_tools 是寄存器自动化生成工具集，支持从 Excel 提取寄存器定义并生成：
  - UVM RAL 模型（SystemVerilog）
  - reg_slv Verilog 模块
  - 寄存器配置表（SystemVerilog）

──────────────────────────────────────────────────────────────────────────────
[bold]支持的命令[/bold]
──────────────────────────────────────────────────────────────────────────────

  [green]extract[/green]     从 Excel 提取寄存器数据并导出为 JSON
  [green]check[/green]       对提取结果进行常规检查
  [green]cif-check[/green]   检查寄存器地址是否在 CIF 定义的地址范围内
  [green]filter[/green]      按 BT 名称筛选 JSON 数据
  [green]regslv[/green]      生成 reg_slv Verilog 代码
  [green]ral[/green]         生成 UVM RAL 模型
  [green]cfg[/green]         生成寄存器配置表
  [green]help[/green]        显示此帮助信息

──────────────────────────────────────────────────────────────────────────────
[bold]1. extract — 从 Excel 提取寄存器数据[/bold]
──────────────────────────────────────────────────────────────────────────────

  用法模式（必须且只能选择一种）：
    单文件模式：  --excel  <file.xlsx>
    目录模式：    --excel-dir <dir>

  参数：
    -e, --excel      TEXT   单个 Excel 文件路径（.xlsx / .xls）
    -d, --excel-dir  TEXT   包含多个 Excel 文件的目录
    -c, --cif        TEXT   CIF 地址映射文件路径（可选）。若未指定，--cif-check 自动关闭
    -o, --output     TEXT   JSON 输出路径 [default: reg_data.json]
    -p, --prefix     TEXT   文件名前缀 [default: ASIC_PDT_V3R1]
        --check            提取后自动执行常规检查
        --cif-check        提取后自动执行 CIF 地址范围检查（仅在指定 --cif 时生效）

  文件名格式要求：{prefix}_{it_name}_{bt_name}.xlsx
  示例：ASIC_PDT_V3R1_lb_emp_sse.xlsx → it_name="lb", bt_name="emp_sse"

  示例：
    $ gen-reg extract -e ASIC_PDT_V3R1_ppe_dmacsec.xlsx -o data.json
    $ gen-reg extract -e ASIC_PDT_V3R1_ppe_dmacsec.xlsx -c CIF.xlsx -o data.json
    $ gen-reg extract -d ./2_Reg/Src/ --prefix Leonis -o all.json

──────────────────────────────────────────────────────────────────────────────
[bold]2. check — 常规检查[/bold]
──────────────────────────────────────────────────────────────────────────────

  参数：
    -j, --json  TEXT   由 extract 生成的 JSON 文件路径（必须）

  检查项：offset_addr 合法性、重复性、reg_width 与 field_bits 一致性等

  示例：
    $ gen-reg check -j reg_data.json

──────────────────────────────────────────────────────────────────────────────
[bold]3. cif-check — CIF 地址范围检查[/bold]
──────────────────────────────────────────────────────────────────────────────

  参数：
    -j, --json  TEXT   JSON 文件路径（必须）
    -c, --cif   TEXT   CIF 地址映射 Excel 文件路径（必须）

  示例：
    $ gen-reg cif-check -j reg_data.json -c ASIC_PDT_V3R1_CIF.xlsx

──────────────────────────────────────────────────────────────────────────────
[bold]4. filter — 按 BT 筛选 JSON / 列出所有 BT[/bold]
──────────────────────────────────────────────────────────────────────────────

  筛选模式（默认）：
    -j, --json    TEXT   JSON 文件路径（筛选模式必须）
    -b, --bt      TEXT   目标 BT 名称，多个用逗号分隔（筛选模式必须）
    -o, --output  TEXT   筛选后的 JSON 输出路径 [default: filtered.json]

  列 BT 模式（--get-bt）：
        --get-bt         列出所有 block_type 为 'bt' 的 Block 名称
    -j, --json    TEXT   从 JSON 文件列出 BT
    -e, --excel   TEXT   从 Excel 单文件提取后列出 BT
    -d, --excel-dir TEXT 从 Excel 目录批量提取后列出 BT
    -p, --prefix  TEXT   Excel 文件名前缀（提取模式可用）

  示例：
    $ gen-reg filter -j reg_data.json -b dmacsec -o dmacsec.json
    $ gen-reg filter -j reg_data.json -b dmacsec,sse,padpt -o sub.json
    $ gen-reg filter --get-bt -j reg_data.json
    $ gen-reg filter --get-bt -e ASIC_PDT_V3R1_ppe_dmacsec.xlsx
    $ gen-reg filter --get-bt -d ./2_Reg/Src/ --prefix Leonis

──────────────────────────────────────────────────────────────────────────────
[bold]5. regslv — 生成 reg_slv Verilog[/bold]
──────────────────────────────────────────────────────────────────────────────

  用法模式（必须且只能选择一种）：
    Excel 模式：  --excel <file>  --sheet <sheet_name>
    JSON 模式：   --json <file>   --bt <block_name>

  参数：
    -e, --excel   TEXT   Excel 文件路径（Excel 模式）
    -j, --json    TEXT   JSON 文件路径（JSON 模式）
    -s, --sheet  TEXT   目标 Sheet 名称（Excel 模式）
    -b, --bt      TEXT   目标 Block 名称（JSON 模式）
    -o, --output  TEXT   输出目录 [default: ./out]
        --config  TEXT   生成配置项 key=value（暂未实现）

  示例：
    $ gen-reg regslv -e ASIC_PDT_V3R1_intf_eth.xlsx -s eth_a2mti_mclk -o ./out/
    $ gen-reg regslv -j reg_data.json -b eth_a2mti_mclk -o ./out/

──────────────────────────────────────────────────────────────────────────────
[bold]6. ral — 生成 UVM RAL 模型[/bold]
──────────────────────────────────────────────────────────────────────────────

  用法模式（必须且只能选择一种）：
    Excel 模式：  --excel <file>  --bn <block_name>
    JSON 模式：   --json <file>   --cfg <cfg.py>

  参数：
    -e, --excel   TEXT   Excel 文件路径（Excel 模式）
    -j, --json    TEXT   JSON 文件路径（JSON 模式）
    -b, --bn      TEXT   目标 Block 名称（Excel 模式）
    -c, --cfg     TEXT   RAL 配置脚本路径（JSON 模式）
    -o, --output  TEXT   输出目录 [default: ./ral_out]

  示例：
    $ gen-reg ral -e ASIC_PDT_V3R1_ppe_dmacsec.xlsx -b dmacsec -o ./ral_out/
    $ gen-reg ral -j reg_data.json -c ral_cfg.py -o ./ral_out/

──────────────────────────────────────────────────────────────────────────────
[bold]7. cfg — 生成寄存器配置表[/bold]
──────────────────────────────────────────────────────────────────────────────

  参数：
    -j, --json    TEXT   JSON 文件路径（必须）
    -b, --bt      TEXT   目标 Block 名称（必须）
    -o, --output  TEXT   输出目录 [default: ./cfg_out]

  输出文件：
    - {bt}_reg_tbl_cfg_decl.sv  — 配置表结构体声明
    - {bt}_reg_tbl_cfg.sv       — 配置表实例化及赋值逻辑
    - {bt}_init_cfg_by_ral.sv   — RAL 配置表初始化代码

  示例：
    $ gen-reg cfg -j reg_data.json -b dmacsec -o ./cfg_out/

──────────────────────────────────────────────────────────────────────────────
[bold]典型工作流[/bold]
──────────────────────────────────────────────────────────────────────────────

  工作流 A：完整项目（目录模式，不带 CIF）
    $ gen-reg extract -d ./2_Reg/Src/ --prefix Leonis -o all.json
    $ gen-reg check -j all.json
    $ gen-reg filter -j all.json -b dmacsec -o dmacsec.json
    $ gen-reg regslv -j dmacsec.json -b dmacsec -o ./regslv_out/
    $ gen-reg cfg    -j dmacsec.json -b dmacsec -o ./cfg_out/

  工作流 B：单个模块快速生成（带 CIF）
    $ gen-reg extract -e ASIC_PDT_V3R1_ppe_dmacsec.xlsx -c CIF.xlsx --check --cif-check -o data.json
    $ gen-reg regslv -j data.json -b dmacsec -o ./regslv_out/
    $ gen-reg ral    -j data.json -c ral_cfg.py -o ./ral_out/
    $ gen-reg cfg    -j data.json -b dmacsec -o ./cfg_out/

──────────────────────────────────────────────────────────────────────────────
[bold]获取子命令帮助[/bold]
──────────────────────────────────────────────────────────────────────────────

  使用 --help 查看任意命令的详细帮助：
    $ gen-reg extract --help
    $ gen-reg regslv --help
    $ gen-reg ral --help
"""
    typer.echo(guide)


if __name__ == "__main__":
    app()
