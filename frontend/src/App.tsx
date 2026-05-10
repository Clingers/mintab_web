import React from 'react';
import { UploadPanel } from './components/UploadPanel';
import { DatasetInfo } from './components/DatasetInfo';
import { StatsTable } from './components/StatsTable';
import { PlotViewer } from './components/PlotViewer';
import { ThemeToggle } from './components/ThemeToggle';
import { useMintabStore } from './store';

function App() {
  const error = useMintabStore(state => state.error);
  const setError = useMintabStore(state => state.setError);

  // Auto‑dismiss error after a few seconds
  React.useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(undefined), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <div className="min-h-screen bg-base-200 p-6">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">Mintab Web</h1>
        <ThemeToggle />
      </header>
      {error && (
        <div className="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01M12 4.5c-5.825 0-10.5 4.675-10.5 10.5s4.675 10.5 10.5 10.5 10.5-4.675 10.5-10.5S17.825 4.5 12 4.5z" />
          </svg>
          <span>{error}</span>
        </div>
      )}
      <UploadPanel />
      <DatasetInfo />
      <StatsTable />
      <PlotViewer />
    </div>
  );
}

export default App;
