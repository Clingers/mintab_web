import React from 'react';
import { useMintabStore } from '../store';

export const DatasetInfo: React.FC = () => {
  const dataset = useMintabStore(state => state.dataset);
  const loading = useMintabStore(state => state.loading);

  if (!dataset) return null;

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-muted)]">Data Preview</span>
        <span className="ml-auto text-xs font-mono text-[var(--color-signal)]">
          {dataset.rows} × {dataset.columns.length}
        </span>
      </div>

      {/* Column metadata */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {dataset.columns.map((col) => (
          <span
            key={col.name}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono bg-[var(--color-surface-2)] border border-[var(--color-border)] text-[var(--color-text-secondary)]"
          >
            <span className="text-[var(--color-signal)]">{col.name}</span>
            <span className="text-[var(--color-text-muted)]">({col.type})</span>
          </span>
        ))}
      </div>

      {/* Data table */}
      {loading ? (
        <div className="h-40 rounded-lg bg-[var(--color-surface-2)] animate-pulse"></div>
      ) : dataset.preview && dataset.preview.length > 0 ? (
        <div className="overflow-auto max-h-64 rounded-lg border border-[var(--color-border)]">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                {dataset.columns.map((col) => (
                  <th key={col.name}>{col.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataset.preview.map((row, idx) => (
                <tr key={idx}>
                  <td className="text-[var(--color-text-muted)]">{idx + 1}</td>
                  {dataset.columns.map((col) => (
                    <td key={col.name}>
                      {row[col.name] != null
                        ? String(row[col.name])
                        : <span className="text-[var(--color-text-muted)] italic">null</span>
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-[var(--color-text-muted)] text-sm font-mono">No preview data available</p>
      )}
    </div>
  );
};
