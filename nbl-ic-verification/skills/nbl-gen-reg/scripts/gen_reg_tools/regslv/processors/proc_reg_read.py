from typing import List, Dict, Any

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcRegRead:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any, ck: str = "") -> None:
        self.ck = ck
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.rd_blk_ls = []

    def get_rd_blk_ls(self) -> None:
        self.logger.debug(f"start ProcRegRead get_rd_blk_ls ")

        group_num = self.config.num_to_group
        aw = self.config.reg_aw
        group_id = 0
        reg_idx = 0
        align_max_len = 0
        rd_blk_dict = {"case_opt_ls": []}

        for reg_dict in self.extract_ls:
            if reg_dict["type"] == "reg":
                for depth_idx in range(reg_dict.get("depth")):
                    if reg_dict.get("depth") == 1:
                        idx = ""
                    else:
                        idx = "_" + str(depth_idx)
                    reg_idx += 1
                    oft_addr = reg_dict.get("offset_addr") + 4 * depth_idx
                    oft_addr = f"{aw}'h" + str(RegUtils.int_to_hex(oft_addr, aw))
                    rhs_reg = f"{reg_dict.get('name')}{idx}_reg"
                    case_opt = f"{oft_addr}: begin norm_reg_hit{self.ck}[{group_id}] <= 1'b1; reg_rdata{self.ck}[{group_id}] <= {rhs_reg};"
                    rd_blk_dict["case_opt_ls"].append(case_opt)

                    align_max_len = len(case_opt) if len(case_opt) > align_max_len else align_max_len

                    rd_blk_dict["grp_id"] = group_id

                    if reg_idx % group_num == 0:
                        rd_blk_dict["default"] = f"default     : begin norm_reg_hit{self.ck}[{group_id}] <= 1'b0; reg_rdata{self.ck}[{group_id}] <= 32'h0;"
                        rd_blk_dict["align_max_len"] = align_max_len
                        self.rd_blk_ls.append(rd_blk_dict)
                        rd_blk_dict = {"case_opt_ls": []}
                        group_id += 1
                        reg_idx = 0

        if reg_idx > 0:
            rd_blk_dict["default"] = f"default     : begin norm_reg_hit{self.ck}[{group_id}] <= 1'b0; reg_rdata{self.ck}[{group_id}] <= 32'h0;"
            rd_blk_dict["align_max_len"] = align_max_len
            self.rd_blk_ls.append(rd_blk_dict)
            rd_blk_dict = {"case_opt_ls": []}
            group_id += 1
