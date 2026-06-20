import json
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.backtest import Backtest
from app.models.strategy import Strategy
from app.repositories.backtest_repository import BacktestRepository
from app.repositories.stock_repository import StockRepository
from app.schemas import BacktestMetrics, HoldingRecord, PortfolioPoint, TradeRecord
from app.services.strategy_engine import StrategyEngine, parse_strategy_rules


class BacktestEngine:
    def __init__(self, db: Session):
        self.db = db
        self.stock_repo = StockRepository(db)
        self.backtest_repo = BacktestRepository(db)
        self.strategy_engine = StrategyEngine()

    def run(self, backtest: Backtest, strategy: Strategy) -> Backtest:
        backtest.status = "running"
        self.backtest_repo.update(backtest)

        try:
            screening_rules, ranking_rules = parse_strategy_rules(
                strategy.screening_rules, strategy.ranking_rules
            )
            result = self._execute_backtest(
                backtest.start_date,
                backtest.end_date,
                backtest.initial_capital,
                backtest.rebalance_frequency,
                backtest.top_n,
                backtest.position_sizing,
                backtest.position_sizing_metric,
                screening_rules,
                ranking_rules,
            )
            backtest.status = "completed"
            backtest.metrics = json.dumps(result["metrics"])
            backtest.portfolio_history = json.dumps(result["portfolio_history"])
            backtest.trades = json.dumps(result["trades"])
            backtest.holdings = json.dumps(result["holdings"])
            backtest.holdings_history = json.dumps(result["holdings_history"])
            backtest.error_message = None
            backtest.completed_at = datetime.utcnow()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            backtest.status = "failed"
            backtest.error_message = str(exc)
            backtest.completed_at = datetime.utcnow()

        return self.backtest_repo.update(backtest)

    def _execute_backtest(
        self,
        start_date: date,
        end_date: date,
        initial_capital: float,
        rebalance_frequency: str,
        top_n: int,
        position_sizing: str,
        position_sizing_metric: str | None,
        screening_rules,
        ranking_rules,
    ) -> dict[str, Any]:
        stocks = self.stock_repo.list_stocks(limit=500)
        if not stocks:
            raise ValueError("No stocks in database. Sync stock data first.")

        # Gather price frames
        price_frames: dict[str, pd.Series] = {}
        for stock in stocks:
            prices = self.stock_repo.get_prices_in_range(stock.id, start_date, end_date)
            if len(prices) < 2:
                continue
            series = pd.Series(
                {p.date: (p.adj_close or p.close) for p in prices},
                name=stock.symbol,
            ).sort_index()
            price_frames[stock.symbol] = series

        if not price_frames:
            raise ValueError("Insufficient price data for backtest period.")

        prices_df = pd.DataFrame(price_frames).ffill().dropna(how="all")
        prices_df.index = pd.to_datetime(prices_df.index)
        prices_df = prices_df.sort_index()

        rebalance_dates = self._get_rebalance_dates(prices_df.index, rebalance_frequency, start_date, end_date)
        if not rebalance_dates:
            raise ValueError("No rebalance dates in selected period.")

        # --- FILTERING ONCE AT START ---
        # Evaluate candidates on the start_date to determine the fixed universe
        start_candidates = self._build_candidates(start_date, universe=None)
        screened_candidates = self.strategy_engine.apply_screening(start_candidates, screening_rules)
        screened_universe = {c["symbol"] for c in screened_candidates}

        if not screened_universe:
            raise ValueError("No stocks passed the screening rules on the start date of the backtest.")

        # --- SIMULATION STATE ---
        cash = initial_capital
        holdings: dict[str, float] = {}
        purchase_prices: dict[str, float] = {}
        trades: list[dict] = []
        holdings_history: list[dict] = []

        benchmark_symbol = next((s for s in price_frames if "NIFTY" in s or s.endswith(".NS")), None)
        benchmark_start = None
        if benchmark_symbol and benchmark_symbol in prices_df.columns:
            benchmark_start = prices_df[benchmark_symbol].dropna().iloc[0]

        # Trade PnL tracking for Winners & Losers
        # trade_pnl: symbol -> {"sells": 0.0, "buys": 0.0, "final_val": 0.0}
        trade_pnl: dict[str, dict[str, float]] = {}

        # Rebalance loop
        for rebal_date in rebalance_dates:
            available_dates = prices_df.index[prices_df.index <= pd.Timestamp(rebal_date)]
            if len(available_dates) == 0:
                continue
            available_date = available_dates[-1]
            row_prices = prices_df.loc[available_date]

            # Fetch candidates from the fixed universe, querying their historical parameters as of this date
            candidates = self._build_candidates(available_date.date(), universe=screened_universe)
            selected = self.strategy_engine.select_top_n(
                candidates, [], ranking_rules, top_n  # screening already applied once at start
            )
            selected_symbols = [c["symbol"] for c in selected if c["symbol"] in row_prices.index]

            portfolio_value = cash + sum(
                qty * float(row_prices[sym]) for sym, qty in holdings.items() if sym in row_prices
            )

            # Log current holdings value and return since last rebalance before selling
            period_holdings = []
            for sym, qty in list(holdings.items()):
                if sym not in row_prices or qty <= 0:
                    continue
                price = float(row_prices[sym])
                val = qty * price
                prev_price = purchase_prices.get(sym, price)
                ret = (price - prev_price) / prev_price if prev_price > 0 else 0.0
                period_holdings.append({
                    "symbol": sym,
                    "quantity": qty,
                    "weight": val / portfolio_value if portfolio_value > 0 else 0.0,
                    "value": val,
                    "price": price,
                    "purchase_price": prev_price,
                    "return": round(ret, 4)
                })

            if period_holdings:
                holdings_history.append({
                    "date": available_date.date().isoformat(),
                    "portfolio_value": portfolio_value,
                    "holdings": period_holdings
                })

            # Sell off existing portfolio
            for sym, qty in list(holdings.items()):
                if sym not in row_prices or qty <= 0:
                    continue
                price = float(row_prices[sym])
                sell_val = qty * price
                trades.append({
                    "date": available_date.date().isoformat(),
                    "symbol": sym,
                    "action": "sell",
                    "quantity": qty,
                    "price": price,
                    "value": sell_val,
                })
                cash += sell_val

                # Track PnL
                if sym not in trade_pnl:
                    trade_pnl[sym] = {"buys": 0.0, "sells": 0.0, "final_val": 0.0}
                trade_pnl[sym]["sells"] += sell_val

            holdings.clear()
            purchase_prices.clear()

            if not selected_symbols:
                continue

            # --- POSITION SIZING ---
            weights: dict[str, float] = {}
            selected_candidates = {c["symbol"]: c for c in selected}

            if position_sizing == "market_cap":
                total_mc = sum(max(0.0, float(selected_candidates[sym].get("market_cap") or 0.0)) for sym in selected_symbols)
                if total_mc > 0:
                    for sym in selected_symbols:
                        mc = float(selected_candidates[sym].get("market_cap") or 0.0)
                        weights[sym] = max(0.0, mc) / total_mc
                else:
                    eq_w = 1.0 / len(selected_symbols)
                    for sym in selected_symbols:
                        weights[sym] = eq_w
            elif position_sizing == "metric" and position_sizing_metric:
                total_metric = sum(max(0.0, float(selected_candidates[sym].get(position_sizing_metric) or 0.0)) for sym in selected_symbols)
                if total_metric > 0:
                    for sym in selected_symbols:
                        val = float(selected_candidates[sym].get(position_sizing_metric) or 0.0)
                        weights[sym] = max(0.0, val) / total_metric
                else:
                    eq_w = 1.0 / len(selected_symbols)
                    for sym in selected_symbols:
                        weights[sym] = eq_w
            else:
                eq_w = 1.0 / len(selected_symbols)
                for sym in selected_symbols:
                    weights[sym] = eq_w

            # Buy new portfolio
            for sym in selected_symbols:
                price = float(row_prices[sym])
                if price <= 0:
                    continue
                weight = weights.get(sym, 0.0)
                if weight <= 0:
                    continue
                allocation = portfolio_value * weight
                qty = allocation / price
                holdings[sym] = qty
                cash -= allocation
                purchase_prices[sym] = price

                trades.append({
                    "date": available_date.date().isoformat(),
                    "symbol": sym,
                    "action": "buy",
                    "quantity": qty,
                    "price": price,
                    "value": allocation,
                })

                # Track PnL
                if sym not in trade_pnl:
                    trade_pnl[sym] = {"buys": 0.0, "sells": 0.0, "final_val": 0.0}
                trade_pnl[sym]["buys"] += allocation

        # Build daily history and drawdown curve
        portfolio_history: list[dict] = []
        max_value = 0.0

        for dt in prices_df.index:
            row = prices_df.loc[dt]
            value = cash + sum(
                qty * float(row[sym]) for sym, qty in holdings.items()
                if sym in row and pd.notna(row[sym])
            )
            benchmark_value = None
            if benchmark_symbol and benchmark_start and benchmark_symbol in row and pd.notna(row[benchmark_symbol]):
                benchmark_value = initial_capital * (float(row[benchmark_symbol]) / benchmark_start)

            if value > max_value:
                max_value = value
            drawdown = (value - max_value) / max_value if max_value > 0 else 0.0

            portfolio_history.append({
                "date": dt.date().isoformat(),
                "value": value,
                "benchmark_value": benchmark_value,
                "drawdown": round(drawdown, 4),
            })

        # Final holdings
        final_holdings = []
        if portfolio_history:
            last_prices = prices_df.iloc[-1]
            final_value = portfolio_history[-1]["value"]
            for sym, qty in holdings.items():
                if sym not in last_prices or pd.isna(last_prices[sym]):
                    continue
                val = qty * float(last_prices[sym])
                final_holdings.append({
                    "symbol": sym,
                    "weight": val / final_value if final_value else 0,
                    "value": val,
                })
                # Add final holdings value to PnL tracker
                if sym in trade_pnl:
                    trade_pnl[sym]["final_val"] = val

        # Calculate Winners & Losers
        winners_losers_list = []
        for sym, data in trade_pnl.items():
            pnl_val = data["sells"] + data["final_val"] - data["buys"]
            ret = pnl_val / data["buys"] if data["buys"] > 0 else 0.0
            winners_losers_list.append({
                "symbol": sym,
                "pnl": round(pnl_val, 2),
                "return": round(ret, 4)
            })

        sorted_pnl = sorted(winners_losers_list, key=lambda x: x["pnl"], reverse=True)
        top_winners = [x for x in sorted_pnl if x["pnl"] > 0][:5]
        top_losers = sorted([x for x in sorted_pnl if x["pnl"] < 0], key=lambda x: x["pnl"])[:5]

        # Compute general performance metrics
        values = pd.Series([p["value"] for p in portfolio_history])
        metrics = self._compute_metrics(values, initial_capital, start_date, end_date, portfolio_history)

        metrics["winners"] = top_winners
        metrics["losers"] = top_losers

        return {
            "metrics": metrics,
            "portfolio_history": portfolio_history,
            "trades": trades,
            "holdings": final_holdings,
            "holdings_history": holdings_history,
        }

    def _build_candidates(self, as_of: date, universe: set[str] | None = None) -> list[dict[str, Any]]:
        candidates = []
        for stock in self.stock_repo.list_stocks(limit=500):
            if universe is not None and stock.symbol not in universe:
                continue
            fundamental = self.stock_repo.get_fundamental_as_of(stock.id, as_of)
            price = self.stock_repo.get_price_as_of(stock.id, as_of)
            if not fundamental and not price:
                continue

            close_price = price.close if price else None

            candidate = {
                "symbol": stock.symbol,
                "sector": stock.sector,
                "market_cap": fundamental.market_cap if fundamental else None,
                "pe_ratio": fundamental.pe_ratio if fundamental else None,
                "pb_ratio": fundamental.pb_ratio if fundamental else None,
                "dividend_yield": fundamental.dividend_yield if fundamental else None,
                "roe": fundamental.roe if fundamental else None,
                "roce": fundamental.roce if fundamental else None,
                "pat": fundamental.pat if fundamental else None,
                "revenue": fundamental.revenue if fundamental else None,
                "profit_margin": fundamental.profit_margin if fundamental else None,
                "debt_to_equity": fundamental.debt_to_equity if fundamental else None,
                "eps": fundamental.eps if fundamental else None,
                "beta": fundamental.beta if fundamental else None,
                "close": close_price,
            }

            if close_price:
                if fundamental and fundamental.eps and fundamental.eps != 0:
                    candidate["pe_ratio"] = float(close_price / fundamental.eps)
                if fundamental and fundamental.book_value and fundamental.shares_outstanding and fundamental.shares_outstanding > 0:
                    bvps = fundamental.book_value / fundamental.shares_outstanding
                    if bvps != 0:
                        candidate["pb_ratio"] = float(close_price / bvps)
                if fundamental and fundamental.shares_outstanding and fundamental.shares_outstanding > 0:
                    candidate["market_cap"] = float(close_price * fundamental.shares_outstanding)

            candidates.append(candidate)
        return candidates

    def _get_rebalance_dates(
        self, index: pd.DatetimeIndex, frequency: str, start: date, end: date
    ) -> list[date]:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        filtered = index[(index >= start_ts) & (index <= end_ts)]
        if filtered.empty:
            return []

        if frequency == "monthly":
            groups = filtered.to_series().groupby([filtered.year, filtered.month]).first()
        elif frequency == "quarterly":
            groups = filtered.to_series().groupby([filtered.year, filtered.quarter]).first()
        else:
            groups = filtered.to_series().groupby(filtered.year).first()

        return [pd.Timestamp(d).date() for d in groups.values]

    def _compute_metrics(
        self,
        values: pd.Series,
        initial_capital: float,
        start_date: date,
        end_date: date,
        portfolio_history: list[dict],
    ) -> dict[str, float]:
        if values.empty:
            raise ValueError("No portfolio values computed.")

        final_value = float(values.iloc[-1])
        total_return = (final_value - initial_capital) / initial_capital

        years = max((end_date - start_date).days / 365.25, 1 / 365.25)
        cagr = (final_value / initial_capital) ** (1 / years) - 1

        daily_returns = values.pct_change().dropna()
        volatility = float(daily_returns.std() * np.sqrt(252)) if len(daily_returns) > 1 else 0.0
        sharpe = float((daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))) if daily_returns.std() > 0 else 0.0

        rolling_max = values.cummax()
        drawdown = (values - rolling_max) / rolling_max
        max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

        positive_periods = (daily_returns > 0).sum()
        win_rate = float(positive_periods / len(daily_returns)) if len(daily_returns) else 0.0

        benchmark_return = None
        if portfolio_history and portfolio_history[-1].get("benchmark_value"):
            benchmark_return = (
                portfolio_history[-1]["benchmark_value"] - initial_capital
            ) / initial_capital

        return {
            "total_return": round(total_return, 4),
            "cagr": round(cagr, 4),
            "max_drawdown": round(max_drawdown, 4),
            "sharpe_ratio": round(sharpe, 4),
            "volatility": round(volatility, 4),
            "win_rate": round(win_rate, 4),
            "final_value": round(final_value, 2),
            "benchmark_return": round(benchmark_return, 4) if benchmark_return is not None else None,
        }
