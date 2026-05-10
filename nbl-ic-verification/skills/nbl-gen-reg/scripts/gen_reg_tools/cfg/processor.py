import importlib.util
import os
from typing import List, Dict, Any, Optional

import typer

from gen_reg_tools.core.data_model import RegData, Block, Register, Field
from gen_reg_tools.core.traversal import RegDataTraverser
from gen_reg_tools.cfg.renderer import CfgRenderer
from gen_reg_tools.extractor.pipeline import Extractor


def _load_cfg(cfg_path: str) -> tuple[str, set[str]]:
    """从 cfg.py 文件加载并返回 (top_name, set(bt_names))。"""
    spec = importlib.util.spec_from_file_location("cfg_module", cfg_path)
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


class CfgProcessor:
    """寄存器配置表生成处理器"""

    def __init__(self, bt_name: str, reg_data: RegData, output_dir: str):
        self.bt_name = bt_name
        self.reg_data = reg_data
        self.output_dir = output_dir

        self._max_reg_dw_length = 0
        self._max_reg_name_length = 0
        self._max_field_dw_length = 0
        self._max_field_name_length = 0
        self._max_mix_reg_name_dw_length = 0

        tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.renderer = CfgRenderer(tpl_dir)

    def _find_bt_node(self) -> Optional[Block]:
        return RegDataTraverser.find_bt(self.reg_data, self.bt_name)

    def extract_register_info(self, bt_node: Block, rw_attrs: Optional[set[str]] = None) -> List[Dict[str, Any]]:
        """
        遍历 BT 节点下的寄存器，提取符合条件的信息，并计算掩码 (mask)。

        若 rw_attrs 为 None（默认），提取所有寄存器（不限制 rw 属性）。
        若 rw_attrs 为指定集合，只提取包含至少一个 field 的 rw_attr 落在该集合中的寄存器。

        掩码计算规则：如果 field name 不为 'rsv'，其对应的 bit 置1，否则置0。
        """
        extracted_regs: List[Dict[str, Any]] = []

        for reg in bt_node.subpart:
            fields = reg.subpart
            should_include = True

            if rw_attrs is not None:
                has_matching_field = False
                for field in fields:
                    if field.rw_attr in rw_attrs:
                        has_matching_field = True
                        break
                should_include = has_matching_field

            if should_include:
                mask_val = 0
                for field in fields:
                    if field.name != "rsv":
                        field_mask = ((1 << field.bits) - 1) << field.lsb
                        mask_val |= field_mask

                mask_str = f"{mask_val:08x}"

                reg_obj = {
                    "name": reg.name,
                    "mask": mask_str,
                    "type": reg.reg_type,
                    "depth": reg.depth,
                    "width": reg.width,
                    "subpart": [],
                }

                rsv_idx = 0
                for field in fields:
                    if field.name == "rsv":
                        field_name = f"rsv_{rsv_idx}"
                        rsv_idx += 1
                    else:
                        field_name = field.name

                    dft = field.default_value
                    field_obj = {
                        "bits": field.bits,
                        "name": field_name,
                        "default_value": f"'h{dft:X}",
                    }
                    reg_obj["subpart"].append(field_obj)

                extracted_regs.append(reg_obj)

        return extracted_regs

    def _field_align_process(self, reg_obj: Dict[str, Any]) -> None:
        if len(str(reg_obj.get("bits"))) > self._max_field_dw_length:
            self._max_field_dw_length = len(str(reg_obj.get("bits")))

        for field_dict in reg_obj.get("subpart", []):
            if len(field_dict.get("name", "")) > self._max_field_name_length:
                self._max_field_name_length = len(field_dict.get("name", ""))

    def _reg_align_process(self, reg_obj: Dict[str, Any]) -> None:
        if len(str(reg_obj.get("width"))) > self._max_reg_dw_length:
            self._max_reg_dw_length = len(str(reg_obj.get("width")))

        if len(reg_obj.get("name", "")) > self._max_reg_name_length:
            self._max_reg_name_length = len(reg_obj.get("name", ""))

    def _mix_align_process(self) -> None:
        if self._max_reg_name_length < self._max_field_dw_length + 6:
            self._max_mix_reg_name_dw_length = self._max_field_dw_length + 6
        else:
            self._max_mix_reg_name_dw_length = self._max_reg_name_length

    def _build_context(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        for item in results:
            self._reg_align_process(item)
            self._field_align_process(item)
        self._mix_align_process()
        return {
            "bt_name": self.bt_name,
            "results": results,
            "max_field_dw_len": self._max_field_dw_length,
            "max_field_name_len": self._max_field_name_length,
            "max_reg_dw_len": self._max_reg_dw_length,
            "max_reg_name_len": self._max_reg_name_length,
            "mix_len": self._max_mix_reg_name_dw_length,
        }

    def build_context(self, *, rw_attrs: Optional[set[str]] = None) -> Dict[str, Any]:
        """只构建渲染上下文，不写入文件。"""
        self._max_reg_dw_length = 0
        self._max_reg_name_length = 0
        self._max_field_dw_length = 0
        self._max_field_name_length = 0
        self._max_mix_reg_name_dw_length = 0

        bt_node = self._find_bt_node()
        if not bt_node:
            raise ValueError(f"在 RegData 结构中未找到 bt_name='{self.bt_name}' 的模块。")

        results = self.extract_register_info(bt_node, rw_attrs=rw_attrs)
        return self._build_context(results)

    def process(self, *, rw_attrs: Optional[set[str]] = None) -> Dict[str, Any]:
        bt_node = self._find_bt_node()
        if not bt_node:
            raise ValueError(f"在 RegData 结构中未找到 bt_name='{self.bt_name}' 的模块。")

        results = self.extract_register_info(bt_node, rw_attrs=rw_attrs)
        context = self._build_context(results)

        os.makedirs(self.output_dir, exist_ok=True)

        decl_str = self.renderer.render_reg_tbl_decl(context)
        decl_path = os.path.join(self.output_dir, f"{self.bt_name}_reg_tbl_cfg_decl.sv")
        with open(decl_path, "w", encoding="utf-8") as f:
            f.write(decl_str)

        cfg_str = self.renderer.render_reg_tbl_cfg(context)
        cfg_path = os.path.join(self.output_dir, f"{self.bt_name}_reg_tbl_cfg.sv")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(cfg_str)

        init_str = self.renderer.render_init_cfg(context)
        init_path = os.path.join(self.output_dir, f"{self.bt_name}_init_cfg_by_ral.sv")
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(init_str)

        return context


class CfgGenerator:
    """寄存器配置表生成器入口"""

    @staticmethod
    def generate(
        *,
        excel_path: str = "",
        bn: str = "",
        json_path: str = "",
        bt: str = "",
        cfg_path: str = "",
        output_dir: str = "",
    ) -> None:
        """生成配置表

        支持三种参数组合：
        - excel_path + bn + output_dir：从 Excel 提取并生成单 bt 配置表
        - json_path + bt + output_dir：从 JSON 加载并生成单 bt 配置表
        - json_path + cfg_path + output_dir：从 JSON + cfg.py 加载并生成系统级配置表
        """
        if not output_dir:
            raise ValueError("output_dir 为必填参数")

        if excel_path and bn:
            data = Extractor.extract_file(excel_path, "/dev/null")
            CfgGenerator.generate_from_data(data=data, bt=bn, output_dir=output_dir)
        elif json_path and bt:
            data = RegData.from_json(json_path)
            CfgGenerator.generate_from_data(data=data, bt=bt, output_dir=output_dir)
        elif json_path and cfg_path:
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

            CfgGenerator._generate_multi_bt(
                data=data,
                top_name=name,
                bt_names=sorted(cfg_bt_names),
                output_dir=output_dir,
            )
        else:
            raise ValueError("必须提供 excel_path+bn 或 json_path+bt 或 json_path+cfg_path")

    @staticmethod
    def _generate_multi_bt(
        *,
        data: RegData,
        top_name: str,
        bt_names: List[str],
        output_dir: str,
    ) -> None:
        """多 BT 模式：为所有 BT 生成配置表，合并输出到 {top_name}_*.sv"""
        os.makedirs(output_dir, exist_ok=True)

        # 收集每个 BT 的上下文
        contexts: List[Dict[str, Any]] = []
        for bt_name in bt_names:
            processor = CfgProcessor(bt_name=bt_name, reg_data=data, output_dir=output_dir)
            ctx = processor.build_context()
            contexts.append(ctx)

        # 计算全局对齐值
        global_max_field_dw = max(c["max_field_dw_len"] for c in contexts)
        global_max_field_name = max(c["max_field_name_len"] for c in contexts)
        global_max_reg_dw = max(c["max_reg_dw_len"] for c in contexts)
        global_max_reg_name = max(c["max_reg_name_len"] for c in contexts)

        if global_max_reg_name < global_max_field_dw + 6:
            global_mix_len = global_max_field_dw + 6
        else:
            global_mix_len = global_max_reg_name

        # 使用临时 processor 访问 renderer
        tpl_proc = CfgProcessor(bt_name=top_name, reg_data=data, output_dir=output_dir)

        # --- reg_tbl_cfg_decl.sv：合并所有 BT 的结构体声明 ---
        merged_results = []
        for ctx in contexts:
            merged_results.extend(ctx["results"])

        decl_ctx = {
            "bt_name": top_name,
            "results": merged_results,
            "max_field_dw_len": global_max_field_dw,
            "max_field_name_len": global_max_field_name,
            "max_reg_dw_len": global_max_reg_dw,
            "max_reg_name_len": global_max_reg_name,
            "mix_len": global_mix_len,
        }
        decl_str = tpl_proc.renderer.render_reg_tbl_decl(decl_ctx)
        decl_path = os.path.join(output_dir, f"{top_name}_reg_tbl_cfg_decl.sv")
        with open(decl_path, "w", encoding="utf-8") as f:
            f.write(decl_str)

        # --- reg_tbl_cfg.sv：按 BT 顺序拼接类定义 ---
        cfg_parts = []
        for ctx in contexts:
            ctx_global = {
                **ctx,
                "max_field_dw_len": global_max_field_dw,
                "max_field_name_len": global_max_field_name,
                "max_reg_dw_len": global_max_reg_dw,
                "max_reg_name_len": global_max_reg_name,
                "mix_len": global_mix_len,
            }
            cfg_parts.append(tpl_proc.renderer.render_reg_tbl_cfg(ctx_global))
        cfg_path = os.path.join(output_dir, f"{top_name}_reg_tbl_cfg.sv")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write("\n".join(cfg_parts))

        # --- init_cfg_by_ral.sv：按 BT 顺序拼接 task ---
        init_parts = []
        for ctx in contexts:
            init_parts.append(tpl_proc.renderer.render_init_cfg(ctx))
        init_path = os.path.join(output_dir, f"{top_name}_init_cfg_by_ral.sv")
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("\n".join(init_parts))

    @staticmethod
    def generate_from_data(
        *,
        data: RegData,
        bt: str = "",
        output_dir: str = "",
    ) -> None:
        """从 RegData 对象生成配置表（单 BT 模式）"""
        if not bt or not output_dir:
            raise ValueError("bt 和 output_dir 为必填参数")
        processor = CfgProcessor(bt_name=bt, reg_data=data, output_dir=output_dir)
        processor.process()
