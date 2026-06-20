import { useEffect } from "react";
import { Link } from "react-router-dom";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import StatCard from "../components/StatCard.jsx";
import { useAppStore } from "../store/useAppStore.js";

export default function DashboardPage() {
  const { dashboard, loading, error, fetchDashboard, clearError } =
    useAppStore();

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  if (loading && !dashboard)
    return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="heading-lg text-slate-900">Dashboard</h1>
        <p className="mt-2 text-slate-600">
          Overview of your equity backtesting platform
        </p>
      </div>

      {error && <ErrorAlert message={error} onDismiss={clearError} />}

      {dashboard && (
        <>
          <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard title="Stocks" value={dashboard.total_stocks} icon="📈" />
            <StatCard
              title="Strategies"
              value={dashboard.total_strategies}
              icon="⚙️"
            />
            <StatCard
              title="Backtests"
              value={dashboard.total_backtests}
              icon="📊"
            />
            <StatCard
              title="Avg CAGR"
              value={
                dashboard.avg_cagr != null
                  ? `${(dashboard.avg_cagr * 100).toFixed(2)}%`
                  : "N/A"
              }
              subtitle={`${dashboard.completed_backtests} completed`}
              icon="🎯"
            />
          </div>

          <div className="card-lg">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="heading-sm">Recent Backtests</h2>
              <Link
                to="/backtests"
                className="text-sm font-semibold text-primary-600 hover:text-primary-700"
              >
                View All →
              </Link>
            </div>

            {dashboard.recent_backtests.length === 0 ? (
              <div className="rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 py-12 text-center">
                <p className="text-slate-600">No backtests yet.</p>
                <Link
                  to="/backtests"
                  className="mt-3 inline-block text-primary-600 font-semibold hover:text-primary-700"
                >
                  Run your first backtest →
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="table-head">
                      <th className="px-4 py-3 text-left font-semibold">
                        Name
                      </th>
                      <th className="px-4 py-3 text-left font-semibold">
                        Period
                      </th>
                      <th className="px-4 py-3 text-left font-semibold">
                        Status
                      </th>
                      <th className="px-4 py-3 text-right font-semibold">
                        CAGR
                      </th>
                      <th className="px-4 py-3 text-center font-semibold">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.recent_backtests.map((bt) => (
                      <tr key={bt.id} className="table-row">
                        <td className="px-4 py-3 font-semibold text-slate-900">
                          {bt.name}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {bt.start_date} → {bt.end_date}
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
                          <Link
                            to={`/backtests/${bt.id}`}
                            className="inline-block rounded-lg bg-primary-50 px-3 py-1.5 text-sm font-semibold text-primary-700 transition hover:bg-primary-100"
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
