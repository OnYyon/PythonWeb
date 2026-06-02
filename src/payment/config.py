from urllib.parse import quote

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_dsn: str | None = Field(
        default=None,
        validation_alias=AliasChoices("PAYMENT_DATABASE_DSN", "DATABASE_URL"),
    )
    db_host: str = Field(default="db", validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
    db_name: str = Field(default="cinema", validation_alias="DB_NAME")
    db_user: str = Field(default="cinema", validation_alias="DB_USER")
    db_password: str = Field(default="P@ssw0rd", validation_alias="DB_PASSWORD")
    pool_min_size: int = Field(default=1, validation_alias="PAYMENT_DB_POOL_MIN")
    pool_max_size: int = Field(default=10, validation_alias="PAYMENT_DB_POOL_MAX")

    @model_validator(mode="after")
    def _validate_pool_sizes(self) -> "Settings":
        if self.pool_min_size <= 0 or self.pool_max_size <= 0:
            raise ValueError("Pool size must be positive")
        if self.pool_min_size > self.pool_max_size:
            raise ValueError("pool_min_size cannot be greater than pool_max_size")
        return self

    @property
    def resolved_database_dsn(self) -> str:
        if self.database_dsn:
            return self.database_dsn

        user = quote(self.db_user, safe="")
        password = quote(self.db_password, safe="")
        return (
            f"postgresql://{user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @classmethod
    def from_env(cls) -> "Settings":
        return cls()
