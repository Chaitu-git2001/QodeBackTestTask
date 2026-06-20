import json
from datetime import date, datetime

import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.stock import Stock, StockFundamental, StockPrice
from app.repositories.stock_repository import StockRepository


class YahooFinanceService:
    def __init__(self, db: Session):
        self.repo = StockRepository(db)

    def sync_symbols(self, symbols: list[str] | None = None, period: str = "5y") -> tuple[list[str], list[str]]:
        symbols = symbols or settings.default_stock_list
        synced: list[str] = []
        failed: list[str] = []

        from concurrent.futures import ThreadPoolExecutor, as_completed
        from app.core.database import SessionLocal

        def sync_worker(symbol: str):
            db = SessionLocal()
            try:
                service = YahooFinanceService(db)
                service._sync_single(symbol, period)
                return symbol, True, None
            except Exception as e:
                return symbol, False, str(e)
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(sync_worker, s.strip().upper()) for s in symbols if s.strip()]
            for future in as_completed(futures):
                sym, success, err = future.result()
                if success:
                    synced.append(sym)
                else:
                    print(f"Error syncing {sym}: {err}")
                    failed.append(sym)

        return synced, failed

    def _sync_single(self, symbol: str, period: str) -> Stock:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        history = ticker.history(period=period, auto_adjust=False)

        if history.empty:
            raise ValueError(f"No price history for {symbol}")

        stock = Stock(
            symbol=symbol,
            name=info.get("longName") or info.get("shortName") or symbol,
            exchange=info.get("exchange") or ("NSE" if symbol.endswith(".NS") else "BSE"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            currency=info.get("currency", "INR"),
        )
        stock = self.repo.upsert_stock(stock)

        prices = []
        for idx, row in history.iterrows():
            prices.append(
                StockPrice(
                    stock_id=stock.id,
                    date=idx.date(),
                    open=float(row["Open"]) if row.get("Open") is not None else None,
                    high=float(row["High"]) if row.get("High") is not None else None,
                    low=float(row["Low"]) if row.get("Low") is not None else None,
                    close=float(row["Close"]),
                    adj_close=float(row.get("Adj Close", row["Close"])),
                    volume=int(row["Volume"]) if row.get("Volume") is not None else None,
                )
            )
        self.repo.bulk_upsert_prices(stock.id, prices)

        # Fetch statements
        financials = ticker.financials
        bs = ticker.balance_sheet
        cf = ticker.cashflow

        # Helper to safely retrieve values from a dataframe row at a date index
        def _get_row(df, row_name, col_name) -> float | None:
            if df is None or df.empty or row_name not in df.index:
                return None
            try:
                val = df.loc[row_name, col_name]
                if isinstance(val, pd.Series):
                    val = val.iloc[0]
                if pd.isna(val) or val is None or (isinstance(val, float) and np.isnan(val)):
                    return None
                return float(val)
            except Exception:
                return None

        # Gather all report dates
        all_dates = set()
        if financials is not None and not financials.empty:
            all_dates.update(financials.columns)
        if bs is not None and not bs.empty:
            all_dates.update(bs.columns)
        if cf is not None and not cf.empty:
            all_dates.update(cf.columns)

        sorted_dates = sorted(list(all_dates))

        # Check if we successfully got any historical statement dates
        if sorted_dates:
            for dt in sorted_dates:
                report_date = dt.date()

                # Extract statement values
                rev = _get_row(financials, "Total Revenue", dt)
                net_income = _get_row(financials, "Net Income", dt)
                ebit = _get_row(financials, "EBIT", dt)
                eps = _get_row(financials, "Basic EPS", dt) or _get_row(financials, "Diluted EPS", dt)

                assets = _get_row(bs, "Total Assets", dt)
                curr_liab = _get_row(bs, "Current Liabilities", dt)
                equity = _get_row(bs, "Stockholders Equity", dt) or _get_row(bs, "Common Stock Equity", dt)
                total_debt = _get_row(bs, "Total Debt", dt)
                shares = _get_row(bs, "Ordinary Shares Number", dt) or _get_row(bs, "Share Issued", dt)

                op_cf = _get_row(cf, "Operating Cash Flow", dt)
                fcf = _get_row(cf, "Free Cash Flow", dt)

                # Compute ratios
                roce = None
                if ebit is not None and assets is not None and curr_liab is not None:
                    cap_employed = assets - curr_liab
                    if cap_employed > 0:
                        roce = float((ebit / cap_employed) * 100)

                roe = None
                if net_income is not None and equity is not None and equity > 0:
                    roe = float((net_income / equity) * 100)

                debt_to_equity = None
                if total_debt is not None and equity is not None and equity > 0:
                    debt_to_equity = float(total_debt / equity)

                profit_margin = None
                if net_income is not None and rev is not None and rev > 0:
                    profit_margin = float(net_income / rev)

                fundamental = StockFundamental(
                    stock_id=stock.id,
                    as_of_date=report_date,
                    revenue=rev,
                    pat=net_income,
                    ebit=ebit,
                    total_assets=assets,
                    current_liabilities=curr_liab,
                    book_value=equity,
                    total_debt=total_debt,
                    shares_outstanding=shares,
                    operating_cash_flow=op_cf,
                    free_cash_flow=fcf,
                    eps=eps,
                    roe=roe,
                    roce=roce,
                    debt_to_equity=debt_to_equity,
                    profit_margin=profit_margin,
                    dividend_yield=_safe_float(info.get("dividendYield")),
                    beta=_safe_float(info.get("beta")),
                )

                # Lookup price in DB for report_date to calculate pe, pb, market_cap for this record
                db_price = self.repo.get_price_on_date(stock.id, report_date)
                close_price = db_price.close if db_price else None

                if close_price and eps:
                    fundamental.pe_ratio = float(close_price / eps)
                else:
                    fundamental.pe_ratio = _safe_float(info.get("trailingPE") or info.get("forwardPE"))

                if close_price and equity and shares and shares > 0:
                    bvps = equity / shares
                    fundamental.pb_ratio = float(close_price / bvps)
                else:
                    fundamental.pb_ratio = _safe_float(info.get("priceToBook"))

                if close_price and shares and shares > 0:
                    fundamental.market_cap = float(close_price * shares)
                else:
                    fundamental.market_cap = _safe_float(info.get("marketCap"))

                self.repo.upsert_fundamental(fundamental)
        else:
            # Fallback to info dict if no statement data was retrieved
            roe_val = _safe_float(info.get("returnOnEquity"))
            fundamental = StockFundamental(
                stock_id=stock.id,
                as_of_date=date.today(),
                market_cap=_safe_float(info.get("marketCap")),
                pe_ratio=_safe_float(info.get("trailingPE") or info.get("forwardPE")),
                pb_ratio=_safe_float(info.get("priceToBook")),
                dividend_yield=_safe_float(info.get("dividendYield")),
                roe=roe_val * 100 if roe_val is not None else None,
                revenue=_safe_float(info.get("totalRevenue")),
                profit_margin=_safe_float(info.get("profitMargins")),
                debt_to_equity=_safe_float(info.get("debtToEquity")),
                eps=_safe_float(info.get("trailingEps")),
                beta=_safe_float(info.get("beta")),
                pat=_safe_float(info.get("netIncomeToCommon") or info.get("netIncome")),
                roce=roe_val * 100 if roe_val is not None else None, # fallback
            )
            self.repo.upsert_fundamental(fundamental)

        return stock


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
