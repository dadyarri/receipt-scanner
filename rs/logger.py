import logging
import os
import traceback


class BaseFormatter(logging.Formatter):
    @staticmethod
    def construct_format(record: logging.LogRecord) -> dict:
        msg = record.msg
        ln = record.levelname
        mdl = record.module
        lno = record.lineno
        if record.exc_info:
            trs = traceback.format_exception(*record.exc_info)
        else:
            trs = None
        return {"msg": msg, "ln": ln, "mdl": mdl, "trs": trs, "lno": lno}

    def format(self, record: logging.LogRecord) -> str:
        data = self.construct_format(record)
        fmt = f"[{data['ln']}] ({data['mdl']}:{data['lno']}): {data['msg']}"
        if record.exc_info is not None:
            fmt += f"\n{''.join(data['trs'])}"
        return fmt


def init():
    logger = logging.getLogger("rc")
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    console = logging.StreamHandler()
    console.setFormatter(BaseFormatter())
    logger.addHandler(console)
    return logger
