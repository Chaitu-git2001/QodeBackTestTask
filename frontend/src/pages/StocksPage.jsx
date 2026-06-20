import { useEffect, useState } from "react";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { useAppStore } from "../store/useAppStore.js";

const DEFAULT_SYMBOLS = [
  "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
  "BAJFINANCE.NS", "BAJAJFINSV.NS", "HCLTECH.NS", "AXISBANK.NS", "ASIANPAINT.NS", "KOTAKBANK.NS", "MARUTI.NS", "ULTRACEMCO.NS", "SUNPHARMA.NS", "TITAN.NS",
  "TATAMOTORS.NS", "TATASTEEL.NS", "NTPC.NS", "POWERGRID.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ONGC.NS", "COALINDIA.NS", "JSWSTEEL.NS",
  "WIPRO.NS", "LTIM.NS", "BPCL.NS", "M&M.NS", "HEROMOTOCO.NS", "GRASIM.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS",
  "EICHERMOT.NS", "HINDALCO.NS", "INDUSINDBK.NS", "IOC.NS", "NESTLEIND.NS", "SBILIFE.NS", "HDFCLIFE.NS", "UPL.NS", "TECHM.NS",
  "SHREECEM.NS", "ACC.NS", "AMBUJACEM.NS", "TATAPOWER.NS", "TRENT.NS", "VBL.NS", "HAL.NS", "IRCTC.NS", "PNB.NS", "CANBK.NS",
  "BOSCHLTD.NS", "DLF.NS", "GODREJCP.NS", "DABUR.NS", "BRITANNIA.NS", "COLPAL.NS", "MARICO.NS", "SRF.NS", "SIEMENS.NS", "ABB.NS",
  "BEL.NS", "PFC.NS", "RECLTD.NS", "SAIL.NS", "GAIL.NS", "NMDC.NS", "GMRINFRA.NS", "IDEA.NS", "YESBANK.NS", "FEDERALBNK.NS",
  "IDFCFIRSTB.NS", "BANDHANBNK.NS", "AUBANK.NS", "LICHSGFIN.NS", "IBULHSGFIN.NS", "PEL.NS", "MUTHOOTFIN.NS", "CHOLAFIN.NS", "BAJAJHLDNG.NS", "TATACOMM.NS",
  "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS", "OFSS.NS", "KPITTECH.NS", "DIXON.NS", "POLYCAB.NS", "KEI.NS", "HAVELLS.NS", "VOLTAS.NS",
  "BLUESTARCO.NS", "CROMPTON.NS", "WHIRLPOOL.NS", "BHEL.NS", "ASHOKLEY.NS", "TVSMOTOR.NS", "BALKRISIND.NS", "MRF.NS", "APOLLOTYRE.NS", "JKTYRE.NS"
];

export default function StocksPage() {
  const { stocks, loading, error, fetchStocks, syncStocks, clearError } =
    useAppStore();
  const [symbolsInput, setSymbolsInput] = useState(DEFAULT_SYMBOLS.join(", "));
  const [syncMessage, setSyncMessage] = useState(null);

  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  const handleSync = async () => {
    setSyncMessage(null);
    const symbols = symbolsInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    try {
      const message = await syncStocks(symbols);
      setSyncMessage(message);
    } catch {
      // error handled in store
    }
  };

  if (loading && stocks.length === 0)
    return <LoadingSpinner message="Loading stocks..." />;

  return (
    <div>
      <div className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="heading-lg">Stocks</h1>
          <p className="mt-2 text-slate-600">
            Fetch and manage Indian equity data from Yahoo Finance
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={loading}
          className="btn-primary-lg"
        >
          {loading ? "Syncing..." : "Sync Data"}
        </button>
      </div>

      {error && <ErrorAlert message={error} onDismiss={clearError} />}
      {syncMessage && (
        <div className="alert alert-success mb-6 flex items-center justify-between">
          <span>{syncMessage}</span>
          <button
            onClick={() => setSyncMessage(null)}
            className="font-semibold hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      <div className="card-lg mb-8">
        <label className="label">
          Symbols to sync (comma-separated, use .NS for NSE)
        </label>
        <textarea
          className="input-lg min-h-[100px]"
          value={symbolsInput}
          onChange={(e) => setSymbolsInput(e.target.value)}
          placeholder="RELIANCE.NS, TCS.NS, INFY.NS"
        />
        <p className="mt-2 text-xs text-slate-500">
          Enter NSE symbols separated by commas. Use .NS suffix for Indian
          stocks.
        </p>
      </div>

      <div className="card-lg overflow-x-auto">
        <h2 className="heading-sm mb-6">Stock Universe ({stocks.length})</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="table-head">
              <th className="px-4 py-3 text-left font-semibold">Symbol</th>
              <th className="px-4 py-3 text-left font-semibold">Name</th>
              <th className="px-4 py-3 text-left font-semibold">Exchange</th>
              <th className="px-4 py-3 text-left font-semibold">Sector</th>
              <th className="px-4 py-3 text-left font-semibold">Industry</th>
            </tr>
          </thead>
          <tbody>
            {stocks.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-8 text-center text-slate-500"
                >
                  <p className="text-sm">No stocks synced yet.</p>
                  <p className="mt-1 text-xs">
                    Click "Sync Data" to fetch from Yahoo Finance.
                  </p>
                </td>
              </tr>
            ) : (
              stocks.map((stock) => (
                <tr key={stock.id} className="table-row">
                  <td className="px-4 py-3 font-semibold text-primary-700">
                    {stock.symbol}
                  </td>
                  <td className="px-4 py-3 text-slate-900">
                    {stock.name || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {stock.exchange || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {stock.sector || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {stock.industry || "—"}
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
