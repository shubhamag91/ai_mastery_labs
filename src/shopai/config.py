"""Settings for shopai, read from environment variables and the .env file."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # A real environment variable beats .env, which beats the defaults below.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: SecretStr  # required: no default, so startup fails without it
    deepseek_api_key: SecretStr | None = None  # optional: only the data generator uses it
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    environment: Literal["local", "ci", "production"] = "local"


@lru_cache
def get_settings() -> Settings:
    """Read the settings once, then hand back the same object on every call."""
    return Settings()
