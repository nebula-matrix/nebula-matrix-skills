from typing import List, Dict, Any
import re

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcInst:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any, ck: str = "") -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.ck = ck
        self.tbl_inst_dict = {}
        self.wreg_inst_dict = {}
        self.ro_tbl_inst_ls = []
        self.wreg_inst_ls = []
        self.inst_ls = []
        self.reg_idx = 0

    def append_ro_tbl_inst_ls(self, item_dict: Dict) -> None:
        if item_dict.get("tbl_rw_attr") != "rw":
            tmp_ro_inst_dict = {}
            reg_aw = self.config.reg_aw
            aw = RegUtils.calc_tbl_aw(item_dict.get("depth"))
            dw = item_dict.get("vld_bits")
            dp = item_dict.get("depth")

            tmp_ro_inst_dict["reg_name"] = item_dict.get("name")
            tmp_ro_inst_dict["oft_addr"] = f"{reg_aw}'h" + RegUtils.int_to_hex(item_dict.get("offset_addr"), self.config.reg_aw)
            tmp_ro_inst_dict["aw"] = aw
            tmp_ro_inst_dict["adw"] = RegUtils.clog2(dp)
            tmp_ro_inst_dict["dw"] = dw
            tmp_ro_inst_dict["rst"] = "xxxx"

            tmp_ro_inst_dict["req"] = f"mid_w2r_{item_dict.get('name')}_tbl_req"
            tmp_ro_inst_dict["rw"] = f"mid_w2r_{item_dict.get('name')}_tbl_rw"
            tmp_ro_inst_dict["offset_addr"] = f"mid_w2r_{item_dict.get('name')}_tbl_addr"
            tmp_ro_inst_dict["wdata"] = "{ " + f"{item_dict.get('vld_bits')}'b0" + "}"
            tmp_ro_inst_dict["ack"] = f"mid_r2w_{item_dict.get('name')}_tbl_ack"
            tmp_ro_inst_dict["rdata"] = f"mid_r2w_{item_dict.get('name')}_tbl_rdata"
            tmp_ro_inst_dict["status"] = f"mid_r2w_{item_dict.get('name')}_tbl_status"

            tmp_ro_inst_dict["ctrl_req"] = f"o_reg_{item_dict.get('name')}_tbl_req"
            tmp_ro_inst_dict["ctrl_rw"] = f"o_reg_{item_dict.get('name')}_tbl_rw"
            tmp_ro_inst_dict["ctrl_addr"] = f"o_reg_{item_dict.get('name')}_tbl_addr"
            tmp_ro_inst_dict["ctrl_wdata"] = ""
            tmp_ro_inst_dict["ctrl_ack"] = f"i_reg_{item_dict.get('name')}_tbl_ack"
            tmp_ro_inst_dict["ctrl_rdata"] = f"i_reg_{item_dict.get('name')}_tbl_rdata"
            tmp_ro_inst_dict["ctrl_status"] = f"i_reg_{item_dict.get('name')}_tbl_status"

            tmp_ro_inst_dict["ro_max_conn_len"] = len(item_dict.get("name")) + 20

            self.ro_tbl_inst_ls.append(tmp_ro_inst_dict)

    def append_inst_ls(self, item_dict: Dict) -> None:
        self.logger.debug(f"start ProcInst append_inst_ls ")

        for depth_idx in range(item_dict.get("depth")):
            if item_dict.get("depth") == 1:
                idx = ""
            else:
                idx = "_" + str(depth_idx)

            self.reg_idx += 1

            for field_dict in item_dict.get("subpart"):
                if field_dict.get("field") != "rsv":
                    if field_dict.get("wr_ctrl") == "y":
                        wr_ctrl = "i_wr_ctrl"
                    else:
                        wr_ctrl = "1'b0"

                    if field_dict.get("snapshot_en") == "y":
                        snapshot_trig = "i_snapshot_trig"
                        sshot_mode_en = "i_sshot_mode_en"
                    else:
                        snapshot_trig = "1'b0"
                        sshot_mode_en = "1'b0"

                    dw = field_dict.get("bits")
                    aw = self.config.reg_aw
                    def_val = field_dict.get("default_value")
                    def_val = f"{dw}'h" + RegUtils.int_to_hex(field_dict.get("default_value"), dw)
                    oft_addr = f"{aw}'h" + RegUtils.int_to_hex(item_dict.get("offset_addr") + 4 * depth_idx, aw)
                    max_cnt = RegUtils.calc_max_cnt(field_dict.get("bits"))
                    max_cnt = f"{field_dict.get('bits')}" + max_cnt

                    group_num = self.config.num_to_group
                    sig_idx = int(self.reg_idx / group_num)

                    data_lsb = field_dict.get("lsb")
                    data_msb = field_dict.get("lsb") + field_dict.get("bits") - 1

                    car_ctrl = f"{self.config.module_name}{self.ck}_car_ctrl_{field_dict.get('rw_attr')}_car"
                    i_ren = f"reg_ren{self.ck}[{sig_idx}]"
                    i_wen = f"reg_wen{self.ck}[{sig_idx}]"
                    i_addr = f"reg_addr{self.ck}[{sig_idx}]"
                    i_wdata = f"reg_wdata{self.ck}[{sig_idx}][{data_msb}:{data_lsb}]"
                    o_data = f"{item_dict.get('name')}_{field_dict.get('field')}{idx}"

                    i_inc_en = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_en"
                    i_inc_num = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_num"
                    o_cnt = f"{item_dict.get('name')}_{field_dict.get('field')}{idx}"
                    i_lgc_wen = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_wen"
                    i_lgc_data = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_data"
                    i_lgc_vld = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}_vld"

                    if field_dict.get("rw_attr") in ["sctr", "rctr"]:
                        if "cif_err_cnt" in item_dict.get("name"):
                            i_inc_en = "inner_cif_err"
                            i_inc_num = "32'd1"
                    elif field_dict.get("rw_attr") in ["rw", "wo"]:
                        if "cfg_test" in item_dict.get("name"):
                            i_wdata = "~" + i_wdata
                    elif field_dict.get("rw_attr") == "rc":
                        pass
                    elif field_dict.get("rw_attr") in ["rwc", "rww"]:
                        if "int_status" in item_dict.get("name"):
                            i_lgc_wen = f"set_{self.config.module_name}{self.ck}_int_{field_dict.get('field')}"
                            i_lgc_data = f"{field_dict.get('bits')}'b1"
                    elif field_dict.get("rw_attr") == "ro":
                        if "cif_err_info" not in item_dict.get("name"):
                            i_lgc_data = f"i_reg_{item_dict.get('name')}_{field_dict.get('field')}{idx}"
                        else:
                            i_lgc_data = f"cif_err_info_{field_dict.get('field')}{idx}{self.ck}"
                    elif field_dict.get("rw_attr") in ["min", "max"]:
                        pass
                    else:
                        self.logger.error(
                            f"reg.rw_attr exception happen, field:{field_dict.get('field')}, rw_attr: {field_dict.get('rw_attr')}"
                        )

                    max_param_len = max([len(str(item)) for item in [dw, aw, max_cnt, oft_addr, def_val]]) + 5
                    max_conn_len = max([len(str(item)) for item in [i_ren, i_wen, i_addr, o_data, i_inc_en, i_lgc_data, snapshot_trig, sshot_mode_en]]) + 5

                    self.inst_ls.append(
                        {
                            "reg_name": item_dict.get("name"),
                            "field": field_dict.get("field"),
                            "idx": idx,
                            "dw": dw,
                            "aw": aw,
                            "max_cnt": max_cnt,
                            "oft_addr": oft_addr,
                            "def_val": def_val,
                            "max_param_len": max_param_len,
                            "rw_attr": field_dict.get("rw_attr"),
                            "i_ren": i_ren,
                            "i_wen": i_wen,
                            "i_addr": i_addr,
                            "i_wdata": i_wdata,
                            "o_data": o_data,
                            "i_inc_en": i_inc_en,
                            "i_inc_num": i_inc_num,
                            "o_cnt": o_cnt,
                            "i_lgc_wen": i_lgc_wen,
                            "i_lgc_data": i_lgc_data,
                            "i_lgc_vld": i_lgc_vld,
                            "car_ctrl": car_ctrl,
                            "wr_ctrl": wr_ctrl,
                            "snapshot_trig": snapshot_trig,
                            "sshot_mode_en": sshot_mode_en,
                            "max_conn_len": max_conn_len,
                        }
                    )

    def get_tbl_inst_dict(self, tbl_ls: List) -> None:
        self.tbl_inst_dict["cah_num"] = self.config.cah_num
        self.tbl_inst_dict["aw"] = self.config.tbl_aw
        self.tbl_inst_dict["dw"] = self.config.tbl_dw
        self.tbl_inst_dict["tbl_num"] = len(tbl_ls)

        id_ls = [f"32'd{idx}" for idx in range(len(tbl_ls))]
        addr_ls = [f"{self.config.tbl_aw}'h{RegUtils.int_to_hex(tbl.get('offset_addr'), self.config.tbl_aw)}" for tbl in tbl_ls]
        dw_ls = [tbl.get("vld_bits") for tbl in tbl_ls]
        dp_ls = [tbl.get("depth") for tbl in tbl_ls]
        dp_aw_ls = []

        dp_aw_ls, self.tbl_inst_dict["tbl_max_dp_aw"] = RegUtils.calc_tbl_dp_entry(dp_ls)
        dp_aw_ls = [f"32'd{aw}" for aw in dp_aw_ls]
        self.tbl_inst_dict["tbl_max_dw_a32"], self.tbl_inst_dict["tbl_max_aw_a2n"] = RegUtils.calc_tbl_dw_entry(dw_ls)

        id_ls.reverse()
        addr_ls.reverse()
        dw_ls.reverse()
        dp_ls.reverse()
        dp_aw_ls.reverse()

        dw_ls = [f"32'd{item}" for item in dw_ls]
        dp_ls = [f"32'd{item}" for item in dp_ls]

        self.tbl_inst_dict["tbl_id"] = "{" + ", ".join(id_ls) + "}"
        self.tbl_inst_dict["tbl_baddr"] = "{" + ", ".join(addr_ls) + "}"
        self.tbl_inst_dict["tbl_entry_dw"] = "{" + ", ".join(dw_ls) + "}"
        self.tbl_inst_dict["tbl_dp"] = "{" + ", ".join(dp_ls) + "}"
        self.tbl_inst_dict["tbl_dp_aw"] = "{" + ", ".join(dp_aw_ls) + "}"

        str_len_ls = [
            len(item)
            for item in [
                self.tbl_inst_dict["tbl_id"],
                self.tbl_inst_dict["tbl_baddr"],
                self.tbl_inst_dict["tbl_entry_dw"],
                self.tbl_inst_dict["tbl_dp"],
                self.tbl_inst_dict["tbl_dp_aw"],
            ]
        ]
        self.tbl_inst_dict["param_max_len"] = max(str_len_ls) + 5

        wr_ctrl = "1'b0"
        for tbl in tbl_ls:
            if wr_ctrl == "i_wr_ctrl":
                break
            for field_dict in tbl.get("subpart"):
                if field_dict.get("wr_ctrl") == "y":
                    wr_ctrl = "i_wr_ctrl"
                    break

        self.tbl_inst_dict["cif_req"] = f"i_cif_{self.config.module_name}_req"
        self.tbl_inst_dict["cif_rw"] = f"i_cif_{self.config.module_name}_rw"
        self.tbl_inst_dict["cif_addr"] = f"i_cif_{self.config.module_name}_addr"
        self.tbl_inst_dict["cif_wdata"] = f"i_cif_{self.config.module_name}_wdata"
        self.tbl_inst_dict["wr_ctrl"] = wr_ctrl
        self.tbl_inst_dict["cif_ack"] = f"{self.config.module_name}_cif_ack"
        self.tbl_inst_dict["cif_rdata"] = f"{self.config.module_name}_cif_rdata"
        self.tbl_inst_dict["cif_acc_hit"] = f"{self.config.module_name}_access_hit"
        self.tbl_inst_dict["cif_ruerr"] = f"{self.config.module_name}_ucor_err"
        self.tbl_inst_dict["cif_werr"] = f"{self.config.module_name}_wr_err"
        self.tbl_inst_dict["tbl_req"] = f"o_{self.config.module_name}_tbl_req"
        self.tbl_inst_dict["tbl_rw"] = f"o_{self.config.module_name}_tbl_rw"
        self.tbl_inst_dict["tbl_addr"] = f"o_{self.config.module_name}_tbl_addr"
        self.tbl_inst_dict["tbl_wdata"] = f"o_{self.config.module_name}_tbl_wdata"
        self.tbl_inst_dict["tbl_ack"] = f"i_{self.config.module_name}_tbl_ack"
        self.tbl_inst_dict["tbl_rdata"] = f"i_{self.config.module_name}_tbl_rdata"
        self.tbl_inst_dict["tbl_status"] = f"i_{self.config.module_name}_tbl_status"

        self.tbl_inst_dict["max_conn_len"] = len(self.config.module_name) + 15

    def get_wreg_inst_dict(self, wreg_ls: List) -> None:
        rw_cnt = 0
        ro_cnt = 0
        sctr_cnt = 0
        rctr_cnt = 0

        rw_dict = {"cnt": None, "saddr_ls": [], "eaddr_ls": [], "dw": [], "def_val": [], "wr_ctrl": []}
        ro_dict = {"cnt": None, "saddr_ls": [], "eaddr_ls": [], "dw": [], "def_val": [], "wr_ctrl": []}
        sctr_dict = {"cnt": None, "saddr_ls": [], "eaddr_ls": [], "dw": [], "def_val": [], "wr_ctrl": [], "sshot_mode_en": []}
        rctr_dict = {"cnt": None, "saddr_ls": [], "eaddr_ls": [], "dw": [], "def_val": [], "wr_ctrl": [], "sshot_mode_en": []}

        dw_ls = [tbl.get("vld_bits") for tbl in wreg_ls]
        max_dw_a32, _ = RegUtils.calc_tbl_dw_entry(dw_ls)

        for item_dict in wreg_ls:
            depth = item_dict.get("depth")
            width = item_dict.get("width")
            aw = self.config.reg_aw

            for depth_idx in range(depth):
                if depth_idx == 0:
                    start_addr = item_dict.get("offset_addr")
                else:
                    start_addr = end_addr + 4
                end_addr = RegUtils.calc_wreg_eaddr(start_addr, 1, width)
                dw = "32'd" + str(item_dict.get("vld_bits"))
                start_addr_str = f"{aw}'h" + RegUtils.int_to_hex(start_addr, aw)
                end_addr_str = f"{aw}'h" + RegUtils.int_to_hex(end_addr, aw)
                for field_dict in item_dict.get("subpart"):
                    def_val = f"{max_dw_a32}'h" + RegUtils.int_to_hex(field_dict.get("default_value"), max_dw_a32)
                    wr_ctrl = "i_wr_ctrl" if field_dict.get("wr_ctrl") == "y" else "1'b0"
                    sshot_mode_en = "i_sshot_mode_en" if field_dict.get("snapshot_en") == "y" else "1'b0"
                    if field_dict.get("field") == "rsv":
                        continue
                    if field_dict.get("rw_attr") == "rw":
                        rw_cnt += 1
                        rw_dict["saddr_ls"].append(start_addr_str)
                        rw_dict["eaddr_ls"].append(end_addr_str)
                        rw_dict["dw"].append(dw)
                        rw_dict["def_val"].append(def_val)
                        rw_dict["wr_ctrl"].append(wr_ctrl)
                    elif field_dict.get("rw_attr") == "ro":
                        ro_cnt += 1
                        ro_dict["saddr_ls"].append(start_addr_str)
                        ro_dict["eaddr_ls"].append(end_addr_str)
                        ro_dict["dw"].append(dw)
                        ro_dict["def_val"].append(def_val)
                        ro_dict["wr_ctrl"].append(wr_ctrl)
                    elif field_dict.get("rw_attr") == "sctr":
                        sctr_cnt += 1
                        sctr_dict["saddr_ls"].append(start_addr_str)
                        sctr_dict["eaddr_ls"].append(end_addr_str)
                        sctr_dict["dw"].append(dw)
                        sctr_dict["def_val"].append(def_val)
                        sctr_dict["wr_ctrl"].append(wr_ctrl)
                        sctr_dict["sshot_mode_en"].append(sshot_mode_en)
                    elif field_dict.get("rw_attr") == "rctr":
                        rctr_cnt += 1
                        rctr_dict["saddr_ls"].append(start_addr_str)
                        rctr_dict["eaddr_ls"].append(end_addr_str)
                        rctr_dict["dw"].append(dw)
                        rctr_dict["def_val"].append(def_val)
                        rctr_dict["wr_ctrl"].append(wr_ctrl)
                        rctr_dict["sshot_mode_en"].append(sshot_mode_en)
                    else:
                        self.logger.error(
                            f"get_wreg_inst_dict rw_attr ERROR, now field_name:{field_dict.get('field')}, rw_attr:{field_dict.get('rw_attr')}"
                        )

        rw_dict["cnt"] = rw_cnt
        ro_dict["cnt"] = ro_cnt
        sctr_dict["cnt"] = sctr_cnt
        rctr_dict["cnt"] = rctr_cnt

        if sctr_cnt == 0:
            sctr_dict["sshot_mode_en"].append("1'b0")
        if rctr_cnt == 0:
            rctr_dict["sshot_mode_en"].append("1'b0")

        rw_dict["saddr_ls"].reverse()
        ro_dict["saddr_ls"].reverse()
        sctr_dict["saddr_ls"].reverse()
        rctr_dict["saddr_ls"].reverse()

        rw_dict["eaddr_ls"].reverse()
        ro_dict["eaddr_ls"].reverse()
        sctr_dict["eaddr_ls"].reverse()
        rctr_dict["eaddr_ls"].reverse()

        rw_dict["dw"].reverse()
        ro_dict["dw"].reverse()
        sctr_dict["dw"].reverse()
        rctr_dict["dw"].reverse()

        rw_dict["def_val"].reverse()
        ro_dict["def_val"].reverse()
        sctr_dict["def_val"].reverse()
        rctr_dict["def_val"].reverse()

        rw_dict["wr_ctrl"].reverse()
        ro_dict["wr_ctrl"].reverse()
        sctr_dict["wr_ctrl"].reverse()
        rctr_dict["wr_ctrl"].reverse()

        sctr_dict["sshot_mode_en"].reverse()
        rctr_dict["sshot_mode_en"].reverse()

        saddr_ls = rctr_dict["saddr_ls"] + sctr_dict["saddr_ls"] + ro_dict["saddr_ls"] + rw_dict["saddr_ls"]
        eaddr_ls = rctr_dict["eaddr_ls"] + sctr_dict["eaddr_ls"] + ro_dict["eaddr_ls"] + rw_dict["eaddr_ls"]
        dw_ls = rctr_dict["dw"] + sctr_dict["dw"] + ro_dict["dw"] + rw_dict["dw"]
        def_val_ls = rctr_dict["def_val"] + sctr_dict["def_val"] + ro_dict["def_val"] + rw_dict["def_val"]
        rw_ctrl_ls = rctr_dict["wr_ctrl"] + sctr_dict["wr_ctrl"] + ro_dict["wr_ctrl"] + rw_dict["wr_ctrl"]
        sctr_snap_ls = sctr_dict["sshot_mode_en"]
        rctr_snap_ls = rctr_dict["sshot_mode_en"]

        saddr_str = "{" + ", ".join(saddr_ls) + "}"
        eaddr_str = "{" + ", ".join(eaddr_ls) + "}"
        dw_str = "{" + ", ".join(dw_ls) + "}"
        def_val_str = "{" + ", ".join(def_val_ls) + "}"
        rw_ctrl_str = "{" + ", ".join(rw_ctrl_ls) + "}"
        sctr_snap_str = "{" + ", ".join(sctr_snap_ls) + "}"
        rctr_snap_str = "{" + ", ".join(rctr_snap_ls) + "}"

        self.wreg_inst_dict["aw"] = self.config.reg_aw
        self.wreg_inst_dict["dw"] = self.config.reg_dw
        self.wreg_inst_dict["pf"] = self.config.pf_num
        self.wreg_inst_dict["rw_num"] = rw_dict["cnt"]
        self.wreg_inst_dict["ro_num"] = ro_dict["cnt"]
        self.wreg_inst_dict["sctr_num"] = sctr_dict["cnt"]
        self.wreg_inst_dict["rctr_num"] = rctr_dict["cnt"]
        self.wreg_inst_dict["baddr"] = saddr_str
        self.wreg_inst_dict["eaddr"] = eaddr_str
        self.wreg_inst_dict["wreg_dw"] = dw_str
        self.wreg_inst_dict["def_val"] = def_val_str
        self.wreg_inst_dict["max_dw_a32"] = max_dw_a32

        wreg_param_len_ls = [len(item) for item in [saddr_str, eaddr_str, dw_str, def_val_str]]
        self.wreg_inst_dict["wreg_param_max_len"] = max(wreg_param_len_ls) + 5

        self.wreg_inst_dict["cif_req"] = f"i_cif_{self.config.module_name}_req"
        self.wreg_inst_dict["cif_rw"] = f"i_cif_{self.config.module_name}_rw"
        self.wreg_inst_dict["cif_addr"] = f"i_cif_{self.config.module_name}_addr"
        self.wreg_inst_dict["cif_wdata"] = f"i_cif_{self.config.module_name}_wdata"
        self.wreg_inst_dict["wr_ctrl"] = rw_ctrl_str
        self.wreg_inst_dict["rctr_car"] = f"{self.config.module_name}_car_ctrl_rctr_car"
        self.wreg_inst_dict["sctr_car"] = f"{self.config.module_name}_car_ctrl_sctr_car"
        self.wreg_inst_dict["cif_ack"] = "wide_reg_ack"
        self.wreg_inst_dict["cif_rdata"] = "wide_reg_rdata"
        self.wreg_inst_dict["rw_data"] = f"{self.config.module_name}_rw_wreg_data"
        self.wreg_inst_dict["ro_data"] = f"{self.config.module_name}_ro_wreg_data"
        self.wreg_inst_dict["sctr_inc_en"] = f"{self.config.module_name}_sctr_inc_en"
        self.wreg_inst_dict["sctr_inc_num"] = f"{self.config.module_name}_sctr_inc_num"
        self.wreg_inst_dict["sctr_snap"] = sctr_snap_str
        self.wreg_inst_dict["rctr_inc_en"] = f"{self.config.module_name}_rctr_inc_en"
        self.wreg_inst_dict["rctr_inc_num"] = f"{self.config.module_name}_rctr_inc_num"
        self.wreg_inst_dict["rctr_snap"] = rctr_snap_str

        self.wreg_inst_dict["wreg_nor_max_len"] = len(self.config.module_name) + 20
        self.wreg_inst_dict["wreg_ls_max_len"] = max([len(rw_ctrl_str), len(sctr_snap_str), len(rctr_snap_str)])

    def get_inst_ls(self) -> None:
        tbl_ls = []
        wreg_ls = []

        for reg_dict in self.extract_ls:
            if reg_dict["type"] == "tbl":
                self.append_ro_tbl_inst_ls(reg_dict)
                tbl_ls.append(reg_dict)
            elif reg_dict["type"] == "wide_reg":
                wreg_ls.append(reg_dict)
            elif reg_dict["type"] == "reg":
                self.append_inst_ls(reg_dict)
            else:
                self.logger.error(
                    f"[function.get_inst_ls] type should be tbl/reg/wide_reg, but now is {reg_dict['type']}"
                )

        if len(tbl_ls) > 0:
            self.get_tbl_inst_dict(tbl_ls)

        if len(wreg_ls) > 0:
            self.get_wreg_inst_dict(wreg_ls)
