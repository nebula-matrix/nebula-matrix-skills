from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.ral.processors.proc_common import calc_tbl_dw_entry


class ProcBlockIntf:
    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.top_name      = all_data_dict.get("top_name")
        self.render_ls     = []

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            widx         = {}
            widx["sctr"] = 0
            widx["rctr"] = 0
            widx["rw"]   = 0
            widx["ro"]   = 0

            dw_ls      = []

            for reg_item in bt_item.get("subpart", []):
                if reg_item.get("type") == "wide_reg":
                    for idx, field_item in enumerate(reg_item.get("subpart", []), 0):
                        if field_item.get("name") != "rsv":
                            field_item["widx"] = widx[field_item.get("rw_attr")]
                            field_item["idx"]  = idx
                            dw_ls.append(field_item["bits"])
                        widx[field_item.get("rw_attr")] += reg_item.get("depth")

            if len(dw_ls) > 0:
                max_dw_a32, _ = calc_tbl_dw_entry(dw_ls)
                bt_item["max_dw_a32"] = max_dw_a32

            self.render_ls.append(bt_item)
