import logging


class RegLogger:
    """寄存器工具日志系统"""

    _LEVEL_MAP = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    @staticmethod
    def get_logger(name: str = "gen_reg_tools", level: str = "info") -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(RegLogger._LEVEL_MAP.get(level.lower(), logging.INFO))
        return logger
