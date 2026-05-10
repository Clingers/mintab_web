import React, { useState } from 'react';
import { useMintabStore } from '../store';
import { generatePlot } from '../services/api';

export const PlotViewer: React.FC = () => {
  const dataset = useMintabStore(state => state.dataset);
  const [plotType, setPlotType] = useState<'scatter' | 'histogram' | 'boxplot' | 'heatmap'>('scatter');
  const [xCol, setXCol] = useState('');
  const [yCol, setYCol] = useState('');
  const setPlot = useMintabStore(state => state.setPlot);
  const plot = useMintabStore(state => state.plot);
  const loading = useMintabStore(state => state.loading);
  const setLoading = useMintabStore(state => state.setLoading);
  const setError = useMintabStore(state => state.setError);

  const handlePlot = async () => {
    if (!dataset) return;
    setLoading(true);
    try {
      const payload = {
        dataset_id: dataset.dataset_id,
        plot_type: plotType,
        x_col: xCol,
        y_col: yCol,
      };
      const res = await generatePlot(payload);
      setPlot(res);
    } catch (e: any) {
      setError(e?.message || '\u7ed8\u56fe\u751f\u6210\u5931\u8d25');
    } finally {
      setLoading(false);
    }
  };

  if (!dataset) return null;

  const columnOptions = dataset.columns.map(c => (
    <option key={c.name} value={c.name}>
      {c.name}
    </option>
  ));

  const downloadPlot = () => {
    if (!plot) return;
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${plot.image}`;
    link.download = `plot_${plotType}.png`;
    link.click();
  };

  return (
    <div className="card bg-base-100 shadow-xl p-6 mb-6">
      <h2 className="card-title text-2xl mb-4">\u7ed8\u56fe</h2>
      <div className="flex flex-col gap-2 mb-4">
        <select className="select select-bordered w-full max-w-xs" value={plotType} onChange={e => setPlotType(e.target.value as any)}>
          <option value="scatter">Scatter</option>
          <option value="histogram">Histogram</option>
          <option value="boxplot">Boxplot</option>
          <option value="heatmap">Heatmap</option>
        </select>
        {(plotType === 'scatter' || plotType === 'heatmap') && (
          <>
            <select className="select select-bordered w-full max-w-xs" value={xCol} onChange={e => setXCol(e.target.value)}>
              <option value="">-- X Column --</option>
              {columnOptions}
            </select>
            {plotType === 'scatter' && (
              <select className="select select-bordered w-full max-w-xs" value={yCol} onChange={e => setYCol(e.target.value)}>
                <option value="">-- Y Column --</option>
                {columnOptions}
              </select>
            )}
          </>
        )}
        {plotType === 'histogram' && (
          <select className="select select-bordered w-full max-w-xs" value={xCol} onChange={e => setXCol(e.target.value)}>
            <option value="">-- Column --</option>
            {columnOptions}
          </select>
        )}
        {plotType === 'boxplot' && (
          <select className="select select-bordered w-full max-x-xs" value={xCol} onChange={e => setXCol(e.target.value)}>
            <option value="">-- Column --</option>
            {columnOptions}
          </select>
        )}
      </div>
      <button className="btn btn-primary mr-2" onClick={handlePlot} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Plot'}
      </button>
      {plot && (
        <>
          <button className="btn btn-outline btn-sm" onClick={downloadPlot}>Download PNG</button>
          <div className="mt-4">
            <img src={`data:image/png;base64,${plot.image}`} alt="Plot" className="max-w-full rounded" />
          </div>
        </>
      )}
    </div>
  );
};
