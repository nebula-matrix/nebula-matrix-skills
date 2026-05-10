from typing import List, Dict, Any

from gen_reg_tools.regslv.config import RegSlvConfig


class ProcRegAsg:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any) -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.reg_assign_ls = []

    def append_reg_asg_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcRegAsg append_reg_asg_ls ")

        for depth_idx in range(item_dict.get("depth")):
            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)

            self.reg_assign_ls.append(
                {"lhs": f"{item_dict.get('name')}{idx}_reg", "sublist": []}
            )

            field_num = len(item_dict.get("subpart"))
            tmp_sublist = []
            for field_idx, field_dict in enumerate(item_dict.get("subpart"), 1):
                if field_idx == field_num:
                    sub_postfix = "\n};"
                else:
                    sub_postfix = ","

                if field_dict.get("rw_attr") == "wo" or field_dict.get("field") == "rsv":
                    tmp_sublist.append(
                        {"sub_sig": f"{field_dict.get('bits')}'b0", "sub_postfix": sub_postfix}
                    )
                else:
                    tmp_sublist.append(
                        {"sub_sig": f"{item_dict.get('name')}_{field_dict.get('field')}{idx}", "sub_postfix": sub_postfix}
                    )
            self.reg_assign_ls[-1]["sublist"].extend(tmp_sublist)

    def get_reg_asg_ls(self) -> None:
        for reg_dict in self.extract_ls:
            if reg_dict["type"] == "reg":
                self.append_reg_asg_ls(reg_dict)
