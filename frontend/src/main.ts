/**
 * 主逻辑 - 初始化应用，绑定事件，处理用户交互。
 * 使用 api.ts 和 ui.ts，状态管理使用模块级变量。
 */

// 导入必要模块
import './style.css';  // 确保样式加载
import type { ColumnMeta } from './types';  // 仅类型导入
import { uploadFile, analyzeData, generatePlot } from './api';
import {
    renderUploadArea,
    renderDataPreview,
    renderStats,
    renderPlotControls,
    renderPlotImage,
    renderStatusMessage,
    clearContainer,
} from './ui';

// 状态
let currentDatasetId: string | null = null;
let currentColumns: ColumnMeta[] = [];

// DOM 容器
const APP_CONTAINER_ID = 'app';
const STATUS_CONTAINER_ID = 'status-container';
const PREVIEW_CONTAINER_ID = 'preview-container';
const STATS_CONTAINER_ID = 'stats-container';
const PLOT_CONTAINER_ID = 'plot-container';

/**
 * 初始化应用
 */
function init(): void {
    const appContainer = document.getElementById(APP_CONTAINER_ID);
    if (!appContainer) {
        console.error('App container not found');
        return;
    }

    // 清空并渲染上传区域
    clearContainer(APP_CONTAINER_ID);
    const uploadArea = renderUploadArea();
    appContainer.appendChild(uploadArea);

    // 添加状态容器
    let statusDiv = document.getElementById(STATUS_CONTAINER_ID);
    if (!statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.id = STATUS_CONTAINER_ID;
        appContainer.appendChild(statusDiv);
    }

    let previewDiv = document.getElementById(PREVIEW_CONTAINER_ID);
    if (!previewDiv) {
        previewDiv = document.createElement('div');
        previewDiv.id = PREVIEW_CONTAINER_ID;
        appContainer.appendChild(previewDiv);
    }

    let statsDiv = document.getElementById(STATS_CONTAINER_ID);
    if (!statsDiv) {
        statsDiv = document.createElement('div');
        statsDiv.id = STATS_CONTAINER_ID;
        appContainer.appendChild(statsDiv);
    }

    let plotDiv = document.createElement('div');
    plotDiv.id = PLOT_CONTAINER_ID;
    appContainer.appendChild(plotDiv);

    // 绑定上传按钮事件
    bindUploadEvents(uploadArea);

    console.log('Mintab Web initialized');
}

/**
 * 绑定上传相关事件
 */
function bindUploadEvents(uploadArea: HTMLElement): void {
    const uploadBtn = uploadArea.querySelector('#upload-btn') as HTMLButtonElement;
    const fileInput = uploadArea.querySelector('#file-input') as HTMLInputElement;
    const statusDiv = uploadArea.querySelector('#upload-status') as HTMLDivElement;

    uploadBtn?.addEventListener('click', async () => {
        if (!fileInput?.files?.[0]) {
            showStatus('请先选择文件', 'error');
            return;
        }

        const file = fileInput.files[0];
        showStatus('正在上传...', 'success');

        try {
            const response = await uploadFile(file);
            currentDatasetId = response.dataset_id;
            currentColumns = response.columns.map(col => ({
                name: col.name,
                type: col.type,
            }));
            currentPreview = response.preview;

            showStatus(`上传成功！数据集 ID: ${response.dataset_id}`, 'success');

            // 渲染数据预览
            const previewContainer = document.getElementById(PREVIEW_CONTAINER_ID);
            if (previewContainer) {
                const previewElement = renderDataPreview(response);
                previewContainer.innerHTML = '';
                previewContainer.appendChild(previewElement);

                // 绑定分析按钮事件
                const analyzeBtn = previewContainer.querySelector('#analyze-btn') as HTMLButtonElement;
                analyzeBtn?.addEventListener('click', () => handleAnalyze());
            }
        } catch (error) {
            showStatus(`上传失败: ${(error as Error).message}`, 'error');
        }
    });
}

/**
 * 处理分析请求
 */
async function handleAnalyze(): Promise<void> {
    if (!currentDatasetId) {
        showStatus('请先上传文件', 'error');
        return;
    }

    showStatus('正在分析数据...', 'success');

    try {
        const response = await analyzeData(currentDatasetId);
        showStatus('分析完成！', 'success');

        // 渲染统计信息
        const statsContainer = document.getElementById(STATS_CONTAINER_ID);
        if (statsContainer) {
            const statsElement = renderStats(response.statistics);
            statsContainer.innerHTML = '';
            statsContainer.appendChild(statsElement);

            // 渲染图表控制面板
            const plotControls = renderPlotControls(currentColumns, currentDatasetId);
            statsContainer.appendChild(plotControls);

            // 绑定生成图表按钮事件
            const generateBtn = statsContainer.querySelector('#generate-plot-btn') as HTMLButtonElement;
            generateBtn?.addEventListener('click', () => handleGeneratePlot());
        }
    } catch (error) {
        showStatus(`分析失败: ${(error as Error).message}`, 'error');
    }
}

/**
 * 处理生成图表请求
 */
async function handleGeneratePlot(): Promise<void> {
    if (!currentDatasetId) {
        showStatus('请先上传文件', 'error');
        return;
    }

    const plotTypeSelect = document.querySelector('#plot-type') as HTMLSelectElement;
    const plotType = plotTypeSelect?.value;

    if (!plotType) {
        showStatus('请选择图表类型', 'error');
        return;
    }

    showStatus('正在生成图表...', 'success');

    try {
        const plotRequest: any = {
            dataset_id: currentDatasetId,
            plot_type: plotType,
        };

        // 根据图表类型添加参数
        if (plotType === 'scatter') {
            const xCol = (document.querySelector('#x-col') as HTMLSelectElement)?.value;
            const yCol = (document.querySelector('#y-col') as HTMLSelectElement)?.value;
            if (!xCol || !yCol) {
                showStatus('散点图需要选择 X 轴和 Y 轴', 'error');
                return;
            }
            plotRequest.x_col = xCol;
            plotRequest.y_col = yCol;
        } else if (plotType === 'histogram') {
            const column = (document.querySelector('#hist-col') as HTMLSelectElement)?.value;
            if (!column) {
                showStatus('直方图需要选择列', 'error');
                return;
            }
            plotRequest.column = column;
        } else if (plotType === 'boxplot') {
            // 可选：选择多列
            // 这里使用所有数值列
        } else if (plotType === 'heatmap') {
            // 可选：选择方法
        }

        const response = await generatePlot(plotRequest);
        showStatus('图表生成成功！', 'success');

        // 渲染图表
        const plotContainer = document.getElementById(PLOT_CONTAINER_ID);
        if (plotContainer) {
            const plotElement = renderPlotImage(response.image);
            plotContainer.innerHTML = '';
            plotContainer.appendChild(plotElement);
        }
    } catch (error) {
        showStatus(`图表生成失败: ${(error as Error).message}`, 'error');
    }
}

/**
 * 显示状态消息
 */
function showStatus(message: string, type: 'success' | 'error' = 'success'): void {
    const statusContainer = document.getElementById(STATUS_CONTAINER_ID);
    if (statusContainer) {
        const statusElement = renderStatusMessage(message, type);
        statusContainer.innerHTML = '';
        statusContainer.appendChild(statusElement);
    }
}

// 初始化应用
init();
