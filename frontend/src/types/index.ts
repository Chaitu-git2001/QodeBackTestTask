export interface Stock {
  id: number
  symbol: string
  name: string | null
  exchange: string | null
  sector: string | null
  industry: string | null
  currency: string | null
  created_at: string
  updated_at: string
}

export interface StockFundamental {
  as_of_date: string
  market_cap: number | null
  pe_ratio: number | null
  pb_ratio: number | null
  dividend_yield: number | null
  roe: number | null
  revenue: number | null
  profit_margin: number | null
  debt_to_equity: number | null
  eps: number | null
  beta: number | null
}

export interface StockDetail extends Stock {
  latest_price?: {
    date: string
    close: number
    volume: number | null
  } | null
  latest_fundamental?: StockFundamental | null
}

export interface ScreeningRule {
  field: string
  operator: 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'between'
  value: number | number[]
}

export interface RankingRule {
  field: string
  direction: 'asc' | 'desc'
  weight: number
}

export interface Strategy {
  id: number
  name: string
  description: string | null
  screening_rules: ScreeningRule[]
  ranking_rules: RankingRule[]
  created_at: string
  updated_at: string
}

export interface BacktestMetrics {
  total_return: number
  cagr: number
  max_drawdown: number
  sharpe_ratio: number
  volatility: number
  win_rate: number
  final_value: number
  benchmark_return: number | null
}

export interface PortfolioPoint {
  date: string
  value: number
  benchmark_value: number | null
}

export interface TradeRecord {
  date: string
  symbol: string
  action: 'buy' | 'sell'
  quantity: number
  price: number
  value: number
}

export interface HoldingRecord {
  symbol: string
  weight: number
  value: number
}

export interface Backtest {
  id: number
  strategy_id: number
  name: string
  start_date: string
  end_date: string
  initial_capital: number
  rebalance_frequency: string
  top_n: number
  status: string
  metrics: BacktestMetrics | null
  portfolio_history: PortfolioPoint[]
  trades: TradeRecord[]
  holdings: HoldingRecord[]
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export interface DashboardStats {
  total_stocks: number
  total_strategies: number
  total_backtests: number
  completed_backtests: number
  avg_cagr: number | null
  recent_backtests: Backtest[]
}

export const FUNDAMENTAL_FIELDS = [
  { value: 'market_cap', label: 'Market Cap' },
  { value: 'pe_ratio', label: 'P/E Ratio' },
  { value: 'pb_ratio', label: 'P/B Ratio' },
  { value: 'dividend_yield', label: 'Dividend Yield' },
  { value: 'roe', label: 'ROE' },
  { value: 'revenue', label: 'Revenue' },
  { value: 'profit_margin', label: 'Profit Margin' },
  { value: 'debt_to_equity', label: 'Debt/Equity' },
  { value: 'eps', label: 'EPS' },
  { value: 'beta', label: 'Beta' },
]

export const OPERATORS = [
  { value: 'gt', label: 'Greater than' },
  { value: 'gte', label: 'Greater than or equal' },
  { value: 'lt', label: 'Less than' },
  { value: 'lte', label: 'Less than or equal' },
  { value: 'eq', label: 'Equal to' },
  { value: 'between', label: 'Between' },
]
