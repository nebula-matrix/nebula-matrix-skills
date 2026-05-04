from typing import Dict, Any
from gen_reg_tools.generator.renderer import BaseRenderer


class CfgRenderer(BaseRenderer):
    def render_reg_tbl_decl(self, context: Dict[str, Any]) -> str:
        return self.render("reg_tbl_cfg_decl.j2", context)

    def render_reg_tbl_cfg(self, context: Dict[str, Any]) -> str:
        return self.render("reg_tbl_cfg.j2", context)

    def render_init_cfg(self, context: Dict[str, Any]) -> str:
        return self.render("init_cfg_by_ral.j2", context)
