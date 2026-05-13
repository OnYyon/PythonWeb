import logging
import sys
from pathlib import Path

import structlog
from structlog.processors import (
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)

from src.shared.utils.logger.config import LoggerConfig
from src.shared.utils.logger.processors.environment import add_environment
from src.shared.utils.logger.processors.service import add_service


def configure_logger(config: LoggerConfig):
    """Configure structlog and logging"""
    processors = [
        structlog.contextvars.merge_contextvars,
        add_log_level,
        add_service(config.service_name),
        add_environment(config.environment),
        TimeStamper(fmt=config.time_format),
        StackInfoRenderer(),
        format_exc_info,
    ]

    if config.json_output:
        indent = None if config.is_prod else 2
        processors.append(JSONRenderer(indent=indent))
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    handlers: list[logging.Handler] = []

    if config.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.log_level))
        handlers.append(console_handler)

    if config.log_file:
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(filename=log_path)
        file_handler.setLevel(getattr(logging, config.log_level))
        handlers.append(file_handler)

    if not handlers:
        handlers.append(logging.NullHandler())

    logging.basicConfig(
        level=getattr(logging, config.log_level),
        handlers=handlers,
        format="%(message)s",
        force=True,
    )

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
