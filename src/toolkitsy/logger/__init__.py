"""Shared logger for toolkitsy and downstream repos.

Public API:

    from toolkitsy.logger import logger
    logger.info("hello")

    from toolkitsy.logger import configure, get_logger, set_level
    from toolkitsy.logger import set_correlation_id, get_correlation_id
"""

from toolkitsy.logger._correlation_id import get_correlation_id, set_correlation_id
from toolkitsy.logger._logger import configure, get_logger, logger, set_level

__all__ = [
    "configure",
    "get_correlation_id",
    "get_logger",
    "logger",
    "set_correlation_id",
    "set_level",
]
