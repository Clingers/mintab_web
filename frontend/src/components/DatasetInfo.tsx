import React, { useEffect } from 'react';
import { useMintabStore } from '../store';
import { analyzeDataset } from '../services/api';

export const DatasetInfo: React.FC = () => {
  const dataset = useMintabStore(state => state.dataset);
  const setStats = useMintabStore(state => state.setStats);
  const loading = useMintabStore(state => state.loading);
  const setLoading = useMintabStore(state => state.setLoading);
  const setError = useMintabStore(state => state.setError);

  useEffect(() => {
    if (!dataset) return;
    const fetchStats = async () => {
      setLoading(true);
      try {
        const stats = await analyzeDataset(dataset.dataset_id);
        setStats(stats);
      } catch (e: any) {
        setError(e?.message || '统计获取失败');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [dataset]);

  if (!dataset) return null;

  return (
    <div className="card bg-base-100 shadow-xl p-6 mb-6">
      <h2 className="card-title text-2xl mb-2">{dataset.filename}</h2>
      <p className="mb-2">{dataset.rows} rows • {dataset.columns.length} columns</p>
      {loading ? (
        <div className="skeleton h-48 w-full"></div>
      ) : (
        <pre className="bg-base-200 p-2 rounded overflow-x-auto max-h-48">
          {JSON.stringify(dataset.preview, null, 2)}
        </pre>
      )}
    </div>
  );
};
