from gen_reg_tools.core.utils import RegUtils


class ProcRalMem:
    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.render_ls     = []

    def __get_tbl_reset(self, tbl_dict):
        number_ls = []
        for field_dict in tbl_dict.get("subpart", []):
            number_ls.append((field_dict.get("bits"), field_dict.get("default_value")))
        reset = RegUtils.concatenate_bits(number_ls)
        return str(hex(reset))[2:]

    def __get_tbl_rmask(self, tbl_dict):
        number_ls = []
        for field_dict in tbl_dict.get("subpart", []):
            w = field_dict.get("bits")
            number_ls.append((w, 2**w - 1))
        rmask = RegUtils.concatenate_bits(number_ls)
        return str(hex(rmask))[2:]

    def __get_tbl_wmask(self, tbl_dict):
        number_ls = []
        for field_dict in tbl_dict.get("subpart", []):
            w = field_dict.get("bits")
            if field_dict["rw_attr"] in ["ro"]:
                number_ls.append((w, 0))
            else:
                number_ls.append((w, 2**w - 1))
        wmask = RegUtils.concatenate_bits(number_ls)
        return str(hex(wmask))[2:]

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            bt_name = bt_item["name"]
            for dict_item in bt_item.get("subpart", []):
                if dict_item["type"] == "tbl":
                    dict_item["bn"]    = bt_name
                    dict_item["reset"] = self.__get_tbl_reset(dict_item)
                    dict_item["rmask"] = self.__get_tbl_rmask(dict_item)
                    dict_item["wmask"] = self.__get_tbl_wmask(dict_item)
                    self.render_ls.append(dict_item)
