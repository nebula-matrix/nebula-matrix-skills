class ProcRalBlock:
    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.render_ls   = []

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            for reg in bt_item.get("subpart", []):
                offset_addr = reg["offset_addr"]
                reg["offset_addr"] = hex(offset_addr).lstrip("0x")
                reg["byte_width"] = int(reg["width"] / 8)
                reg["depth_dec"] = int(reg["depth"])
                field_len_rm_rsv_lsb = len(reg["subpart"])
                for field in reversed(reg["subpart"]):
                    if field["field"] == "rsv":
                        field_len_rm_rsv_lsb = field_len_rm_rsv_lsb - 1
                    else:
                        break
                reg["field_len_rm_rsv_lsb"] = field_len_rm_rsv_lsb
            self.render_ls.append(bt_item)
