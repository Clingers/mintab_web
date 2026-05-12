import React, { useState } from 'react';
import { uploadFile, analyzeDataset } from '../services/api';
import { useMintabStore } from '../store';

export const UploadPanel: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const setDataset = useMintabStore(state => state.setDataset);
  const setStats = useMintabStore(state => state.setStats);
  const setLoading = useMintabStore(state => state.setLoading);
  const setError = useMintabStore(state => state.setError);
  const loading = useMintabStore(state => state.loading);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadFile(file);
      setDataset(data);
      const stats = await analyzeDataset(data.dataset_id);
      setStats(stats);
    } catch (err: any) {
      setError(err?.message || '文件上传失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-muted)]">Data Input</span>
      </div>

      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
          dragOver
            ? 'border-[var(--color-signal)] bg-[var(--color-signal-dim)]/10'
            : 'border-[var(--color-border)] hover:border-[var(--color-text-muted)]'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleChange}
          className="hidden"
          disabled={loading}
        />
        <div className="text-[var(--color-text-muted)] text-sm">
          {file ? (
            <span className="text-[var(--color-signal)] font-mono">{file.name}</span>
          ) : (
            <>
              <p className="mb-1">Drop file here or click to browse</p>
              <p className="text-xs">.csv, .xlsx, .xls</p>
            </>
          )}
        </div>
      </div>

      <button
        className="btn-primary w-full mt-4"
        disabled={!file || loading}
        onClick={handleUpload}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
            Processing...
          </span>
        ) : (
          'Upload & Analyze'
        )}
      </button>
    </div>
  );
};
