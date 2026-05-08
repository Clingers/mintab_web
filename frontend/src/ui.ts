/**
 * UI 组件函数 - 每个函数返回 HTMLElement，职责单一。
 * 支持中文界面文案。
 */

import type { ColumnMeta, StatsInfo, UploadResponse, PlotRequest } from './types';

/**
 * 渲染上传区域
 */
export function renderUploadArea(): HTMLElement {
    const container = document.createElement('div');
    container.className = 'upload-area';
    container.innerHTML = `
        <h2>上传数据文件</h2>
        <p>支持 CSV、Excel (.xlsx, .xls) 文件</p>
        <input type="file" id="file-input" accept=".csv,.xlsx,.xls" />
        <button id="upload-btn" class="primary-btn">上传</button>
        <div id="upload-status" class="status"></div>
    `;
    return container;
}

/**
 * 渲染数据预览
 */
export function renderDataPreview(response: UploadResponse): HTMLElement {
    const container = document.createElement('div');
    container.className = 'data-preview';
    
    let columnsHtml = response.columns.map(col => `
        <tr>
            <td>${col.name}</td>
            <td><span class="badge ${col.type}">${col.type === 'numeric' ? '数值型' : '分类型'}</span></td>
            <td>${col.non_null}</td>
            <td>${col.null_pct}%</td>
            <td>${Array.isArray(col.unique_values) ? col.unique_values.length : col.unique_values}</td>
        </tr>
    `).join('');

    let previewHtml = response.preview.map(row => `
        <tr>
            ${response.columns.map(col => `<td>${row[col.name] ?? ''}</td>`).join('')}
        </tr>
    `).join('');

    container.innerHTML = `
        <h2>数据预览：${response.filename}</h2>
        <p>总行数：<strong>${response.rows}</strong> | 列数：<strong>${response.columns.length}</strong></p>
        
        <h3>列信息</h3>
        <table>
            <thead>
                <tr>
                    <th>列名</th>
                    <th>类型</th>
                    <th>非空数</th>
                    <th>缺失率</th>
                    <th>唯一值数</th>
                </tr>
            </thead>
            <tbody>${columnsHtml}</tbody>
        </table>

        <h3>前 5 行数据</h3>
        <table>
            <thead>
                <tr>
                    ${response.columns.map(col => `<th>${col.name}</th>`).join('')}
                </tr>
            </thead>
            <tbody>${previewHtml}</tbody>
        </table>

        <button id="analyze-btn" class="primary-btn">开始统计分析</button>
        <div id="stats-container"></div>
        <div id="plot-container"></div>
    `;
    return container;
}

/**
 * 渲染统计信息
 */
export function renderStats(stats: Record<string, StatsInfo>): HTMLElement {
    const container = document.createElement('div');
    container.className = 'stats-container';

    let statsHtml = Object.entries(stats).map(([colName, stat]) => {
        if (stat.error) {
            return `
                <div class="stat-item error">
                    <h4>${colName}</h4>
                    <p class="error-text">错误：${stat.error}</p>
                </div>
            `;
        }

        if (stat.type === 'categorical') {
            return `
                <div class="stat-item">
                    <h4>${colName}</h4>
                    <p>类型：<span class="badge categorical">分类型</span></p>
                    <p>唯一值数：${stat.unique}</p>
                </div>
            `;
        }

        // 数值型统计
        return `
            <div class="stat-item numeric">
                <h4>${colName} <span class="badge numeric">数值型</span></h4>
                <div class="stat-grid">
                    <div>均值：<strong>${stat.mean?.toFixed(2)}</strong></div>
                    <div>中位数：<strong>${stat.median?.toFixed(2)}</strong></div>
                    <div>标准差：<strong>${stat.std?.toFixed(2)}</strong></div>
                    <div>最小值：<strong>${stat.min}</strong></div>
                    <div>最大值：<strong>${stat.max}</strong></div>
                    <div>Q1：<strong>${stat.q1?.toFixed(2)}</strong></div>
                    <div>Q3：<strong>${stat.q3?.toFixed(2)}</strong></div>
                    <div>有效数：<strong>${stat.count}</strong></div>
                    <div>缺失数：<strong>${stat.missing}</strong></div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <h2>统计分析结果</h2>
        <div class="stats-grid">${statsHtml}</div>
        <hr />
        <h3>生成图表</h3>
    `;
    return container;
}

/**
 * 渲染图表控制面板
 */
export function renderPlotControls(columns: ColumnMeta[], datasetId: string): HTMLElement {
    const numericCols = columns.filter(col => col.type === 'numeric').map(col => col.name);
    const allCols = columns.map(col => col.name);

    const container = document.createElement('div');
    container.className = 'plot-controls';
    container.innerHTML = `
        <div class="control-group">
            <label for="plot-type">图表类型：</label>
            <select id="plot-type">
                <option value="scatter">散点图</option>
                <option value="histogram">直方图</option>
                <option value="boxplot">箱式图</option>
                <option value="heatmap">热力图</option>
            </select>
        </div>

        <div class="control-group" id="scatter-controls">
            <label for="x-col">X 轴：</label>
            <select id="x-col">
                ${numericCols.map(col => `<option value="${col}">${col}</option>`).join('')}
            </select>
            <label for="y-col">Y 轴：</label>
            <select id="y-col">
                ${numericCols.map(col => `<option value="${col}">${col}</option>`).join('')}
            </select>
        </div>

        <div class="control-group hidden" id="histogram-controls">
            <label for="hist-col">列：</label>
            <select id="hist-col">
                ${numericCols.map(col => `<option value="${col}">${col}</option>`).join('')}
            </select>
        </div>

        <button id="generate-plot-btn" class="primary-btn">生成图表</button>
    `;

    // 图表类型切换逻辑
    const plotTypeSelect = container.querySelector('#plot-type') as HTMLSelectElement;
    const scatterControls = container.querySelector('#scatter-controls') as HTMLElement;
    const histogramControls = container.querySelector('#histogram-controls') as HTMLElement;

    plotTypeSelect?.addEventListener('change', () => {
        const type = plotTypeSelect.value;
        scatterControls.classList.toggle('hidden', type !== 'scatter');
        histogramControls.classList.toggle('hidden', type !== 'histogram');
    });

    // 生成图表按钮逻辑（由 main.ts 绑定完整逻辑）
    return container;
}

/**
 * 渲染图表图片
 */
export function renderPlotImage(base64: string): HTMLElement {
    const container = document.createElement('div');
    container.className = 'plot-image-container';
    container.innerHTML = `
        <h3>图表预览</h3>
        <img src="data:image/png;base64,${base64}" alt="生成的图表" class="plot-image" />
    `;
    return container;
}

/**
 * 渲染状态消息（成功/错误）
 */
export function renderStatusMessage(message: string, type: 'success' | 'error' = 'success'): HTMLElement {
    const div = document.createElement('div');
    div.className = `status-message ${type}`;
    div.textContent = message;
    return div;
}

/**
 * 清空指定容器
 */
export function clearContainer(containerId: string): void {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
    }
}
