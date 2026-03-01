from __future__ import annotations

import os
from dataclasses import dataclass, field


def _milliseconds_to_seconds(value: str, default: int) -> float:
    raw_value = int(value) if value else default
    return raw_value / 1000


@dataclass(frozen=True)
class Settings:
    postgres_db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB"))
    postgres_user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER"))
    postgres_password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD"))
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST"))
    postgres_port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT")))
    poll_interval_seconds: float = field(
        default_factory=lambda: _milliseconds_to_seconds(
            os.getenv("POLL_INTERVAL_MS"),
            10000,
        )
    )

    request_timeout_seconds: float = field(
        default_factory=lambda: _milliseconds_to_seconds(
            os.getenv("REQUEST_TIMEOUT_MS"),
            5000,
        )
    )

    exchange_rate_api_key: str = field(
        default_factory=lambda: os.getenv("EXCHANGE_RATE_API_KEY")
    )

    exchange_rate_api_url: str = field(init=False)
    log_file: str = field(default_factory=lambda: os.getenv("LOG_FILE"))

    def __post_init__(self) -> None:
        exchange_rate_api_url_template = os.getenv("EXCHANGE_RATE_API_URL")

        object.__setattr__(
            self,
            "exchange_rate_api_url",
            exchange_rate_api_url_template.format(api_key=self.exchange_rate_api_key),
        )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_settings() -> Settings:
    return Settings()
