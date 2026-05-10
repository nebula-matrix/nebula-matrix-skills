from typing import Dict, Any
import time
import getpass

from gen_reg_tools.regslv.config import RegSlvConfig


class ProcHeader:

    def __init__(self, config: RegSlvConfig, logger: Any) -> None:
        self.config = config
        self.logger = logger
        self.header_dict = {}

    def get_header_dict(self) -> None:
        now_time = time.localtime()
        date = f"{now_time.tm_year}/{now_time.tm_mon:>02}/{now_time.tm_mday:02}"
        user = getpass.getuser()
        version = 1.0

        self.header_dict["year"] = now_time.tm_year
        self.header_dict["module_name"] = self.config.module_name
        self.header_dict["history_title"] = f"{'Rev.level':<9}   {'Date':<10}  {'Code by':<20}      Contents"
        self.header_dict["history"] = f"{version:<9}   {date:<10}  {user:<20}"
