import importlib.util
import typer

from gen_reg_tools.ral.renderer import RalRenderer
from gen_reg_tools.ral.processors import RalProcessor


def _load_cfg(cfg_path: str) -> tuple[str, set[str]]:
    """从 cfg.py 文件加载并返回 (top_name, set(bt_names))。"""
    spec = importlib.util.spec_from_file_location("ral_cfg", cfg_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法加载配置文件: {cfg_path}")
    cfg_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg_module)

    top_name = getattr(cfg_module, "top_name", None)
    if top_name is None:
        raise ValueError(f"配置文件 {cfg_path} 中未定义 top_name")

    inst_map = getattr(cfg_module, "inst_map", {})
    bt_names = set(inst_map.keys()) if isinstance(inst_map, dict) else set()

    return str(top_name).lower(), bt_names


class RalGenerator:
    """UVM RAL 生成器入口"""

    @staticmethod
    def generate(
        *,
        excel_path: str = "",
        excel_dir: str = "",
        prefix: str = "",
        bn: str = "",
        json_path: str = "",
        cfg_path: str = "",
        output_dir: str = "",
    ) -> None:
        """生成 UVM RAL 模型

        支持三种参数组合：
        - excel_path + bn + output_dir：从 Excel 提取并生成
        - excel_dir + cfg_path + output_dir：从目录提取 + cfg.py 生成
        - json_path + cfg_path + output_dir：从 JSON + cfg.py 加载并生成
        """
        if not output_dir:
            raise ValueError("output_dir 为必填参数")

        if excel_path and bn:
            from gen_reg_tools.extractor.pipeline import Extractor
            data = Extractor.extract_file(excel_path, "/dev/null")
            RalGenerator.generate_from_data(
                data=data, name=bn.lower(), output_dir=output_dir
            )
        elif excel_dir and cfg_path:
            from gen_reg_tools.extractor.pipeline import Extractor
            from gen_reg_tools.core.traversal import RegDataTraverser

            data = Extractor.extract_dir(excel_dir, "/dev/null", prefix=prefix if prefix else None)
            name, cfg_bt_names = _load_cfg(cfg_path)

            # 校验 JSON 中是否包含 cfg 要求的所有 BT
            json_bt_names = set(RegDataTraverser.get_all_bt_names(data))
            missing = cfg_bt_names - json_bt_names
            if missing:
                typer.echo(
                    f"Error: 配置文件中的 BT 在 JSON 中未找到: {', '.join(sorted(missing))}"
                )
                raise typer.Exit(1)

            RalGenerator.generate_from_data(
                data=data, name=name, output_dir=output_dir
            )
        elif json_path and cfg_path:
            from gen_reg_tools.core.data_model import RegData
            from gen_reg_tools.core.traversal import RegDataTraverser

            data = RegData.from_json(json_path)
            name, cfg_bt_names = _load_cfg(cfg_path)

            # 校验 JSON 中是否包含 cfg 要求的所有 BT
            json_bt_names = set(RegDataTraverser.get_all_bt_names(data))
            missing = cfg_bt_names - json_bt_names
            if missing:
                typer.echo(
                    f"Error: 配置文件中的 BT 在 JSON 中未找到: {', '.join(sorted(missing))}"
                )
                raise typer.Exit(1)

            RalGenerator.generate_from_data(
                data=data, name=name, output_dir=output_dir
            )
        else:
            raise ValueError("必须提供 excel_path+bn 或 excel_dir+cfg_path 或 json_path+cfg_path")

    @staticmethod
    def generate_from_data(
        *,
        data,
        name: str = "",
        output_dir: str = "",
    ) -> None:
        """从 RegData 对象生成 RAL"""
        import os

        if not output_dir:
            raise ValueError("output_dir 为必填参数")

        processor = RalProcessor(data)
        processor.process()

        tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
        renderer = RalRenderer(tpl_dir)

        os.makedirs(output_dir, exist_ok=True)

        # 文件名使用传入的 name（小写），模板内容仍使用 processor.top_name
        file_name = name if name else processor.top_name

        # 渲染各个子模板
        top_name = processor.top_name
        txt_reg = renderer.render_reg({"subpart": processor.proc_reg.render_ls})
        txt_block = renderer.render_block({"subpart": processor.proc_ral_block.render_ls})
        txt_mem = renderer.render_mem({"subpart": processor.proc_ral_mem.render_ls})
        txt_vreg = renderer.render_vreg({"subpart": processor.proc_vreg.render_ls})
        txt_bkdr = renderer.render_reg_bkdr({
            "subpart": processor.proc_reg_bkdr.render_ls,
            "top_name": top_name,
        })
        txt_block_intf = renderer.render_block_intf({
            "subpart": processor.proc_block_intf.render_ls,
            "top_name": top_name,
        })
        txt_sys_block = renderer.render_sys_block({
            "subpart": processor.proc_ral_sys_block.render_ls,
            "top_name": top_name,
        })

        # 拼接 6 个文件内容为 ral_sys_{name}_block.sv
        # bkdr 放在最前面，其余按原有顺序
        txt_sys_block_combined = "\n".join([
            txt_bkdr,
            txt_reg,
            txt_block,
            txt_mem,
            txt_vreg,
            txt_sys_block,
        ])

        outputs = {
            f"ral_sys_{file_name}_block.sv": txt_sys_block_combined,
            f"ral_{file_name}_block_intf.sv": txt_block_intf,
        }

        for fname, content in outputs.items():
            path = os.path.join(output_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            typer.echo(f"  已生成: {path}")

        typer.echo(f"RAL 生成完成: {output_dir}")
