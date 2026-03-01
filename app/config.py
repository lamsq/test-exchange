from __future__ import annotations

from functools import lru_cache
import os
from dataclasses import dataclass, field


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value in (None, ""):
        raise ValueError(f"Переменная {name} обязательна")
    return value


def _get_int_env(name: str, default: int | None = None) -> int:
    raw_value = os.getenv(name)
    if raw_value in (None, ""):
        if default is None:
            raise ValueError(f"Переменная {name} обязательна")
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"Переменная {name} должна быть целочисленной") from exc


def _milliseconds_to_seconds(name: str) -> float:
    raw_value = _get_int_env(name)
    if raw_value < 0:
        raise ValueError(f"Переменная {name} должна быть положительной")
    return raw_value / 1000


@dataclass(frozen=True)
class Settings:
    postgres_db: str = field(init=False)
    postgres_user: str = field(init=False)
    postgres_password: str = field(init=False)
    postgres_host: str = field(init=False)
    postgres_port: int = field(init=False)
    db_ready_check_interval_seconds: float = field(init=False)
    db_ready_max_attempts: int = field(init=False)
    poll_interval_seconds: float = field(init=False)
    request_timeout_seconds: float = field(init=False)
    exchange_rate_api_key: str = field(init=False)
    exchange_rate_api_url: str = field(init=False)
    log_file: str = field(init=False)

    def __post_init__(self) -> None:
        postgres_db = _get_required_env("POSTGRES_DB")
        postgres_user = _get_required_env("POSTGRES_USER")
        postgres_password = _get_required_env("POSTGRES_PASSWORD")
        postgres_host = _get_required_env("POSTGRES_HOST")
        postgres_port = _get_int_env("POSTGRES_PORT")
        exchange_rate_api_key = _get_required_env("EXCHANGE_RATE_API_KEY")
        exchange_rate_api_url_template = _get_required_env("EXCHANGE_RATE_API_URL")
        log_file = _get_required_env("LOG_FILE")
        db_ready_check_interval_seconds = _get_int_env("DB_READY_CHECK_INTERVAL_MS", 2000) / 1000
        db_ready_max_attempts = _get_int_env("DB_READY_MAX_ATTEMPTS", 30)
        poll_interval_seconds = _milliseconds_to_seconds("POLL_INTERVAL_MS")
        request_timeout_seconds = _milliseconds_to_seconds("REQUEST_TIMEOUT_MS")

        if db_ready_check_interval_seconds <= 0:
            raise ValueError("DB_READY_CHECK_INTERVAL_MS должен быть больше 0")
        if db_ready_max_attempts <= 0:
            raise ValueError("DB_READY_MAX_ATTEMPTS должен быть больше 0")
        if request_timeout_seconds <= 0 or poll_interval_seconds <= 0:
            raise ValueError("POLL_INTERVAL_MS и REQUEST_TIMEOUT_MS должен быть больше 0")

        object.__setattr__(self, "postgres_db", postgres_db)
        object.__setattr__(self, "postgres_user", postgres_user)
        object.__setattr__(self, "postgres_password", postgres_password)
        object.__setattr__(self, "postgres_host", postgres_host)
        object.__setattr__(self, "postgres_port", postgres_port)
        object.__setattr__(self, "db_ready_check_interval_seconds", db_ready_check_interval_seconds)
        object.__setattr__(self, "db_ready_max_attempts", db_ready_max_attempts)
        object.__setattr__(self, "poll_interval_seconds", poll_interval_seconds)
        object.__setattr__(self, "request_timeout_seconds", request_timeout_seconds)
        object.__setattr__(self, "exchange_rate_api_key", exchange_rate_api_key)
        object.__setattr__(self, "log_file", log_file)
        object.__setattr__(
            self,
            "exchange_rate_api_url",
            exchange_rate_api_url_template.format(api_key=exchange_rate_api_key),
        )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
