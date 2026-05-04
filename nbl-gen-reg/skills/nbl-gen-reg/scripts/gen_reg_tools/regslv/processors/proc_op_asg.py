from typing import List, Dict, Any
import re
import os

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcOpAsg:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any) -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.op_assign_ls = []
        self.wreg_op_assign_ls = []
        self.tbl_op_assign_ls = []
        self.tbl_asg_dict = {}
        self.wreg_asg_dict = {}

    def append_tbl_op_asg_ls(self, item_dict) -> None:
        self.logger.debug(f"start ProcOpAsg append_tbl_op_asg_ls ")

    def append_wreg_op_asg_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcSigDecl append_wreg_decl_ls ")

        special_reg_flag = bool(re.search(r"int_mask|int_set|car_ctrl", item_dict.get("name")))

        for depth_idx in range(item_dict.get("depth")):
            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)
            for field_dict in item_dict.get("subpart"):
                if field_dict.get("rw_attr") in self.config.output_sig_ls and (not special_reg_flag) and field_dict.get("rw_attr") != "rwc":
                    self.wreg_op_assign_ls.append(
                        {"lhs_sig": f'o_reg_{item_dict.get("name")}{idx}', "rhs_sig": f'{item_dict.get("name")}{idx}'},
                    )

    def append_reg_op_asg_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcOpAsg append_reg_op_asg_ls ")

        special_reg_flag = bool(re.search(r"int_mask|int_set|car_ctrl", item_dict.get("name")))

        for depth_idx in range(item_dict.get("depth")):
            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)
            for field_dict in item_dict.get("subpart"):
                if field_dict.get("rw_attr") in self.config.output_sig_ls and field_dict.get("field") != "rsv" and (not special_reg_flag):
                    if field_dict.get("rw_attr") == "rwc" and "int_status" not in item_dict.get("name"):
                        pass
                    else:
                        self.op_assign_ls.append(
                            {"lhs_sig": f'o_reg_{item_dict.get("name")}_{field_dict.get("field")}{idx}', "rhs_sig": f'{item_dict.get("name")}_{field_dict.get("field")}{idx}'},
                        )

    def get_tbl_asg_dict(self, tbl_ls: List) -> None:
        tbl_ack_ls = []
        tbl_rdata_ls = []
        tbl_status_ls = []
        output_tbl_ls = []

        dw_ls = [tbl.get("vld_bits") for tbl in tbl_ls]
        max_dw, _ = RegUtils.calc_tbl_dw_entry(dw_ls)

        dp_ls = [tbl.get("depth") for tbl in tbl_ls]
        _, max_dp_aw = RegUtils.calc_tbl_dp_entry(dp_ls)

        for tbl_idx, tbl_dict in enumerate(tbl_ls, 0):
            dw_gap = max_dw - tbl_dict.get("vld_bits")

            if tbl_dict.get("tbl_rw_attr") == "rw":
                tbl_ack_ls.append(f"i_reg_{tbl_dict.get('name')}_tbl_ack")
                tbl_status_ls.append(f"i_reg_{tbl_dict.get('name')}_tbl_status")
                if dw_gap == 0:
                    tbl_rdata_ls.append(f"i_reg_{tbl_dict.get('name')}_tbl_rdata")
                else:
                    tbl_rdata_ls.append("{" + f"{dw_gap}'b0, i_reg_{tbl_dict.get('name')}_tbl_rdata" + "}")
            else:
                tbl_ack_ls.append(f"mid_r2w_{tbl_dict.get('name')}_tbl_ack")
                tbl_status_ls.append(f"mid_r2w_{tbl_dict.get('name')}_tbl_status")
                if dw_gap == 0:
                    tbl_rdata_ls.append(f"mid_r2w_{tbl_dict.get('name')}_tbl_rdata")
                else:
                    tbl_rdata_ls.append("{" + f"{dw_gap}'b0, mid_r2w_{tbl_dict.get('name')}_tbl_rdata" + "}")

            addr_start = tbl_idx * max_dp_aw
            addr_end = addr_start + RegUtils.clog2(tbl_dict.get("depth")) - 1
            wdata_start = tbl_idx * max_dw
            wdata_end = wdata_start + tbl_dict.get("vld_bits") - 1
            if tbl_dict.get("tbl_rw_attr") == "rw":
                output_tbl_ls.append({"lhs": f"o_reg_{tbl_dict.get('name')}_tbl_req", "rhs": f"o_{self.config.module_name}_tbl_req[{tbl_idx}]"})
                output_tbl_ls.append({"lhs": f"o_reg_{tbl_dict.get('name')}_tbl_rw", "rhs": f"o_{self.config.module_name}_tbl_rw[{tbl_idx}]"})
                output_tbl_ls.append({"lhs": f"o_reg_{tbl_dict.get('name')}_tbl_addr", "rhs": f"o_{self.config.module_name}_tbl_addr[{addr_end}:{addr_start}]"})
                output_tbl_ls.append({"lhs": f"o_reg_{tbl_dict.get('name')}_tbl_wdata", "rhs": f"o_{self.config.module_name}_tbl_wdata[{wdata_end}:{wdata_start}]"})
            else:
                output_tbl_ls.append({"lhs": f"mid_w2r_{tbl_dict.get('name')}_tbl_req", "rhs": f"o_{self.config.module_name}_tbl_req[{tbl_idx}]"})
                output_tbl_ls.append({"lhs": f"mid_w2r_{tbl_dict.get('name')}_tbl_rw", "rhs": f"o_{self.config.module_name}_tbl_rw[{tbl_idx}]"})
                output_tbl_ls.append({"lhs": f"mid_w2r_{tbl_dict.get('name')}_tbl_addr", "rhs": f"o_{self.config.module_name}_tbl_addr[{addr_end}:{addr_start}]"})
                output_tbl_ls.append({"lhs": f"mid_w2r_{tbl_dict.get('name')}_tbl_wdata", "rhs": f"o_{self.config.module_name}_tbl_wdata[{wdata_end}:{wdata_start}]"})

        tbl_ack_ls.reverse()
        tbl_rdata_ls.reverse()
        tbl_status_ls.reverse()

        self.tbl_asg_dict["tbl_ack_lhs"] = f"i_{self.config.module_name}_tbl_ack"
        self.tbl_asg_dict["tbl_rdata_lhs"] = f"i_{self.config.module_name}_tbl_rdata"
        self.tbl_asg_dict["tbl_status_lhs"] = f"i_{self.config.module_name}_tbl_status"
        self.tbl_asg_dict["tbl_ack_rhs"] = "{" + ", ".join(tbl_ack_ls) + "}"
        self.tbl_asg_dict["tbl_rdata_rhs"] = "{" + ", ".join(tbl_rdata_ls) + "}"
        self.tbl_asg_dict["tbl_status_rhs"] = "{" + ", ".join(tbl_status_ls) + "}"
        self.tbl_asg_dict["output_tbl_asg"] = output_tbl_ls

    def get_wreg_asg_dict(self, wreg_ls: List) -> None:
        rw_cnt = 0
        ro_cnt = 0
        sctr_cnt = 0
        rctr_cnt = 0

        rw_sent_ls = []
        ro_sig_ls = []
        sctr_inc_en_ls = []
        sctr_inc_num_ls = []
        rctr_inc_en_ls = []
        rctr_inc_num_ls = []

        dw_ls = [tbl.get("vld_bits") for tbl in wreg_ls]
        max_dw_a32, _ = RegUtils.calc_tbl_dw_entry(dw_ls)

        for item_dict in wreg_ls:
            depth = item_dict.get("depth")
            width = item_dict.get("width")
            aw = self.config.reg_aw
            for depth_idx in range(depth):
                if item_dict.get("depth") == 1:
                    idx = ""
                else:
                    idx = "_" + str(depth_idx)

                for field_dict in item_dict.get("subpart"):
                    dw_gap = max_dw_a32 - field_dict.get("bits")
                    if field_dict.get("field") == "rsv":
                        continue
                    if field_dict.get("rw_attr") == "rw":
                        start_addr = rw_cnt * max_dw_a32
                        end_addr = rw_cnt * max_dw_a32 + width - 1
                        start_addr_str = str(start_addr)
                        end_addr_str = str(end_addr)

                        rw_cnt += 1
                        rw_sent_ls.append(
                            {"lhs": f"{item_dict.get('name')}{idx}", "rhs": f"{self.config.module_name}_rw_wreg_data[{end_addr_str}:{start_addr_str}]"}
                        )
                    elif field_dict.get("rw_attr") == "ro":
                        ro_cnt += 1
                        if dw_gap == 0:
                            ro_sig_ls.append(f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}")
                        else:
                            ro_sig_ls.append("{" + f"{dw_gap}'b0, " + f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}" + "}")
                    elif field_dict.get("rw_attr") == "sctr":
                        sctr_cnt += 1
                        sctr_inc_en_ls.append(f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_en")
                        if dw_gap == 0:
                            sctr_inc_num_ls.append(f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_num")
                        else:
                            sctr_inc_num_ls.append("{" + f"{dw_gap}'b0, " + f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_num" + "}")
                    elif field_dict.get("rw_attr") == "rctr":
                        rctr_cnt += 1
                        rctr_inc_en_ls.append(f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_en")
                        if dw_gap == 0:
                            rctr_inc_num_ls.append(f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_num")
                        else:
                            rctr_inc_num_ls.append("{" + f"{dw_gap}'b0, " + f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_num" + "}")
                    else:
                        self.logger.error(
                            f"get_wreg_asg_dict rw_attr ERROR, now field_name:{field_dict.get('field')}, rw_attr:{field_dict.get('rw_attr')}"
                        )

        rw_sent_ls.reverse()
        ro_sig_ls.reverse()
        sctr_inc_en_ls.reverse()
        sctr_inc_num_ls.reverse()
        rctr_inc_en_ls.reverse()
        rctr_inc_num_ls.reverse()

        if ro_cnt == 0:
            ro_str = f"{max_dw_a32}'b0"
        else:
            ro_str = "{" + ", ".join(ro_sig_ls) + "}"

        if sctr_cnt == 0:
            sctr_inc_en_str = "1'b0"
            sctr_inc_num_str = f"{max_dw_a32}'b0"
        else:
            sctr_inc_en_str = "{" + ", ".join(sctr_inc_en_ls) + "}"
            sctr_inc_num_str = "{" + ", ".join(sctr_inc_num_ls) + "}"

        if rctr_cnt == 0:
            rctr_inc_en_str = "1'b0"
            rctr_inc_num_str = f"{max_dw_a32}'b0"
        else:
            rctr_inc_en_str = "{" + ", ".join(rctr_inc_en_ls) + "}"
            rctr_inc_num_str = "{" + ", ".join(rctr_inc_num_ls) + "}"

        self.wreg_asg_dict["rw_ls"] = rw_sent_ls
        self.wreg_asg_dict["ro_lhs"] = f"{self.config.module_name}_ro_wreg_data"
        self.wreg_asg_dict["ro_rhs"] = ro_str
        self.wreg_asg_dict["sctr_inc_en_lhs"] = f"{self.config.module_name}_sctr_inc_en"
        self.wreg_asg_dict["sctr_inc_en_rhs"] = sctr_inc_en_str
        self.wreg_asg_dict["sctr_inc_num_lhs"] = f"{self.config.module_name}_sctr_inc_num"
        self.wreg_asg_dict["sctr_inc_num_rhs"] = sctr_inc_num_str
        self.wreg_asg_dict["rctr_inc_en_lhs"] = f"{self.config.module_name}_rctr_inc_en"
        self.wreg_asg_dict["rctr_inc_en_rhs"] = rctr_inc_en_str
        self.wreg_asg_dict["rctr_inc_num_lhs"] = f"{self.config.module_name}_rctr_inc_num"
        self.wreg_asg_dict["rctr_inc_num_rhs"] = rctr_inc_num_str

    def get_op_asg_ls(self) -> None:
        tbl_ls = []
        wreg_ls = []
        reg_cif_err_info_flag = None
        reg_cif_err_cnt_flag = None

        for reg_dict in self.extract_ls:
            if reg_cif_err_info_flag != True and "cif_err_info" in reg_dict.get("name"):
                reg_cif_err_info_flag = True
            if reg_cif_err_cnt_flag != True and "cif_err_cnt" in reg_dict.get("name"):
                reg_cif_err_cnt_flag = True

            if reg_dict["type"] == "tbl":
                self.append_tbl_op_asg_ls(reg_dict)
                tbl_ls.append(reg_dict)
            elif reg_dict["type"] == "wide_reg":
                self.append_wreg_op_asg_ls(reg_dict)
                wreg_ls.append(reg_dict)
            elif reg_dict["type"] == "reg":
                self.append_reg_op_asg_ls(reg_dict)
            else:
                self.logger.error(
                    f"[function.get_op_asg_ls] type should be tbl/reg/wide_reg, but now is {reg_dict['type']}"
                )

        if len(tbl_ls) > 0:
            if (reg_cif_err_info_flag != True) or (reg_cif_err_cnt_flag != True):
                self.logger.error(f"When existing table, Excel must have cif_err_info/cif_err_cnt register")
                os.sys.exit(0)
            self.get_tbl_asg_dict(tbl_ls)
        else:
            if reg_cif_err_info_flag == True:
                self.tbl_asg_dict["cif_err_info_tie0"] = True
            if reg_cif_err_cnt_flag == True:
                self.tbl_asg_dict["cif_err_cnt_tie0"] = True

        if len(wreg_ls) > 0:
            self.get_wreg_asg_dict(wreg_ls)
