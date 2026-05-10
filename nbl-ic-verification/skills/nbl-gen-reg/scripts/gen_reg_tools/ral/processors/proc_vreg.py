import math


class ProcVreg:
    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.render_ls     = []

    def __get_tbl_nbits(self, bt_dict):
        nbits = 0
        for field_dict in bt_dict.get("subpart", []):
            if field_dict["name"] != "rsv":
                nbits += field_dict["bits"]
        nbits = ((nbits + 7) // 8) * 8
        return nbits

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            bt_name = bt_item["name"]
            for dict_item in bt_item.get("subpart", []):
                if dict_item["type"] == "tbl":
                    dict_item["bn"]    = bt_name
                    dict_item["nbits"] = self.__get_tbl_nbits(dict_item)
                    self.render_ls.append(dict_item)
