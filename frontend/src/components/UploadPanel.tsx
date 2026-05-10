import React, { useState } from 'react';
import { uploadFile } from '../services/api';
import { useMintabStore } from '../store';

export const UploadPanel: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const setDataset = useMintabStore(state => state.setDataset);
  const setLoading = useMintabStore(state => state.setLoading);
  const setError = useMintabStore(state => state.setError);
  const loading = useMintabStore(state => state.loading);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadFile(file);
      setDataset(data);
    } catch (err: any) {
      setError(err?.message || '文件上传失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card bg-base-100 shadow-xl p-6 mb-6">
      <h2 className="card-title text-2xl mb-4">上传数据文件</h2>
      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleChange}
        className="file-input file-input-bordered w-full max-w-xs mb-4"
        disabled={loading}
      />
      <button
        className={`btn btn-primary ${loading ? 'loading' : ''}`}
        disabled={!file || loading}
        onClick={handleUpload}
      >
        {loading ? '上传中...' : '上传并分析'}
      </button>
    </div>
  );
};
