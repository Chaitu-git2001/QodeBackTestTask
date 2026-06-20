import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function PortfolioChart({ data }) {
  const chartData = data.map((point) => ({
    date: point.date,
    Portfolio: point.value,
    Benchmark: point.benchmark_value,
  }));

  return (
    <div className="card-lg">
      <h3 className="heading-sm mb-6">Portfolio Performance</h3>
      <div className="h-96 rounded-lg border border-slate-200 bg-slate-50">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "#64748b" }}
              tickFormatter={(v) => v.slice(0, 7)}
              stroke="#cbd5e1"
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#64748b" }}
              tickFormatter={(v) => `₹${(v / 100000).toFixed(1)}L`}
              stroke="#cbd5e1"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              }}
              formatter={(value) => [`₹${value.toLocaleString("en-IN")}`, ""]}
              labelFormatter={(label) => `Date: ${label}`}
              labelStyle={{ color: "#0f172a" }}
            />
            <Legend
              wrapperStyle={{ paddingTop: "20px" }}
              iconType="line"
              formatter={(value) => (
                <span style={{ color: "#475569" }}>{value}</span>
              )}
            />
            <Line
              type="monotone"
              dataKey="Portfolio"
              stroke="#2563eb"
              strokeWidth={3}
              dot={false}
              isAnimationActive={false}
              name="Portfolio Value"
            />
            <Line
              type="monotone"
              dataKey="Benchmark"
              stroke="#94a3b8"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
              isAnimationActive={false}
              name="Benchmark"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
