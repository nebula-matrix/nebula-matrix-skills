from typing import List, Dict, Any

from gen_reg_tools.regslv.config import RegSlvConfig


class ProcSetInt:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any, ckp: str = "") -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.setint_ls = []
        self.ckp = ckp

    def append_setint_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcSetInt append_setint_ls ")

        if self.config.multi_ck:
            clock_domain = "_" + item_dict.get("clock_domain")
        else:
            clock_domain = ""

        for depth_idx in range(item_dict.get("depth")):
            for field_idx, field_dict in enumerate(item_dict.get("subpart"), 1):
                if field_dict.get("field") != "rsv" and "int_status" in item_dict.get("name"):
                    if "cif_err" in field_dict.get("field"):
                        self.setint_ls.append(
                            {
                                "lhs": f"set_{self.config.module_name}{self.ckp}_int_{field_dict.get('field')}",
                                "rhs": f"inner_cif_err{clock_domain} | {self.config.module_name}{self.ckp}_int_set_{field_dict.get('field')}",
                            }
                        )
                    else:
                        self.setint_ls.append(
                            {
                                "lhs": f"set_{self.config.module_name}{self.ckp}_int_{field_dict.get('field')}",
                                "rhs": f"i_reg_{self.config.module_name}{self.ckp}_int_status_{field_dict.get('field')}_set | {self.config.module_name}{self.ckp}_int_set_{field_dict.get('field')}",
                            }
                        )

    def get_setint_ls(self) -> None:
        for reg_dict in self.extract_ls:
            if reg_dict["type"] == "reg":
                self.append_setint_ls(reg_dict)
