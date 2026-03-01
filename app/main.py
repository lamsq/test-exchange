from __future__ import annotations

import time

from alembic import command
from alembic.config import Config
import requests
from sqlalchemy import text

from app.config import get_settings
from app.db import SessionLocal, engine
from app.logger import configure_logging
from app.models import RequestRecord, ResponseRecord


settings = get_settings()
logger = configure_logging(settings.log_file)


def wait_for_database() -> None:
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("БД подключена")
            return
        except Exception:
            logger.exception("БД не готова")
            time.sleep(2)


def run_migrations() -> None:
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    logger.info("Применены миграции")


def store_request(url: str) -> int:
    with SessionLocal() as session:
        request_record = RequestRecord(url=url)
        session.add(request_record)
        session.commit()
        session.refresh(request_record)
        return request_record.id


def store_response(request_id: int, payload: dict) -> None:
    with SessionLocal() as session:
        session.add(
            ResponseRecord(
                request_id=request_id,
                result=str(payload.get("result", "")),
                time_last_update_unix=int(payload.get("time_last_update_unix", 0)),
                base_code=str(payload.get("base_code", "")),
                conversion_rates=payload.get("conversion_rates", {}),
            )
        )
        session.commit()


def poll_exchange_rate() -> None:
    while True:
        request_id = store_request(settings.exchange_rate_api_url)

        try:
            response = requests.get(
                settings.exchange_rate_api_url,
                timeout=settings.request_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            store_response(request_id, payload)
            logger.info("Для запроса request_id=%s сохранен ответ", request_id)
        except requests.exceptions.Timeout:
            logger.exception("Таймаут для запроса request_id=%s", request_id)
        except requests.exceptions.ConnectionError:
            logger.exception("Ошибка подклбчения для запроса request_id=%s", request_id)
        except requests.exceptions.RequestException:
            logger.exception("Ошибка запроса request_id=%s", request_id)
        except ValueError:
            logger.exception("Некорректные данные для запроса request_id=%s", request_id)

        time.sleep(settings.poll_interval_seconds)


def main() -> None:
    wait_for_database()
    run_migrations()
    poll_exchange_rate()


if __name__ == "__main__":
    main()
