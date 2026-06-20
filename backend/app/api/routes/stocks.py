from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.repositories.stock_repository import StockRepository
from app.schemas import (
    StockDetailResponse,
    StockFundamentalResponse,
    StockPriceResponse,
    StockResponse,
    StockSyncRequest,
    StockSyncResponse,
)
from app.services.yahoo_finance_service import YahooFinanceService

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("", response_model=list[StockResponse])
def list_stocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    repo = StockRepository(db)
    return repo.list_stocks(skip=skip, limit=limit)


@router.get("/{symbol}", response_model=StockDetailResponse)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    repo = StockRepository(db)
    stock = repo.get_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    latest_price = repo.get_latest_price(stock.id)
    latest_fundamental = repo.get_latest_fundamental(stock.id)

    return StockDetailResponse(
        id=stock.id,
        symbol=stock.symbol,
        name=stock.name,
        exchange=stock.exchange,
        sector=stock.sector,
        industry=stock.industry,
        currency=stock.currency,
        created_at=stock.created_at,
        updated_at=stock.updated_at,
        latest_price=StockPriceResponse.model_validate(latest_price) if latest_price else None,
        latest_fundamental=(
            StockFundamentalResponse.model_validate(latest_fundamental)
            if latest_fundamental
            else None
        ),
    )


@router.get("/{symbol}/prices", response_model=list[StockPriceResponse])
def get_stock_prices(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
):
    from datetime import date

    repo = StockRepository(db)
    stock = repo.get_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    start = date.fromisoformat(start_date) if start_date else date(2019, 1, 1)
    end = date.fromisoformat(end_date) if end_date else date.today()
    prices = repo.get_prices_in_range(stock.id, start, end)
    return prices


@router.post("/sync", response_model=StockSyncResponse)
def sync_stocks(payload: StockSyncRequest, db: Session = Depends(get_db)):
    service = YahooFinanceService(db)
    symbols = payload.symbols or settings.default_stock_list
    synced, failed = service.sync_symbols(symbols, payload.period)
    return StockSyncResponse(
        synced=synced,
        failed=failed,
        message=f"Synced {len(synced)} stocks, {len(failed)} failed.",
    )
