import React, { useState } from 'react';
import { useMintabStore } from '../store';
import { generatePlot } from '../services/api';

export const PlotViewer: React.FC = () => {
  const dataset = useMintabStore(state => state.dataset);
  const [plotType, setPlotType] = useState<'scatter' | 'histogram' | 'boxplot' | 'heatmap'>('histogram');
  const [xCol, setXCol] = useState('');
  const [yCol, setYCol] = useState('');
  const [method, setMethod] = useState('pearson');
  const setPlot = useMintabStore(state => state.setPlot);
  const plot = useMintabStore(state => state.plot);
  const loading = useMintabStore(state => state.loading);
  const setLoading = useMintabStore(state => state.setLoading);
  const setError = useMintabStore(state => state.setError);

  const handlePlot = async () => {
    if (!dataset) return;
    setLoading(true);
    try {
      const payload: Record<string, any> = {
        dataset_id: dataset.dataset_id,
        plot_type: plotType,
      };

      if (plotType === 'scatter') {
        payload.x_col = xCol;
        payload.y_col = yCol;
      } else if (plotType === 'histogram' || plotType === 'boxplot') {
        payload.column = xCol;
      } else if (plotType === 'heatmap') {
        payload.method = method;
      }

      const res = await generatePlot(payload);
      setPlot(res);
    } catch (e: any) {
      setError(e?.message || '绘图生成失败');
    } finally {
      setLoading(false);
    }
  };

  if (!dataset) return null;

  const columnOptions = dataset.columns.map(c => (
    <option key={c.name} value={c.name}>{c.name}</option>
  ));

  const downloadPlot = () => {
    if (!plot) return;
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${plot.image}`;
    link.download = `mintab_${plotType}.png`;
    link.click();
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-muted)]">Visualization</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <select className="select-field" value={plotType} onChange={e => setPlotType(e.target.value as any)}>
          <option value="histogram">Histogram</option>
          <option value="scatter">Scatter</option>
          <option value="boxplot">Boxplot</option>
          <option value="heatmap">Heatmap</option>
        </select>

        {plotType === 'scatter' && (
          <>
            <select className="select-field" value={xCol} onChange={e => setXCol(e.target.value)}>
              <option value="">X axis</option>
              {columnOptions}
            </select>
            <select className="select-field" value={yCol} onChange={e => setYCol(e.target.value)}>
              <option value="">Y axis</option>
              {columnOptions}
            </select>
          </>
        )}

        {(plotType === 'histogram' || plotType === 'boxplot') && (
          <select className="select-field" value={xCol} onChange={e => setXCol(e.target.value)}>
            <option value="">Select column</option>
            {columnOptions}
          </select>
        )}

        {plotType === 'heatmap' && (
          <select className="select-field" value={method} onChange={e => setMethod(e.target.value)}>
            <option value="pearson">Pearson</option>
            <option value="kendall">Kendall</option>
            <option value="spearman">Spearman</option>
          </select>
        )}

        <button
          className="btn-primary"
          onClick={handlePlot}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>

      {plot && (
        <div className="mt-4">
          <div className="flex justify-end mb-2">
            <button className="btn-ghost" onClick={downloadPlot}>
              Download PNG
            </button>
          </div>
          <div className="rounded-lg overflow-hidden border border-[var(--color-border)] bg-[var(--color-surface-2)]">
            <img
              src={`data:image/png;base64,${plot.image}`}
              alt={`${plotType} plot`}
              className="w-full h-auto"
            />
          </div>
        </div>
      )}
    </div>
  );
};
