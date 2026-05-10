from typing import List, Dict, Any
import re

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcSigDecl:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any, ckp: str = "") -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.sig_decl_ls = []
        self.wreg_sig_decl_ls = []
        self.tbl_sig_decl_ls = []
        self.wreg_decl_dict = {}
        self.ckp = ckp

    def append_tbl_decl_ls(self, item_dict) -> None:
        self.logger.debug(f"start ProcSigDecl append_tbl_decl_ls ")
        for field_dict in item_dict.get("subpart"):
            if field_dict.get("rw_attr") != "ro":
                return 0

        tbl_addr_cnt = RegUtils.calc_tbl_aw(item_dict.get("depth")) + 1
        tmp_ls = [
            {"unit": "logic", "sig_name": f'mid_w2r_{item_dict.get("name")}_tbl_req'},
            {"unit": "logic", "sig_name": f'mid_w2r_{item_dict.get("name")}_tbl_rw'},
            {"unit": "logic", "sig_name": f'mid_w2r_{item_dict.get("name")}_tbl_addr', "aw": tbl_addr_cnt},
            {"unit": "logic", "sig_name": f'mid_w2r_{item_dict.get("name")}_tbl_wdata', "dw": item_dict.get("vld_bits")},
            {"unit": "logic", "sig_name": f'mid_r2w_{item_dict.get("name")}_tbl_ack'},
            {"unit": "logic", "sig_name": f'mid_r2w_{item_dict.get("name")}_tbl_rdata', "dw": item_dict.get("vld_bits")},
            {"unit": "logic", "sig_name": f'mid_r2w_{item_dict.get("name")}_tbl_status'},
        ]
        self.tbl_sig_decl_ls.extend(tmp_ls)

    def append_wreg_decl_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcSigDecl append_wreg_decl_ls ")

        special_reg_flag = bool(re.search(r"int_mask|int_set|car_ctrl", item_dict.get("name")))

        for depth_idx in range(item_dict.get("depth")):
            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)
            for field_dict in item_dict.get("subpart"):
                if field_dict.get("field") != "rsv":
                    if field_dict.get("rw_attr") not in self.config.input_sig_ls and (not special_reg_flag):
                        self.wreg_sig_decl_ls.append(
                            {"unit": "logic", "sig_name": f'{item_dict.get("name")}{idx}', "dw": item_dict.get("vld_bits")},
                        )

    def get_wreg_decl_dict(self, wreg_ls: List) -> None:
        rw_cnt = 0
        ro_cnt = 0
        sctr_cnt = 0
        rctr_cnt = 0

        dw_ls = [tbl.get("vld_bits") for tbl in wreg_ls]
        max_dw_a32, _ = RegUtils.calc_tbl_dw_entry(dw_ls)

        for item_dict in wreg_ls:
            depth = item_dict.get("depth")
            for depth_idx in range(depth):
                for field_dict in item_dict.get("subpart"):
                    if field_dict.get("field") == "rsv":
                        continue
                    if field_dict.get("rw_attr") == "rw":
                        rw_cnt += 1
                    elif field_dict.get("rw_attr") == "ro":
                        ro_cnt += 1
                    elif field_dict.get("rw_attr") == "sctr":
                        sctr_cnt += 1
                    elif field_dict.get("rw_attr") == "rctr":
                        rctr_cnt += 1
                    else:
                        self.logger.error(
                            f"get_wreg_decl_dict rw_attr ERROR, now field_name:{field_dict.get('field')}, rw_attr:{field_dict.get('rw_attr')}"
                        )

        self.wreg_decl_dict["rw_cnt"] = rw_cnt
        self.wreg_decl_dict["ro_cnt"] = ro_cnt
        self.wreg_decl_dict["sctr_cnt"] = sctr_cnt
        self.wreg_decl_dict["rctr_cnt"] = rctr_cnt
        self.wreg_decl_dict["max_dw_a32"] = max_dw_a32

    def append_reg_decl_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcSigDecl append_reg_decl_ls ")

        for depth_idx in range(item_dict.get("depth")):
            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)

            self.sig_decl_ls.append(
                {"unit": "logic", "sig_name": f'{item_dict.get("name")}{idx}_reg', "dw": item_dict.get("width")},
            )

            if "cif_err_info" in item_dict.get("name"):
                self.sig_decl_ls.append(
                    {"unit": "logic", "sig_name": f'inner_cif_err'},
                )

            for field_item in item_dict.get("subpart"):
                if field_item.get("field") != "rsv":
                    self.sig_decl_ls.append(
                        {"unit": "logic", "sig_name": f'{item_dict.get("name")}_{field_item.get("field")}{idx}', "dw": field_item.get("bits")},
                    )
                    if "int_status" in item_dict.get("name"):
                        self.sig_decl_ls.append(
                            {"unit": "logic", "sig_name": f'set_{self.config.module_name}{self.ckp}_int_{field_item.get("field")}'},
                        )

    def get_sig_decl_ls(self) -> None:
        wreg_ls = []

        for reg_dict in self.extract_ls:
            if reg_dict["type"] == "tbl":
                self.append_tbl_decl_ls(reg_dict)
            elif reg_dict["type"] == "wide_reg":
                self.append_wreg_decl_ls(reg_dict)
                wreg_ls.append(reg_dict)
            elif reg_dict["type"] == "reg":
                self.append_reg_decl_ls(reg_dict)
            else:
                self.logger.error(
                    f"[function.get_sig_decl_ls] type should be tbl/reg/wide_reg, but now is {reg_dict['type']}"
                )

        if len(wreg_ls) > 0:
            self.get_wreg_decl_dict(wreg_ls)
