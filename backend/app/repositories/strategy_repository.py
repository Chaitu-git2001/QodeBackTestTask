from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.strategy import Strategy


class StrategyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_strategies(self) -> list[Strategy]:
        return list(self.db.scalars(select(Strategy).order_by(desc(Strategy.updated_at))).all())

    def get_by_id(self, strategy_id: int) -> Strategy | None:
        return self.db.get(Strategy, strategy_id)

    def create(self, strategy: Strategy) -> Strategy:
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def update(self, strategy: Strategy) -> Strategy:
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def delete(self, strategy: Strategy) -> None:
        self.db.delete(strategy)
        self.db.commit()

    def count(self) -> int:
        from sqlalchemy import func, select as sa_select

        return self.db.scalar(sa_select(func.count()).select_from(Strategy)) or 0
