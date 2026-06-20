from datetime import date

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.backtest import Backtest


class BacktestRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_backtests(self, limit: int = 50) -> list[Backtest]:
        return list(
            self.db.scalars(
                select(Backtest).order_by(desc(Backtest.created_at)).limit(limit)
            ).all()
        )

    def get_by_id(self, backtest_id: int) -> Backtest | None:
        return self.db.get(Backtest, backtest_id)

    def create(self, backtest: Backtest) -> Backtest:
        self.db.add(backtest)
        self.db.commit()
        self.db.refresh(backtest)
        return backtest

    def update(self, backtest: Backtest) -> Backtest:
        self.db.commit()
        self.db.refresh(backtest)
        return backtest

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Backtest)) or 0

    def count_completed(self) -> int:
        return (
            self.db.scalar(
                select(func.count()).select_from(Backtest).where(Backtest.status == "completed")
            )
            or 0
        )

    def avg_cagr(self) -> float | None:
        import json

        backtests = list(
            self.db.scalars(select(Backtest).where(Backtest.status == "completed")).all()
        )
        if not backtests:
            return None
        values = []
        for bt in backtests:
            if not bt.metrics:
                continue
            metrics = json.loads(bt.metrics)
            if metrics.get("cagr") is not None:
                values.append(metrics["cagr"])
        return sum(values) / len(values) if values else None
