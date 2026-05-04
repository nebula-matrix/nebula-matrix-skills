from gen_reg_tools.core.data_model import Top
from gen_reg_tools.ral.extractor_adapter import top_to_dict
from gen_reg_tools.ral.processors.proc_block_intf import ProcBlockIntf
from gen_reg_tools.ral.processors.proc_ral_block import ProcRalBlock
from gen_reg_tools.ral.processors.proc_ral_mem import ProcRalMem
from gen_reg_tools.ral.processors.proc_ral_sys_block import ProcRalSysBlock
from gen_reg_tools.ral.processors.proc_reg import ProcReg
from gen_reg_tools.ral.processors.proc_vreg import ProcVreg
from gen_reg_tools.ral.processors.proc_reg_bkdr import ProcRegBkdr


class RalProcessor:

    def __init__(self, reg_data: Top):
        self.all_data_dict = top_to_dict(reg_data)
        self.top_name = reg_data.name

        self.proc_block_intf     = None
        self.proc_ral_block      = None
        self.proc_ral_mem        = None
        self.proc_ral_sys_block  = None
        self.proc_reg            = None
        self.proc_vreg           = None
        self.proc_reg_bkdr       = None

    def process(self):
        self.proc_block_intf        = ProcBlockIntf(all_data_dict=self.all_data_dict)
        self.proc_block_intf.process()

        self.proc_ral_block         = ProcRalBlock(all_data_dict=self.all_data_dict)
        self.proc_ral_block.process()

        self.proc_ral_mem           = ProcRalMem(all_data_dict=self.all_data_dict)
        self.proc_ral_mem.process()

        self.proc_ral_sys_block     = ProcRalSysBlock(all_data_dict=self.all_data_dict)
        self.proc_ral_sys_block.process()

        self.proc_reg               = ProcReg(all_data_dict=self.all_data_dict)
        self.proc_reg.process()

        self.proc_vreg              = ProcVreg(all_data_dict=self.all_data_dict)
        self.proc_vreg.process()

        self.proc_reg_bkdr          = ProcRegBkdr(all_data_dict=self.all_data_dict)
        self.proc_reg_bkdr.process()
