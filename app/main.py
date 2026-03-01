from __future__ import annotations

import time
from logging import Logger
from typing import Any

from alembic import command
from alembic.config import Config
import requests
from sqlalchemy import Engine
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.db import get_engine, get_session_factory
from app.exchange import validate_exchange_payload
from app.logger import configure_logging
from app.models import RequestRecord, ResponseRecord


def wait_for_database(engine: Engine, logger: Logger, settings: Settings) -> None:
    for attempt in range(1, settings.db_ready_max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("БД подключена")
            return
        except sqlalchemy_exc.SQLAlchemyError as exc:
            if attempt == settings.db_ready_max_attempts:
                raise RuntimeError("БД недоступна, достигнут лимит попыток") from exc
            logger.warning("БД не готова (попытка %s/%s): %s",attempt,settings.db_ready_max_attempts,exc)
            time.sleep(settings.db_ready_check_interval_seconds)


def run_migrations(logger: Logger) -> None:
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    logger.info("Применены миграции")


def store_request(url: str, session_factory: sessionmaker) -> int:
    with session_factory.begin() as session:
        request_record = RequestRecord(url=url)
        session.add(request_record)
        session.flush()
        session.refresh(request_record)
        return request_record.id


def store_response(
    request_id: int,
    payload: dict[str, Any],
    session_factory: sessionmaker,
) -> None:
    with session_factory.begin() as session:
        session.add(
            ResponseRecord(
                request_id=request_id,
                result=payload["result"],
                time_last_update_unix=payload["time_last_update_unix"],
                base_code=payload["base_code"],
                conversion_rates=payload["conversion_rates"],
            )
        )


def poll_exchange_rate(
    settings: Settings,
    logger: Logger,
    session_factory: sessionmaker,
) -> None:
    while True:
        request_id = store_request(settings.exchange_rate_api_url, session_factory)

        try:
            response = requests.get(settings.exchange_rate_api_url,timeout=settings.request_timeout_seconds)
            response.raise_for_status()
            payload = validate_exchange_payload(response.json())
            store_response(request_id, payload, session_factory)
            logger.info("Для запроса request_id=%s сохранен ответ", request_id)
        except requests.exceptions.Timeout:
            logger.exception("Таймаут для запроса request_id=%s", request_id)
        except requests.exceptions.ConnectionError:
            logger.exception("Ошибка подключения для запроса request_id=%s", request_id)
        except requests.exceptions.RequestException:
            logger.exception("Ошибка запроса request_id=%s", request_id)
        except ValueError:
            logger.exception("Некорректные данные для запроса request_id=%s", request_id)

        time.sleep(settings.poll_interval_seconds)


def main() -> None:
    settings = get_settings()
    logger = configure_logging(settings.log_file)
    engine = get_engine(settings.database_url)
    session_factory = get_session_factory(settings.database_url)

    wait_for_database(engine, logger, settings)
    run_migrations(logger)
    poll_exchange_rate(settings, logger, session_factory)


if __name__ == "__main__":
    main()
