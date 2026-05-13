from dataclasses import dataclass
from typing import Literal


@dataclass
class LoggerConfig:
    """Logger config"""

    service_name: str = "testing"
    environment: Literal["prod", "dev", "testing"] = "dev"
    json_output: bool = False
    log_file: str | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    console_output: bool = True
    time_format: str = "iso"

    @property
    def is_dev(self) -> bool:
        return self.environment == "dev"

    @property
    def is_prod(self) -> bool:
        return self.environment == "prod"
