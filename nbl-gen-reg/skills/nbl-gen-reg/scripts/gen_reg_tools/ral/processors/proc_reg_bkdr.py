class ProcRegBkdr:
    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.top_name      = all_data_dict.get("top_name")
        self.render_ls     = []

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            self.render_ls.append(bt_item)
