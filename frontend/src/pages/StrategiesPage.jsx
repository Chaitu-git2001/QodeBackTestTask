import { useEffect, useState } from "react";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { useAppStore } from "../store/useAppStore.js";
import { FUNDAMENTAL_FIELDS, OPERATORS } from "../types/index.js";

const emptyScreeningRule = () => ({
  field: "pe_ratio",
  operator: "lt",
  value: 25,
});

const emptyRankingRule = () => ({
  field: "roe",
  direction: "desc",
  weight: 1,
});

export default function StrategiesPage() {
  const {
    strategies,
    loading,
    error,
    fetchStrategies,
    createStrategy,
    deleteStrategy,
    clearError,
  } = useAppStore();

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [screeningRules, setScreeningRules] = useState([emptyScreeningRule()]);
  const [rankingRules, setRankingRules] = useState([emptyRankingRule()]);

  useEffect(() => {
    fetchStrategies();
  }, [fetchStrategies]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createStrategy({
      name,
      description: description || null,
      screening_rules: screeningRules,
      ranking_rules: rankingRules,
    });
    setShowForm(false);
    setName("");
    setDescription("");
    setScreeningRules([emptyScreeningRule()]);
    setRankingRules([emptyRankingRule()]);
  };

  if (loading && strategies.length === 0)
    return <LoadingSpinner message="Loading strategies..." />;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Strategies</h2>
          <p className="text-slate-500">
            Define custom screening and ranking rules
          </p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? "Cancel" : "New Strategy"}
        </button>
      </div>

      {error && <ErrorAlert message={error} onDismiss={clearError} />}

      {showForm && (
        <form onSubmit={handleSubmit} className="card mb-6 space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Strategy Name</label>
              <input
                className="input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Value Momentum Strategy"
              />
            </div>
            <div>
              <label className="label">Description</label>
              <input
                className="input"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional description"
              />
            </div>
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Screening Rules</h3>
              <button
                type="button"
                className="btn-secondary"
                onClick={() =>
                  setScreeningRules([...screeningRules, emptyScreeningRule()])
                }
              >
                Add Rule
              </button>
            </div>
            <div className="space-y-3">
              {screeningRules.map((rule, idx) => (
                <div
                  key={idx}
                  className="grid gap-3 rounded-lg border border-slate-200 p-4 sm:grid-cols-4"
                >
                  <select
                    className="input"
                    value={rule.field}
                    onChange={(e) => {
                      const updated = [...screeningRules];
                      updated[idx] = { ...rule, field: e.target.value };
                      setScreeningRules(updated);
                    }}
                  >
                    {FUNDAMENTAL_FIELDS.map((f) => (
                      <option key={f.value} value={f.value}>
                        {f.label}
                      </option>
                    ))}
                  </select>
                  <select
                    className="input"
                    value={rule.operator}
                    onChange={(e) => {
                      const updated = [...screeningRules];
                      updated[idx] = { ...rule, operator: e.target.value };
                      setScreeningRules(updated);
                    }}
                  >
                    {OPERATORS.map((op) => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>
                  <input
                    className="input"
                    type="number"
                    step="any"
                    value={
                      Array.isArray(rule.value) ? rule.value[0] : rule.value
                    }
                    onChange={(e) => {
                      const updated = [...screeningRules];
                      updated[idx] = {
                        ...rule,
                        value: parseFloat(e.target.value),
                      };
                      setScreeningRules(updated);
                    }}
                  />
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() =>
                      setScreeningRules(
                        screeningRules.filter((_, i) => i !== idx),
                      )
                    }
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Ranking Rules</h3>
              <button
                type="button"
                className="btn-secondary"
                onClick={() =>
                  setRankingRules([...rankingRules, emptyRankingRule()])
                }
              >
                Add Rule
              </button>
            </div>
            <div className="space-y-3">
              {rankingRules.map((rule, idx) => (
                <div
                  key={idx}
                  className="grid gap-3 rounded-lg border border-slate-200 p-4 sm:grid-cols-4"
                >
                  <select
                    className="input"
                    value={rule.field}
                    onChange={(e) => {
                      const updated = [...rankingRules];
                      updated[idx] = { ...rule, field: e.target.value };
                      setRankingRules(updated);
                    }}
                  >
                    {FUNDAMENTAL_FIELDS.map((f) => (
                      <option key={f.value} value={f.value}>
                        {f.label}
                      </option>
                    ))}
                  </select>
                  <select
                    className="input"
                    value={rule.direction}
                    onChange={(e) => {
                      const updated = [...rankingRules];
                      updated[idx] = { ...rule, direction: e.target.value };
                      setRankingRules(updated);
                    }}
                  >
                    <option value="desc">Higher is better</option>
                    <option value="asc">Lower is better</option>
                  </select>
                  <input
                    className="input"
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={rule.weight}
                    onChange={(e) => {
                      const updated = [...rankingRules];
                      updated[idx] = {
                        ...rule,
                        weight: parseFloat(e.target.value),
                      };
                      setRankingRules(updated);
                    }}
                  />
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() =>
                      setRankingRules(rankingRules.filter((_, i) => i !== idx))
                    }
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Saving..." : "Create Strategy"}
          </button>
        </form>
      )}

      <div className="grid gap-4">
        {strategies.length === 0 ? (
          <div className="card text-center text-slate-500">
            No strategies yet. Create one to start backtesting.
          </div>
        ) : (
          strategies.map((strategy) => (
            <div key={strategy.id} className="card">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">
                    {strategy.name}
                  </h3>
                  {strategy.description && (
                    <p className="mt-1 text-sm text-slate-500">
                      {strategy.description}
                    </p>
                  )}
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="rounded-full bg-primary-100 px-2 py-1 text-xs text-primary-700">
                      {strategy.screening_rules.length} screening rules
                    </span>
                    <span className="rounded-full bg-purple-100 px-2 py-1 text-xs text-purple-700">
                      {strategy.ranking_rules.length} ranking rules
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => deleteStrategy(strategy.id)}
                  className="btn-secondary text-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
