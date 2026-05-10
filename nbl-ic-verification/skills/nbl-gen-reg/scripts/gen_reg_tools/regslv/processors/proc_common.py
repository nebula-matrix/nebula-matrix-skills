from typing import List, Dict, Any

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcCommon:

    cls_max_dw = 0
    cls_max_name_length = 0

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any) -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.common_dict = {}

    def judge_wr_ctrl_snap(self, item_dict: Dict) -> None:
        for field_dict in item_dict.get("subpart"):
            if self.common_dict.get("have_wr_ctrl") != True and field_dict.get("have_wr_ctrl") not in ["", None]:
                self.common_dict["have_wr_ctrl"] = True
            if self.common_dict.get("have_snap") != True and field_dict.get("snapshot_en") not in ["", None]:
                self.common_dict["have_snap"] = True

    def tbl_align_process(self, item_dict: Dict) -> None:
        if len(str(item_dict.get("width"))) > ProcCommon.cls_max_dw:
            ProcCommon.cls_max_dw = len(str(item_dict.get("width")))

        if len(item_dict.get("name")) > ProcCommon.cls_max_name_length:
            ProcCommon.cls_max_name_length = len(item_dict.get("name"))

    def judge_tbl_cnt(self, item_dict: Dict) -> None:
        if self.common_dict.get("have_tbl") != True:
            self.common_dict["have_tbl"] = True
            self.common_dict["tbl_start_addr"] = RegUtils.int_to_hex(
                item_dict.get("offset_addr"), self.config.reg_aw
            )

    def wreg_align_process(self, item_dict: Dict) -> None:
        if len(str(item_dict.get("width"))) > ProcCommon.cls_max_dw:
            ProcCommon.cls_max_dw = len(str(item_dict.get("width")))

        for depth_idx in range(item_dict.get("depth")):
            for field_dict in item_dict.get("subpart"):
                if len(item_dict.get("name") + field_dict.get("field")) > ProcCommon.cls_max_name_length:
                    ProcCommon.cls_max_name_length = len(item_dict.get("name") + field_dict.get("field"))

    def judge_wreg_cnt(self, item_dict) -> None:
        if self.common_dict.get("have_wreg") != True:
            self.common_dict["have_wreg"] = True

    def reg_align_process(self, item_dict: Dict) -> None:
        if len(str(item_dict.get("width"))) > ProcCommon.cls_max_dw:
            ProcCommon.cls_max_dw = len(str(item_dict.get("width")))

        for depth_idx in range(item_dict.get("depth")):
            for field_dict in item_dict.get("subpart"):
                if len(item_dict.get("name") + field_dict.get("field")) > ProcCommon.cls_max_name_length:
                    ProcCommon.cls_max_name_length = len(item_dict.get("name") + field_dict.get("field"))

    def judge_interupt(self, item_dict: Dict) -> None:
        if self.common_dict.get("have_int") != True and "int_status" in item_dict.get("name"):
            self.common_dict["have_int"] = True

        for field_dict in item_dict.get("subpart"):
            if self.common_dict.get("have_cif_err_int") != True and "cif_err" in field_dict.get("field"):
                self.common_dict["have_cif_err_int"] = True
                self.common_dict["err_event"] = "inner_cif_err"
                self.common_dict["err_info"] = (
                    "{" + "cif_ucor_err, " + "cif_wr_err, "
                    + f"{str(30 - self.config.reg_aw)}'b0, "
                    + f"i_cif_{self.config.module_name}_addr"
                    + "}"
                )
                self.common_dict["int_state"] = f"{self.config.module_name}_int_status_cif_err"
                self.common_dict["reg_err_info"] = (
                    "{" + "cif_err_info_ucor_err, " + "cif_err_info_wr_err, " + "cif_err_info_addr" + "}"
                )
                break

    def get_common_dict(self) -> None:
        norm_reg_cnt = 0
        tbl_cnt = 0
        self.common_dict["fast_access"] = None
        self.common_dict["have_wreg"] = None
        self.common_dict["have_tbl"] = None
        self.common_dict["have_int"] = None
        self.common_dict["have_cif_err_int"] = None
        self.common_dict["have_wr_ctrl"] = None
        self.common_dict["have_snap"] = None

        for reg_dict in self.extract_ls:
            self.judge_wr_ctrl_snap(reg_dict)
            if reg_dict["type"] == "tbl":
                self.tbl_align_process(reg_dict)
                self.judge_tbl_cnt(reg_dict)
                tbl_cnt += 1
            elif reg_dict["type"] == "wide_reg":
                self.wreg_align_process(reg_dict)
                self.judge_wreg_cnt(reg_dict)
            elif reg_dict["type"] == "reg":
                self.reg_align_process(reg_dict)
                self.judge_interupt(reg_dict)
                norm_reg_cnt += reg_dict.get("depth")
            else:
                self.logger.error(
                    f"[function.get_common_dict] type should be tbl/reg/wide_reg, but now is {reg_dict['type']}"
                )

        self.common_dict["max_dw_len"] = ProcCommon.cls_max_dw + 2
        self.common_dict["max_name_len"] = ProcCommon.cls_max_name_length + 20
        self.common_dict["tbl_cnt"] = tbl_cnt
        self.common_dict["module_name"] = self.config.module_name

        if self.config.multi_ck:
            norm_reg_cnt = int((norm_reg_cnt + 2 - 1) / 2)
        self.common_dict["grp_cnt"] = int(
            (norm_reg_cnt + self.config.num_to_group - 1) / self.config.num_to_group
        )

        self.common_dict["reg_aw"] = self.config.reg_aw
        self.common_dict["reg_dw"] = self.config.reg_dw

        if self.config.reset_low_valid:
            self.common_dict["low_rst"] = True
            if self.config.sync_reset:
                self.common_dict["sync_rst"] = True
            else:
                self.common_dict["sync_rst"] = False
        else:
            self.common_dict["low_rst"] = False
            if self.config.sync_reset:
                self.common_dict["sync_rst"] = True
            else:
                self.common_dict["sync_rst"] = False

        self.common_dict["fast_access"] = self.config.fast_access
        self.common_dict["apb_intf_en"] = self.config.apb_intf_en
        self.common_dict["apn_intf_async"] = self.config.apb_intf_async

        self.common_dict["clk"] = self.config.clk
        self.common_dict["rst"] = self.config.rst
        self.common_dict["clk_ls"] = self.config.multi_ck_ls
        self.common_dict["multick"] = self.config.multi_ck
