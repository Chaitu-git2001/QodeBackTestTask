# Equity Backtesting Platform - Complete Setup & Implementation Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Database Setup](#database-setup)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Running the Application](#running-the-application)
8. [Key Features](#key-features)
9. [How It Works](#how-it-works)
10. [Code Structure](#code-structure)
11. [Testing Workflows](#testing-workflows)

---

## Project Overview

**Equity Strategy Backtesting Platform** is a full-stack web application that allows users to:

- ✅ Fetch real-time stock data from Yahoo Finance
- ✅ Define custom fundamental-based screening and ranking strategies
- ✅ Run historical backtests on Indian stocks (NSE/BSE)
- ✅ Analyze performance metrics (Returns, Sharpe Ratio, Max Drawdown, etc.)
- ✅ Compare multiple strategies
- ✅ Export backtest results (CSV, Excel)
- ✅ Track portfolio holdings and trade history

---

## Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React/TypeScript)            │
│         - Strategy Builder UI                           │
│         - Backtest Runner                              │
│         - Performance Charts & Dashboard                │
└────────────────────┬────────────────────────────────────┘
                     │ (REST API calls)
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI/Python)                    │
│  Routes:  /stocks | /strategies | /backtests | /export  │
├────────────────────────────────────────────────────────┤
│  Services:                                              │
│  - YahooFinanceService (data fetching)                 │
│  - BacktestEngine (strategy execution)                 │
│  - StrategyEngine (screening & ranking)                │
│  - ExportService (CSV/Excel generation)                │
├────────────────────────────────────────────────────────┤
│  Database Layer:                                        │
│  - StockRepository                                      │
│  - StrategyRepository                                   │
│  - BacktestRepository                                   │
└────────────────────┬────────────────────────────────────┘
                     │ (SQLAlchemy ORM)
┌────────────────────▼────────────────────────────────────┐
│              MySQL Database                              │
│  Tables: stocks | stock_prices | stock_fundamentals   │
│          strategies | backtests                         │
└──────────────────────────────────────────────────────────┘

External:
┌──────────────────────────┐
│   Yahoo Finance API      │
│   (Data Provider)        │
└──────────────────────────┘
```

### Data Flow

```
1. Data Ingestion:
   Frontend/User → POST /stocks/sync → Yahoo Finance API → Database

2. Strategy Definition:
   Frontend → POST /strategies → Validation → Database

3. Backtest Execution:
   Frontend → POST /backtests → BacktestEngine →
   StrategyEngine (screening/ranking) → Portfolio Calculation → Database

4. Results Retrieval:
   Frontend → GET /backtests/{id} → Database → JSON Response
```

---

## Prerequisites

### System Requirements

- **OS:** Windows 10+, macOS 10.15+, or Linux
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 2GB for database and dependencies

### Software Requirements

#### Backend

- **Python:** 3.11 or higher
- **MySQL:** 8.0 or higher
- **pip:** Python package manager

#### Frontend

- **Node.js:** 18.0 or higher
- **npm:** 9.0 or higher

### Verify Installations

```bash
# Check Python
python --version

# Check Node.js
node --version
npm --version

# Check MySQL (if installed locally)
mysql --version
```

---

## Database Setup

### Option 1: Local MySQL Installation

#### Windows (PowerShell)

```powershell
# Run the initialization script
.\backend\scripts\init-local-mysql.ps1
```

#### macOS/Linux (Bash)

```bash
# Install MySQL using Homebrew (macOS)
brew install mysql
brew services start mysql

# Or use the SQL script directly
mysql -u root -p < backend/scripts/init-local-mysql.sql
```

### Option 2: Docker Setup (Recommended)

```bash
# Start MySQL in Docker
docker run -d `
  --name equity-mysql `
  -e MYSQL_ROOT_PASSWORD=root_password `
  -e MYSQL_DATABASE=equity_backtest `
  -p 3306:3306 `
  mysql:8.0

# Verify connection
mysql -h localhost -u root -p -e "SELECT 1"
```

### Database Schema

The following tables are automatically created on first run:

#### `stocks` Table

```sql
CREATE TABLE stocks (
  id INT PRIMARY KEY AUTO_INCREMENT,
  symbol VARCHAR(32) UNIQUE NOT NULL,
  name VARCHAR(255),
  exchange VARCHAR(16),
  sector VARCHAR(128),
  industry VARCHAR(128),
  currency VARCHAR(8) DEFAULT 'INR',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `stock_prices` Table

```sql
CREATE TABLE stock_prices (
  id INT PRIMARY KEY AUTO_INCREMENT,
  stock_id INT NOT NULL,
  date DATE NOT NULL,
  open FLOAT,
  high FLOAT,
  low FLOAT,
  close FLOAT NOT NULL,
  adj_close FLOAT,
  volume INT,
  UNIQUE(stock_id, date),
  FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
```

#### `stock_fundamentals` Table

```sql
CREATE TABLE stock_fundamentals (
  id INT PRIMARY KEY AUTO_INCREMENT,
  stock_id INT NOT NULL,
  as_of_date DATE NOT NULL,
  market_cap FLOAT,
  pe_ratio FLOAT,
  pb_ratio FLOAT,
  dividend_yield FLOAT,
  roe FLOAT,
  revenue FLOAT,
  profit_margin FLOAT,
  debt_to_equity FLOAT,
  eps FLOAT,
  beta FLOAT,
  UNIQUE(stock_id, as_of_date),
  FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
```

#### `strategies` Table

```sql
CREATE TABLE strategies (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL,
  description TEXT,
  screening_rules TEXT NOT NULL DEFAULT '[]',
  ranking_rules TEXT NOT NULL DEFAULT '[]',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `backtests` Table

```sql
CREATE TABLE backtests (
  id INT PRIMARY KEY AUTO_INCREMENT,
  strategy_id INT NOT NULL,
  name VARCHAR(128) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  initial_capital FLOAT DEFAULT 1000000,
  rebalance_frequency VARCHAR(32) DEFAULT 'monthly',
  top_n INT DEFAULT 5,
  status VARCHAR(32) DEFAULT 'pending',
  metrics TEXT,
  portfolio_history TEXT,
  trades TEXT,
  holdings TEXT,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);
```

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Python Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**

- `fastapi[all]` - Web framework
- `sqlalchemy` - ORM for database
- `pydantic` - Data validation
- `yfinance` - Yahoo Finance data
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `python-multipart` - File upload support
- `openpyxl` - Excel export
- `mysql-connector-python` - MySQL driver

### Step 4: Configure Environment Variables

Create a `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=mysql://root:password@localhost:3306/equity_backtest
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=equity_backtest

# Application
APP_NAME=Equity Backtesting Platform
APP_VERSION=1.0.0
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Default Stocks (for sync)
DEFAULT_STOCK_LIST=TCS.NS,INFY.NS,WIPRO.NS,HCLTECH.NS,TECHM.NS,BAJAJFINSV.NS,HDFC.NS,ICICIBANK.NS,AXISBANK.NS,KOTAKBANK.NS
```

### Step 5: Initialize Database

```bash
python -m app.core.database
```

This command will:

- Create all tables if they don't exist
- Set up relationships between tables
- Initialize indexes for performance

### Step 6: Verify Backend Setup

```bash
# Run health check
python -c "from app.main import app; print('✓ Backend ready')"
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

**Key Dependencies:**

- `react` - UI framework
- `typescript` - Type safety
- `vite` - Build tool
- `tailwindcss` - Styling
- `axios` - HTTP client
- `recharts` - Charting library
- `react-router-dom` - Navigation
- `zustand` - State management

### Step 3: Configure API Endpoint

Create `.env.local` file in `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000/api
```

### Step 4: Build Frontend Components

The frontend comes with pre-built components:

**Components Structure:**

```
src/
├── components/
│   ├── ErrorAlert.tsx          # Error notification display
│   ├── LoadingSpinner.tsx       # Loading indicator
│   ├── MetricsGrid.tsx          # Performance metrics display
│   ├── PortfolioChart.tsx       # Portfolio value chart
│   ├── StatCard.tsx             # Individual stat card
│   ├── charts/                  # Chart components
│   ├── layout/                  # Layout components
│   └── ui/                      # Reusable UI components
├── pages/
│   ├── BacktestDetailPage.tsx   # Backtest results page
│   ├── BacktestsPage.tsx        # Backtest history
│   ├── DashboardPage.tsx        # Main dashboard
│   ├── StocksPage.tsx           # Stock browser
│   └── StrategiesPage.tsx       # Strategy management
├── services/
│   └── api.ts                   # API integration
├── store/
│   └── useAppStore.ts           # Zustand state store
└── types/
    └── index.ts                 # TypeScript types
```

### Step 5: Verify Frontend Setup

```bash
npm run build
```

This compiles TypeScript and bundles the application.

---

## Running the Application

### Terminal Setup (Use Multiple Terminals)

#### Terminal 1: Backend (Python/FastAPI)

```bash
cd backend
.venv\Scripts\activate                    # Activate virtual environment
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**

```
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2: Frontend (Node.js/Vite)

```bash
cd frontend
npm run dev
```

**Expected Output:**

```
  VITE v5.x.x  ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

#### Terminal 3: Database (if using Docker)

```bash
docker logs equity-mysql
```

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)

---

## Key Features

### 1. Stock Data Management

**Sync Stocks:**

- Fetch latest data from Yahoo Finance
- Stores OHLCV (Open, High, Low, Close, Volume) prices
- Retrieves fundamental metrics (P/E, ROE, Dividend Yield, etc.)
- Supports NSE, BSE, and other exchanges

**Browse Stocks:**

- List all synced stocks with pagination
- View stock details, latest prices, and fundamentals
- Search and filter by sector/industry

### 2. Strategy Builder

**Define Strategies:**

- Create screening rules (filters) based on fundamental metrics
  - Example: P/E < 20, ROE > 15%, Debt/Equity < 1.0
- Define ranking rules to score filtered stocks
  - Example: Sort by ROE (60% weight), P/B ratio (40% weight)

**Supported Metrics:**

- P/E Ratio, P/B Ratio
- Return on Equity (ROE)
- Dividend Yield
- Revenue, Profit Margin
- Debt-to-Equity, Beta
- Earnings Per Share (EPS)

### 3. Backtesting Engine

**Run Backtests:**

- Specify date range (1 year, 5 years, custom)
- Set initial capital (default: ₹10 lakhs)
- Choose rebalancing frequency (daily, weekly, monthly, quarterly, yearly)
- Select top N stocks to hold (default: 5)

**Backtest Results:**

- Total Return & CAGR (Compound Annual Growth Rate)
- Sharpe Ratio (risk-adjusted return)
- Maximum Drawdown
- Win Rate
- Trade history with buy/sell prices
- Daily portfolio values
- Final holdings

### 4. Performance Analysis

**Metrics Dashboard:**

- Compare multiple backtest runs
- Analyze strategy efficiency
- View comparative performance against benchmarks

**Export Capabilities:**

- Export portfolio history (CSV)
- Export trade records (Excel)
- Export final holdings with weights

---

## How It Works

### Backtest Execution Flow

```
User Input
    ↓
┌─────────────────────────────┐
│ Run Backtest Request        │
│ - Strategy ID               │
│ - Date Range                │
│ - Initial Capital           │
│ - Rebalance Frequency       │
└─────────┬───────────────────┘
          ↓
┌─────────────────────────────┐
│ Load Stock Data             │
│ - Fetch prices for period   │
│ - Load fundamentals         │
└─────────┬───────────────────┘
          ↓
┌─────────────────────────────┐
│ Portfolio Simulation        │
│ For each rebalance date:    │
│  1. Apply screening rules   │
│  2. Rank candidates         │
│  3. Select top N            │
│  4. Equal weight allocation │
│  5. Track trades & values   │
└─────────┬───────────────────┘
          ↓
┌─────────────────────────────┐
│ Compute Performance Metrics │
│ - Return, CAGR              │
│ - Sharpe Ratio              │
│ - Max Drawdown              │
│ - Win Rate                  │
└─────────┬───────────────────┘
          ↓
  Display Results
```

### Strategy Screening Example

**Initial Candidate Pool:** 200 stocks

**Screening Rules:**

```
- P/E Ratio > 20
- ROE > 15%
- Debt/Equity < 1.0
- Market Cap > ₹1,000 Cr
```

**After Screening:** 45 stocks

**Ranking Rules:**

```
- ROE (descending) - 60% weight
- P/E Ratio (ascending) - 40% weight
```

**Select Top 5:** TCS, INFY, Infosys Tech, Wipro, HCL Tech

---

## Code Structure

### Backend Directory

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app setup
│   ├── api/
│   │   └── routes/
│   │       ├── backtests.py    # POST /backtests, GET /backtests/{id}
│   │       ├── stocks.py       # GET /stocks, POST /stocks/sync
│   │       ├── strategies.py   # CRUD strategies
│   │       └── dashboard.py    # Dashboard/export endpoints
│   ├── core/
│   │   ├── config.py           # Environment configuration
│   │   └── database.py         # Database setup & session
│   ├── models/
│   │   ├── stock.py            # Stock, StockPrice, StockFundamental
│   │   ├── strategy.py         # Strategy model
│   │   └── backtest.py         # Backtest model
│   ├── repositories/
│   │   ├── stock_repository.py
│   │   ├── strategy_repository.py
│   │   └── backtest_repository.py
│   ├── schemas/
│   │   └── __init__.py         # Pydantic models
│   ├── services/
│   │   ├── backtest_engine.py  # Core backtesting logic
│   │   ├── strategy_engine.py  # Screening & ranking
│   │   ├── yahoo_finance_service.py
│   │   └── export_service.py
│   └── utils/
│       └── serializers.py      # Convert models to schemas
├── scripts/
│   ├── init-local-mysql.ps1    # Windows DB setup
│   └── init-local-mysql.sql    # SQL initialization
└── requirements.txt

frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── api/
│   │   └── client.ts           # Axios instance
│   ├── components/             # Reusable React components
│   ├── pages/                  # Page components
│   ├── services/               # Service layer
│   ├── store/                  # Zustand store
│   └── types/                  # TypeScript types
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

### Key Service Classes

#### BacktestEngine (`backend/app/services/backtest_engine.py`)

- `run(backtest, strategy)` - Execute backtest
- `_execute_backtest()` - Main simulation loop
- `_build_candidates()` - Build stock pool for screening
- `_get_rebalance_dates()` - Calculate rebalancing dates
- `_compute_metrics()` - Calculate performance metrics

#### StrategyEngine (`backend/app/services/strategy_engine.py`)

- `apply_screening()` - Filter stocks by rules
- `rank_stocks()` - Score and rank candidates
- `select_top_n()` - Select best stocks

#### YahooFinanceService (`backend/app/services/yahoo_finance_service.py`)

- `sync_symbols()` - Fetch and store stock data
- `_sync_single()` - Sync single symbol

---

## Testing Workflows

### Workflow 1: Initial Data Load

```bash
# 1. Start backend and frontend
# 2. Open API docs: http://localhost:8000/docs

# 3. Sync default stocks
POST /stocks/sync
{
  "period": "5y"
}

# Expected: 200 OK with synced stock list
```

### Workflow 2: Create and Test Strategy

```bash
# 1. Create a strategy
POST /strategies
{
  "name": "Test Strategy",
  "description": "Simple test",
  "screening_rules": [
    {
      "field": "pe_ratio",
      "operator": "lt",
      "value": 25
    }
  ],
  "ranking_rules": [
    {
      "field": "roe",
      "direction": "desc",
      "weight": 1.0
    }
  ]
}

# Returns strategy_id (e.g., 1)

# 2. Run backtest
POST /backtests
{
  "strategy_id": 1,
  "name": "Q1 2024 Test",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "initial_capital": 500000,
  "rebalance_frequency": "monthly",
  "top_n": 5
}

# Returns backtest_id and metrics

# 3. View results
GET /backtests/{backtest_id}
```

### Workflow 3: Performance Analysis

```bash
# 1. List all backtests
GET /backtests

# 2. Get dashboard stats
GET /dashboard/stats

# 3. Export results
GET /export/{backtest_id}/csv?export_type=portfolio
GET /export/{backtest_id}/excel
```

---

## Troubleshooting

### Backend Issues

**Port Already in Use:**

```bash
# Find process using port 8000
lsof -i :8000        # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn app.main:app --reload --port 8001
```

**Database Connection Error:**

```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Verify DATABASE_URL in .env
# Check credentials match MySQL user
```

**Module Not Found Errors:**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port Already in Use:**

```bash
npm run dev -- --port 5174
```

**Module Dependencies:**

```bash
npm install
npm cache clean --force
```

---

## Performance Optimization

### Database Indexes

The system automatically creates indexes on:

- `stocks.symbol` (unique)
- `stock_prices.stock_id, stock_prices.date`
- `stock_fundamentals.stock_id, stock_fundamentals.as_of_date`

### Caching Strategy

- Recent backtests cached in memory
- Stock data cached for 1 hour
- Strategy definitions cached for session

### Query Optimization

- Use pagination for large result sets
- Filter stocks before processing
- Limit historical data retrieval to needed period

---

## Next Steps & Enhancements

### Phase 2 Features

- [ ] User authentication & authorization
- [ ] Strategy templates & presets
- [ ] Real-time data streaming
- [ ] Machine learning strategy optimization
- [ ] Mobile app (React Native)
- [ ] Advanced charting (TradingView)
- [ ] Strategy recommendations engine
- [ ] Sentiment analysis integration

### Database Improvements

- [ ] Add indexing for performance
- [ ] Implement data archiving
- [ ] Add audit logging
- [ ] Optimize query plans

### API Enhancements

- [ ] WebSocket for real-time updates
- [ ] GraphQL alternative
- [ ] Rate limiting
- [ ] Request caching

---

## Support & Documentation

- **API Documentation:** [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **FastAPI Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Yahoo Finance Docs:** https://finance.yahoo.com

---

**Platform Version:** 1.0.0
**Last Updated:** June 2024
**Maintainer:** Your Organization
