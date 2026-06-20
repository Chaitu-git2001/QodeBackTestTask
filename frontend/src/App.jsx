import { NavLink, Route, Routes } from "react-router-dom";
import BacktestDetailPage from "./pages/BacktestDetailPage.jsx";
import BacktestsPage from "./pages/BacktestsPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import StocksPage from "./pages/StocksPage.jsx";
import StrategiesPage from "./pages/StrategiesPage.jsx";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/stocks", label: "Stocks" },
  { to: "/strategies", label: "Strategies" },
  { to: "/backtests", label: "Backtests" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              Equity Backtest Platform
            </h1>
            <p className="text-sm text-slate-500">
              Indian equity strategy backtesting
            </p>
          </div>
          <nav className="flex gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium ${
                    isActive
                      ? "bg-primary-100 text-primary-700"
                      : "text-slate-600 hover:bg-slate-100"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/stocks" element={<StocksPage />} />
          <Route path="/strategies" element={<StrategiesPage />} />
          <Route path="/backtests" element={<BacktestsPage />} />
          <Route path="/backtests/:id" element={<BacktestDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}
