import React from 'react';
import { useMintabStore } from '../store';
import { saveAs } from 'file-saver';

export const StatsTable: React.FC = () => {
  const stats = useMintabStore(state => state.stats);

  if (!stats) return null;
  const { statistics } = stats;

  const exportCsv = () => {
    const headers = ['column', 'count', 'mean', 'median', 'std', 'min', 'max'];
    const rows = Object.entries(statistics).map(([col, data]: [string, any]) => {
      return [
        col,
        data.count ?? '',
        data.mean ?? '',
        data.median ?? '',
        data.std ?? '',
        data.min ?? '',
        data.max ?? '',
      ].join(',');
    });
    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'statistics.csv');
  };

  return (
    <div className="card bg-base-100 shadow-xl p-6 mb-6 overflow-x-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="card-title text-2xl">统计结果</h2>
        <button className="btn btn-sm btn-outline" onClick={exportCsv}>CSV 导出</button>
      </div>
      <table className="table w-full">
        <thead>
          <tr>
            <th>字段</th>
            <th>计数</th>
            <th>均值</th>
            <th>中位数</th>
            <th>标准差</th>
            <th>最小值</th>
            <th>最大值</th>
          </tr>
        </thead>
      <tbody>
          {Object.entries(statistics as Record<string, any>).map(([col, data]) => {
            const d = data as any;
            return (
            <tr key={col}>
              <td>{col}</td>
              <td>{d.count ?? '-'}</td>
              <td>{d.mean ?? '-'}</td>
              <td>{d.median ?? '-'}</td>
              <td>{d.std ?? '-'}</td>
              <td>{d.min ?? '-'}</td>
              <td>{d.max ?? '-'}</td>
            </tr>
            );
          })}
        </tbody>
      </table>

    </div>
  );
};
