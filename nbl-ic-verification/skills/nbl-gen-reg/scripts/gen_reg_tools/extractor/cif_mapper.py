import xlrd
from typing import Dict, Optional


class CifAddrMapper:
    """CIF 地址映射解析器（迁移自 CifAddrMapClass + Analysis_cif_addr）"""

    def __init__(self, path: str) -> None:
        self.path = path
        self.wb = xlrd.open_workbook(path)
        self.sheet = self.wb.sheet_by_name("地址映射 ")
        self.it_bt_map_dict: Dict[str, Dict] = {}
        self.m_addr_size_dict: Dict[str, Dict] = {}

    @staticmethod
    def addr_to_int(addr_str):
        """将地址字符串转为整数，支持 float/hex 格式"""
        if isinstance(addr_str, float):
            addr_str = str(addr_str)[:-2]  # float: 0.0 -> "0"
        if not isinstance(addr_str, str):
            addr_str = str(addr_str)
        if addr_str[:2] != "0x":
            addr_str = "0x" + addr_str
        return int(addr_str, 16)

    def _excel_data_to_str(self, cell) -> str:
        """将 Excel 单元格内容转为字符串"""
        error_str = ""
        if isinstance(cell, float):
            return str(int(cell))
        elif isinstance(cell, str):
            try:
                res_cell = cell.encode("ascii")
            except UnicodeEncodeError:
                return error_str
            if isinstance(res_cell, bytes):
                res_cell = res_cell.decode("utf-8")
            return res_cell
        else:
            return str(cell)

    def parse_map(self) -> Dict[str, Dict]:
        """解析 CIF 地址映射表，返回 {block_name: {...}} 结构"""
        block = ""
        start_line = 0
        base_addr_col = block_name_col = module_name_col = size_col = 0
        found_header = False

        for row in range(0, self.sheet.nrows):
            row_line = self.sheet.row_values(row)
            if "base_addr" in row_line:
                start_line = row
                base_addr_col = row_line.index("base_addr")
                block_name_col = row_line.index("block_name")
                module_name_col = row_line.index("module_name")
                size_col = row_line.index("size")
                found_header = True
                break

        if not found_header:
            raise ValueError("CIF address mapping sheet missing required headers")

        for row in range(start_line + 1, self.sheet.nrows):
            row_line = self.sheet.row_values(row)
            block_name = row_line[block_name_col]
            module_name = row_line[module_name_col]
            size = row_line[size_col]

            if block_name != "":
                block = block_name
                base_addr = self.addr_to_int(row_line[base_addr_col])
                self.it_bt_map_dict[block] = {
                    "block_name": block,
                    "base_addr": base_addr,
                    "size": size,
                    "mdl_part": [],
                }
            elif module_name != "":
                base_addr = self.addr_to_int(row_line[base_addr_col])
                self.it_bt_map_dict[block]["mdl_part"].append(
                    {
                        "module_name": module_name,
                        "base_addr": base_addr,
                        "size": size,
                    }
                )

        return self.it_bt_map_dict

    def _get_sheet_info(self) -> None:
        """读取各模块的基地址和大小（迁移自 Analysis_cif_addr.get_sheet_info）"""
        register_start = 0
        base_addr_idx = block_name_idx = module_name_idx = module_inst_name_idx = size_idx = 0

        for i in range(0, self.sheet.nrows):
            row_tmp = self.sheet.row_values(i)
            if register_start == 0:
                if "base_addr" in row_tmp:
                    try:
                        base_addr_idx = row_tmp.index("base_addr")
                        block_name_idx = row_tmp.index("block_name")
                        module_name_idx = row_tmp.index("module_name")
                        module_inst_name_idx = row_tmp.index("module_inst_name")
                        size_idx = row_tmp.index("size")
                        register_start = 1
                    except ValueError:
                        register_start = 0
                    continue
            else:
                base_addr = self._excel_data_to_str(
                    self.sheet.cell_value(i, base_addr_idx)
                ).strip()
                module_name = self._excel_data_to_str(
                    self.sheet.cell_value(i, module_name_idx)
                ).strip()
                size = self._excel_data_to_str(
                    self.sheet.cell_value(i, size_idx)
                ).strip()

                if module_name != "":
                    self.m_addr_size_dict[module_name] = {
                        "base_addr": base_addr,
                        "size": size,
                    }

    def _cal_eaddr(self, module_name: str) -> Optional[int]:
        """计算模块的结束地址（迁移自 Analysis_cif_addr.cal_eaddr）"""
        if module_name not in self.m_addr_size_dict:
            return None

        base_addr = self.m_addr_size_dict[module_name]["base_addr"]
        size = self.m_addr_size_dict[module_name]["size"]

        base_addr_int = int(base_addr, 16)
        size_int = int(size)

        eaddr_int = base_addr_int + size_int * 1024

        self.m_addr_size_dict[module_name]["eaddr_hex"] = hex(eaddr_int)
        self.m_addr_size_dict[module_name]["esize_int"] = size_int * 1024
        return eaddr_int

    def get_max_addr(self, module_name: str) -> Optional[int]:
        """获取模块的最大地址范围（esize_int）"""
        self._get_sheet_info()
        self._cal_eaddr(module_name)
        return self.m_addr_size_dict.get(module_name, {}).get("esize_int")

    def main(self) -> Dict[str, Dict]:
        self.parse_map()
        return self.it_bt_map_dict
