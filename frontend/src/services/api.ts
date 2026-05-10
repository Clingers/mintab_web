import axios from 'axios';
import type { DatasetResponse, StatsResponse, PlotResponse } from '../types';

const api = axios.create({
  baseURL: '/api', // docker-compose proxies /api to backend
  timeout: 15000,
});

// Global error interceptor – forward error messages to callers
api.interceptors.response.use(
  response => response,
  error => {
    // Attach a readable message if possible
    const msg = error?.response?.data?.detail || error.message || 'Network error';
    return Promise.reject(new Error(msg));
  }
);


export const uploadFile = async (file: File): Promise<DatasetResponse> => {
  const form = new FormData();
  form.append('file', file);
  const res = await api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data as DatasetResponse;
};

export const analyzeDataset = async (datasetId: string): Promise<StatsResponse> => {
  const res = await api.post('/analyze', { dataset_id: datasetId });
  return res.data as StatsResponse;
};

export const generatePlot = async (payload: any): Promise<PlotResponse> => {
  const res = await api.post('/plot', payload);
  return res.data as PlotResponse;
};

export const healthCheck = async () => {
  const res = await api.get('/health');
  return res.data;
};
