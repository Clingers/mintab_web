/**
 * 类型定义 - 前后端接口契约。
 * 与后端 models 保持一致。
 */

/** 上传响应 */
export interface UploadResponse {
    dataset_id: string;
    filename: string;
    rows: number;
    columns: ColumnMeta[];
    preview: Record<string, any>[];
}

/** 列元信息 */
export interface ColumnMeta {
    name: string;
    type: 'numeric' | 'categorical';
    non_null: number;
    null_pct: number;
    unique_values: any[];
}

/** 基本统计信息 */
export interface StatsInfo {
    mean?: number;
    median?: number;
    std?: number;
    min?: number;
    max?: number;
    count?: number;
    missing?: number;
    q1?: number;
    q3?: number;
    type?: string;      // for categorical columns
    unique?: number;   // for categorical columns
    error?: string;    // if stats calculation failed
}

/** 分析响应 */
export interface AnalyzeResponse {
    dataset_id: string;
    statistics: Record<string, StatsInfo>;
}

/** 画图请求 */
export interface PlotRequest {
    dataset_id: string;
    plot_type: 'scatter' | 'histogram' | 'boxplot' | 'heatmap';
    x_col?: string;      // for scatter
    y_col?: string;      // for scatter
    column?: string;     // for histogram
    columns?: string[];  // for boxplot
    method?: string;      // for heatmap: pearson/kendall/spearman
}

/** 画图响应 */
export interface PlotResponse {
    image: string;   // base64 PNG string
    format: string;   // 'png'
}

/** 错误响应 */
export interface ErrorResponse {
    detail: string;
}

/** 健康响应 */
export interface HealthResponse {
    status: string;
    datasets_count?: number;
}
