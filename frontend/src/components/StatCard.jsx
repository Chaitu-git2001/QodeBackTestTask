export default function StatCard({ title, value, subtitle, icon }) {
  return (
    <div className="card group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="mt-3 text-3xl font-bold text-slate-900">{value}</p>
          {subtitle && (
            <p className="mt-2 text-xs text-slate-500">{subtitle}</p>
          )}
        </div>
        {icon && (
          <span className="text-3xl opacity-60 group-hover:opacity-100 transition">
            {icon}
          </span>
        )}
      </div>
    </div>
  );
}
