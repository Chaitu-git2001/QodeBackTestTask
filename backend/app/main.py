from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import backtests, dashboard, stocks, strategies
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-ready equity strategy backtesting platform for Indian stocks. "
        "Fetch data from Yahoo Finance, define screening/ranking strategies, "
        "run backtests, analyze performance, and export results."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(backtests.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
