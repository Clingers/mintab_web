/**
 * API 调用封装 - 所有后端通信集中管理，便于维护和错误处理。
 * 使用 types.ts 中的类型定义。
 */

import type {
    UploadResponse,
    AnalyzeResponse,
    PlotRequest,
    PlotResponse,
    ErrorResponse,
} from './types';

const API_BASE = '/api';  // Nginx 反向代理前缀，开发环境需配置代理

/**
 * 上传 CSV/Excel 文件
 */
export async function uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData: ErrorResponse = await response.json().catch(() => ({
            detail: `Upload failed: ${response.statusText}`,
        }));
        throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * 分析数据集，获取统计信息
 */
export async function analyzeData(datasetId: string): Promise<AnalyzeResponse> {
    const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ dataset_id: datasetId }),
    });

    if (!response.ok) {
        const errorData: ErrorResponse = await response.json().catch(() => ({
            detail: `Analysis failed: ${response.statusText}`,
        }));
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * 生成图表
 */
export async function generatePlot(request: PlotRequest): Promise<PlotResponse> {
    const response = await fetch(`${API_BASE}/plot`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        const errorData: ErrorResponse = await response.json().catch(() => ({
            detail: `Plot generation failed: ${response.statusText}`,
        }));
        throw new Error(errorData.detail || `Plot generation failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * 健康检查
 */
export async function checkHealth(): Promise<{ status: string; datasets_count?: number }> {
    const response = await fetch(`${API_BASE}/health`);
    
    if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
}
