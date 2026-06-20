// Stock interfaces
export const FUNDAMENTAL_FIELDS = [
  { value: "market_cap", label: "Market Cap" },
  { value: "pe_ratio", label: "P/E Ratio" },
  { value: "pb_ratio", label: "P/B Ratio" },
  { value: "dividend_yield", label: "Dividend Yield" },
  { value: "roe", label: "ROE (%)" },
  { value: "roce", label: "ROCE (%)" },
  { value: "pat", label: "PAT (Profit After Tax)" },
  { value: "revenue", label: "Revenue" },
  { value: "profit_margin", label: "Profit Margin" },
  { value: "debt_to_equity", label: "Debt to Equity" },
  { value: "eps", label: "EPS" },
  { value: "beta", label: "Beta" },
];

export const OPERATORS = [
  { value: "gt", label: "Greater than (>)" },
  { value: "gte", label: "Greater or equal (≥)" },
  { value: "lt", label: "Less than (<)" },
  { value: "lte", label: "Less or equal (≤)" },
  { value: "eq", label: "Equal (=)" },
  { value: "between", label: "Between" },
];

// Note: The following are JSDoc type definitions for IDE support
/**
 * @typedef {Object} Stock
 * @property {number} id
 * @property {string} symbol
 * @property {string | null} name
 * @property {string | null} exchange
 * @property {string | null} sector
 * @property {string | null} industry
 * @property {string | null} currency
 * @property {string} created_at
 * @property {string} updated_at
 */

/**
 * @typedef {Object} StockFundamental
 * @property {string} as_of_date
 * @property {number | null} market_cap
 * @property {number | null} pe_ratio
 * @property {number | null} pb_ratio
 * @property {number | null} dividend_yield
 * @property {number | null} roe
 * @property {number | null} revenue
 * @property {number | null} profit_margin
 * @property {number | null} debt_to_equity
 * @property {number | null} eps
 * @property {number | null} beta
 */

/**
 * @typedef {Stock & Object} StockDetail
 * @property {Object | null} latest_price
 * @property {string} latest_price.date
 * @property {number} latest_price.close
 * @property {number | null} latest_price.volume
 * @property {StockFundamental | null} latest_fundamental
 */

/**
 * @typedef {Object} ScreeningRule
 * @property {string} field
 * @property {'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'between'} operator
 * @property {number | number[]} value
 */

/**
 * @typedef {Object} RankingRule
 * @property {string} field
 * @property {'asc' | 'desc'} direction
 * @property {number} weight
 */

/**
 * @typedef {Object} Strategy
 * @property {number} id
 * @property {string} name
 * @property {string | null} description
 * @property {ScreeningRule[]} screening_rules
 * @property {RankingRule[]} ranking_rules
 * @property {string} created_at
 * @property {string} updated_at
 */

/**
 * @typedef {Object} BacktestMetrics
 * @property {number} total_return
 * @property {number} cagr
 * @property {number} max_drawdown
 * @property {number} sharpe_ratio
 * @property {number} volatility
 * @property {number} win_rate
 * @property {number} final_value
 * @property {number | null} benchmark_return
 */

/**
 * @typedef {Object} PortfolioPoint
 * @property {string} date
 * @property {number} value
 * @property {number | null} benchmark_value
 */

/**
 * @typedef {Object} TradeRecord
 * @property {string} date
 * @property {string} symbol
 * @property {'buy' | 'sell'} action
 * @property {number} quantity
 * @property {number} price
 * @property {number} value
 */

/**
 * @typedef {Object} HoldingRecord
 * @property {string} symbol
 * @property {number} weight
 * @property {number} value
 */

/**
 * @typedef {Object} Backtest
 * @property {number} id
 * @property {number} strategy_id
 * @property {string} name
 * @property {string} start_date
 * @property {string} end_date
 * @property {number} initial_capital
 * @property {string} rebalance_frequency
 * @property {number} top_n
 * @property {string} status
 * @property {BacktestMetrics | null} metrics
 * @property {PortfolioPoint[]} portfolio_history
 * @property {TradeRecord[]} trades
 * @property {HoldingRecord[]} holdings
 * @property {string | null} error_message
 * @property {string} created_at
 * @property {string} updated_at
 */

/**
 * @typedef {Object} DashboardStats
 * @property {number} total_stocks
 * @property {number} total_strategies
 * @property {number} total_backtests
 * @property {number} completed_backtests
 * @property {number | null} avg_cagr
 * @property {Array<Object>} recent_backtests
 */
