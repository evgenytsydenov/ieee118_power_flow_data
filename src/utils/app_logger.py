import logging
import logging.handlers
import os
from datetime import datetime
from logging.handlers import QueueHandler
from multiprocessing import Queue
from typing import Optional

import pytz

from definitions import LOG_DATE_FORMAT, LOG_FORMAT_DEBUG, LOG_FORMAT_INFO, LOG_PATH


class CustomFormatter(logging.Formatter):
    """Override standard formatter to specify timezone."""

    def converter(self, timestamp: float) -> datetime:
        """Convert time to UTC zone.

        Args:
            timestamp: Time in seconds.

        Returns:
            Datetime object in UTC zone.
        """
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        return dt.astimezone(pytz.timezone("UTC"))

    def formatTime(
        self, record: logging.LogRecord, datefmt: Optional[str] = None
    ) -> str:
        """Convert time to specified format.

        Args:
            record: Log record.
            datefmt: Date format.

        Returns:
            Time in string format.
        """
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


def _get_file_handler(path: str) -> logging.FileHandler:
    """Create logger to save logs to a file.

    Args:
        path: Path to log file.

    Returns:
        File handler for logs.
    """
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        CustomFormatter(fmt=LOG_FORMAT_DEBUG, datefmt=LOG_DATE_FORMAT)
    )
    return file_handler


def _get_stream_handler() -> logging.StreamHandler:
    """Create logger to print logs to console.

    Returns:
        Stream handler for logs.
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(
        CustomFormatter(fmt=LOG_FORMAT_INFO, datefmt=LOG_DATE_FORMAT)
    )
    return stream_handler


def get_logger(module_name: str) -> logging.Logger:
    """Create logger.

    Args:
        module_name: Name of the module where events happen.

    Returns:
        Logger.
    """
    project_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    path_log = os.path.join(project_path, LOG_PATH)
    os.makedirs(os.path.dirname(path_log), exist_ok=True)
    logger = logging.getLogger(module_name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_get_file_handler(path_log))
        logger.addHandler(_get_stream_handler())
    return logger


def get_queue_logger(module_name: str, queue: Queue) -> logging.Logger:
    """Logger used in subprocesses.

    Args:
        queue: Shared queue.
        module_name: Name of the module where events happen.

    Returns:
        Logger.
    """
    logger = logging.getLogger(module_name)
    if not logger.handlers:
        logger.addHandler(QueueHandler(queue))
        logger.setLevel(logging.DEBUG)
    return logger


def queue_listener(module_name: str, queue: Queue) -> None:
    """Listen the log queue.

    Args:
        queue: Queue to listen.
        module_name: Name of the module where events happen.
    """
    logger = get_logger(module_name)
    while True:
        message = queue.get()
        if message is None:
            break
        logger.handle(message)
