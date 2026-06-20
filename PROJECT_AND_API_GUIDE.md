# Equity Backtesting Platform - Complete Project Guide & API Reference

Welcome to the **Equity Backtesting Platform** documentation. This single-file guide contains the complete overview of the project, including its system architecture, data models, backtesting algorithms, and a complete, corrected reference for all 16 API endpoints currently implemented in the codebase.

---

## Table of Contents

1. [Project Overview & Technology Stack](#1-project-overview--technology-stack)
2. [System Architecture & Data Flow](#2-system-architecture--data-flow)
3. [Database Schema & Models](#3-database-schema--models)
4. [Backtesting Engine Algorithm](#4-backtesting-engine-algorithm)
5. [Frontend Structure & Components](#5-frontend-structure--components)
6. [API Authentication & Configuration](#6-api-authentication--configuration)
7. [API Endpoint Reference](#7-api-endpoint-reference)
   - [Stocks Endpoints](#stocks-endpoints)
   - [Strategies Endpoints](#strategies-endpoints)
   - [Backtests Endpoints](#backtests-endpoints)
   - [Dashboard & Export Endpoints](#dashboard--export-endpoints)
   - [Health Check Endpoint](#health-check-endpoint)
8. [Error Handling & API Responses](#8-error-handling--api-responses)
9. [Example Integration Workflows](#9-example-integration-workflows)

---

## 1. Project Overview & Technology Stack

The **Equity Strategy Backtesting Platform** is a production-ready system designed to define, test, and analyze quantitative investing strategies on Indian stocks. Users can synchronize historical stock data, define custom screening and ranking criteria, run backtests over customizable historical periods, evaluate performance metrics (CAGR, Sharpe Ratio, Max Drawdown, etc.), and export the resulting trade logs or portfolio values.

### Core Technologies

*   **Backend API Layer**: Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) (high performance, automatic type-safety, and validation via Pydantic).
*   **Database & ORM**: MySQL 8.0+ as the relational database, managed via [SQLAlchemy ORM](https://www.sqlalchemy.org/).
*   **Frontend Client**: React 18+, [Vite](https://vitejs.dev/) for high-speed builds, [Tailwind CSS](https://tailwindcss.com/) for layout styling, [Zustand](https://github.com/pmndrs/zustand) for global state management, and [Recharts](https://recharts.org/) for plotting interactive portfolio performance and drawdown curves.
*   **Market Data Provider**: Yahoo Finance API (fetching historical daily OHLCV and fundamental metrics like P/E ratio, P/B ratio, ROE, etc.).

---

## 2. System Architecture & Data Flow

The platform is designed around clean separation of concerns, structured into five distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│                 React / TypeScript / Vite               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Dashboard  │ Stocks  │ Strategies │ Backtests   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  State Management: Zustand                       │   │
│  │  Visualization: Recharts, HTML5, Tailwind CSS     │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ JSON / HTTP REST API (Axios client)
                   ▼
┌─────────────────────────────────────────────────────────┐
│                       API LAYER                         │
│                    FastAPI / Python                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Stocks Route  │ Strategies │ Backtests Export  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Pydantic Schema Validation & Serialization      │   │
│  │  CORS Middleware, Global Error Handlers          │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ Dependency Injection
┌─────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  BacktestEngine      │  StrategyEngine           │   │
│  │  YahooFinanceService │  ExportService            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Screening/Ranking, Portfolio History Simulation,│   │
│  │  Performance Metrics Math, CSV/Excel Generators  │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ Repository Pattern
┌─────────────────────────────────────────────────────────┐
│             REPOSITORY LAYER (DATA ACCESS)              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  StockRepository  │  StrategyRepository          │   │
│  │  BacktestRepository                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SQLAlchemy ORM queries, inserts, and updates    │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ Connection Pool
┌─────────────────────────────────────────────────────────┐
│                       DATA LAYER                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │                 MySQL Database                   │   │
│  │  - stocks             - strategies               │   │
│  │  - stock_prices       - backtests                │   │
│  │  - stock_fundamentals                            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Typical Request/Response Flow: Running a Backtest
1. **Frontend Request**: The user fills out parameters (Strategy, Dates, Capital, Rebalance frequency) and clicks "Run Backtest". The frontend component performs client-side validation and sends a `POST /api/backtests` request containing the parameters as a JSON body.
2. **FastAPI Validation**: FastAPI intercepts the request, runs validation rules on the payload against the Pydantic schema `BacktestCreate`, and returns `422 Unprocessable Entity` immediately if types or parameters are wrong.
3. **Route Handler & Database Transaction**: The route controller queries the `StrategyRepository` to verify the strategy exists. It inserts a new `Backtest` record with a status of `"pending"`.
4. **Service Execution**: The route controller calls `BacktestEngine.run()`. The engine fetches historical daily close prices and fundamental tables. It generates the rebalance dates chronologically and simulates the strategy's performance step-by-step.
5. **Database persistence**: The engine updates the `Backtest` record status to `"completed"`, stores calculated metrics (total return, CAGR, Sharpe ratio, max drawdown), daily portfolio value history, executed trade details, and final holdings in serialized JSON columns.
6. **Frontend Render**: The API returns a `201 Created` status with the serialized `BacktestResponse` schema. The React frontend updates its local Zustand state, hides the loading state, and renders charts and transaction lists.

---

## 3. Database Schema & Models

Below are the SQL database table schemas corresponding to the SQLAlchemy models:

### 1. `stocks` Table
Stores basic metadata about equities.
```sql
CREATE TABLE stocks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  symbol VARCHAR(32) UNIQUE NOT NULL,
  name VARCHAR(255) NULL,
  exchange VARCHAR(16) NULL,
  sector VARCHAR(128) NULL,
  industry VARCHAR(128) NULL,
  currency VARCHAR(8) DEFAULT 'INR',
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL
);
```

### 2. `stock_prices` Table
Stores historical daily stock prices.
```sql
CREATE TABLE stock_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stock_id INT NOT NULL,
  date DATE NOT NULL,
  open FLOAT NULL,
  high FLOAT NULL,
  low FLOAT NULL,
  close FLOAT NOT NULL,
  adj_close FLOAT NULL,
  volume BIGINT NULL,
  FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
  UNIQUE(stock_id, date)
);
CREATE INDEX idx_stock_prices_date ON stock_prices(date);
```

### 3. `stock_fundamentals` Table
Stores historical fundamentals used for screening rules.
```sql
CREATE TABLE stock_fundamentals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stock_id INT NOT NULL,
  as_of_date DATE NOT NULL,
  market_cap FLOAT NULL,
  pe_ratio FLOAT NULL,
  pb_ratio FLOAT NULL,
  dividend_yield FLOAT NULL,
  roe FLOAT NULL,
  revenue FLOAT NULL,
  profit_margin FLOAT NULL,
  debt_to_equity FLOAT NULL,
  eps FLOAT NULL,
  beta FLOAT NULL,
  roce FLOAT NULL,
  pat FLOAT NULL,
  FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
  UNIQUE(stock_id, as_of_date)
);
```

### 4. `strategies` Table
Stores custom strategies defined by user rules.
```sql
CREATE TABLE strategies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  description TEXT NULL,
  screening_rules TEXT NOT NULL, -- Serialized JSON array of rules
  ranking_rules TEXT NOT NULL,   -- Serialized JSON array of rules
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL
);
```

### 5. `backtests` Table
Stores the results of backtest runs.
```sql
CREATE TABLE backtests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  strategy_id INT NOT NULL,
  name VARCHAR(128) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  initial_capital FLOAT NOT NULL,
  rebalance_frequency VARCHAR(32) NOT NULL,
  top_n INT NOT NULL,
  position_sizing VARCHAR(32) DEFAULT 'equal',
  position_sizing_metric VARCHAR(64) NULL,
  status VARCHAR(32) NOT NULL, -- pending, running, completed, failed
  metrics TEXT NULL,            -- Serialized JSON object (returns, CAGR, Sharpe)
  portfolio_history TEXT NULL,  -- Serialized JSON array of daily capital points
  trades TEXT NULL,             -- Serialized JSON list of executed transactions
  holdings TEXT NULL,            -- Serialized JSON list of active/final allocations
  holdings_history TEXT NULL,    -- Serialized JSON array of historical holdings
  error_message TEXT NULL,
  created_at DATETIME NOT NULL,
  completed_at DATETIME NULL,
  FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);
```

---

## 4. Backtesting Engine Algorithm

The core execution path inside `BacktestEngine.run()` simulates historical portfolio management:

```
[Start Backtest Engine]
       │
       ▼
1. Load historical daily price matrix for all stock symbols.
2. Load fundamental metric history for screening/ranking.
3. Generate chronological rebalance dates based on frequency:
   - "monthly": first trading day of each month
   - "quarterly": first trading day of each calendar quarter
   - "yearly": first trading day of each year
       │
       ▼
   [For Each Rebalance Date] ◄─────────────────────────────────────────┐
   ├── a. Filter Candidate Pool                                        │
   │      - Extract fundamentals active as of the rebalance date.      │
   │      - Apply screening rules (e.g. pe_ratio < 25 AND roe > 15).   │
   │                                                                   │
   ├── b. Score and Rank Candidates                                    │
   │      - Score remaining candidates using weighted ranking rules.   │
   │      - Formula: Score = Sum(Metric_Value * Weight * Direction)    │
   │      - Sort candidates in descending order of score.              │
   │                                                                   │
   ├── c. Select Top N Equities                                        │
   │      - Take the first N stocks from the ranked list.              │
   │                                                                   │
   └── d. Execute Rebalancing & Sizing                                 │
          - Liquidate previous holdings to free up cash.               │
          - Calculate new positions based on Sizing Method:            │
             * "equal": Weight = 1.0 / N                               │
             * "weighted": Weight proportional to a sizing metric      │
          - Save executed transaction logs.                            │
                                                                       │
   [Next Rebalance Date] ──────────────────────────────────────────────┘
       │
       ▼
4. Simulate daily portfolio valuation:
   - For every trading day, calculate: Cash + Sum(Quantity_held * Close_price_t)
   - Compute drawdown curve relative to local peak.
5. Compute overall backtest metrics:
   - Total Return: (Final Value - Initial Capital) / Initial Capital
   - CAGR: (Final Value / Initial Capital) ^ (365 / days_elapsed) - 1
   - Annualized Volatility: StdDev(Daily Returns) * sqrt(252)
   - Sharpe Ratio: (CAGR - RiskFreeRate) / Annualized Volatility
   - Win Rate: Count(Profitable Trades) / Count(Total Trades)
6. Write results as JSON into DB and mark status as "completed".
```

---

## 5. Frontend Structure & Components

The frontend client is structured cleanly around a Single Page Application (SPA) dashboard layout.

### Component Structure
*   `App.tsx`: Sets up routes and displays the navigation sidebar/header.
*   `store/useAppStore.ts`: Global state container (Zustand) managing shared stocks, strategies, backtests, active items, and dashboard metrics.
*   `pages/DashboardPage.tsx`: Displays high-level KPIs (Total Stocks, Total Strategies, Total Backtests, Average CAGR) and lists recent backtests.
*   `pages/StocksPage.tsx`: Displays tables of synchronized stocks, allows triggering new data syncs from Yahoo Finance, and opens detailed stock modal overlays.
*   `pages/StrategiesPage.tsx`: Allows creation, view, edit, and deletion of strategies using an interactive builder interface for screening/ranking rules.
*   `pages/BacktestsPage.tsx`: Offers a configuration wizard to run backtests (select strategy, date range, initial capital, rebalance frequency, and sizing) and shows the backtest run history.
*   `pages/BacktestDetailPage.tsx`: Features interactive Recharts plots showing the daily portfolio value vs. benchmark, drawdown curves, trade history logs, and final stock holdings.

---

## 6. API Authentication & Configuration

### CORS Policies
The backend comes equipped with CORS headers enabled for integration with frontend environments:
```python
# app/core/config.py
settings.cors_origin_list = ["http://localhost:5173", "http://localhost:3000"]
```

### Request Headers
Clients should specify appropriate content headers:
*   `Content-Type`: `application/json` (Required for `POST` and `PUT` request bodies)
*   `Accept`: `application/json`

### Base API URL
All API paths listed below are relative to:
```
http://localhost:8000/api
```

---

## 7. API Endpoint Reference

### Stocks Endpoints

#### 1. List All Stocks
*   **Method**: `GET`
*   **Path**: `/stocks`
*   **Description**: Retrieves a paginated list of all stocks available in the system database.
*   **Query Parameters**:
    *   `skip` (integer, optional, default: `0`, range: `≥ 0`): Pagination offset.
    *   `limit` (integer, optional, default: `100`, range: `1` to `500`): Maximum stocks to return.
*   **Response Format**: `list[StockResponse]`
*   **Success Response (`200 OK`)**:
    ```json
    [
      {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services Limited",
        "exchange": "NSE",
        "sector": "Information Technology",
        "industry": "IT Consulting & Services",
        "currency": "INR",
        "id": 1,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-06-19T14:22:00"
      }
    ]
    ```

---

#### 2. Get Stock Details
*   **Method**: `GET`
*   **Path**: `/stocks/{symbol}`
*   **Description**: Fetch stock metadata, latest daily price data, and latest fundamental metrics.
*   **Path Parameters**:
    *   `symbol` (string, required): The stock symbol (e.g. `TCS.NS`, `INFY.NS`).
*   **Response Format**: `StockDetailResponse`
*   **Success Response (`200 OK`)**:
    ```json
    {
      "id": 1,
      "symbol": "TCS.NS",
      "name": "Tata Consultancy Services Limited",
      "exchange": "NSE",
      "sector": "Information Technology",
      "industry": "IT Consulting & Services",
      "currency": "INR",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-06-19T14:22:00",
      "latest_price": {
        "date": "2024-06-19",
        "open": 3450.5,
        "high": 3485.25,
        "low": 3440.0,
        "close": 3475.5,
        "adj_close": 3475.5,
        "volume": 2850000
      },
      "latest_fundamental": {
        "as_of_date": "2024-06-19",
        "market_cap": 14500000000000.0,
        "pe_ratio": 28.5,
        "pb_ratio": 6.2,
        "dividend_yield": 1.8,
        "roe": 35.2,
        "revenue": 285000000000.0,
        "profit_margin": 22.5,
        "debt_to_equity": 0.15,
        "eps": 122.0,
        "beta": 0.85,
        "roce": 42.1,
        "pat": 45000000000.0
      }
    }
    ```
*   **Error Response (`404 Not Found`)**:
    ```json
    { "detail": "Stock not found" }
    ```

---

#### 3. Get Historical Price Data
*   **Method**: `GET`
*   **Path**: `/stocks/{symbol}/prices`
*   **Description**: Get historical stock prices between a given date range.
*   **Path Parameters**:
    *   `symbol` (string, required): Stock ticker symbol.
*   **Query Parameters**:
    *   `start_date` (string, optional, format `YYYY-MM-DD`): Start date of data. Default is `2019-01-01`.
    *   `end_date` (string, optional, format `YYYY-MM-DD`): End date of data. Default is today.
*   **Response Format**: `list[StockPriceResponse]`
*   **Success Response (`200 OK`)**:
    ```json
    [
      {
        "date": "2024-06-18",
        "open": 3440.0,
        "high": 3465.5,
        "low": 3430.25,
        "close": 3450.5,
        "adj_close": 3450.5,
        "volume": 2750000
      },
      {
        "date": "2024-06-19",
        "open": 3450.5,
        "high": 3485.25,
        "low": 3440.0,
        "close": 3475.5,
        "adj_close": 3475.5,
        "volume": 2850000
      }
    ]
    ```
*   **Error Responses**:
    *   `404 Not Found`: Stock symbol not database registered.
    *   `400 Bad Request`: Invalid ISO date format.

---

#### 4. Sync Stock Data from Yahoo Finance
*   **Method**: `POST`
*   **Path**: `/stocks/sync`
*   **Description**: Fetches recent historical stock price logs and fundamental data directly from Yahoo Finance API.
*   **Request Body (`StockSyncRequest`)**:
    ```json
    {
      "symbols": ["TCS.NS", "INFY.NS", "WIPRO.NS"],
      "period": "5y"
    }
    ```
    *   `symbols` (array of strings, optional): List of tickers. If omitted, uses default watchlist.
    *   `period` (string, default: `"5y"`): Timeframe of historical prices to download. Options: `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `max`.
*   **Response Format**: `StockSyncResponse`
*   **Success Response (`200 OK`)**:
    ```json
    {
      "synced": ["TCS.NS", "INFY.NS"],
      "failed": ["WIPRO.NS"],
      "message": "Synced 2 stocks, 1 failed."
    }
    ```

---

### Strategies Endpoints

#### 5. List All Strategies
*   **Method**: `GET`
*   **Path**: `/strategies`
*   **Description**: Fetch all screening and ranking strategies defined in the system.
*   **Response Format**: `list[StrategyResponse]`
*   **Success Response (`200 OK`)**:
    ```json
    [
      {
        "id": 1,
        "name": "High Quality Value Strategy",
        "description": "Select low PE value stocks with high return on equity",
        "screening_rules": [
          {
            "field": "pe_ratio",
            "operator": "lt",
            "value": 25.0
          },
          {
            "field": "roe",
            "operator": "gte",
            "value": 15.0
          }
        ],
        "ranking_rules": [
          {
            "field": "pe_ratio",
            "direction": "asc",
            "weight": 0.5
          },
          {
            "field": "roe",
            "direction": "desc",
            "weight": 0.5
          }
        ],
        "created_at": "2024-06-19T10:00:00",
        "updated_at": "2024-06-19T10:00:00"
      }
    ]
    ```

---

#### 6. Create New Strategy
*   **Method**: `POST`
*   **Path**: `/strategies`
*   **Description**: Save a new screening/ranking strategy configuration.
*   **Request Body (`StrategyCreate`)**:
    ```json
    {
      "name": "Growth At Reasonable Price (GARP)",
      "description": "Mid-range PE stocks with robust ROE and growth",
      "screening_rules": [
        {
          "field": "pe_ratio",
          "operator": "between",
          "value": [12.0, 35.0]
        },
        {
          "field": "roe",
          "operator": "gt",
          "value": 18.0
        }
      ],
      "ranking_rules": [
        {
          "field": "roe",
          "direction": "desc",
          "weight": 0.7
        },
        {
          "field": "dividend_yield",
          "direction": "desc",
          "weight": 0.3
        }
      ]
    }
    ```
    *   **Rule operators**: `gt`, `gte`, `lt`, `lte`, `eq`, `between`.
    *   **Supported fields**: `pe_ratio`, `pb_ratio`, `dividend_yield`, `roe`, `revenue`, `profit_margin`, `debt_to_equity`, `eps`, `beta`, `roce`, `pat`, `market_cap`.
*   **Response Format**: `StrategyResponse`
*   **Success Response (`201 Created`)**:
    ```json
    {
      "id": 2,
      "name": "Growth At Reasonable Price (GARP)",
      "description": "Mid-range PE stocks with robust ROE and growth",
      "screening_rules": [...],
      "ranking_rules": [...],
      "created_at": "2024-06-20T09:00:00",
      "updated_at": "2024-06-20T09:00:00"
    }
    ```
*   **Error Response (`422 Unprocessable Entity`)**: Validation failed (e.g. operator string misspelled).

---

#### 7. Get Strategy Details
*   **Method**: `GET`
*   **Path**: `/strategies/{strategy_id}`
*   **Description**: Get configuration parameters for a specific strategy ID.
*   **Path Parameters**:
    *   `strategy_id` (integer, required): Strategy unique index.
*   **Response Format**: `StrategyResponse`
*   **Success Response (`200 OK`)**:
    ```json
    {
      "id": 2,
      "name": "Growth At Reasonable Price (GARP)",
      "description": "Mid-range PE stocks with robust ROE and growth",
      "screening_rules": [...],
      "ranking_rules": [...],
      "created_at": "2024-06-20T09:00:00",
      "updated_at": "2024-06-20T09:00:00"
    }
    ```
*   **Error Response (`404 Not Found`)**:
    ```json
    { "detail": "Strategy not found" }
    ```

---

#### 8. Update Strategy
*   **Method**: `PUT`
*   **Path**: `/strategies/{strategy_id}`
*   **Description**: Updates fields and rules of a strategy. All fields are optional inside payload.
*   **Path Parameters**:
    *   `strategy_id` (integer, required): Target strategy identifier.
*   **Request Body (`StrategyUpdate`)**:
    ```json
    {
      "name": "Modified GARP Strategy",
      "screening_rules": [
        {
          "field": "pe_ratio",
          "operator": "lt",
          "value": 30.0
        }
      ]
    }
    ```
*   **Response Format**: `StrategyResponse`
*   **Success Response (`200 OK`)**: Updated strategy object returned.
*   **Error Response (`404 Not Found`)**: Target strategy id missing.

---

#### 9. Delete Strategy
*   **Method**: `DELETE`
*   **Path**: `/strategies/{strategy_id}`
*   **Description**: Delete strategy and all associated historical backtest run records from database.
*   **Path Parameters**:
    *   `strategy_id` (integer, required): Target strategy id.
*   **Success Response (`204 No Content`)**:
    *   No content returned in response body.
*   **Error Response (`404 Not Found`)**: Strategy does not exist.

---

### Backtests Endpoints

#### 10. List All Backtests
*   **Method**: `GET`
*   **Path**: `/backtests`
*   **Description**: Fetch all executed and pending backtests from the platform databases.
*   **Response Format**: `list[BacktestResponse]`
*   **Success Response (`200 OK`)**:
    ```json
    [
      {
        "id": 1,
        "strategy_id": 2,
        "name": "GARP Run - 5 Year",
        "start_date": "2019-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 1000000.0,
        "rebalance_frequency": "monthly",
        "top_n": 5,
        "position_sizing": "equal",
        "position_sizing_metric": null,
        "status": "completed",
        "metrics": {
          "total_return": 1.254,
          "cagr": 0.1765,
          "max_drawdown": -0.185,
          "sharpe_ratio": 1.45,
          "volatility": 0.1217,
          "win_rate": 0.65,
          "final_value": 2254000.0,
          "benchmark_return": 0.72
        },
        "created_at": "2024-06-20T09:15:00",
        "completed_at": "2024-06-20T09:16:05"
      }
    ]
    ```

---

#### 11. Run New Backtest
*   **Method**: `POST`
*   **Path**: `/backtests`
*   **Description**: Runs the backtest simulator using the defined strategy rules. Runs synchronously and updates parameters in database.
*   **Request Body (`BacktestCreate`)**:
    ```json
    {
      "strategy_id": 2,
      "name": "GARP Backtest - Run 2",
      "start_date": "2020-01-01",
      "end_date": "2024-01-01",
      "initial_capital": 500000.0,
      "rebalance_frequency": "monthly",
      "top_n": 5,
      "position_sizing": "equal",
      "position_sizing_metric": null
    }
    ```
    *   `rebalance_frequency`: Options: `monthly`, `quarterly`, `yearly`.
    *   `top_n` (integer, default `5`, range `1` to `50`): Max stocks to hold.
    *   `position_sizing`: Weight allocation method (e.g. `"equal"` or `"weighted"`).
    *   `position_sizing_metric` (string, optional): Column name if ranking rules determine weights.
*   **Response Format**: `BacktestResponse`
*   **Success Response (`201 Created`)**:
    ```json
    {
      "id": 2,
      "strategy_id": 2,
      "name": "GARP Backtest - Run 2",
      "start_date": "2020-01-01",
      "end_date": "2024-01-01",
      "initial_capital": 500000.0,
      "rebalance_frequency": "monthly",
      "top_n": 5,
      "position_sizing": "equal",
      "position_sizing_metric": null,
      "status": "completed",
      "metrics": {
        "total_return": 0.842,
        "cagr": 0.165,
        "max_drawdown": -0.154,
        "sharpe_ratio": 1.32,
        "volatility": 0.125,
        "win_rate": 0.62,
        "final_value": 921000.0,
        "benchmark_return": 0.54
      },
      "portfolio_history": [
        {
          "date": "2020-01-01",
          "value": 500000.0,
          "benchmark_value": 500000.0,
          "drawdown": 0.0
        }
      ],
      "trades": [
        {
          "date": "2020-01-01",
          "symbol": "TCS.NS",
          "action": "buy",
          "quantity": 29.0,
          "price": 3450.0,
          "value": 100050.0
        }
      ],
      "holdings": [
        {
          "symbol": "TCS.NS",
          "weight": 0.2,
          "value": 100050.0
        }
      ],
      "holdings_history": [],
      "error_message": null,
      "created_at": "2024-06-20T09:20:00",
      "completed_at": "2024-06-20T09:20:30"
    }
    ```
*   **Error Responses**:
    *   `404 Not Found`: Strategy ID not found.
    *   `400 Bad Request`: `start_date` must be before `end_date`.

---

#### 12. Get Backtest Results
*   **Method**: `GET`
*   **Path**: `/backtests/{backtest_id}`
*   **Description**: Retrieves daily valuation records, trade logs, and metrics of a backtest.
*   **Path Parameters**:
    *   `backtest_id` (integer, required): ID of target backtest.
*   **Response Format**: `BacktestResponse`
*   **Success Response (`200 OK`)**: Complete backtest detail object.
*   **Error Response (`404 Not Found`)**: Backtest record does not exist.

---

### Dashboard & Export Endpoints

#### 13. Get Dashboard Stats
*   **Method**: `GET`
*   **Path**: `/dashboard/stats`
*   **Description**: Get platform aggregation KPIs and the latest 5 run backtests.
*   **Response Format**: `DashboardStats`
*   **Success Response (`200 OK`)**:
    ```json
    {
      "total_stocks": 150,
      "total_strategies": 5,
      "total_backtests": 12,
      "completed_backtests": 11,
      "avg_cagr": 0.1852,
      "recent_backtests": [
        {
          "id": 2,
          "strategy_id": 2,
          "name": "GARP Backtest - Run 2",
          "status": "completed",
          "metrics": { ... }
        }
      ]
    }
    ```

---

#### 14. Export Backtest to CSV
*   **Method**: `GET`
*   **Path**: `/export/{backtest_id}/csv`
*   **Description**: Returns a downloadable CSV file containing specific components of the backtest.
*   **Path Parameters**:
    *   `backtest_id` (integer, required): ID of target backtest.
*   **Query Parameters**:
    *   `export_type` (string, optional, default: `"portfolio"`): Target table component. Options: `"portfolio"` (daily values), `"trades"` (full transaction lists), or `"holdings"` (final holdings allocation). Matches regex pattern `^(portfolio|trades|holdings)$`.
*   **Success Response (`200 OK`)**:
    *   Returns header `Content-Disposition: attachment; filename=backtest_12_portfolio.csv` containing raw CSV rows.
*   **Error Response (`400 Bad Request`)**: Invalid export type parameter.

---

#### 15. Export Backtest to Excel
*   **Method**: `GET`
*   **Path**: `/export/{backtest_id}/excel`
*   **Description**: Generates and downloads a multi-sheet Microsoft Excel `.xlsx` workbook containing all backtest outputs (Summary Metrics, Daily Portfolio Valuation, Trade log, and Final Holdings) formatted cleanly.
*   **Path Parameters**:
    *   `backtest_id` (integer, required): ID of target backtest.
*   **Success Response (`200 OK`)**:
    *   Returns header `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` containing the spreadsheet stream.

---

### Health Check Endpoint

#### 16. Health Status Endpoint
*   **Method**: `GET`
*   **Path**: `/health`
*   **Description**: Simple service uptime check.
*   **Success Response (`200 OK`)**:
    ```json
    {
      "status": "ok",
      "app": "Equity Strategy Backtesting Platform",
      "version": "1.0.0"
    }
    ```

---

## 8. Error Handling & API Responses

The platform uses a standardized, uniform error structure returning clear explanations.

### Standard Schema: `MessageResponse`
```json
{
  "detail": "Descriptive error message string"
}
```

### Common HTTP Status Reference

| Status Code | Type | Meaning | Common Cause |
| :--- | :--- | :--- | :--- |
| **`200 OK`** | Success | Request succeeded | Standard retrieval requests (`GET`) |
| **`201 Created`** | Success | Resource saved | Saving strategies or spawning new backtests (`POST`) |
| **`204 No Content`** | Success | Resource deleted | Strategy deletion completed (`DELETE`) |
| **`400 Bad Request`** | Client Error | Invalid parameters | `start_date` after `end_date`, invalid export request |
| **`404 Not Found`** | Client Error | Resource missing | Requested stock ticker or strategy ID not in DB |
| **`422 Unprocessable`** | Client Error | JSON validation failed | Missing parameters or type mismatch in request payload |
| **`500 Server Error`** | Server Error | Database failure | Loss of DB connection, Yahoo Finance rate-limiting limits |

---

## 9. Example Integration Workflows

### Scenario 1: Setup a Strategy and Run a Backtest
```
[Client]                                                        [API Server]
   │                                                                 │
   │ 1. Sync Stock Tickers                                           │
   ├───────────────── POST /api/stocks/sync ────────────────────────►│
   │                  { "symbols": ["TCS.NS", "INFY.NS"], "period": "5y" }
   │                                                                 │
   │◄──────────────── Sync Confirmation (200 OK) ────────────────────┤
   │                                                                 │
   │ 2. Create Strategy                                              │
   ├───────────────── POST /api/strategies ─────────────────────────►│
   │                  { "name": "IT Value", "screening_rules": ... } │
   │                                                                 │
   │◄──────────────── Strategy Details with ID (201 Created) ────────┤
   │                                                                 │
   │ 3. Execute Backtest                                             │
   ├───────────────── POST /api/backtests ──────────────────────────►│
   │                  { "strategy_id": 1, "name": "Backtest 1", ... }│
   │                                                                 │
   │◄──────────────── Detailed Metrics & History (210 Created) ──────┤
   │                                                                 │
   │ 4. Download Spreadsheet                                         │
   ├───────────────── GET /api/export/1/excel ──────────────────────►│
   │                                                                 │
   │◄──────────────── Excel Binary Stream (200 OK) ──────────────────┤
   │                                                                 │
```

### Scenario 2: Rendering Stock Dashboard and Price Chart
1. **Load Dashboard**: React calls `GET /api/dashboard/stats` to render KPIs card.
2. **Display Watchlist**: React calls `GET /api/stocks?limit=50` to list stock rows.
3. **Show Chart**: Clicking a stock symbol executes `GET /api/stocks/TCS.NS/prices?start_date=2023-01-01` to supply data points to Recharts line charts.
