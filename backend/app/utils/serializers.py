import json

from app.models.backtest import Backtest
from app.models.strategy import Strategy
from app.schemas import (
    BacktestMetrics,
    BacktestResponse,
    HoldingRecord,
    PortfolioPoint,
    RankingRule,
    ScreeningRule,
    StrategyResponse,
    TradeRecord,
)


def strategy_to_response(strategy: Strategy) -> StrategyResponse:
    return StrategyResponse(
        id=strategy.id,
        name=strategy.name,
        description=strategy.description,
        screening_rules=[ScreeningRule.model_validate(r) for r in json.loads(strategy.screening_rules or "[]")],
        ranking_rules=[RankingRule.model_validate(r) for r in json.loads(strategy.ranking_rules or "[]")],
        created_at=strategy.created_at,
        updated_at=strategy.updated_at,
    )


def backtest_to_response(backtest: Backtest) -> BacktestResponse:
    metrics = None
    if backtest.metrics:
        metrics = BacktestMetrics.model_validate(json.loads(backtest.metrics))

    portfolio_history = [
        PortfolioPoint.model_validate(p) for p in json.loads(backtest.portfolio_history or "[]")
    ]
    trades = [TradeRecord.model_validate(t) for t in json.loads(backtest.trades or "[]")]
    holdings = [HoldingRecord.model_validate(h) for h in json.loads(backtest.holdings or "[]")]
    holdings_history = json.loads(backtest.holdings_history or "[]")

    return BacktestResponse(
        id=backtest.id,
        strategy_id=backtest.strategy_id,
        name=backtest.name,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        initial_capital=backtest.initial_capital,
        rebalance_frequency=backtest.rebalance_frequency,
        top_n=backtest.top_n,
        position_sizing=backtest.position_sizing,
        position_sizing_metric=backtest.position_sizing_metric,
        status=backtest.status,
        metrics=metrics,
        portfolio_history=portfolio_history,
        trades=trades,
        holdings=holdings,
        holdings_history=holdings_history,
        error_message=backtest.error_message,
        created_at=backtest.created_at,
        completed_at=backtest.completed_at,
    )
