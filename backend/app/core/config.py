from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Equity Strategy Backtesting Platform"
    app_version: str = "1.0.0"
    database_url: str = "mysql+pymysql://equity_user:equity_pass@localhost:3306/equity_backtest"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    default_stocks: str = (
        "RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ICICIBANK.NS,SBIN.NS,BHARTIARTL.NS,ITC.NS,HINDUNILVR.NS,LT.NS,"
        "BAJFINANCE.NS,BAJAJFINSV.NS,HCLTECH.NS,AXISBANK.NS,ASIANPAINT.NS,KOTAKBANK.NS,MARUTI.NS,ULTRACEMCO.NS,SUNPHARMA.NS,TITAN.NS,"
        "TATAMOTORS.NS,TATASTEEL.NS,NTPC.NS,POWERGRID.NS,ADANIENT.NS,ADANIPORTS.NS,ONGC.NS,COALINDIA.NS,JSWSTEEL.NS,"
        "WIPRO.NS,LTIM.NS,BPCL.NS,M&M.NS,HEROMOTOCO.NS,GRASIM.NS,CIPLA.NS,DRREDDY.NS,APOLLOHOSP.NS,DIVISLAB.NS,"
        "EICHERMOT.NS,HINDALCO.NS,INDUSINDBK.NS,IOC.NS,NESTLEIND.NS,SBILIFE.NS,HDFCLIFE.NS,UPL.NS,TECHM.NS,"
        "SHREECEM.NS,ACC.NS,AMBUJACEM.NS,TATAPOWER.NS,TRENT.NS,VBL.NS,HAL.NS,IRCTC.NS,PNB.NS,CANBK.NS,"
        "BOSCHLTD.NS,DLF.NS,GODREJCP.NS,DABUR.NS,BRITANNIA.NS,COLPAL.NS,MARICO.NS,SRF.NS,SIEMENS.NS,ABB.NS,"
        "BEL.NS,PFC.NS,RECLTD.NS,SAIL.NS,GAIL.NS,NMDC.NS,GMRINFRA.NS,IDEA.NS,YESBANK.NS,FEDERALBNK.NS,"
        "IDFCFIRSTB.NS,BANDHANBNK.NS,AUBANK.NS,LICHSGFIN.NS,IBULHSGFIN.NS,PEL.NS,MUTHOOTFIN.NS,CHOLAFIN.NS,BAJAJHLDNG.NS,TATACOMM.NS,"
        "COFORGE.NS,PERSISTENT.NS,MPHASIS.NS,OFSS.NS,KPITTECH.NS,DIXON.NS,POLYCAB.NS,KEI.NS,HAVELLS.NS,VOLTAS.NS,"
        "BLUESTARCO.NS,CROMPTON.NS,WHIRLPOOL.NS,BHEL.NS,ASHOKLEY.NS,TVSMOTOR.NS,BALKRISIND.NS,MRF.NS,APOLLOTYRE.NS,JKTYRE.NS"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def default_stock_list(self) -> list[str]:
        return [symbol.strip() for symbol in self.default_stocks.split(",") if symbol.strip()]


settings = Settings()
