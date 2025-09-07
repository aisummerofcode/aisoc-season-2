import logging, datetime as dt
import os
from colorama import Fore, Style

class ColorFormmater(logging.Formatter):
    """Custom formatter to color our logs based on their level"""

    def format(self, record):
        message = super().format(record)
        _time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # map color to log level
        color_map = {
            logging.INFO: Fore.LIGHTGREEN_EX,
            logging.WARNING: Fore.LIGHTYELLOW_EX,
            logging.ERROR: Fore.LIGHTRED_EX
        }

        color_format = color_map.get(record.levelno)
        message = f"{color_format}[{record.levelname}] {_time}{Style.RESET_ALL}: {message}"
        return message

def set_logger(
    logger_name: str = None,
    log_level: int = logging.INFO,
    to_file: bool = False,
    log_file_name: str = None,
    to_console: bool = False,
    custom_formatter: logging.Formatter = None
) -> logging.Logger:
    """
    Create and write log data for the system's operations.
    Log anything and everything!
    """

    if not to_file and not to_console:
        raise ValueError("Must provide wither `to_file` or `to_console` for where to stream logs.")
    
    logger = logging.getLogger(logger_name or __name__)
    logger.setLevel(log_level)

    # prevent multiple handlers
    if not logger.hasHandlers():

        default_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # log to file
        if to_file:
            if not log_file_name:
                raise ValueError("Must provide `log_file_name`")
            
            # Ensure directory exists for the log file
            log_dir = os.path.dirname(log_file_name)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file_name)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(default_formatter)
            logger.addHandler(file_handler)

        # log to terminal
        if to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)

            console_formatter = default_formatter if not custom_formatter else custom_formatter("%(message)s")

            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

    return logger