from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class RequestRecord(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    responses: Mapped[list["ResponseRecord"]] = relationship(back_populates="request")


class ResponseRecord(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    time_last_update_unix: Mapped[int] = mapped_column(BigInteger, nullable=False)
    base_code: Mapped[str] = mapped_column(String(16), nullable=False)
    conversion_rates: Mapped[dict] = mapped_column(JSON, nullable=False)
    request: Mapped[RequestRecord] = relationship(back_populates="responses")
