from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.backtest_repository import BacktestRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.strategy_repository import StrategyRepository
from app.schemas import DashboardStats
from app.services.export_service import ExportService
from app.utils.serializers import backtest_to_response

router = APIRouter(tags=["Dashboard & Export"])


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    stock_repo = StockRepository(db)
    strategy_repo = StrategyRepository(db)
    backtest_repo = BacktestRepository(db)

    recent = [backtest_to_response(b) for b in backtest_repo.list_backtests(limit=5)]

    return DashboardStats(
        total_stocks=stock_repo.count_stocks(),
        total_strategies=strategy_repo.count(),
        total_backtests=backtest_repo.count_all(),
        completed_backtests=backtest_repo.count_completed(),
        avg_cagr=backtest_repo.avg_cagr(),
        recent_backtests=recent,
    )


@router.get("/export/{backtest_id}/csv")
def export_csv(
    backtest_id: int,
    export_type: str = Query("portfolio", pattern="^(portfolio|trades|holdings)$"),
    db: Session = Depends(get_db),
):
    service = ExportService(db)
    try:
        return service.export_csv(backtest_id, export_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/export/{backtest_id}/excel")
def export_excel(backtest_id: int, db: Session = Depends(get_db)):
    service = ExportService(db)
    try:
        return service.export_excel(backtest_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
