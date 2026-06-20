import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function DrawdownChart({ data }) {
  const chartData = data.map((point) => ({
    date: point.date,
    Drawdown: (point.drawdown || 0) * 100, // Convert to percentage
  }));

  return (
    <div className="card-lg mt-8">
      <h3 className="heading-sm mb-6 text-slate-800">Portfolio Drawdown (%)</h3>
      <div className="h-64 rounded-lg border border-slate-200 bg-slate-50">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "#64748b" }}
              tickFormatter={(v) => v.slice(0, 7)}
              stroke="#cbd5e1"
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#64748b" }}
              tickFormatter={(v) => `${v.toFixed(1)}%`}
              stroke="#cbd5e1"
              domain={["auto", 0]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              }}
              formatter={(value) => [`${value.toFixed(2)}%`, "Drawdown"]}
              labelFormatter={(label) => `Date: ${label}`}
              labelStyle={{ color: "#0f172a" }}
            />
            <Area
              type="monotone"
              dataKey="Drawdown"
              stroke="#ef4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#drawdownGradient)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
