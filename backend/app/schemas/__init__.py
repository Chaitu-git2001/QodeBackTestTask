from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StockBase(BaseModel):
    symbol: str
    name: str | None = None
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    currency: str | None = "INR"


class StockResponse(StockBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StockPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    open: float | None
    high: float | None
    low: float | None
    close: float
    adj_close: float | None
    volume: int | None


class StockFundamentalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    as_of_date: date
    market_cap: float | None
    pe_ratio: float | None
    pb_ratio: float | None
    dividend_yield: float | None
    roe: float | None
    revenue: float | None
    profit_margin: float | None
    debt_to_equity: float | None
    eps: float | None
    beta: float | None
    roce: float | None = None
    pat: float | None = None


class StockDetailResponse(StockResponse):
    latest_price: StockPriceResponse | None = None
    latest_fundamental: StockFundamentalResponse | None = None


class StockSyncRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    period: str = "5y"


class StockSyncResponse(BaseModel):
    synced: list[str]
    failed: list[str]
    message: str


class ScreeningRule(BaseModel):
    field: str
    operator: Literal["gt", "gte", "lt", "lte", "eq", "between"]
    value: float | list[float]


class RankingRule(BaseModel):
    field: str
    direction: Literal["asc", "desc"] = "desc"
    weight: float = 1.0


class StrategyCreate(BaseModel):
    name: str
    description: str | None = None
    screening_rules: list[ScreeningRule] = Field(default_factory=list)
    ranking_rules: list[RankingRule] = Field(default_factory=list)


class StrategyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    screening_rules: list[ScreeningRule] | None = None
    ranking_rules: list[RankingRule] | None = None


class StrategyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    screening_rules: list[ScreeningRule]
    ranking_rules: list[RankingRule]
    created_at: datetime
    updated_at: datetime


class BacktestCreate(BaseModel):
    strategy_id: int
    name: str
    start_date: date
    end_date: date
    initial_capital: float = 1_000_000.0
    rebalance_frequency: Literal["monthly", "quarterly", "yearly"] = "monthly"
    top_n: int = Field(default=5, ge=1, le=50)
    position_sizing: str = "equal"
    position_sizing_metric: str | None = None


class BacktestMetrics(BaseModel):
    total_return: float
    cagr: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    win_rate: float
    final_value: float
    benchmark_return: float | None = None


class PortfolioPoint(BaseModel):
    date: date
    value: float
    benchmark_value: float | None = None
    drawdown: float | None = None


class TradeRecord(BaseModel):
    date: date
    symbol: str
    action: Literal["buy", "sell"]
    quantity: float
    price: float
    value: float


class HoldingRecord(BaseModel):
    symbol: str
    weight: float
    value: float


class BacktestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    strategy_id: int
    name: str
    start_date: date
    end_date: date
    initial_capital: float
    rebalance_frequency: str
    top_n: int
    position_sizing: str
    position_sizing_metric: str | None = None
    status: str
    metrics: BacktestMetrics | None = None
    portfolio_history: list[PortfolioPoint] = Field(default_factory=list)
    trades: list[TradeRecord] = Field(default_factory=list)
    holdings: list[HoldingRecord] = Field(default_factory=list)
    holdings_history: list[Any] = Field(default_factory=list)
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class DashboardStats(BaseModel):
    total_stocks: int
    total_strategies: int
    total_backtests: int
    completed_backtests: int
    avg_cagr: float | None = None
    recent_backtests: list[BacktestResponse] = Field(default_factory=list)


class MessageResponse(BaseModel):
    message: str
    detail: Any | None = None
