import logging
import datetime

from django.conf import settings
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)

# 静态定义
LOG_LEVEL = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARN,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


class MLogger:
    def __init__(self, filename=None, log_filename=None):
        self.now_dt = datetime.datetime.now()
        self.filename = filename
        self.log_path = getattr(settings, "MLOGGER_LOG_PATH", settings.BASE_DIR / "logs")
        self.level = LOG_LEVEL.get(getattr(settings, "MLOGGER_LOG_LEVEL", "INFO"))
        self.header_level = LOG_LEVEL.get(getattr(settings, "MLOGGER_HEADER_LEVEL", "DEBUG"))

        __log_format = "%(asctime)s - %(levelname)s - %(message)s"
        self.log_format = getattr(settings, "MLOGGER_LOG_FORMAT", None) or __log_format

        # 处理 log-filename，判断传入是否带后缀
        __log_filename = str(log_filename) or "mlog.log"
        if __log_filename.split(".")[-1] != "log":
            __log_filename += ".log"
        self.log_filename = __log_filename

        __when = ("S", "M", "H", "D", "W", "midnight")
        __settings_when = getattr(settings, "MLOGGER_WHEN", "midnight")
        if __settings_when in __when:
            self.when = __settings_when
        else:
            self.when = "midnight"

    def guard(self, log_filename=None):
        """
        : 装饰器，守护代码异常
        Tag: 需要注意装饰器位置，建议放在最下层（否则日志中的文件位置可能会是意想不到的）
        """
        log_filename = log_filename or self.log_filename

        def _guard(func):
            def wrapper(*args, **kwargs):
                # 获取装饰的函数 __code__, 获取 函数名与函数代码起始行号
                # :Tag 起始行号会将装饰器也算上。
                func_obj = func.__code__
                basic_info = "funcName: {} - funcLine: {} - ".format(str(func_obj.co_name),
                                                                     str(func_obj.co_firstlineno))
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_info = str(type(e)) + " " + str(e)
                    _logger = self.get_logger(self.filename, self.log_path / log_filename)
                    _logger.error(basic_info + error_info)

            return wrapper

        return _guard

    def get_logger(self, func_origin_fn, log_filename):
        _logger = logging.getLogger(func_origin_fn)
        _logger.setLevel(self.level)

        file_handler = TimedRotatingFileHandler(log_filename, self.when)
        # file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(self.log_format)
        file_handler.setFormatter(formatter)

        _logger.addHandler(file_handler)

        return _logger
