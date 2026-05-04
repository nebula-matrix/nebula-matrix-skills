from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RegSlvConfig:
    sync_reset: bool = True
    reset_low_valid: bool = True
    fast_access: bool = False
    apb_intf_en: bool = False
    apb_intf_async: bool = False
    module_name: str = ""
    multi_ck: bool = False
    multi_ck_ls: List[str] = field(default_factory=list)

    # Address / data width constants
    reg_aw: int = 25
    reg_dw: int = 32
    num_to_group: int = 64

    # Clock / reset
    clk: str = "i_clk"
    rst: str = ""

    # Address space
    max_addr: Optional[int] = None

    # Table / wide_reg constants
    cah_num: int = 4
    pf_num: int = 4
    tbl_aw: int = 25
    tbl_dw: int = 32

    # Signal direction lists
    input_sig_ls: List[str] = field(
        default_factory=lambda: ["rwc", "rww", "ro", "sctr", "rctr", "rc", "min", "max"]
    )
    output_sig_ls: List[str] = field(
        default_factory=lambda: ["rw", "wo", "rwc", "rww"]
    )

    def __post_init__(self):
        if not self.rst:
            self.rst = "i_rst_n" if self.reset_low_valid else "i_rst"
        if self.max_addr is None:
            self.max_addr = 1 << self.reg_aw
