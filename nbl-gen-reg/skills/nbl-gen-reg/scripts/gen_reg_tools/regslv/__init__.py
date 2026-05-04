import typer

from gen_reg_tools.regslv.config import RegSlvConfig
from gen_reg_tools.regslv.renderer import RegSlvRenderer


class RegSlvGenerator:
    """reg_slv 生成器入口（骨架）"""

    @staticmethod
    def generate(
        *,
        excel_path: str = "",
        sheet: str = "",
        json_path: str = "",
        bt: str = "",
        output_dir: str = "",
    ) -> None:
        """生成 reg_slv Verilog 代码（骨架实现）

        支持两种参数组合：
        - excel_path + sheet + output_dir：从 Excel 提取并生成
        - json_path + bt + output_dir：从 JSON 加载并生成
        """
        if not output_dir:
            raise ValueError("output_dir 为必填参数")

        if excel_path and sheet:
            from gen_reg_tools.extractor.pipeline import Extractor
            from gen_reg_tools.core.traversal import RegDataTraverser
            data = Extractor.extract_file(excel_path, "/dev/null")
            block = RegDataTraverser.find_bt(data, sheet)
            if not block:
                raise ValueError(f"在 Excel 中未找到 sheet='{sheet}' 对应的 Block")
            RegSlvGenerator.generate_from_data(data=data, bt=sheet, output_dir=output_dir)
        elif json_path and bt:
            from gen_reg_tools.core.data_model import RegData
            data = RegData.from_json(json_path)
            RegSlvGenerator.generate_from_data(data=data, bt=bt, output_dir=output_dir)
        else:
            raise ValueError("必须提供 excel_path+sheet 或 json_path+bt")

    @staticmethod
    def generate_from_data(
        *,
        data,
        bt: str = "",
        output_dir: str = "",
    ) -> None:
        """从 RegData 对象生成 reg_slv"""
        import os
        import logging
        from gen_reg_tools.core.traversal import RegDataTraverser
        from gen_reg_tools.regslv.config import RegSlvConfig
        from gen_reg_tools.regslv.renderer import RegSlvRenderer
        from gen_reg_tools.regslv.processors import RegProcessor

        if not bt or not output_dir:
            raise ValueError("bt 和 output_dir 为必填参数")

        block = RegDataTraverser.find_bt(data, bt)
        if not block:
            raise ValueError(f"在 RegData 中未找到 bt='{bt}' 的 Block")

        config = RegSlvConfig(module_name=bt)
        logger = logging.getLogger("regslv")

        processor = RegProcessor(block, config, logger)
        processor.process()

        # 构建模板上下文
        is_multi = config.multi_ck and len(config.multi_ck_ls) > 1
        if is_multi:
            # 多时钟域：每个域渲染一次，生成多个文件
            # TODO: 多时钟域生成需要进一步验证
            raise NotImplementedError("多时钟域 reg_slv 生成暂未实现")

        # 单时钟域
        tpl_dict = {
            "header": processor.proc_header.header_dict,
            "common": processor.proc_common.common_dict,
            "iport": processor.proc_port.iport_ls,
            "oport": processor.proc_port.oport_ls,
            "wreg_iport": processor.proc_port.wreg_iport_ls,
            "wreg_oport": processor.proc_port.wreg_oport_ls,
            "tbl_iport": processor.proc_port.tbl_iport_ls,
            "tbl_oport": processor.proc_port.tbl_oport_ls,
            "reg_decl": processor.proc_decl.sig_decl_ls,
            "wreg_decl": processor.proc_decl.wreg_sig_decl_ls,
            "tbl_decl": processor.proc_decl.tbl_sig_decl_ls,
            "wreg_decl_dict": processor.proc_decl.wreg_decl_dict,
            "tbl_dict": processor.proc_inst.tbl_inst_dict,
            "tbl_inst_dict": processor.proc_inst.tbl_inst_dict,
            "op_assign_ls": processor.proc_op_asg.op_assign_ls,
            "wreg_op_assign_ls": processor.proc_op_asg.wreg_op_assign_ls,
            "tbl_op_assign_ls": processor.proc_op_asg.tbl_op_assign_ls,
            "tbl_asg_dict": processor.proc_op_asg.tbl_asg_dict,
            "wreg_asg_dict": processor.proc_op_asg.wreg_asg_dict,
            "reg_assign_ls": processor.proc_reg_asg.reg_assign_ls,
            "setint_ls": processor.proc_setint.setint_ls,
            "inst_ls": processor.proc_inst.inst_ls,
            "ro_tbl_inst_ls": processor.proc_inst.ro_tbl_inst_ls,
            "wreg_inst_dict": processor.proc_inst.wreg_inst_dict,
            "wreg_inst_ls": processor.proc_inst.wreg_inst_ls,
            "rd_blk_ls": processor.proc_rd_blk.rd_blk_ls,
            "ck_domain": "",
        }

        if processor.proc_cross_ck:
            tpl_dict["cross_ck_dict"] = processor.proc_cross_ck.cross_ck_dict

        tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
        renderer = RegSlvRenderer(tpl_dir)

        os.makedirs(output_dir, exist_ok=True)

        parts = [
            renderer.render_header(tpl_dict),
            renderer.render_port(tpl_dict),
            renderer.render_decl(tpl_dict),
            renderer.render_main_code(tpl_dict),
            renderer.render_output(tpl_dict),
            renderer.render_regout(tpl_dict),
            renderer.render_setint(tpl_dict),
            renderer.render_inst(tpl_dict),
            renderer.render_reg_read(tpl_dict),
            renderer.render_ending(),
        ]

        if processor.proc_cross_ck:
            parts.insert(-1, renderer.render_cross_ck(tpl_dict))

        content = "\n".join(parts)

        output_path = os.path.join(output_dir, f"{bt}_reg_slv.sv")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        typer.echo(f"reg_slv 生成完成: {output_path}")
