const formatPercent = (value) => `${(value * 100).toFixed(2)}%`;
const formatCurrency = (value) =>
  `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

export default function MetricsGrid({ metrics }) {
  const items = [
    {
      label: "Total Return",
      value: formatPercent(metrics.total_return),
      icon: "📈",
    },
    { label: "CAGR", value: formatPercent(metrics.cagr), icon: "🎯" },
    {
      label: "Max Drawdown",
      value: formatPercent(metrics.max_drawdown),
      icon: "📉",
    },
    {
      label: "Sharpe Ratio",
      value: metrics.sharpe_ratio.toFixed(2),
      icon: "⚖️",
    },
    {
      label: "Volatility",
      value: formatPercent(metrics.volatility),
      icon: "📊",
    },
    { label: "Win Rate", value: formatPercent(metrics.win_rate), icon: "✅" },
    {
      label: "Final Value",
      value: formatCurrency(metrics.final_value),
      icon: "💰",
    },
    {
      label: "Benchmark Return",
      value:
        metrics.benchmark_return != null
          ? formatPercent(metrics.benchmark_return)
          : "N/A",
      icon: "🏆",
    },
  ];

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="card group">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">{item.label}</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {item.value}
              </p>
            </div>
            <span className="text-2xl opacity-60 group-hover:opacity-100 transition">
              {item.icon}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
