import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { backtestApi, exportApi } from "../api/client.js";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import MetricsGrid from "../components/MetricsGrid.jsx";
import PortfolioChart from "../components/PortfolioChart.jsx";
import DrawdownChart from "../components/DrawdownChart.jsx";

export default function BacktestDetailPage() {
  const { id } = useParams();
  const [backtest, setBacktest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLogIndex, setSelectedLogIndex] = useState(0);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    backtestApi
      .get(Number(id))
      .then(setBacktest)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingSpinner message="Loading backtest results..." />;
  if (error) return <ErrorAlert message={error} />;
  if (!backtest) return <ErrorAlert message="Backtest not found" />;

  return (
    <div>
      <div className="mb-8">
        <Link
          to="/backtests"
          className="text-sm font-semibold text-primary-600 hover:text-primary-700"
        >
          ← Back to Backtests
        </Link>
        <h1 className="heading-lg mt-3">{backtest.name}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-slate-600">
          <span>
            {backtest.start_date} → {backtest.end_date}
          </span>
          <span className="text-slate-300">•</span>
          <span className="capitalize">
            {backtest.rebalance_frequency} rebalance
          </span>
          <span className="text-slate-300">•</span>
          <span>Top {backtest.top_n} stocks</span>
        </div>
      </div>

      {backtest.status === "failed" && backtest.error_message && (
        <ErrorAlert message={backtest.error_message} />
      )}

      {backtest.status === "completed" && backtest.metrics && (
        <>
          <div className="mb-8 flex flex-wrap gap-3">
            <a
              href={exportApi.csvUrl(backtest.id, "portfolio")}
              className="btn-secondary"
            >
              📥 Export Portfolio CSV
            </a>
            <a
              href={exportApi.csvUrl(backtest.id, "trades")}
              className="btn-secondary"
            >
              📥 Export Trades CSV
            </a>
            <a
              href={exportApi.excelUrl(backtest.id)}
              className="btn-primary-lg"
            >
              📊 Export Excel Report
            </a>
          </div>

          <div className="mb-8">
            <MetricsGrid metrics={backtest.metrics} />
          </div>

          {backtest.portfolio_history.length > 0 && (
            <div className="mb-8">
              <PortfolioChart data={backtest.portfolio_history} />
              <DrawdownChart data={backtest.portfolio_history} />
            </div>
          )}

          {/* Top Winners & Losers */}
          {backtest.metrics && backtest.metrics.winners && backtest.metrics.losers && (
            <div className="mb-8 grid gap-8 lg:grid-cols-2">
              <div className="card-lg border-t-4 border-emerald-500 overflow-x-auto">
                <h3 className="heading-sm mb-4 text-emerald-800">🏆 Top 5 Winners</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="table-head">
                      <th className="px-4 py-2 text-left font-semibold">Symbol</th>
                      <th className="px-4 py-2 text-right font-semibold">PnL</th>
                      <th className="px-4 py-2 text-right font-semibold">Return</th>
                    </tr>
                  </thead>
                  <tbody>
                    {backtest.metrics.winners.map((w) => (
                      <tr key={w.symbol} className="table-row">
                        <td className="px-4 py-2 font-semibold text-primary-700">{w.symbol}</td>
                        <td className="px-4 py-2 text-right text-emerald-600 font-semibold">+₹{w.pnl.toLocaleString("en-IN")}</td>
                        <td className="px-4 py-2 text-right text-emerald-600 font-semibold">+{((w.return || 0) * 100).toFixed(2)}%</td>
                      </tr>
                    ))}
                    {backtest.metrics.winners.length === 0 && (
                      <tr>
                        <td colSpan={3} className="px-4 py-4 text-center text-slate-400">No winners (all trades negative PnL)</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="card-lg border-t-4 border-rose-500 overflow-x-auto">
                <h3 className="heading-sm mb-4 text-rose-800">⚠️ Top 5 Losers</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="table-head">
                      <th className="px-4 py-2 text-left font-semibold">Symbol</th>
                      <th className="px-4 py-2 text-right font-semibold">PnL</th>
                      <th className="px-4 py-2 text-right font-semibold">Return</th>
                    </tr>
                  </thead>
                  <tbody>
                    {backtest.metrics.losers.map((l) => (
                      <tr key={l.symbol} className="table-row">
                        <td className="px-4 py-2 font-semibold text-primary-700">{l.symbol}</td>
                        <td className="px-4 py-2 text-right text-rose-600 font-semibold">₹{l.pnl.toLocaleString("en-IN")}</td>
                        <td className="px-4 py-2 text-right text-rose-600 font-semibold">{((l.return || 0) * 100).toFixed(2)}%</td>
                      </tr>
                    ))}
                    {backtest.metrics.losers.length === 0 && (
                      <tr>
                        <td colSpan={3} className="px-4 py-4 text-center text-slate-400">No losers (all trades positive PnL)</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Portfolio Rebalance Logs */}
          {backtest.holdings_history && backtest.holdings_history.length > 0 && (
            <div className="card-lg mb-8">
              <h3 className="heading-sm mb-4 text-slate-800">📅 Portfolio Rebalance Logs</h3>
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <span className="text-sm font-semibold text-slate-700">Select Rebalance Date:</span>
                <select
                  className="input max-w-xs"
                  value={selectedLogIndex}
                  onChange={(e) => setSelectedLogIndex(Number(e.target.value))}
                >
                  {backtest.holdings_history.map((log, idx) => (
                    <option key={log.date} value={idx}>
                      {log.date} (Value: ₹{log.portfolio_value.toLocaleString("en-IN")})
                    </option>
                  ))}
                </select>
              </div>

              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="table-head">
                      <th className="px-4 py-3 text-left font-semibold">Symbol</th>
                      <th className="px-4 py-3 text-right font-semibold">Quantity</th>
                      <th className="px-4 py-3 text-right font-semibold">Weight</th>
                      <th className="px-4 py-3 text-right font-semibold">Purchase Price</th>
                      <th className="px-4 py-3 text-right font-semibold">Current Price</th>
                      <th className="px-4 py-3 text-right font-semibold">Period Return</th>
                      <th className="px-4 py-3 text-right font-semibold">Current Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {backtest.holdings_history[selectedLogIndex]?.holdings.map((h) => (
                      <tr key={h.symbol} className="table-row">
                        <td className="px-4 py-3 font-semibold text-primary-700">{h.symbol}</td>
                        <td className="px-4 py-3 text-right text-slate-600">{h.quantity.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-slate-900">{(h.weight * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-right text-slate-600">₹{h.purchase_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                        <td className="px-4 py-3 text-right text-slate-600">₹{h.price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                        <td className={`px-4 py-3 text-right font-semibold ${h.return >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                          {h.return >= 0 ? "+" : ""}{(h.return * 100).toFixed(2)}%
                        </td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{h.value.toLocaleString("en-IN")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="grid gap-8 lg:grid-cols-2">
            <div className="card-lg overflow-x-auto">
              <h2 className="heading-sm mb-6">Final Holdings</h2>
              <table className="w-full text-sm">
                <thead>
                  <tr className="table-head">
                    <th className="px-4 py-3 text-left font-semibold">
                      Symbol
                    </th>
                    <th className="px-4 py-3 text-right font-semibold">
                      Weight
                    </th>
                    <th className="px-4 py-3 text-right font-semibold">
                      Value
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {backtest.holdings.map((h) => (
                    <tr key={h.symbol} className="table-row">
                      <td className="px-4 py-3 font-semibold text-primary-700">
                        {h.symbol}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-900">
                        {(h.weight * 100).toFixed(1)}%
                      </td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">
                        ₹{h.value.toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card-lg overflow-x-auto">
              <h2 className="heading-sm mb-6">Recent Trades</h2>
              <table className="w-full text-sm">
                <thead>
                  <tr className="table-head">
                    <th className="px-4 py-3 text-left font-semibold">Date</th>
                    <th className="px-4 py-3 text-left font-semibold">
                      Symbol
                    </th>
                    <th className="px-4 py-3 text-center font-semibold">
                      Action
                    </th>
                    <th className="px-4 py-3 text-right font-semibold">
                      Value
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {backtest.trades
                    .slice(-10)
                    .reverse()
                    .map((t, i) => (
                      <tr
                        key={`${t.date}-${t.symbol}-${i}`}
                        className="table-row"
                      >
                        <td className="px-4 py-3 text-slate-600">{t.date}</td>
                        <td className="px-4 py-3 font-semibold text-primary-700">
                          {t.symbol}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span
                            className={`badge ${
                              t.action === "buy"
                                ? "badge-success"
                                : "badge-error"
                            }`}
                          >
                            {t.action === "buy" ? "BUY" : "SELL"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">
                          ₹{t.value.toLocaleString("en-IN")}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
