from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

from gen_reg_tools.core.data_model import Block
from gen_reg_tools.regslv.config import RegSlvConfig
from gen_reg_tools.regslv.extractor_adapter import block_to_dict_list, block_to_domain_dict_lists

from gen_reg_tools.regslv.processors.proc_common import ProcCommon
from gen_reg_tools.regslv.processors.proc_header import ProcHeader
from gen_reg_tools.regslv.processors.proc_port import ProcPort
from gen_reg_tools.regslv.processors.proc_sig_decl import ProcSigDecl
from gen_reg_tools.regslv.processors.proc_op_asg import ProcOpAsg
from gen_reg_tools.regslv.processors.proc_reg_asg import ProcRegAsg
from gen_reg_tools.regslv.processors.proc_setint import ProcSetInt
from gen_reg_tools.regslv.processors.proc_inst import ProcInst
from gen_reg_tools.regslv.processors.proc_reg_read import ProcRegRead
from gen_reg_tools.regslv.processors.proc_cross_ck import ProcCrossCk


class RegProcessor:

    def __init__(self, block: Block, config: RegSlvConfig, logger: Any) -> None:
        self.block = block
        self.config = config
        self.logger = logger
        self.all_data_ls = block_to_dict_list(block)

        self.proc_common = None
        self.proc_header = None
        self.proc_port = None
        self.proc_cross_ck = None

        self.proc_decl = None
        self.proc_op_asg = None
        self.proc_reg_asg = None
        self.proc_setint = None
        self.proc_inst = None
        self.proc_rd_blk = None

    @staticmethod
    def _inst_and_calls(cls, method, *cls_args) -> Any:
        obj = cls(*cls_args)
        method = getattr(obj, method)
        method()
        return obj

    def proc_single_ck(self) -> None:
        with ThreadPoolExecutor(max_workers=9) as executor:
            processor_common = executor.submit(self._inst_and_calls, ProcCommon, "get_common_dict", self.all_data_ls, self.config, self.logger)
            processor_header = executor.submit(self._inst_and_calls, ProcHeader, "get_header_dict", self.config, self.logger)
            processor_port = executor.submit(self._inst_and_calls, ProcPort, "get_port_ls", self.all_data_ls, self.config, self.logger)
            processor_sig_decl = executor.submit(self._inst_and_calls, ProcSigDecl, "get_sig_decl_ls", self.all_data_ls, self.config, self.logger)
            processor_op_asg = executor.submit(self._inst_and_calls, ProcOpAsg, "get_op_asg_ls", self.all_data_ls, self.config, self.logger)
            processor_reg_asg = executor.submit(self._inst_and_calls, ProcRegAsg, "get_reg_asg_ls", self.all_data_ls, self.config, self.logger)
            processor_setint = executor.submit(self._inst_and_calls, ProcSetInt, "get_setint_ls", self.all_data_ls, self.config, self.logger)
            processor_inst = executor.submit(self._inst_and_calls, ProcInst, "get_inst_ls", self.all_data_ls, self.config, self.logger)
            processor_reg_rdata = executor.submit(self._inst_and_calls, ProcRegRead, "get_rd_blk_ls", self.all_data_ls, self.config, self.logger)

        self.proc_common = processor_common.result()
        self.proc_header = processor_header.result()
        self.proc_port = processor_port.result()
        self.proc_decl = processor_sig_decl.result()
        self.proc_op_asg = processor_op_asg.result()
        self.proc_reg_asg = processor_reg_asg.result()
        self.proc_setint = processor_setint.result()
        self.proc_inst = processor_inst.result()
        self.proc_rd_blk = processor_reg_rdata.result()

    def proc_multi_ck(self) -> None:
        domain_data_ls = block_to_domain_dict_lists(self.block)
        ckp_ls = ["_" + ck for ck in self.config.multi_ck_ls]

        with ThreadPoolExecutor(max_workers=9) as executor:
            processor_common = executor.submit(self._inst_and_calls, ProcCommon, "get_common_dict", self.all_data_ls, self.config, self.logger)
            processor_header = executor.submit(self._inst_and_calls, ProcHeader, "get_header_dict", self.config, self.logger)
            processor_port = executor.submit(self._inst_and_calls, ProcPort, "get_port_ls", self.all_data_ls, self.config, self.logger)
            processor_cross_ck = executor.submit(self._inst_and_calls, ProcCrossCk, "get_cross_ck_dict", self.all_data_ls, self.config, self.logger)
            processor_sig_decl_0 = executor.submit(self._inst_and_calls, ProcSigDecl, "get_sig_decl_ls", domain_data_ls[0], self.config, self.logger, ckp_ls[0])
            processor_sig_decl_1 = executor.submit(self._inst_and_calls, ProcSigDecl, "get_sig_decl_ls", domain_data_ls[1], self.config, self.logger, ckp_ls[1])
            processor_op_asg_0 = executor.submit(self._inst_and_calls, ProcOpAsg, "get_op_asg_ls", domain_data_ls[0], self.config, self.logger)
            processor_op_asg_1 = executor.submit(self._inst_and_calls, ProcOpAsg, "get_op_asg_ls", domain_data_ls[1], self.config, self.logger)
            processor_reg_asg_0 = executor.submit(self._inst_and_calls, ProcRegAsg, "get_reg_asg_ls", domain_data_ls[0], self.config, self.logger)
            processor_reg_asg_1 = executor.submit(self._inst_and_calls, ProcRegAsg, "get_reg_asg_ls", domain_data_ls[1], self.config, self.logger)
            processor_setint_0 = executor.submit(self._inst_and_calls, ProcSetInt, "get_setint_ls", domain_data_ls[0], self.config, self.logger, ckp_ls[0])
            processor_setint_1 = executor.submit(self._inst_and_calls, ProcSetInt, "get_setint_ls", domain_data_ls[1], self.config, self.logger, ckp_ls[1])
            processor_inst_0 = executor.submit(self._inst_and_calls, ProcInst, "get_inst_ls", domain_data_ls[0], self.config, self.logger, ckp_ls[0])
            processor_inst_1 = executor.submit(self._inst_and_calls, ProcInst, "get_inst_ls", domain_data_ls[1], self.config, self.logger, ckp_ls[1])
            processor_reg_rd_0 = executor.submit(self._inst_and_calls, ProcRegRead, "get_rd_blk_ls", domain_data_ls[0], self.config, self.logger, ckp_ls[0])
            processor_reg_rd_1 = executor.submit(self._inst_and_calls, ProcRegRead, "get_rd_blk_ls", domain_data_ls[1], self.config, self.logger, ckp_ls[1])

        self.proc_common = processor_common.result()
        self.proc_header = processor_header.result()
        self.proc_port = processor_port.result()
        self.proc_cross_ck = processor_cross_ck.result()
        self.proc_decl = [processor_sig_decl_0.result(), processor_sig_decl_1.result()]
        self.proc_op_asg = [processor_op_asg_0.result(), processor_op_asg_1.result()]
        self.proc_reg_asg = [processor_reg_asg_0.result(), processor_reg_asg_1.result()]
        self.proc_setint = [processor_setint_0.result(), processor_setint_1.result()]
        self.proc_inst = [processor_inst_0.result(), processor_inst_1.result()]
        self.proc_rd_blk = [processor_reg_rd_0.result(), processor_reg_rd_1.result()]

    def process(self) -> None:
        if self.config.multi_ck and len(self.config.multi_ck_ls) > 1:
            self.proc_multi_ck()
        else:
            self.proc_single_ck()
