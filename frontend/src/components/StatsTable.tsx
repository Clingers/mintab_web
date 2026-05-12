import React from 'react';
import { useMintabStore } from '../store';
import { saveAs } from 'file-saver';

export const StatsTable: React.FC = () => {
  const stats = useMintabStore(state => state.stats);

  if (!stats) return null;
  const { statistics } = stats;

  const exportCsv = () => {
    const headers = ['column', 'count', 'mean', 'median', 'std', 'min', 'max', 'q1', 'q3'];
    const rows = Object.entries(statistics).map(([col, data]: [string, any]) => {
      return [
        col, data.count ?? '', data.mean ?? '', data.median ?? '',
        data.std ?? '', data.min ?? '', data.max ?? '', data.q1 ?? '', data.q3 ?? '',
      ].join(',');
    });
    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'statistics.csv');
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-muted)]">Statistical Analysis</span>
        <button className="btn-ghost ml-auto" onClick={exportCsv}>
          Export CSV
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-[var(--color-border)]">
        <table className="data-table">
          <thead>
            <tr>
              <th>Column</th>
              <th>Count</th>
              <th>Mean</th>
              <th>Median</th>
              <th>Std</th>
              <th>Min</th>
              <th>Q1</th>
              <th>Q3</th>
              <th>Max</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(statistics as Record<string, any>).map(([col, data]) => {
              const d = data as any;
              return (
                <tr key={col}>
                  <td className="font-semibold text-[var(--color-signal)]">{col}</td>
                  <td>{d.count ?? '—'}</td>
                  <td>{typeof d.mean === 'number' ? d.mean.toFixed(2) : '—'}</td>
                  <td>{typeof d.median === 'number' ? d.median.toFixed(2) : '—'}</td>
                  <td>{typeof d.std === 'number' ? d.std.toFixed(2) : '—'}</td>
                  <td>{d.min ?? '—'}</td>
                  <td>{d.q1 ?? '—'}</td>
                  <td>{d.q3 ?? '—'}</td>
                  <td>{d.max ?? '—'}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
