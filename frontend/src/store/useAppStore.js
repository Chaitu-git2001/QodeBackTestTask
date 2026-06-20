import { create } from "zustand";
import {
  backtestApi,
  dashboardApi,
  stockApi,
  strategyApi,
} from "../api/client.js";

export const useAppStore = create((set, get) => ({
  stocks: [],
  strategies: [],
  backtests: [],
  dashboard: null,
  loading: false,
  error: null,

  fetchStocks: async () => {
    set({ loading: true, error: null });
    try {
      const stocks = await stockApi.list();
      set({ stocks, loading: false });
    } catch (err) {
      set({ loading: false, error: err.message });
    }
  },

  syncStocks: async (symbols = []) => {
    set({ loading: true, error: null });
    try {
      const result = await stockApi.sync(symbols);
      await get().fetchStocks();
      set({ loading: false });
      return result.message;
    } catch (err) {
      set({ loading: false, error: err.message });
      throw err;
    }
  },

  fetchStrategies: async () => {
    set({ loading: true, error: null });
    try {
      const strategies = await strategyApi.list();
      set({ strategies, loading: false });
    } catch (err) {
      set({ loading: false, error: err.message });
    }
  },

  createStrategy: async (data) => {
    set({ loading: true, error: null });
    try {
      await strategyApi.create(data);
      await get().fetchStrategies();
      set({ loading: false });
    } catch (err) {
      set({ loading: false, error: err.message });
      throw err;
    }
  },

  deleteStrategy: async (id) => {
    set({ loading: true, error: null });
    try {
      await strategyApi.delete(id);
      await get().fetchStrategies();
      set({ loading: false });
    } catch (err) {
      set({ loading: false, error: err.message });
    }
  },

  fetchBacktests: async () => {
    set({ loading: true, error: null });
    try {
      const backtests = await backtestApi.list();
      set({ backtests, loading: false });
    } catch (err) {
      set({ loading: false, error: err.message });
    }
  },

  runBacktest: async (data) => {
    set({ loading: true, error: null });
    try {
      const result = await backtestApi.run(data);
      await get().fetchBacktests();
      set({ loading: false });
      return result;
    } catch (err) {
      set({ loading: false, error: err.message });
      throw err;
    }
  },

  fetchDashboard: async () => {
    set({ loading: true, error: null });
    try {
      const dashboard = await dashboardApi.stats();
      set({ dashboard, loading: false });
    } catch (err) {
      set({ loading: false, error: err.message });
    }
  },

  clearError: () => set({ error: null }),
}));
