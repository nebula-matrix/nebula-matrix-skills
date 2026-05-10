import re
from gen_reg_tools.core.data_model import Top
from gen_reg_tools.checker.base import CheckResult


class NormalChecker:
    """提取结果常规检查器"""

    @staticmethod
    def check(data: Top) -> CheckResult:
        result = CheckResult()

        for block in data.subpart:
            addr_map = []
            reg_name_map = []
            tbl_num = 0
            car_ctrl_flag = False
            reg_cif_err_info_flag = False
            reg_cif_err_cnt_flag = False
            reg_car_ctrl_flag = False
            tbl_start_flag = False

            for reg in block.subpart:
                if reg.reg_type == "tbl" and not tbl_start_flag:
                    tbl_start_flag = True
                if reg.reg_type in ["reg", "wide_reg"] and tbl_start_flag:
                    result.add_error(
                        f"ERROR, module: {block.name} reg: {reg.name}, after tbl, sheet should not happen reg/wide_reg!"
                    )

                if reg.reg_type == "tbl":
                    tbl_num += 1
                    if reg.width > 1024:
                        result.add_error(
                            f"ERROR, module: {block.name} reg: {reg.name}, tbl width should be < 1024 !"
                        )

                if reg.reg_type == "wide_reg":
                    if not ((reg.width & (reg.width - 1)) == 0):
                        result.add_error(
                            f"ERROR, module: {block.name} reg: {reg.name}, wreg width should be 2^n !"
                        )

                if reg.offset_addr % 4 != 0:
                    result.add_error(
                        f"ERROR, module: {block.name} reg: {reg.name}, offset_addr should be multiple of 4 !"
                    )

                reg_all_bits = reg.width * reg.depth
                reg_addr_num = reg_all_bits // 32
                if reg_addr_num == 0:
                    reg_addr_num = 1

                addr_conflict = False
                for idx in range(reg_addr_num):
                    addr = reg.offset_addr + 4 * idx
                    if addr in addr_map:
                        addr_conflict = True
                    addr_map.append(addr)

                if addr_conflict:
                    result.add_error(
                        f"ERROR, module: {block.name} reg: {reg.name}, offset_addr should be different !"
                    )

                if reg.name in reg_name_map:
                    result.add_error(
                        f"ERROR, module: {block.name} reg: {reg.name}, reg_name should be different !"
                    )
                else:
                    reg_name_map.append(reg.name)

                all_field_bits = sum(f.bits for f in reg.subpart)
                if all_field_bits != reg.width:
                    result.add_error(
                        f"ERROR, module: {block.name} reg: {reg.name}, offset_addr: {hex(reg.offset_addr)}, "
                        f"reg_width({reg.width}) shoule be equal with all(field_bits)({all_field_bits})!"
                    )

                for f in reg.subpart:
                    if not re.match(r"[a-zA-Z0-9_]+$", f.name):
                        result.add_error(
                            f"ERROR, module: {block.name} reg: {reg.name}, offset_addr: {hex(reg.offset_addr)}, "
                            f"field({f.name}) shoule be [a-z][A-Z][0-9][-], illegal field name"
                        )

        return result
