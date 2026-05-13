from structlog import get_logger as _get_logger

from src.shared.utils.logger.config import LoggerConfig
from src.shared.utils.logger.setup import configure_logger


def get_logger(name: str | None = None):
    """Convenience wrapper around structlog.get_logger.

    If `name` is provided, the logger will be created with that name.
    """
    return _get_logger(name)


__all__ = ["LoggerConfig", "configure_logger", "get_logger"]
