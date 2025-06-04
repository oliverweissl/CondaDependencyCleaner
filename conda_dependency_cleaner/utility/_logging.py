import logging
from typing import Any


class ColorFormatter(logging.Formatter):
    """A Color Formatter for logging."""

    COLOR_CODES = {
        logging.DEBUG: "\033[94m",  # Blue
        logging.INFO: "\033[92m",  # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.CRITICAL: "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: Any) -> str:
        """
        Format the record according to schema.

        :param record: The record to format.
        :return: The formatted string.
        """
        color = self.COLOR_CODES.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}[CDC] {message}{self.RESET}"


def configure_global_logger(level: int = logging.DEBUG) -> None:
    """
    Configure the global logger.

    :param level: What level of messages should be shown.
    """
    logger = logging.getLogger()  # root logger
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter("%(message)s"))
        logger.addHandler(handler)
