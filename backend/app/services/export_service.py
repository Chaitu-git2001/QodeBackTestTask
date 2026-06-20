import json
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.backtest import Backtest
from app.repositories.backtest_repository import BacktestRepository


class ExportService:
    def __init__(self, db: Session):
        self.repo = BacktestRepository(db)

    def get_backtest(self, backtest_id: int) -> Backtest:
        backtest = self.repo.get_by_id(backtest_id)
        if not backtest:
            raise ValueError("Backtest not found")
        if backtest.status != "completed":
            raise ValueError("Backtest is not completed yet")
        return backtest

    def export_csv(self, backtest_id: int, export_type: str = "portfolio") -> StreamingResponse:
        backtest = self.get_backtest(backtest_id)
        df = self._build_dataframe(backtest, export_type)
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        filename = f"backtest_{backtest_id}_{export_type}.csv"
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    def export_excel(self, backtest_id: int) -> StreamingResponse:
        backtest = self.get_backtest(backtest_id)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            self._build_dataframe(backtest, "portfolio").to_excel(
                writer, sheet_name="Portfolio", index=False
            )
            self._build_dataframe(backtest, "trades").to_excel(
                writer, sheet_name="Trades", index=False
            )
            self._build_dataframe(backtest, "holdings").to_excel(
                writer, sheet_name="Holdings", index=False
            )
            if backtest.metrics:
                pd.DataFrame([json.loads(backtest.metrics)]).to_excel(
                    writer, sheet_name="Metrics", index=False
                )
        output.seek(0)
        filename = f"backtest_{backtest_id}_report.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    def _build_dataframe(self, backtest: Backtest, export_type: str) -> pd.DataFrame:
        if export_type == "trades":
            data = json.loads(backtest.trades or "[]")
        elif export_type == "holdings":
            data = json.loads(backtest.holdings or "[]")
        else:
            data = json.loads(backtest.portfolio_history or "[]")
        return pd.DataFrame(data)
