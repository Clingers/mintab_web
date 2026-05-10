export interface ColumnInfo {
  name: string;
  type: string;
  non_null: number;
  null_pct: number;
  unique_values: number;
}

export interface DatasetResponse {
  dataset_id: string;
  filename: string;
  rows: number;
  columns: ColumnInfo[];
  preview: Record<string, any>[];
}

export interface StatsResponse {
  dataset_id: string;
  statistics: Record<string, any>;
}

export interface PlotResponse {
  image: string; // base64 png
  format: string;
}
