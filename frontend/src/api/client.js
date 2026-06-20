import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const stockApi = {
  list: () => api.get("/stocks").then((r) => r.data),
  get: (symbol) => api.get(`/stocks/${symbol}`).then((r) => r.data),
  sync: (symbols = [], period = "5y") =>
    api.post("/stocks/sync", { symbols, period }).then((r) => r.data),
};

export const strategyApi = {
  list: () => api.get("/strategies").then((r) => r.data),
  get: (id) => api.get(`/strategies/${id}`).then((r) => r.data),
  create: (data) => api.post("/strategies", data).then((r) => r.data),
  update: (id, data) => api.put(`/strategies/${id}`, data).then((r) => r.data),
  delete: (id) => api.delete(`/strategies/${id}`),
};

export const backtestApi = {
  list: () => api.get("/backtests").then((r) => r.data),
  get: (id) => api.get(`/backtests/${id}`).then((r) => r.data),
  run: (data) => api.post("/backtests", data).then((r) => r.data),
};

export const dashboardApi = {
  stats: () => api.get("/dashboard/stats").then((r) => r.data),
};

export const exportApi = {
  csvUrl: (backtestId, type = "portfolio") =>
    `/api/export/${backtestId}/csv?export_type=${type}`,
  excelUrl: (backtestId) => `/api/export/${backtestId}/excel`,
};

export default api;
