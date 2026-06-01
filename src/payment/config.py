from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_dsn: str = Field(
        validation_alias=AliasChoices("PAYMENT_DATABASE_DSN", "DATABASE_URL")
    )
    pool_min_size: int = Field(default=1, validation_alias="PAYMENT_DB_POOL_MIN")
    pool_max_size: int = Field(default=10, validation_alias="PAYMENT_DB_POOL_MAX")

    @model_validator(mode="after")
    def _validate_pool_sizes(self) -> "Settings":
        if self.pool_min_size <= 0 or self.pool_max_size <= 0:
            raise ValueError("Pool size must be positive")
        if self.pool_min_size > self.pool_max_size:
            raise ValueError("pool_min_size cannot be greater than pool_max_size")
        return self

    @classmethod
    def from_env(cls) -> "Settings":
        return cls()  # type: ignore
