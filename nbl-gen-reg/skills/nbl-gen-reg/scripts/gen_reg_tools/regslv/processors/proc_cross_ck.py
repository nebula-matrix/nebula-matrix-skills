from typing import List, Dict, Any

from gen_reg_tools.core.utils import RegUtils
from gen_reg_tools.regslv.config import RegSlvConfig


class ProcCrossCk:

    def __init__(self, extract_ls: List, config: RegSlvConfig, logger: Any) -> None:
        self.extract_ls = extract_ls
        self.config = config
        self.logger = logger
        self.cross_ck_dict = {}

    def get_cross_ck_decl(self) -> None:
        mdl_name = self.config.module_name
        ck0 = "_" + self.config.multi_ck_ls[0]
        ck1 = "_" + self.config.multi_ck_ls[-1]

        self.cross_ck_dict["cif_req"] = f"i_cif_{mdl_name}_req"
        self.cross_ck_dict["cif_rw"] = f"i_cif_{mdl_name}_rw"
        self.cross_ck_dict["cif_addr"] = f"i_cif_{mdl_name}_addr"
        self.cross_ck_dict["cif_wdata"] = f"i_cif_{mdl_name}_wdata"
        self.cross_ck_dict["cif_ack"] = f"o_{mdl_name}_cif_ack"
        self.cross_ck_dict["cif_rdata"] = f"o_{mdl_name}_cif_rdata"
        self.cross_ck_dict["ck0_req"] = f"i_cif_{mdl_name}{ck0}_req"
        self.cross_ck_dict["ck0_rw"] = f"i_cif_{mdl_name}{ck0}_rw"
        self.cross_ck_dict["ck0_addr"] = f"i_cif_{mdl_name}{ck0}_addr"
        self.cross_ck_dict["ck0_wdata"] = f"i_cif_{mdl_name}{ck0}_wdata"
        self.cross_ck_dict["ck0_ack"] = f"o_{mdl_name}{ck0}_cif_ack"
        self.cross_ck_dict["ck0_rdata"] = f"o_{mdl_name}{ck0}_cif_rdata"
        self.cross_ck_dict["ck1_req"] = f"i_cif_{mdl_name}{ck1}_req"
        self.cross_ck_dict["ck1_rw"] = f"i_cif_{mdl_name}{ck1}_rw"
        self.cross_ck_dict["ck1_addr"] = f"i_cif_{mdl_name}{ck1}_addr"
        self.cross_ck_dict["ck1_wdata"] = f"i_cif_{mdl_name}{ck1}_wdata"
        self.cross_ck_dict["ck1_ack"] = f"o_{mdl_name}{ck1}_cif_ack"
        self.cross_ck_dict["ck1_rdata"] = f"o_{mdl_name}{ck1}_cif_rdata"
        self.cross_ck_dict["mid_req"] = f"i_mid_cif_{mdl_name}{ck1}_req"
        self.cross_ck_dict["mid_rw"] = f"i_mid_cif_{mdl_name}{ck1}_rw"
        self.cross_ck_dict["mid_addr"] = f"i_mid_cif_{mdl_name}{ck1}_addr"
        self.cross_ck_dict["mid_wdata"] = f"i_mid_cif_{mdl_name}{ck1}_wdata"
        self.cross_ck_dict["mid_ack"] = f"o_mid_{mdl_name}{ck1}_cif_ack"
        self.cross_ck_dict["mid_rdata"] = f"o_mid_{mdl_name}{ck1}_cif_rdata"

        self.cross_ck_dict["max_len"] = len(self.cross_ck_dict["mid_rdata"])

    def get_cross_ck_inst(self) -> None:
        ck1 = self.config.multi_ck_ls[-1]
        for reg_dict in self.extract_ls:
            if reg_dict.get("clock_domain") == ck1:
                snd_ck_start_addr = reg_dict.get("offset_addr")
                break

        fst_ck_start_addr = 0
        fst_ck_end_addr = snd_ck_start_addr - 4
        snd_ck_end_addr = self.config.max_addr - 4

        self.cross_ck_dict["fst_ck_start_addr"] = f"{self.config.reg_aw}'h" + RegUtils.int_to_hex(fst_ck_start_addr, self.config.reg_aw)
        self.cross_ck_dict["fst_ck_end_addr"] = f"{self.config.reg_aw}'h" + RegUtils.int_to_hex(fst_ck_end_addr, self.config.reg_aw)
        self.cross_ck_dict["snd_ck_start_addr"] = f"{self.config.reg_aw}'h" + RegUtils.int_to_hex(snd_ck_start_addr, self.config.reg_aw)
        self.cross_ck_dict["snd_ck_end_addr"] = f"{self.config.reg_aw}'h" + RegUtils.int_to_hex(snd_ck_end_addr, self.config.reg_aw)

    def get_cross_ck_dict(self) -> None:
        self.get_cross_ck_decl()
        self.get_cross_ck_inst()
