from datetime import date

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.stock import Stock, StockFundamental, StockPrice


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_stocks(self, skip: int = 0, limit: int = 100) -> list[Stock]:
        return list(self.db.scalars(select(Stock).offset(skip).limit(limit)).all())

    def count_stocks(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Stock)) or 0

    def get_by_symbol(self, symbol: str) -> Stock | None:
        return self.db.scalar(select(Stock).where(Stock.symbol == symbol.upper()))

    def get_by_id(self, stock_id: int) -> Stock | None:
        return self.db.get(Stock, stock_id)

    def upsert_stock(self, stock: Stock) -> Stock:
        existing = self.get_by_symbol(stock.symbol)
        if existing:
            existing.name = stock.name or existing.name
            existing.exchange = stock.exchange or existing.exchange
            existing.sector = stock.sector or existing.sector
            existing.industry = stock.industry or existing.industry
            existing.currency = stock.currency or existing.currency
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock

    def bulk_upsert_prices(self, stock_id: int, prices: list[StockPrice]) -> int:
        if not prices:
            return 0
        dates = [p.date for p in prices]
        existing_dates = set(
            self.db.scalars(
                select(StockPrice.date).where(
                    StockPrice.stock_id == stock_id, StockPrice.date.in_(dates)
                )
            ).all()
        )
        inserted = 0
        for price in prices:
            if price.date in existing_dates:
                continue
            price.stock_id = stock_id
            self.db.add(price)
            inserted += 1
        self.db.commit()
        return inserted

    def upsert_fundamental(self, fundamental: StockFundamental) -> StockFundamental:
        existing = self.db.scalar(
            select(StockFundamental).where(
                StockFundamental.stock_id == fundamental.stock_id,
                StockFundamental.as_of_date == fundamental.as_of_date,
            )
        )
        if existing:
            for field in (
                "market_cap", "pe_ratio", "pb_ratio", "dividend_yield", "roe",
                "revenue", "profit_margin", "debt_to_equity", "eps", "beta",
            ):
                setattr(existing, field, getattr(fundamental, field))
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(fundamental)
        self.db.commit()
        self.db.refresh(fundamental)
        return fundamental

    def get_latest_price(self, stock_id: int) -> StockPrice | None:
        return self.db.scalar(
            select(StockPrice)
            .where(StockPrice.stock_id == stock_id)
            .order_by(desc(StockPrice.date))
            .limit(1)
        )

    def get_latest_fundamental(self, stock_id: int) -> StockFundamental | None:
        return self.db.scalar(
            select(StockFundamental)
            .where(StockFundamental.stock_id == stock_id)
            .order_by(desc(StockFundamental.as_of_date))
            .limit(1)
        )

    def get_prices_in_range(
        self, stock_id: int, start_date: date, end_date: date
    ) -> list[StockPrice]:
        return list(
            self.db.scalars(
                select(StockPrice)
                .where(
                    StockPrice.stock_id == stock_id,
                    StockPrice.date >= start_date,
                    StockPrice.date <= end_date,
                )
                .order_by(StockPrice.date)
            ).all()
        )

    def get_all_prices_for_symbols(
        self, symbols: list[str], start_date: date, end_date: date
    ) -> dict[str, list[StockPrice]]:
        stocks = list(
            self.db.scalars(select(Stock).where(Stock.symbol.in_(symbols))).all()
        )
        result: dict[str, list[StockPrice]] = {}
        for stock in stocks:
            result[stock.symbol] = self.get_prices_in_range(stock.id, start_date, end_date)
        return result

    def get_fundamental_as_of(self, stock_id: int, as_of: date) -> StockFundamental | None:
        return self.db.scalar(
            select(StockFundamental)
            .where(
                StockFundamental.stock_id == stock_id,
                StockFundamental.as_of_date <= as_of
            )
            .order_by(desc(StockFundamental.as_of_date))
            .limit(1)
        )

    def get_price_as_of(self, stock_id: int, as_of: date) -> StockPrice | None:
        return self.db.scalar(
            select(StockPrice)
            .where(
                StockPrice.stock_id == stock_id,
                StockPrice.date <= as_of
            )
            .order_by(desc(StockPrice.date))
            .limit(1)
        )

    def get_price_on_date(self, stock_id: int, d: date) -> StockPrice | None:
        return self.db.scalar(
            select(StockPrice)
            .where(
                StockPrice.stock_id == stock_id,
                StockPrice.date == d
            )
            .limit(1)
        )

