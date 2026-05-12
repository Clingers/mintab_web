import React from 'react';
import { UploadPanel } from './components/UploadPanel';
import { DatasetInfo } from './components/DatasetInfo';
import { StatsTable } from './components/StatsTable';
import { PlotViewer } from './components/PlotViewer';
import { useMintabStore } from './store';

function App() {
  const error = useMintabStore(state => state.error);
  const setError = useMintabStore(state => state.setError);
  const dataset = useMintabStore(state => state.dataset);

  React.useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(undefined), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <header className="flex items-center justify-between mb-8 pb-4 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-3">
          <div className="signal-dot"></div>
          <h1 className="text-xl font-semibold tracking-tight text-[var(--color-text-primary)]">
            Mintab<span className="text-[var(--color-signal)]">Web</span>
          </h1>
          <span className="text-xs text-[var(--color-text-muted)] font-mono ml-2">v1.0</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-[var(--color-text-muted)] font-mono">
          <span className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${dataset ? 'bg-[var(--color-signal)]' : 'bg-[var(--color-text-muted)]'}`}></span>
            {dataset ? `${dataset.filename}` : 'No dataset'}
          </span>
          <span>|</span>
          <span>{dataset ? `${dataset.rows} rows × ${dataset.columns.length} cols` : '—'}</span>
        </div>
      </header>

      {/* Error Toast */}
      {error && (
        <div className="mb-6 px-4 py-3 rounded-lg bg-red-950/60 border border-red-800/50 text-red-300 text-sm font-mono flex items-center gap-2 animate-[fadeIn_0.2s_ease]">
          <span className="text-red-400">✗</span>
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Upload + Dataset Info */}
        <div className="lg:col-span-1 space-y-6">
          <UploadPanel />
          <DatasetInfo />
        </div>

        {/* Right Column: Stats + Plot */}
        <div className="lg:col-span-2 space-y-6">
          <StatsTable />
          <PlotViewer />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-12 pt-4 border-t border-[var(--color-border)] text-center text-xs text-[var(--color-text-muted)] font-mono">
        Mintab Web — Industrial Quality Data Analysis Console
      </footer>
    </div>
  );
}

export default App;
