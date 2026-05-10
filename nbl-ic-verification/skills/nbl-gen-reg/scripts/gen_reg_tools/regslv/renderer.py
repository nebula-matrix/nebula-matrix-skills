from typing import Dict, Any
from gen_reg_tools.generator.renderer import BaseRenderer


class RegSlvRenderer(BaseRenderer):
    def render_header(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_1_header.sv", context)

    def render_port(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_2_port.sv", context)

    def render_decl(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_3_decl.sv", context)

    def render_main_code(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_4_main_code.sv", context)

    def render_output(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_5_output_asg.sv", context)

    def render_regout(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_6_regout.sv", context)

    def render_setint(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_7_setint.sv", context)

    def render_inst(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_8_inst.sv", context)

    def render_reg_read(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_9_reg_read.sv", context)

    def render_ending(self) -> str:
        return self.render("tpl_10_ending.sv", {})

    def render_cross_ck(self, context: Dict[str, Any]) -> str:
        return self.render("tpl_11_cross_ck.sv", context)
