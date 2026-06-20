import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { useAppStore } from "../store/useAppStore.js";

export default function BacktestsPage() {
  const navigate = useNavigate();
  const {
    backtests,
    strategies,
    loading,
    error,
    fetchBacktests,
    fetchStrategies,
    runBacktest,
    clearError,
  } = useAppStore();

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    strategy_id: 0,
    name: "",
    start_date: "2020-01-01",
    end_date: "2024-12-31",
    initial_capital: 1000000,
    rebalance_frequency: "monthly",
    top_n: 5,
    position_sizing: "equal",
    position_sizing_metric: "roce",
  });

  useEffect(() => {
    fetchBacktests();
    fetchStrategies();
  }, [fetchBacktests, fetchStrategies]);

  useEffect(() => {
    if (strategies.length > 0 && form.strategy_id === 0) {
      setForm((f) => ({ ...f, strategy_id: strategies[0].id }));
    }
  }, [strategies, form.strategy_id]);

  const handleRun = async (e) => {
    e.preventDefault();
    try {
      const result = await runBacktest(form);
      setShowForm(false);
      navigate(`/backtests/${result.id}`);
    } catch {
      // error in store
    }
  };

  if (loading && backtests.length === 0)
    return <LoadingSpinner message="Loading backtests..." />;

  return (
    <div>
      <div className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="heading-lg">Backtests</h1>
          <p className="mt-2 text-slate-600">
            Run and analyze strategy backtests
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary-lg"
          disabled={strategies.length === 0}
        >
          {showForm ? "Cancel" : "Run Backtest"}
        </button>
      </div>

      {strategies.length === 0 && (
        <div className="alert alert-warning mb-6">
          Create a strategy first before running a backtest.
        </div>
      )}

      {error && <ErrorAlert message={error} onDismiss={clearError} />}

      {showForm && (
        <form onSubmit={handleRun} className="card-lg mb-8 space-y-6">
          <div className="heading-sm">New Backtest</div>
          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <label className="label">Backtest Name</label>
              <input
                className="input"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                placeholder="Q1 2024 Value Test"
              />
            </div>
            <div>
              <label className="label">Strategy</label>
              <select
                className="input"
                value={form.strategy_id}
                onChange={(e) =>
                  setForm({ ...form, strategy_id: Number(e.target.value) })
                }
              >
                {strategies.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Start Date</label>
              <input
                className="input"
                type="date"
                value={form.start_date}
                onChange={(e) =>
                  setForm({ ...form, start_date: e.target.value })
                }
                required
              />
            </div>
            <div>
              <label className="label">End Date</label>
              <input
                className="input"
                type="date"
                value={form.end_date}
                onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Initial Capital (₹)</label>
              <input
                className="input"
                type="number"
                min="10000"
                value={form.initial_capital}
                onChange={(e) =>
                  setForm({
                    ...form,
                    initial_capital: Number(e.target.value),
                  })
                }
                required
              />
            </div>
            <div>
              <label className="label">Rebalance Frequency</label>
              <select
                className="input"
                value={form.rebalance_frequency}
                onChange={(e) =>
                  setForm({
                    ...form,
                    rebalance_frequency: e.target.value,
                  })
                }
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
            <div>
              <label className="label">Top N Stocks</label>
              <input
                className="input"
                type="number"
                min="1"
                max="50"
                value={form.top_n}
                onChange={(e) =>
                  setForm({ ...form, top_n: Number(e.target.value) })
                }
                required
              />
            </div>
            <div>
              <label className="label">Position Sizing Method</label>
              <select
                className="input"
                value={form.position_sizing}
                onChange={(e) =>
                  setForm({
                    ...form,
                    position_sizing: e.target.value,
                  })
                }
              >
                <option value="equal">Equal-weighted</option>
                <option value="market_cap">Market cap-weighted</option>
                <option value="metric">Metric-weighted</option>
              </select>
            </div>
            {form.position_sizing === "metric" && (
              <div>
                <label className="label">Sizing Metric</label>
                <select
                  className="input"
                  value={form.position_sizing_metric}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      position_sizing_metric: e.target.value,
                    })
                  }
                >
                  <option value="roce">ROCE</option>
                  <option value="roe">ROE</option>
                  <option value="market_cap">Market Cap</option>
                  <option value="revenue">Revenue</option>
                </select>
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <button type="submit" disabled={loading} className="btn-primary-lg">
              {loading ? "Running..." : "Run Backtest"}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="card-lg overflow-x-auto">
        <h2 className="heading-sm mb-6">
          Backtest History ({backtests.length})
        </h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="table-head">
              <th className="px-4 py-3 text-left font-semibold">Name</th>
              <th className="px-4 py-3 text-left font-semibold">Period</th>
              <th className="px-4 py-3 text-left font-semibold">Capital</th>
              <th className="px-4 py-3 text-left font-semibold">Status</th>
              <th className="px-4 py-3 text-right font-semibold">CAGR</th>
              <th className="px-4 py-3 text-center font-semibold">Action</th>
            </tr>
          </thead>
          <tbody>
            {backtests.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-slate-500"
                >
                  <p className="text-sm">No backtests yet.</p>
                  <p className="mt-1 text-xs">
                    Click "Run Backtest" to create your first backtest.
                  </p>
                </td>
              </tr>
            ) : (
              backtests.map((bt) => (
                <tr key={bt.id} className="table-row">
                  <td className="px-4 py-3 font-semibold text-slate-900">
                    {bt.name}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {bt.start_date} → {bt.end_date}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    ₹{bt.initial_capital.toLocaleString("en-IN")}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`badge ${
                        bt.status === "completed"
                          ? "badge-success"
                          : bt.status === "failed"
                            ? "badge-error"
                            : "badge-warning"
                      }`}
                    >
                      {bt.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-900">
                    {bt.metrics
                      ? `${(bt.metrics.cagr * 100).toFixed(2)}%`
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {bt.status === "completed" ? (
                      <Link
                        to={`/backtests/${bt.id}`}
                        className="inline-block rounded-lg bg-primary-50 px-3 py-1.5 text-sm font-semibold text-primary-700 transition hover:bg-primary-100"
                      >
                        View
                      </Link>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
