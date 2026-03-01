from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker


@lru_cache(maxsize=None)
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, future=True)


@lru_cache(maxsize=None)
def get_session_factory(database_url: str) -> sessionmaker:
    return sessionmaker(
        bind=get_engine(database_url),
        autoflush=False,
        autocommit=False,
        future=True,
    )
