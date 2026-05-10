from typing import List, Dict, Any
import re

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcPort:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any) -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.iport_ls = []
        self.oport_ls = []
        self.wreg_iport_ls = []
        self.wreg_oport_ls = []
        self.tbl_iport_ls = []
        self.tbl_oport_ls = []

    def append_tbl_port_ls(self, item_dict) -> None:
        self.logger.debug("start function: append_tbl_port_ls")

        tmp_ls = [
            {"direct": "input", "unit": "logic", "sig_name": f'i_reg_{item_dict.get("name")}_tbl_ack'},
            {"direct": "input", "unit": "logic", "sig_name": f'i_reg_{item_dict.get("name")}_tbl_status'},
            {"direct": "input", "unit": "logic", "sig_name": f'i_reg_{item_dict.get("name")}_tbl_rdata', "dw": item_dict["vld_bits"]},
        ]
        self.tbl_iport_ls.extend(tmp_ls)

        aw = RegUtils.calc_tbl_aw(item_dict.get("depth"))
        tmp_ls = [
            {"direct": "output", "unit": "logic", "sig_name": f'o_reg_{item_dict.get("name")}_tbl_req', "dw": 1},
            {"direct": "output", "unit": "logic", "sig_name": f'o_reg_{item_dict.get("name")}_tbl_rw', "dw": 1},
            {"direct": "output", "unit": "logic", "sig_name": f'o_reg_{item_dict.get("name")}_tbl_addr', "aw": aw},
        ]
        self.tbl_oport_ls.extend(tmp_ls)
        if item_dict.get("tbl_rw_attr") == "rw":
            self.tbl_oport_ls.append(
                {"direct": "output", "unit": "logic", "sig_name": f'o_reg_{item_dict.get("name")}_tbl_wdata', "dw": item_dict["vld_bits"]},
            )

    def append_wreg_port_ls(self, item_dict: Dict) -> None:
        self.logger.debug("start function: append_wreg_port_ls")

        for depth_idx in range(item_dict.get("depth")):
            reg_int_status_flag = "int_status" in item_dict.get("name")
            reg_cif_err_cnt_flag = "cif_err_cnt" in item_dict.get("name")
            reg_cif_err_info_flag = "cif_err_info" in item_dict.get("name")
            reg_output_exclude_flag = bool(re.search(r"int_mask|int_set|car_ctrl", item_dict.get("name")))

            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)

            for field_dict in item_dict.get("subpart"):
                field_lgc_input_flag = field_dict.get("rw_attr") in ["rc", "rwc", "rww"]
                field_cnt_flag = field_dict.get("rw_attr") in ["sctr", "rctr"]
                field_cif_err_flag = "cif_err" in field_dict.get("field")

                tmp_input_sig = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}"
                tmp_output_sig = f"o_reg_{item_dict.get('name')}"

                if field_dict.get("field") != "rsv":
                    if field_dict.get("rw_attr") in self.config.input_sig_ls:
                        if reg_int_status_flag and (not field_cif_err_flag):
                            self.wreg_iport_ls.append(
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_set", "dw": 1},
                            )
                        elif (not reg_int_status_flag) and field_lgc_input_flag:
                            tmp_ls = [
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_wen", "dw": 1},
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_data", "dw": field_dict.get("bits")},
                            ]
                            self.wreg_iport_ls.extend(tmp_ls)
                        elif (not reg_int_status_flag) and field_cnt_flag and (not reg_cif_err_cnt_flag):
                            tmp_ls = [
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_en", "dw": 1},
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_num", "dw": field_dict.get("bits")},
                            ]
                            self.wreg_iport_ls.extend(tmp_ls)
                        elif field_dict.get("field") == "ro":
                            self.wreg_iport_ls.append(
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_data", "dw": item_dict.get("vld_bits")},
                            )
                        elif field_dict.get("field") in ["max", "min"]:
                            tmp_ls = [
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_vld", "dw": 1},
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_data", "dw": field_dict.get("vld_bits")},
                            ]
                            self.wreg_iport_ls.extend(tmp_ls)
                        elif (not reg_cif_err_info_flag) and (not reg_cif_err_cnt_flag):
                            self.wreg_iport_ls.append(
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}", "dw": field_dict.get("bits")},
                            )
                        else:
                            self.logger.error(
                                f"[Processor.append_wreg_port_ls] iport else triggered!(cif_err_info&cif_err_cnt not port decl)"
                            )

                        if (reg_int_status_flag and field_dict.get("rw_attr") == "rwc") or field_dict.get("rw_attr") == "rww":
                            self.wreg_oport_ls.append(
                                {"direct": "output", "unit": "logic", "sig_name": f"{tmp_output_sig}_{field_dict.get('field')}{idx}", "dw": field_dict.get("bits")},
                            )

                    elif field_dict.get("rw_attr") in self.config.output_sig_ls:
                        if not reg_output_exclude_flag:
                            self.wreg_oport_ls.append(
                                {"direct": "output", "unit": "logic", "sig_name": f"{tmp_output_sig}{idx}", "dw": field_dict.get("bits")},
                            )
                    else:
                        self.logger.error(
                            f"[Processor.append_wreg_port_ls] rw_attr should be in INPUT_SIG_LS/OUTPUT_SIG_LS, but now is {field_dict.get('rw_attr')}"
                        )

    def append_reg_port_ls(self, item_dict: Dict) -> None:
        self.logger.debug("start function: append_reg_port_ls")

        for depth_idx in range(item_dict.get("depth")):
            reg_int_status_flag = "int_status" in item_dict.get("name")
            reg_cif_err_cnt_flag = "cif_err_cnt" in item_dict.get("name")
            reg_cif_err_info_flag = "cif_err_info" in item_dict.get("name")
            reg_output_exclude_flag = bool(re.search(r"int_mask|int_set|car_ctrl", item_dict.get("name")))

            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)

            for field_dict in item_dict.get("subpart"):
                field_lgc_input_flag = field_dict.get("rw_attr") in ["rc", "rwc", "rww"]
                field_cnt_flag = field_dict.get("rw_attr") in ["sctr", "rctr"]
                field_cif_err_flag = "cif_err" in field_dict.get("field")

                tmp_input_sig = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}"
                tmp_output_sig = f"o_reg_{item_dict.get('name')}"

                if field_dict.get("field") != "rsv":
                    if field_dict.get("rw_attr") in self.config.input_sig_ls:
                        if reg_int_status_flag and (not field_cif_err_flag):
                            self.iport_ls.append(
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_set", "dw": 1},
                            )
                        elif reg_int_status_flag and field_cif_err_flag:
                            pass
                        elif (not reg_int_status_flag) and field_lgc_input_flag:
                            tmp_ls = [
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_wen", "dw": 1},
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_data", "dw": field_dict.get("bits")},
                            ]
                            self.iport_ls.extend(tmp_ls)
                        elif (not reg_int_status_flag) and field_cnt_flag and (not reg_cif_err_cnt_flag):
                            tmp_ls = [
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_en", "dw": 1},
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_num", "dw": field_dict.get("bits")},
                            ]
                            self.iport_ls.extend(tmp_ls)
                        elif field_dict.get("rw_attr") in ["max", "min"]:
                            self.iport_ls.append(
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}_data", "dw": item_dict.get("vld_bits")},
                            )
                        elif (not reg_cif_err_info_flag) and (not reg_cif_err_cnt_flag):
                            self.iport_ls.append(
                                {"direct": "input", "unit": "logic", "sig_name": f"{tmp_input_sig}", "dw": field_dict.get("bits")},
                            )
                        else:
                            self.logger.debug(
                                f"[Processor.append_reg_port_ls] reg_port else triggered! reg_name:{item_dict.get('name')} field_name:{field_dict.get('field')}((cif_err_info&cif_err_cnt not port decl))"
                            )

                        if (reg_int_status_flag and field_dict.get("rw_attr") == "rwc") or field_dict.get("rw_attr") == "rww":
                            self.oport_ls.append(
                                {"direct": "output", "unit": "logic", "sig_name": f"{tmp_output_sig}_{field_dict.get('field')}{idx}", "dw": field_dict.get("bits")},
                            )

                    elif field_dict.get("rw_attr") in self.config.output_sig_ls:
                        if not reg_output_exclude_flag:
                            self.oport_ls.append(
                                {"direct": "output", "unit": "logic", "sig_name": f"{tmp_output_sig}_{field_dict.get('field')}{idx}", "dw": field_dict.get("bits")},
                            )
                    else:
                        self.logger.error(
                            f"[Processor.append_reg_port_ls] rw_attr should be in INPUT_SIG_LS/OUTPUT_SIG_LS, but now is {field_dict.get('rw_attr')}"
                        )

    def get_port_ls(self) -> None:
        for reg_dict in self.extract_ls:
            if reg_dict["type"] == "tbl":
                self.append_tbl_port_ls(reg_dict)
            elif reg_dict["type"] == "wide_reg":
                self.append_wreg_port_ls(reg_dict)
            elif reg_dict["type"] == "reg":
                self.append_reg_port_ls(reg_dict)
            else:
                self.logger.error(
                    f"[function.get_port_ls] type should be tbl/reg/wide_reg, but now is {reg_dict['type']}"
                )
