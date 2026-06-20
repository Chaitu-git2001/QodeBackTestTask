from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.backtest import Backtest
from app.repositories.backtest_repository import BacktestRepository
from app.repositories.strategy_repository import StrategyRepository
from app.schemas import BacktestCreate, BacktestResponse
from app.services.backtest_engine import BacktestEngine
from app.utils.serializers import backtest_to_response

router = APIRouter(prefix="/backtests", tags=["Backtests"])


@router.get("", response_model=list[BacktestResponse])
def list_backtests(db: Session = Depends(get_db)):
    repo = BacktestRepository(db)
    return [backtest_to_response(b) for b in repo.list_backtests()]


@router.post("", response_model=BacktestResponse, status_code=201)
def run_backtest(payload: BacktestCreate, db: Session = Depends(get_db)):
    strategy_repo = StrategyRepository(db)
    strategy = strategy_repo.get_by_id(payload.strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if payload.start_date >= payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    backtest_repo = BacktestRepository(db)
    backtest = Backtest(
        strategy_id=payload.strategy_id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        initial_capital=payload.initial_capital,
        rebalance_frequency=payload.rebalance_frequency,
        top_n=payload.top_n,
        position_sizing=payload.position_sizing,
        position_sizing_metric=payload.position_sizing_metric,
        status="pending",
    )
    backtest = backtest_repo.create(backtest)

    engine = BacktestEngine(db)
    backtest = engine.run(backtest, strategy)
    return backtest_to_response(backtest)


@router.get("/{backtest_id}", response_model=BacktestResponse)
def get_backtest(backtest_id: int, db: Session = Depends(get_db)):
    repo = BacktestRepository(db)
    backtest = repo.get_by_id(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return backtest_to_response(backtest)
