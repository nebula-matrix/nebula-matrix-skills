import math
import re
from typing import List, Tuple, Union


class RegUtils:
    """寄存器工具函数"""

    @staticmethod
    def concatenate_bits(number_ls: List[Tuple[int, int]]) -> int:
        """拼接多段 (width, value) 为单个整数"""
        result = 0
        for (width, value) in number_ls:
            if value < 0 or value >= 2**width:
                raise ValueError(f"concatenate_bits value({value}) input Error, width max_value({2**width - 1})")
            result <<= width
            result |= value
        return result

    @staticmethod
    def addr_to_int(addr_str: Union[str, int, float]) -> Union[int, str]:
        if addr_str == "":
            return addr_str
        if isinstance(addr_str, float):
            return int(addr_str)
        if isinstance(addr_str, int):
            return addr_str
        if isinstance(addr_str, str):
            addr_str = addr_str.strip()
            if addr_str[:2].lower() == "0x" or addr_str[:2] == "'h":
                return int(addr_str.replace("_", ""), 16)
            numbers = re.findall(r"(\d+)", addr_str)
            if numbers:
                return int(numbers[0])
        return addr_str

    @staticmethod
    def int_to_hex(addr: int, width: int = 25) -> str:
        hex_str = hex(addr)[2:]
        num_chars = math.ceil(width / 4)
        return hex_str.zfill(num_chars)

    @staticmethod
    def clog2(para: int) -> int:
        return 1 if para == 1 else math.ceil(math.log2(para))

    @staticmethod
    def calc_max_cnt(width: Union[int, float]) -> str:
        width = int(width)
        max_val = (1 << width) - 1
        return "'h" + hex(max_val)[2:]

    @staticmethod
    def calc_tbl_aw(depth: int) -> int:
        if depth < 3:
            return 0
        return int(math.ceil(math.log(depth, 2)) - 1)

    @staticmethod
    def calc_tbl_dp_entry(entry_dp_ls: List[int]):
        entry_dp_aw_ls = [RegUtils.clog2(dp) for dp in entry_dp_ls]
        entry_dp_aw_max = max(entry_dp_aw_ls)
        return entry_dp_aw_ls, entry_dp_aw_max

    @staticmethod
    def calc_tbl_dw_entry(entry_dw_ls: List[int]):
        if len(entry_dw_ls) == 0:
            return 32, 5
        max_entry_dw = max(entry_dw_ls)
        max_entry_dw = ((max_entry_dw + 31) // 32) * 32
        align_2n = RegUtils.clog2(max_entry_dw)
        return max_entry_dw, align_2n

    @staticmethod
    def calc_wreg_saddr(start_addr: str) -> str:
        return start_addr.replace("_", "")[2:]

    @staticmethod
    def calc_wreg_saddr_multi_depth(prev_end_addr: str) -> str:
        prev = int(prev_end_addr, 16)
        start = prev + 4
        return "0x" + f"{start:08x}"

    @staticmethod
    def calc_wreg_eaddr(start_addr: int, depth: int, width: int) -> int:
        return start_addr + ((width // 32) - 1) * 4

    @staticmethod
    def check_list(lst: List) -> bool:
        return any(str(item).strip() for item in lst)
