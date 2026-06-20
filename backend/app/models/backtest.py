from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Backtest(Base):
    __tablename__ = "backtests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[int] = mapped_column(
        ForeignKey("strategies.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_capital: Mapped[float] = mapped_column(Float, default=1_000_000.0)
    rebalance_frequency: Mapped[str] = mapped_column(String(32), default="monthly")
    top_n: Mapped[int] = mapped_column(Integer, default=5)
    position_sizing: Mapped[str] = mapped_column(String(32), default="equal")
    position_sizing_metric: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    metrics: Mapped[str | None] = mapped_column(Text)
    portfolio_history: Mapped[str | None] = mapped_column(Text)
    trades: Mapped[str | None] = mapped_column(Text)
    holdings: Mapped[str | None] = mapped_column(Text)
    holdings_history: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    strategy: Mapped["Strategy"] = relationship("Strategy", back_populates="backtests")
