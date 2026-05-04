from typing import Dict, Any
from gen_reg_tools.generator.renderer import BaseRenderer


class RalRenderer(BaseRenderer):
    def render_block_intf(self, context: Dict[str, Any]) -> str:
        return self.render("ral_xxx_block_intf.sv", context)

    def render_mem(self, context: Dict[str, Any]) -> str:
        return self.render("ral_mem_xxx.sv", context)

    def render_vreg(self, context: Dict[str, Any]) -> str:
        return self.render("ral_vreg_xxx.sv", context)

    def render_reg_bkdr(self, context: Dict[str, Any]) -> str:
        return self.render("ral_reg_xxx_bkdr.sv", context)

    def render_sys_block(self, context: Dict[str, Any]) -> str:
        return self.render("ral_sys_xxx_block.sv", context)

    def render_block(self, context: Dict[str, Any]) -> str:
        return self.render("ral_block_xxx.sv", context)

    def render_reg(self, context: Dict[str, Any]) -> str:
        return self.render("ral_reg_xxx.sv", context)

    def render_sys(self, context: Dict[str, Any]) -> str:
        return self.render("ral_sys_xxx.sv", context)
