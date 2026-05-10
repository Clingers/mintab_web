import { create } from 'zustand';
import type { DatasetResponse, StatsResponse, PlotResponse } from '../types';

interface MintabState {
  dataset?: DatasetResponse;
  stats?: StatsResponse;
  plot?: PlotResponse;
  loading: boolean;
  error?: string;
  setDataset: (data: DatasetResponse) => void;
  setStats: (data: StatsResponse) => void;
  setPlot: (data: PlotResponse) => void;
  setLoading: (val: boolean) => void;
  setError: (msg?: string) => void;
}

export const useMintabStore = create<MintabState>((set) => ({
  loading: false,
  setDataset: (dataset) => set({ dataset }),
  setStats: (stats) => set({ stats }),
  setPlot: (plot) => set({ plot }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
