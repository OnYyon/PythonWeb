import os
from typing import Literal, cast

from django.apps import AppConfig

from src.shared.utils.logger import LoggerConfig, configure_logger, get_logger


class SubscriptionConfig(AppConfig):
    name = "src.cinema_platform_django.subscription"
    label = "subscription"

    def ready(self) -> None:
        raw_env = os.getenv("ENVIRONMENT", "dev")
        if raw_env not in {"prod", "dev", "testing"}:
            raw_env = "dev"
        environment = cast(Literal["prod", "dev", "testing"], raw_env)
        configure_logger(
            LoggerConfig(service_name="subscription", environment=environment)
        )
        logger = get_logger("subscription")
        logger.info("subscription_logger_configured", environment=environment)
