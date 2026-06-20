# Initialize the local MySQL database and app user for equity-backtest-platform.
# Usage: .\backend\scripts\init-local-mysql.ps1
# You will be prompted for your MySQL root password.

$ErrorActionPreference = "Stop"
$mysqlExe = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$sqlFile = Join-Path $PSScriptRoot "init-local-mysql.sql"

if (-not (Test-Path $mysqlExe)) {
    Write-Error "MySQL client not found at $mysqlExe. Install MySQL 8 or update the path in this script."
}

Write-Host "Creating database and user on local MySQL..."
Get-Content $sqlFile -Raw | & $mysqlExe -u root -p

Write-Host "Done. Update backend\.env if you use different credentials."
