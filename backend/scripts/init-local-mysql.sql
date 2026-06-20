-- One-time setup for local MySQL (run as root or another admin user).
-- Example (Windows):
--   mysql -u root -p < backend\scripts\init-local-mysql.sql
-- Example (macOS/Linux):
--   mysql -u root -p < backend/scripts/init-local-mysql.sql

CREATE DATABASE IF NOT EXISTS equity_backtest
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'equity_user'@'localhost' IDENTIFIED BY 'equity_pass';
GRANT ALL PRIVILEGES ON equity_backtest.* TO 'equity_user'@'localhost';
FLUSH PRIVILEGES;
