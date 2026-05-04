class ProcRalSysBlock:
    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.top_name      = all_data_dict.get("top_name")
        self.render_ls = []

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            if "size" in bt_item and bt_item["size"] is not None:
                bt_item["size_hex"] = hex(bt_item["size"]).lstrip("0x")
            bt_item["baseaddr_hex"] = hex(bt_item["baseaddr"]).lstrip("0x")
            self.render_ls.append(bt_item)
