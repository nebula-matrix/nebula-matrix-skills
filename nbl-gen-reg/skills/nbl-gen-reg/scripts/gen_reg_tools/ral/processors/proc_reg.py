import math
import re
import sys


class ProcReg:

    def __init__(self, all_data_dict):
        self.all_data_dict = all_data_dict
        self.render_ls = []
        self.fcov_pattern0  = r'(!?)\s*\[\s*([\da-zA-Z]*)\s*(:?)\s*([\da-zA-Z]*)\s*\]\s*(/?)\s*(\d*)(\+?)'
        self.fcov_pattern1  = r'{(.*)}'

    def process(self):
        for bt_item in self.all_data_dict.get("subpart", []):
            for reg in bt_item.get("subpart", []):
                reg["width_vld"] = reg["width"]
                if reg["type"] == "tbl" or reg["type"] == "table":
                    depth = reg["depth"]
                    reg["depth"] = hex(depth).lstrip("0x")
                for field in reg.get("subpart", []):
                    field["max_val"] = int(2**field["bits"] - 1)
                    self.fcov_parse(reg["name"], field["name"], field)
                    self.gen_bins(reg["name"], field["name"], field)
                    if field["default_value"] == 0:
                        field["default_value_hex"] = 0
                    else:
                        field["default_value_hex"] = hex(field["default_value"]).lstrip("0x")
                    field["field"] = field["field"].lstrip("|")
                    if field["field"] == "rsv":
                        reg["width_vld"] = reg["width_vld"] - field["bits"]
                    else:
                        field["fcov_max"] = hex(2**field["bits"] - 1).lstrip("0x")
                        field["fcov_max-1"] = hex(2**field["bits"] - 2).lstrip("0x")
                        if field["rw_attr"] == "rw":
                            reg["tbl_rw_attr"] = "rw"
                        else:
                            reg["tbl_rw_attr"] = "ro"
                reg["tbl_data_width"] = hex(2**reg["width_vld"] - 1).lstrip("0x")
                reg["tbl_nbits"] = math.ceil(reg["width_vld"] / 8) * 8
            self.render_ls.append(bt_item)

    def fcov_parse(self, reg_name, field_name, field):

        field["black"]      = []
        field["white"]      = []
        field["white_num"]  = []
        field["brace"]      = []

        fcov = field.get("fcov", "")
        if fcov == "":
            field["white"].append((0, int(field["max_val"])))
            if int(field["max_val"]) == 1:
                field["white_num"].append(int(2))
            else:
                field["white_num"].append(-int(1))
        else:
            fcov_list_old = fcov.split(';')
            fcov_list = [item for item in fcov_list_old if item]
            for idx, f in enumerate(fcov_list):
                if re.search(self.fcov_pattern1, f):
                    match = re.search(self.fcov_pattern1, f)
                    field["brace"].append(match.group(1))
                elif re.search(self.fcov_pattern0, f):
                    match = re.search(self.fcov_pattern0, f)
                    if ("!" in f and (("/" in f) or (match.group(6) != "") or ("+" in f))):
                        print("%s %s fcov is format error '!' not with '/N+'" % (reg_name, field_name))
                        sys.exit(0)
                    if (("/" in f and match.group(6) == "") or
                       ("/" not in f and match.group(6) != "")):
                        print("%s %s fcov is format error '/N' is right format" % (reg_name, field_name))
                        sys.exit(0)
                    min1 = match.group(2)
                    max1 = match.group(4)
                    min1, max1 = self.small_to_big(reg_name, field_name, field, min1.lower(), max1.lower())
                    if "!" in f:
                        field["black"].append((min1, max1))
                    else:
                        field["white"].append((min1, max1))
                        if "/" in f and "+" in f:
                            field["white_num"].append(-int(match.group(6)))
                            m_bin = int(match.group(6)) + 2
                        elif "/" in f:
                            field["white_num"].append(int(match.group(6)))
                            m_bin = int(match.group(6))
                        elif "+" in f:
                            field["white_num"].append(-int(1))
                            m_bin = int(3)
                        else:
                            field["white_num"].append(int(1))
                            m_bin = int(1)
                        if (max1 - min1 + 1) < m_bin:
                            print("%s %s fcov bin num larger than range" % (reg_name, field_name))
                            sys.exit(0)
                else:
                    print("%s %s fcov is not match" % (reg_name, field_name))
                    sys.exit(0)

    def small_to_big(self, rg_name, fd_name, fd, small, big):
        if small == "":
            small1 = 0
        elif "0x" in small:
            small1 = int(small.lstrip("0x"), 16)
        else:
            small1 = small
        if big == "":
            big1 = fd["max_val"]
        elif "0x" in big:
            big1 = int(big.lstrip("0x"), 16)
        else:
            big1 = big
        if int(small1) > int(big1):
            print("%s %s fcov is format error small:big" % (rg_name, fd_name))
            sys.exit(0)
        return int(small1), int(big1)

    def gen_bins(self, reg_name, field_name, field):
        field["mbin"] = []
        field["mbin_num"] = []
        field["rsv"]  = []
        field["weight"]  = 0

        if len(field["white"]) != 0:
            for idx, f in enumerate(field["white"]):
                if field["white_num"][idx] < 0:
                    field["mbin"].append((hex(f[0]), hex(f[0])))
                    field["mbin_num"].append(1)
                    field["mbin"].append((hex(f[1]), hex(f[1])))
                    field["mbin_num"].append(1)
                    field["mbin"].append((hex(f[0] + 1), hex(f[1] - 1)))
                    field["mbin_num"].append(abs(field["white_num"][idx]))
                    field["weight"] = field["weight"] + 2 + abs(field["white_num"][idx])
                else:
                    field["mbin"].append((hex(f[0]), hex(f[1])))
                    field["mbin_num"].append(field["white_num"][idx])
                    field["weight"] = field["weight"] + field["white_num"][idx]

        if len(field["brace"]) != 0:
            field["white"].extend(self.brace_split(reg_name, field_name, field))
            field["weight"] = field["weight"] + len(field["brace"])

        w_b_list = field["white"] + field["black"]
        field["rsv"].extend(self.rsv_bin(field["max_val"], w_b_list))
        if len(field["rsv"]) > 0:
            field["weight"] = field["weight"] + 1

    def brace_split(self, reg_name, field_name, field):
        field["brace_new"]      = []
        mbrace_list = []
        mbrace_list_1 = []
        mbrace_list_2 = []
        mbrace = field["brace"]
        for f in mbrace:
            mbrace_list_1 = f.split(',')
            mbrace_list_1 = [item for item in mbrace_list_1 if item]
            mbrace_list_2.extend(mbrace_list_1)
            mbrace_list_1 = [item.replace("0x", "'h") for item in mbrace_list_1 if item]
            field["brace_new"].append(",".join(mbrace_list_1))
        for f in mbrace_list_2:
            if "[" not in f:
                min1, max1 = self.small_to_big(reg_name, field_name, field, f.lower(), f.lower())
                mbrace_list.append((min1, max1))
            else:
                match = re.search(self.fcov_pattern0, f)
                min1 = match.group(2)
                max1 = match.group(4)
                min1, max1 = self.small_to_big(reg_name, field_name, field, min1.lower(), max1.lower())
                mbrace_list.append((min1, max1))
        return mbrace_list

    def rsv_bin(self, max1, valid: list[tuple]) -> list[range]:
        flag = 0
        mlist = []
        find_max = []
        V = sorted(valid)

        s, e = V[0]
        if s > 0:
            mlist.append((hex(0), hex(s - 1)))
        mlen = len(V)
        for idx, f in enumerate(V):
            find_max.append(f[1])
            if idx == (mlen - 1):
                break
            if flag > 0:
                flag = flag - 1
                continue
            s, e = f
            for i in range(idx + 1, mlen):
                s1, e1 = V[i]
                if e + 1 < s1:
                    mlist.append((hex(e + 1), hex(s1 - 1)))
                    break
                if e1 > e:
                    e = e1
                else:
                    flag = flag + 1
        find_max = sorted(find_max)
        e = find_max[-1]
        if e < max1:
            mlist.append((hex(e + 1), hex(max1)))
        return mlist
